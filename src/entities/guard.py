from ..utils.loader import load_animation
from .base import BaseEntity

class Guard(BaseEntity):
    def __init__(self, pos, groups):
        animations = {
            "idle": load_animation("iso_bandit", 4),  # możesz podmienić na iso_guard
        }
        super().__init__(pos, groups, animations)
        self.speed = 100

    def update(self, dt):
        # tu dodaj logikę ścigania gracza…
        super().update(dt)
