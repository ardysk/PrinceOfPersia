# src/entities/trap.py

import pygame
from ..utils.loader import load_animation
from .base import BaseEntity

class SpikeTrap(BaseEntity):
    def __init__(self, pos, groups):
        # 3 klatki: 0=zamknięte, 1=otwieranie, 2=otwarte
        animations = {
            "idle": load_animation("iso_spikes", 3)
        }
        super().__init__(pos, groups, animations)
        self.timer = 0.0
        self.cycle = 3.0    # pełny obrót (zamknięte→otwarte→...)
        self.damage_enabled = False

    def update(self, dt):
        # aktualizuj timer modulo pełnego cyklu
        self.timer = (self.timer + dt) % self.cycle
        # co sekundę przechodzimy do kolejnej klatki
        idx = int(self.timer // 1.0)  # 0,1 lub 2
        self.frame_index = idx
        # odśwież obraz i maskę
        self.image = self.animations["idle"][self.frame_index]
        self.mask  = pygame.mask.from_surface(self.image)
        # w pełni otwarte (idx==2) -> damage on
        self.damage_enabled = (idx == 2)

class FloorCollapse(BaseEntity):
    def __init__(self, pos, groups):
        animations = {
            "idle": load_animation("iso_floor_collapse", 2)
        }
        super().__init__(pos, groups, animations)
        self.triggered = False

    def trigger(self):
        self.triggered = True

    def update(self, dt):
        if self.triggered:
            # klatka „upadek”
            self.frame_index = 1
            self.image = self.animations["idle"][1]
            self.mask  = pygame.mask.from_surface(self.image)
        super().update(dt)

class BladeSpinner(BaseEntity):
    DMG        = 20          # obrażenia przy kontakcie
    SPIN_FPS   = 8           # ile klatek na sekundę

    def __init__(self, pos, groups):
        animations = {"idle": load_animation("iso_blade_spinner", 4)}
        super().__init__(pos, groups, animations)
        self.frame_index = 0

    def update(self, dt):
        # płynny obrót
        self.frame_index = (self.frame_index + self.SPIN_FPS * dt) % 4
        idx = int(self.frame_index)
        self.image = self.animations["idle"][idx]
        self.mask  = pygame.mask.from_surface(self.image)
        super().update(dt)
