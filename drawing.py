"""Procedural pet drawing — cat & dog, expressions, animations, evolution tiers."""

import math
import random
import pygame
from settings import (
    PET_CAT, PET_DOG,
    ACTION_IDLE, ACTION_EATING, ACTION_PLAYING,
    ACTION_SLEEPING, ACTION_SICK, ACTION_RUNNING_AWAY,
    CAT_BODY, CAT_BODY_DARK, CAT_BELLY, CAT_STRIPE, CAT_NOSE,
    DOG_BODY, DOG_BODY_DARK, DOG_BELLY, DOG_NOSE, DOG_TONGUE,
    THRIVING_TINT, SCRUFFY_TINT,
    SPARKLE_COLOR, STAR_COLOR, ZZZ_COLOR, SWEAT_COLOR, FOOD_COLOR,
    WHITE, BLACK, PET_CENTER_X, PET_CENTER_Y,
)


def _tint_color(color, amount):
    """Add or subtract brightness from a color."""
    return tuple(max(0, min(255, c + amount)) for c in color)


def _get_pet_colors(pet_type, evolution_tier):
    """Get colors adjusted for evolution tier."""
    tint = 0
    if evolution_tier == "thriving":
        tint = THRIVING_TINT
    elif evolution_tier == "scruffy":
        tint = SCRUFFY_TINT

    if pet_type == PET_CAT:
        return {
            "body": _tint_color(CAT_BODY, tint),
            "body_dark": _tint_color(CAT_BODY_DARK, tint),
            "belly": _tint_color(CAT_BELLY, tint),
            "stripe": _tint_color(CAT_STRIPE, tint),
            "nose": CAT_NOSE,
        }
    else:
        return {
            "body": _tint_color(DOG_BODY, tint),
            "body_dark": _tint_color(DOG_BODY_DARK, tint),
            "belly": _tint_color(DOG_BELLY, tint),
            "nose": DOG_NOSE,
            "tongue": DOG_TONGUE,
        }


class Particles:
    """Simple particle system for effects."""

    def __init__(self):
        self.particles = []

    def emit(self, x, y, color, count=5, speed=40, lifetime=0.8, size=3):
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
            })

    def update(self, dt):
        for p in self.particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["vy"] += 30 * dt  # gravity
            p["life"] -= dt
        self.particles = [p for p in self.particles if p["life"] > 0]

    def draw(self, surface):
        for p in self.particles:
            alpha = p["life"] / p["max_life"]
            size = max(1, int(p["size"] * alpha))
            pygame.draw.circle(surface, p["color"],
                               (int(p["x"]), int(p["y"])), size)


