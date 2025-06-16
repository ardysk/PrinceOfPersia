import json
from pathlib import Path

import pygame
import pygame_menu

from ..core.settings import (
    WIDTH, HEIGHT, IMG_DIR,
    CFG_DIR,           # …/config/
    DEFAULT_VOLUME     # domyślna głośność (0-1)
)
from ..utils.loader import set_master_volume
from ..utils.save      import add_score, get_top
from functools import partial
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

        self.menu = pygame_menu.Menu("", WIDTH, HEIGHT, theme=theme)
        self.menu.add.vertical_margin(120)

        self.menu.add.button("NEW GAME", self._new_game)
        self.menu.add.button("SCORES", self._open_scores)  # ← NOWY
        self.menu.add.button("OPTIONS", self._options)  # ← zmodyfikowany (patrz niżej)
        self.menu.add.button("QUIT", pygame_menu.events.EXIT)

        pygame.mouse.set_visible(False)

    # ────────────────────────────────────────────────────────────────
    # CALLBACKI

    def _new_game(self):
        self.game.level_index = 0
        self.game.start_level()

    # --- menu OPTIONS -------------------------------------------------

        # ─────────────────────────────────────────────────────────────
        #  _options  (zastąp całą metodę)
        # ─────────────────────────────────────────────────────────────
    def _options(self):
        """Pod-menu ustawień: nick + głośność."""
        sub_theme = self.menu.get_theme().copy()
        sub_theme.background_color = (10, 35, 80)          # ciemny niebieski
        sub_theme.title_font_size   = 40
        sub_theme.widget_font_color = (255, 173, 46)       # pomarańcz

        theme = self.menu.get_theme().copy()
        sub = pygame_menu.Menu("Options", WIDTH * 0.8, HEIGHT * 0.8, theme=sub_theme)

        # — Nickname —
        def _set_nick(text):
            self.game.nick = (text.strip() or "Player")[:12]

        sub.add.text_input("Nickname: ", default=self.game.nick,
                            maxchar=12, onchange=_set_nick)

        # — Master volume —
        cfg_path = CFG_DIR / "user_settings.json"
        current = DEFAULT_VOLUME
        if cfg_path.exists():
            try:
                current = json.loads(cfg_path.read_text()).get("volume", DEFAULT_VOLUME)
            except Exception:
                pass

        slider = sub.add.range_slider(
            "Volume: ",
            default=current,
            range_values=(0, 1),
            increment=0.05,
            width=300,
            value_format=lambda v: f"{int(v * 100)}%"
        )

        def _apply():
            vol = slider.get_value()
            set_master_volume(vol)
            cfg_path.parent.mkdir(exist_ok=True)
            cfg_path.write_text(json.dumps({"volume": vol}, indent=2))
            sub._back()  # zamknij pod-menu

        sub.add.button("Apply", _apply)
        sub.add.button("Back", pygame_menu.events.BACK)
        self.menu._open(sub)

    # ────────────────────────────────────────────────────────────────
    # STATE-MACHINE HOOKS

    def handle_event(self, event: pygame.event.Event):
        self.menu.update([event])

    def update(self, dt: float):
        pass  # statyczne menu – brak logiki czasowej

    def draw(self, screen: pygame.Surface):
        self.menu.draw(screen)

# ─────────────────────────────────────────────────────────────
#  _open_scores  (nowa / poprawiona metoda – wklej JAKO osobną
#  metodę klasy, np. tuż nad handle_event)
# ─────────────────────────────────────────────────────────────
    def _open_scores(self):
        """Wyświetla TOP-5 dla każdego poziomu w mniejszym, wyśrodkowanym oknie."""

        sub_theme = self.menu.get_theme().copy()
        sub_theme.background_color = (10, 35, 80)          # ciemny niebieski
        sub_theme.title_font_size   = 40
        sub_theme.widget_font_color = (255, 173, 46)       # pomarańcz

        sub = pygame_menu.Menu(
            title="High-Scores",
            width=WIDTH * 0.7,
            height=HEIGHT * 0.7,
            theme=sub_theme,
        )

        for i in range(len(self.game.levels)):
            lvl_name = f"level{i + 1}"
            rows = get_top(lvl_name, 5)

            # nagłówek poziomu
            sub.add.label(f"[ {lvl_name.upper()} ]",
                          font_size=30,
                          align=pygame_menu.locals.ALIGN_CENTER)

            if not rows:
                sub.add.label("(no scores yet)",
                              font_size=24,
                              align=pygame_menu.locals.ALIGN_CENTER)
            else:
                for rank, (nick, sc) in enumerate(rows, 1):
                    sub.add.label(f"{rank} {nick:<12} {sc:>5}",
                                  font_size=24,
                                  align=pygame_menu.locals.ALIGN_CENTER)

            sub.add.vertical_margin(12)

        sub.add.vertical_margin(20)
        sub.add.button("Back", pygame_menu.events.BACK)
        self.menu._open(sub)


