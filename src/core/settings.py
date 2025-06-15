from pathlib import Path

# OKNO
WIDTH, HEIGHT = 960, 540
FPS = 60

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
DEFAULT_VOLUME = 0.6

# PLIKI AUDIO
MUSIC_FILE      = "music.mp3"
SND_JUMP        = "jump.mp3"
SND_PUNCH       = "punch.mp3"
SND_GAME_OVER   = "game_over.mp3"
