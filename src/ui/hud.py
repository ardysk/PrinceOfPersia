# src/ui/hud.py

import time
import pygame
from ..core.settings import WIDTH

class HUD:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 24)

    def draw(self, screen):
        # ——— szukamy instancji Player ———
        player = getattr(self.game, "player", None)
        if player is None:
            # może gra jeszcze nie przypisała; spróbuj w stanie maszyny
            player = getattr(self.game.states.state, "player", None)

        # 1) HP
        if player is not None:
            hp_text = f"HP: {max(player.hp, 0)}/{player.max_hp}"
        else:
            hp_text = "HP: --/--"
        hp_surf = self.font.render(hp_text, True, (255, 0, 0))
        screen.blit(hp_surf, (10, 10))

        # 2) Level
        lvl_index = getattr(self.game, "level_index", None)
        lvl_text = f"Level: {lvl_index + 1}" if lvl_index is not None else "Level: --"
        lvl_surf = self.font.render(lvl_text, True, (255, 255, 255))
        screen.blit(lvl_surf, (10, 10 + hp_surf.get_height() + 5))

        # 3) Time
        if self.game.start_time is not None and not self.game.game_over_flag:
            elapsed = int(time.time() - self.game.start_time)
            time_text = f"Time: {elapsed}s"
            time_surf = self.font.render(time_text, True, (200, 200, 200))
            screen.blit(time_surf, (WIDTH - time_surf.get_width() - 10, 10))