class PetDrawer:
    """Draws the pet procedurally using pygame.draw."""

    def __init__(self):
        self.time = 0.0
        self.particles = Particles()
        self.ear_twitch_timer = 0.0
        self.ear_twitch_offset = 0
        self.zzz_timer = 0.0

    def update(self, dt):
        self.time += dt
        self.particles.update(dt)

        # Random ear twitch
        self.ear_twitch_timer -= dt
        if self.ear_twitch_timer <= 0:
            self.ear_twitch_timer = random.uniform(2.0, 5.0)
            self.ear_twitch_offset = random.choice([-3, 3, -5, 5])
        elif self.ear_twitch_timer < 0.15:
            self.ear_twitch_offset = 0

        # Zzz particles
        self.zzz_timer += dt

    def draw(self, surface, pet):
        """Draw the pet based on its current state."""
        cx = PET_CENTER_X
        cy = PET_CENTER_Y
        colors = _get_pet_colors(pet.pet_type, pet.evolution_tier)

        # Breathing animation
        breath = math.sin(self.time * 2.0) * 3

        # Scale factor for evolution
        scale = 1.0
        if pet.evolution_tier == "thriving":
            scale = 1.1
        elif pet.evolution_tier == "scruffy":
            scale = 0.9

        # Action-specific offsets
        head_offset_y = 0
        body_bounce = 0

        if pet.action == ACTION_EATING:
            # Head bobs down
            head_offset_y = abs(math.sin(self.time * 8)) * 10
            # Food particles
            if random.random() < 0.15:
                self.particles.emit(cx, cy + 20, FOOD_COLOR,
                                    count=2, speed=30, lifetime=0.5, size=3)

        elif pet.action == ACTION_PLAYING:
            # Bouncing
            body_bounce = abs(math.sin(self.time * 6)) * 15
            # Star particles
            if random.random() < 0.1:
                self.particles.emit(
                    cx + random.randint(-30, 30),
                    cy - 20 + random.randint(-20, 10),
                    STAR_COLOR, count=1, speed=25, lifetime=0.6, size=4)

        elif pet.action == ACTION_SLEEPING:
            # Zzz particles
            if self.zzz_timer > 1.0:
                self.zzz_timer = 0.0
                self.particles.emit(cx + 30, cy - 50, ZZZ_COLOR,
                                    count=1, speed=15, lifetime=1.5, size=5)

        # Sick overlay: shaking
        shake_x = 0
        if pet.is_sick and pet.action != ACTION_SLEEPING:
            shake_x = math.sin(self.time * 20) * 3
            # Sweat drops
            if random.random() < 0.08:
                self.particles.emit(cx + random.choice([-20, 20]),
                                    cy - 50, SWEAT_COLOR,
                                    count=1, speed=20, lifetime=0.6, size=3)

        # Runaway: move off screen
        runaway_offset_x = 0
        if pet.action == ACTION_RUNNING_AWAY:
            runaway_offset_x = pet.runaway_progress * 500

        final_x = cx + shake_x + runaway_offset_x
        final_y = cy - body_bounce

        # Draw the pet
        if pet.action == ACTION_SLEEPING:
            self._draw_sleeping(surface, pet, colors, final_x, final_y, scale, breath)
        else:
            self._draw_standing(surface, pet, colors, final_x, final_y,
                                scale, breath, head_offset_y)

        # Thriving sparkles
        if pet.evolution_tier == "thriving" and pet.action not in (ACTION_SLEEPING, ACTION_RUNNING_AWAY):
            if random.random() < 0.05:
                self.particles.emit(
                    final_x + random.randint(-35, 35),
                    final_y - 30 + random.randint(-30, 20),
                    SPARKLE_COLOR, count=1, speed=15, lifetime=0.8, size=3)

        # Sick green tint overlay
        if pet.is_sick and pet.action != ACTION_RUNNING_AWAY:
            tint_surf = pygame.Surface((100, 120), pygame.SRCALPHA)
            tint_surf.fill((0, 180, 0, 30))
            surface.blit(tint_surf, (final_x - 50, final_y - 70))

        # Draw particles
        self.particles.draw(surface)

    def _draw_standing(self, surface, pet, colors, cx, cy, scale, breath, head_bob):
        """Draw pet standing (idle, eating, playing, sick, running away)."""
        s = scale

        # Body (oval)
        body_w = int(50 * s)
        body_h = int(40 * s)
        body_rect = pygame.Rect(cx - body_w, cy - body_h // 2 + breath,
                                body_w * 2, body_h)
        pygame.draw.ellipse(surface, colors["body"], body_rect)

        # Belly
        belly_rect = pygame.Rect(cx - int(30 * s), cy - int(10 * s) + breath,
                                 int(60 * s), int(30 * s))
        pygame.draw.ellipse(surface, colors["belly"], belly_rect)

        # Legs
        leg_y = cy + body_h // 2 + breath - 5
        for lx in [cx - int(25 * s), cx - int(10 * s),
                    cx + int(10 * s), cx + int(25 * s)]:
            pygame.draw.rect(surface, colors["body_dark"],
                             (lx - 5, leg_y, 10, int(25 * s)))
            # Paws
            pygame.draw.ellipse(surface, colors["body_dark"],
                                (lx - 7, leg_y + int(20 * s), 14, 10))

        # Head
        head_y = cy - int(45 * s) + breath + head_bob
        head_r = int(30 * s)
        pygame.draw.circle(surface, colors["body"], (cx, head_y), head_r)

        if pet.pet_type == PET_CAT:
            self._draw_cat_features(surface, pet, colors, cx, head_y, s)
        else:
            self._draw_dog_features(surface, pet, colors, cx, head_y, s)

        # Tail
        self._draw_tail(surface, pet, colors, cx, cy, s, breath)

    def _draw_sleeping(self, surface, pet, colors, cx, cy, scale, breath):
        """Draw pet curled up sleeping."""
        s = scale

        # Curled body (wider, lower)
        body_w = int(55 * s)
        body_h = int(30 * s)
        body_y = cy + 10 + breath * 0.5
        body_rect = pygame.Rect(cx - body_w, body_y - body_h // 2,
                                body_w * 2, body_h)
        pygame.draw.ellipse(surface, colors["body"], body_rect)
        # Belly visible
        belly_rect = pygame.Rect(cx - int(35 * s), body_y - int(5 * s),
                                 int(70 * s), int(20 * s))
        pygame.draw.ellipse(surface, colors["belly"], belly_rect)

        # Head resting on body
        head_r = int(25 * s)
        head_x = cx - int(25 * s)
        head_y = body_y - int(15 * s)
        pygame.draw.circle(surface, colors["body"], (head_x, head_y), head_r)

        # Closed eyes (curved lines)
        eye_y = head_y - 2
        for ex in [head_x - 8, head_x + 8]:
            pygame.draw.arc(surface, BLACK,
                            (ex - 5, eye_y - 3, 10, 8),
                            0, math.pi, 2)

        # Tail curled around body
        tail_points = []
        for i in range(20):
            t = i / 19
            angle = t * math.pi * 1.2 + math.pi * 0.8
            r = int((35 + t * 15) * s)
            tx = cx + int(math.cos(angle) * r)
            ty = body_y + int(math.sin(angle) * r * 0.5)
            tail_points.append((tx, ty))
        if len(tail_points) > 2:
            pygame.draw.lines(surface, colors["body_dark"], False, tail_points, 5)

    def _draw_cat_features(self, surface, pet, colors, cx, head_y, s):
        """Draw cat-specific features: ears, whiskers, eyes, nose."""
        # Triangular ears
        ear_twitch = self.ear_twitch_offset
        for side in [-1, 1]:
            ear_x = cx + side * int(20 * s)
            ear_tip_y = head_y - int(35 * s) + (ear_twitch if side == 1 else 0)
            ear_points = [
                (ear_x - side * int(5 * s), head_y - int(18 * s)),
                (ear_x + side * int(8 * s), ear_tip_y),
                (ear_x + side * int(18 * s), head_y - int(15 * s)),
            ]
            pygame.draw.polygon(surface, colors["body"], ear_points)
            # Inner ear
            inner = [
                (ear_x - side * int(2 * s), head_y - int(17 * s)),
                (ear_x + side * int(8 * s), ear_tip_y + 4),
                (ear_x + side * int(14 * s), head_y - int(14 * s)),
            ]
            pygame.draw.polygon(surface, (230, 180, 180), inner)

        # Eyes
        is_sad = pet.is_sick or pet.action == ACTION_RUNNING_AWAY
        eye_y = head_y - int(5 * s)
        for side in [-1, 1]:
            ex = cx + side * int(10 * s)
            # White of eye
            pygame.draw.ellipse(surface, WHITE,
                                (ex - 7, eye_y - 6, 14, 13))
            # Pupil - vertical slit for cat
            pupil_w = 4 if not is_sad else 3
            pygame.draw.ellipse(surface, BLACK,
                                (ex - pupil_w // 2, eye_y - 5, pupil_w, 11))
            # Sad eyes: eyebrows angled down
            if is_sad:
                brow_y = eye_y - 10
                pygame.draw.line(surface, colors["body_dark"],
                                 (ex - 6, brow_y - side * 2),
                                 (ex + 6, brow_y + side * 2), 2)

        # Nose
        nose_y = head_y + int(5 * s)
        pygame.draw.polygon(surface, colors["nose"], [
            (cx, nose_y + 4), (cx - 4, nose_y), (cx + 4, nose_y)
        ])

        # Mouth
        if is_sad:
            # Frown
            pygame.draw.arc(surface, BLACK,
                            (cx - 6, nose_y + 4, 12, 8),
                            0, math.pi, 1)
        else:
            # Smile
            pygame.draw.arc(surface, BLACK,
                            (cx - 6, nose_y + 2, 12, 8),
                            math.pi, 2 * math.pi, 1)

        # Whiskers
        whisker_y = head_y + int(3 * s)
        for side in [-1, 1]:
            for dy in [-4, 0, 4]:
                start_x = cx + side * int(12 * s)
                end_x = cx + side * int(35 * s)
                pygame.draw.line(surface, colors.get("stripe", colors["body_dark"]),
                                 (start_x, whisker_y + dy),
                                 (end_x, whisker_y + dy + dy), 1)

    def _draw_dog_features(self, surface, pet, colors, cx, head_y, s):
        """Draw dog-specific features: floppy ears, eyes, nose, tongue."""
        # Floppy ears
        ear_twitch = self.ear_twitch_offset
        for side in [-1, 1]:
            ear_x = cx + side * int(22 * s)
            ear_top_y = head_y - int(15 * s)
            ear_w = int(15 * s)
            ear_h = int(25 * s) + (ear_twitch if side == 1 else 0)
            ear_rect = pygame.Rect(ear_x - ear_w // 2, ear_top_y,
                                   ear_w, ear_h)
            pygame.draw.ellipse(surface, colors["body_dark"], ear_rect)

        # Eyes
        is_sad = pet.is_sick or pet.action == ACTION_RUNNING_AWAY
        eye_y = head_y - int(5 * s)
        for side in [-1, 1]:
            ex = cx + side * int(10 * s)
            pygame.draw.ellipse(surface, WHITE,
                                (ex - 7, eye_y - 6, 14, 13))
            # Round pupils for dog
            pygame.draw.circle(surface, BLACK, (ex, eye_y), 5)
            # Highlight
            pygame.draw.circle(surface, WHITE, (ex + 2, eye_y - 2), 2)
            if is_sad:
                brow_y = eye_y - 10
                pygame.draw.line(surface, colors["body_dark"],
                                 (ex - 6, brow_y - side * 2),
                                 (ex + 6, brow_y + side * 2), 2)

        # Nose
        nose_y = head_y + int(6 * s)
        pygame.draw.ellipse(surface, colors["nose"],
                            (cx - 5, nose_y - 3, 10, 7))

        # Mouth & tongue
        if is_sad:
            pygame.draw.arc(surface, BLACK,
                            (cx - 8, nose_y + 4, 16, 10),
                            0, math.pi, 1)
        else:
            pygame.draw.arc(surface, BLACK,
                            (cx - 8, nose_y + 2, 16, 10),
                            math.pi, 2 * math.pi, 1)
            # Tongue when happy
            if pet.happiness > 50:
                pygame.draw.ellipse(surface, colors.get("tongue", DOG_TONGUE),
                                    (cx - 4, nose_y + 8, 8, 12))

    def _draw_tail(self, surface, pet, colors, cx, cy, s, breath):
        """Draw tail with animation."""
        tail_base_x = cx + int(40 * s)
        tail_base_y = cy - int(10 * s) + breath

        if pet.pet_type == PET_CAT:
            # Curved wavy tail
            wag_speed = 3.0
            if pet.action == ACTION_PLAYING:
                wag_speed = 8.0
            points = []
            for i in range(15):
                t = i / 14
                tx = tail_base_x + t * int(30 * s)
                ty = (tail_base_y - t * int(40 * s)
                      + math.sin(self.time * wag_speed + t * 3) * 8 * (1 - t * 0.5))
                points.append((int(tx), int(ty)))
            if len(points) > 2:
                pygame.draw.lines(surface, colors["body_dark"], False, points, 4)
        else:
            # Dog tail - wagging
            wag_speed = 4.0
            if pet.action == ACTION_PLAYING:
                wag_speed = 12.0
            wag = math.sin(self.time * wag_speed) * 15
            tail_end_x = tail_base_x + int(20 * s)
            tail_end_y = tail_base_y - int(35 * s) + wag
            pygame.draw.line(surface, colors["body_dark"],
                             (tail_base_x, tail_base_y),
                             (tail_end_x, tail_end_y), 5)
            # Tail tip
            pygame.draw.circle(surface, colors["body_dark"],
                               (tail_end_x, tail_end_y), 6)
