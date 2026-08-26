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

                llm = LLMClient(settings)
                with st.spinner('Generating test cases...'):
                    response = llm.send_prompt(prompt)

                st.subheader('Generated Test Cases')
                st.markdown(response)

                # Save option
                if st.button('Save to outputs'):
                    out_file = OUTPUTS / f"{jira_key or 'ad-hoc'}_test_cases.md"
                    out_file.write_text(response, encoding='utf-8')
                    st.success(f'Saved to {out_file}')

with col2:
    st.header('Quick Actions')
    if st.button('Open Settings'):
        st.info("Open the 'settings' page from the left sidebar to configure credentials and LLM settings.")
    st.markdown('---')
    st.write('Saved settings:')
    st.json(settings or {})
