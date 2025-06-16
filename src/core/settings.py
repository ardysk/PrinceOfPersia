from pathlib import Path

# OKNO
WIDTH, HEIGHT = 960, 540
FPS = 60
# ──────────────────────────────────────────────────────────────
#  PUNKTACJA

ENEMY_POINTS = 50           # ile punktów za zabicie przeciwnika

# bonus za ukończenie poziomu w określonym czasie (sekundy → punkty)
TIME_BONUS = {
     60: 300,               # ≤  60 s  → +300 pkt
    120: 150,               # ≤ 120 s  → +150
    180:  50,               # ≤ 180 s  → +50
}

# ROZMIAR KAFELKA I ANIMACJI
TILE = 128

# ŚCIEŻKI (nie zmieniaj)
ROOT_DIR = Path(__file__).resolve().parents[2]
ASSETS   = ROOT_DIR / "assets"
IMG_DIR  = ASSETS / "images"
SND_DIR  = ASSETS / "sounds"
LVL_DIR  = ASSETS / "levels"
CFG_DIR  = ROOT_DIR / "config"
SAVE_DIR = ROOT_DIR / "saves"
DEFAULT_VOLUME = 0.3

# PLIKI AUDIO
MUSIC_FILE      = "music.mp3"
SND_JUMP        = "jump.mp3"
SND_PUNCH       = "punch.mp3"
SND_GAME_OVER   = "game_over.mp3"
