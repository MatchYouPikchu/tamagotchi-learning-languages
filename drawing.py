"""Procedural pet drawing — clean kawaii outline style cat & dog, expressions, animations, evolution tiers."""

import math
import random
import pygame
from settings import (
    PET_CAT, PET_DOG,
    ACTION_IDLE, ACTION_EATING, ACTION_PLAYING, ACTION_CLEANING,
    ACTION_SLEEPING, ACTION_SICK, ACTION_RUNNING_AWAY,
    CAT_BODY, CAT_BODY_DARK, CAT_NOSE,
    DOG_BODY, DOG_BODY_DARK, DOG_NOSE, DOG_TONGUE,
    THRIVING_TINT, SCRUFFY_TINT,
    SPARKLE_COLOR, STAR_COLOR, ZZZ_COLOR, SWEAT_COLOR, FOOD_COLOR,
    WHITE, BLACK, PET_CENTER_X, PET_CENTER_Y, GROUND_Y,
    BLINK_DURATION, BLINK_MIN_INTERVAL, BLINK_MAX_INTERVAL,
    FIDGET_MIN_INTERVAL, FIDGET_MAX_INTERVAL, FIDGET_DURATION,
    SHADOW_BASE_ALPHA, BLUSH_COLOR, BLUSH_THRESHOLD,
    KAWAII_HEAD_RADIUS, KAWAII_BODY_W, KAWAII_BODY_H,
    BUBBLE_COLOR, BOWL_COLOR, BOWL_FOOD_COLOR, BALL_COLOR,
    OUTLINE_WIDTH, KAWAII_TOTAL_H, KAWAII_HEAD_RATIO, KAWAII_BODY_TAPER,
    KAWAII_PAW_BUMP_R, KAWAII_PAW_SPACING,
    KAWAII_EYE_Y_RATIO, KAWAII_BLUSH_RADIUS,
    KAWAII_WHISKER_LEN, KAWAII_WHISKER_COUNT,
    CAT_EAR_INNER_COLOR, DOG_EAR_INNER_COLOR,
    GROWTH_BABY, GROWTH_KID, GROWTH_SCALE,
    BABY_BOW_COLOR, KID_BELL_COLOR, ADULT_GEM_COLOR,
    BANDANA_COLOR, BONE_TAG_COLOR, KID_BANDANA_COLOR, ADULT_COLLAR_COLOR,
)


# --------------- Easing utilities ---------------

def _ease_in_out_cubic(t):
    t = max(0.0, min(1.0, t))
    if t < 0.5:
        return 4.0 * t * t * t
    return 1.0 - (-2.0 * t + 2.0) ** 3 / 2.0


def _ease_out_quad(t):
    t = max(0.0, min(1.0, t))
    return 1.0 - (1.0 - t) * (1.0 - t)


def _smooth_sin(time_val, speed, offset=0.0):
    phase = (time_val * speed + offset) % (2.0 * math.pi)
    normalized = phase / (2.0 * math.pi)
    eased = _ease_in_out_cubic(abs(normalized * 2.0 - 1.0))
    return eased * 2.0 - 1.0


# --------------- Color helpers ---------------

def _tint_color(color, amount):
    return tuple(max(0, min(255, c + amount)) for c in color)


def _get_pet_colors(pet_type, evolution_tier, appearance=None):
    tint = 0
    if evolution_tier == "thriving":
        tint = THRIVING_TINT
    elif evolution_tier == "scruffy":
        tint = SCRUFFY_TINT

    # Custom appearance colors override defaults
    if appearance and appearance.get("body_color"):
        body = tuple(appearance["body_color"])
        body_dark = _tint_color(body, -30)
        accent = tuple(appearance["accent_color"]) if appearance.get("accent_color") else body_dark
        if pet_type == PET_CAT:
            return {
                "body": _tint_color(body, tint),
                "body_dark": _tint_color(body_dark, tint),
                "nose": CAT_NOSE,
                "ear_inner": _tint_color(accent, -20),
            }
        else:
            return {
                "body": _tint_color(body, tint),
                "body_dark": _tint_color(body_dark, tint),
                "nose": DOG_NOSE,
                "tongue": DOG_TONGUE,
                "ear_inner": _tint_color(accent, -20),
            }

    if pet_type == PET_CAT:
        return {
            "body": _tint_color(CAT_BODY, tint),
            "body_dark": _tint_color(CAT_BODY_DARK, tint),
            "nose": CAT_NOSE,
            "ear_inner": CAT_EAR_INNER_COLOR,
        }
    else:
        return {
            "body": _tint_color(DOG_BODY, tint),
            "body_dark": _tint_color(DOG_BODY_DARK, tint),
            "nose": DOG_NOSE,
            "tongue": DOG_TONGUE,
            "ear_inner": DOG_EAR_INNER_COLOR,
        }


# --------------- Expression system (kawaii) ---------------

def _get_expression(pet):
    """Return expression dict with eye_style and mouth fields."""
    if pet.action == ACTION_SLEEPING:
        return {"eye_style": "happy_closed", "mouth": "smile"}
    if pet.action == ACTION_RUNNING_AWAY:
        return {"eye_style": "sad", "mouth": "frown"}
    if pet.is_sick:
        return {"eye_style": "dizzy", "mouth": "frown"}
    if pet.action == ACTION_EATING:
        return {"eye_style": "happy_closed", "mouth": "eating"}
    if pet.action == ACTION_CLEANING:
        return {"eye_style": "happy_closed", "mouth": "smile"}
    if pet.action == ACTION_PLAYING:
        return {"eye_style": "sparkle", "mouth": "big_smile"}

    avg = pet.avg_stat
    if avg > 80:
        return {"eye_style": "sparkle", "mouth": "big_smile"}
    elif avg > 60:
        return {"eye_style": "normal", "mouth": "smile"}
    elif avg > 40:
        return {"eye_style": "normal", "mouth": "small_smile"}
    elif avg > 25:
        return {"eye_style": "sad", "mouth": "flat"}
    else:
        return {"eye_style": "sad", "mouth": "frown"}


# --------------- Particle shapes ---------------

def _draw_star(surface, x, y, size, color, rotation):
    points = []
    for i in range(10):
        angle = rotation + i * math.pi / 5 - math.pi / 2
        r = size if i % 2 == 0 else size * 0.4
        points.append((x + math.cos(angle) * r, y + math.sin(angle) * r))
    pygame.draw.polygon(surface, color, points)


def _draw_sparkle(surface, x, y, size, color, rotation):
    for i in range(4):
        angle = rotation + i * math.pi / 2
        ex = x + math.cos(angle) * size
        ey = y + math.sin(angle) * size
        pygame.draw.line(surface, color, (int(x), int(y)), (int(ex), int(ey)), 2)


def _draw_heart(surface, x, y, size, color, _rotation):
    r = max(2, int(size * 0.45))
    pygame.draw.circle(surface, color, (int(x - r * 0.5), int(y - r * 0.3)), r)
    pygame.draw.circle(surface, color, (int(x + r * 0.5), int(y - r * 0.3)), r)
    pygame.draw.polygon(surface, color, [
        (x - r * 1.2, int(y)),
        (x + r * 1.2, int(y)),
        (int(x), int(y + r * 1.5)),
    ])


def _draw_zzz_letter(surface, x, y, size, color, _rotation):
    s = max(2, int(size))
    pygame.draw.line(surface, color, (int(x - s), int(y - s)), (int(x + s), int(y - s)), 2)
    pygame.draw.line(surface, color, (int(x + s), int(y - s)), (int(x - s), int(y + s)), 2)
    pygame.draw.line(surface, color, (int(x - s), int(y + s)), (int(x + s), int(y + s)), 2)


