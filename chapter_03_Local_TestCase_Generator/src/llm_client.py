import requests
import socket
import json
from urllib.parse import urlparse

class LLMClient:
    def __init__(self, settings: dict):
        self.settings = settings or {}
        self.provider = self.settings.get('llm_provider','ollama')
        self.ollama_url = self.settings.get('ollama_url') or 'http://localhost:11434'
        self.groq_key = self.settings.get('groq_api_key')
        self.model = self.settings.get('ollama_model','gemma3:1b')

    def _check_tcp(self, url, timeout=1.0):
        try:
            u = urlparse(url)
            host = u.hostname or 'localhost'
            port = u.port or (11434 if '11434' in url or 'ollama' in url else 443)
            s = socket.create_connection((host, port), timeout)
            s.close()
            return True
        except Exception:
            return False

    def _ollama_available(self):
        return self._check_tcp(self.ollama_url)

    def test_provider(self):
        # returns (ok, message)
        if self.provider == 'ollama' and self._ollama_available():
            return True, 'ollama reachable'
        if self.provider == 'groq' and self.groq_key:
            return True, 'groq configured (key present)'
        if self._ollama_available():
            return True, 'ollama reachable'
        return False, 'no provider reachable'

    def send_prompt(self, prompt: str, timeout=30) -> str:
        # Try Ollama first unless user selected Groq explicitly
        prefer_groq = (self.provider == 'groq')
        if not prefer_groq and self._ollama_available():
            try:
                return self._call_ollama(prompt, timeout)
            except Exception:
                pass
        # fallback to Groq if configured
        if self.groq_key:
            try:
                return self._call_groq(prompt, timeout)
            except Exception:
                pass
        # last attempt Ollama
        try:
            return self._call_ollama(prompt, timeout)
        except Exception as e:
            return f'LLM call failed: {e}'

    def _call_ollama(self, prompt: str, timeout=30) -> str:
        # Minimal Ollama POST attempt. Actual Ollama API may differ; this is a best-effort call.
        base = self.ollama_url.rstrip('/')
        if base.endswith('/api'):
            url = base + '/generate'
        else:
            url = base + '/api/generate'
        payload = {'model': self.model, 'prompt': prompt, 'max_tokens': 800}
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        text = resp.text
        # Try to parse JSON first (non-streaming)
        try:
            j = resp.json()
            # try common fields
            if isinstance(j, dict):
                return j.get('text') or j.get('output') or json.dumps(j)
            # if it's a list, join text fields
            if isinstance(j, list):
                parts = []
                for entry in j:
                    if isinstance(entry, dict):
                        parts.append(entry.get('text') or entry.get('response') or '')
                return '\n'.join([p for p in parts if p])
        except Exception:
            pass
        # Handle newline-delimited JSON (streaming tokens)
        out_parts = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                # Ollama streaming may use 'response' or 'text' keys
                if isinstance(obj, dict):
                    if 'response' in obj:
                        out_parts.append(obj.get('response') or '')
                    elif 'text' in obj:
                        out_parts.append(obj.get('text') or '')
                    elif 'output' in obj:
                        out_parts.append(obj.get('output') or '')
                else:
                    out_parts.append(str(obj))
            except Exception:
                # not JSON, append raw
                out_parts.append(line)
        if out_parts:
            return ''.join(out_parts)
        return text

    def _call_groq(self, prompt: str, timeout=30) -> str:
        # Placeholder Groq call - uses groq.ai or groq.com API endpoint if available.
        url = 'https://api.groq.com/v1/generate'
        headers = {'Authorization': f'Bearer {self.groq_key}'}
        payload = {'prompt': prompt, 'max_tokens': 800}
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
        try:
            j = resp.json()
            return j.get('text') or j.get('output') or str(j)
        except Exception:
            return resp.text
