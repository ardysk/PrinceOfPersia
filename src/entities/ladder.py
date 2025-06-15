import pygame
from .base import BaseEntity
from ..utils.loader import image

class Ladder(BaseEntity):
    def __init__(self, pos, *groups):
        # wczytujemy i skalujemy drabinę (64×64)
        surf = image("iso_lader/iso_lader.png")
        surf = pygame.transform.scale(surf, (surf.get_width()//2, surf.get_height()//2))
        super().__init__(pos, groups, {"idle":[surf]}, anim_interval=1.0)