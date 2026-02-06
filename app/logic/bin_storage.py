import json
import os
from datetime import datetime
from typing import Any, Dict, List

def _ensure_file(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_events(path: str) -> List[Dict[str, Any]]:
    _ensure_file(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def append_event(path: str, event: Dict[str, Any]) -> None:
    _ensure_file(path)
    events = load_events(path)
    events.append(event)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")
