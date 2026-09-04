import re

import requests
from requests.auth import HTTPBasicAuth

# Atlassian Document Format nodes that carry no text of their own.
_INLINE_ATTR_KEYS = ('text', 'shortName', 'displayName')


def _apply_marks(text: str, marks) -> str:
    for mark in marks or []:
        kind = mark.get('type')
        if kind == 'strong':
            text = f'**{text}**'
        elif kind == 'em':
            text = f'*{text}*'
        elif kind == 'code':
            text = f'`{text}`'
        elif kind == 'link':
            href = (mark.get('attrs') or {}).get('href')
            if href:
                text = f'[{text}]({href})'
    return text


def _inline_text(nodes) -> str:
    parts = []
    for node in nodes or []:
        kind = node.get('type')
        if kind == 'text':
            parts.append(_apply_marks(node.get('text', ''), node.get('marks')))
        elif kind == 'hardBreak':
            parts.append('\n')
        elif kind in ('emoji', 'mention', 'status', 'date'):
            attrs = node.get('attrs') or {}
            parts.append(next((attrs[k] for k in _INLINE_ATTR_KEYS if attrs.get(k)), ''))
        elif node.get('content'):
            parts.append(_inline_text(node['content']))
    return ''.join(parts)


def _table_lines(node) -> list:
    rows = []
    for row in node.get('content') or []:
        if row.get('type') != 'tableRow':
            continue
        cells = []
        for cell in row.get('content') or []:
            text = ' '.join(l.strip() for l in _block_lines(cell.get('content')) if l.strip())
            cells.append(text.replace('|', r'\|'))
        if cells:
            rows.append(cells)
    if not rows:
        return []
    width = max(len(r) for r in rows)
    out = []
    for index, cells in enumerate(rows):
        padded = cells + [''] * (width - len(cells))
        out.append('| ' + ' | '.join(padded) + ' |')
        if index == 0:
            out.append('| ' + ' | '.join(['---'] * width) + ' |')
    return out


def _block_lines(nodes, depth: int = 0) -> list:
    lines = []
    for node in nodes or []:
        kind = node.get('type')
        content = node.get('content')
        if kind == 'paragraph':
            lines.append(_inline_text(content))
        elif kind == 'heading':
            level = max(1, min(6, (node.get('attrs') or {}).get('level', 3)))
            lines.append('#' * level + ' ' + _inline_text(content))
        elif kind in ('bulletList', 'orderedList'):
            ordered = kind == 'orderedList'
            start = (node.get('attrs') or {}).get('order') or 1
            indent = '  ' * depth
            for offset, item in enumerate(content or []):
                marker = f'{start + offset}.' if ordered else '-'
                item_lines = [l for l in _block_lines(item.get('content'), depth + 1) if l.strip()]
                if not item_lines:
                    continue
                lines.append(f'{indent}{marker} {item_lines[0].strip()}')
                lines.extend(f'{indent}   {extra.strip()}' for extra in item_lines[1:])
            lines.append('')
        elif kind == 'table':
            lines.extend(_table_lines(node))
            lines.append('')
        elif kind == 'rule':
            lines.append('---')
        elif kind == 'codeBlock':
            language = (node.get('attrs') or {}).get('language') or ''
            lines.extend([f'```{language}', _inline_text(content), '```'])
        elif kind in ('blockquote', 'panel'):
            for line in _block_lines(content, depth):
                lines.append(f'> {line}' if line.strip() else '>')
        elif content:
            lines.extend(_block_lines(content, depth))
    return lines


def adf_to_markdown(field) -> str:
    """Flatten an Atlassian Document Format value into markdown text."""
    if field is None:
        return ''
    if isinstance(field, str):
        return field
    if not isinstance(field, dict):
        return str(field)
    lines = []
    for block in field.get('content') or []:
        lines.extend(_block_lines([block]))
        lines.append('')
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(lines)).strip()


def extract_section(text: str, keywords=('acceptance criteria', 'acceptance')) -> str:
    """Return the body of the first heading whose title matches one of the keywords."""
    if not text:
        return ''
    lines = text.splitlines()
    start = None
    heading_level = 0
    for index, line in enumerate(lines):
        match = re.match(r'^(#{1,6})\s+(.*)$', line.strip())
        if not match:
            continue
        title = match.group(2).strip().lower().rstrip(':')
        if any(word in title for word in keywords):
            start = index + 1
            heading_level = len(match.group(1))
            break
    if start is None:
        return ''
    body = []
    for line in lines[start:]:
        stripped = line.strip()
        match = re.match(r'^(#{1,6})\s+', stripped)
        if match and len(match.group(1)) <= heading_level:
            break
        if stripped == '---' and body:
            break
        body.append(line)
    return '\n'.join(body).strip()


class JiraClient:
    def __init__(self, settings: dict):
        self.base = settings.get('jira_url')
        self.email = settings.get('jira_email')
        self.token = settings.get('jira_api_token')

    def get_issue(self, key: str) -> dict:
        if not key:
            raise ValueError('No ticket key')
        url = (
            f"{self.base.rstrip('/')}/rest/api/3/issue/{key}"
            '?fields=summary,description,issuetype,priority,labels'
        )
        resp = requests.get(url, auth=HTTPBasicAuth(self.email, self.token), timeout=15)
        resp.raise_for_status()
        fields = resp.json().get('fields', {})

        description = adf_to_markdown(fields.get('description'))
        acceptance = extract_section(description)

        return {
            'key': key,
            'summary': fields.get('summary', ''),
            'description': description,
            'acceptance_criteria': acceptance,
            'issue_type': ((fields.get('issuetype') or {}).get('name') or ''),
            'priority': ((fields.get('priority') or {}).get('name') or ''),
            'labels': fields.get('labels') or [],
        }

    def test_credentials(self):
        try:
            url = f"{self.base.rstrip('/')}/rest/api/3/myself"
            resp = requests.get(url, auth=HTTPBasicAuth(self.email, self.token), timeout=8)
            if resp.status_code == 200:
                return True, 'OK'
            return False, f'Status {resp.status_code}'
        except Exception as e:
            return False, str(e)
