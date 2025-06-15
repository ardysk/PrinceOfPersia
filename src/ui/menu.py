import json
from pathlib import Path

import pygame
import pygame_menu

from ..core.settings import (
    WIDTH, HEIGHT, IMG_DIR,
    CFG_DIR,           # …/config/
    DEFAULT_VOLUME     # domyślna głośność (0-1)
)
from ..utils.save   import load_scores
from ..utils.loader import set_master_volume
from ..levels.level import Level


class MainMenu:
    """Start screen with background image, logo and four buttons."""

    BG_PATH = IMG_DIR / "iso-menu" / "iso-meny.png"

    def __init__(self, game):
        self.game = game

        # ─── background image ──────────────────────────────────────────
        bg = pygame_menu.baseimage.BaseImage(
            image_path=str(self.BG_PATH),
            drawing_mode=pygame_menu.baseimage.IMAGE_MODE_FILL,
        )

        theme = pygame_menu.themes.Theme(
            background_color=bg,
            title=False,                          # hide default title bar

            widget_font=pygame_menu.font.FONT_8BIT,
            widget_font_size=32,
            widget_font_color=(255, 173, 46),     # warm orange
            selection_color=(255, 255, 255),

            widget_alignment=pygame_menu.locals.ALIGN_CENTER,
            widget_margin=(0, 20),
            widget_selection_effect=pygame_menu.widgets.NoneSelection(),
        )

        # pierwszy argument to *title* – podaj pusty string
        self.menu = pygame_menu.Menu("", WIDTH, HEIGHT, theme=theme)

        # opuszczamy blok przycisków niżej (≈ wysokość jednego przycisku)
        self.menu.add.vertical_margin(120)

        # ─── przyciski ────────────────────────────────────────────────
        self.menu.add.button("NEW GAME", self._new_game)
        self.menu.add.button("LOAD",     self._load_game)
        self.menu.add.button("OPTIONS",  self._options)
        self.menu.add.button("QUIT",     pygame_menu.events.EXIT)

        pygame.mouse.set_visible(False)

    # ────────────────────────────────────────────────────────────────
    # CALLBACKI

    def _new_game(self):
        self.game.level_index = 0
        self.game.start_level()

    def _load_game(self):
        data = load_scores()
        last = data.get("last_level", 0)
        self.game.level_index = max(0, min(last, len(self.game.levels) - 1))
        self.game.start_level()

    # --- menu OPTIONS -------------------------------------------------

    def _options(self):
        sub = pygame_menu.Menu("Options", WIDTH * 0.8, HEIGHT * 0.8)

        # wczytaj zapisany poziom głośności (albo domyślny)
        cfg_path: Path = CFG_DIR / "user_settings.json"
        volume = DEFAULT_VOLUME
        if cfg_path.exists():
            try:
                volume = json.loads(cfg_path.read_text()).get("volume", DEFAULT_VOLUME)
            except Exception:
                pass

        # suwak 0–100 %
        slider = sub.add.range_slider(
            "Master Volume :",
            default=volume,
            range_values=(0, 1),
            increment=0.05,
            width=300,
            value_format=lambda v: f"{int(v * 100)}%"
        )

        def _apply():
            vol = slider.get_value()
            set_master_volume(vol)                # natychmiastowa zmiana
            cfg_path.parent.mkdir(exist_ok=True)
            cfg_path.write_text(json.dumps({"volume": vol}, indent=2))
            pygame_menu.events.BACK

        sub.add.button("Apply", _apply)
        sub.add.button("Back",  pygame_menu.events.BACK)

        self.menu._open(sub)

    # ────────────────────────────────────────────────────────────────
    # STATE-MACHINE HOOKS

    def handle_event(self, event: pygame.event.Event):
        self.menu.update([event])

    def update(self, dt: float):
        pass  # statyczne menu – brak logiki czasowej

    def draw(self, screen: pygame.Surface):
        self.menu.draw(screen)
