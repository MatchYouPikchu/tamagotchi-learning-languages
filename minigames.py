"""Sub-state overlays: food selection menu and click mini games."""

import math
import random
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_Y, BLACK, WHITE,
    OUTLINE_WIDTH, STAT_MAX,
    # Food menu
    FOODS, FOOD_MENU_WIDTH, FOOD_MENU_HEIGHT, FOOD_ROW_HEIGHT,
    FOOD_MENU_BG, FOOD_MENU_BORDER, FOOD_MENU_HOVER,
    FOOD_MENU_TEXT, FOOD_MENU_STAT_TEXT,
    # Mini game general
    MINIGAME_DURATION, MINIGAME_RESULTS_DURATION,
    MINIGAME_BASE_HAPPINESS, MINIGAME_PER_SCORE, MINIGAME_HAPPINESS_CAP,
    OVERLAY_ALPHA, OVERLAY_TITLE_COLOR, OVERLAY_SCORE_COLOR,
    OVERLAY_TIMER_BG, OVERLAY_TIMER_FG,
    # Treat game
    TREAT_SPAWN_INTERVAL, TREAT_FALL_SPEED, TREAT_RADIUS, TREAT_COLOR,
    # Bubble game
    BUBBLE_SPAWN_INTERVAL, BUBBLE_FLOAT_SPEED,
    BUBBLE_MIN_RADIUS, BUBBLE_MAX_RADIUS,
    BUBBLE_WOBBLE_AMP, BUBBLE_WOBBLE_SPEED, MINIGAME_BUBBLE_COLOR,
    # Ball game
    CHASE_BALL_START_SPEED, CHASE_BALL_SPEED_INCREASE,
    CHASE_BALL_RADIUS, CHASE_BALL_COLOR,
    # Cleaning menu
    CLEANINGS,
    # Medicine game
    MEDICINE_DURATION, MEDICINE_SPAWN_INTERVAL, MEDICINE_FALL_SPEED,
    MEDICINE_BOTTLE_W, MEDICINE_BOTTLE_H, MEDICINE_COLORS,
    MEDICINE_STAT_RESTORE, MEDICINE_SICK_TIMER_RESET,
    DARK_GRAY, MID_GRAY,
)

# Play area bounds
PLAY_TOP = 100
PLAY_BOTTOM = GROUND_Y


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _draw_overlay_bg(surface):
    """Draw a semi-transparent dark overlay over the whole screen."""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, OVERLAY_ALPHA))
    surface.blit(overlay, (0, 0))


def _kawaii_circle(surface, center, radius, color):
    """Draw a kawaii-style outlined circle (black outline then fill)."""
    pygame.draw.circle(surface, BLACK, center, radius + OUTLINE_WIDTH)
    pygame.draw.circle(surface, color, center, radius)


def _calc_happiness(score):
    """Calculate happiness gain from a mini game score."""
    return min(MINIGAME_HAPPINESS_CAP,
               MINIGAME_BASE_HAPPINESS + score * MINIGAME_PER_SCORE)


# ---------------------------------------------------------------------------
# FoodMenu
# ---------------------------------------------------------------------------

