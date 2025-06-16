# src/core/game.py
import sys
import time
import pygame

from pathlib import Path
from .settings      import WIDTH, HEIGHT, FPS, LVL_DIR           # ← LVL_DIR
from .state_machine import StateMachine
from ..ui.menu      import MainMenu
from ..levels.level import Level


class Game:
    def __init__(self):
        self.nick = "Player"  # domyślny nick

        pygame.init()
        pygame.mixer.init()

        # stałe okno
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), 0)
        pygame.display.set_caption("Prince of Persia EDU")
        self.clock = pygame.time.Clock()

        # ─── DYNAMICZNA LISTA POZIOMÓW ───────────────────────────
        # zbiera wszystkie pliki level*.txt, sortuje alfabetycznie
        self.levels = sorted(
            p.name for p in LVL_DIR.glob("level*.txt")
        )
        if not self.levels:
            raise FileNotFoundError("No level*.txt files in assets/levels/")

        self.level_index = 0
        self.start_time  = None

        # game-over status
        self.game_over_flag   = False
        self.game_over_won    = False
        self.game_over_time   = 0.0
        self.game_over_levels = 0

        # begin in main menu
        self.states = StateMachine(MainMenu(self))

    # ──────────────────────────────────────────────────────────────
    def start_level(self):
        """Launch (or restart) current level_index."""
        if self.level_index >= len(self.levels):
            return  # safety guard – brak kolejnego poziomu

        self.start_time = time.time()

        fname      = self.levels[self.level_index]
        next_fname = self.levels[self.level_index + 1] \
                     if self.level_index + 1 < len(self.levels) else None

        level = Level(self, filename=fname, next_level=next_fname)

        level.camera.update(0, 0)     # ← przywracamy widok startowy
        self.player = level.player    # eksponujemy gracza (HUD / AI)
        self.states.change(level)

    # ──────────────────────────────────────────────────────────────
    def game_over(self, won: bool):
        """Called from Level when player dies OR finishes last level."""
        self.game_over_flag = True
        self.game_over_won  = won
        self.game_over_time = 0 if self.start_time is None \
                                else time.time() - self.start_time
        self.game_over_levels = self.level_index + (1 if won else 0)

    # ──────────────────────────────────────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # game-over screen
                if self.game_over_flag:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        # reset and go back to main menu
                        self.game_over_flag = False
                        self.level_index    = 0
                        self.start_time     = None
                        self.states.change(MainMenu(self))
                    continue

                # normal state events
                self.states.state.handle_event(event)

            # update
            if not self.game_over_flag:
                # if Start pressed in MainMenu
                if isinstance(self.states.state, MainMenu) and \
                   getattr(self.states.state, "start_pressed", False):
                    self.start_level()
                self.states.state.update(dt)

            # draw
            if self.game_over_flag:
                self._draw_game_over()
            else:
                self.states.state.draw(self.screen)

            pygame.display.flip()

    # ──────────────────────────────────────────────────────────────
    def _draw_game_over(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 48)

        if self.game_over_won:
            text = f"Congratulations! You finished {self.game_over_levels} level(s) in {int(self.game_over_time)}s"
        else:
            text = f"Game Over! Levels cleared: {self.game_over_levels}  Time: {int(self.game_over_time)}s"
        surf = font.render(text, True, (255, 255, 255))
        rect = surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(surf, rect)

        info = font.render("Press Enter to return to menu", True, (200, 200, 200))
        r2 = info.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        self.screen.blit(info, r2)


if __name__ == "__main__":
    Game().run()
