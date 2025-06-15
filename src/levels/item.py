import pygame

class Item(pygame.sprite.Sprite):
    def __init__(self, pos, surf: pygame.Surface, name: str, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft=pos)
        self.name = name