def _draw_bubble(surface, x, y, size, color, _rotation):
    """Draw a translucent soap bubble with highlight."""
    r = max(2, int(size))
    bub_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
    cx_b, cy_b = r + 2, r + 2
    pygame.draw.circle(bub_surf, (*color, 80), (cx_b, cy_b), r)
    pygame.draw.circle(bub_surf, (255, 255, 255, 140), (cx_b - r // 3, cy_b - r // 3), max(1, r // 3))
    surface.blit(bub_surf, (int(x) - r - 2, int(y) - r - 2))


# --------------- Prop drawing helpers ---------------

def _draw_food_bowl(surface, x, y):
    """Draw a small food bowl at (x, y) where y is the base."""
    pygame.draw.ellipse(surface, BOWL_COLOR, (x - 18, y - 10, 36, 14))
    pygame.draw.ellipse(surface, _tint_color(BOWL_COLOR, 30), (x - 20, y - 14, 40, 10))
    pygame.draw.ellipse(surface, BOWL_FOOD_COLOR, (x - 14, y - 16, 28, 10))


def _draw_toy_ball(surface, x, y, time_val):
    """Draw a bouncing toy ball at (x, base_y)."""
    bounce = abs(math.sin(time_val * 5.0)) * 20
    ball_y = y - 12 - bounce
    pygame.draw.circle(surface, BALL_COLOR, (int(x), int(ball_y)), 12)
    pygame.draw.circle(surface, WHITE, (int(x) - 3, int(ball_y) - 4), 3)
    pygame.draw.arc(surface, _tint_color(BALL_COLOR, -40),
                    (int(x) - 12, int(ball_y) - 12, 24, 24),
                    0.3, 1.2, 2)


def _draw_food_prop(surface, cx, cy, food_index, food_color):
    """Draw a scaled-up kawaii food icon as a prop next to the pet."""
    if food_index == 0:  # Apple
        # Large apple
        pygame.draw.circle(surface, BLACK, (cx, cy), 22)
        pygame.draw.circle(surface, food_color, (cx, cy), 20)
        # Stem
        pygame.draw.line(surface, (100, 70, 30), (cx, cy - 20), (cx + 3, cy - 28), 3)
        # Leaf
        pygame.draw.ellipse(surface, (60, 160, 50), (cx + 3, cy - 32, 14, 8))
        # Highlight
        pygame.draw.circle(surface, (255, 255, 255), (cx - 6, cy - 8), 4)
    elif food_index == 1:  # Fish
        # Body ellipse
        pygame.draw.ellipse(surface, BLACK, (cx - 26, cy - 14, 52, 28))
        pygame.draw.ellipse(surface, food_color, (cx - 24, cy - 12, 48, 24))
        # Tail
        pygame.draw.polygon(surface, food_color,
                            [(cx + 20, cy), (cx + 34, cy - 12), (cx + 34, cy + 12)])
        pygame.draw.polygon(surface, BLACK,
                            [(cx + 20, cy), (cx + 34, cy - 12), (cx + 34, cy + 12)], 2)
        # Eye
        pygame.draw.circle(surface, BLACK, (cx - 8, cy - 2), 4)
        pygame.draw.circle(surface, WHITE, (cx - 7, cy - 3), 2)
    elif food_index == 2:  # Cake
        # Base
        pygame.draw.rect(surface, BLACK, (cx - 20, cy - 10, 40, 28), border_radius=4)
        pygame.draw.rect(surface, food_color, (cx - 18, cy - 8, 36, 24), border_radius=3)
        # Frosting top
        pygame.draw.rect(surface, (255, 255, 240), (cx - 18, cy - 12, 36, 8), border_radius=3)
        # Cherry
        pygame.draw.circle(surface, BLACK, (cx, cy - 16), 6)
        pygame.draw.circle(surface, (220, 50, 50), (cx, cy - 16), 5)
        pygame.draw.circle(surface, (255, 255, 255), (cx - 2, cy - 18), 2)
    elif food_index == 3:  # Milk
        # Bottle body
        pygame.draw.rect(surface, BLACK, (cx - 14, cy - 18, 28, 36), border_radius=5)
        pygame.draw.rect(surface, food_color, (cx - 12, cy - 16, 24, 32), border_radius=4)
        # Cap
        pygame.draw.rect(surface, BLACK, (cx - 10, cy - 24, 20, 10), border_radius=3)
        pygame.draw.rect(surface, (100, 150, 220), (cx - 8, cy - 22, 16, 6), border_radius=2)
        # Label
        pygame.draw.rect(surface, (255, 255, 255), (cx - 8, cy - 4, 16, 8), border_radius=2)


# --------------- Particle system (with gravity) ---------------

class Particles:
    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=5, speed=40, lifetime=0.8, size=3,
             shape="circle", gravity=30):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(speed * 0.5, speed)
            self.particles.append({
                "x": x, "y": y,
                "vx": math.cos(angle) * spd,
                "vy": math.sin(angle) * spd - 20,
                "life": lifetime,
                "max_life": lifetime,
                "color": color,
                "size": size,
                "shape": shape,
                "rotation": random.uniform(0, 2 * math.pi),
                "rotation_speed": random.uniform(-3, 3),
                "gravity": gravity,
            })

    def update(self, dt):
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += p["gravity"] * dt
            p["life"] -= dt
            p["rotation"] += p["rotation_speed"] * dt
        self.particles = [p for p in self.particles if p["life"] > 0]

    def draw(self, surface):
        for p in self.particles:
            alpha = p["life"] / p["max_life"]
            size = max(1, int(p["size"] * alpha))
            x, y = int(p["x"]), int(p["y"])
            shape = p["shape"]
            color = p["color"]
            rot = p["rotation"]

            if size < 3 or shape == "circle":
                pygame.draw.circle(surface, color, (x, y), size)
            elif shape == "star":
                _draw_star(surface, x, y, size, color, rot)
            elif shape == "sparkle":
                _draw_sparkle(surface, x, y, size, color, rot)
            elif shape == "heart":
                _draw_heart(surface, x, y, size, color, rot)
            elif shape == "zzz":
                _draw_zzz_letter(surface, x, y, size, color, rot)
            elif shape == "bubble":
                _draw_bubble(surface, x, y, size, color, rot)
            else:
                pygame.draw.circle(surface, color, (x, y), size)


# --------------- Outline helper ---------------

def _inflate_triangle(points, amount):
    """Push triangle vertices outward from centroid by amount pixels."""
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    result = []
    for px, py in points:
        dx = px - cx
        dy = py - cy
        dist = math.hypot(dx, dy)
        if dist < 0.01:
            result.append((px, py))
        else:
            result.append((px + dx / dist * amount, py + dy / dist * amount))
    return result


# --------------- Kawaii eye / mouth drawing ---------------

def _draw_kawaii_eyes(surface, cx, eye_y, s, eye_style, blink_close, is_cat=True,
                     appearance_eye_style=None):
    """Draw kawaii-style eyes: solid black circles with single white highlight.

    eye_style: expression-driven style (normal/sparkle/happy_closed/dizzy/sad)
    appearance_eye_style: designer appearance style (big/sleepy/sparkly/wink/dot)
    """
    r = int(7 * s)   # eye radius
    spacing = int(12 * s)

    # "dot" appearance style: tiny solid dots, no highlight
    if appearance_eye_style == "dot" and eye_style in ("normal", "sparkle"):
        dot_r = max(1, int(3 * s))
        for side in [-1, 1]:
            ex = cx + side * spacing
            draw_r = max(1, int(dot_r * (1.0 - blink_close * 0.85)))
            if blink_close > 0.7:
                arc_w = int(8 * s)
                arc_h = int(3 * s)
                pygame.draw.arc(surface, BLACK,
                                (ex - arc_w // 2, eye_y - arc_h // 2, arc_w, arc_h),
                                0, math.pi, 2)
            else:
                pygame.draw.circle(surface, BLACK, (ex, eye_y), draw_r)
        return

    # "wink" appearance style: left eye normal, right eye happy_closed arc
    if appearance_eye_style == "wink" and eye_style in ("normal", "sparkle"):
        for side in [-1, 1]:
            ex = cx + side * spacing
            if side == 1:
                # Right eye: happy_closed arc (winking)
                arc_w = int(12 * s)
                arc_h = int(6 * s)
                pygame.draw.arc(surface, BLACK,
                                (ex - arc_w // 2, eye_y - arc_h // 2, arc_w, arc_h),
                                0, math.pi, 2)
            else:
                # Left eye: normal
                draw_r = max(2, int(r * (1.0 - blink_close * 0.85)))
                if blink_close > 0.7:
                    arc_w = int(12 * s)
                    arc_h = int(4 * s)
                    pygame.draw.arc(surface, BLACK,
                                    (ex - arc_w // 2, eye_y - arc_h // 2, arc_w, arc_h),
                                    0, math.pi, 2)
                else:
                    pygame.draw.circle(surface, BLACK, (ex, eye_y), draw_r)
                    hl_r = max(1, int(3 * s))
                    hl_x = ex + int(2 * s)
                    hl_y = eye_y - int(2 * s * (1.0 - blink_close * 0.5))
                    pygame.draw.circle(surface, WHITE, (hl_x, hl_y), hl_r)
        return

    for side in [-1, 1]:
        ex = cx + side * spacing

        if eye_style == "happy_closed":
            arc_w = int(12 * s)
            arc_h = int(6 * s)
            pygame.draw.arc(surface, BLACK,
                            (ex - arc_w // 2, eye_y - arc_h // 2, arc_w, arc_h),
                            0, math.pi, 2)
            continue

        if eye_style == "dizzy":
            sz = int(5 * s)
            pygame.draw.line(surface, BLACK, (ex - sz, eye_y - sz), (ex + sz, eye_y + sz), 2)
            pygame.draw.line(surface, BLACK, (ex + sz, eye_y - sz), (ex - sz, eye_y + sz), 2)
            continue

        if eye_style == "sad":
            sad_r = int(5 * s)
            pygame.draw.circle(surface, BLACK, (ex, eye_y), sad_r)
            pygame.draw.circle(surface, WHITE, (ex + int(2 * s), eye_y - int(2 * s)),
                               max(1, int(2 * s)))
            if side == 1:
                tear_y = eye_y + sad_r + int(2 * s)
                pygame.draw.circle(surface, (150, 200, 255), (ex + int(3 * s), tear_y),
                                   max(1, int(3 * s)))
            continue

        # Normal / sparkle: solid black circle with single white highlight
        draw_r = max(2, int(r * (1.0 - blink_close * 0.85)))

        if blink_close > 0.7:
            arc_w = int(12 * s)
            arc_h = int(4 * s)
            pygame.draw.arc(surface, BLACK,
                            (ex - arc_w // 2, eye_y - arc_h // 2, arc_w, arc_h),
                            0, math.pi, 2)
            continue

        # Solid black circle
        pygame.draw.circle(surface, BLACK, (ex, eye_y), draw_r)

        # Single white highlight (upper-right)
        hl_r = max(1, int(3 * s))
        hl_x = ex + int(2 * s)
        hl_y = eye_y - int(2 * s * (1.0 - blink_close * 0.5))
        pygame.draw.circle(surface, WHITE, (hl_x, hl_y), hl_r)

        # Extra sparkle for "sparkle" style or "sparkly" appearance style
        if eye_style == "sparkle" or appearance_eye_style == "sparkly":
            hl_r2 = max(1, int(1.5 * s))
            pygame.draw.circle(surface, WHITE,
                               (ex - int(1 * s), eye_y + int(2 * s)), hl_r2)
            if appearance_eye_style == "sparkly":
                # Additional sparkle dots
                hl_r3 = max(1, int(1 * s))
                pygame.draw.circle(surface, WHITE,
                                   (ex - int(3 * s), eye_y - int(1 * s)), hl_r3)


def _draw_kawaii_mouth(surface, cx, mouth_y, mouth_type, s, is_cat=True, time_val=0.0):
    """Draw kawaii mouth based on type."""
    if mouth_type == "eating":
        if int(time_val * 6) % 2 == 0:
            r = int(4 * s)
            pygame.draw.circle(surface, BLACK, (cx, mouth_y), r)
            pygame.draw.circle(surface, (180, 80, 80), (cx, mouth_y), max(1, r - 1))
        else:
            w = int(8 * s)
            h = int(4 * s)
            pygame.draw.arc(surface, BLACK,
                            (cx - w // 2, mouth_y - h // 2, w, h),
                            math.pi, 2 * math.pi, 2)
        return

    if is_cat and mouth_type in ("smile", "small_smile"):
        # Cat "w" mouth
        w = int(5 * s)
        h = int(3 * s)
        for side in [-1, 1]:
            mx = cx + side * int(3 * s)
            pygame.draw.arc(surface, BLACK,
                            (mx - w // 2, mouth_y - h // 2, w, h),
                            math.pi, 2 * math.pi, 2)
        return

    if mouth_type == "big_smile":
        w = int(12 * s)
        h = int(8 * s)
        pygame.draw.arc(surface, BLACK,
                        (cx - w // 2, mouth_y - h // 3, w, h),
                        math.pi, 2 * math.pi, 2)
        # No fang — clean kawaii style
        return

    if mouth_type == "frown":
        w = int(8 * s)
        h = int(4 * s)
        pygame.draw.arc(surface, BLACK,
                        (cx - w // 2, mouth_y, w, h),
                        0, math.pi, 2)
        return

    if mouth_type == "flat":
        hw = int(5 * s)
        pygame.draw.line(surface, BLACK,
                         (cx - hw, mouth_y + int(2 * s)),
                         (cx + hw, mouth_y + int(2 * s)), 1)
        return

    # Default: small smile arc
    w = int(8 * s)
    h = int(4 * s)
    pygame.draw.arc(surface, BLACK,
                    (cx - w // 2, mouth_y - h // 2, w, h),
                    math.pi, 2 * math.pi, 1)


# --------------- Main PetDrawer ---------------

class PetDrawer:
    def __init__(self):
        self.time = 0.0
        self.particles = Particles()
        self.ear_twitch_timer = 0.0
        self.ear_twitch_offset = 0
        self.zzz_timer = 0.0

        # Blinking state
        self.blink_timer = random.uniform(BLINK_MIN_INTERVAL, BLINK_MAX_INTERVAL)
        self.blink_phase = 0.0
        self.is_blinking = False
        self.blink_progress = 0.0
        self.pending_double_blink = False

        # Fidget state
        self.fidget_timer = random.uniform(FIDGET_MIN_INTERVAL, FIDGET_MAX_INTERVAL)
        self.fidget_type = None
        self.fidget_progress = 0.0
        self.fidget_direction = 1
        self.last_action = ACTION_IDLE

    def update(self, dt):
        self.time += dt
        self.particles.update(dt)

        self.ear_twitch_timer -= dt
        if self.ear_twitch_timer <= 0:
            self.ear_twitch_timer = random.uniform(2.0, 5.0)
            self.ear_twitch_offset = random.choice([-3, 3, -5, 5])
        elif self.ear_twitch_timer < 0.15:
            self.ear_twitch_offset = 0

        self.zzz_timer += dt
        self._update_blink(dt)
        self._update_fidget(dt)

    def _update_blink(self, dt):
        if self.is_blinking:
            self.blink_progress += dt / BLINK_DURATION
            if self.blink_progress >= 1.0:
                self.blink_progress = 0.0
                self.is_blinking = False
                if self.pending_double_blink:
                    self.pending_double_blink = False
                    self.is_blinking = True
                    self.blink_progress = 0.0
                else:
                    self.blink_timer = random.uniform(BLINK_MIN_INTERVAL, BLINK_MAX_INTERVAL)
            if self.blink_progress < 0.5:
                self.blink_phase = self.blink_progress * 2.0
            else:
                self.blink_phase = (1.0 - self.blink_progress) * 2.0
        else:
            self.blink_phase = 0.0
            self.blink_timer -= dt
            if self.blink_timer <= 0:
                self.is_blinking = True
                self.blink_progress = 0.0
                self.pending_double_blink = random.random() < 0.2

    def _update_fidget(self, dt):
        if self.fidget_type is not None:
            self.fidget_progress += dt / FIDGET_DURATION
            if self.fidget_progress >= 1.0:
                self.fidget_type = None
                self.fidget_progress = 0.0
        else:
            self.fidget_timer -= dt
            if self.fidget_timer <= 0:
                self.fidget_timer = random.uniform(FIDGET_MIN_INTERVAL, FIDGET_MAX_INTERVAL)
                self.fidget_type = random.choice(["head_tilt", "weight_shift", "look_around"])
                self.fidget_progress = 0.0
                self.fidget_direction = random.choice([-1, 1])

    def _get_fidget_offsets(self, action):
        if action != ACTION_IDLE or self.fidget_type is None:
            return 0, 0
        t = self.fidget_progress
        curve = _ease_in_out_cubic(1.0 - abs(t * 2.0 - 1.0))
        d = self.fidget_direction
        if self.fidget_type == "head_tilt":
            return int(4 * curve * d), 0
        elif self.fidget_type == "weight_shift":
            return 0, int(3 * curve * d)
        return 0, 0

    def draw(self, surface, pet):
        # Cancel fidget on action change
        if pet.action != self.last_action:
            if self.last_action == ACTION_IDLE:
                self.fidget_type = None
                self.fidget_progress = 0.0
            self.last_action = pet.action

        cx = PET_CENTER_X
        cy = PET_CENTER_Y
        appearance = getattr(pet, 'appearance', None)
        colors = _get_pet_colors(pet.pet_type, pet.evolution_tier, appearance)

        breath = _smooth_sin(self.time, 2.0) * 3

        base_scale = GROWTH_SCALE.get(pet.growth_stage, 1.0)
        tier_mod = 0.0
        if pet.evolution_tier == "thriving":
            tier_mod = 0.05
        elif pet.evolution_tier == "scruffy":
            tier_mod = -0.05
        scale = base_scale + tier_mod

        # Action-specific offsets
        head_offset_y = 0
        head_offset_x = 0
        body_bounce = 0
        body_sway_x = 0

        if pet.action == ACTION_EATING:
            head_offset_y = abs(_smooth_sin(self.time, 8.0)) * 6
            head_offset_x = -8
            if random.random() < 0.12:
                bowl_x = cx - int(55 * scale)
                particle_color = pet.last_food_color if pet.last_food_color else FOOD_COLOR
                self.particles.emit(bowl_x, GROUND_Y - 10, particle_color,
                                    count=3, speed=35, lifetime=0.4, size=3,
                                    gravity=50)

        elif pet.action == ACTION_PLAYING:
            body_bounce = abs(_smooth_sin(self.time, 6.0)) * 18
            if random.random() < 0.12:
                self.particles.emit(
                    cx + random.randint(-30, 30),
                    cy - 20 + random.randint(-20, 10),
                    STAR_COLOR, count=random.randint(2, 3),
                    speed=25, lifetime=0.6, size=5, shape="star")

        elif pet.action == ACTION_CLEANING:
            clean_idx = pet.last_clean_index
            if clean_idx == 0:  # Bath: blue water drops with gravity, larger bubbles
                body_sway_x = _smooth_sin(self.time, 4.0) * 5
                if random.random() < 0.18:
                    self.particles.emit(
                        cx + random.randint(-30, 30),
                        cy + random.randint(-30, 0),
                        (100, 180, 255), count=2, speed=20, lifetime=0.8, size=4,
                        shape="circle", gravity=50)
                if random.random() < 0.12:
                    self.particles.emit(
                        cx + random.randint(-25, 25),
                        cy + random.randint(-20, 10),
                        BUBBLE_COLOR, count=1, speed=10, lifetime=1.4, size=8,
                        shape="bubble", gravity=-8)
            elif clean_idx == 1:  # Brush: pink streak sparkles moving sideways
                body_sway_x = _smooth_sin(self.time, 5.0) * 7
                if random.random() < 0.18:
                    side = random.choice([-1, 1])
                    self.particles.emit(
                        cx + side * random.randint(10, 30),
                        cy + random.randint(-20, 10),
                        (240, 160, 200), count=2, speed=30, lifetime=0.6, size=4,
                        shape="sparkle", gravity=-3)
            elif clean_idx == 2:  # Towel: soft white puffs floating up
                body_sway_x = _smooth_sin(self.time, 3.0) * 4
                if random.random() < 0.14:
                    self.particles.emit(
                        cx + random.randint(-20, 20),
                        cy + random.randint(-10, 10),
                        (240, 240, 255), count=1, speed=8, lifetime=1.2, size=6,
                        shape="circle", gravity=-12)
                if random.random() < 0.06:
                    self.particles.emit(
                        cx + random.randint(-15, 15),
                        cy + random.randint(-25, -5),
                        SPARKLE_COLOR, count=1, speed=8, lifetime=0.8, size=3,
                        shape="sparkle", gravity=-5)
            elif clean_idx == 3:  # Pick Up: small brown sparkles near ground
                body_sway_x = _smooth_sin(self.time, 4.0) * 3
                if random.random() < 0.12:
                    self.particles.emit(
                        cx + random.randint(-20, 60),
                        GROUND_Y - random.randint(5, 20),
                        (140, 100, 60), count=2, speed=15, lifetime=0.5, size=3,
                        shape="sparkle", gravity=20)
            else:  # Default: original bubbles+sparkles
                body_sway_x = _smooth_sin(self.time, 4.0) * 5
                if random.random() < 0.15:
                    self.particles.emit(
                        cx + random.randint(-25, 25),
                        cy + random.randint(-20, 10),
                        BUBBLE_COLOR, count=1, speed=12, lifetime=1.2, size=6,
                        shape="bubble", gravity=-10)
                if random.random() < 0.08:
                    self.particles.emit(
                        cx + random.randint(-20, 20),
                        cy + random.randint(-30, 0),
                        SPARKLE_COLOR, count=1, speed=10, lifetime=0.8, size=4,
                        shape="sparkle", gravity=-5)

        elif pet.action == ACTION_SLEEPING:
            if self.zzz_timer > 1.0:
                self.zzz_timer = 0.0
                self.particles.emit(cx + 30, cy - 50, ZZZ_COLOR,
                                    count=1, speed=15, lifetime=1.5, size=6,
                                    shape="zzz", gravity=-5)

        # Sick shaking
        shake_x = 0
        if pet.is_sick and pet.action != ACTION_SLEEPING:
            shake_x = math.sin(self.time * 20) * 3
            if random.random() < 0.08:
                self.particles.emit(cx + random.choice([-20, 20]),
                                    cy - 50, SWEAT_COLOR,
                                    count=1, speed=20, lifetime=0.6, size=3)

        # Runaway offset
        runaway_offset_x = 0
        if pet.action == ACTION_RUNNING_AWAY:
            runaway_offset_x = pet.runaway_progress * 500

        # Fidget offsets
        fidget_head_x, fidget_body_x = self._get_fidget_offsets(pet.action)

        final_x = cx + shake_x + runaway_offset_x + fidget_body_x + body_sway_x
        final_y = cy - body_bounce

        blink_close = self.blink_phase if pet.action != ACTION_SLEEPING else 0.0
        expression = _get_expression(pet)

        # Draw shadow on the grass line
        self._draw_shadow(surface, final_x, scale, body_bounce, pet.action)

        # Draw props BEHIND pet
        if pet.action == ACTION_EATING:
            bowl_x = cx - int(55 * scale) + int(shake_x)
            if pet.last_food_index >= 0 and pet.last_food_color:
                _draw_food_prop(surface, bowl_x, GROUND_Y - 15,
                                pet.last_food_index, pet.last_food_color)
            else:
                _draw_food_bowl(surface, bowl_x, GROUND_Y - 5)

        # Draw the pet
        if pet.action == ACTION_SLEEPING:
            self._draw_sleeping(surface, pet, colors, final_x, final_y, scale, breath)
        else:
            self._draw_standing(surface, pet, colors, final_x, final_y,
                                scale, breath, head_offset_y, head_offset_x,
                                blink_close, expression, fidget_head_x)

        # Draw props IN FRONT of pet
        if pet.action == ACTION_PLAYING:
            ball_x = cx + int(55 * scale) + int(shake_x)
            _draw_toy_ball(surface, ball_x, GROUND_Y - 5, self.time)

        # Cheek blush (always for kawaii when not running away)
        if pet.action != ACTION_RUNNING_AWAY and pet.action != ACTION_SLEEPING:
            self._draw_blush(surface, pet, final_x, final_y, scale, breath,
                             head_offset_y, head_offset_x + fidget_head_x)

        # Thriving sparkles
        if pet.evolution_tier == "thriving" and pet.action not in (ACTION_SLEEPING, ACTION_RUNNING_AWAY):
            if random.random() < 0.07:
                self.particles.emit(
                    final_x + random.randint(-35, 35),
                    final_y - 30 + random.randint(-30, 20),
                    SPARKLE_COLOR, count=1, speed=15, lifetime=0.8, size=4,
                    shape="sparkle")

        # Floating heart decoration (when not sick/running away)
        if (pet.action not in (ACTION_SICK, ACTION_RUNNING_AWAY)
                and not pet.is_sick and pet.action != ACTION_SLEEPING):
            heart_bob = math.sin(self.time * 2.5) * 3
            heart_x = final_x + int(25 * scale)
            heart_y = final_y - int(60 * scale) + heart_bob
            _draw_heart(surface, heart_x, heart_y, 4, (255, 150, 180), 0)

        # Rare idle hearts
        if (pet.action == ACTION_IDLE and pet.happiness > 80
                and random.random() < 0.01):
            self.particles.emit(
                final_x + random.randint(-20, 20),
                final_y - 60,
                (255, 120, 150), count=1, speed=18, lifetime=1.0, size=5,
                shape="heart")

        # Sick green tint
        if pet.is_sick and pet.action != ACTION_RUNNING_AWAY:
            tint_surf = pygame.Surface((100, 120), pygame.SRCALPHA)
            tint_surf.fill((0, 180, 0, 30))
            surface.blit(tint_surf, (final_x - 50, final_y - 70))

        # Draw particles on top
        self.particles.draw(surface)

    # ---- Shadow (on the grass line) ----

    def _draw_shadow(self, surface, cx, scale, bounce, action):
        shadow_y = GROUND_Y
        squish = 1.0 - bounce / 30.0
        if action == ACTION_SLEEPING:
            sw = int(65 * scale)
            sh = int(10 * scale)
        else:
            sw = int(50 * scale * max(0.6, squish))
            sh = int(12 * scale * max(0.5, squish))

        shadow_surf = pygame.Surface((sw * 2 + 10, sh * 2 + 10), pygame.SRCALPHA)
        center = (sw + 5, sh + 5)
        for i in range(5):
            f = 1.0 - i * 0.18
            alpha = max(0, int(SHADOW_BASE_ALPHA * (1.0 - i * 0.22)))
            ew = max(1, int(sw * f))
            eh = max(1, int(sh * f))
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, alpha),
                                (center[0] - ew, center[1] - eh, ew * 2, eh * 2))
        surface.blit(shadow_surf,
                     (cx - sw - 5, shadow_y - sh - 5 + int(bounce * 0.3)))

    # ---- Cheek blush (circular) ----

    def _draw_blush(self, surface, pet, cx, cy, scale, breath, head_bob, head_dx):
        if pet.happiness <= BLUSH_THRESHOLD:
            return
        s = scale
        head_r = int(KAWAII_HEAD_RADIUS * s)
        total_h = int(KAWAII_TOTAL_H * s)
        head_section = int(total_h * KAWAII_HEAD_RATIO)
        head_cy = cy - total_h // 2 + head_section // 2 + int(breath) + head_bob
        head_x = cx + head_dx

        # Position blush in lower half of head (near eyes)
        eye_y_offset = int(head_r * KAWAII_EYE_Y_RATIO)
        blush_r = int(KAWAII_BLUSH_RADIUS * s)

        alpha = min(90, int((pet.happiness - BLUSH_THRESHOLD) * 2.2))
        for side in [-1, 1]:
            bx = int(head_x) + side * int(16 * s)
            by = int(head_cy) + eye_y_offset + int(4 * s)
            blush_surf = pygame.Surface((blush_r * 2 + 2, blush_r * 2 + 2), pygame.SRCALPHA)
            pygame.draw.circle(blush_surf, (*BLUSH_COLOR, alpha),
                              (blush_r + 1, blush_r + 1), blush_r)
            surface.blit(blush_surf, (bx - blush_r - 1, by - blush_r - 1))

    # ---- Ear drawing helpers ----

    def _draw_cat_ears(self, surface, cx, head_cy, head_r, s, color, outline=False,
                       ear_scale=1.0):
        """Draw cat triangle ears. If outline=True, draw in BLACK inflated."""
        ear_twitch = self.ear_twitch_offset
        ow = OUTLINE_WIDTH if outline else 0
        fill_color = BLACK if outline else color
        es = ear_scale

        for side in [-1, 1]:
            ear_x = cx + side * int(18 * s * es)
            ear_tip_y = head_cy - head_r - int(15 * s * es) + (ear_twitch if side == 1 else 0)
            ear_points = [
                (ear_x - side * int(8 * s * es), head_cy - head_r + int(5 * s)),
                (ear_x + side * int(2 * s * es), ear_tip_y),
                (ear_x + side * int(14 * s * es), head_cy - head_r + int(8 * s)),
            ]
            if outline:
                ear_points = _inflate_triangle(ear_points, ow)
            pygame.draw.polygon(surface, fill_color, ear_points)

    def _draw_cat_ear_fill(self, surface, cx, head_cy, head_r, s, colors, ear_scale=1.0):
        """Draw cat ear body fill + dark inner fill on top of outline."""
        ear_twitch = self.ear_twitch_offset
        es = ear_scale
        for side in [-1, 1]:
            ear_x = cx + side * int(18 * s * es)
            ear_tip_y = head_cy - head_r - int(15 * s * es) + (ear_twitch if side == 1 else 0)
            ear_points = [
                (ear_x - side * int(8 * s * es), head_cy - head_r + int(5 * s)),
                (ear_x + side * int(2 * s * es), ear_tip_y),
                (ear_x + side * int(14 * s * es), head_cy - head_r + int(8 * s)),
            ]
            # Body color fill
            pygame.draw.polygon(surface, colors["body"], ear_points)
            # Dark inner fill
            inner = [
                (ear_x - side * int(5 * s * es), head_cy - head_r + int(7 * s)),
                (ear_x + side * int(2 * s * es), ear_tip_y + int(5 * s)),
                (ear_x + side * int(11 * s * es), head_cy - head_r + int(9 * s)),
            ]
            pygame.draw.polygon(surface, colors["ear_inner"], inner)

    def _draw_dog_ears(self, surface, cx, head_cy, head_r, s, color, outline=False,
                       ear_scale=1.0):
        """Draw dog floppy ears. If outline=True, draw in BLACK inflated."""
        ear_twitch = self.ear_twitch_offset
        ow = OUTLINE_WIDTH if outline else 0
        fill_color = BLACK if outline else color
        es = ear_scale

        for side in [-1, 1]:
            ear_x = cx + side * int(22 * s)
            ear_top_y = head_cy - int(8 * s)
            ear_w = int(14 * s * es) + ow * 2
            ear_h = int(28 * s * es) + (ear_twitch if side == 1 else 0) + ow * 2
            ear_rect = pygame.Rect(ear_x - ear_w // 2, ear_top_y - ow, ear_w, ear_h)
            pygame.draw.ellipse(surface, fill_color, ear_rect)

    def _draw_dog_ear_fill(self, surface, cx, head_cy, head_r, s, colors, ear_scale=1.0):
        """Draw dog ear body fill + dark inner fill on top of outline."""
        ear_twitch = self.ear_twitch_offset
        es = ear_scale
        for side in [-1, 1]:
            ear_x = cx + side * int(22 * s)
            ear_top_y = head_cy - int(8 * s)
            ear_w = int(14 * s * es)
            ear_h = int(28 * s * es) + (ear_twitch if side == 1 else 0)
            ear_rect = pygame.Rect(ear_x - ear_w // 2, ear_top_y, ear_w, ear_h)
            pygame.draw.ellipse(surface, colors["body"], ear_rect)
            # Dark inner fill
            inner_w = int(10 * s * es)
            inner_h = int(20 * s * es) + (ear_twitch if side == 1 else 0)
            inner_rect = pygame.Rect(ear_x - inner_w // 2, ear_top_y + int(3 * s),
                                     inner_w, inner_h)
            pygame.draw.ellipse(surface, colors["ear_inner"], inner_rect)

    # ---- Round ears (bear-style, for ear_style="round") ----

    def _draw_round_ears(self, surface, cx, head_cy, head_r, s, color, outline=False,
                         ear_scale=1.0):
        """Draw round bear-style ears. If outline=True, draw in BLACK inflated."""
        ow = OUTLINE_WIDTH if outline else 0
        fill_color = BLACK if outline else color
        es = ear_scale

        for side in [-1, 1]:
            ear_x = cx + side * int(20 * s * es)
            ear_y = head_cy - head_r + int(2 * s)
            ear_r = int(10 * s * es) + ow
            pygame.draw.circle(surface, fill_color, (ear_x, ear_y), ear_r)

    def _draw_round_ear_fill(self, surface, cx, head_cy, head_r, s, colors, ear_scale=1.0):
        """Draw round ear body fill + dark inner fill on top of outline."""
        es = ear_scale
        for side in [-1, 1]:
            ear_x = cx + side * int(20 * s * es)
            ear_y = head_cy - head_r + int(2 * s)
            ear_r = int(10 * s * es)
            pygame.draw.circle(surface, colors["body"], (ear_x, ear_y), ear_r)
            # Dark inner fill
            inner_r = int(7 * s * es)
            pygame.draw.circle(surface, colors["ear_inner"], (ear_x, ear_y), inner_r)

    # ---- Tail with outline ----

    def _draw_tail(self, surface, pet, colors, cx, cy, s, breath, tail_scale=1.0,
                   tail_style=None):
        tail_base_x = cx + int(KAWAII_BODY_W * s * 0.8)
        tail_base_y = cy + int(breath)

        wag_speed = 3.0
        if pet.action in (ACTION_PLAYING, ACTION_CLEANING):
            wag_speed = 8.0

        # Apply tail_style scale modifiers
        ts = tail_scale
        if tail_style == "short":
            ts *= 0.5
        elif tail_style == "long":
            ts *= 1.5
        elif tail_style == "fluffy":
            ts *= 1.4

        if pet.pet_type == PET_CAT:
            # Cat tail: overlapping circles along curve
            circle_count = 10
            if tail_style == "fluffy":
                circle_count = 14
            amplitude = 8 * ts
            if tail_style == "curly":
                amplitude = 16 * ts

            # Outline pass
            for i in range(circle_count):
                t = i / max(1, circle_count - 1)
                tx = tail_base_x + t * int(25 * s * ts)
                ty = (tail_base_y - t * int(35 * s * ts)
                      + _smooth_sin(self.time, wag_speed, t * 3) * amplitude * (1 - t * 0.5))
                r = max(2, int((5 - t * 2) * s * ts))
                if tail_style == "fluffy":
                    r = max(2, int((6 - t * 2) * s * ts))
                pygame.draw.circle(surface, BLACK, (int(tx), int(ty)), r + OUTLINE_WIDTH)
            # Fill pass
            for i in range(circle_count):
                t = i / max(1, circle_count - 1)
                tx = tail_base_x + t * int(25 * s * ts)
                ty = (tail_base_y - t * int(35 * s * ts)
                      + _smooth_sin(self.time, wag_speed, t * 3) * amplitude * (1 - t * 0.5))
                r = max(2, int((5 - t * 2) * s * ts))
                if tail_style == "fluffy":
                    r = max(2, int((6 - t * 2) * s * ts))
                pygame.draw.circle(surface, colors["body"], (int(tx), int(ty)), r)
        else:
            # Dog tail: line + circle tip
            wag = _smooth_sin(self.time, wag_speed) * 15 * ts
            tail_end_x = tail_base_x + int(20 * s * ts)
            tail_end_y = tail_base_y - int(30 * s * ts) + wag

            if tail_style == "curly":
                # Spiral circles for dogs
                for i in range(8):
                    t = i / 7
                    angle = t * math.pi * 2
                    spiral_r = int(8 * s * ts * (1 - t * 0.3))
                    sx = tail_base_x + int(t * 15 * s * ts) + int(math.cos(angle) * spiral_r)
                    sy = tail_base_y - int(t * 25 * s * ts) + int(math.sin(angle) * spiral_r) + wag * t
                    cr = max(2, int((4 - t) * s * ts))
                    pygame.draw.circle(surface, BLACK, (int(sx), int(sy)), cr + OUTLINE_WIDTH)
                for i in range(8):
                    t = i / 7
                    angle = t * math.pi * 2
                    spiral_r = int(8 * s * ts * (1 - t * 0.3))
                    sx = tail_base_x + int(t * 15 * s * ts) + int(math.cos(angle) * spiral_r)
                    sy = tail_base_y - int(t * 25 * s * ts) + int(math.sin(angle) * spiral_r) + wag * t
                    cr = max(2, int((4 - t) * s * ts))
                    pygame.draw.circle(surface, colors["body"], (int(sx), int(sy)), cr)
            else:
                # Standard dog tail (line + circle tip)
                # Outline pass
                pygame.draw.line(surface, BLACK,
                                 (tail_base_x, tail_base_y),
                                 (tail_end_x, tail_end_y), 5 + OUTLINE_WIDTH * 2)
                pygame.draw.circle(surface, BLACK,
                                   (tail_end_x, tail_end_y), max(3, int(6 * ts)) + OUTLINE_WIDTH)
                # Fill pass
                pygame.draw.line(surface, colors["body"],
                                 (tail_base_x, tail_base_y),
                                 (tail_end_x, tail_end_y), 5)
                pygame.draw.circle(surface, colors["body"],
                                   (tail_end_x, tail_end_y), max(3, int(6 * ts)))

            if tail_style == "fluffy":
                # Extra fluffy tip circles for dog
                for i in range(4):
                    angle = math.pi * 2 * i / 4
                    fx = tail_end_x + int(math.cos(angle) * 4 * s)
                    fy = tail_end_y + int(math.sin(angle) * 4 * s)
                    pygame.draw.circle(surface, BLACK, (int(fx), int(fy)), int(3 * s) + OUTLINE_WIDTH)
                for i in range(4):
                    angle = math.pi * 2 * i / 4
                    fx = tail_end_x + int(math.cos(angle) * 4 * s)
                    fy = tail_end_y + int(math.sin(angle) * 4 * s)
                    pygame.draw.circle(surface, colors["body"], (int(fx), int(fy)), int(3 * s))

        # Ribbon bow at tail tip
        if tail_style == "ribbon":
            # Get accent_color from appearance
            accent = colors.get("ear_inner", (255, 100, 120))
            appearance = getattr(pet, 'appearance', None)
            if appearance and appearance.get("accent_color"):
                accent = tuple(appearance["accent_color"])
            if pet.pet_type == PET_CAT:
                # Find tip position
                tip_t = 1.0
                tip_x = int(tail_base_x + tip_t * int(25 * s * ts))
                tip_y = int(tail_base_y - tip_t * int(35 * s * ts)
                           + _smooth_sin(self.time, wag_speed, tip_t * 3) * 8 * ts * 0.5)
            else:
                tip_x = tail_base_x + int(20 * s * ts)
                tip_y = tail_base_y - int(30 * s * ts) + int(_smooth_sin(self.time, wag_speed) * 15 * ts)
            bow_r = int(4 * s)
            pygame.draw.circle(surface, BLACK, (tip_x - bow_r, tip_y), bow_r + 1)
            pygame.draw.circle(surface, BLACK, (tip_x + bow_r, tip_y), bow_r + 1)
            pygame.draw.circle(surface, accent, (tip_x - bow_r, tip_y), bow_r)
            pygame.draw.circle(surface, accent, (tip_x + bow_r, tip_y), bow_r)
            pygame.draw.circle(surface, _tint_color(accent, -30), (tip_x, tip_y), int(2 * s))

    # ---- Fur style on head ----

    def _draw_fur_style(self, surface, fur_style, head_x, head_cy, head_r, s, colors):
        """Draw hair/fur on top of the pet's head."""
        if not fur_style or fur_style == "short":
            return

        body_color = colors["body"]
        body_dark = colors["body_dark"]
        accent = colors.get("ear_inner", body_dark)

        if fur_style == "fluffy":
            # 5-6 small overlapping circles protruding above head outline
            for i in range(6):
                angle = math.pi * 0.2 + (math.pi * 0.6) * i / 5
                cx_f = head_x + int(math.cos(angle) * head_r * 0.6)
                cy_f = head_cy - int(math.sin(angle) * head_r * 0.95)
                r = int(6 * s)
                pygame.draw.circle(surface, BLACK, (cx_f, cy_f), r + OUTLINE_WIDTH)
            for i in range(6):
                angle = math.pi * 0.2 + (math.pi * 0.6) * i / 5
                cx_f = head_x + int(math.cos(angle) * head_r * 0.6)
                cy_f = head_cy - int(math.sin(angle) * head_r * 0.95)
                r = int(6 * s)
                pygame.draw.circle(surface, body_color, (cx_f, cy_f), r)

        elif fur_style == "long":
            # 2-3 flowing curves draping from head top past ears
            for side in [-1, 1]:
                for i in range(3):
                    start_x = head_x + side * int((5 + i * 8) * s)
                    start_y = head_cy - head_r + int(2 * s)
                    end_y = head_cy + int((10 + i * 5) * s)
                    ctrl_x = start_x + side * int(8 * s)
                    # Draw as series of circles along curve
                    for t_step in range(8):
                        t = t_step / 7
                        px = int(start_x + (ctrl_x - start_x) * t * (1 - t) * 2)
                        py = int(start_y + (end_y - start_y) * t)
                        r = max(1, int((3 - t * 1.5) * s))
                        pygame.draw.circle(surface, BLACK, (px, py), r + 1)
                    for t_step in range(8):
                        t = t_step / 7
                        px = int(start_x + (ctrl_x - start_x) * t * (1 - t) * 2)
                        py = int(start_y + (end_y - start_y) * t)
                        r = max(1, int((3 - t * 1.5) * s))
                        pygame.draw.circle(surface, body_dark, (px, py), r)

        elif fur_style == "curly":
            # Cluster of small circles along head crown
            for i in range(7):
                angle = math.pi * 0.15 + (math.pi * 0.7) * i / 6
                cx_f = head_x + int(math.cos(angle) * head_r * 0.55)
                cy_f = head_cy - int(math.sin(angle) * head_r * 0.9)
                r = int(4 * s)
                pygame.draw.circle(surface, BLACK, (cx_f, cy_f), r + OUTLINE_WIDTH)
            for i in range(7):
                angle = math.pi * 0.15 + (math.pi * 0.7) * i / 6
                cx_f = head_x + int(math.cos(angle) * head_r * 0.55)
                cy_f = head_cy - int(math.sin(angle) * head_r * 0.9)
                r = int(4 * s)
                pygame.draw.circle(surface, body_dark, (cx_f, cy_f), r)

        elif fur_style == "spiky":
            # 5-7 small triangles pointing upward, alternating heights
            for i in range(7):
                angle = math.pi * 0.15 + (math.pi * 0.7) * i / 6
                base_x = head_x + int(math.cos(angle) * head_r * 0.55)
                base_y = head_cy - int(math.sin(angle) * head_r * 0.85)
                spike_h = int((8 + (i % 2) * 5) * s)
                hw = int(3 * s)
                tri = [
                    (base_x - hw, base_y),
                    (base_x + hw, base_y),
                    (base_x, base_y - spike_h),
                ]
                pygame.draw.polygon(surface, BLACK, _inflate_triangle(tri, 1))
                pygame.draw.polygon(surface, body_dark, tri)

        elif fur_style == "mohawk":
            # Row of 3-5 circles along center-top, using accent_color
            for i in range(5):
                cy_f = head_cy - head_r + int((-3 + i * 4) * s)
                r = int((5 - abs(i - 2) * 0.8) * s)
                pygame.draw.circle(surface, BLACK, (head_x, cy_f), r + OUTLINE_WIDTH)
            for i in range(5):
                cy_f = head_cy - head_r + int((-3 + i * 4) * s)
                r = int((5 - abs(i - 2) * 0.8) * s)
                pygame.draw.circle(surface, accent, (head_x, cy_f), r)

    # ---- Standing pose (clean kawaii outline) ----

    def _draw_standing(self, surface, pet, colors, cx, cy, scale, breath, head_bob,
                       head_dx=0, blink_close=0.0, expression=None, fidget_head_x=0):
        s = scale
        if expression is None:
            expression = _get_expression(pet)

        ow = OUTLINE_WIDTH
        head_r = int(KAWAII_HEAD_RADIUS * s)
        total_h = int(KAWAII_TOTAL_H * s)

        # Stage-dependent proportions
        head_ratio = {GROWTH_BABY: 0.78, GROWTH_KID: 0.68}.get(pet.growth_stage, 0.62)
        eye_scale = {GROWTH_BABY: 1.3, GROWTH_KID: 1.0}.get(pet.growth_stage, 0.95)
        body_taper = {GROWTH_BABY: 1.0, GROWTH_KID: 0.85}.get(pet.growth_stage, 0.80)
        paw_scale = {GROWTH_BABY: 0.6, GROWTH_KID: 1.0}.get(pet.growth_stage, 1.2)
        ear_scale = {GROWTH_BABY: 0.75, GROWTH_KID: 0.9}.get(pet.growth_stage, 1.0)
        tail_scale = {GROWTH_BABY: 0.6, GROWTH_KID: 0.85}.get(pet.growth_stage, 1.0)

        head_section = int(total_h * head_ratio)
        body_section = total_h - head_section

        # Key positions
        head_x = cx + head_dx + fidget_head_x
        head_cy = cy - total_h // 2 + head_section // 2 + int(breath) + head_bob
        body_top = head_cy + head_r * 0.4   # overlap into head
        body_bottom = cy + total_h // 2 - int(KAWAII_PAW_BUMP_R * s * paw_scale) + int(breath)

        body_top_w = head_r * 0.95  # match head width at overlap
        body_bot_w = head_r * body_taper  # tapered bottom

        # Bell-shaped body polygon points
        body_poly = [
            (cx - body_top_w, body_top),
            (cx + body_top_w, body_top),
            (cx + body_bot_w, body_bottom),
            (cx - body_bot_w, body_bottom),
        ]

        # Paw bump positions
        paw_r = int(KAWAII_PAW_BUMP_R * s * paw_scale)
        paw_y = body_bottom + int(paw_r * 0.3)
        paw_spacing = int(KAWAII_PAW_SPACING * s)
        paw_positions = [
            (cx - paw_spacing, paw_y),
            (cx + paw_spacing, paw_y),
        ]

        # === Z-ORDER DRAWING ===

        # Read style overrides from appearance
        _appearance = getattr(pet, 'appearance', None)
        _tail_style = _appearance.get("tail_style") if _appearance else None
        _ear_style = _appearance.get("ear_style") if _appearance else None

        # Apply ear_style modifiers to ear_scale
        if _ear_style == "tiny":
            ear_scale *= 0.5
        elif _ear_style == "big":
            ear_scale *= 1.4

        # 1. Tail (outline + fill) — scaled by tail_scale
        self._draw_tail(surface, pet, colors, cx, cy, s, breath, tail_scale,
                        tail_style=_tail_style)

        # 2. Ears outline behind head (dog-style floppy or round, drawn before head)
        _use_floppy = (pet.pet_type == PET_DOG and _ear_style not in ("pointy", "round")) or \
                      (pet.pet_type == PET_CAT and _ear_style == "floppy")
        _use_round = (_ear_style == "round")

        if _use_round:
            self._draw_round_ears(surface, int(head_x), int(head_cy), head_r, s,
                                  colors["body_dark"], outline=True, ear_scale=ear_scale)
        elif _use_floppy:
            floppy_scale = ear_scale * (1.4 if pet.pet_type == PET_DOG and _ear_style == "floppy" else 1.0)
            self._draw_dog_ears(surface, int(head_x), int(head_cy), head_r, s,
                               colors["body_dark"], outline=True, ear_scale=floppy_scale)

        # 3. Body bell polygon outline (BLACK, inflated)
        outline_poly = []
        poly_cx = sum(p[0] for p in body_poly) / len(body_poly)
        poly_cy = sum(p[1] for p in body_poly) / len(body_poly)
        for px, py in body_poly:
            dx = px - poly_cx
            dy = py - poly_cy
            dist = math.hypot(dx, dy)
            if dist > 0.01:
                outline_poly.append((px + dx / dist * ow, py + dy / dist * ow))
            else:
                outline_poly.append((px, py))
        pygame.draw.polygon(surface, BLACK, outline_poly)

        # 4. Head circle outline (BLACK, inflated)
        pygame.draw.circle(surface, BLACK, (int(head_x), int(head_cy)), head_r + ow)

        # 5. Paw bump circles outline (BLACK, inflated)
        for px, py in paw_positions:
            pygame.draw.circle(surface, BLACK, (int(px), int(py)), paw_r + ow)

        # 6. Body bell polygon fill (body color)
        pygame.draw.polygon(surface, colors["body"], body_poly)

        # 7. Head circle fill (body color)
        pygame.draw.circle(surface, colors["body"], (int(head_x), int(head_cy)), head_r)

        # 8. Paw bump circles fill (body color)
        for px, py in paw_positions:
            pygame.draw.circle(surface, colors["body"], (int(px), int(py)), paw_r)

        # Fill gap between body and paws (body color rect to cover outline seam)
        gap_rect = pygame.Rect(int(cx - body_bot_w), int(body_bottom - paw_r),
                               int(body_bot_w * 2), int(paw_r + 2))
        pygame.draw.rect(surface, colors["body"], gap_rect)

        # Adult paw pads: draw 3 tiny darker dots on each paw
        if pet.growth_stage not in (GROWTH_BABY, GROWTH_KID):
            pad_color = colors["body_dark"]
            for px, py in paw_positions:
                for dx in [-2, 0, 2]:
                    pygame.draw.circle(surface, pad_color,
                                       (int(px + dx * s), int(py + 1)), max(1, int(1.5 * s)))

        # 8b. Fur style (after head fill, before ears and features)
        appearance = getattr(pet, 'appearance', None)
        fur_style = appearance.get("fur_style") if appearance else None
        if fur_style:
            self._draw_fur_style(surface, fur_style, int(head_x), int(head_cy),
                                 head_r, s, colors)

        # 9. Ears: outline + fill (on top of head) — routed by ear_style
        if _use_round:
            self._draw_round_ear_fill(surface, int(head_x), int(head_cy), head_r, s,
                                      colors, ear_scale=ear_scale)
        elif _use_floppy:
            # Floppy ears (cat with floppy or default dog)
            floppy_scale = ear_scale * (1.4 if pet.pet_type == PET_DOG and _ear_style == "floppy" else 1.0)
            self._draw_dog_ear_fill(surface, int(head_x), int(head_cy), head_r, s,
                                    colors, ear_scale=floppy_scale)
        elif pet.pet_type == PET_CAT or (pet.pet_type == PET_DOG and _ear_style == "pointy"):
            # Pointy ears (default cat or dog with pointy)
            pointy_scale = ear_scale * (1.3 if pet.pet_type == PET_CAT and _ear_style == "pointy" else 1.0)
            self._draw_cat_ears(surface, int(head_x), int(head_cy), head_r, s,
                               colors["body"], outline=True, ear_scale=pointy_scale)
            self._draw_cat_ear_fill(surface, int(head_x), int(head_cy), head_r, s,
                                    colors, ear_scale=pointy_scale)
        elif pet.pet_type == PET_DOG:
            # Default dog ears (floppy)
            self._draw_dog_ear_fill(surface, int(head_x), int(head_cy), head_r, s,
                                    colors, ear_scale=ear_scale)

        # 10. Facial features (with eye_scale + appearance eye_style)
        _app_eye_style = appearance.get("eye_style") if appearance else None
        # "big" modifies eye_scale; "sleepy" modifies blink_close
        _adj_eye_scale = eye_scale
        _adj_blink = blink_close
        if _app_eye_style == "big":
            _adj_eye_scale *= 1.3
        if _app_eye_style == "sleepy" and expression and expression.get("eye_style") in ("normal", "sparkle", None):
            _adj_blink = max(_adj_blink, 0.5)
        # "sparkly" forces sparkle expression eye_style
        _adj_expression = expression
        if _app_eye_style == "sparkly" and expression and expression.get("eye_style") in ("normal", None):
            _adj_expression = dict(expression)
            _adj_expression["eye_style"] = "sparkle"

        if pet.pet_type == PET_CAT:
            self._draw_cat_features(surface, pet, colors, int(head_x), int(head_cy), head_r, s,
                                    _adj_blink, _adj_expression, eye_scale=_adj_eye_scale,
                                    appearance_eye_style=_app_eye_style)
        else:
            self._draw_dog_features(surface, pet, colors, int(head_x), int(head_cy), head_r, s,
                                    _adj_blink, _adj_expression, eye_scale=_adj_eye_scale,
                                    appearance_eye_style=_app_eye_style)

        # 11. Designer accessories (pattern, scarf, collar, glasses, hat, special)
        self._draw_designer_accessories(surface, pet, int(head_x), int(head_cy), head_r,
                                         cx, body_top, s, body_poly)

        # 12. Stage accessories (bow, bell, collar, bandana, etc.)
        self._draw_stage_accessories(surface, pet, int(head_x), int(head_cy), head_r,
                                     cx, body_top, s)

    # ---- Sleeping pose (kawaii outline) ----

    def _draw_sleeping(self, surface, pet, colors, cx, cy, scale, breath):
        s = scale
        ow = OUTLINE_WIDTH

        # Curled body
        body_w = int(55 * s)
        body_h = int(30 * s)
        body_y = cy + 10 + breath * 0.5

        # Baby has proportionally larger head when sleeping too
        head_scale = 28
        if pet.growth_stage == GROWTH_BABY:
            head_scale = 32
        elif pet.growth_stage == GROWTH_KID:
            head_scale = 30
        head_r = int(head_scale * s)
        head_x = cx - int(22 * s)
        head_y = int(body_y) - int(18 * s)

        # Tail curled around
        tail_points = []
        for i in range(20):
            t = i / 19
            angle = t * math.pi * 1.2 + math.pi * 0.8
            r = int((35 + t * 15) * s)
            tx = cx + int(math.cos(angle) * r)
            ty = int(body_y) + int(math.sin(angle) * r * 0.5)
            tail_points.append((tx, ty))

        # === Outline pass (BLACK, inflated) ===
        # Tail outline
        if len(tail_points) > 2:
            if pet.pet_type == PET_CAT:
                for i, (tx, ty) in enumerate(tail_points):
                    t = i / len(tail_points)
                    r = max(2, int((4 - t * 2) * s))
                    pygame.draw.circle(surface, BLACK, (tx, ty), r + ow)
            else:
                pygame.draw.lines(surface, BLACK, False, tail_points, 5 + ow * 2)

        # Body outline
        body_outline = pygame.Rect(cx - body_w - ow, int(body_y) - body_h // 2 - ow,
                                   (body_w + ow) * 2, body_h + ow * 2)
        pygame.draw.ellipse(surface, BLACK, body_outline)

        # Head outline
        pygame.draw.circle(surface, BLACK, (head_x, head_y), head_r + ow)

        # === Fill pass (body color) ===
        # Tail fill
        if len(tail_points) > 2:
            if pet.pet_type == PET_CAT:
                for i, (tx, ty) in enumerate(tail_points):
                    t = i / len(tail_points)
                    r = max(2, int((4 - t * 2) * s))
                    pygame.draw.circle(surface, colors["body"], (tx, ty), r)
            else:
                pygame.draw.lines(surface, colors["body"], False, tail_points, 5)

        # Body fill
        body_rect = pygame.Rect(cx - body_w, int(body_y) - body_h // 2,
                                body_w * 2, body_h)
        pygame.draw.ellipse(surface, colors["body"], body_rect)

        # Head fill
        pygame.draw.circle(surface, colors["body"], (head_x, head_y), head_r)

        # Ears with outline
        if pet.pet_type == PET_CAT:
            for side in [-1, 1]:
                ear_x = head_x + side * int(16 * s)
                ear_tip_y = head_y - int(30 * s)
                ear_pts = [
                    (ear_x - side * int(4 * s), head_y - int(18 * s)),
                    (ear_x + side * int(6 * s), ear_tip_y),
                    (ear_x + side * int(14 * s), head_y - int(16 * s)),
                ]
                # Outline
                pygame.draw.polygon(surface, BLACK, _inflate_triangle(ear_pts, ow))
                # Fill
                pygame.draw.polygon(surface, colors["body"], ear_pts)
                # Dark inner
                inner = [
                    (ear_x - side * int(2 * s), head_y - int(17 * s)),
                    (ear_x + side * int(6 * s), ear_tip_y + 3),
                    (ear_x + side * int(11 * s), head_y - int(15 * s)),
                ]
                pygame.draw.polygon(surface, colors["ear_inner"], inner)
        elif pet.pet_type == PET_DOG:
            for side in [-1, 1]:
                ear_x = head_x + side * int(20 * s)
                ear_top_y = head_y - int(12 * s)
                ear_w = int(14 * s)
                ear_h = int(22 * s)
                # Outline
                ear_outline = pygame.Rect(ear_x - ear_w // 2 - ow, ear_top_y - ow,
                                         ear_w + ow * 2, ear_h + ow * 2)
                pygame.draw.ellipse(surface, BLACK, ear_outline)
                # Fill
                ear_rect = pygame.Rect(ear_x - ear_w // 2, ear_top_y, ear_w, ear_h)
                pygame.draw.ellipse(surface, colors["body"], ear_rect)
                # Dark inner
                inner_w = int(10 * s)
                inner_h = int(16 * s)
                inner_rect = pygame.Rect(ear_x - inner_w // 2, ear_top_y + int(2 * s),
                                        inner_w, inner_h)
                pygame.draw.ellipse(surface, colors["ear_inner"], inner_rect)

        # Kawaii closed eyes (^_^ arcs)
        eye_y = head_y - int(2 * s)
        for side in [-1, 1]:
            ex = head_x + side * int(10 * s)
            arc_w = int(10 * s)
            arc_h = int(5 * s)
            pygame.draw.arc(surface, BLACK,
                            (ex - arc_w // 2, eye_y - arc_h // 2, arc_w, arc_h),
                            0, math.pi, 2)

        # Sleeping blush (circular)
        if pet.happiness > BLUSH_THRESHOLD:
            alpha = min(90, int((pet.happiness - BLUSH_THRESHOLD) * 2.2))
            blush_r = int(KAWAII_BLUSH_RADIUS * s * 0.8)
            for side in [-1, 1]:
                bx = head_x + side * int(14 * s)
                by = eye_y + int(6 * s)
                blush_surf = pygame.Surface((blush_r * 2 + 2, blush_r * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(blush_surf, (*BLUSH_COLOR, alpha),
                                  (blush_r + 1, blush_r + 1), blush_r)
                surface.blit(blush_surf, (bx - blush_r - 1, by - blush_r - 1))

        # Small smile
        mouth_y = head_y + int(6 * s)
        if pet.pet_type == PET_CAT:
            w = int(4 * s)
            h = int(3 * s)
            for ms in [-1, 1]:
                mx = head_x + ms * int(3 * s)
                pygame.draw.arc(surface, BLACK,
                                (mx - w // 2, mouth_y - h // 2, w, h),
                                math.pi, 2 * math.pi, 1)
        else:
            w = int(6 * s)
            h = int(3 * s)
            pygame.draw.arc(surface, BLACK,
                            (head_x - w // 2, mouth_y - h // 2, w, h),
                            math.pi, 2 * math.pi, 1)

        # Sleeping stage accessories (simplified overlays)
        stage = pet.growth_stage
        if pet.pet_type == PET_CAT:
            if stage == GROWTH_BABY:
                # Tiny bow visible on sleeping head
                bow_x = head_x + int(8 * s)
                bow_y = head_y - head_r + int(2 * s)
                br = int(4 * s)
                pygame.draw.circle(surface, BLACK, (bow_x - br, bow_y), br + 1)
                pygame.draw.circle(surface, BLACK, (bow_x + br, bow_y), br + 1)
                pygame.draw.circle(surface, BABY_BOW_COLOR, (bow_x - br, bow_y), br)
                pygame.draw.circle(surface, BABY_BOW_COLOR, (bow_x + br, bow_y), br)
                pygame.draw.circle(surface, _tint_color(BABY_BOW_COLOR, -30),
                                   (bow_x, bow_y), int(2 * s))
            elif stage == GROWTH_KID:
                # Bell collar visible at neck area
                bell_y = int(body_y) - int(8 * s)
                bell_r = int(3 * s)
                pygame.draw.circle(surface, BLACK, (head_x + int(12 * s), bell_y), bell_r + 1)
                pygame.draw.circle(surface, KID_BELL_COLOR,
                                   (head_x + int(12 * s), bell_y), bell_r)
            else:
                # Adult gem collar peek
                gem_y = int(body_y) - int(8 * s)
                gem_r = int(3 * s)
                pygame.draw.circle(surface, BLACK, (head_x + int(12 * s), gem_y), gem_r + 1)
                pygame.draw.circle(surface, ADULT_GEM_COLOR,
                                   (head_x + int(12 * s), gem_y), gem_r)
        else:  # DOG
            if stage == GROWTH_BABY:
                # Neckerchief corner visible
                nk_x = head_x + int(14 * s)
                nk_y = int(body_y) - int(6 * s)
                pts = [(nk_x - int(4 * s), nk_y),
                       (nk_x + int(4 * s), nk_y),
                       (nk_x, nk_y + int(6 * s))]
                pygame.draw.polygon(surface, BLACK, _inflate_triangle(pts, 1))
                pygame.draw.polygon(surface, BANDANA_COLOR, pts)
            elif stage == GROWTH_KID:
                # Bandana knot visible
                knot_x = head_x + int(14 * s)
                knot_y = int(body_y) - int(6 * s)
                pygame.draw.circle(surface, BLACK, (knot_x, knot_y), int(3 * s) + 1)
                pygame.draw.circle(surface, KID_BANDANA_COLOR, (knot_x, knot_y), int(3 * s))
            else:
                # Bone tag visible
                tag_x = head_x + int(14 * s)
                tag_y = int(body_y) - int(6 * s)
                bw = int(6 * s)
                bh = int(3 * s)
                pygame.draw.rect(surface, BLACK,
                                 (tag_x - bw // 2 - 1, tag_y - bh // 2 - 1,
                                  bw + 2, bh + 2), border_radius=1)
                pygame.draw.rect(surface, BONE_TAG_COLOR,
                                 (tag_x - bw // 2, tag_y - bh // 2,
                                  bw, bh), border_radius=1)

    # ---- Cat features (kawaii — no ears, no stripes) ----

    def _draw_cat_features(self, surface, pet, colors, cx, head_cy, head_r, s,
                           blink_close=0.0, expression=None, eye_scale=1.0,
                           appearance_eye_style=None):
        if expression is None:
            expression = _get_expression(pet)

        # Eyes positioned in lower half of head
        eye_y = head_cy + int(head_r * KAWAII_EYE_Y_RATIO) - int(head_r * 0.3)
        eye_style = expression.get("eye_style", "normal")
        _draw_kawaii_eyes(surface, cx, eye_y, s * eye_scale, eye_style, blink_close, is_cat=True,
                         appearance_eye_style=appearance_eye_style)

        # Nose
        nose_y = eye_y + int(10 * s)
        pygame.draw.polygon(surface, colors["nose"], [
            (cx, nose_y + 4), (cx - 4, nose_y), (cx + 4, nose_y)
        ])

        # Mouth (close to nose)
        mouth_y = nose_y + int(3 * s)
        mouth_type = expression.get("mouth", "smile")
        _draw_kawaii_mouth(surface, cx, mouth_y, mouth_type, s, is_cat=True,
                          time_val=self.time)

        # Whiskers: 2 per side, in BLACK
        whisker_y = eye_y + int(8 * s)
        whisker_len = int(KAWAII_WHISKER_LEN * s)
        for side in [-1, 1]:
            for i in range(KAWAII_WHISKER_COUNT):
                dy = (i - (KAWAII_WHISKER_COUNT - 1) / 2) * int(4 * s)
                start_x = cx + side * int(12 * s)
                end_x = cx + side * (int(12 * s) + whisker_len)
                pygame.draw.line(surface, BLACK,
                                 (start_x, int(whisker_y + dy)),
                                 (end_x, int(whisker_y + dy + dy * 0.5)), 1)

    # ---- Dog features (kawaii — no ears) ----

    def _draw_dog_features(self, surface, pet, colors, cx, head_cy, head_r, s,
                           blink_close=0.0, expression=None, eye_scale=1.0,
                           appearance_eye_style=None):
        if expression is None:
            expression = _get_expression(pet)

        # Eyes positioned in lower half of head
        eye_y = head_cy + int(head_r * KAWAII_EYE_Y_RATIO) - int(head_r * 0.3)
        eye_style = expression.get("eye_style", "normal")
        _draw_kawaii_eyes(surface, cx, eye_y, s * eye_scale, eye_style, blink_close, is_cat=False,
                         appearance_eye_style=appearance_eye_style)

        # Nose (bigger, round, dark brown)
        nose_y = eye_y + int(10 * s)
        pygame.draw.ellipse(surface, colors["nose"],
                            (cx - 6, nose_y - 4, 12, 8))

        # Mouth (simple single arc)
        mouth_y = nose_y + int(4 * s)
        mouth_type = expression.get("mouth", "smile")
        _draw_kawaii_mouth(surface, cx, mouth_y, mouth_type, s, is_cat=False,
                          time_val=self.time)

        # Tongue only on big_smile/playing states
        if mouth_type in ("big_smile",) or pet.action == ACTION_PLAYING:
            tongue_y = mouth_y + int(2 * s)
            pygame.draw.ellipse(surface, colors.get("tongue", DOG_TONGUE),
                                (cx - 4, tongue_y, 8, 10))

    # ---- Stage accessories (baby/kid/adult visual markers) ----

    def _draw_stage_accessories(self, surface, pet, head_x, head_cy, head_r,
                                cx, body_top, s):
        """Draw stage+type-specific accessories on top of the pet."""
        stage = pet.growth_stage

        if pet.pet_type == PET_CAT:
            if stage == GROWTH_BABY:
                # Tiny pink bow on top of head
                bow_x = head_x + int(10 * s)
                bow_y = head_cy - head_r - int(2 * s)
                bow_r = int(5 * s)
                # Two bow loops
                pygame.draw.circle(surface, BLACK, (bow_x - bow_r, bow_y), bow_r + 1)
                pygame.draw.circle(surface, BLACK, (bow_x + bow_r, bow_y), bow_r + 1)
                pygame.draw.circle(surface, BABY_BOW_COLOR, (bow_x - bow_r, bow_y), bow_r)
                pygame.draw.circle(surface, BABY_BOW_COLOR, (bow_x + bow_r, bow_y), bow_r)
                # Center knot
                pygame.draw.circle(surface, BLACK, (bow_x, bow_y), int(3 * s) + 1)
                pygame.draw.circle(surface, _tint_color(BABY_BOW_COLOR, -30),
                                   (bow_x, bow_y), int(3 * s))
            elif stage == GROWTH_KID:
                # Bell collar at neck
                neck_y = int(body_top + 4 * s)
                collar_w = int(head_r * 1.4)
                # Collar band
                pygame.draw.ellipse(surface, BLACK,
                                    (cx - collar_w // 2 - 1, neck_y - 2,
                                     collar_w + 2, int(6 * s) + 2))
                pygame.draw.ellipse(surface, KID_BANDANA_COLOR,
                                    (cx - collar_w // 2, neck_y - 1,
                                     collar_w, int(6 * s)))
                # Bell
                bell_r = int(4 * s)
                pygame.draw.circle(surface, BLACK, (cx, neck_y + int(6 * s)), bell_r + 1)
                pygame.draw.circle(surface, KID_BELL_COLOR, (cx, neck_y + int(6 * s)), bell_r)
                # Bell slit
                pygame.draw.line(surface, BLACK,
                                 (cx - 2, neck_y + int(6 * s)),
                                 (cx + 2, neck_y + int(6 * s)), 1)
                pygame.draw.circle(surface, BLACK, (cx, neck_y + int(6 * s) + 2), 1)
            else:
                # Adult: elegant collar with gem + longer curled whiskers
                neck_y = int(body_top + 4 * s)
                collar_w = int(head_r * 1.5)
                # Collar band
                pygame.draw.ellipse(surface, BLACK,
                                    (cx - collar_w // 2 - 1, neck_y - 2,
                                     collar_w + 2, int(7 * s) + 2))
                pygame.draw.ellipse(surface, ADULT_COLLAR_COLOR,
                                    (cx - collar_w // 2, neck_y - 1,
                                     collar_w, int(7 * s)))
                # Gem
                gem_r = int(4 * s)
                pygame.draw.circle(surface, BLACK, (cx, neck_y + int(5 * s)), gem_r + 1)
                pygame.draw.circle(surface, ADULT_GEM_COLOR, (cx, neck_y + int(5 * s)), gem_r)
                # Gem highlight
                pygame.draw.circle(surface, WHITE,
                                   (cx - 1, neck_y + int(5 * s) - 1), max(1, int(1.5 * s)))

        else:  # DOG
            if stage == GROWTH_BABY:
                pass  # Clean baby look — no accessory
            elif stage == GROWTH_KID:
                # Red bandana at neck
                neck_y = int(body_top + 3 * s)
                nk_w = int(head_r * 1.4)
                pts = [
                    (cx - nk_w // 2, neck_y),
                    (cx + nk_w // 2, neck_y),
                    (cx + int(4 * s), neck_y + int(14 * s)),
                    (cx - int(4 * s), neck_y + int(14 * s)),
                ]
                outline_pts = []
                pcx_b = sum(p[0] for p in pts) / len(pts)
                pcy_b = sum(p[1] for p in pts) / len(pts)
                for px, py in pts:
                    dx = px - pcx_b
                    dy = py - pcy_b
                    dist = math.hypot(dx, dy)
                    if dist > 0.01:
                        outline_pts.append((px + dx / dist * 1, py + dy / dist * 1))
                    else:
                        outline_pts.append((px, py))
                pygame.draw.polygon(surface, BLACK, outline_pts)
                pygame.draw.polygon(surface, KID_BANDANA_COLOR, pts)
                # Knot circle
                pygame.draw.circle(surface, BLACK, (cx, neck_y + int(2 * s)), int(3 * s) + 1)
                pygame.draw.circle(surface, _tint_color(KID_BANDANA_COLOR, -20),
                                   (cx, neck_y + int(2 * s)), int(3 * s))
            else:
                # Adult: collar with bone tag + perky ear tips
                neck_y = int(body_top + 3 * s)
                collar_w = int(head_r * 1.5)
                # Collar band
                pygame.draw.ellipse(surface, BLACK,
                                    (cx - collar_w // 2 - 1, neck_y - 2,
                                     collar_w + 2, int(7 * s) + 2))
                pygame.draw.ellipse(surface, ADULT_COLLAR_COLOR,
                                    (cx - collar_w // 2, neck_y - 1,
                                     collar_w, int(7 * s)))
                # Bone tag
                tag_x = cx
                tag_y = neck_y + int(8 * s)
                bone_w = int(8 * s)
                bone_h = int(4 * s)
                # Bone shape: rect + circles on ends
                pygame.draw.rect(surface, BLACK,
                                 (tag_x - bone_w // 2 - 1, tag_y - bone_h // 2 - 1,
                                  bone_w + 2, bone_h + 2), border_radius=2)
                pygame.draw.rect(surface, BONE_TAG_COLOR,
                                 (tag_x - bone_w // 2, tag_y - bone_h // 2,
                                  bone_w, bone_h), border_radius=2)
                br = int(3 * s)
                for dx in [-bone_w // 2, bone_w // 2]:
                    pygame.draw.circle(surface, BLACK, (tag_x + dx, tag_y), br + 1)
                    pygame.draw.circle(surface, BONE_TAG_COLOR, (tag_x + dx, tag_y), br)

    # ---- Designer accessories (from pet customization) ----

    def _draw_designer_accessories(self, surface, pet, head_x, head_cy, head_r,
                                    cx, body_top, s, body_poly):
        """Draw custom appearance accessories from the pet designer."""
        appearance = getattr(pet, 'appearance', None)
        if not appearance:
            return

        eye_y = head_cy + int(head_r * KAWAII_EYE_Y_RATIO) - int(head_r * 0.3)
        neck_y = int(body_top + 4 * s)

        # Pattern overlay on body
        pattern = appearance.get("pattern")
        if pattern and pattern != "solid" and appearance.get("pattern_color"):
            self._draw_pattern(surface, pattern, appearance["pattern_color"],
                               body_poly, cx, body_top, s)

        # Scarf (between body and face)
        scarf = appearance.get("scarf")
        if scarf:
            self._draw_scarf(surface, scarf, cx, neck_y, s)

        # Collar (designer collar, below scarf)
        collar = appearance.get("collar")
        if collar:
            self._draw_collar(surface, collar, cx, neck_y + int(6 * s), s, head_r)

        # Glasses (over eyes)
        glasses = appearance.get("glasses")
        if glasses:
            self._draw_glasses(surface, glasses, head_x, eye_y, s)

        # Hat (on top of head)
        hat = appearance.get("hat")
        if hat:
            self._draw_hat(surface, hat, head_x, head_cy, head_r, s)

        # Special effects (sparkles, freckles, etc.)
        special = appearance.get("special")
        if special:
            self._draw_special(surface, special, head_x, head_cy, head_r, s, eye_y)

    def _draw_hat(self, surface, hat_type, head_x, head_cy, head_r, s):
        """Draw a hat on top of the pet's head."""
        top_y = head_cy - head_r

        if hat_type == "beret":
            pygame.draw.ellipse(surface, BLACK,
                                (head_x - int(16 * s) - 1, top_y - int(10 * s) - 1,
                                 int(32 * s) + 2, int(14 * s) + 2))
            pygame.draw.ellipse(surface, (180, 50, 50),
                                (head_x - int(16 * s), top_y - int(10 * s),
                                 int(32 * s), int(14 * s)))
            # Nub on top
            pygame.draw.circle(surface, (180, 50, 50),
                               (head_x, top_y - int(10 * s)), int(3 * s))

        elif hat_type == "crown":
            cw = int(22 * s)
            ch = int(14 * s)
            base_y = top_y - int(4 * s)
            # Base band
            pygame.draw.rect(surface, BLACK,
                             (head_x - cw // 2 - 1, base_y - 1, cw + 2, int(6 * s) + 2),
                             border_radius=2)
            pygame.draw.rect(surface, (255, 210, 80),
                             (head_x - cw // 2, base_y, cw, int(6 * s)),
                             border_radius=2)
            # Crown points
            for dx in [-cw // 3, 0, cw // 3]:
                tip_y = base_y - int(8 * s)
                pygame.draw.polygon(surface, (255, 210, 80), [
                    (head_x + dx - int(3 * s), base_y),
                    (head_x + dx + int(3 * s), base_y),
                    (head_x + dx, tip_y),
                ])
            # Gem on front
            pygame.draw.circle(surface, (220, 60, 60),
                               (head_x, base_y + int(3 * s)), max(1, int(2 * s)))

        elif hat_type == "tophat":
            tw = int(18 * s)
            brim_w = int(28 * s)
            th = int(18 * s)
            base_y = top_y - int(2 * s)
            # Brim
            pygame.draw.ellipse(surface, BLACK,
                                (head_x - brim_w // 2 - 1, base_y - 1,
                                 brim_w + 2, int(6 * s) + 2))
            pygame.draw.ellipse(surface, (30, 30, 40),
                                (head_x - brim_w // 2, base_y, brim_w, int(6 * s)))
            # Cylinder
            pygame.draw.rect(surface, BLACK,
                             (head_x - tw // 2 - 1, base_y - th - 1, tw + 2, th + 2),
                             border_radius=2)
            pygame.draw.rect(surface, (30, 30, 40),
                             (head_x - tw // 2, base_y - th, tw, th), border_radius=2)
            # Band
            pygame.draw.rect(surface, (180, 60, 60),
                             (head_x - tw // 2, base_y - int(5 * s), tw, int(3 * s)))

        elif hat_type == "flower":
            fx = head_x + int(10 * s)
            fy = top_y - int(4 * s)
            # Petals
            for angle in range(0, 360, 72):
                px = fx + int(math.cos(math.radians(angle)) * 5 * s)
                py = fy + int(math.sin(math.radians(angle)) * 5 * s)
                pygame.draw.circle(surface, (255, 180, 200), (int(px), int(py)),
                                   int(4 * s))
            # Center
            pygame.draw.circle(surface, (255, 220, 80), (fx, fy), int(3 * s))

        elif hat_type == "bow":
            bx = head_x
            by = top_y - int(3 * s)
            br = int(7 * s)
            pygame.draw.circle(surface, BLACK, (bx - br, by), br + 1)
            pygame.draw.circle(surface, BLACK, (bx + br, by), br + 1)
            pygame.draw.circle(surface, (255, 100, 120), (bx - br, by), br)
            pygame.draw.circle(surface, (255, 100, 120), (bx + br, by), br)
            pygame.draw.circle(surface, (220, 80, 100), (bx, by), int(4 * s))

        elif hat_type == "helmet":
            hw = int(head_r * 1.3)
            hh = int(head_r * 0.9)
            hy = top_y - int(4 * s)
            pygame.draw.ellipse(surface, BLACK,
                                (head_x - hw - 1, hy - 1, hw * 2 + 2, hh + 2))
            pygame.draw.ellipse(surface, (160, 170, 180),
                                (head_x - hw, hy, hw * 2, hh))
            # Visor line
            pygame.draw.line(surface, (100, 110, 120),
                             (head_x - hw + int(4 * s), hy + hh - int(4 * s)),
                             (head_x + hw - int(4 * s), hy + hh - int(4 * s)), 2)

        elif hat_type == "propeller":
            # Beanie base
            hw = int(head_r * 1.1)
            hh = int(head_r * 0.5)
            hy = top_y - int(2 * s)
            pygame.draw.ellipse(surface, BLACK,
                                (head_x - hw - 1, hy - 1, hw * 2 + 2, hh + 2))
            pygame.draw.ellipse(surface, (80, 180, 80),
                                (head_x - hw, hy, hw * 2, hh))
            # Propeller
            prop_y = hy - int(2 * s)
            angle = self.time * 8.0
            for i in range(3):
                a = angle + i * math.pi * 2 / 3
                px = head_x + int(math.cos(a) * 10 * s)
                py = prop_y + int(math.sin(a) * 3 * s)
                pygame.draw.line(surface, (255, 80, 80),
                                 (head_x, prop_y), (int(px), int(py)), 2)
            pygame.draw.circle(surface, (60, 60, 60), (head_x, prop_y), int(2 * s))

    def _draw_glasses(self, surface, glasses_type, head_x, eye_y, s):
        """Draw glasses over the pet's eyes."""
        spacing = int(12 * s)
        lens_r = int(7 * s)

        if glasses_type == "round":
            for side in [-1, 1]:
                ex = head_x + side * spacing
                pygame.draw.circle(surface, BLACK, (ex, eye_y), lens_r + 1)
                pygame.draw.circle(surface, (220, 230, 240, 60), (ex, eye_y), lens_r)
                pygame.draw.circle(surface, BLACK, (ex, eye_y), lens_r, 2)
            # Bridge
            pygame.draw.line(surface, BLACK,
                             (head_x - spacing + lens_r, eye_y),
                             (head_x + spacing - lens_r, eye_y), 2)

        elif glasses_type == "cat_eye":
            for side in [-1, 1]:
                ex = head_x + side * spacing
                pts = [
                    (ex - int(8 * s), eye_y + int(3 * s)),
                    (ex - int(6 * s), eye_y - int(5 * s)),
                    (ex + side * int(10 * s), eye_y - int(7 * s)),
                    (ex + int(8 * s), eye_y + int(3 * s)),
                ]
                pygame.draw.polygon(surface, BLACK, pts, 2)
            pygame.draw.line(surface, BLACK,
                             (head_x - spacing + int(8 * s), eye_y),
                             (head_x + spacing - int(8 * s), eye_y), 2)

        elif glasses_type == "sunglasses":
            for side in [-1, 1]:
                ex = head_x + side * spacing
                rect = pygame.Rect(ex - int(9 * s), eye_y - int(5 * s),
                                   int(18 * s), int(10 * s))
                pygame.draw.rect(surface, (20, 20, 30), rect, border_radius=3)
                pygame.draw.rect(surface, BLACK, rect, 2, border_radius=3)
            pygame.draw.line(surface, BLACK,
                             (head_x - spacing + int(9 * s), eye_y),
                             (head_x + spacing - int(9 * s), eye_y), 2)

        elif glasses_type == "monocle":
            ex = head_x + spacing  # right eye
            pygame.draw.circle(surface, BLACK, (ex, eye_y), lens_r, 2)
            # Chain
            pygame.draw.line(surface, (180, 160, 100),
                             (ex, eye_y + lens_r),
                             (ex + int(5 * s), eye_y + int(20 * s)), 1)

    def _draw_scarf(self, surface, scarf_type, cx, neck_y, s):
        """Draw a scarf around the pet's neck."""
        scarf_colors = {
            "red": (220, 60, 60), "blue": (60, 100, 220),
            "rainbow": (220, 100, 180), "gold": (220, 190, 60),
        }
        color = scarf_colors.get(scarf_type, (220, 60, 60))
        sw = int(30 * s)
        sh = int(8 * s)
        # Wrap
        pygame.draw.ellipse(surface, BLACK,
                            (cx - sw - 1, neck_y - 1, sw * 2 + 2, sh + 2))
        pygame.draw.ellipse(surface, color,
                            (cx - sw, neck_y, sw * 2, sh))
        # Dangling ends
        for dx in [-1, 1]:
            end_x = cx + dx * int(6 * s)
            pts = [
                (end_x - int(4 * s), neck_y + sh - int(2 * s)),
                (end_x + int(4 * s), neck_y + sh - int(2 * s)),
                (end_x + dx * int(3 * s), neck_y + sh + int(12 * s)),
            ]
            pygame.draw.polygon(surface, BLACK, _inflate_triangle(pts, 1))
            pygame.draw.polygon(surface, color, pts)

    def _draw_collar(self, surface, collar_type, cx, neck_y, s, head_r):
        """Draw a designer collar."""
        collar_w = int(head_r * 1.3)
        ch = int(5 * s)

        if collar_type == "bell":
            pygame.draw.ellipse(surface, BLACK,
                                (cx - collar_w // 2 - 1, neck_y - 1,
                                 collar_w + 2, ch + 2))
            pygame.draw.ellipse(surface, (220, 60, 60),
                                (cx - collar_w // 2, neck_y, collar_w, ch))
            # Bell
            pygame.draw.circle(surface, BLACK, (cx, neck_y + ch), int(4 * s) + 1)
            pygame.draw.circle(surface, (255, 220, 80), (cx, neck_y + ch), int(4 * s))

        elif collar_type == "bowtie":
            # Small bowtie
            bw = int(8 * s)
            bh = int(5 * s)
            for side in [-1, 1]:
                pts = [
                    (cx, neck_y + ch // 2),
                    (cx + side * bw, neck_y + ch // 2 - bh),
                    (cx + side * bw, neck_y + ch // 2 + bh),
                ]
                pygame.draw.polygon(surface, BLACK, _inflate_triangle(pts, 1))
                pygame.draw.polygon(surface, (60, 60, 180), pts)
            pygame.draw.circle(surface, (40, 40, 140), (cx, neck_y + ch // 2), int(2 * s))

        elif collar_type == "bandana":
            pts = [
                (cx - collar_w // 2, neck_y),
                (cx + collar_w // 2, neck_y),
                (cx, neck_y + int(14 * s)),
            ]
            pygame.draw.polygon(surface, BLACK, _inflate_triangle(pts, 1))
            pygame.draw.polygon(surface, (220, 70, 70), pts)

        elif collar_type == "tag":
            pygame.draw.ellipse(surface, BLACK,
                                (cx - collar_w // 2 - 1, neck_y - 1,
                                 collar_w + 2, ch + 2))
            pygame.draw.ellipse(surface, (100, 70, 50),
                                (cx - collar_w // 2, neck_y, collar_w, ch))
            # Tag
            tag_r = int(4 * s)
            pygame.draw.circle(surface, BLACK, (cx, neck_y + ch + tag_r), tag_r + 1)
            pygame.draw.circle(surface, (200, 200, 220), (cx, neck_y + ch + tag_r), tag_r)

    def _draw_pattern(self, surface, pattern, color, body_poly, cx, body_top, s):
        """Draw spots or stripes pattern overlay on the body."""
        pat_color = tuple(color) if isinstance(color, list) else color
        pat_surf = pygame.Surface((200, 200), pygame.SRCALPHA)

        if pattern == "spots":
            # Random-looking but deterministic spots
            import random as _rng
            rng = _rng.Random(42)
            for _ in range(8):
                sx = rng.randint(20, 180)
                sy = rng.randint(20, 160)
                sr = rng.randint(4, 8)
                pygame.draw.circle(pat_surf, (*pat_color, 100), (sx, sy), sr)

        elif pattern == "stripes":
            for i in range(0, 200, 16):
                pygame.draw.line(pat_surf, (*pat_color, 80),
                                 (0, i), (200, i + 20), 4)

        # Position overlay roughly on body area
        bx = int(cx - 100)
        by = int(body_top - 20)
        surface.blit(pat_surf, (bx, by),
                     special_flags=pygame.BLEND_ALPHA_SDL2 if hasattr(pygame, 'BLEND_ALPHA_SDL2') else 0)

    def _draw_special(self, surface, special_type, head_x, head_cy, head_r, s, eye_y):
        """Draw special effects (sparkle eyes, freckles, star cheeks, rosy cheeks)."""
        if special_type == "sparkle_eyes":
            # Extra sparkle dots around eyes
            spacing = int(12 * s)
            for side in [-1, 1]:
                ex = head_x + side * spacing
                for i in range(4):
                    angle = self.time * 2 + i * math.pi / 2 + side
                    sx = ex + int(math.cos(angle) * 8 * s)
                    sy = eye_y + int(math.sin(angle) * 8 * s)
                    pygame.draw.circle(surface, (255, 255, 200),
                                       (int(sx), int(sy)), max(1, int(1.5 * s)))

        elif special_type == "freckles":
            # 3 dots on each cheek
            for side in [-1, 1]:
                bx = head_x + side * int(14 * s)
                by = eye_y + int(8 * s)
                for dx, dy in [(-2, -1), (1, 1), (3, -2)]:
                    pygame.draw.circle(surface, (180, 130, 80),
                                       (bx + int(dx * s), by + int(dy * s)), max(1, int(s)))

        elif special_type == "star_cheeks":
            for side in [-1, 1]:
                sx = head_x + side * int(16 * s)
                sy = eye_y + int(6 * s)
                _draw_star(surface, sx, sy, int(4 * s), (255, 220, 80), 0)

        elif special_type == "rosy_cheeks":
            for side in [-1, 1]:
                bx = head_x + side * int(16 * s)
                by = eye_y + int(6 * s)
                blush_r = int(6 * s)
                blush_surf = pygame.Surface((blush_r * 2 + 2, blush_r * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(blush_surf, (255, 130, 150, 100),
                                   (blush_r + 1, blush_r + 1), blush_r)
                surface.blit(blush_surf, (bx - blush_r - 1, by - blush_r - 1))
