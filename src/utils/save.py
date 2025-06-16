# src/utils/save.py
"""
Proste API punktacji:

    add_score(level_name: str, nick: str, value: int)
    get_top(level_name: str, n: int = 5) -> list[tuple[nick, score]]

Format pliku scores.json
{
  "level1": [ {"n": "Ada", "s": 550}, {"n": "Bob", "s": 420}, ... ],
  "level2": [ ... ],
  ...
}
"""

import json
from pathlib import Path
from typing import List, Tuple

from ..core.settings import SAVE_DIR

SAVE_DIR.mkdir(exist_ok=True)
_SCORES_PATH = SAVE_DIR / "scores.json"


# ────────────────────────────────────────────────────────────
def _load_raw() -> dict:
    if _SCORES_PATH.exists():
        return json.loads(_SCORES_PATH.read_text())
    return {}


def _dump_raw(data: dict) -> None:
    _SCORES_PATH.write_text(json.dumps(data, indent=2))


# ────────────────────────────────────────────────────────────
def add_score(level_name: str, nick: str, value: int) -> None:
    """Dodaj wynik; posortuj malejąco; zachowaj max 30 rekordów/level."""
    data = _load_raw()
    lst = data.setdefault(level_name, [])
    lst.append({"n": nick, "s": int(value)})

    # sort malejąco i obetnij
    lst.sort(key=lambda d: d["s"], reverse=True)
    data[level_name] = lst[:30]
    _dump_raw(data)


def get_top(level_name: str, n: int = 5) -> List[Tuple[str, int]]:
    """Zwraca listę (nick, score) — maksymalnie n rekordów."""
    data = _load_raw()
    return [(d["n"], d["s"]) for d in data.get(level_name, [])][:n]
