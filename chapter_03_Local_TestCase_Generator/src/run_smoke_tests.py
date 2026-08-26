import os
import sys
from dotenv import load_dotenv, dotenv_values
from pathlib import Path

# load .env from this folder
ROOT = Path(__file__).parent
env_path = ROOT / '.env'
if not env_path.exists():
    print('ENV_NOT_FOUND')
    sys.exit(2)

# Load values without printing them
load_dotenv(dotenv_path=env_path)
vals = dotenv_values(env_path)

# helper: case-insensitive fetch
def get_env(key_candidates):
    for k in key_candidates:
        for existing in vals.keys():
            if existing.lower() == k.lower():
                return vals.get(existing)
    return None

settings = {
    'jira_url': get_env(['JIRA_URL','JIRA_URL']),
    'jira_email': get_env(['JIRA_EMAIL','JIRA_USER','JIRA_USERNAME']),
    'jira_api_token': get_env(['JIRA_API_TOKEN','JIRA_TOKEN']),
    'llm_provider': 'ollama',
    'ollama_url': get_env(['OLLAMA_URL','OLLAMA_HOST','OLLAMA_ENDPOINT']) or os.getenv('OLLAMA_URL'),
    'groq_api_key': get_env(['GROQ_API_TOKEN','GROQ_API_TOken','GROQ_API_KEY','GROQ_KEY'])
}

# Do not print any secret values
print('LOADED_KEYS:')
for k, v in settings.items():
    print(f'- {k}: ' + ('PRESENT' if v else 'MISSING'))

# Import clients
try:
    from jira_client import JiraClient
    from llm_client import LLMClient
except Exception as e:
    print('IMPORT_FAILED')
    print(str(e))
    sys.exit(3)

# Run Jira test if possible
if settings['jira_url'] and settings['jira_email'] and settings['jira_api_token']:
    jc = JiraClient(settings)
    ok, msg = jc.test_credentials()
    print('\nJIRA_TEST:')
    print(' status: ' + ('OK' if ok else 'FAIL'))
    print(' message: ' + (msg if isinstance(msg, str) and len(msg) < 200 else '[LONG_MESSAGE]'))
else:
    print('\nJIRA_TEST: SKIPPED (missing credentials)')

# Run LLM test
llm = LLMClient(settings)
ok2, msg2 = llm.test_provider()
print('\nLLM_TEST:')
print(' status: ' + ('OK' if ok2 else 'FAIL'))
print(' message: ' + (msg2 if isinstance(msg2, str) and len(msg2) < 200 else '[LONG_MESSAGE]'))

# If Ollama reachable and provider is ollama, optionally run a tiny prompt test (no secrets)
if ok2 and settings.get('ollama_url') and settings.get('llm_provider','ollama')=='ollama':
    try:
        sample = 'Say: smoke test ping.'
        out = llm.send_prompt(sample, timeout=10)
        # redact anything long
        if isinstance(out, str) and len(out) < 1000:
            print('\nLLM_SAMPLE_OUTPUT: PRESENT')
        else:
            print('\nLLM_SAMPLE_OUTPUT: [REDACTED/LONG]')
    except Exception as e:
        print('\nLLM_SAMPLE_OUTPUT: ERROR')
        print(str(e))

print('\nSMOKE_TEST_COMPLETE')
