# src/levels/level.py

import sys
import pygame
from pygame.sprite import Group, spritecollide
from ..core.settings import LVL_DIR, TILE, WIDTH, HEIGHT
from ..entities.player   import Player
from ..entities.guard    import Guard
from ..entities.bat      import Bat
from ..entities.skeleton import Skeleton
from ..entities.bandit   import Bandit
from ..entities.ladder   import Ladder
from ..entities.trap     import SpikeTrap, FloorCollapse, BladeSpinner
from ..ui.hud            import HUD
from ..utils.loader      import image
from ..core.settings import SND_GAME_OVER
from ..utils.loader  import play



class Level:
    def __init__(self, game, filename="level01.txt", next_level=None, prev_hp=None):
        import pygame

        # ─── stałe obrażeń ──────────────────────────────────────
        self.SPIKE_DMG, self.BLADE_DMG, self.COLLAPSE_DMG = 30, 20, 15

        # ─── podstawy stanu ─────────────────────────────────────
        self.game, self.filename, self.next_lvl = game, filename, next_level

        self.hud     = HUD(game)
        self.world   = Group()
        self.enemies = Group()
        self.traps   = Group()
        self.ladders = Group()

        # początkowe przesunięcie statyczne (ręczne „kadrowanie” planszy)
        self.offset_x, self.offset_y = -260, -210

        # kamera & margines przewijania (¼ ekranu)
        self.camera    = pygame.math.Vector2(0, 0)
        self.SCROLL_X  = WIDTH // 4
        self.SCROLL_Y  = HEIGHT // 4

        # ─── tło okna ───────────────────────────────────────────
        try:
            self.bg = image("bgn/bgn.png")
        except pygame.error:
            self.bg = pygame.Surface((WIDTH, HEIGHT))
            self.bg.fill((30, 10, 0))

        # ─── kafle podłogi ──────────────────────────────────────
        plates = [image("iso_block/iso_plate_1.png"),
                  image("iso_block/iso_plate_2.png")]

        # ─── wczytanie ASCII-mapy do listy tmp_tiles ────────────
        lines = (LVL_DIR / filename).read_text().splitlines()
        spx, spy = TILE // 3, TILE // 6

        tmp_tiles = []
        for y, row in enumerate(lines):
            for x, ch in enumerate(row):
                if ch == "#":
                    continue
                wx = (x - y) * spx + WIDTH // 2 + self.offset_x
                wy = (x + y) * spy + 100      + self.offset_y
                tmp_tiles.append((x, y, wx, wy, ch))

        # ─── granice świata (lewy-górny i prawy-dolny kafla) ────
        left   = min(t[2] for t in tmp_tiles)
        right  = max(t[2] + plates[0].get_width()  for t in tmp_tiles)
        top    = min(t[3] for t in tmp_tiles)
        bottom = max(t[3] + plates[0].get_height() for t in tmp_tiles)
        self.world_rect = pygame.Rect(left, top, right - left, bottom - top)

        # ─── duża powierzchnia podłogi (rozmiar = cała mapa) ────
        self.floor_surface = pygame.Surface(
            (self.world_rect.width, self.world_rect.height), pygame.SRCALPHA
        )
        self.tile_positions = []

        # ─── rysowanie kafli + tworzenie obiektów ───────────────
        for x, y, wx, wy, ch in tmp_tiles:
            surf = plates[(x + y) % 2]
            # rysujemy względem lewego-górnego rogu mapy
            self.floor_surface.blit(surf, (wx - left, wy - top))
            self.tile_positions.append(
                pygame.Rect(wx, wy, surf.get_width(), surf.get_height())
            )

            pos = (wx, wy)
            if   ch == "P":
                self.player = Player(pos, self.world)
                if prev_hp is not None:
                    self.player.hp = max(0, min(prev_hp, self.player.max_hp))
            elif ch == "G":
                self.enemies.add(Guard(pos, self.world))
            elif ch == "b":
                self.enemies.add(Bat(pos, self.world, self.game))
            elif ch == "S":
                self.enemies.add(Skeleton(pos, self.world, self.game))
            elif ch == "B":
                self.enemies.add(Bandit(pos, self.world, self.game))
            elif ch == "L":
                Ladder(pos, self.world, self.ladders)
            elif ch in "^XO":
                trap_cls = {"^": SpikeTrap, "X": FloorCollapse, "O": BladeSpinner}[ch]
                t = trap_cls(pos, self.world)
                t.hit_rect = pygame.Rect(wx, wy, surf.get_width(), surf.get_height())
                t.hit_mask = pygame.mask.from_surface(surf)
                self.traps.add(t)

        # ─── maska podłogi (kolizja z przepaścią) ───────────────
        self.floor_mask = pygame.mask.from_surface(self.floor_surface)

    def _calc_patrol_bounds(self, pos):
        same_row = [r for r in self.tile_positions if abs(r.y - pos[1]) < 1]
        if not same_row:
            return pygame.Rect(0, 0, WIDTH, HEIGHT)
        left  = min(r.left  for r in same_row)
        right = max(r.right for r in same_row)
        return pygame.Rect(left, 0, right-left, HEIGHT)

    # ------------------------------------------------------------
    def _edge_scroll_camera(self):
        """Przesuwa kamerę, gdy gracz wpada w margines SCROLL_X / SCROLL_Y."""
        cx, cy = self.camera
        px, py = self.player.rect.center

        # współrzędne gracza względem okna
        screen_x = px - cx
        screen_y = py - cy

        # --- poziom: w lewo / w prawo ---
        if screen_x < self.SCROLL_X:
            cx = px - self.SCROLL_X
        elif screen_x > WIDTH - self.SCROLL_X:
            cx = px + self.SCROLL_X - WIDTH

        # --- pion: w górę / w dół ---
        if screen_y < self.SCROLL_Y:
            cy = py - self.SCROLL_Y
        elif screen_y > HEIGHT - self.SCROLL_Y:
            cy = py + self.SCROLL_Y - HEIGHT

        # klamrowanie do granic mapy
        cx = max(min(cx, self.world_rect.right  - WIDTH),  self.world_rect.left)
        cy = max(min(cy, self.world_rect.bottom - HEIGHT), self.world_rect.top)

        self.camera.update(cx, cy)


    def handle_event(self, event):
        pass
    def update(self, dt):
        # 0) uaktualnij animacje i AI wszystkich sprite’ów
        self.world.update(dt)

        # rozmiar maski podłogi (to CAŁA mapa, nie tylko okno)
        mw, mh = self.floor_mask.get_size()

        # 1) grawitacja / sprawdzanie, czy obiekt stoi nad kaflem
        for spr in self.world:
            if not hasattr(spr, "pos") or isinstance(spr, Bat):
                continue                        # nietoperze latają
            if getattr(spr, "jumping", False) or getattr(spr, "falling_off", False):
                continue                        # w locie już obsłużone

            # pozycja „stopy” w układzie świata
            foot_world = (spr.rect.centerx, spr.rect.bottom - 1)
            # lokalne współrzędne względem surface podłogi
            lx = foot_world[0] - self.world_rect.x
            ly = foot_world[1] - self.world_rect.y

            out = lx < 0 or lx >= mw or ly < 0 or ly >= mh
            bad = False
            if not out:
                bad = self.floor_mask.get_at((lx, ly)) == 0

            spr.falling_off = out or bad
            if not spr.falling_off and hasattr(spr, "fall_vel"):
                spr.fall_vel = 0

        # 2) przegrana przy upadku poza ekran
        if getattr(self, "player", None) and self.player.falling_off:
            if self.player.rect.top > HEIGHT + 200:
                play(SND_GAME_OVER)
                self.game.game_over(False)
                return

        if not getattr(self, "player", None):
            return  # brak gracza – dalsza logika niepotrzebna

        # 3) PUŁAPKI – kolizja stopą gracza
        foot_pt = (self.player.rect.centerx, self.player.rect.bottom - 2)
        for trap in self.traps:
            if not trap.hit_rect.collidepoint(foot_pt):
                continue
            lx = foot_pt[0] - trap.hit_rect.x
            ly = foot_pt[1] - trap.hit_rect.y
            if trap.hit_mask.get_at((lx, ly)) == 0:
                continue

            if isinstance(trap, SpikeTrap):
                if trap.damage_enabled and self._apply_damage(self.SPIKE_DMG):
                    return
            elif isinstance(trap, FloorCollapse):
                trap.trigger()
                if self._apply_damage(self.COLLAPSE_DMG):
                    return
            else:  # BladeSpinner
                if self._apply_damage(self.BLADE_DMG):
                    return

        # 4) wrogowie → gracz
        if spritecollide(self.player, self.enemies, False, pygame.sprite.collide_mask):
            if self.player.invul_timer <= 0 and self._apply_damage(10):
                return

        # 5) gracz → wrogowie (cios mieczem)
        atk_box = self.player.attack_hitbox()
        if atk_box:
            for e in list(self.enemies):
                if atk_box.colliderect(e.rect):
                    if hasattr(e, "hp"):
                        e.hp -= 20
                        if e.hp <= 0:
                            e.kill()
                    else:
                        e.kill()

        # 6) drabiny – wyjście z poziomu
        if spritecollide(self.player, self.ladders, False, pygame.sprite.collide_mask):
            if self.next_lvl:
                self.camera.update(0, 0)          # reset widoku
                self.game.level_index += 1
                self.game.start_level()
            else:
                self.game.game_over(True)
            return

        # 7) przesuwanie kamery (edge-scroll)
        self._edge_scroll_camera()

    def _apply_damage(self, dmg: int) -> bool:
        """Zadaje obrażenia, uruchamia nieczułość.
           Zwraca True, gdy gracz zginął."""
        if self.player.invul_timer > 0:           # wciąż nieczuły
            return False
        self.player.hp -= dmg
        self.player.invul_timer  = 1.0            # 1 s nieczułości
        self.player._blink_timer = 0.0
        self.player._blink_state = True
        if self.player.hp <= 0:
            play(SND_GAME_OVER)
            self.game.game_over(False)
            return True
        return False

    def draw(self, screen):
        ox, oy = -int(self.camera.x), -int(self.camera.y)

        # 1) tło – nie przesuwamy
        screen.blit(self.bg, (0, 0))

        # 2) spadające obiekty (rysuj przed podłogą)
        below = [s for s in self.world if getattr(s, "falling_off", False)]
        for spr in sorted(below, key=lambda s: s.rect.bottom):
            screen.blit(spr.image, spr.rect.move(ox, oy))

        # 3) podłoga – cała mapa, przesunięcie = kamera + world_rect
        screen.blit(self.floor_surface,
                    (ox + self.world_rect.left, oy + self.world_rect.top))


        # 4) pułapki
        for trap in self.traps:
            screen.blit(trap.image, trap.rect.move(ox, oy))

        # 5) reszta sprite’ów (bez pułapek i spadających) – sort wg Y
        drawables = [s for s in self.world if s not in self.traps and s not in below]
        for spr in sorted(drawables, key=lambda s: s.rect.bottom):
            screen.blit(spr.image, spr.rect.move(ox, oy))

        # 6) drabiny
        for lad in self.ladders:
            screen.blit(lad.image, lad.rect.move(ox, oy))

        # 7) HUD
        self.hud.draw(screen)

