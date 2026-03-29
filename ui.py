"""UI elements — stat bars, buttons, backgrounds, day/night sky, menus."""

import math
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    HUD_HEIGHT, HUD_ROW1_Y, HUD_ROW2_Y, HUD_BAR_W, HUD_BAR_H,
    HUD_ICON_SIZE, HUD_XP_Y, HUD_XP_H,
    BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_SPACING, BUTTON_COUNT,
    BUTTON_WIDTH_COMPACT, BUTTON_SPACING_COMPACT,
    GROUND_Y, PET_CENTER_X,
    COLOR_HUNGER, COLOR_HAPPINESS, COLOR_ENERGY, COLOR_CLEANLINESS,
    COLOR_STAT_BG, COLOR_STAT_BORDER,
    COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_BUTTON_TEXT,
    COLOR_TITLE, COLOR_SUBTITLE, COLOR_MOOD_TEXT, COLOR_DAY_TEXT,
    XP_BAR_COLOR, XP_BAR_BG,
    XP_LEVEL_COLOR, STREAK_ICON_COLOR,
    SKY_DAY, SKY_SUNSET, SKY_NIGHT, SKY_DAWN,
    GRASS_GREEN, GRASS_DARK,
    WHITE, BLACK, DARK_GRAY, LIGHT_GRAY,
    STAT_MAX,
    DAY_PHASE_LENGTH, DAY_LENGTH,
    GRASS_SWAY_SPEED_BACK, GRASS_SWAY_SPEED_FRONT,
    STAR_COUNT, STAR_TWINKLE_MIN_SPEED, STAR_TWINKLE_MAX_SPEED,
    POOP_COLOR, POOP_COLOR_DARK,
    OUTLINE_WIDTH,
    SICK_TIMER_LIMIT,
    GROWTH_BABY, GROWTH_KID, GROWTH_ADULT,
    BADGE_RANKS,
    WARDROBE_HINT_COLOR, WARDROBE_HINT_BG, WARDROBE_HINT_BORDER,
    WARDROBE_HINT_Y, WARDROBE_HINT_DURATION,
)


