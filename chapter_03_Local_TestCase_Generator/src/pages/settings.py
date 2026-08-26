import streamlit as st
from pathlib import Path

from config_store import ConfigStore
from jira_client import JiraClient
from llm_client import LLMClient

ROOT = Path(__file__).parents[1]
config = ConfigStore(config_path=ROOT / 'config.json')

st.title('Settings')

settings = config.get_settings() or {}

with st.form('settings_form'):
    st.subheader('Jira')
    jira_url = st.text_input('Jira Base URL', value=settings.get('jira_url',''))
    jira_email = st.text_input('Jira Email', value=settings.get('jira_email',''))
    jira_token = st.text_input('Jira API Token', value=settings.get('jira_api_token',''), type='password')

    st.subheader('LLM')
    provider = st.selectbox('LLM Provider', options=['ollama','groq'], index=0 if settings.get('llm_provider','ollama')=='ollama' else 1)
    ollama_url = st.text_input('Ollama URL', value=settings.get('ollama_url','http://localhost:11434'))
    groq_key = st.text_input('Groq API Key', value=settings.get('groq_api_key',''), type='password')

    submitted = st.form_submit_button('Save')
    if submitted:
        new = {
            'jira_url': jira_url.strip(),
            'jira_email': jira_email.strip(),
            'jira_api_token': jira_token.strip(),
            'llm_provider': provider,
            'ollama_url': ollama_url.strip(),
            'groq_api_key': groq_key.strip()
        }
        config.save_settings(new)
        st.success('Settings saved')

st.markdown('---')
if st.button('Test Jira Credentials'):
    settings = config.get_settings() or {}
    if not settings.get('jira_url'):
        st.error('Jira settings missing')
    else:
        jc = JiraClient(settings)
        ok, msg = jc.test_credentials()
        if ok:
            st.success('Jira credentials OK')
        else:
            st.error(f'Jira test failed: {msg}')

if st.button('Test LLM'):
    settings = config.get_settings() or {}
    llm = LLMClient(settings)
    ok, msg = llm.test_provider()
    if ok:
        st.success('LLM provider reachable')
    else:
        st.error(f'LLM test failed: {msg}')
