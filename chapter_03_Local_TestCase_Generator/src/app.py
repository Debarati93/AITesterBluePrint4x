import re
import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from config_store import ConfigStore
from jira_client import JiraClient
from llm_client import LLMClient

load_dotenv()
ROOT = Path(__file__).parent
TEMPLATES = ROOT / 'templates'
OUTPUTS = ROOT / 'outputs'
OUTPUTS.mkdir(exist_ok=True)

st.set_page_config(page_title='Jira Test Case Generator', layout='wide')

config = ConfigStore(config_path=ROOT / 'config.json')
settings = config.get_settings() or {}

ollama_default = os.getenv('OLLAMA_URL', 'http://localhost:11434')

# Helpers
JIRA_KEY_RE = re.compile(r'([A-Z][A-Z0-9]+-\d+)')

def extract_jira_key(text):
    m = JIRA_KEY_RE.search(text)
    return m.group(1) if m else None

# UI
st.title('Jira Test Case Generator')

col1, col2 = st.columns([3,1])

with col1:
    st.header('Chat')
    chat_input = st.text_area('Message', height=120)
    if st.button('Send'):
        if not chat_input.strip():
            st.warning('Please enter a message or Jira key')
        else:
            jira_key = extract_jira_key(chat_input)
            if not jira_key:
                st.info('No Jira key detected. The message will be sent to the LLM directly.')
            # load settings
            settings = config.get_settings() or {}
            if not settings.get('jira_url'):
                st.error('Jira settings missing. Go to Settings.')
            else:
                jira = JiraClient(settings)
                try:
                    issue = jira.get_issue(jira_key) if jira_key else None
                except Exception as e:
                    st.error(f'Jira fetch failed: {e}')
                    issue = None

                # load template
                template_path = TEMPLATES / 'test_case_template.md'
                if template_path.exists():
                    template = template_path.read_text(encoding='utf-8')
                else:
                    template = 'Summary: {{summary}}\nDescription: {{description}}\nAcceptance Criteria: {{acceptance_criteria}}'

                prompt = chat_input
                if issue:
                    replaced = template.replace('{{jira_id}}', jira_key or '')\
                                     .replace('{{summary}}', issue.get('summary',''))\
                                     .replace('{{description}}', issue.get('description',''))\
                                     .replace('{{acceptance_criteria}}', issue.get('acceptance_criteria',''))\
                                     .replace('{{preconditions}}', '- User has access to application')
                    prompt = f"Generate structured test cases for {jira_key}:\n\n{replaced}"

                st.subheader('LLM Prompt')
                st.code(prompt)

                # Clear any previous response stored in Streamlit session to avoid showing intermediate fragments
                if 'latest_response' in st.session_state:
                    try:
                        del st.session_state['latest_response']
                    except Exception:
                        st.session_state['latest_response'] = ''

                llm = LLMClient(settings)
                with st.spinner('Generating test cases...'):
                    # call LLM and capture final response only
                    response = llm.send_prompt(prompt)

                # Sanitize response to remove any leftover JSON token fragments before display
                def _sanitize_display(text: str) -> str:
                    if not text:
                        return ''
                    import re
                    # normalize concatenated objects
                    t = text.replace('}{', '}' + '\n' + '{')
                    t = t.replace('][', ']' + '\n' + '[')
                    # remove common trailing streaming suffixes like ,"done":false or similar
                    t = re.sub(r'\,?\s*"done"\s*:\s*(?:true|false)\s*', '', t, flags=re.IGNORECASE)
                    # remove JSON objects/arrays that clearly contain model tokens
                    t = re.sub(r'\{[^\}]*\"model\"[^\}]*\}', '', t, flags=re.DOTALL)
                    t = re.sub(r'\[[^\]]*\"model\"[^\]]*\]', '', t, flags=re.DOTALL)
                    # split into lines and filter out lines that look like JSON fragments
                    out_lines = []
                    for line in t.splitlines():
                        s = line.strip()
                        if not s:
                            continue
                        # skip if line is JSON-like and mentions model/response/done
                        if (s.startswith('{') or s.startswith('[')) and ( '"model"' in s or '"response"' in s or '"done"' in s ):
                            continue
                        # skip lines that are mostly punctuation/quotes
                        if re.fullmatch(r'[\[\]\{\}\"\,\:\s]+', s):
                            continue
                        # otherwise keep line
                        out_lines.append(line)
                    cleaned = '\n'.join(out_lines).strip()
                    # collapse multiple blank lines
                    cleaned = re.sub(r"\n\s*\n+", '\n\n', cleaned)
                    if cleaned:
                        return cleaned
                    # aggressive fallback: remove any remaining JSON-like tokens and return what remains
                    fallback = re.sub(r'\{[^\}]*\}', '', t)
                    fallback = re.sub(r'\[[^\]]*\]', '', fallback)
                    fallback = re.sub(r'\s+', ' ', fallback).strip()
                    return fallback[:2000]

                display_text = _sanitize_display(response)

                # if sanitizer returned empty, show a friendly message instead of raw fragments
                if not display_text:
                    display_text = 'LLM returned no readable text. Try re-running or check LLM logs.'

                # Store the final sanitized response in session state and display it — avoids showing any streaming fragments
                st.session_state['latest_response'] = display_text

                st.subheader('Generated Test Cases')
                st.markdown(st.session_state.get('latest_response', ''))

                # Save option
                if st.button('Save to outputs'):
                    out_file = OUTPUTS / f"{jira_key or 'ad-hoc'}_test_cases.md"
                    out_file.write_text(st.session_state.get('latest_response',''), encoding='utf-8')
                    st.success(f'Saved to {out_file}')

with col2:
    st.header('Quick Actions')
    if st.button('Open Settings'):
        st.info("Open the 'settings' page from the left sidebar to configure credentials and LLM settings.")
    st.markdown('---')
    st.write('Saved settings:')
    st.json(settings or {})
