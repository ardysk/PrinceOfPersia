# src/entities/player.py

import math
import pygame
from ..core.settings import TILE
from ..utils.loader import load_animation
from ..core.settings import SND_JUMP, SND_PUNCH
from ..utils.loader  import play
from .base import BaseEntity

class Player(BaseEntity):
    def __init__(self, pos, groups):
        animations = {
            "idle":   load_animation("iso_prince_hero",        3),
            "run":    load_animation("iso_prince_hero_run",    3),
            "climb":  load_animation("iso_prince_hero_climb",  1),
            "crouch": load_animation("iso_prince_crouch",      1),
            "attack": load_animation("iso_prince_hero_attack", 1),   # <- nowy sprite
        }

        # skalowanie 128×128 → 64×64
        for state, frames in animations.items():
            animations[state] = [
                pygame.transform.scale(
                    f, (f.get_width() // 2, f.get_height() // 2)
                )
                for f in frames
            ]
        super().__init__(pos, groups, animations, anim_interval=0.15)

        # pozycja i ruch
        self.pos   = pygame.math.Vector2(self.rect.topleft)
        self.vel   = pygame.math.Vector2(0, 0)
        self.speed = 200

        # skok
        self.gravity    = 800.0
        self.jump_vel   = -300.0
        self.jumping    = False
        self.vz         = 0.0
        self.z_offset   = 0.0

        # spadanie poza mapę
        self.falling_off = False
        self.fall_vel    = 0.0

        # izometria
        self.spx   = TILE // 3
        self.spy   = TILE // 6
        self._norm = self.speed / math.hypot(self.spx, self.spy)

        # walka
        self.state        = "idle"
        self.attack_timer = 0.0
        self.attack_dur   = 0.3

        # zdrowie
        self.max_hp = 100
        self.hp     = self.max_hp

        # punkty
        self.score = 0       # licznik zdobytych punktów

        # nieczułość po trafieniu
        self.invul_timer  = 0.0
        self._blink_timer = 0.0
        self._blink_state = True

        # kierunek patrzenia (start – w prawo)
        self.facing = pygame.math.Vector2(1, 0)

    def handle_input(self):
        if self.falling_off:
            return

        keys = pygame.key.get_pressed()
        dx = dy = 0

        # ruch
        if keys[pygame.K_LEFT]:
            dx, self.state = -1, "run"
        elif keys[pygame.K_RIGHT]:
            dx, self.state = 1, "run"
        if keys[pygame.K_UP]:
            dy, self.state = -1, "run"
        elif keys[pygame.K_DOWN]:
            dy, self.state = 1, "run"
        if dx == 0 and dy == 0 and self.state != "attack":
            self.state = "idle"

        # skok
        if keys[pygame.K_SPACE] and not self.jumping and not self.falling_off:
            self.jumping = True
            self.vz = self.jump_vel
            self.z_offset = 0.0
            play(SND_JUMP)
            # ----------------  ATAK  ----------------
        if not hasattr(self, "attack_ready"):
            self.attack_ready = True  # inicjalizacja przy pierwszym wywołaniu

        key_attack = keys[pygame.K_g]

        # rozpocznij atak tylko, jeśli klawisz został _wciśnięty_
        if key_attack and self.attack_ready and self.state != "attack":
            self.state = "attack"
            self.attack_timer = 0.0
            self.attack_ready = False  # blokada trzymania przycisku
            play(SND_PUNCH)
            # odblokuj możliwość ataku po puszczeniu klawisza
        if not key_attack:
            self.attack_ready = True

        # normalizacja prędkości izometrycznej
        if dx and dy:
            m = 1 / math.sqrt(2)
            dx *= m
            dy *= m
        vx0 = dx - dy
        vy0 = dx + dy
        self.vel.x = vx0 * self.spx * self._norm
        self.vel.y = vy0 * self.spy * self._norm

        # zapamiętaj kierunek patrzenia, gdy bohater się porusza
        if dx or dy:
            self.facing = pygame.math.Vector2(vx0, vy0).normalize()

    def attack_hitbox(self) -> pygame.Rect | None:
        """Zwraca prostokąt trafienia miecza (lub None, gdy brak)."""
        if self.state != "attack":
            return None
        if self.attack_timer > 0.15:          # okno trafienia: pierwsze 150 ms
            return None

        # rozmiar hit-boxu
        w, h = 60, 40
        offset = self.facing * 35             # odsunięcie od środka gracza

        cx = self.rect.centerx + offset.x
        cy = self.rect.centery + offset.y

        return pygame.Rect(cx - w // 2, cy - h // 2, w, h)

    def update(self, dt: float):
        # 1) animacja ataku
        if self.state == "attack":
            self.attack_timer += dt
            if self.attack_timer >= self.attack_dur:
                self.state = "idle"
                self.attack_timer = 0.0

        # 2) ruch i grawitacja
        if self.jumping or self.falling_off:
            self.handle_input()
            self.vz += self.gravity * dt
            self.z_offset += self.vz * dt
            self.pos += self.vel * dt

            if self.jumping and self.z_offset >= 0:
                self.z_offset = 0
                self.jumping = False

            if self.falling_off:
                self.fall_vel += self.gravity * dt
                self.pos.y += self.fall_vel * dt

            self.rect.topleft = (int(self.pos.x), int(self.pos.y + self.z_offset))
        else:
            self.handle_input()
            self.pos += self.vel * dt
            self.rect.topleft = (int(self.pos.x), int(self.pos.y))

        # 3) zwykła animacja klatek (BaseEntity)
        super().update(dt)

        # 4) nieczułość + miganie — nie dotykamy oryginalnych klatek!
        if self.invul_timer > 0:
            self.invul_timer -= dt
            self._blink_timer += dt
            if self._blink_timer >= 0.1:
                self._blink_timer = 0.0
                self._blink_state = not self._blink_state

            # kopiujemy bieżącą klatkę, aby nie psuć tej z cache
            self.image = self.image.copy()
            self.image.set_alpha(128 if self._blink_state else 0)
        else:
            self._blink_state = True  # widoczny
            # upewnij się, że klatka jest w 100 % widoczna
            self.image = self.image.copy()
            self.image.set_alpha(255)
