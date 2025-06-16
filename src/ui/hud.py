# src/ui/hud.py
import time
import pygame
from ..core.settings import WIDTH

class HUD:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.Font(None, 24)

    def draw(self, screen):
        # 1) HP
        hp_txt = f"HP: {self.game.player.hp}/{self.game.player.max_hp}"
        hp_surf = self.font.render(hp_txt, True, (255, 0, 0))
        screen.blit(hp_surf, (10, 10))

        # 2) SCORE
        score_val = getattr(self.game.states.state, "score", 0)
        sc_txt = f"Score: {score_val}"
        sc_surf = self.font.render(sc_txt, True, (255, 173, 46))
        screen.blit(sc_surf, (10, 10 + hp_surf.get_height() + 5))

        # 3) LEVEL #
        lvl_idx = getattr(self.game, "level_index", 0) + 1
        lvl_surf = self.font.render(f"Level: {lvl_idx}", True, (200, 200, 200))
        screen.blit(lvl_surf, (10, 10 + hp_surf.get_height() + sc_surf.get_height() + 10))
