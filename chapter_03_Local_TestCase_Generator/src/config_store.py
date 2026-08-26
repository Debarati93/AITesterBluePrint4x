import json
from pathlib import Path
from typing import Optional

class ConfigStore:
    def __init__(self, config_path: Path):
        self.config_path = Path(config_path)

    def get_settings(self) -> Optional[dict]:
        if not self.config_path.exists():
            return None
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def save_settings(self, settings: dict):
        # ensure parent dir
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)

    def append_history(self, record: dict):
        history_path = self.config_path.with_name('history.json')
        history = []
        if history_path.exists():
            try:
                with open(history_path, 'r', encoding='utf-8') as h:
                    history = json.load(h)
            except Exception:
                history = []
        history.append(record)
        with open(history_path, 'w', encoding='utf-8') as h:
            json.dump(history, h, indent=2)