class FoodMenu:
    """Overlay that lets the player pick one of 4 foods."""

    def __init__(self):
        self.done = False
        self.result = None  # (name, hunger, happiness, energy) or None
        self.hovered = -1
        # Menu rect, centered
        self.rect = pygame.Rect(
            (SCREEN_WIDTH - FOOD_MENU_WIDTH) // 2,
            (SCREEN_HEIGHT - FOOD_MENU_HEIGHT) // 2 - 30,
            FOOD_MENU_WIDTH,
            FOOD_MENU_HEIGHT,
        )
        self._row_rects = []
        y = self.rect.y + 44  # leave room for title
        for _ in FOODS:
            r = pygame.Rect(self.rect.x + 8, y, FOOD_MENU_WIDTH - 16, FOOD_ROW_HEIGHT)
            self._row_rects.append(r)
            y += FOOD_ROW_HEIGHT

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.done = True
                self.result = None
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                idx = event.key - pygame.K_1
                if 0 <= idx < len(FOODS):
                    name, hunger, happiness, energy, _ = FOODS[idx]
                    self.result = (name, hunger, happiness, energy)
                    self.done = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._row_rects):
                if r.collidepoint(mouse_pos):
                    name, hunger, happiness, energy, _ = FOODS[i]
                    self.result = (name, hunger, happiness, energy)
                    self.done = True
                    return
            # Click outside menu = cancel
            if not self.rect.collidepoint(mouse_pos):
                self.done = True
                self.result = None

    def update(self, dt):
        pass

    def draw(self, surface, mouse_pos):
        _draw_overlay_bg(surface)
        # Menu background
        pygame.draw.rect(surface, FOOD_MENU_BG, self.rect, border_radius=12)
        pygame.draw.rect(surface, FOOD_MENU_BORDER, self.rect, width=3, border_radius=12)

        # Title
        font_title = pygame.font.SysFont(None, 36)
        title = font_title.render("Choose Food", True, OVERLAY_TITLE_COLOR)
        surface.blit(title, (self.rect.centerx - title.get_width() // 2,
                             self.rect.y + 12))

        font_name = pygame.font.SysFont(None, 32)
        font_stat = pygame.font.SysFont(None, 24)

        for i, (r, food) in enumerate(zip(self._row_rects, FOODS)):
            name, hunger, happiness, energy, icon_color = food
            hovered = r.collidepoint(mouse_pos)

            # Row background
            if hovered:
                pygame.draw.rect(surface, FOOD_MENU_HOVER, r, border_radius=8)

            # Kawaii food icon
            icon_cx = r.x + 28
            icon_cy = r.centery
            self._draw_food_icon(surface, icon_cx, icon_cy, i, icon_color)

            # Food name
            label = font_name.render(f"{i+1}. {name}", True, FOOD_MENU_TEXT)
            surface.blit(label, (r.x + 56, r.y + 6))

            # Stat effects
            parts = []
            if hunger:
                parts.append(f"+{hunger} hunger")
            if happiness:
                parts.append(f"+{happiness} happy")
            if energy:
                parts.append(f"+{energy} energy")
            stat_text = font_stat.render("  ".join(parts), True, FOOD_MENU_STAT_TEXT)
            surface.blit(stat_text, (r.x + 56, r.y + 30))

    @staticmethod
    def _draw_food_icon(surface, cx, cy, index, color):
        """Draw a tiny kawaii food icon procedurally."""
        if index == 0:  # Apple
            _kawaii_circle(surface, (cx, cy), 10, color)
            # Stem
            pygame.draw.line(surface, (100, 70, 30), (cx, cy - 10), (cx + 2, cy - 15), 2)
            # Leaf
            pygame.draw.ellipse(surface, (60, 160, 50),
                                (cx + 2, cy - 17, 8, 5))
        elif index == 1:  # Fish
            # Body ellipse
            pygame.draw.ellipse(surface, BLACK,
                                (cx - 14, cy - 8, 28, 16))
            pygame.draw.ellipse(surface, color,
                                (cx - 12, cy - 6, 24, 12))
            # Tail
            pygame.draw.polygon(surface, color,
                                [(cx + 10, cy), (cx + 18, cy - 7), (cx + 18, cy + 7)])
            pygame.draw.polygon(surface, BLACK,
                                [(cx + 10, cy), (cx + 18, cy - 7), (cx + 18, cy + 7)], 2)
            # Eye
            pygame.draw.circle(surface, BLACK, (cx - 4, cy - 1), 2)
        elif index == 2:  # Cake
            # Base
            pygame.draw.rect(surface, BLACK,
                             (cx - 11, cy - 6, 22, 16), border_radius=3)
            pygame.draw.rect(surface, color,
                             (cx - 9, cy - 4, 18, 12), border_radius=2)
            # Frosting top
            pygame.draw.rect(surface, (255, 255, 240),
                             (cx - 9, cy - 6, 18, 5), border_radius=2)
            # Cherry
            pygame.draw.circle(surface, (220, 50, 50), (cx, cy - 8), 3)
        elif index == 3:  # Milk
            # Bottle body
            pygame.draw.rect(surface, BLACK,
                             (cx - 8, cy - 10, 16, 20), border_radius=3)
            pygame.draw.rect(surface, color,
                             (cx - 6, cy - 8, 12, 16), border_radius=2)
            # Cap
            pygame.draw.rect(surface, (100, 150, 220),
                             (cx - 5, cy - 12, 10, 5), border_radius=2)


# ---------------------------------------------------------------------------
# Base Mini Game
# ---------------------------------------------------------------------------

