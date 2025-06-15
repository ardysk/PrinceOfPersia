from __future__ import annotations
from functools import lru_cache
from pathlib import Path

import pygame

# ────────────────────────────────────────────────────────────────
# STAŁE I KATALOGI

from ..core.settings import (
    IMG_DIR,          # assets/images/
    SND_DIR,          # assets/sounds/
    DEFAULT_VOLUME,   # domyślna głośność (0–1)
    MUSIC_FILE        # np. "music.mp3"
)

# ────────────────────────────────────────────────────────────────
# INICJALIZACJA PYGAME MIXER

pygame.mixer.init()

# ────────────────────────────────────────────────────────────────
# ŁADOWANIE GRAFIKI

@lru_cache(maxsize=256)
def image(name: str) -> pygame.Surface:
    """
    Ładuje grafikę z assets/images/<name> i zwraca ją jako Surface z alpha.
    `name` może zawierać podkatalogi, np. "iso_block/iso_block_1.png".
    """
    return pygame.image.load(IMG_DIR / name).convert_alpha()

# ────────────────────────────────────────────────────────────────
# ŁADOWANIE DŹWIĘKU

@lru_cache(maxsize=64)
def sound(name: str) -> pygame.mixer.Sound:
    """
    Ładuje efekt z assets/sounds/<name>.
    """
    return pygame.mixer.Sound(SND_DIR / name)


def set_master_volume(vol: float) -> None:
    """
    Globalna regulacja głośności (0–1) – obejmuje muzykę i wszystkie kanały.
    """
    vol = max(0.0, min(1.0, vol))
    pygame.mixer.music.set_volume(vol)
    for i in range(pygame.mixer.get_num_channels()):
        pygame.mixer.Channel(i).set_volume(vol)


def play(name: str) -> None:
    """
    Odtwórz pojedynczy efekt dźwiękowy z uwzględnieniem bieżącej głośności.
    """
    snd = sound(name)
    snd.set_volume(pygame.mixer.music.get_volume())
    snd.play()

# ────────────────────────────────────────────────────────────────
# MUZYKA W TLE – inicjowana jednokrotnie

def _init_music() -> None:
    """
    Ładuje i zapętla podkład muzyczny, jeśli jeszcze nie gra.
    """
    if not pygame.mixer.music.get_busy():
        pygame.mixer.music.load(SND_DIR / MUSIC_FILE)
        pygame.mixer.music.set_volume(DEFAULT_VOLUME)
        pygame.mixer.music.play(-1)      # pętla nieskończona

_init_music()

# ────────────────────────────────────────────────────────────────
# POMOCNICZE: sprite-sheet → klatki

def slice_sheet(sheet: pygame.Surface, w: int, h: int) -> list[pygame.Surface]:
    """
    Dzieli sprite-sheet na kafelki w×h; pomija niepełne komórki na krawędziach.
    """
    frames: list[pygame.Surface] = []
    cols = sheet.get_width()  // w
    rows = sheet.get_height() // h
    for row in range(rows):
        for col in range(cols):
            x, y = col * w, row * h
            frames.append(sheet.subsurface((x, y, w, h)).copy())
    return frames


def load_animation(folder: str, count: int) -> list[pygame.Surface]:
    """
    Ładuje <count> kolejnych klatek z katalogu assets/images/<folder>/.
    Jeśli którejś brak, duplikuje ostatnią odczytaną, aby nie wyrzucać wyjątku.
    """
    frames: list[pygame.Surface] = []
    for i in range(1, count + 1):
        rel = f"{folder}/{folder}_{i}.png"
        path = IMG_DIR / rel
        if path.exists():
            frames.append(image(rel))
        else:
            if frames:
                frames.append(frames[-1])           # duplikuj ostatnią
            else:
                raise FileNotFoundError(f"Brak pierwszej klatki animacji: {rel}")
    return frames


def load_images_from_folder(folder: str) -> list[pygame.Surface]:
    """
    Zwraca wszystkie .png z assets/images/<folder>/ posortowane alfabetycznie.
    """
    dir_path: Path = IMG_DIR / folder
    if not dir_path.exists():
        raise FileNotFoundError(f"Folder z obrazami nie istnieje: {dir_path}")

    frames: list[pygame.Surface] = []
    for file in sorted(dir_path.iterdir()):
        if file.suffix.lower() == ".png":
            frames.append(pygame.image.load(file).convert_alpha())
    return frames
