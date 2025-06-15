from .base import GameObject

class Enemy(GameObject):
    """Bazowa klasa przeciwnika – łagodny IA do nadpisania."""
    SPEED = 80

    def __init__(self, pos, *groups):
        super().__init__(*groups)
        # TODO: załaduj grafikę / animacje
        self.image = self._placeholder()
        self.rect = self.image.get_rect(topleft=pos)

    def _placeholder(self):
        import pygame
        surf = pygame.Surface((32, 32))
        surf.fill((200, 20, 20))
        return surf

    def update(self, dt):
        # Prosty patrol: w prawo → w lewo
        super().update(dt)
