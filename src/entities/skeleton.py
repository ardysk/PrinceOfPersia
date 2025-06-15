# src/entities/skeleton.py
import random
import math
import pygame

from ..utils.loader import load_animation
from .base import BaseEntity
from ..core.settings import TILE


class Skeleton(BaseEntity):
    # ─── AI parameters ─────────────────────────────────────────────
    DETECT_RADIUS = 250          # px
    MELEE_RANGE   = 40           # px (centre–centre)
    SPD_PATROL    = 70           # px / s
    SPD_CHASE     = 120          # px / s
    TURN_DELAY    = (1.0, 2.5)   # random re-direction, patrol
    ATK_COOLDOWN  = 0.8          # seconds
    DMG           = 25           # damage dealt to player
    MAX_HP        = 40

    # ─── iso helpers (same as Player / Bandit) ─────────────────────
    SPX  = TILE // 3
    SPY  = TILE // 6
    NORM = 1 / math.hypot(SPX, SPY)

    FOOT_SHIFT_Y = TILE // 2     # push sprite down; foot on floor

    # ───────────────────────────────────────────────────────────────
    def __init__(self, pos, groups, game):
        # load & scale 50 %
        frames = [
            pygame.transform.scale(
                f, (int(f.get_width() * 0.5), int(f.get_height() * 0.5))
            )
            for f in load_animation("iso_skeleton_contrast", 2)
        ]
        animations = {"idle": frames, "run": frames}
        super().__init__(pos, groups, animations, anim_interval=0.15)

        self.game = game
        # initial position: slightly lower so feet hit the tile
        self.pos = pygame.math.Vector2(pos[0], pos[1] + self.FOOT_SHIFT_Y)

        # random iso direction
        self._pick_new_dir()
        self.turn_t = random.uniform(*self.TURN_DELAY)

        # combat
        self.hp    = self.MAX_HP
        self.atk_t = 0.0

    # ───────── internal helpers ────────────────────────────────────
    def _pick_new_dir(self):
        while True:
            dx, dy = random.choice((-1, 0, 1)), random.choice((-1, 0, 1))
            if dx or dy:
                break
        self.dir_iso = pygame.math.Vector2(dx, dy)

    def _iso_vel(self, speed):
        vx = (self.dir_iso.x - self.dir_iso.y) * self.SPX
        vy = (self.dir_iso.x + self.dir_iso.y) * self.SPY
        return pygame.math.Vector2(vx, vy) * (speed * self.NORM)

    @staticmethod
    def _foot_ok(pos, rect, floor_mask):
        """Check three foot points (¼, ½, ¾ width) are on floor."""
        foot_y = int(pos.y + rect.height - 2)
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

    # ───────── main update ─────────────────────────────────────────
    def update(self, dt: float):
        level = self.game.states.state
        floor_mask = getattr(level, "floor_mask", None)
        if floor_mask is None:
            return

        world_off = level.world_rect.topleft
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

        test_x = next_pos.x - world_off[0]
        test_y = next_pos.y - world_off[1]
        foot_y = int(test_y + self.rect.height - 2)
        xs = [
            int(test_x + self.rect.width * 0.25),
            int(test_x + self.rect.width * 0.50),
            int(test_x + self.rect.width * 0.75),
        ]
        mw, mh = floor_mask.get_size()
        ok = all(0 <= px < mw and 0 <= foot_y < mh and floor_mask.get_at((px, foot_y))
                 for px in xs)

        if ok:
            self.pos = next_pos
        else:
            self._pick_new_dir()

        # ── atak wręcz ─────────────────────────────────────
        if chasing and dist_player <= self.MELEE_RANGE and self.atk_t <= 0:
            if hasattr(level, "_apply_damage"):
                level._apply_damage(self.DMG)
            self.atk_t = self.ATK_COOLDOWN

        self.atk_t = max(0, self.atk_t - dt)

        # ── animacja / render ─────────────────────────────
        self.state = "run"
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))
        super().update(dt)