def _lerp_color(c1, c2, t):
    """Linearly interpolate between two colors."""
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def _draw_gradient(surface, color_top, color_bottom, rect):
    """Draw a vertical gradient using ~20 horizontal bands."""
    x, y, w, h = rect
    bands = 20
    band_h = max(1, h // bands)
    for i in range(bands + 1):
        t = i / bands
        color = _lerp_color(color_top, color_bottom, t)
        by = y + int(t * h)
        pygame.draw.rect(surface, color, (x, by, w, band_h + 1))


def _draw_icon_hunger(surface, cx, cy, color):
    """Drumstick icon ~12px."""
    pygame.draw.circle(surface, color, (cx - 1, cy - 1), 4)
    pygame.draw.line(surface, color, (cx + 2, cy + 1), (cx + 5, cy + 4), 2)


def _draw_icon_happy(surface, cx, cy, color):
    """Heart icon ~12px."""
    pygame.draw.circle(surface, color, (cx - 2, cy - 1), 3)
    pygame.draw.circle(surface, color, (cx + 2, cy - 1), 3)
    pygame.draw.polygon(surface, color, [(cx - 4, cy), (cx + 4, cy), (cx, cy + 4)])


def _draw_icon_energy(surface, cx, cy, color):
    """Lightning bolt ~12px."""
    pygame.draw.polygon(surface, color, [
        (cx + 2, cy - 5), (cx - 1, cy - 1), (cx + 1, cy - 1),
        (cx - 2, cy + 5), (cx + 1, cy + 1), (cx - 1, cy + 1),
    ])


def _draw_icon_clean(surface, cx, cy, color):
    """Water droplet ~12px."""
    pygame.draw.circle(surface, color, (cx, cy + 1), 4)
    pygame.draw.polygon(surface, color, [(cx - 3, cy - 1), (cx + 3, cy - 1), (cx, cy - 5)])


def _draw_outline_pet(surface, cx, cy, pet_type, scale, time_val, ow=2):
    """Draw a full kawaii-style outlined pet at any position/size.

    Used by menu and pet select screens. Draws: outline body+head merged
    silhouette, paw bumps, ears, eyes with highlight, nose, mouth, whiskers
    (cat only), blush circles, shadow ellipse, floating heart.
    """
    s = scale
    bounce = math.sin(time_val * 2.5) * 5

    # Colors
    if pet_type == "cat":
        body_color = (230, 160, 60)
        ear_inner = (80, 60, 30)
        nose_color = (230, 130, 130)
    else:
        body_color = (200, 160, 80)
        ear_inner = (150, 110, 50)
        nose_color = (60, 40, 30)

    # Dimensions
    head_r = int(22 * s)
    body_w = int(28 * s)
    body_h = int(20 * s)
    paw_r = int(4 * s)
    paw_spacing = int(10 * s)

    head_cy = cy - int(20 * s) + bounce
    body_cy = cy + int(2 * s) + bounce
    body_bottom = body_cy + body_h // 2

    # Shadow ellipse on ground
    shadow_surf = pygame.Surface((int(60 * s), int(10 * s)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 40),
                        (0, 0, int(60 * s), int(10 * s)))
    surface.blit(shadow_surf,
                 (cx - int(30 * s), cy + int(14 * s) + bounce))

    # === OUTLINE PASS (BLACK, inflated) ===
    # Body outline
    pygame.draw.ellipse(surface, BLACK,
                        (cx - body_w - ow, body_cy - body_h // 2 - ow,
                         (body_w + ow) * 2, body_h + ow * 2))
    # Head outline
    pygame.draw.circle(surface, BLACK, (cx, int(head_cy)), head_r + ow)
    # Paw outlines
    paw_y = body_bottom + int(paw_r * 0.3)
    for side in [-1, 1]:
        pygame.draw.circle(surface, BLACK,
                           (cx + side * paw_spacing, int(paw_y)), paw_r + ow)

    # Ear outlines
    if pet_type == "cat":
        for side in [-1, 1]:
            ear_pts = [
                (cx + side * int(8 * s), int(head_cy) - head_r + int(5 * s)),
                (cx + side * int(2 * s), int(head_cy) - head_r - int(14 * s)),
                (cx + side * int(16 * s), int(head_cy) - head_r + int(6 * s)),
            ]
            ecx = sum(p[0] for p in ear_pts) / 3
            ecy = sum(p[1] for p in ear_pts) / 3
            inflated = []
            for px, py in ear_pts:
                dx, dy = px - ecx, py - ecy
                d = max(0.01, math.hypot(dx, dy))
                inflated.append((px + dx / d * ow, py + dy / d * ow))
            pygame.draw.polygon(surface, BLACK, inflated)
    else:
        for side in [-1, 1]:
            ear_x = cx + side * int(16 * s)
            pygame.draw.ellipse(surface, BLACK,
                                (ear_x - int(7 * s) - ow,
                                 int(head_cy) - int(8 * s) - ow,
                                 int(14 * s) + ow * 2, int(24 * s) + ow * 2))

    # === FILL PASS (body color) ===
    # Body fill
    pygame.draw.ellipse(surface, body_color,
                        (cx - body_w, body_cy - body_h // 2,
                         body_w * 2, body_h))
    # Head fill
    pygame.draw.circle(surface, body_color, (cx, int(head_cy)), head_r)
    # Paw fills
    for side in [-1, 1]:
        pygame.draw.circle(surface, body_color,
                           (cx + side * paw_spacing, int(paw_y)), paw_r)
    # Fill gap between body and paws
    gap_rect = pygame.Rect(cx - body_w, int(body_bottom - paw_r),
                           body_w * 2, int(paw_r + 2))
    pygame.draw.rect(surface, body_color, gap_rect)

    # Ear fills
    if pet_type == "cat":
        for side in [-1, 1]:
            ear_pts = [
                (cx + side * int(8 * s), int(head_cy) - head_r + int(5 * s)),
                (cx + side * int(2 * s), int(head_cy) - head_r - int(14 * s)),
                (cx + side * int(16 * s), int(head_cy) - head_r + int(6 * s)),
            ]
            pygame.draw.polygon(surface, body_color, ear_pts)
            inner = [
                (cx + side * int(9 * s), int(head_cy) - head_r + int(6 * s)),
                (cx + side * int(3 * s), int(head_cy) - head_r - int(10 * s)),
                (cx + side * int(14 * s), int(head_cy) - head_r + int(7 * s)),
            ]
            pygame.draw.polygon(surface, ear_inner, inner)
    else:
        for side in [-1, 1]:
            ear_x = cx + side * int(16 * s)
            pygame.draw.ellipse(surface, body_color,
                                (ear_x - int(7 * s), int(head_cy) - int(8 * s),
                                 int(14 * s), int(24 * s)))
            pygame.draw.ellipse(surface, ear_inner,
                                (ear_x - int(5 * s), int(head_cy) - int(5 * s),
                                 int(10 * s), int(17 * s)))

    # === FACIAL FEATURES ===
    eye_y = int(head_cy) + int(head_r * 0.15)

    # Eyes (black circles with white highlight)
    for side in [-1, 1]:
        ex = cx + side * int(8 * s)
        er = int(4 * s)
        pygame.draw.circle(surface, BLACK, (ex, eye_y), er)
        # White highlight
        hl_r = max(1, int(2 * s))
        pygame.draw.circle(surface, WHITE, (ex + int(1.5 * s), eye_y - int(1.5 * s)), hl_r)

    # Nose
    nose_y = eye_y + int(8 * s)
    if pet_type == "cat":
        pygame.draw.polygon(surface, nose_color, [
            (cx, nose_y + int(3 * s)),
            (cx - int(3 * s), nose_y),
            (cx + int(3 * s), nose_y),
        ])
    else:
        pygame.draw.ellipse(surface, nose_color,
                            (cx - int(5 * s), nose_y - int(3 * s),
                             int(10 * s), int(6 * s)))

    # Mouth
    mouth_y = nose_y + int(4 * s)
    if pet_type == "cat":
        # Cat "w" mouth
        w = int(4 * s)
        h = int(3 * s)
        for side in [-1, 1]:
            mx = cx + side * int(3 * s)
            pygame.draw.arc(surface, BLACK,
                            (mx - w // 2, mouth_y - h // 2, w, h),
                            math.pi, 2 * math.pi, 1)
    else:
        w = int(8 * s)
        h = int(4 * s)
        pygame.draw.arc(surface, BLACK,
                        (cx - w // 2, mouth_y - h // 3, w, h),
                        math.pi, 2 * math.pi, 1)

    # Whiskers (cat only)
    if pet_type == "cat":
        whisker_y = eye_y + int(6 * s)
        whisker_len = int(16 * s)
        for side in [-1, 1]:
            for i in range(2):
                dy = (i - 0.5) * int(4 * s)
                start_x = cx + side * int(10 * s)
                end_x = cx + side * (int(10 * s) + whisker_len)
                pygame.draw.line(surface, BLACK,
                                 (start_x, int(whisker_y + dy)),
                                 (end_x, int(whisker_y + dy + dy * 0.5)), 1)

    # Blush circles
    blush_r = int(5 * s)
    blush_surf = pygame.Surface((blush_r * 2 + 2, blush_r * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(blush_surf, (255, 130, 150, 70),
                       (blush_r + 1, blush_r + 1), blush_r)
    for side in [-1, 1]:
        bx = cx + side * int(14 * s)
        by = eye_y + int(5 * s)
        surface.blit(blush_surf, (bx - blush_r - 1, by - blush_r - 1))

    # Floating heart above pet
    heart_bob = math.sin(time_val * 3) * 3
    heart_y = int(head_cy) - head_r - int(18 * s) + heart_bob
    hr = max(2, int(3 * s))
    pygame.draw.circle(surface, (255, 150, 180),
                       (cx - int(hr * 0.5), heart_y - int(hr * 0.3)), hr)
    pygame.draw.circle(surface, (255, 150, 180),
                       (cx + int(hr * 0.5), heart_y - int(hr * 0.3)), hr)
    pygame.draw.polygon(surface, (255, 150, 180), [
        (cx - int(hr * 1.2), heart_y),
        (cx + int(hr * 1.2), heart_y),
        (cx, heart_y + int(hr * 1.5)),
    ])


def _draw_sad_pet(surface, cx, cy, pet_type, scale, ow=2):
    """Draw a sad outlined pet silhouette for the ran-away screen.

    Drooping head, sad eyes (X or downturned), frown mouth, no heart/blush.
    """
    s = scale
    if pet_type == "cat":
        body_color = (180, 130, 60)
        ear_inner = (80, 60, 30)
    else:
        body_color = (160, 130, 70)
        ear_inner = (120, 90, 45)

    head_r = int(22 * s)
    body_w = int(28 * s)
    body_h = int(20 * s)
    paw_r = int(4 * s)
    paw_spacing = int(10 * s)

    # Head droops lower than normal
    head_cy = cy - int(14 * s)
    body_cy = cy + int(2 * s)
    body_bottom = body_cy + body_h // 2

    # Shadow
    shadow_surf = pygame.Surface((int(60 * s), int(10 * s)), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 30),
                        (0, 0, int(60 * s), int(10 * s)))
    surface.blit(shadow_surf, (cx - int(30 * s), cy + int(14 * s)))

    # === OUTLINE PASS ===
    pygame.draw.ellipse(surface, BLACK,
                        (cx - body_w - ow, body_cy - body_h // 2 - ow,
                         (body_w + ow) * 2, body_h + ow * 2))
    pygame.draw.circle(surface, BLACK, (cx, head_cy), head_r + ow)
    paw_y = body_bottom + int(paw_r * 0.3)
    for side in [-1, 1]:
        pygame.draw.circle(surface, BLACK,
                           (cx + side * paw_spacing, paw_y), paw_r + ow)

    # Ear outlines
    if pet_type == "cat":
        for side in [-1, 1]:
            ear_pts = [
                (cx + side * int(8 * s), head_cy - head_r + int(5 * s)),
                (cx + side * int(2 * s), head_cy - head_r - int(10 * s)),
                (cx + side * int(16 * s), head_cy - head_r + int(6 * s)),
            ]
            ecx = sum(p[0] for p in ear_pts) / 3
            ecy = sum(p[1] for p in ear_pts) / 3
            inflated = []
            for px, py in ear_pts:
                dx, dy = px - ecx, py - ecy
                d = max(0.01, math.hypot(dx, dy))
                inflated.append((px + dx / d * ow, py + dy / d * ow))
            pygame.draw.polygon(surface, BLACK, inflated)
    else:
        for side in [-1, 1]:
            ear_x = cx + side * int(16 * s)
            # Ears droop more
            pygame.draw.ellipse(surface, BLACK,
                                (ear_x - int(7 * s) - ow,
                                 head_cy - int(4 * s) - ow,
                                 int(14 * s) + ow * 2, int(26 * s) + ow * 2))

    # === FILL PASS ===
    pygame.draw.ellipse(surface, body_color,
                        (cx - body_w, body_cy - body_h // 2,
                         body_w * 2, body_h))
    pygame.draw.circle(surface, body_color, (cx, head_cy), head_r)
    for side in [-1, 1]:
        pygame.draw.circle(surface, body_color,
                           (cx + side * paw_spacing, paw_y), paw_r)
    gap_rect = pygame.Rect(cx - body_w, body_bottom - paw_r,
                           body_w * 2, paw_r + 2)
    pygame.draw.rect(surface, body_color, gap_rect)

    # Ear fills
    if pet_type == "cat":
        for side in [-1, 1]:
            ear_pts = [
                (cx + side * int(8 * s), head_cy - head_r + int(5 * s)),
                (cx + side * int(2 * s), head_cy - head_r - int(10 * s)),
                (cx + side * int(16 * s), head_cy - head_r + int(6 * s)),
            ]
            pygame.draw.polygon(surface, body_color, ear_pts)
            inner = [
                (cx + side * int(9 * s), head_cy - head_r + int(6 * s)),
                (cx + side * int(3 * s), head_cy - head_r - int(7 * s)),
                (cx + side * int(14 * s), head_cy - head_r + int(7 * s)),
            ]
            pygame.draw.polygon(surface, ear_inner, inner)
    else:
        for side in [-1, 1]:
            ear_x = cx + side * int(16 * s)
            pygame.draw.ellipse(surface, body_color,
                                (ear_x - int(7 * s), head_cy - int(4 * s),
                                 int(14 * s), int(26 * s)))
            pygame.draw.ellipse(surface, ear_inner,
                                (ear_x - int(5 * s), head_cy - int(1 * s),
                                 int(10 * s), int(19 * s)))

    # === SAD FACE ===
    eye_y = head_cy + int(head_r * 0.15)

    # Sad X eyes
    for side in [-1, 1]:
        ex = cx + side * int(8 * s)
        sz = int(4 * s)
        pygame.draw.line(surface, BLACK,
                         (ex - sz, eye_y - sz), (ex + sz, eye_y + sz), 2)
        pygame.draw.line(surface, BLACK,
                         (ex + sz, eye_y - sz), (ex - sz, eye_y + sz), 2)

    # Tear drop on one side
    tear_y = eye_y + int(6 * s)
    pygame.draw.circle(surface, (150, 200, 255),
                       (cx + int(10 * s), tear_y), int(3 * s))

    # Frown mouth
    mouth_y = eye_y + int(12 * s)
    w = int(8 * s)
    h = int(4 * s)
    pygame.draw.arc(surface, BLACK,
                    (cx - w // 2, mouth_y, w, h),
                    0, math.pi, 2)


class Button:
    def __init__(self, x, y, width, height, text, shortcut_label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.shortcut_label = shortcut_label
        self.hovered = False
        # Batch 4B: interaction polish
        self.hover_progress = 0.0   # 0→1 smooth
        self.press_progress = 0.0   # 1→0 decay after click

    def update(self, mouse_pos, dt=1 / 60):
        self.hovered = self.rect.collidepoint(mouse_pos)
        # Smooth hover transition
        target = 1.0 if self.hovered else 0.0
        speed = 8.0  # lerp speed
        self.hover_progress += (target - self.hover_progress) * min(1.0, speed * dt)
        # Press decay
        if self.press_progress > 0:
            self.press_progress = max(0.0, self.press_progress - dt * 4.0)

    def click(self):
        """Call when button is pressed."""
        self.press_progress = 1.0

    def draw(self, surface, font, small_font=None):
        hp = self.hover_progress
        pp = self.press_progress

        # Interpolated color
        color = _lerp_color(COLOR_BUTTON, COLOR_BUTTON_HOVER, hp)

        # Scale inflate on hover (slight)
        inflate = int(hp * 4) - int(pp * 3)
        draw_rect = self.rect.inflate(inflate, inflate)

        # Drop shadow when hovered
        if hp > 0.1:
            shadow_rect = draw_rect.move(2, 3)
            shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(shadow_surf, (0, 0, 0, int(40 * hp)),
                             (0, 0, shadow_rect.width, shadow_rect.height),
                             border_radius=8)
            surface.blit(shadow_surf, shadow_rect.topleft)

        # Main button
        pygame.draw.rect(surface, color, draw_rect, border_radius=8)

        # Top-edge highlight for 3D feel
        hl_rect = pygame.Rect(draw_rect.x + 4, draw_rect.y + 2,
                               draw_rect.width - 8, 3)
        hl_surf = pygame.Surface((hl_rect.width, hl_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(hl_surf, (255, 255, 255, int(30 + 25 * hp)),
                         (0, 0, hl_rect.width, hl_rect.height), border_radius=2)
        surface.blit(hl_surf, hl_rect.topleft)

        # Border
        pygame.draw.rect(surface, LIGHT_GRAY, draw_rect, 2, border_radius=8)

        text_surf = font.render(self.text, True, COLOR_BUTTON_TEXT)
        text_rect = text_surf.get_rect(center=(draw_rect.centerx,
                                                draw_rect.centery - (4 if self.shortcut_label else 0)))
        surface.blit(text_surf, text_rect)

        if self.shortcut_label and small_font:
            key_surf = small_font.render(self.shortcut_label, True, LIGHT_GRAY)
            key_rect = key_surf.get_rect(center=(draw_rect.centerx,
                                                  draw_rect.bottom - 12))
            surface.blit(key_surf, key_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


class UI:
    def __init__(self):
        self.font_large = pygame.font.SysFont("Arial", 44, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 26)
        self.font_small = pygame.font.SysFont("Arial", 20)
        self.font_tiny = pygame.font.SysFont("Arial", 16)
        self.font_title = pygame.font.SysFont("Arial", 58, bold=True)

        # Batch 3B: time for environment animations
        self.time = 0.0

        # Create action buttons
        self.buttons = {}
        self.rebuild_buttons(False)

        # Pet select buttons (centered under each card)
        sel_w = 140
        sel_h = 70
        sel_y = 390
        cat_card_cx = SCREEN_WIDTH // 2 - 110
        dog_card_cx = SCREEN_WIDTH // 2 + 110
        self.cat_button = Button(cat_card_cx - sel_w // 2, sel_y,
                                 sel_w, sel_h, "Cat")
        self.dog_button = Button(dog_card_cx - sel_w // 2, sel_y,
                                 sel_w, sel_h, "Dog")

        # Main menu buttons
        btn_w = 170
        btn_h = 50
        gap = 16
        total = btn_w * 2 + gap
        start_x = (SCREEN_WIDTH - total) // 2
        btn_y = 440
        self.menu_new_btn = Button(start_x, btn_y, btn_w, btn_h, "New")
        self.menu_continue_btn = Button(start_x + btn_w + gap, btn_y,
                                        btn_w, btn_h, "Continue")

        # Save button — circular icon button in header strip, right side
        self._save_btn_size = 22
        self.save_btn_rect = pygame.Rect(
            SCREEN_WIDTH - 30 - self._save_btn_size // 2,
            HUD_ROW1_Y - self._save_btn_size // 2,
            self._save_btn_size, self._save_btn_size)
        self._save_press_timer = 0.0

        # Batch 3C: pre-generate star data
        import random
        rng = random.Random(42)
        self.stars = []
        for _ in range(STAR_COUNT):
            self.stars.append({
                "x": rng.randint(0, SCREEN_WIDTH),
                "y": rng.randint(0, GROUND_Y - 50),
                "base_brightness": rng.uniform(0.5, 1.0),
                "twinkle_speed": rng.uniform(STAR_TWINKLE_MIN_SPEED,
                                             STAR_TWINKLE_MAX_SPEED),
                "phase": rng.uniform(0, 2 * math.pi),
            })

    def rebuild_buttons(self, show_medicine=False):
        """Rebuild button row with 4 or 5 buttons."""
        if show_medicine:
            count = 5
            bw = BUTTON_WIDTH_COMPACT
            bs = BUTTON_SPACING_COMPACT
            btn_data = [
                ("feed", "Feed", "[1]"),
                ("play", "Play", "[2]"),
                ("clean", "Clean", "[3]"),
                ("sleep", "Zzz", "[4]"),
                ("medicine", "Meds", "[5]"),
            ]
        else:
            count = 4
            bw = BUTTON_WIDTH
            bs = BUTTON_SPACING
            btn_data = [
                ("feed", "Feed", "[1]"),
                ("play", "Play", "[2]"),
                ("clean", "Clean", "[3]"),
                ("sleep", "Zzz", "[4]"),
            ]
        total_width = count * bw + (count - 1) * bs
        start_x = (SCREEN_WIDTH - total_width) // 2
        self.buttons = {}
        for i, (key, label, shortcut) in enumerate(btn_data):
            x = start_x + i * (bw + bs)
            self.buttons[key] = Button(x, BUTTON_Y, bw, BUTTON_HEIGHT,
                                       label, shortcut)

    def draw_poop_piles(self, surface, poop_piles):
        """Draw kawaii poop piles on the floor to the right of the pet."""
        offsets = [60, 95, 125]
        for i in range(min(poop_piles, len(offsets))):
            px = PET_CENTER_X + offsets[i]
            py = GROUND_Y - 5

            # Stink lines (animated wavy)
            for j in range(2):
                sx = px - 4 + j * 8
                for k in range(5):
                    ky = py - 18 - k * 3
                    wave = math.sin(self.time * 3 + j * 2 + k * 0.8) * 3
                    pygame.draw.circle(surface, (180, 180, 140),
                                       (int(sx + wave), ky), 1)

            # Bottom circle (largest)
            pygame.draw.circle(surface, BLACK, (px, py), 8 + OUTLINE_WIDTH)
            pygame.draw.circle(surface, POOP_COLOR, (px, py), 8)
            # Middle circle
            pygame.draw.circle(surface, BLACK, (px - 3, py - 8), 6 + OUTLINE_WIDTH)
            pygame.draw.circle(surface, POOP_COLOR, (px - 3, py - 8), 6)
            # Top circle (smallest)
            pygame.draw.circle(surface, BLACK, (px + 2, py - 14), 4 + OUTLINE_WIDTH)
            pygame.draw.circle(surface, POOP_COLOR_DARK, (px + 2, py - 14), 4)

            # Tiny highlight
            pygame.draw.circle(surface, (180, 140, 90), (px - 2, py - 3), 2)

    def update(self, dt):
        """Update environment animation time."""
        self.time += dt
        # Save button press decay
        if self._save_press_timer > 0:
            self._save_press_timer = max(0.0, self._save_press_timer - dt)

    def draw_sky(self, surface, day_progress):
        """Draw day/night sky gradient based on progress through the day."""
        p = day_progress

        if p < 0.1:
            sky_color = _lerp_color(SKY_NIGHT, SKY_DAWN, p / 0.1)
        elif p < 0.2:
            sky_color = _lerp_color(SKY_DAWN, SKY_DAY, (p - 0.1) / 0.1)
        elif p < 0.55:
            sky_color = SKY_DAY
        elif p < 0.65:
            sky_color = _lerp_color(SKY_DAY, SKY_SUNSET, (p - 0.55) / 0.1)
        elif p < 0.75:
            sky_color = _lerp_color(SKY_SUNSET, SKY_NIGHT, (p - 0.65) / 0.1)
        else:
            sky_color = SKY_NIGHT

        surface.fill(sky_color)

        # Twinkling stars at night (Batch 3C)
        if p > 0.75 or p < 0.1:
            alpha = 1.0
            if 0.75 < p < 0.8:
                alpha = (p - 0.75) / 0.05
            elif 0.05 < p < 0.1:
                alpha = (0.1 - p) / 0.05
            if alpha > 0:
                for star in self.stars:
                    twinkle = 0.6 + 0.4 * math.sin(
                        self.time * star["twinkle_speed"] + star["phase"])
                    brightness = int(200 * alpha * star["base_brightness"] * twinkle)
                    brightness = max(0, min(255, brightness))
                    star_color = (brightness, brightness, min(255, brightness + 20))
                    r = 2 if star["base_brightness"] > 0.8 and twinkle > 0.85 else 1
                    pygame.draw.circle(surface, star_color,
                                       (star["x"], star["y"]), r)

    def draw_ground(self, surface, day_progress):
        """Draw ground/grass area with swaying blades (Batch 3B)."""
        is_night = day_progress > 0.7 or day_progress < 0.1
        grass_color = GRASS_DARK if is_night else GRASS_GREEN
        pygame.draw.rect(surface, grass_color,
                         (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))

        t = self.time

        # Back layer: shorter blades, slow sway
        back_color = _lerp_color(grass_color, (40, 100, 30), 0.2)
        for i in range(0, SCREEN_WIDTH, 18):
            h = 6 + (i * 7 % 9)
            sway = math.sin(t * GRASS_SWAY_SPEED_BACK + i * 0.08) * 2
            pygame.draw.line(surface, back_color,
                             (i, GROUND_Y), (i + 2 + sway, GROUND_Y - h), 1)

        # Front layer: taller blades, faster sway
        front_color = _lerp_color(grass_color, (40, 100, 30), 0.35)
        for i in range(0, SCREEN_WIDTH, 12):
            h = 8 + (i * 7 % 11)
            sway = math.sin(t * GRASS_SWAY_SPEED_FRONT + i * 0.12) * 3.5
            pygame.draw.line(surface, front_color,
                             (i, GROUND_Y), (i + 3 + sway, GROUND_Y - h), 1)

    def _get_sky_color(self, day_progress):
        """Compute the sky color for a given day_progress value."""
        p = day_progress
        if p < 0.1:
            return _lerp_color(SKY_NIGHT, SKY_DAWN, p / 0.1)
        elif p < 0.2:
            return _lerp_color(SKY_DAWN, SKY_DAY, (p - 0.1) / 0.1)
        elif p < 0.55:
            return SKY_DAY
        elif p < 0.65:
            return _lerp_color(SKY_DAY, SKY_SUNSET, (p - 0.55) / 0.1)
        elif p < 0.75:
            return _lerp_color(SKY_SUNSET, SKY_NIGHT, (p - 0.65) / 0.1)
        else:
            return SKY_NIGHT

    def _get_night_factor(self, day_progress):
        """Return 0.0 (full day) to 1.0 (full night) with smooth transitions."""
        p = day_progress
        if p < 0.05:
            return 1.0 - p / 0.05
        elif p < 0.15:
            return 0.0
        elif p < 0.55:
            return 0.0
        elif p < 0.7:
            return (p - 0.55) / 0.15
        else:
            return 1.0

    def draw_room(self, surface, day_progress):
        """Draw a decorated kawaii apartment interior as the play background."""
        t = self.time
        nf = self._get_night_factor(day_progress)

        # === WALL ===
        wall_day = (245, 230, 210)
        wall_night = (180, 160, 140)
        wall_color = _lerp_color(wall_day, wall_night, nf)
        wall_top = 70
        wall_bottom = 350
        pygame.draw.rect(surface, wall_color,
                         (0, wall_top, SCREEN_WIDTH, wall_bottom - wall_top))

        # Wallpaper texture: faint dots
        dot_color = _lerp_color((235, 218, 195), (170, 150, 130), nf)
        for wy in range(wall_top + 15, wall_bottom, 30):
            offset = 15 if (wy // 30) % 2 else 0
            for wx in range(offset, SCREEN_WIDTH, 30):
                pygame.draw.circle(surface, dot_color, (wx, wy), 1)

        # === WINDOW (left-center) ===
        win_x, win_y, win_w, win_h = 60, 80, 140, 120
        frame_color = _lerp_color((160, 120, 70), (120, 90, 50), nf)
        # Frame outer
        pygame.draw.rect(surface, frame_color,
                         (win_x - 6, win_y - 6, win_w + 12, win_h + 18),
                         border_radius=4)
        # Sky inside window
        sky_color = self._get_sky_color(day_progress)
        pygame.draw.rect(surface, sky_color,
                         (win_x, win_y, win_w, win_h))
        # Window cross bars
        bar_color = _lerp_color((140, 105, 60), (100, 75, 40), nf)
        pygame.draw.line(surface, bar_color,
                         (win_x + win_w // 2, win_y),
                         (win_x + win_w // 2, win_y + win_h), 3)
        pygame.draw.line(surface, bar_color,
                         (win_x, win_y + win_h // 2),
                         (win_x + win_w, win_y + win_h // 2), 3)

        # Stars through window at night
        if nf > 0.3:
            star_alpha = min(1.0, (nf - 0.3) / 0.3)
            for star in self.stars:
                sx = star["x"] % win_w + win_x
                sy = star["y"] % win_h + win_y
                if win_x < sx < win_x + win_w and win_y < sy < win_y + win_h:
                    twinkle = 0.6 + 0.4 * math.sin(
                        t * star["twinkle_speed"] + star["phase"])
                    b = int(180 * star_alpha * star["base_brightness"] * twinkle)
                    b = max(0, min(255, b))
                    pygame.draw.circle(surface, (b, b, min(255, b + 15)),
                                       (sx, sy), 1)

        # Curtains (soft drapes on sides)
        curtain_color = _lerp_color((220, 180, 180), (170, 140, 140), nf)
        sway = math.sin(t * 0.8) * 3
        # Left curtain
        pygame.draw.polygon(surface, curtain_color, [
            (win_x - 4, win_y - 4),
            (win_x + 18 + sway, win_y - 4),
            (win_x + 12 + sway, win_y + win_h + 4),
            (win_x - 4, win_y + win_h + 4),
        ])
        # Right curtain
        pygame.draw.polygon(surface, curtain_color, [
            (win_x + win_w + 4, win_y - 4),
            (win_x + win_w - 18 - sway, win_y - 4),
            (win_x + win_w - 12 - sway, win_y + win_h + 4),
            (win_x + win_w + 4, win_y + win_h + 4),
        ])
        # Window sill
        sill_color = _lerp_color((145, 110, 60), (110, 80, 40), nf)
        pygame.draw.rect(surface, sill_color,
                         (win_x - 10, win_y + win_h + 6, win_w + 20, 8),
                         border_radius=2)

        # === PICTURE FRAME (right side) ===
        pf_x, pf_y, pf_w, pf_h = 340, 100, 50, 60
        pf_frame = _lerp_color((130, 90, 50), (100, 70, 40), nf)
        pygame.draw.rect(surface, pf_frame,
                         (pf_x - 4, pf_y - 4, pf_w + 8, pf_h + 8),
                         border_radius=3)
        pf_bg = _lerp_color((255, 245, 235), (210, 200, 185), nf)
        pygame.draw.rect(surface, pf_bg, (pf_x, pf_y, pf_w, pf_h))
        # Draw a tiny heart inside
        hcx, hcy = pf_x + pf_w // 2, pf_y + pf_h // 2
        hr = 6
        heart_color = _lerp_color((255, 150, 180), (200, 120, 150), nf)
        pygame.draw.circle(surface, heart_color, (hcx - 4, hcy - 2), hr)
        pygame.draw.circle(surface, heart_color, (hcx + 4, hcy - 2), hr)
        pygame.draw.polygon(surface, heart_color, [
            (hcx - 9, hcy + 1), (hcx + 9, hcy + 1), (hcx, hcy + 10),
        ])

        # === WALL SHELF (right side) ===
        sh_x, sh_y, sh_w, sh_h = 350, 210, 90, 10
        shelf_color = _lerp_color((140, 100, 55), (110, 80, 40), nf)
        pygame.draw.rect(surface, shelf_color,
                         (sh_x, sh_y, sh_w, sh_h), border_radius=2)
        # Shelf bracket lines
        pygame.draw.line(surface, shelf_color,
                         (sh_x + 10, sh_y + sh_h),
                         (sh_x + 10, sh_y + sh_h + 10), 2)
        pygame.draw.line(surface, shelf_color,
                         (sh_x + sh_w - 10, sh_y + sh_h),
                         (sh_x + sh_w - 10, sh_y + sh_h + 10), 2)

        # Books on shelf
        book_colors = [
            _lerp_color((180, 80, 80), (140, 60, 60), nf),
            _lerp_color((80, 130, 180), (60, 100, 140), nf),
            _lerp_color((80, 160, 90), (60, 120, 70), nf),
        ]
        bx = sh_x + 5
        for i, bc in enumerate(book_colors):
            bw = 10 + (i % 2) * 3
            bh = 22 + (i % 3) * 4
            pygame.draw.rect(surface, bc,
                             (bx, sh_y - bh, bw, bh), border_radius=1)
            bx += bw + 2

        # Potted plant on shelf
        pot_x = sh_x + sh_w - 25
        pot_color = _lerp_color((190, 120, 70), (150, 95, 55), nf)
        pygame.draw.polygon(surface, pot_color, [
            (pot_x - 8, sh_y),
            (pot_x + 8, sh_y),
            (pot_x + 6, sh_y - 16),
            (pot_x - 6, sh_y - 16),
        ])
        # Leaves
        leaf_color = _lerp_color((90, 180, 80), (60, 130, 55), nf)
        leaf_sway = math.sin(t * 1.2) * 2
        pygame.draw.circle(surface, leaf_color,
                           (pot_x + int(leaf_sway), sh_y - 24), 7)
        pygame.draw.circle(surface, leaf_color,
                           (pot_x - 7 + int(leaf_sway * 0.7), sh_y - 20), 6)
        pygame.draw.circle(surface, leaf_color,
                           (pot_x + 8 + int(leaf_sway * 0.5), sh_y - 19), 5)

        # === CLOCK (right-upper) ===
        clk_cx, clk_cy, clk_r = 420, 95, 18
        clock_rim = _lerp_color((160, 120, 70), (120, 90, 50), nf)
        clock_face = _lerp_color((255, 250, 240), (210, 200, 185), nf)
        pygame.draw.circle(surface, clock_rim, (clk_cx, clk_cy), clk_r + 3)
        pygame.draw.circle(surface, clock_face, (clk_cx, clk_cy), clk_r)
        # Hour marks
        for i in range(12):
            angle = i * math.pi / 6 - math.pi / 2
            mx = clk_cx + int(math.cos(angle) * (clk_r - 3))
            my = clk_cy + int(math.sin(angle) * (clk_r - 3))
            pygame.draw.circle(surface, clock_rim, (mx, my), 1)
        # Hour hand
        hour_angle = day_progress * 2 * math.pi - math.pi / 2
        hx = clk_cx + int(math.cos(hour_angle) * (clk_r - 8))
        hy = clk_cy + int(math.sin(hour_angle) * (clk_r - 8))
        pygame.draw.line(surface, BLACK, (clk_cx, clk_cy), (hx, hy), 2)
        # Minute hand
        min_angle = t * 0.5 - math.pi / 2
        mx2 = clk_cx + int(math.cos(min_angle) * (clk_r - 4))
        my2 = clk_cy + int(math.sin(min_angle) * (clk_r - 4))
        pygame.draw.line(surface, DARK_GRAY, (clk_cx, clk_cy), (mx2, my2), 1)
        # Center dot
        pygame.draw.circle(surface, BLACK, (clk_cx, clk_cy), 2)

        # === FLOOR LAMP (left side) ===
        lamp_x = 45
        lamp_top = 250
        lamp_base_y = wall_bottom
        pole_color = _lerp_color((120, 100, 70), (90, 75, 50), nf)
        shade_color = _lerp_color((240, 220, 180), (200, 180, 150), nf)
        # Pole
        pygame.draw.line(surface, pole_color,
                         (lamp_x, lamp_top + 30), (lamp_x, lamp_base_y), 3)
        # Base
        pygame.draw.ellipse(surface, pole_color,
                            (lamp_x - 12, lamp_base_y - 4, 24, 8))
        # Shade (trapezoid)
        pygame.draw.polygon(surface, shade_color, [
            (lamp_x - 20, lamp_top + 30),
            (lamp_x + 20, lamp_top + 30),
            (lamp_x + 10, lamp_top),
            (lamp_x - 10, lamp_top),
        ])
        # Shade outline
        pygame.draw.polygon(surface, pole_color, [
            (lamp_x - 20, lamp_top + 30),
            (lamp_x + 20, lamp_top + 30),
            (lamp_x + 10, lamp_top),
            (lamp_x - 10, lamp_top),
        ], 1)

        # === BASEBOARD ===
        baseboard_color = _lerp_color((180, 155, 120), (130, 110, 85), nf)
        pygame.draw.rect(surface, baseboard_color,
                         (0, wall_bottom, SCREEN_WIDTH, 8))

        # === FLOOR ===
        floor_top = wall_bottom + 8
        floor_bottom = GROUND_Y
        plank1_day = (200, 165, 115)
        plank2_day = (190, 155, 105)
        plank1 = _lerp_color(plank1_day, (150, 125, 85), nf)
        plank2 = _lerp_color(plank2_day, (140, 115, 78), nf)
        plank_h = 14
        for py in range(floor_top, floor_bottom, plank_h):
            color = plank1 if ((py - floor_top) // plank_h) % 2 == 0 else plank2
            h = min(plank_h, floor_bottom - py)
            pygame.draw.rect(surface, color, (0, py, SCREEN_WIDTH, h))
            # Plank gap line
            gap_color = _lerp_color((170, 140, 95), (120, 100, 70), nf)
            pygame.draw.line(surface, gap_color,
                             (0, py), (SCREEN_WIDTH, py), 1)

        # === BUTTON AREA (below GROUND_Y) ===
        btn_bg = _lerp_color((160, 135, 95), (110, 90, 65), nf)
        pygame.draw.rect(surface, btn_bg,
                         (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))

        # === RUG (centered on pet area) ===
        rug_cx, rug_cy = 240, 420
        rug_rx, rug_ry = 75, 28
        rug_border = _lerp_color((180, 120, 150), (140, 90, 115), nf)
        rug_fill = _lerp_color((230, 180, 200), (190, 145, 165), nf)
        pygame.draw.ellipse(surface, rug_border,
                            (rug_cx - rug_rx, rug_cy - rug_ry,
                             rug_rx * 2, rug_ry * 2))
        pygame.draw.ellipse(surface, rug_fill,
                            (rug_cx - rug_rx + 4, rug_cy - rug_ry + 3,
                             (rug_rx - 4) * 2, (rug_ry - 3) * 2))

        # === TOP BAR (above wall, for stat bars area) ===
        top_color = _lerp_color((230, 215, 195), (165, 145, 125), nf)
        pygame.draw.rect(surface, top_color, (0, 0, SCREEN_WIDTH, wall_top))

        # === NIGHT LAMP GLOW ===
        if nf > 0.2:
            glow_alpha = int(45 * min(1.0, (nf - 0.2) / 0.3))
            glow_r = 70
            glow_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
            for ring in range(glow_r, 0, -2):
                a = int(glow_alpha * (ring / glow_r))
                pygame.draw.circle(glow_surf, (255, 220, 140, a),
                                   (glow_r, glow_r), ring)
            surface.blit(glow_surf,
                         (lamp_x - glow_r, lamp_top + 10 - glow_r))

        # === SUBTLE NIGHT OVERLAY ===
        if nf > 0.3:
            ov_alpha = int(18 * min(1.0, (nf - 0.3) / 0.3))
            overlay = pygame.Surface((SCREEN_WIDTH, GROUND_Y), pygame.SRCALPHA)
            overlay.fill((20, 15, 40, ov_alpha))
            surface.blit(overlay, (0, 0))

    def draw_stat_bars(self, surface, pet):
        """Draw 4 compact icon + mini bar stats in a single row."""
        stats = [
            ("hunger", pet.hunger, COLOR_HUNGER, _draw_icon_hunger),
            ("happy", pet.happiness, COLOR_HAPPINESS, _draw_icon_happy),
            ("energy", pet.energy, COLOR_ENERGY, _draw_icon_energy),
            ("clean", pet.cleanliness, COLOR_CLEANLINESS, _draw_icon_clean),
        ]
        num = len(stats)
        slot_w = HUD_ICON_SIZE + 4 + HUD_BAR_W   # icon + gap + bar
        gap = 8
        total_w = num * slot_w + (num - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2

        for i, (name, value, color, icon_fn) in enumerate(stats):
            x = start_x + i * (slot_w + gap)
            bar_y = HUD_ROW2_Y

            # Draw icon
            icon_cx = x + HUD_ICON_SIZE // 2
            icon_cy = bar_y + HUD_BAR_H // 2
            icon_fn(surface, icon_cx, icon_cy, color)

            # Bar background
            bar_x = x + HUD_ICON_SIZE + 4
            bar_rect = pygame.Rect(bar_x, bar_y, HUD_BAR_W, HUD_BAR_H)
            pygame.draw.rect(surface, COLOR_STAT_BG, bar_rect, border_radius=3)

            # Bar fill
            fill_w = int((value / STAT_MAX) * HUD_BAR_W)
            if fill_w > 0:
                bar_color = (220, 50, 50) if value < 20 else color
                fill_rect = pygame.Rect(bar_x, bar_y, fill_w, HUD_BAR_H)
                pygame.draw.rect(surface, bar_color, fill_rect, border_radius=3)
                # Shimmer
                shimmer_h = max(1, HUD_BAR_H // 3)
                shimmer_surf = pygame.Surface((fill_w, shimmer_h), pygame.SRCALPHA)
                shimmer_surf.fill((255, 255, 255, 30))
                surface.blit(shimmer_surf, (bar_x, bar_y))

            # Border
            pygame.draw.rect(surface, COLOR_STAT_BORDER, bar_rect, 1, border_radius=3)

    def draw_xp_bar(self, surface, pet):
        """Draw a thin full-width XP bar with Lv label and streak flame."""
        margin = 40
        bar_x = margin
        bar_w = SCREEN_WIDTH - margin * 2
        bar_y = HUD_XP_Y
        bar_h = HUD_XP_H

        # "Lv.X" label left of bar
        lv_surf = self.font_tiny.render(f"Lv.{pet.level}", True, XP_LEVEL_COLOR)
        surface.blit(lv_surf, (bar_x - 32, bar_y - 2))

        # Background
        bg_rect = pygame.Rect(bar_x, bar_y, bar_w, bar_h)
        pygame.draw.rect(surface, XP_BAR_BG, bg_rect, border_radius=3)

        # Fill
        if pet.xp_for_next_level > 0:
            ratio = min(1.0, pet.xp_for_current_level / pet.xp_for_next_level)
        else:
            ratio = 1.0
        fill_w = int(ratio * bar_w)
        if fill_w > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_w, bar_h)
            pygame.draw.rect(surface, XP_BAR_COLOR, fill_rect, border_radius=3)

        # Border
        pygame.draw.rect(surface, (100, 80, 140), bg_rect, 1, border_radius=3)

        # Streak flame icon + count on the right
        if pet.streak_days > 0:
            flame_x = bar_x + bar_w + 10
            flame_y = bar_y + bar_h // 2
            pygame.draw.circle(surface, STREAK_ICON_COLOR,
                               (flame_x, flame_y + 1), 4)
            pygame.draw.polygon(surface, STREAK_ICON_COLOR, [
                (flame_x - 3, flame_y + 2),
                (flame_x + 3, flame_y + 2),
                (flame_x, flame_y - 6),
            ])
            streak_text = self.font_tiny.render(
                str(pet.streak_days), True, STREAK_ICON_COLOR)
            surface.blit(streak_text, (flame_x + 7, bar_y - 2))

    def draw_vocab_badge(self, surface, pet):
        """Draw the vocabulary badge/rank pill below the XP bar, right-aligned."""
        rank_name, rank_idx = pet.vocab_badge
        _, _, icon_shape, color = BADGE_RANKS[rank_idx]

        pill_w = 88
        pill_h = 16
        pill_x = SCREEN_WIDTH - 40 - pill_w  # right-aligned under XP bar
        pill_y = HUD_XP_Y + HUD_XP_H + 3

        # Background
        bg_color = (max(0, color[0] // 5 + 20),
                    max(0, color[1] // 5 + 20),
                    max(0, color[2] // 5 + 20))
        pygame.draw.rect(surface, bg_color,
                         (pill_x, pill_y, pill_w, pill_h), border_radius=8)
        pygame.draw.rect(surface, color,
                         (pill_x, pill_y, pill_w, pill_h), width=1, border_radius=8)

        # Icon
        icx = pill_x + 12
        icy = pill_y + pill_h // 2
        if icon_shape == "star":
            pts = []
            for i in range(10):
                angle = i * math.pi / 5 - math.pi / 2
                r = 5 if i % 2 == 0 else 2
                pts.append((icx + math.cos(angle) * r,
                            icy + math.sin(angle) * r))
            pygame.draw.polygon(surface, color, pts)
        elif icon_shape == "book":
            pygame.draw.rect(surface, color, (icx - 4, icy - 4, 4, 8), border_radius=1)
            pygame.draw.rect(surface, color, (icx, icy - 4, 4, 8), border_radius=1)
            pygame.draw.line(surface, bg_color, (icx, icy - 4), (icx, icy + 4), 1)
        elif icon_shape == "star2":
            for dx in (-3, 3):
                pts = []
                for i in range(10):
                    angle = i * math.pi / 5 - math.pi / 2
                    r = 4 if i % 2 == 0 else 1.6
                    pts.append((icx + dx + math.cos(angle) * r,
                                icy + math.sin(angle) * r))
                pygame.draw.polygon(surface, color, pts)
        elif icon_shape == "star3":
            for dx in (-4, 0, 4):
                pts = []
                for i in range(10):
                    angle = i * math.pi / 5 - math.pi / 2
                    r = 3.5 if i % 2 == 0 else 1.4
                    pts.append((icx + dx + math.cos(angle) * r,
                                icy + math.sin(angle) * r))
                pygame.draw.polygon(surface, color, pts)
        elif icon_shape == "crown":
            pygame.draw.rect(surface, color, (icx - 6, icy - 1, 12, 5))
            for dx in (-4, 0, 4):
                pygame.draw.polygon(surface, color, [
                    (icx + dx - 2, icy - 1),
                    (icx + dx + 2, icy - 1),
                    (icx + dx, icy - 5)])

        # Rank name
        rank_surf = self.font_tiny.render(rank_name, True, color)
        surface.blit(rank_surf, (icx + 10,
                                 pill_y + pill_h // 2 - rank_surf.get_height() // 2))

    def draw_save_button(self, surface, mouse_pos):
        """Draw a circular save icon button in the HUD header strip, right side."""
        r = self.save_btn_rect
        hovered = r.collidepoint(mouse_pos)
        cx = r.centerx
        cy = r.centery
        radius = self._save_btn_size // 2

        # Press shrink effect
        shrink = 0
        if self._save_press_timer > 0:
            shrink = 1

        # Draw circle background
        btn_surf = pygame.Surface((self._save_btn_size + 8, self._save_btn_size + 8),
                                  pygame.SRCALPHA)
        bcx = self._save_btn_size // 2 + 4
        bcy = self._save_btn_size // 2 + 4
        dr = radius - shrink

        if hovered:
            # Glow ring
            pygame.draw.circle(btn_surf, (100, 90, 150, 60), (bcx, bcy), dr + 3)
            pygame.draw.circle(btn_surf, (70, 60, 100, 200), (bcx, bcy), dr)
            icon_color = (240, 235, 255)
        else:
            pygame.draw.circle(btn_surf, (40, 35, 60, 140), (bcx, bcy), dr)
            icon_color = (180, 170, 210)

        # Bookmark/ribbon icon: rectangle with V-notch at bottom
        bk_w = int(dr * 0.7)
        bk_h = int(dr * 1.0)
        bk_x = bcx - bk_w // 2
        bk_y = bcy - bk_h // 2 - 1
        notch_depth = bk_h // 3

        bookmark_pts = [
            (bk_x, bk_y),
            (bk_x + bk_w, bk_y),
            (bk_x + bk_w, bk_y + bk_h),
            (bk_x + bk_w // 2, bk_y + bk_h - notch_depth),
            (bk_x, bk_y + bk_h),
        ]
        pygame.draw.polygon(btn_surf, icon_color, bookmark_pts)

        surface.blit(btn_surf, (cx - self._save_btn_size // 2 - 4,
                                cy - self._save_btn_size // 2 - 4))

    def draw_save_toast(self, surface, timer):
        """Draw a 'Saved!' toast as a centered banner at y=80, fades over last 0.5s."""
        if timer <= 0:
            return
        alpha = min(255, int(255 * (timer / 0.5))) if timer < 0.5 else 255

        txt = self.font_small.render("Saved!", True, (255, 220, 100))
        tw = txt.get_width()
        th = txt.get_height()
        pill_w = tw + 28
        pill_h = th + 10
        pill_x = (SCREEN_WIDTH - pill_w) // 2
        pill_y = 80

        toast_surf = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
        pygame.draw.rect(toast_surf, (40, 35, 60, min(200, alpha)),
                         (0, 0, pill_w, pill_h), border_radius=pill_h // 2)
        txt.set_alpha(alpha)
        toast_surf.blit(txt, (14, 5))
        surface.blit(toast_surf, (pill_x, pill_y))

    def draw_wardrobe_hint(self, surface, timer, mastered_needed=5):
        """Draw floating tooltip above pet: 'Master N words to unlock styles!'"""
        if timer <= 0:
            return
        # Fade in/out
        t = timer / WARDROBE_HINT_DURATION
        if t > 0.85:
            alpha = int(255 * ((1.0 - t) / 0.15))
        elif t < 0.2:
            alpha = int(255 * (t / 0.2))
        else:
            alpha = 255
        # Slight float upward as it fades
        y_off = int((1.0 - t) * -6)

        star = "\u2605 "
        text = f"{star}Master {mastered_needed} words to unlock styles!"
        txt_surf = self.font_small.render(text, True, WARDROBE_HINT_COLOR)
        tw, th = txt_surf.get_size()
        pill_w = tw + 28
        pill_h = th + 14
        pill_x = (SCREEN_WIDTH - pill_w) // 2
        pill_y = WARDROBE_HINT_Y + y_off

        hint_surf = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
        bg_r, bg_g, bg_b, bg_a = WARDROBE_HINT_BG
        pygame.draw.rect(hint_surf, (bg_r, bg_g, bg_b, min(bg_a, alpha)),
                         (0, 0, pill_w, pill_h), border_radius=pill_h // 2)
        br, bg, bb = WARDROBE_HINT_BORDER
        pygame.draw.rect(hint_surf, (br, bg, bb, min(255, alpha)),
                         (0, 0, pill_w, pill_h), 2, border_radius=pill_h // 2)
        txt_surf.set_alpha(alpha)
        hint_surf.blit(txt_surf, (14, 7))
        surface.blit(hint_surf, (pill_x, pill_y))

        # Arrow pointing down

        arrow_cx = SCREEN_WIDTH // 2
        arrow_y = pill_y + pill_h
        arrow_surf = pygame.Surface((16, 8), pygame.SRCALPHA)
        pygame.draw.polygon(arrow_surf, (bg_r, bg_g, bg_b, min(bg_a, alpha)),
                            [(0, 0), (16, 0), (8, 8)])
        surface.blit(arrow_surf, (arrow_cx - 8, arrow_y))

    def draw_badge_celebration(self, surface, rank_name, rank_color, unlocked_items, timer):
        """Draw centered rank-up celebration toast with list of unlocked items."""
        if timer <= 0:
            return
        # Fade in/out
        max_time = 4.0
        t = timer / max_time
        if t > 0.9:
            alpha = int(255 * ((1.0 - t) / 0.1))
            scale_f = 0.6 + 0.4 * ((1.0 - t) / 0.1)
        elif t < 0.15:
            alpha = int(255 * (t / 0.15))
            scale_f = 1.0
        else:
            alpha = 255
            scale_f = 1.0

        # Toast dimensions
        toast_w = 380
        # Height depends on number of unlock chips
        chip_rows = (len(unlocked_items) + 3) // 4 if unlocked_items else 0
        toast_h = 90 + chip_rows * 22
        toast_x = (SCREEN_WIDTH - toast_w) // 2
        toast_y = (SCREEN_HEIGHT - toast_h) // 2

        toast_surf = pygame.Surface((toast_w, toast_h), pygame.SRCALPHA)

        # Background
        pygame.draw.rect(toast_surf, (35, 22, 74, min(240, alpha)),
                         (0, 0, toast_w, toast_h), border_radius=18)
        # Border
        br, bg_c, bb = WARDROBE_HINT_BORDER
        pygame.draw.rect(toast_surf, (br, bg_c, bb, min(255, alpha)),
                         (0, 0, toast_w, toast_h), 3, border_radius=18)

        # "New Rank:" label
        label = self.font_small.render("New Rank:", True, (170, 170, 170))
        label.set_alpha(alpha)
        toast_surf.blit(label, (toast_w // 2 - label.get_width() // 2 - 50, 16))

        # Rank name
        rank_txt = self.font_large.render(f" {rank_name}!", True, rank_color)
        rank_txt.set_alpha(alpha)
        toast_surf.blit(rank_txt, (toast_w // 2 - label.get_width() // 2 +
                                   label.get_width() - 50, 10))

        # "New styles unlocked!" subtitle
        sub = self.font_small.render("New styles unlocked!", True, (200, 184, 238))
        sub.set_alpha(alpha)
        toast_surf.blit(sub, (toast_w // 2 - sub.get_width() // 2, 42))

        # Unlock chips
        if unlocked_items:
            chip_y = 66
            chip_x_start = 12
            cx = chip_x_start
            for item_label in unlocked_items:
                chip_txt = self.font_tiny.render(item_label, True, (142, 232, 142))
                chip_w = chip_txt.get_width() + 16
                chip_h = 18
                if cx + chip_w > toast_w - 12:
                    cx = chip_x_start
                    chip_y += 22

                chip_bg = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
                pygame.draw.rect(chip_bg, (100, 220, 100, min(40, alpha // 6)),
                                 (0, 0, chip_w, chip_h), border_radius=8)
                pygame.draw.rect(chip_bg, (100, 220, 100, min(100, alpha // 2)),
                                 (0, 0, chip_w, chip_h), 1, border_radius=8)
                chip_txt.set_alpha(alpha)
                chip_bg.blit(chip_txt, (8, 2))
                toast_surf.blit(chip_bg, (cx, chip_y))
                cx += chip_w + 6

        surface.blit(toast_surf, (toast_x, toast_y))

    def draw_day_info(self, surface, pet):
        """Draw the full compact HUD header background and name/day/time row."""
        # Full header dark background
        bg_surf = pygame.Surface((SCREEN_WIDTH, HUD_HEIGHT), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 100))
        surface.blit(bg_surf, (0, 0))

        # Row 1: name / day (stage) / time — centered at HUD_ROW1_Y
        is_night = not pet.is_daytime
        icon = "Moon" if is_night else "Sun"
        stage_label = {"baby": "Baby", "kid": "Kid", "adult": "Adult"}.get(
            pet.growth_stage, "")
        text = f"{pet.name}   Day {pet.day_count} ({stage_label})   {icon}   {pet.time_of_day_label}"
        text_surf = self.font_small.render(text, True, COLOR_DAY_TEXT)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, HUD_ROW1_Y))
        surface.blit(text_surf, text_rect)

    def draw_mood_text(self, surface, pet):
        """Draw mood text below the pet, above buttons."""
        text_surf = self.font_medium.render(pet.mood_text, True, COLOR_MOOD_TEXT)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 450))
        surface.blit(text_surf, text_rect)

    def draw_action_buttons(self, surface, mouse_pos, dt=1 / 60):
        """Draw the four action buttons (Batch 4B: polish)."""
        for btn in self.buttons.values():
            btn.update(mouse_pos, dt)
            btn.draw(surface, self.font_medium, self.font_tiny)

    def draw_sick_warning(self, surface, pet):
        """Draw sick warning below pet area if pet is sick."""
        if not pet.is_sick:
            return
        remaining = SICK_TIMER_LIMIT - pet.sick_timer
        if remaining < 0:
            remaining = 0
        text = f"{pet.name} is sick! Help within {int(remaining)}s or it will run away!"
        text_surf = self.font_small.render(text, True, (255, 80, 80))
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 430))
        surface.blit(text_surf, text_rect)

    def draw_menu(self, surface, time_val, mouse_pos=(0, 0)):
        """Draw the main menu screen with gradient, particles, and kawaii pets."""
        # Soft vertical gradient background
        _draw_gradient(surface, (35, 20, 65), (55, 30, 80),
                       (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Floating decorative particles (hearts and stars)
        import random as _rng
        particle_rng = _rng.Random(42)
        num_particles = 18
        for i in range(num_particles):
            px = particle_rng.randint(10, SCREEN_WIDTH - 10)
            base_y = particle_rng.randint(50, SCREEN_HEIGHT - 50)
            drift_speed = particle_rng.uniform(0.3, 0.8)
            p_size = particle_rng.uniform(3, 6)
            shape = particle_rng.choice(["heart", "star"])
            # Drift upward, wrap around
            py = (base_y - time_val * drift_speed * 40) % SCREEN_HEIGHT
            alpha = int(40 + 30 * math.sin(time_val * 1.5 + i))
            p_surf = pygame.Surface((int(p_size * 4), int(p_size * 4)), pygame.SRCALPHA)
            pcx, pcy = int(p_size * 2), int(p_size * 2)
            if shape == "heart":
                hr = max(2, int(p_size * 0.5))
                color = (255, 150, 180, alpha)
                pygame.draw.circle(p_surf, color, (pcx - hr, pcy - int(hr * 0.3)), hr)
                pygame.draw.circle(p_surf, color, (pcx + hr, pcy - int(hr * 0.3)), hr)
                pygame.draw.polygon(p_surf, color, [
                    (pcx - int(hr * 1.5), pcy),
                    (pcx + int(hr * 1.5), pcy),
                    (pcx, pcy + int(hr * 1.5)),
                ])
            else:
                color = (255, 220, 100, alpha)
                sr = max(2, int(p_size * 0.6))
                pts = []
                rot = time_val * 0.5 + i
                for j in range(10):
                    angle = rot + j * math.pi / 5 - math.pi / 2
                    r = sr if j % 2 == 0 else sr * 0.4
                    pts.append((pcx + math.cos(angle) * r,
                                pcy + math.sin(angle) * r))
                pygame.draw.polygon(p_surf, color, pts)
            surface.blit(p_surf, (int(px - p_size * 2), int(py - p_size * 2)))

        # Title with shadow
        title_y = 140 + math.sin(time_val * 1.5) * 8
        # Shadow
        shadow_surf = self.font_title.render("Tamagotchi", True, BLACK)
        shadow_rect = shadow_surf.get_rect(center=(SCREEN_WIDTH // 2 + 2,
                                                    title_y + 2))
        surface.blit(shadow_surf, shadow_rect)
        # Main title
        title_surf = self.font_title.render("Tamagotchi", True, COLOR_TITLE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, title_y))
        surface.blit(title_surf, title_rect)

        # Subtitle
        sub_surf = self.font_medium.render("Virtual Pet", True, COLOR_SUBTITLE)
        sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, title_y + 50))
        surface.blit(sub_surf, sub_rect)

        # Kawaii pet previews
        _draw_outline_pet(surface, 140, 320, "cat", 0.65, time_val)
        _draw_outline_pet(surface, 340, 320, "dog", 0.65, time_val)

        # Menu buttons
        self.menu_new_btn.update(mouse_pos)
        self.menu_new_btn.draw(surface, self.font_medium)
        self.menu_continue_btn.update(mouse_pos)
        self.menu_continue_btn.draw(surface, self.font_medium)

    def draw_break_warning(self, surface):
        """Draw a soft session time warning overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        surface.blit(overlay, (0, 0))

        # Message box
        box_w, box_h = 360, 120
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = (SCREEN_HEIGHT - box_h) // 2 - 40
        pygame.draw.rect(surface, (50, 45, 70),
                         (box_x, box_y, box_w, box_h), border_radius=16)
        pygame.draw.rect(surface, (120, 100, 160),
                         (box_x, box_y, box_w, box_h), 2, border_radius=16)

        line1 = self.font_medium.render("Time for a break!", True,
                                         (255, 220, 100))
        line2 = self.font_small.render("Your pet is getting sleepy.", True,
                                        (200, 200, 220))
        surface.blit(line1, line1.get_rect(center=(SCREEN_WIDTH // 2,
                                                    box_y + 40)))
        surface.blit(line2, line2.get_rect(center=(SCREEN_WIDTH // 2,
                                                    box_y + 80)))

    def draw_hard_cap_overlay(self, surface, pet):
        """Draw a persistent overlay when the session hard cap is reached."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        surface.blit(overlay, (0, 0))

        box_w, box_h = 380, 140
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = (SCREEN_HEIGHT - box_h) // 2 - 40
        pygame.draw.rect(surface, (40, 35, 60),
                         (box_x, box_y, box_w, box_h), border_radius=16)
        pygame.draw.rect(surface, (100, 80, 140),
                         (box_x, box_y, box_w, box_h), 2, border_radius=16)

        line1 = self.font_medium.render("Your pet is sleeping now.", True,
                                         (180, 180, 220))
        line2 = self.font_small.render("See you tomorrow!", True,
                                        (255, 220, 100))
        line3 = self.font_tiny.render("Press ESC to save and exit", True,
                                       (160, 160, 180))
        surface.blit(line1, line1.get_rect(center=(SCREEN_WIDTH // 2,
                                                    box_y + 38)))
        surface.blit(line2, line2.get_rect(center=(SCREEN_WIDTH // 2,
                                                    box_y + 72)))
        surface.blit(line3, line3.get_rect(center=(SCREEN_WIDTH // 2,
                                                    box_y + 110)))

    def draw_stage_up(self, surface, pet):
        """Draw a brief congratulatory message when the pet evolves to a new stage."""
        stage_names = {GROWTH_BABY: "Baby", GROWTH_KID: "Kid", GROWTH_ADULT: "Adult"}
        stage_name = stage_names.get(pet.growth_stage, pet.growth_stage)

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 60))
        surface.blit(overlay, (0, 0))

        box_w, box_h = 340, 100
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = (SCREEN_HEIGHT - box_h) // 2 - 60
        pygame.draw.rect(surface, (60, 50, 80),
                         (box_x, box_y, box_w, box_h), border_radius=16)
        pygame.draw.rect(surface, (180, 140, 255),
                         (box_x, box_y, box_w, box_h), 2, border_radius=16)

        line1 = self.font_medium.render("Your pet grew up!", True,
                                         (255, 220, 100))
        line2 = self.font_small.render(f"Now a {stage_name}!", True,
                                        (220, 200, 255))
        surface.blit(line1, line1.get_rect(center=(SCREEN_WIDTH // 2,
                                                    box_y + 35)))
        surface.blit(line2, line2.get_rect(center=(SCREEN_WIDTH // 2,
                                                    box_y + 68)))

    def draw_pet_select(self, surface, mouse_pos, time_val):
        """Draw the pet selection screen with gradient, cards, and kawaii pets."""
        # Same gradient as menu for consistency
        _draw_gradient(surface, (35, 20, 65), (55, 30, 80),
                       (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Title with shadow
        shadow_surf = self.font_large.render("Choose Your Pet", True, BLACK)
        shadow_rect = shadow_surf.get_rect(center=(SCREEN_WIDTH // 2 + 2, 82))
        surface.blit(shadow_surf, shadow_rect)

        title_surf = self.font_large.render("Choose Your Pet", True, COLOR_TITLE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
        surface.blit(title_surf, title_rect)

        # Pet preview cards
        cat_cx = SCREEN_WIDTH // 2 - 110
        dog_cx = SCREEN_WIDTH // 2 + 110
        card_y = 140
        card_w = 170
        card_h = 220

        for card_cx, pet_type, label in [(cat_cx, "cat", "Cat"),
                                          (dog_cx, "dog", "Dog")]:
            # Card background (semi-transparent rounded rect)
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            pygame.draw.rect(card_surf, (40, 35, 65, 160),
                             (0, 0, card_w, card_h), border_radius=16)
            # Lighter border
            pygame.draw.rect(card_surf, (80, 70, 120, 120),
                             (0, 0, card_w, card_h), 2, border_radius=16)
            surface.blit(card_surf, (card_cx - card_w // 2, card_y))

            # Pet preview inside card
            pet_y = card_y + card_h // 2 - 10
            _draw_outline_pet(surface, card_cx, pet_y, pet_type, 0.8, time_val)

            # Label below card
            lbl_surf = self.font_medium.render(label, True, WHITE)
            lbl_rect = lbl_surf.get_rect(center=(card_cx, card_y + card_h + 12))
            surface.blit(lbl_surf, lbl_rect)

        # Buttons
        self.cat_button.update(mouse_pos)
        self.dog_button.update(mouse_pos)
        self.cat_button.draw(surface, self.font_large)
        self.dog_button.draw(surface, self.font_large)

    def draw_ran_away(self, surface, pet, time_val):
        """Draw the pet ran away screen with somber gradient, sad pet, and rain."""
        # Dark reddish-brown gradient
        _draw_gradient(surface, (50, 20, 25), (30, 15, 20),
                       (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Subtle diagonal rain lines (single surface for all rain)
        import random as _rng
        rain_rng = _rng.Random(7)
        rain_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(60):
            rx = rain_rng.randint(0, SCREEN_WIDTH + 40)
            ry_base = rain_rng.randint(0, SCREEN_HEIGHT)
            rain_speed = rain_rng.uniform(120, 200)
            rain_len = rain_rng.randint(10, 25)
            ry = (ry_base + time_val * rain_speed) % (SCREEN_HEIGHT + 40) - 20
            rain_alpha = rain_rng.randint(30, 70)
            start = (int(rx), int(ry))
            end = (int(rx - 8), int(ry + rain_len))
            pygame.draw.line(rain_surf, (180, 200, 220, rain_alpha),
                             start, end, 1)
        surface.blit(rain_surf, (0, 0))

        # Title with shadow and wobble
        wobble = math.sin(time_val * 3) * 2
        title_y = 130 + wobble
        # Shadow
        ran_title = f"{pet.name} ran away..."
        shadow_surf = self.font_large.render(ran_title, True, BLACK)
        shadow_rect = shadow_surf.get_rect(center=(SCREEN_WIDTH // 2 + 2,
                                                    title_y + 2))
        surface.blit(shadow_surf, shadow_rect)
        # Main title
        title_surf = self.font_large.render(ran_title, True,
                                             (220, 140, 140))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, title_y))
        surface.blit(title_surf, title_rect)

        # Message
        msg = f"{pet.name} left after {pet.day_count} day{'s' if pet.day_count != 1 else ''}."
        msg_surf = self.font_medium.render(msg, True, LIGHT_GRAY)
        msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, 200))
        surface.blit(msg_surf, msg_rect)

        tip_surf = self.font_small.render("Remember to keep all stats above 15!",
                                           True, (180, 180, 200))
        tip_rect = tip_surf.get_rect(center=(SCREEN_WIDTH // 2, 240))
        surface.blit(tip_surf, tip_rect)

        # Sad pet silhouette matching pet type
        _draw_sad_pet(surface, SCREEN_WIDTH // 2, 370, pet.pet_type, 1.0)

        # Restart prompt (blinking)
        if int(time_val * 2) % 2 == 0:
            restart_surf = self.font_medium.render("Press SPACE to try again",
                                                    True, WHITE)
            restart_rect = restart_surf.get_rect(center=(SCREEN_WIDTH // 2, 500))
            surface.blit(restart_surf, restart_rect)
