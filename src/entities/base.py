import pygame

class BaseEntity(pygame.sprite.Sprite):
    def __init__(self, pos, groups, animations: dict[str, list[pygame.Surface]], anim_interval: float = 0.12):
        super().__init__(groups)
        self.animations    = animations
        self.state         = "idle"
        self.frame_index   = 0
        self.anim_interval = anim_interval  # czas [s] między klatkami
        self.anim_timer    = 0.0

        # ustaw pierwszy obraz i maskę
        self.image = self.animations[self.state][0]
        self.mask  = pygame.mask.from_surface(self.image)
        self.rect  = self.image.get_rect(topleft=pos)

    def animate(self, dt: float):
        seq = self.animations[self.state]
        self.anim_timer += dt
        # jeżeli upłynęło wystarczająco dużo czasu, przejdź do kolejnej klatki
        if self.anim_timer >= self.anim_interval:
            # ile klatek przeskoczyć?
            frames_advance = int(self.anim_timer / self.anim_interval)
            self.frame_index = (self.frame_index + frames_advance) % len(seq)
            self.anim_timer %= self.anim_interval
            self.image = seq[int(self.frame_index)]
            self.mask  = pygame.mask.from_surface(self.image)

    def update(self, dt: float = 0):
        # dt przekazywane z Game.run()
        self.animate(dt)