class _MiniGameBase:
    """Shared logic for timed click mini games."""

    title = "Mini Game"

    def __init__(self, sound):
        self.sound = sound
        self.timer = MINIGAME_DURATION
        self.score = 0
        self.done = False
        self.result = None  # happiness amount when done
        self._phase = "play"  # "play" | "results"
        self._results_timer = 0.0
        self._sparkles = []  # brief visual effects at click

    def handle_event(self, event, mouse_pos):
        if self._phase != "play":
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._on_click(mouse_pos)

    def _on_click(self, pos):
        """Override in subclass to handle clicks during play phase."""
        pass

    def update(self, dt):
        # Update sparkles
        self._sparkles = [(x, y, t - dt, c) for x, y, t, c in self._sparkles if t - dt > 0]

        if self._phase == "play":
            self.timer -= dt
            self._update_play(dt)
            if self.timer <= 0:
                self.timer = 0
                self._phase = "results"
                self.result = _calc_happiness(self.score)
                self._results_timer = MINIGAME_RESULTS_DURATION
        elif self._phase == "results":
            self._results_timer -= dt
            if self._results_timer <= 0:
                self.done = True

    def _update_play(self, dt):
        """Override in subclass for game-specific update logic."""
        pass

    def draw(self, surface, mouse_pos):
        _draw_overlay_bg(surface)
        if self._phase == "play":
            self._draw_play(surface, mouse_pos)
            self._draw_hud(surface)
        else:
            self._draw_results(surface)
        # Sparkles
        for x, y, t, color in self._sparkles:
            alpha = int(255 * (t / 0.3))
            r = int(12 * (1 - t / 0.3))
            if alpha > 0:
                pygame.draw.circle(surface, color, (int(x), int(y)), r + 3, 2)

    def _draw_play(self, surface, mouse_pos):
        """Override in subclass."""
        pass

    def _draw_hud(self, surface):
        """Draw title, timer bar, and score."""
        font_title = pygame.font.SysFont(None, 38)
        font_score = pygame.font.SysFont(None, 34)

        # Title
        title_surf = font_title.render(self.title, True, OVERLAY_TITLE_COLOR)
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 20))

        # Timer bar
        bar_w = 300
        bar_h = 12
        bar_x = (SCREEN_WIDTH - bar_w) // 2
        bar_y = 55
        pygame.draw.rect(surface, OVERLAY_TIMER_BG,
                         (bar_x, bar_y, bar_w, bar_h), border_radius=6)
        fill_w = int(bar_w * max(0, self.timer / MINIGAME_DURATION))
        if fill_w > 0:
            pygame.draw.rect(surface, OVERLAY_TIMER_FG,
                             (bar_x, bar_y, fill_w, bar_h), border_radius=6)

        # Score
        score_surf = font_score.render(f"Score: {self.score}", True, OVERLAY_SCORE_COLOR)
        surface.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, 74))

    def _draw_results(self, surface):
        """Draw results screen."""
        font_big = pygame.font.SysFont(None, 50)
        font_med = pygame.font.SysFont(None, 38)

        cy = SCREEN_HEIGHT // 2 - 40
        t1 = font_big.render("Time's Up!", True, OVERLAY_TITLE_COLOR)
        surface.blit(t1, (SCREEN_WIDTH // 2 - t1.get_width() // 2, cy))

        t2 = font_med.render(f"Score: {self.score}", True, OVERLAY_SCORE_COLOR)
        surface.blit(t2, (SCREEN_WIDTH // 2 - t2.get_width() // 2, cy + 50))

        happiness = self.result or 0
        t3 = font_med.render(f"+{happiness} Happiness!", True, (255, 220, 100))
        surface.blit(t3, (SCREEN_WIDTH // 2 - t3.get_width() // 2, cy + 85))

    def _add_sparkle(self, x, y, color=(255, 255, 180)):
        self._sparkles.append((x, y, 0.3, color))


# ---------------------------------------------------------------------------
# CatchTreats
# ---------------------------------------------------------------------------

class CatchTreats(_MiniGameBase):
    title = "Catch Treats!"

    def __init__(self, sound):
        super().__init__(sound)
        self._treats = []  # [(x, y, speed)]
        self._spawn_timer = 0.0

    def _on_click(self, pos):
        mx, my = pos
        for i, (tx, ty, _) in enumerate(self._treats):
            dx = mx - tx
            dy = my - ty
            if dx * dx + dy * dy <= (TREAT_RADIUS + 6) ** 2:
                self.score += 1
                self._add_sparkle(tx, ty, TREAT_COLOR)
                if self.sound:
                    self.sound.play("catch")
                self._treats.pop(i)
                return

    def _update_play(self, dt):
        self._spawn_timer += dt
        if self._spawn_timer >= TREAT_SPAWN_INTERVAL:
            self._spawn_timer -= TREAT_SPAWN_INTERVAL
            x = random.randint(40, SCREEN_WIDTH - 40)
            speed = TREAT_FALL_SPEED + random.uniform(-20, 20)
            self._treats.append([x, PLAY_TOP - TREAT_RADIUS, speed])

        # Move treats
        alive = []
        for t in self._treats:
            t[1] += t[2] * dt
            if t[1] < PLAY_BOTTOM + TREAT_RADIUS:
                alive.append(t)
        self._treats = alive

    def _draw_play(self, surface, mouse_pos):
        for tx, ty, _ in self._treats:
            # Kawaii treat: outlined circle with face
            _kawaii_circle(surface, (int(tx), int(ty)), TREAT_RADIUS, TREAT_COLOR)
            # Eyes
            ex = int(tx)
            ey = int(ty) - 2
            pygame.draw.circle(surface, BLACK, (ex - 4, ey), 2)
            pygame.draw.circle(surface, BLACK, (ex + 4, ey), 2)
            # Smile
            pygame.draw.arc(surface, BLACK,
                            (ex - 4, ey + 1, 8, 6), 3.14, 6.28, 1)


# ---------------------------------------------------------------------------
# PopBubbles
# ---------------------------------------------------------------------------

class PopBubbles(_MiniGameBase):
    title = "Pop Bubbles!"

    def __init__(self, sound):
        super().__init__(sound)
        self._bubbles = []  # [(x, y, radius, phase)]
        self._spawn_timer = 0.0
        self._pop_effects = []  # [(x, y, radius, timer)]

    def _on_click(self, pos):
        mx, my = pos
        for i, (bx, by, br, _) in enumerate(self._bubbles):
            dx = mx - bx
            dy = my - by
            if dx * dx + dy * dy <= (br + 6) ** 2:
                self.score += 1
                self._pop_effects.append([bx, by, br, 0.3])
                self._add_sparkle(bx, by, MINIGAME_BUBBLE_COLOR)
                if self.sound:
                    self.sound.play("pop")
                self._bubbles.pop(i)
                return

    def _update_play(self, dt):
        self._spawn_timer += dt
        if self._spawn_timer >= BUBBLE_SPAWN_INTERVAL:
            self._spawn_timer -= BUBBLE_SPAWN_INTERVAL
            x = random.randint(60, SCREEN_WIDTH - 60)
            r = random.randint(BUBBLE_MIN_RADIUS, BUBBLE_MAX_RADIUS)
            phase = random.uniform(0, math.pi * 2)
            self._bubbles.append([x, PLAY_BOTTOM + r, r, phase])

        alive = []
        for b in self._bubbles:
            b[1] -= BUBBLE_FLOAT_SPEED * dt
            b[3] += BUBBLE_WOBBLE_SPEED * dt
            if b[1] > PLAY_TOP - b[2]:
                alive.append(b)
        self._bubbles = alive

        # Pop effects
        self._pop_effects = [[x, y, r, t - dt]
                             for x, y, r, t in self._pop_effects if t - dt > 0]

    def _draw_play(self, surface, mouse_pos):
        for bx, by, br, phase in self._bubbles:
            # Wobble horizontal position
            draw_x = int(bx + math.sin(phase) * BUBBLE_WOBBLE_AMP * 0.3)
            draw_y = int(by)

            # Translucent bubble
            bub_surf = pygame.Surface((br * 2 + 6, br * 2 + 6), pygame.SRCALPHA)
            pygame.draw.circle(bub_surf, (*MINIGAME_BUBBLE_COLOR, 100),
                               (br + 3, br + 3), br)
            pygame.draw.circle(bub_surf, (*WHITE, 160),
                               (br + 3, br + 3), br, 2)
            surface.blit(bub_surf, (draw_x - br - 3, draw_y - br - 3))

            # Highlight
            pygame.draw.circle(surface, (*WHITE, 200),
                               (draw_x - br // 3, draw_y - br // 3),
                               max(2, br // 4))

        # Pop effects: expanding ring
        for px, py, pr, t in self._pop_effects:
            progress = 1.0 - t / 0.3
            ring_r = int(pr + pr * progress)
            alpha = int(200 * (1 - progress))
            if alpha > 0:
                eff_surf = pygame.Surface((ring_r * 2 + 4, ring_r * 2 + 4), pygame.SRCALPHA)
                pygame.draw.circle(eff_surf, (*MINIGAME_BUBBLE_COLOR, alpha),
                                   (ring_r + 2, ring_r + 2), ring_r, 3)
                surface.blit(eff_surf, (int(px) - ring_r - 2, int(py) - ring_r - 2))


# ---------------------------------------------------------------------------
# ChaseBall
# ---------------------------------------------------------------------------

class ChaseBall(_MiniGameBase):
    title = "Chase the Ball!"

    def __init__(self, sound):
        super().__init__(sound)
        self._speed = CHASE_BALL_START_SPEED
        self._ball_x = float(SCREEN_WIDTH // 2)
        self._ball_y = float((PLAY_TOP + PLAY_BOTTOM) // 2)
        self._vx = self._speed * random.choice([-1, 1])
        self._vy = self._speed * random.choice([-1, 1])
        self._flash_timer = 0.0

    def _on_click(self, pos):
        mx, my = pos
        dx = mx - self._ball_x
        dy = my - self._ball_y
        if dx * dx + dy * dy <= (CHASE_BALL_RADIUS + 8) ** 2:
            self.score += 1
            self._add_sparkle(self._ball_x, self._ball_y, CHASE_BALL_COLOR)
            if self.sound:
                self.sound.play("catch")
            self._flash_timer = 0.2
            # Speed up
            self._speed += CHASE_BALL_SPEED_INCREASE
            # Teleport
            self._ball_x = random.uniform(60, SCREEN_WIDTH - 60)
            self._ball_y = random.uniform(PLAY_TOP + 40, PLAY_BOTTOM - 40)
            angle = random.uniform(0, math.pi * 2)
            self._vx = self._speed * math.cos(angle)
            self._vy = self._speed * math.sin(angle)

    def _update_play(self, dt):
        self._ball_x += self._vx * dt
        self._ball_y += self._vy * dt

        # Bounce off walls
        left = 30 + CHASE_BALL_RADIUS
        right = SCREEN_WIDTH - 30 - CHASE_BALL_RADIUS
        top = PLAY_TOP + CHASE_BALL_RADIUS
        bottom = PLAY_BOTTOM - CHASE_BALL_RADIUS

        if self._ball_x < left:
            self._ball_x = left
            self._vx = abs(self._vx)
        elif self._ball_x > right:
            self._ball_x = right
            self._vx = -abs(self._vx)

        if self._ball_y < top:
            self._ball_y = top
            self._vy = abs(self._vy)
        elif self._ball_y > bottom:
            self._ball_y = bottom
            self._vy = -abs(self._vy)

        if self._flash_timer > 0:
            self._flash_timer -= dt

    def _draw_play(self, surface, mouse_pos):
        bx = int(self._ball_x)
        by = int(self._ball_y)
        r = CHASE_BALL_RADIUS

        # Flash yellow briefly on catch
        color = (255, 240, 80) if self._flash_timer > 0 else CHASE_BALL_COLOR

        _kawaii_circle(surface, (bx, by), r, color)

        # Highlight
        pygame.draw.circle(surface, WHITE, (bx - r // 3, by - r // 3),
                           max(2, r // 3))

        # Kawaii face
        pygame.draw.circle(surface, BLACK, (bx - 5, by - 3), 3)
        pygame.draw.circle(surface, BLACK, (bx + 5, by - 3), 3)
        # Smile
        pygame.draw.arc(surface, BLACK,
                        (bx - 5, by, 10, 7), 3.14, 6.28, 2)


# ---------------------------------------------------------------------------
# CleanMenu
# ---------------------------------------------------------------------------

class CleanMenu:
    """Overlay that lets the player pick one of 4 cleaning options."""

    def __init__(self, poop_piles=0):
        self.done = False
        self.result = None  # (name, cleanliness, happiness, energy) or None
        self.poop_piles = poop_piles
        self.hovered = -1
        # Menu rect, centered
        self.rect = pygame.Rect(
            (SCREEN_WIDTH - FOOD_MENU_WIDTH) // 2,
            (SCREEN_HEIGHT - FOOD_MENU_HEIGHT) // 2 - 30,
            FOOD_MENU_WIDTH,
            FOOD_MENU_HEIGHT,
        )
        self._row_rects = []
        y = self.rect.y + 44
        for _ in CLEANINGS:
            r = pygame.Rect(self.rect.x + 8, y, FOOD_MENU_WIDTH - 16, FOOD_ROW_HEIGHT)
            self._row_rects.append(r)
            y += FOOD_ROW_HEIGHT

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.done = True
                self.result = None
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                idx = event.key - pygame.K_1
                if 0 <= idx < len(CLEANINGS):
                    self._select(idx)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._row_rects):
                if r.collidepoint(mouse_pos):
                    self._select(i)
                    return
            if not self.rect.collidepoint(mouse_pos):
                self.done = True
                self.result = None

    def _select(self, idx):
        name, cleanliness, happiness, energy, _ = CLEANINGS[idx]
        if name == "Pick Up" and self.poop_piles <= 0:
            return  # grayed out
        self.result = (name, cleanliness, happiness, energy)
        self.done = True

    def update(self, dt):
        pass

    def draw(self, surface, mouse_pos):
        _draw_overlay_bg(surface)
        pygame.draw.rect(surface, FOOD_MENU_BG, self.rect, border_radius=12)
        pygame.draw.rect(surface, FOOD_MENU_BORDER, self.rect, width=3, border_radius=12)

        font_title = pygame.font.SysFont(None, 36)
        title = font_title.render("Clean Pet", True, OVERLAY_TITLE_COLOR)
        surface.blit(title, (self.rect.centerx - title.get_width() // 2,
                             self.rect.y + 12))

        font_name = pygame.font.SysFont(None, 32)
        font_stat = pygame.font.SysFont(None, 24)

        for i, (r, cleaning) in enumerate(zip(self._row_rects, CLEANINGS)):
            name, cleanliness, happiness, energy, icon_color = cleaning
            is_disabled = (name == "Pick Up" and self.poop_piles <= 0)
            hovered = r.collidepoint(mouse_pos) and not is_disabled

            if hovered:
                pygame.draw.rect(surface, FOOD_MENU_HOVER, r, border_radius=8)

            icon_cx = r.x + 28
            icon_cy = r.centery
            self._draw_clean_icon(surface, icon_cx, icon_cy, i, icon_color, is_disabled)

            text_color = MID_GRAY if is_disabled else FOOD_MENU_TEXT
            label = font_name.render(f"{i+1}. {name}", True, text_color)
            surface.blit(label, (r.x + 56, r.y + 6))

            parts = []
            if cleanliness:
                parts.append(f"+{cleanliness} clean")
            if happiness:
                parts.append(f"+{happiness} happy")
            if energy:
                sign = "+" if energy > 0 else ""
                parts.append(f"{sign}{energy} energy")
            if name == "Pick Up":
                parts.append(f"({self.poop_piles} piles)")
            stat_color = MID_GRAY if is_disabled else FOOD_MENU_STAT_TEXT
            stat_text = font_stat.render("  ".join(parts), True, stat_color)
            surface.blit(stat_text, (r.x + 56, r.y + 30))

    @staticmethod
    def _draw_clean_icon(surface, cx, cy, index, color, disabled=False):
        draw_color = MID_GRAY if disabled else color
        if index == 0:  # Bath - water drops
            for dx, dy in [(-6, -4), (0, 2), (6, -2)]:
                pygame.draw.circle(surface, BLACK, (cx + dx, cy + dy), 6)
                pygame.draw.circle(surface, draw_color, (cx + dx, cy + dy), 5)
            # Highlight
            pygame.draw.circle(surface, WHITE, (cx - 4, cy - 6), 2)
        elif index == 1:  # Brush - rectangle with bristles
            pygame.draw.rect(surface, BLACK,
                             (cx - 10, cy - 8, 20, 16), border_radius=3)
            pygame.draw.rect(surface, draw_color,
                             (cx - 8, cy - 6, 16, 12), border_radius=2)
            for bx in range(-6, 8, 4):
                pygame.draw.line(surface, BLACK,
                                 (cx + bx, cy + 6), (cx + bx, cy + 11), 1)
        elif index == 2:  # Towel - folded rectangle
            pygame.draw.rect(surface, BLACK,
                             (cx - 12, cy - 7, 24, 14), border_radius=3)
            pygame.draw.rect(surface, draw_color,
                             (cx - 10, cy - 5, 20, 10), border_radius=2)
            pygame.draw.line(surface, BLACK,
                             (cx - 10, cy), (cx + 10, cy), 1)
        elif index == 3:  # Pick Up - brown bag
            pygame.draw.polygon(surface, BLACK, [
                (cx - 9, cy - 8), (cx + 9, cy - 8),
                (cx + 7, cy + 8), (cx - 7, cy + 8),
            ])
            pygame.draw.polygon(surface, draw_color, [
                (cx - 7, cy - 6), (cx + 7, cy - 6),
                (cx + 5, cy + 6), (cx - 5, cy + 6),
            ])
            # Tie at top
            pygame.draw.line(surface, BLACK,
                             (cx - 3, cy - 8), (cx, cy - 12), 2)
            pygame.draw.line(surface, BLACK,
                             (cx + 3, cy - 8), (cx, cy - 12), 2)


# ---------------------------------------------------------------------------
# MedicineGame
# ---------------------------------------------------------------------------

class MedicineGame:
    """Falling-bottle mini game. Click the correct color to cure sickness."""

    title = "Give Medicine!"

    def __init__(self, sound):
        self.sound = sound
        self.timer = MEDICINE_DURATION
        self.score = 0
        self.done = False
        self.result = None
        self._phase = "play"
        self._results_timer = 0.0
        self._bottles = []  # [(x, y, color_index)]
        self._spawn_timer = 0.0
        self._target_color = random.randint(0, len(MEDICINE_COLORS) - 1)
        self._sparkles = []
        self._shake_timer = 0.0

    def handle_event(self, event, mouse_pos):
        if self._phase != "play":
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._on_click(mouse_pos)

    def _on_click(self, pos):
        mx, my = pos
        bw, bh = MEDICINE_BOTTLE_W, MEDICINE_BOTTLE_H
        for i in range(len(self._bottles) - 1, -1, -1):
            bx, by, ci = self._bottles[i]
            if (bx - bw // 2 - 4 <= mx <= bx + bw // 2 + 4 and
                    by - bh // 2 - 4 <= my <= by + bh // 2 + 4):
                if ci == self._target_color:
                    self.score += 1
                    self._sparkles.append((bx, by, 0.3, MEDICINE_COLORS[ci]))
                    if self.sound:
                        self.sound.play("catch")
                else:
                    self.timer = max(0, self.timer - 1.0)
                    self._shake_timer = 0.2
                    if self.sound:
                        self.sound.play("wrong")
                self._bottles.pop(i)
                return

    def update(self, dt):
        self._sparkles = [(x, y, t - dt, c) for x, y, t, c in self._sparkles if t - dt > 0]

        if self._shake_timer > 0:
            self._shake_timer = max(0, self._shake_timer - dt)

        if self._phase == "play":
            self.timer -= dt
            self._spawn_timer += dt
            if self._spawn_timer >= MEDICINE_SPAWN_INTERVAL:
                self._spawn_timer -= MEDICINE_SPAWN_INTERVAL
                x = random.randint(40, SCREEN_WIDTH - 40)
                ci = random.randint(0, len(MEDICINE_COLORS) - 1)
                self._bottles.append([x, PLAY_TOP - MEDICINE_BOTTLE_H, ci])

            alive = []
            for b in self._bottles:
                b[1] += MEDICINE_FALL_SPEED * dt
                if b[1] < PLAY_BOTTOM + MEDICINE_BOTTLE_H:
                    alive.append(b)
            self._bottles = alive

            if self.timer <= 0:
                self.timer = 0
                self._phase = "results"
                if self.score >= 3:
                    self.result = ("full", MEDICINE_STAT_RESTORE)
                elif self.score >= 1:
                    self.result = ("partial", 0)
                else:
                    self.result = ("fail", MEDICINE_SICK_TIMER_RESET)
                self._results_timer = MINIGAME_RESULTS_DURATION
        elif self._phase == "results":
            self._results_timer -= dt
            if self._results_timer <= 0:
                self.done = True

    def draw(self, surface, mouse_pos):
        _draw_overlay_bg(surface)

        # Shake offset
        sx, sy = 0, 0
        if self._shake_timer > 0:
            sx = random.randint(-3, 3)
            sy = random.randint(-3, 3)

        if self._phase == "play":
            self._draw_play(surface, mouse_pos, sx, sy)
            self._draw_hud(surface, sx, sy)
        else:
            self._draw_results(surface)

        for x, y, t, color in self._sparkles:
            alpha = int(255 * (t / 0.3))
            r = int(12 * (1 - t / 0.3))
            if alpha > 0:
                pygame.draw.circle(surface, color, (int(x) + sx, int(y) + sy), r + 3, 2)

    def _draw_play(self, surface, mouse_pos, sx=0, sy=0):
        # Target indicator at top
        target_color = MEDICINE_COLORS[self._target_color]
        indicator_x = SCREEN_WIDTH // 2
        indicator_y = 115
        self._draw_bottle(surface, indicator_x + sx, indicator_y + sy,
                          target_color, scale=1.5)
        font_hint = pygame.font.SysFont(None, 26)
        hint = font_hint.render("Click this color!", True, OVERLAY_TITLE_COLOR)
        surface.blit(hint, (indicator_x - hint.get_width() // 2 + sx,
                            indicator_y + 30 + sy))

        # Falling bottles
        for bx, by, ci in self._bottles:
            color = MEDICINE_COLORS[ci]
            self._draw_bottle(surface, int(bx) + sx, int(by) + sy, color)

    def _draw_bottle(self, surface, cx, cy, color, scale=1.0):
        bw = int(MEDICINE_BOTTLE_W * scale)
        bh = int(MEDICINE_BOTTLE_H * scale)
        cap_h = int(8 * scale)
        cap_w = int(12 * scale)

        # Bottle body outline + fill
        body_rect = pygame.Rect(cx - bw // 2, cy - bh // 2, bw, bh)
        pygame.draw.rect(surface, BLACK, body_rect.inflate(4, 4), border_radius=4)
        pygame.draw.rect(surface, color, body_rect, border_radius=3)

        # Cap
        cap_rect = pygame.Rect(cx - cap_w // 2, cy - bh // 2 - cap_h, cap_w, cap_h)
        pygame.draw.rect(surface, BLACK, cap_rect.inflate(2, 2), border_radius=2)
        pygame.draw.rect(surface, WHITE, cap_rect, border_radius=2)

        # Label stripe
        stripe_h = int(8 * scale)
        stripe_rect = pygame.Rect(cx - bw // 2 + 2, cy - stripe_h // 2,
                                   bw - 4, stripe_h)
        pygame.draw.rect(surface, WHITE, stripe_rect, border_radius=1)

        # Kawaii face on label
        ey = cy - int(2 * scale)
        er = max(1, int(2 * scale))
        pygame.draw.circle(surface, BLACK, (cx - int(4 * scale), ey), er)
        pygame.draw.circle(surface, BLACK, (cx + int(4 * scale), ey), er)
        # Smile
        smile_w = int(6 * scale)
        smile_h = int(4 * scale)
        pygame.draw.arc(surface, BLACK,
                        (cx - smile_w // 2, ey + int(1 * scale),
                         smile_w, smile_h),
                        3.14, 6.28, max(1, int(scale)))

    def _draw_hud(self, surface, sx=0, sy=0):
        font_title = pygame.font.SysFont(None, 38)
        font_score = pygame.font.SysFont(None, 34)

        title_surf = font_title.render(self.title, True, OVERLAY_TITLE_COLOR)
        surface.blit(title_surf, (SCREEN_WIDTH // 2 - title_surf.get_width() // 2 + sx,
                                   20 + sy))

        bar_w = 300
        bar_h = 12
        bar_x = (SCREEN_WIDTH - bar_w) // 2 + sx
        bar_y = 55 + sy
        pygame.draw.rect(surface, OVERLAY_TIMER_BG,
                         (bar_x, bar_y, bar_w, bar_h), border_radius=6)
        fill_w = int(bar_w * max(0, self.timer / MEDICINE_DURATION))
        if fill_w > 0:
            pygame.draw.rect(surface, OVERLAY_TIMER_FG,
                             (bar_x, bar_y, fill_w, bar_h), border_radius=6)

        score_surf = font_score.render(f"Score: {self.score}", True, OVERLAY_SCORE_COLOR)
        surface.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2 + sx,
                                   74 + sy))

    def _draw_results(self, surface):
        font_big = pygame.font.SysFont(None, 50)
        font_med = pygame.font.SysFont(None, 38)

        cy = SCREEN_HEIGHT // 2 - 40
        t1 = font_big.render("Time's Up!", True, OVERLAY_TITLE_COLOR)
        surface.blit(t1, (SCREEN_WIDTH // 2 - t1.get_width() // 2, cy))

        t2 = font_med.render(f"Score: {self.score}", True, OVERLAY_SCORE_COLOR)
        surface.blit(t2, (SCREEN_WIDTH // 2 - t2.get_width() // 2, cy + 50))

        if self.result:
            outcome, value = self.result
            if outcome == "full":
                msg = "Full cure! +{} to lowest stat!".format(value)
                color = (100, 255, 100)
            elif outcome == "partial":
                msg = "Partial cure! Sickness gone."
                color = (255, 220, 100)
            else:
                msg = "Failed... still sick."
                color = (255, 100, 100)
            t3 = font_med.render(msg, True, color)
            surface.blit(t3, (SCREEN_WIDTH // 2 - t3.get_width() // 2, cy + 85))


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_random_minigame(sound):
    """Return a random mini game instance."""
    cls = random.choice([CatchTreats, PopBubbles, ChaseBall])
    return cls(sound)
