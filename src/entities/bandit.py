# src/entities/bandit.py
import random
import math
import pygame

from ..utils.loader import load_animation
from .base import BaseEntity
from ..core.settings import TILE


class Bandit(BaseEntity):
    """Bandyta patroluje izometrycznie po całej podłodze, a w promieniu DETECT_RADIUS ściga gracza.
    Nigdy nie schodzi z kafelków, bo każdy krok jest sprawdzany maską floor_mask."""

    # ───────── STAŁE AI ────────────────────────────────────────────────────────
    DETECT_RADIUS = 250      # zasięg zauważenia gracza   [px]
    MELEE_RANGE   = 40       # dystans ciosu              [px]
    SPD_PATROL    = 60       # prędkość w patrolu         [px/s]
    SPD_CHASE     = 110      # prędkość w pościgu         [px/s]
    TURN_DELAY    = (1.2, 3.0)   # losowa zmiana kierunku w patrolu  [s]
    ATK_COOLDOWN  = 0.8      # odstęp między ciosami      [s]
    DMG           = 10       # obrażenia zadawane graczowi
    MAX_HP        = 30

    # ───────── IZOMETRIA ───────────────────────────────────────────────────────
    SPX  = TILE // 3         # przesunięcie x dla v=(1,0)
    SPY  = TILE // 6         # przesunięcie y dla v=(1,0)
    NORM = 1 / math.hypot(SPX, SPY)  # do skalowania prędkości

    FOOT_SHIFT_Y = TILE // 2  # obniżenie sprite’a, by stopa trafiała w romb

    # ───────────────────────────────────────────────────────────────────────────
    def __init__(self, pos, groups, game):
        frames = [
            pygame.transform.scale(
                f, (int(f.get_width() * 0.5), int(f.get_height() * 0.5))
            )
            for f in load_animation("iso_bandit", 4)
        ]
        animations = {"idle": frames, "run": frames}
        super().__init__(pos, groups, animations, anim_interval=0.12)

        self.game = game
        # startujemy lekko niżej, żeby stopa była na podłodze
        self.pos = pygame.math.Vector2(pos[0], pos[1] + self.FOOT_SHIFT_Y)

        # losowy kierunek izometryczny (dx,dy ∈ {-1,0,1} \ {(0,0)})
        self._pick_new_dir()
        self.turn_t = random.uniform(*self.TURN_DELAY)

        # walka
        self.hp    = self.MAX_HP
        self.atk_t = 0.0    # timer cooldownu ciosu

    # ───────── POMOCNICZE ──────────────────────────────────────────────────────
    def _pick_new_dir(self):
        while True:
            dx = random.choice((-1, 0, 1))
            dy = random.choice((-1, 0, 1))
            if dx or dy:
                break
        self.dir_iso = pygame.math.Vector2(dx, dy)

    def _iso_vel(self, speed: float) -> pygame.math.Vector2:
        vx = (self.dir_iso.x - self.dir_iso.y) * self.SPX
        vy = (self.dir_iso.x + self.dir_iso.y) * self.SPY
        return pygame.math.Vector2(vx, vy) * (speed * self.NORM)

    @staticmethod
    def _foot_ok(pos: pygame.math.Vector2,
                 rect: pygame.Rect,
                 floor_mask: pygame.mask.Mask) -> bool:
        """True jeśli CAŁA szerokość stopy (3 próbki) stoi na podłodze."""
        foot_y = int(pos.y + rect.height - 2)

        # lewa ¼, środek, prawa ¾ sprite’a
        xs = [
            int(pos.x + rect.width * 0.25),
            int(pos.x + rect.width * 0.50),
            int(pos.x + rect.width * 0.75),
        ]
        w, h = floor_mask.get_size()
        for px in xs:
            if not (0 <= px < w and 0 <= foot_y < h):
                return False
            if floor_mask.get_at((px, foot_y)) == 0:
                return False
        return True

    # ───────── GŁÓWNA AKTUALIZACJA ────────────────────────────────────────────
    def update(self, dt: float):
        level = self.game.states.state
        floor_mask = getattr(level, "floor_mask", None)
        if floor_mask is None:
            return

        world_off = level.world_rect.topleft  # ← ♻  przesunięcie mapy
        player = getattr(self.game, "player", None)
        dist_player = (pygame.math.Vector2(player.rect.center) - self.pos).length() \
            if player else 1e9
        chasing = dist_player <= self.DETECT_RADIUS

        # ── kierunek / prędkość ───────────────────────────
        if chasing:
            vec = pygame.math.Vector2(player.rect.center) - self.pos
            if vec.length_squared():
                self.dir_iso = pygame.math.Vector2(
                    math.copysign(1, vec.x) if abs(vec.x) > abs(vec.y) else 0,
                    math.copysign(1, vec.y) if abs(vec.y) >= abs(vec.x) else 0,
                )
            speed = self.SPD_CHASE
        else:
            self.turn_t -= dt
            if self.turn_t <= 0:
                self._pick_new_dir()
                self.turn_t = random.uniform(*self.TURN_DELAY)
            speed = self.SPD_PATROL

        # ── próba ruchu ───────────────────────────────────
        vel = self._iso_vel(speed)
        next_pos = self.pos + vel * dt

        # lokalne współrzędne maski
        test_x = next_pos.x - world_off[0]
        test_y = next_pos.y - world_off[1]
        foot_y = int(test_y + self.rect.height - 2)
        xs = [
            int(test_x + self.rect.width * 0.25),
            int(test_x + self.rect.width * 0.50),
            int(test_x + self.rect.width * 0.75),
        ]
        ok = True
        mw, mh = floor_mask.get_size()
        for px in xs:
            if not (0 <= px < mw and 0 <= foot_y < mh) or floor_mask.get_at((px, foot_y)) == 0:
                ok = False
                break

        if ok:
            self.pos = next_pos
        else:
            self._pick_new_dir()

        # ── walka wręcz ───────────────────────────────────
        if chasing and dist_player <= self.MELEE_RANGE and self.atk_t <= 0:
            if hasattr(level, "_apply_damage"):
                level._apply_damage(self.DMG)
            self.atk_t = self.ATK_COOLDOWN

        self.atk_t = max(0.0, self.atk_t - dt)

        # ── animacja / render ─────────────────────────────
        self.state = "run"
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))
        super().update(dt)

