import pygame
from .base import BaseEntity

class Projectile(BaseEntity):
    def __init__(self, pos, groups, velocity):
        # prosta żółta kwadratowa kula jako placeholder
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        surf.fill((255, 220, 0))
        animations = {"idle": [surf]}
        super().__init__(pos, groups, animations)
        self.vel = pygame.math.Vector2(velocity)

    def update(self, dt):
        self.rect.x += int(self.vel.x * dt)
        self.rect.y += int(self.vel.y * dt)
        super().update(dt)
