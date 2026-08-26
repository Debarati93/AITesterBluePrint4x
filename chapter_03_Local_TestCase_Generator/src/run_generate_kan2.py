import os
from pathlib import Path
from dotenv import load_dotenv, dotenv_values

ROOT = Path(__file__).parent
load_dotenv(ROOT / '.env')
vals = dotenv_values(ROOT / '.env')

settings = {
    'jira_url': vals.get('JIRA_URL') or os.getenv('JIRA_URL'),
    'jira_email': vals.get('JIRA_EMAIL') or os.getenv('JIRA_EMAIL'),
    'jira_api_token': vals.get('JIRA_API_TOKEN') or os.getenv('JIRA_API_TOKEN'),
    'llm_provider': 'ollama',
    'ollama_url': vals.get('OLLAMA_URL') or os.getenv('OLLAMA_URL'),
    'groq_api_key': vals.get('GROQ_API_TOken') or vals.get('GROQ_API_KEY') or os.getenv('GROQ_API_KEY')
}

from jira_client import JiraClient
from llm_client import LLMClient

jc = JiraClient(settings)
issue = jc.get_issue('KAN-2')
print('ISSUE SUMMARY:', issue.get('summary')[:200])
print('ISSUE DESCRIPTION (truncated):', (issue.get('description') or '')[:400])
print('AC:', issue.get('acceptance_criteria'))

template_path = ROOT / 'templates' / 'test_case_template.md'
template = template_path.read_text(encoding='utf-8') if template_path.exists() else 'Summary: {{summary}}\nDescription: {{description}}\nAcceptance Criteria: {{acceptance_criteria}}'

prompt = template.replace('{{summary}}', issue.get('summary',''))\
                 .replace('{{description}}', issue.get('description',''))\
                 .replace('{{acceptance_criteria}}', issue.get('acceptance_criteria',''))
prompt = f"Generate structured test cases for KAN-2:\n\n{prompt}"

print('\nPROMPT (truncated):', prompt[:500])

llm = LLMClient(settings)
resp = llm.send_prompt(prompt, timeout=60)
print('\nLLM RESPONSE LENGTH:', len(resp))
print('\nLLM RESPONSE (first 1000 chars):\n')
print(resp[:1000])
