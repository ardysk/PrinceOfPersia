import random, pygame
from ..utils.loader import load_animation
from .base import BaseEntity

class Bat(BaseEntity):
    SPD_FLY       = 120
    ATK_COOLDOWN  = 0.8
    DMG           = 10
    TURN_DELAY    = (1.0, 3.0)    # losowa zmiana kierunku

    def __init__(self, pos, groups, game):
        frames = load_animation("iso_bat_contrast", 4)
        frames = [pygame.transform.scale(f, (f.get_width()//2, f.get_height()//2))
                  for f in frames]                  # 2× mniejszy
        super().__init__(pos, groups, {"idle": frames}, anim_interval=0.1)

        self.game = game
        self.pos  = pygame.math.Vector2(pos)
        self.dir  = pygame.math.Vector2(random.uniform(-1,1), random.uniform(-1,1)).normalize()
        self.turn_timer = random.uniform(*self.TURN_DELAY)
        self.atk_t      = 0.0

    # ------------------------
    def _rand_turn(self):
        self.dir = pygame.math.Vector2(random.uniform(-1,1), random.uniform(-1,1))
        if self.dir.length_squared() == 0:
            self.dir = pygame.math.Vector2(1,0)
        self.dir = self.dir.normalize()
        self.turn_timer = random.uniform(*self.TURN_DELAY)

    # ------------------------
    def update(self, dt):
        # losowe latanie po całym ekranie
        self.turn_timer -= dt
        if self.turn_timer <= 0:
            self._rand_turn()

        self.pos += self.dir * self.SPD_FLY * dt

        # ogranicz do ekranu – odbij od krawędzi
        from ..core.settings import WIDTH, HEIGHT
        if self.pos.x < 0 or self.pos.x > WIDTH:
            self.dir.x *= -1
        if self.pos.y < 0 or self.pos.y > HEIGHT:
            self.dir.y *= -1
        self.pos.x = max(0, min(self.pos.x, WIDTH))
        self.pos.y = max(0, min(self.pos.y, HEIGHT))

        # atak na gracza
        player = getattr(self.game, "player", None)
        if player:
            if self.atk_t <= 0 and self.rect.colliderect(player.rect):
                level = self.game.states.state
                if hasattr(level, "_apply_damage"):
                    level._apply_damage(self.DMG)
                self.atk_t = self.ATK_COOLDOWN
        self.atk_t = max(0, self.atk_t - dt)

        self.rect.center = (int(self.pos.x), int(self.pos.y))
        super().update(dt)
