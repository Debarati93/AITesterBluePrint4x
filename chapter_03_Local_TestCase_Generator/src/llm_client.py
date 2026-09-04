import json
import socket
from urllib.parse import urlparse

import requests

GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'


class LLMClient:
    def __init__(self, settings: dict):
        self.settings = settings or {}
        self.provider = self.settings.get('llm_provider', 'ollama')
        self.ollama_url = self.settings.get('ollama_url') or 'http://localhost:11434'
        self.groq_key = self.settings.get('groq_api_key')
        self.model = self.settings.get('ollama_model', 'gemma3:1b')
        self.groq_model = self.settings.get('groq_model', 'llama-3.3-70b-versatile')
        self.num_predict = int(self.settings.get('num_predict', 2048))
        self.temperature = float(self.settings.get('temperature', 0.2))

    def _check_tcp(self, url, timeout=1.0):
        try:
            parsed = urlparse(url)
            host = parsed.hostname or 'localhost'
            port = parsed.port or (443 if parsed.scheme == 'https' else 11434)
            socket.create_connection((host, port), timeout).close()
            return True
        except Exception:
            return False

    def _ollama_available(self):
        return self._check_tcp(self.ollama_url)

    def test_provider(self):
        if self.provider == 'ollama' and self._ollama_available():
            return True, 'ollama reachable'
        if self.provider == 'groq' and self.groq_key:
            return True, 'groq configured (key present)'
        if self._ollama_available():
            return True, 'ollama reachable'
        return False, 'no provider reachable'

    def send_prompt(self, prompt: str, timeout=180) -> str:
        errors = []
        attempts = []
        if self.provider == 'groq' and self.groq_key:
            attempts.append(('groq', self._call_groq))
        if self._ollama_available():
            attempts.append(('ollama', self._call_ollama))
        if self.groq_key and self.provider != 'groq':
            attempts.append(('groq', self._call_groq))

        for name, call in attempts:
            try:
                text = call(prompt, timeout)
                if text and text.strip():
                    return text
                errors.append(f'{name}: empty response')
            except Exception as e:
                errors.append(f'{name}: {e}')

        return 'LLM call failed: ' + ('; '.join(errors) if errors else 'no provider configured')

    def _call_ollama(self, prompt: str, timeout=180) -> str:
        base = self.ollama_url.rstrip('/')
        url = base + '/generate' if base.endswith('/api') else base + '/api/generate'
        payload = {
            'model': self.model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'num_predict': self.num_predict,
                'temperature': self.temperature,
            },
        }
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        try:
            data = resp.json()
        except ValueError:
            # A proxy may still hand back newline-delimited streaming chunks.
            return self._join_ndjson(resp.text)
        if isinstance(data, dict):
            return (data.get('response') or data.get('text') or data.get('output') or '').strip()
        return self._join_ndjson(resp.text)

    def _call_groq(self, prompt: str, timeout=180) -> str:
        if not self.groq_key:
            raise RuntimeError('Groq API key not configured')
        headers = {
            'Authorization': f'Bearer {self.groq_key}',
            'Content-Type': 'application/json',
        }
        payload = {
            'model': self.groq_model,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': self.temperature,
            'max_tokens': self.num_predict,
        }
        resp = requests.post(GROQ_URL, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        choices = data.get('choices') or []
        if choices:
            return (choices[0].get('message', {}).get('content') or '').strip()
        raise RuntimeError(f"unexpected Groq payload: {list(data)}")

    @staticmethod
    def _join_ndjson(text: str) -> str:
        """Stitch Ollama streaming chunks back together, keeping the model's own line breaks."""
        parts = []
        for line in text.replace('}{', '}\n{').splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except ValueError:
                parts.append(line)
                continue
            if isinstance(obj, dict):
                value = obj.get('response') or obj.get('text') or obj.get('output') or ''
                if isinstance(value, str):
                    parts.append(value)
        return ''.join(parts).strip()
