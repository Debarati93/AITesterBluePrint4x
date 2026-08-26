import requests
import socket
import json
from urllib.parse import urlparse

import re

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
        # Normalize concatenated JSON objects that may appear without newlines, e.g. '}{' -> '}\n{'
        text = text.replace('}{', '}' + '\n' + '{')

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
                    # Some streams wrap token fragments under 'response' or 'response' may itself be a dict/list
                    if 'response' in obj:
                        val = obj.get('response')
                        if isinstance(val, str):
                            out_parts.append(val)
                        elif isinstance(val, dict):
                            # try common nested fields
                            out_parts.append(val.get('text') or val.get('output') or '')
                        elif isinstance(val, list):
                            for item in val:
                                if isinstance(item, dict):
                                    out_parts.append(item.get('response') or item.get('text') or '')
                                else:
                                    out_parts.append(str(item))
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
            cleaned = ''.join(out_parts)
            return self._postprocess_output(cleaned)
        return self._postprocess_output(text)

    def _postprocess_output(self, text: str) -> str:
        """Try to extract readable text from streaming JSON fragments or concatenated objects.
        If JSON objects are found, prefer their 'response'/'text'/'output' fields concatenated.
        Otherwise, return original text with harmless cleanup (strip trailing/leading whitespace).
        """
        if not text:
            return text
        # Quick heuristics: if text contains repeated JSON-like objects, extract them
        # Normalize concatenated objects
        norm = text.replace('}{', '}' + '\n' + '{')
        # find JSON objects that include a model/response or text key
        objs = []
        try:
            for m in re.finditer(r'\{\s*"model".*?\}', norm, flags=re.DOTALL):
                s = m.group(0)
                try:
                    objs.append(json.loads(s))
                except Exception:
                    continue
        except Exception:
            objs = []

        if objs:
            parts = []
            for o in objs:
                if isinstance(o, dict):
                    val = o.get('response') or o.get('text') or o.get('output')
                    if isinstance(val, str) and val:
                        parts.append(val)
                    elif isinstance(val, list):
                        for it in val:
                            if isinstance(it, dict):
                                parts.append(it.get('response') or it.get('text') or '')
                            else:
                                parts.append(str(it))
            candidate = ''.join(parts).strip()
            if candidate:
                return candidate

        # fallback: try to strip any leading JSON tokens like lines starting with {"model"
        cleaned_lines = []
        for line in norm.splitlines():
            l = line.strip()
            if not l:
                continue
            if l.startswith('{') and '"model"' in l:
                # try to parse and extract response/text
                try:
                    o = json.loads(l)
                    val = o.get('response') or o.get('text') or o.get('output')
                    if isinstance(val, str) and val:
                        cleaned_lines.append(val)
                        continue
                except Exception:
                    pass
                # otherwise skip this token line
                continue
            cleaned_lines.append(line)
        result = '\n'.join(cleaned_lines).strip()
        return result

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
