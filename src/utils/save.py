import json
from pathlib import Path
from ..core.settings import SAVE_DIR

SAVE_DIR.mkdir(exist_ok=True)

def load_scores() -> dict:
    path = SAVE_DIR / "scores.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}

def save_score(name: str, value: int):
    data = load_scores()
    data[name] = max(value, data.get(name, 0))
    (SAVE_DIR / "scores.json").write_text(json.dumps(data, indent=2))
