import requests
from requests.auth import HTTPBasicAuth

class JiraClient:
    def __init__(self, settings: dict):
        self.base = settings.get('jira_url')
        self.email = settings.get('jira_email')
        self.token = settings.get('jira_api_token')

    def get_issue(self, key: str) -> dict:
        if not key:
            raise ValueError('No ticket key')
        url = f"{self.base.rstrip('/')}/rest/api/3/issue/{key}?fields=summary,description"
        resp = requests.get(url, auth=HTTPBasicAuth(self.email, self.token), timeout=10)
        resp.raise_for_status()
        data = resp.json()
        fields = data.get('fields', {})
        summary = fields.get('summary','')
        description = ''
        # description may be complex object; try to extract plain text
        desc_field = fields.get('description')
        if isinstance(desc_field, dict):
            # fallback to 'content' traversal if Atlassian Document Format
            try:
                parts = []
                for block in desc_field.get('content', []):
                    for inner in block.get('content', []):
                        parts.append(inner.get('text',''))
                description = '\n'.join([p for p in parts if p])
            except Exception:
                description = str(desc_field)
        else:
            description = desc_field or ''

        # best-effort extract acceptance criteria by looking for 'Acceptance' in description
        ac = ''
        if description:
            for line in description.splitlines():
                if 'accept' in line.lower():
                    ac += line + '\n'

        return {
            'summary': summary,
            'description': description,
            'acceptance_criteria': ac.strip()
        }

    def test_credentials(self) -> (bool, str):
        try:
            url = f"{self.base.rstrip('/')}/rest/api/3/myself"
            resp = requests.get(url, auth=HTTPBasicAuth(self.email, self.token), timeout=8)
            if resp.status_code == 200:
                return True, 'OK'
            return False, f'Status {resp.status_code}'
        except Exception as e:
            return False, str(e)
