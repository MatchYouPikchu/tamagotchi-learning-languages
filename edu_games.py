"""Educational mini-games: PlayMenu + 4 Polish-English learning games.

All classes follow the sub-state interface used by main.py:
    handle_event(event, mouse_pos), update(dt), draw(surface, mouse_pos),
    .done, .result
"""

import math
import random
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, OUTLINE_WIDTH,
    OVERLAY_ALPHA, OVERLAY_TITLE_COLOR, OVERLAY_SCORE_COLOR,
    OVERLAY_TIMER_BG, OVERLAY_TIMER_FG,
    FOOD_MENU_BG, FOOD_MENU_BORDER, FOOD_MENU_HOVER, FOOD_MENU_TEXT,
    MINIGAME_RESULTS_DURATION,
    EDU_GAME_BASE_HAPPINESS, EDU_GAME_PER_SCORE, EDU_GAME_HAPPINESS_CAP,
    XP_PER_CORRECT, XP_BONUS_PERFECT,
    PLAY_MENU_WIDTH, PLAY_MENU_HEIGHT, PLAY_MENU_ROW_HEIGHT,
    MEMORY_PAIRS, MEMORY_CARD_W, MEMORY_CARD_H, MEMORY_CARD_SPACING,
    MEMORY_CARD_BACK, MEMORY_CARD_MATCHED, MEMORY_MISMATCH_DELAY,
    MEMORY_DURATION, MEMORY_PEEK_DURATION,
    FALLING_WORD_DURATION, FALLING_WORD_ROUNDS, FALLING_WORD_SPEED,
    FALLING_WORD_PILL_W, FALLING_WORD_PILL_H,
    SPELLING_DURATION, SPELLING_WORD_COUNT, SPELLING_TILE_SIZE,
    SPELLING_TILE_COLOR, SPELLING_TILE_CORRECT, SPELLING_HINT_DELAY,
    QUIZ_DURATION, QUIZ_QUESTION_COUNT,
    QUIZ_BUTTON_W, QUIZ_BUTTON_H, QUIZ_BUTTON_COLOR, QUIZ_BUTTON_HOVER,
    QUIZ_CORRECT_COLOR, QUIZ_WRONG_COLOR,
    MEMORY_PAIRS_BY_DIFF, FALLING_ROUNDS_BY_DIFF, FALLING_SPEED_BY_DIFF,
    SPELLING_COUNT_BY_DIFF, QUIZ_COUNT_BY_DIFF, QUIZ_OPTIONS_BY_DIFF,
    WORDBOOK_CARD_H, WORDBOOK_CARD_W, WORDBOOK_CARD_GAP,
    WORDBOOK_HEADER_H, WORDBOOK_TAB_H, WORDBOOK_SCROLL_IMPULSE,
    WORDBOOK_STAR_SIZE, WORDBOOK_MASTERED_COLOR, WORDBOOK_LEARNING_COLOR,
    WORDBOOK_NEW_COLOR, TIER_UNLOCK_THRESHOLD,
)
from vocabulary import (get_random_words, get_distractors, get_smart_words,
                        get_unlocked_tier)

def _get_difficulty(level):
    """Return difficulty index 0=easy, 1=medium, 2=hard based on pet level."""
    if level <= 3:
        return 0
    elif level <= 6:
        return 1
    return 2


# Play area bounds (same as minigames.py)
PLAY_TOP = 100
PLAY_BOTTOM = 460


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _draw_overlay_bg(surface):
    """Solid dark background — no room bleed-through."""
    surface.fill((20, 18, 30))


def _draw_vocab_icon(surface, cx, cy, icon_hint, size=20):
    """Draw a procedural shape based on icon_hint = (shape, color)."""
    shape, color = icon_hint
    o = 2  # outline thickness

    # ------------------------------------------------------------------
    # Original basic shapes (used by PlayMenu + color words)
    # ------------------------------------------------------------------
    if shape == "circle":
        pygame.draw.circle(surface, BLACK, (cx, cy), size + o)
        pygame.draw.circle(surface, color, (cx, cy), size)
    elif shape == "rect":
        r = pygame.Rect(cx - size, cy - int(size * 0.7),
                        size * 2, int(size * 1.4))
        pygame.draw.rect(surface, BLACK, r.inflate(4, 4), border_radius=4)
        pygame.draw.rect(surface, color, r, border_radius=3)
    elif shape == "triangle":
        pts = [
            (cx, cy - size),
            (cx - size, cy + int(size * 0.7)),
            (cx + size, cy + int(size * 0.7)),
        ]
        outer = []
        ecx = sum(p[0] for p in pts) / 3
        ecy = sum(p[1] for p in pts) / 3
        for px, py in pts:
            dx, dy = px - ecx, py - ecy
            d = max(0.01, math.hypot(dx, dy))
            outer.append((px + dx / d * 2, py + dy / d * 2))
        pygame.draw.polygon(surface, BLACK, outer)
        pygame.draw.polygon(surface, color, pts)
    elif shape == "ellipse":
        r = pygame.Rect(cx - size, cy - int(size * 0.6),
                        size * 2, int(size * 1.2))
        pygame.draw.ellipse(surface, BLACK, r.inflate(4, 4))
        pygame.draw.ellipse(surface, color, r)
    elif shape == "drop":
        pygame.draw.circle(surface, BLACK, (cx, cy + 2), size + o)
        pygame.draw.circle(surface, color, (cx, cy + 2), size)
        pygame.draw.polygon(surface, BLACK, [
            (cx - size - o, cy + 2), (cx + size + o, cy + 2),
            (cx, cy - int(size * 1.4) - o),
        ])
        pygame.draw.polygon(surface, color, [
            (cx - size, cy + 2), (cx + size, cy + 2),
            (cx, cy - int(size * 1.4)),
        ])
    elif shape == "heart":
        hr = size // 2
        pygame.draw.circle(surface, BLACK, (cx - hr, cy - hr // 2), hr + o)
        pygame.draw.circle(surface, BLACK, (cx + hr, cy - hr // 2), hr + o)
        pygame.draw.polygon(surface, BLACK, [
            (cx - size - o, cy), (cx + size + o, cy),
            (cx, cy + size + o),
        ])
        pygame.draw.circle(surface, color, (cx - hr, cy - hr // 2), hr)
        pygame.draw.circle(surface, color, (cx + hr, cy - hr // 2), hr)
        pygame.draw.polygon(surface, color, [
            (cx - size, cy), (cx + size, cy),
            (cx, cy + size),
        ])
    elif shape == "star":
        pts = []
        for i in range(10):
            angle = i * math.pi / 5 - math.pi / 2
            r = size if i % 2 == 0 else size * 0.4
            pts.append((cx + math.cos(angle) * r,
                        cy + math.sin(angle) * r))
        outer = []
        scx = sum(p[0] for p in pts) / len(pts)
        scy = sum(p[1] for p in pts) / len(pts)
        for px, py in pts:
            dx, dy = px - scx, py - scy
            d = max(0.01, math.hypot(dx, dy))
            outer.append((px + dx / d * 2, py + dy / d * 2))
        pygame.draw.polygon(surface, BLACK, outer)
        pygame.draw.polygon(surface, color, pts)

    # ------------------------------------------------------------------
    # Animals
    # ------------------------------------------------------------------
    elif shape == "cat_face":
        # Round head
        pygame.draw.circle(surface, BLACK, (cx, cy), size + o)
        pygame.draw.circle(surface, color, (cx, cy), size)
        # Triangle ears
        ear_w = int(size * 0.4)
        ear_h = int(size * 0.6)
        for sx in (-1, 1):
            ex = cx + sx * int(size * 0.55)
            ey = cy - int(size * 0.6)
            pts = [(ex, ey - ear_h), (ex - ear_w * sx, ey + 2), (ex + ear_w * sx * 0.2, ey + 2)]
            pygame.draw.polygon(surface, BLACK, pts)
            inner = [(ex, ey - ear_h + 3), (ex - ear_w * sx + sx * 2, ey), (ex + ear_w * sx * 0.2 - sx, ey)]
            pygame.draw.polygon(surface, color, inner)
        # Eyes
        ed = int(size * 0.3)
        es = max(2, int(size * 0.12))
        pygame.draw.circle(surface, BLACK, (cx - ed, cy - int(size * 0.1)), es)
        pygame.draw.circle(surface, BLACK, (cx + ed, cy - int(size * 0.1)), es)
        # Tiny nose
        ns = max(1, int(size * 0.08))
        pygame.draw.circle(surface, (220, 140, 140), (cx, cy + int(size * 0.15)), ns)
        # Whiskers
        wl = int(size * 0.5)
        wy = cy + int(size * 0.25)
        for sx in (-1, 1):
            wx = cx + sx * int(size * 0.15)
            pygame.draw.line(surface, BLACK, (wx, wy - 2), (wx + sx * wl, wy - int(size * 0.15)), 1)
            pygame.draw.line(surface, BLACK, (wx, wy), (wx + sx * wl, wy + 2), 1)

    elif shape == "dog_face":
        # Round head
        pygame.draw.circle(surface, BLACK, (cx, cy), size + o)
        pygame.draw.circle(surface, color, (cx, cy), size)
        # Floppy ears
        ear_w = int(size * 0.35)
        ear_h = int(size * 0.7)
        for sx in (-1, 1):
            ex = cx + sx * int(size * 0.7)
            ey = cy + int(size * 0.1)
            er = pygame.Rect(ex - ear_w, ey - int(ear_h * 0.3), ear_w * 2, ear_h)
            darker = (max(0, color[0] - 40), max(0, color[1] - 40), max(0, color[2] - 30))
            pygame.draw.ellipse(surface, BLACK, er.inflate(4, 4))
            pygame.draw.ellipse(surface, darker, er)
        # Eyes
        ed = int(size * 0.28)
        es = max(2, int(size * 0.13))
        pygame.draw.circle(surface, BLACK, (cx - ed, cy - int(size * 0.15)), es)
        pygame.draw.circle(surface, BLACK, (cx + ed, cy - int(size * 0.15)), es)
        # Round nose
        ns = max(2, int(size * 0.14))
        pygame.draw.circle(surface, BLACK, (cx, cy + int(size * 0.15)), ns)
        # Tongue
        tw = max(2, int(size * 0.15))
        th = int(size * 0.3)
        tr = pygame.Rect(cx - tw, cy + int(size * 0.35), tw * 2, th)
        pygame.draw.ellipse(surface, (220, 100, 100), tr)

    elif shape == "fish_icon":
        # Ellipse body
        bw = size
        bh = int(size * 0.6)
        br = pygame.Rect(cx - bw, cy - bh, bw * 2, bh * 2)
        pygame.draw.ellipse(surface, BLACK, br.inflate(4, 4))
        pygame.draw.ellipse(surface, color, br)
        # V-shaped tail
        tx = cx + size
        ts = int(size * 0.5)
        pygame.draw.polygon(surface, BLACK, [
            (tx - 2, cy), (tx + ts + 2, cy - ts - 1), (tx + ts + 2, cy + ts + 1)])
        pygame.draw.polygon(surface, color, [
            (tx, cy), (tx + ts, cy - ts), (tx + ts, cy + ts)])
        # Eye
        es = max(2, int(size * 0.12))
        pygame.draw.circle(surface, WHITE, (cx - int(size * 0.35), cy - int(size * 0.1)), es + 1)
        pygame.draw.circle(surface, BLACK, (cx - int(size * 0.35), cy - int(size * 0.1)), es)

    elif shape == "bird_icon":
        # Ellipse body
        bw = size
        bh = int(size * 0.55)
        br = pygame.Rect(cx - bw, cy - bh, bw * 2, bh * 2)
        pygame.draw.ellipse(surface, BLACK, br.inflate(4, 4))
        pygame.draw.ellipse(surface, color, br)
        # Triangle beak
        bk_x = cx - size - int(size * 0.15)
        bk_s = int(size * 0.35)
        pygame.draw.polygon(surface, (240, 180, 60), [
            (bk_x, cy), (bk_x - bk_s, cy - bk_s // 3), (bk_x - bk_s, cy + bk_s // 3)])
        # Wing arc
        wr = pygame.Rect(cx - int(size * 0.3), cy - int(size * 0.4),
                         int(size * 1.2), int(size * 0.8))
        darker = (max(0, color[0] - 30), max(0, color[1] - 30), max(0, color[2] - 20))
        pygame.draw.ellipse(surface, darker, wr)
        # Eye
        es = max(2, int(size * 0.1))
        pygame.draw.circle(surface, BLACK, (cx - int(size * 0.45), cy - int(size * 0.12)), es)

    # ------------------------------------------------------------------
    # Food
    # ------------------------------------------------------------------
    elif shape == "apple_icon":
        # Main body
        pygame.draw.circle(surface, BLACK, (cx, cy + 2), size + o)
        pygame.draw.circle(surface, color, (cx, cy + 2), size)
        # Stem
        sw = max(2, int(size * 0.1))
        sh = int(size * 0.4)
        sr = pygame.Rect(cx - sw, cy - size - sh + 2, sw * 2, sh)
        pygame.draw.rect(surface, (120, 80, 40), sr)
        # Leaf
        lw = int(size * 0.4)
        lh = int(size * 0.25)
        lr = pygame.Rect(cx + 1, cy - size - sh + 4, lw, lh)
        pygame.draw.ellipse(surface, (80, 180, 60), lr)

    elif shape == "bottle":
        # Body rectangle
        bw = int(size * 0.6)
        bh = int(size * 1.4)
        by = cy - int(bh * 0.3)
        br = pygame.Rect(cx - bw, by, bw * 2, bh)
        pygame.draw.rect(surface, BLACK, br.inflate(4, 4), border_radius=4)
        pygame.draw.rect(surface, color, br, border_radius=3)
        # Cap on top
        cw = int(size * 0.35)
        ch = int(size * 0.35)
        cr = pygame.Rect(cx - cw, by - ch, cw * 2, ch)
        pygame.draw.rect(surface, BLACK, cr.inflate(4, 2), border_radius=2)
        pygame.draw.rect(surface, (200, 200, 210), cr, border_radius=2)

    elif shape == "cake_icon":
        # Body
        bw = size
        bh = int(size * 0.9)
        by = cy - int(bh * 0.2)
        br = pygame.Rect(cx - bw, by, bw * 2, bh)
        pygame.draw.rect(surface, BLACK, br.inflate(4, 4), border_radius=4)
        pygame.draw.rect(surface, color, br, border_radius=3)
        # Frosting layer on top
        fr = pygame.Rect(cx - bw, by - int(size * 0.2), bw * 2, int(size * 0.35))
        pygame.draw.rect(surface, BLACK, fr.inflate(4, 2), border_radius=6)
        pygame.draw.rect(surface, (255, 230, 240), fr, border_radius=5)
        # Cherry
        cherry_r = max(2, int(size * 0.15))
        pygame.draw.circle(surface, BLACK, (cx, by - int(size * 0.2) - cherry_r), cherry_r + 1)
        pygame.draw.circle(surface, (220, 40, 60), (cx, by - int(size * 0.2) - cherry_r), cherry_r)

    elif shape == "loaf":
        # Dome-topped rectangle
        bw = size
        bh = int(size * 0.7)
        by = cy
        br = pygame.Rect(cx - bw, by, bw * 2, bh)
        # Dome
        dr = pygame.Rect(cx - bw, by - int(size * 0.5), bw * 2, int(size * 0.9))
        pygame.draw.ellipse(surface, BLACK, dr.inflate(4, 4))
        pygame.draw.rect(surface, BLACK, br.inflate(4, 4), border_radius=3)
        pygame.draw.ellipse(surface, color, dr)
        pygame.draw.rect(surface, color, br, border_radius=2)
        # Score line on top
        pygame.draw.line(surface, (max(0, color[0] - 30), max(0, color[1] - 30), max(0, color[2] - 20)),
                         (cx - int(bw * 0.5), by - int(size * 0.15)),
                         (cx + int(bw * 0.5), by - int(size * 0.15)), max(1, o - 1))

    # ------------------------------------------------------------------
    # Faces / Feelings
    # ------------------------------------------------------------------
    elif shape == "smiley":
        # Face circle
        pygame.draw.circle(surface, BLACK, (cx, cy), size + o)
        pygame.draw.circle(surface, color, (cx, cy), size)
        # Eyes
        ed = int(size * 0.3)
        es = max(2, int(size * 0.12))
        pygame.draw.circle(surface, BLACK, (cx - ed, cy - int(size * 0.2)), es)
        pygame.draw.circle(surface, BLACK, (cx + ed, cy - int(size * 0.2)), es)
        # Smile arc
        arc_r = pygame.Rect(cx - int(size * 0.45), cy - int(size * 0.15),
                            int(size * 0.9), int(size * 0.7))
        pygame.draw.arc(surface, BLACK, arc_r, math.pi + 0.3, 2 * math.pi - 0.3, max(2, o))

    elif shape == "frowny":
        # Face circle
        pygame.draw.circle(surface, BLACK, (cx, cy), size + o)
        pygame.draw.circle(surface, color, (cx, cy), size)
        # Eyes
        ed = int(size * 0.3)
        es = max(2, int(size * 0.12))
        pygame.draw.circle(surface, BLACK, (cx - ed, cy - int(size * 0.2)), es)
        pygame.draw.circle(surface, BLACK, (cx + ed, cy - int(size * 0.2)), es)
        # Frown arc
        arc_r = pygame.Rect(cx - int(size * 0.4), cy + int(size * 0.1),
                            int(size * 0.8), int(size * 0.55))
        pygame.draw.arc(surface, BLACK, arc_r, 0.3, math.pi - 0.3, max(2, o))
        # Teardrop
        td = max(2, int(size * 0.08))
        tx = cx + ed + 2
        ty = cy - int(size * 0.05)
        pygame.draw.circle(surface, (100, 160, 240), (tx, ty + td * 2), td)
        pygame.draw.polygon(surface, (100, 160, 240), [
            (tx - td, ty + td * 2), (tx + td, ty + td * 2), (tx, ty)])

    elif shape == "sleepy":
        # Face circle
        pygame.draw.circle(surface, BLACK, (cx, cy), size + o)
        pygame.draw.circle(surface, color, (cx, cy), size)
        # Closed eyes (horizontal lines)
        ed = int(size * 0.3)
        ew = int(size * 0.2)
        ey = cy - int(size * 0.15)
        pygame.draw.line(surface, BLACK, (cx - ed - ew, ey), (cx - ed + ew, ey), max(2, o))
        pygame.draw.line(surface, BLACK, (cx + ed - ew, ey), (cx + ed + ew, ey), max(2, o))
        # Sleepy mouth (small 'o')
        mr = max(2, int(size * 0.1))
        pygame.draw.circle(surface, BLACK, (cx, cy + int(size * 0.3)), mr, max(1, o - 1))
        # "z" text
        fsize = max(8, int(size * 0.5))
        font_z = pygame.font.SysFont("Arial", fsize, bold=True)
        z1 = font_z.render("z", True, (200, 200, 255))
        surface.blit(z1, (cx + int(size * 0.5), cy - int(size * 0.7)))
        fsize2 = max(6, int(size * 0.35))
        font_z2 = pygame.font.SysFont("Arial", fsize2, bold=True)
        z2 = font_z2.render("z", True, (180, 180, 240))
        surface.blit(z2, (cx + int(size * 0.75), cy - int(size * 0.95)))

    elif shape == "head_icon":
        # Face circle
        pygame.draw.circle(surface, BLACK, (cx, cy), size + o)
        pygame.draw.circle(surface, color, (cx, cy), size)
        # Eyes
        ed = int(size * 0.28)
        es = max(2, int(size * 0.1))
        pygame.draw.circle(surface, BLACK, (cx - ed, cy - int(size * 0.15)), es)
        pygame.draw.circle(surface, BLACK, (cx + ed, cy - int(size * 0.15)), es)
        # Nose line
        nl = int(size * 0.2)
        pygame.draw.line(surface, BLACK, (cx, cy), (cx, cy + nl), max(1, o - 1))
        # Mouth line
        mw = int(size * 0.25)
        my = cy + int(size * 0.35)
        pygame.draw.line(surface, BLACK, (cx - mw, my), (cx + mw, my), max(1, o - 1))

    elif shape == "eye_icon":
        # Almond outer shape
        ew = size
        eh = int(size * 0.55)
        pts = [
            (cx - ew, cy),
            (cx, cy - eh),
            (cx + ew, cy),
            (cx, cy + eh),
        ]
        pygame.draw.polygon(surface, BLACK,
                            [(p[0], p[1]) for p in pts])
        # Slightly smaller white
        ew2 = ew - 2
        eh2 = eh - 2
        pts2 = [(cx - ew2, cy), (cx, cy - eh2), (cx + ew2, cy), (cx, cy + eh2)]
        pygame.draw.polygon(surface, (240, 240, 245), pts2)
        # Iris
        ir = int(size * 0.35)
        pygame.draw.circle(surface, color, (cx, cy), ir)
        # Pupil
        pr = int(size * 0.18)
        pygame.draw.circle(surface, BLACK, (cx, cy), pr)
        # Highlight
        hr = max(1, int(size * 0.08))
        pygame.draw.circle(surface, WHITE, (cx - int(size * 0.1), cy - int(size * 0.1)), hr)

    elif shape == "hand_icon":
        # Palm
        pw = int(size * 0.7)
        ph = int(size * 0.8)
        py_top = cy - int(ph * 0.2)
        pr = pygame.Rect(cx - pw // 2, py_top, pw, ph)
        pygame.draw.rect(surface, BLACK, pr.inflate(4, 4), border_radius=4)
        pygame.draw.rect(surface, color, pr, border_radius=3)
        # 4 fingers
        fw = max(2, int(size * 0.13))
        fh = int(size * 0.5)
        gap = (pw - fw * 4) // 5
        for i in range(4):
            fx = pr.x + gap + i * (fw + gap)
            fr = pygame.Rect(fx, py_top - fh, fw, fh + 2)
            pygame.draw.rect(surface, BLACK, fr.inflate(2, 2), border_radius=3)
            pygame.draw.rect(surface, color, fr, border_radius=2)
        # Thumb
        tw = max(2, int(size * 0.15))
        th = int(size * 0.35)
        tr = pygame.Rect(pr.x - tw - 1, py_top + int(ph * 0.1), tw, th)
        pygame.draw.rect(surface, BLACK, tr.inflate(2, 2), border_radius=3)
        pygame.draw.rect(surface, color, tr, border_radius=2)

    # ------------------------------------------------------------------
    # Weather
    # ------------------------------------------------------------------
    elif shape == "sun_rays":
        # Rays (8 lines radiating)
        ray_len = size
        ray_inner = int(size * 0.55)
        for i in range(8):
            angle = i * math.pi / 4
            x1 = cx + int(math.cos(angle) * ray_inner)
            y1 = cy + int(math.sin(angle) * ray_inner)
            x2 = cx + int(math.cos(angle) * ray_len)
            y2 = cy + int(math.sin(angle) * ray_len)
            pygame.draw.line(surface, BLACK, (x1, y1), (x2, y2), max(3, o + 1))
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), max(2, o))
        # Center circle
        cr = int(size * 0.5)
        pygame.draw.circle(surface, BLACK, (cx, cy), cr + o)
        pygame.draw.circle(surface, color, (cx, cy), cr)

    elif shape == "cloud_rain":
        # Cloud: overlapping circles
        cr = int(size * 0.4)
        cloud_y = cy - int(size * 0.2)
        offsets = [(-int(size * 0.4), 0), (int(size * 0.4), 0), (0, -int(size * 0.25))]
        for dx, dy in offsets:
            pygame.draw.circle(surface, BLACK, (cx + dx, cloud_y + dy), cr + o)
        for dx, dy in offsets:
            pygame.draw.circle(surface, color, (cx + dx, cloud_y + dy), cr)
        # 3 rain drops below
        drop_r = max(2, int(size * 0.08))
        drop_y = cy + int(size * 0.45)
        for dx in (-int(size * 0.3), 0, int(size * 0.3)):
            pygame.draw.circle(surface, (80, 140, 230), (cx + dx, drop_y), drop_r)
            pygame.draw.polygon(surface, (80, 140, 230), [
                (cx + dx - drop_r, drop_y),
                (cx + dx + drop_r, drop_y),
                (cx + dx, drop_y - drop_r * 3),
            ])

    elif shape == "snowflake":
        # 3 crossed lines
        arm = int(size * 0.85)
        for i in range(3):
            angle = i * math.pi / 3
            x1 = cx + int(math.cos(angle) * arm)
            y1 = cy + int(math.sin(angle) * arm)
            x2 = cx - int(math.cos(angle) * arm)
            y2 = cy - int(math.sin(angle) * arm)
            pygame.draw.line(surface, BLACK, (x1, y1), (x2, y2), max(3, o + 1))
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), max(2, o))
            # Small angled branches at midpoints
            br_len = int(size * 0.25)
            for sign in (-1, 1):
                mx = cx + int(math.cos(angle) * arm * 0.5) * sign
                my = cy + int(math.sin(angle) * arm * 0.5) * sign
                for ba in (angle + math.pi / 4, angle - math.pi / 4):
                    bx = mx + int(math.cos(ba) * br_len * sign)
                    by = my + int(math.sin(ba) * br_len * sign)
                    pygame.draw.line(surface, color, (mx, my), (bx, by), max(1, o - 1))
        # Center dot
        pygame.draw.circle(surface, color, (cx, cy), max(2, int(size * 0.1)))

    elif shape == "wind_icon":
        # 3 wavy horizontal lines
        lw = max(2, o)
        for i, dy in enumerate((-int(size * 0.4), 0, int(size * 0.4))):
            pts = []
            line_w = size - i * int(size * 0.15)
            for x_step in range(20):
                t = x_step / 19.0
                px = cx - line_w + t * line_w * 2
                wave = math.sin(t * math.pi * 2 + i) * int(size * 0.15)
                pts.append((int(px), int(cy + dy + wave)))
            if len(pts) >= 2:
                pygame.draw.lines(surface, BLACK, False, pts, lw + 1)
                pygame.draw.lines(surface, color, False, pts, lw)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    elif shape == "running":
        # Stick figure in running pose
        lw = max(2, o)
        # Head
        hr = int(size * 0.2)
        hx = cx
        hy = cy - int(size * 0.6)
        pygame.draw.circle(surface, BLACK, (hx, hy), hr + 1)
        pygame.draw.circle(surface, color, (hx, hy), hr)
        # Body
        body_top = hy + hr
        body_bot = cy + int(size * 0.05)
        pygame.draw.line(surface, BLACK, (hx, body_top), (hx - int(size * 0.1), body_bot), lw + 1)
        pygame.draw.line(surface, color, (hx, body_top), (hx - int(size * 0.1), body_bot), lw)
        # Arms spread
        arm_y = body_top + int(size * 0.2)
        pygame.draw.line(surface, BLACK, (hx, arm_y), (hx + int(size * 0.5), arm_y - int(size * 0.3)), lw + 1)
        pygame.draw.line(surface, color, (hx, arm_y), (hx + int(size * 0.5), arm_y - int(size * 0.3)), lw)
        pygame.draw.line(surface, BLACK, (hx, arm_y), (hx - int(size * 0.45), arm_y + int(size * 0.15)), lw + 1)
        pygame.draw.line(surface, color, (hx, arm_y), (hx - int(size * 0.45), arm_y + int(size * 0.15)), lw)
        # Legs spread
        lx = hx - int(size * 0.1)
        pygame.draw.line(surface, BLACK, (lx, body_bot), (lx + int(size * 0.5), cy + int(size * 0.6)), lw + 1)
        pygame.draw.line(surface, color, (lx, body_bot), (lx + int(size * 0.5), cy + int(size * 0.6)), lw)
        pygame.draw.line(surface, BLACK, (lx, body_bot), (lx - int(size * 0.35), cy + int(size * 0.65)), lw + 1)
        pygame.draw.line(surface, color, (lx, body_bot), (lx - int(size * 0.35), cy + int(size * 0.65)), lw)

    elif shape == "fork":
        # Handle
        hw = max(2, int(size * 0.12))
        hh = int(size * 0.8)
        hy = cy + int(size * 0.15)
        hr = pygame.Rect(cx - hw, hy, hw * 2, hh)
        pygame.draw.rect(surface, BLACK, hr.inflate(3, 3), border_radius=2)
        pygame.draw.rect(surface, color, hr, border_radius=2)
        # Bridge
        bw = int(size * 0.45)
        bh = max(2, int(size * 0.1))
        br = pygame.Rect(cx - bw, hy - bh, bw * 2, bh)
        pygame.draw.rect(surface, BLACK, br.inflate(3, 3), border_radius=1)
        pygame.draw.rect(surface, color, br, border_radius=1)
        # 3 tines
        tw = max(1, int(size * 0.08))
        th = int(size * 0.55)
        for dx in (-int(size * 0.3), 0, int(size * 0.3)):
            tr = pygame.Rect(cx + dx - tw, hy - bh - th, tw * 2, th)
            pygame.draw.rect(surface, BLACK, tr.inflate(2, 2), border_radius=2)
            pygame.draw.rect(surface, color, tr, border_radius=1)

    elif shape == "moon":
        # Full circle
        pygame.draw.circle(surface, BLACK, (cx, cy), size + o)
        pygame.draw.circle(surface, color, (cx, cy), size)
        # Dark cutout circle to create crescent
        bg = (20, 18, 30)
        cut_offset = int(size * 0.4)
        pygame.draw.circle(surface, bg, (cx + cut_offset, cy - int(size * 0.15)), int(size * 0.8))
        # Tiny stars
        star_s = max(1, int(size * 0.06))
        for sx, sy in ((int(size * 0.6), -int(size * 0.6)),
                        (int(size * 0.8), int(size * 0.1)),
                        (int(size * 0.35), -int(size * 0.85))):
            pygame.draw.circle(surface, (240, 240, 200), (cx + sx, cy + sy), star_s)

    elif shape == "book":
        # Two adjacent rectangles (open book)
        hw = int(size * 0.8)
        bh = int(size * 1.2)
        by = cy - bh // 2
        # Left page
        lr = pygame.Rect(cx - hw, by, hw, bh)
        pygame.draw.rect(surface, BLACK, lr.inflate(3, 3), border_radius=2)
        pygame.draw.rect(surface, (245, 240, 230), lr, border_radius=2)
        # Right page
        rr = pygame.Rect(cx, by, hw, bh)
        pygame.draw.rect(surface, BLACK, rr.inflate(3, 3), border_radius=2)
        pygame.draw.rect(surface, (245, 240, 230), rr, border_radius=2)
        # Spine line
        pygame.draw.line(surface, color, (cx, by), (cx, by + bh), max(2, o))
        # Text lines on left page
        tl = max(1, o - 1)
        for i in range(3):
            ly = by + int(bh * 0.25) + i * int(bh * 0.2)
            pygame.draw.line(surface, (180, 170, 160),
                             (lr.x + 4, ly), (lr.right - 4, ly), tl)
        # Text lines on right page
        for i in range(3):
            ly = by + int(bh * 0.25) + i * int(bh * 0.2)
            pygame.draw.line(surface, (180, 170, 160),
                             (rr.x + 4, ly), (rr.right - 4, ly), tl)

    elif shape == "ball":
        # Circle with decorative arc
        pygame.draw.circle(surface, BLACK, (cx, cy), size + o)
        pygame.draw.circle(surface, color, (cx, cy), size)
        # Curved stripe pattern
        arc_r1 = pygame.Rect(cx - int(size * 0.8), cy - size, int(size * 1.6), size * 2)
        lighter = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
        pygame.draw.arc(surface, lighter, arc_r1, 0.5, 2.5, max(2, o))
        pygame.draw.arc(surface, lighter,
                        pygame.Rect(cx - int(size * 0.3), cy - size, int(size * 0.6), size * 2),
                        -0.5, 1.5, max(2, o))

    elif shape == "plate":
        # Flat ellipse plate
        pw = size
        ph = int(size * 0.45)
        pr = pygame.Rect(cx - pw, cy - ph + int(size * 0.15), pw * 2, ph * 2)
        pygame.draw.ellipse(surface, BLACK, pr.inflate(4, 4))
        pygame.draw.ellipse(surface, color, pr)
        # Inner ring
        inner = pr.inflate(-int(size * 0.5), -int(size * 0.3))
        pygame.draw.ellipse(surface, (min(255, color[0] + 25), min(255, color[1] + 25),
                                       min(255, color[2] + 25)), inner)
        # Small fork beside plate
        fk_x = cx + size + int(size * 0.3)
        fk_h = int(size * 0.8)
        fk_w = max(1, int(size * 0.06))
        pygame.draw.line(surface, (180, 180, 190), (fk_x, cy - fk_h // 2), (fk_x, cy + fk_h // 2), fk_w + 1)
        for dy in (-fk_h // 2, -fk_h // 2 + int(fk_h * 0.15)):
            pygame.draw.line(surface, (180, 180, 190),
                             (fk_x - int(size * 0.1), cy + dy),
                             (fk_x + int(size * 0.1), cy + dy), max(1, fk_w))

    # ------------------------------------------------------------------
    # Animals (new icons)
    # ------------------------------------------------------------------
    elif shape == "horse_face":
        # Round head
        pygame.draw.circle(surface, BLACK, (cx, cy), size + o)
        pygame.draw.circle(surface, color, (cx, cy), size)
        # Pointed ears
        ear_h = int(size * 0.5)
        ear_w = int(size * 0.2)
        for sx in (-1, 1):
            ex = cx + sx * int(size * 0.4)
            ey = cy - size + int(size * 0.15)
            pts = [(ex, ey - ear_h), (ex - ear_w, ey), (ex + ear_w, ey)]
            pygame.draw.polygon(surface, BLACK, pts)
            inner = [(ex, ey - ear_h + 2), (ex - ear_w + 1, ey - 1), (ex + ear_w - 1, ey - 1)]
            pygame.draw.polygon(surface, color, inner)
        # Nostrils
        nr = max(2, int(size * 0.1))
        ny = cy + int(size * 0.35)
        pygame.draw.circle(surface, BLACK, (cx - int(size * 0.18), ny), nr)
        pygame.draw.circle(surface, BLACK, (cx + int(size * 0.18), ny), nr)
        # Eyes
        es = max(2, int(size * 0.1))
        pygame.draw.circle(surface, BLACK, (cx - int(size * 0.3), cy - int(size * 0.15)), es)
        pygame.draw.circle(surface, BLACK, (cx + int(size * 0.3), cy - int(size * 0.15)), es)
        # Mane lines on top
        mane_color = (max(0, color[0] - 50), max(0, color[1] - 40), max(0, color[2] - 30))
        for i in range(3):
            mx = cx - int(size * 0.15) + i * int(size * 0.15)
            pygame.draw.line(surface, mane_color,
                             (mx, cy - size - int(size * 0.1)),
                             (mx + int(size * 0.1), cy - size + int(size * 0.2)), max(2, o))

    elif shape == "mouse_face":
        # Round head
        pygame.draw.circle(surface, BLACK, (cx, cy), size + o)
        pygame.draw.circle(surface, color, (cx, cy), size)
        # Large round ears
        ear_r = int(size * 0.45)
        for sx in (-1, 1):
            ex = cx + sx * int(size * 0.65)
            ey = cy - int(size * 0.4)
            pygame.draw.circle(surface, BLACK, (ex, ey), ear_r + o)
            pygame.draw.circle(surface, color, (ex, ey), ear_r)
            # Inner ear pink
            pygame.draw.circle(surface, (240, 180, 190), (ex, ey), int(ear_r * 0.6))
        # Tiny dot eyes
        es = max(2, int(size * 0.1))
        pygame.draw.circle(surface, BLACK, (cx - int(size * 0.25), cy - int(size * 0.1)), es)
        pygame.draw.circle(surface, BLACK, (cx + int(size * 0.25), cy - int(size * 0.1)), es)
        # Pink nose
        ns = max(2, int(size * 0.12))
        pygame.draw.circle(surface, (240, 140, 160), (cx, cy + int(size * 0.15)), ns)
        # Whiskers
        wl = int(size * 0.55)
        wy = cy + int(size * 0.25)
        for sx in (-1, 1):
            wx = cx + sx * int(size * 0.15)
            pygame.draw.line(surface, BLACK, (wx, wy - 3), (wx + sx * wl, wy - int(size * 0.15)), 1)
            pygame.draw.line(surface, BLACK, (wx, wy), (wx + sx * wl, wy + 2), 1)

    elif shape == "frog_face":
        # Wide flat ellipse head
        hw = int(size * 1.1)
        hh = int(size * 0.7)
        hr = pygame.Rect(cx - hw, cy - hh, hw * 2, hh * 2)
        pygame.draw.ellipse(surface, BLACK, hr.inflate(4, 4))
        pygame.draw.ellipse(surface, color, hr)
        # Bulging eyes on top
        eye_r = int(size * 0.3)
        for sx in (-1, 1):
            ex = cx + sx * int(size * 0.5)
            ey = cy - int(size * 0.55)
            pygame.draw.circle(surface, BLACK, (ex, ey), eye_r + o)
            pygame.draw.circle(surface, WHITE, (ex, ey), eye_r)
            # Pupil
            pr = max(2, int(eye_r * 0.5))
            pygame.draw.circle(surface, BLACK, (ex, ey), pr)
        # Wide smile arc
        arc_r = pygame.Rect(cx - int(size * 0.6), cy - int(size * 0.15),
                            int(size * 1.2), int(size * 0.7))
        pygame.draw.arc(surface, BLACK, arc_r, math.pi + 0.2, 2 * math.pi - 0.2, max(2, o))

    # ------------------------------------------------------------------
    # Body (new icons)
    # ------------------------------------------------------------------
    elif shape == "nose_icon":
        # Rounded teardrop shape pointing down
        nr = int(size * 0.6)
        # Bottom circle
        pygame.draw.circle(surface, BLACK, (cx, cy + int(size * 0.2)), nr + o)
        pygame.draw.circle(surface, color, (cx, cy + int(size * 0.2)), nr)
        # Triangular top leading to bridge
        pygame.draw.polygon(surface, BLACK, [
            (cx - nr - o, cy + int(size * 0.2)),
            (cx + nr + o, cy + int(size * 0.2)),
            (cx, cy - int(size * 0.7) - o),
        ])
        pygame.draw.polygon(surface, color, [
            (cx - nr, cy + int(size * 0.2)),
            (cx + nr, cy + int(size * 0.2)),
            (cx, cy - int(size * 0.7)),
        ])
        # Two nostril dots
        nd = max(2, int(size * 0.12))
        ny = cy + int(size * 0.3)
        pygame.draw.circle(surface, BLACK, (cx - int(size * 0.2), ny), nd)
        pygame.draw.circle(surface, BLACK, (cx + int(size * 0.2), ny), nd)

    elif shape == "ear_icon":
        # C-shaped outer curve (thick arc)
        ear_w = int(size * 1.2)
        ear_h = int(size * 1.6)
        ear_r = pygame.Rect(cx - ear_w // 2, cy - ear_h // 2, ear_w, ear_h)
        pygame.draw.arc(surface, BLACK, ear_r.inflate(4, 4), -0.8, math.pi + 0.8, max(4, o + 2))
        pygame.draw.arc(surface, color, ear_r, -0.8, math.pi + 0.8, max(3, o + 1))
        # Inner canal spiral line
        inner_w = int(size * 0.6)
        inner_h = int(size * 0.9)
        inner_r = pygame.Rect(cx - inner_w // 2, cy - inner_h // 2 + int(size * 0.05),
                              inner_w, inner_h)
        darker = (max(0, color[0] - 40), max(0, color[1] - 40), max(0, color[2] - 30))
        pygame.draw.arc(surface, darker, inner_r, -0.3, math.pi + 0.3, max(2, o))

    # ------------------------------------------------------------------
    # Nature (new icons)
    # ------------------------------------------------------------------
    elif shape == "tree_icon":
        # Brown rectangle trunk
        tw = int(size * 0.3)
        th = int(size * 0.8)
        tr = pygame.Rect(cx - tw // 2, cy + int(size * 0.1), tw, th)
        pygame.draw.rect(surface, BLACK, tr.inflate(4, 4), border_radius=2)
        pygame.draw.rect(surface, (120, 80, 40), tr, border_radius=2)
        # Green filled circle canopy
        canopy_r = int(size * 0.8)
        canopy_y = cy - int(size * 0.25)
        pygame.draw.circle(surface, BLACK, (cx, canopy_y), canopy_r + o)
        pygame.draw.circle(surface, color, (cx, canopy_y), canopy_r)

    elif shape == "forest_icon":
        # 3 overlapping triangle trees at different heights
        tree_color = color
        dark_green = (max(0, color[0] - 20), max(0, color[1] - 30), max(0, color[2] - 15))
        trunk_color = (100, 70, 35)
        # Tree positions: (x_offset, height_factor, tree_size)
        trees = [
            (-int(size * 0.45), 0.9, 0.7),   # left, shorter
            (int(size * 0.45), 0.85, 0.65),   # right, shortest
            (0, 1.0, 0.85),                     # center, tallest (drawn last = on top)
        ]
        for tx_off, h_factor, t_sz in trees:
            t_cx = cx + tx_off
            t_h = int(size * 1.3 * h_factor)
            t_w = int(size * t_sz)
            t_top = cy - int(size * 0.5) - int(t_h * 0.4)
            t_bot = cy + int(size * 0.4)
            # Trunk
            tkw = max(2, int(size * 0.1))
            tkr = pygame.Rect(t_cx - tkw, t_bot - int(size * 0.3), tkw * 2, int(size * 0.35))
            pygame.draw.rect(surface, trunk_color, tkr)
            # Triangle tree
            pts = [(t_cx, t_top), (t_cx - t_w, t_bot), (t_cx + t_w, t_bot)]
            pts_outer = [(t_cx, t_top - 2), (t_cx - t_w - 2, t_bot + 1), (t_cx + t_w + 2, t_bot + 1)]
            pygame.draw.polygon(surface, BLACK, pts_outer)
            tc = dark_green if tx_off != 0 else tree_color
            pygame.draw.polygon(surface, tc, pts)

    # ------------------------------------------------------------------
    # Adjectives (new icons)
    # ------------------------------------------------------------------
    elif shape == "big_icon":
        # Large filled circle + small circle beside it for scale
        big_r = int(size * 0.75)
        small_r = int(size * 0.3)
        # Big circle (left-center)
        bx = cx - int(size * 0.2)
        pygame.draw.circle(surface, BLACK, (bx, cy), big_r + o)
        pygame.draw.circle(surface, color, (bx, cy), big_r)
        # Small circle (right)
        sx = cx + int(size * 0.7)
        sy = cy + int(size * 0.3)
        pygame.draw.circle(surface, BLACK, (sx, sy), small_r + o)
        pygame.draw.circle(surface, (min(255, color[0] + 40), min(255, color[1] + 40),
                                      min(255, color[2] + 40)), (sx, sy), small_r)

    elif shape == "small_icon":
        # Small filled circle + large outlined circle beside it
        small_r = int(size * 0.3)
        big_r = int(size * 0.7)
        # Large outlined circle (left-center)
        bx = cx - int(size * 0.15)
        pygame.draw.circle(surface, BLACK, (bx, cy), big_r + o)
        pygame.draw.circle(surface, (40, 36, 60), (bx, cy), big_r - o)
        pygame.draw.circle(surface, color, (bx, cy), big_r, max(2, o))
        # Small filled circle (right)
        sx = cx + int(size * 0.65)
        sy = cy + int(size * 0.25)
        pygame.draw.circle(surface, BLACK, (sx, sy), small_r + o)
        pygame.draw.circle(surface, color, (sx, sy), small_r)

    elif shape == "old_icon":
        # Circle face + spectacles + wrinkle lines
        pygame.draw.circle(surface, BLACK, (cx, cy), size + o)
        pygame.draw.circle(surface, color, (cx, cy), size)
        # Spectacle arcs over eyes
        spec_r = int(size * 0.25)
        for sx in (-1, 1):
            spec_x = cx + sx * int(size * 0.28)
            spec_y = cy - int(size * 0.1)
            spec_rect = pygame.Rect(spec_x - spec_r, spec_y - spec_r, spec_r * 2, spec_r * 2)
            pygame.draw.ellipse(surface, BLACK, spec_rect, max(2, o))
            # Eye dot inside
            es = max(1, int(size * 0.08))
            pygame.draw.circle(surface, BLACK, (spec_x, spec_y), es)
        # Bridge between spectacles
        pygame.draw.line(surface, BLACK,
                         (cx - int(size * 0.05), cy - int(size * 0.1)),
                         (cx + int(size * 0.05), cy - int(size * 0.1)), max(1, o - 1))
        # Wrinkle lines on forehead
        ww = int(size * 0.3)
        for wy_off in (-int(size * 0.45), -int(size * 0.55)):
            pygame.draw.line(surface, (max(0, color[0] - 40), max(0, color[1] - 40),
                                        max(0, color[2] - 30)),
                             (cx - ww, cy + wy_off), (cx + ww, cy + wy_off), 1)
        # Small mouth line
        mw = int(size * 0.2)
        pygame.draw.line(surface, BLACK, (cx - mw, cy + int(size * 0.35)),
                         (cx + mw, cy + int(size * 0.35)), max(1, o - 1))

    elif shape == "snail_icon":
        # Spiral shell circle
        shell_r = int(size * 0.55)
        shell_x = cx + int(size * 0.1)
        shell_y = cy - int(size * 0.1)
        pygame.draw.circle(surface, BLACK, (shell_x, shell_y), shell_r + o)
        pygame.draw.circle(surface, color, (shell_x, shell_y), shell_r)
        # Spiral inside shell
        darker = (max(0, color[0] - 50), max(0, color[1] - 50), max(0, color[2] - 40))
        for i, factor in enumerate((0.7, 0.45, 0.25)):
            sr = int(shell_r * factor)
            offset = int(shell_r * 0.1 * (i + 1))
            if sr > 1:
                arc_rect = pygame.Rect(shell_x - sr + offset, shell_y - sr, sr * 2, sr * 2)
                pygame.draw.arc(surface, darker, arc_rect, 0, math.pi, max(1, o - 1))
        # Body bump beneath
        body_y = cy + int(size * 0.35)
        body_w = int(size * 0.9)
        body_h = int(size * 0.3)
        body_r = pygame.Rect(cx - int(size * 0.5), body_y, body_w, body_h)
        pygame.draw.ellipse(surface, BLACK, body_r.inflate(3, 3))
        pygame.draw.ellipse(surface, color, body_r)
        # Two antennae lines
        ant_len = int(size * 0.4)
        ant_base_x = cx - int(size * 0.3)
        ant_base_y = cy + int(size * 0.1)
        for sx in (-1, 1):
            ax = ant_base_x + sx * int(size * 0.15)
            pygame.draw.line(surface, BLACK, (ax, ant_base_y),
                             (ax + sx * int(size * 0.15), ant_base_y - ant_len), max(1, o))
            # Antenna tip dot
            pygame.draw.circle(surface, BLACK,
                               (ax + sx * int(size * 0.15), ant_base_y - ant_len),
                               max(1, int(size * 0.06)))

    # ------------------------------------------------------------------
    # Verbs (new icons)
    # ------------------------------------------------------------------
    elif shape == "music_note":
        # Filled oval note head
        head_w = int(size * 0.35)
        head_h = int(size * 0.28)
        head_x = cx - int(size * 0.1)
        head_y = cy + int(size * 0.35)
        head_rect = pygame.Rect(head_x - head_w, head_y - head_h, head_w * 2, head_h * 2)
        pygame.draw.ellipse(surface, BLACK, head_rect.inflate(3, 3))
        pygame.draw.ellipse(surface, color, head_rect)
        # Vertical stem line
        stem_x = head_x + head_w - 1
        stem_top = cy - int(size * 0.6)
        pygame.draw.line(surface, BLACK, (stem_x, head_y), (stem_x, stem_top), max(3, o + 1))
        pygame.draw.line(surface, color, (stem_x, head_y), (stem_x, stem_top), max(2, o))
        # Flag curve on top
        flag_w = int(size * 0.35)
        flag_h = int(size * 0.35)
        flag_rect = pygame.Rect(stem_x, stem_top, flag_w, flag_h)
        pygame.draw.arc(surface, BLACK, flag_rect, 0, math.pi, max(3, o + 1))
        pygame.draw.arc(surface, color, flag_rect, 0, math.pi, max(2, o))

    elif shape == "pencil_icon":
        # Angled rectangle body (tilted ~30 degrees)
        lw = max(2, o)
        # Pencil body - draw as a thick angled line
        body_len = int(size * 1.4)
        angle = math.pi / 6  # 30 degrees
        # Tip position (bottom-left)
        tip_x = cx - int(math.cos(angle) * body_len * 0.4)
        tip_y = cy + int(math.sin(angle) * body_len * 0.4)
        # Eraser position (top-right)
        end_x = cx + int(math.cos(angle) * body_len * 0.6)
        end_y = cy - int(math.sin(angle) * body_len * 0.6)
        # Body width (perpendicular offset)
        bw = int(size * 0.18)
        dx_perp = int(math.sin(angle) * bw)
        dy_perp = int(math.cos(angle) * bw)
        # Body polygon
        body_pts = [
            (tip_x + int(math.cos(angle) * int(size * 0.3)) - dx_perp,
             tip_y - int(math.sin(angle) * int(size * 0.3)) - dy_perp),
            (tip_x + int(math.cos(angle) * int(size * 0.3)) + dx_perp,
             tip_y - int(math.sin(angle) * int(size * 0.3)) + dy_perp),
            (end_x + dx_perp, end_y + dy_perp),
            (end_x - dx_perp, end_y - dy_perp),
        ]
        pygame.draw.polygon(surface, BLACK, body_pts)
        inner_pts = [
            (body_pts[0][0] + 1, body_pts[0][1] + 1),
            (body_pts[1][0] - 1, body_pts[1][1] - 1),
            (body_pts[2][0] - 1, body_pts[2][1] - 1),
            (body_pts[3][0] + 1, body_pts[3][1] + 1),
        ]
        pygame.draw.polygon(surface, color, inner_pts)
        # Triangle tip
        pygame.draw.polygon(surface, BLACK, [
            (tip_x, tip_y),
            (tip_x + int(math.cos(angle) * int(size * 0.3)) - dx_perp,
             tip_y - int(math.sin(angle) * int(size * 0.3)) - dy_perp),
            (tip_x + int(math.cos(angle) * int(size * 0.3)) + dx_perp,
             tip_y - int(math.sin(angle) * int(size * 0.3)) + dy_perp),
        ])
        pygame.draw.polygon(surface, (80, 60, 50), [
            (tip_x + 1, tip_y),
            (tip_x + int(math.cos(angle) * int(size * 0.28)) - dx_perp + 1,
             tip_y - int(math.sin(angle) * int(size * 0.28)) - dy_perp),
            (tip_x + int(math.cos(angle) * int(size * 0.28)) + dx_perp - 1,
             tip_y - int(math.sin(angle) * int(size * 0.28)) + dy_perp),
        ])
        # Eraser rectangle at back
        eraser_len = int(size * 0.2)
        eraser_pts = [
            (end_x - dx_perp, end_y - dy_perp),
            (end_x + dx_perp, end_y + dy_perp),
            (end_x + int(math.cos(angle) * eraser_len) + dx_perp,
             end_y - int(math.sin(angle) * eraser_len) + dy_perp),
            (end_x + int(math.cos(angle) * eraser_len) - dx_perp,
             end_y - int(math.sin(angle) * eraser_len) - dy_perp),
        ]
        pygame.draw.polygon(surface, BLACK, eraser_pts)
        pygame.draw.polygon(surface, (240, 180, 180), [
            (ep[0] + (1 if i < 2 else -1), ep[1]) for i, ep in enumerate(eraser_pts)
        ])

    elif shape == "speech_icon":
        # Rounded rectangle bubble
        bw = int(size * 1.2)
        bh = int(size * 0.8)
        br = pygame.Rect(cx - bw, cy - bh, bw * 2, bh * 2)
        pygame.draw.rect(surface, BLACK, br.inflate(4, 4), border_radius=int(size * 0.3))
        pygame.draw.rect(surface, color, br, border_radius=int(size * 0.3))
        # Small triangle tail at bottom-left
        tail_pts = [
            (cx - int(size * 0.4), cy + bh - 2),
            (cx - int(size * 0.7), cy + bh + int(size * 0.5)),
            (cx - int(size * 0.1), cy + bh - 2),
        ]
        pygame.draw.polygon(surface, BLACK, [
            (tail_pts[0][0] - 1, tail_pts[0][1]),
            (tail_pts[1][0] - 1, tail_pts[1][1] + 2),
            (tail_pts[2][0] + 1, tail_pts[2][1]),
        ])
        pygame.draw.polygon(surface, color, tail_pts)
        # Three dots inside bubble
        dot_r = max(2, int(size * 0.1))
        for dx in (-int(size * 0.4), 0, int(size * 0.4)):
            pygame.draw.circle(surface, BLACK, (cx + dx, cy), dot_r)

    # ------------------------------------------------------------------
    # Phrases (new icons)
    # ------------------------------------------------------------------
    elif shape == "wave_icon":
        # Open palm with 5 finger bumps on arc + motion lines
        # Palm base
        palm_r = int(size * 0.5)
        palm_y = cy + int(size * 0.2)
        pygame.draw.circle(surface, BLACK, (cx, palm_y), palm_r + o)
        pygame.draw.circle(surface, color, (cx, palm_y), palm_r)
        # 5 finger bumps in an arc above palm
        finger_r = max(2, int(size * 0.14))
        for i in range(5):
            angle = math.pi * 0.15 + i * math.pi * 0.175
            fx = cx + int(math.cos(angle) * int(size * 0.7)) - int(size * 0.1)
            fy = palm_y - int(math.sin(angle) * int(size * 0.8))
            pygame.draw.circle(surface, BLACK, (fx, fy), finger_r + 1)
            pygame.draw.circle(surface, color, (fx, fy), finger_r)
        # Motion lines to the right
        ml = int(size * 0.35)
        for i, dy in enumerate((-int(size * 0.2), 0, int(size * 0.2))):
            mx = cx + int(size * 0.8) + i * int(size * 0.08)
            pygame.draw.line(surface, color, (mx, palm_y + dy), (mx + ml, palm_y + dy), max(1, o - 1))

    elif shape == "checkmark":
        # Bold checkmark stroke
        lw = max(3, int(size * 0.2))
        # Two thick lines forming a check
        p1 = (cx - int(size * 0.6), cy)
        p2 = (cx - int(size * 0.15), cy + int(size * 0.5))
        p3 = (cx + int(size * 0.7), cy - int(size * 0.55))
        pygame.draw.line(surface, BLACK, p1, p2, lw + 2)
        pygame.draw.line(surface, BLACK, p2, p3, lw + 2)
        pygame.draw.line(surface, color, p1, p2, lw)
        pygame.draw.line(surface, color, p2, p3, lw)

    elif shape == "cross_icon":
        # Bold X stroke
        lw = max(3, int(size * 0.2))
        half = int(size * 0.6)
        pygame.draw.line(surface, BLACK, (cx - half, cy - half), (cx + half, cy + half), lw + 2)
        pygame.draw.line(surface, BLACK, (cx + half, cy - half), (cx - half, cy + half), lw + 2)
        pygame.draw.line(surface, color, (cx - half, cy - half), (cx + half, cy + half), lw)
        pygame.draw.line(surface, color, (cx + half, cy - half), (cx - half, cy + half), lw)

    # ------------------------------------------------------------------
    # Numbers
    # ------------------------------------------------------------------
    elif shape.startswith("num_"):
        digit = shape[4:]  # e.g. "1", "2", "3", "5"
        pygame.draw.circle(surface, BLACK, (cx, cy), size + o)
        pygame.draw.circle(surface, color, (cx, cy), size)
        fsize = max(10, int(size * 1.1))
        font_num = pygame.font.SysFont("Arial", fsize, bold=True)
        txt = font_num.render(digit, True, WHITE)
        surface.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))

    # ------------------------------------------------------------------
    # Fallback: unknown shape → plain colored circle
    # ------------------------------------------------------------------
    else:
        pygame.draw.circle(surface, BLACK, (cx, cy), size + o)
        pygame.draw.circle(surface, color, (cx, cy), size)


def _draw_word_panel(surface, polish, icon_hint, cy):
    """Draw a centred panel with large vocab icon + Polish word."""
    font = pygame.font.SysFont("Arial", 44, bold=True)
    word_surf = font.render(polish, True, WHITE)
    icon_sz = 26
    gap = 16
    content_w = icon_sz * 2 + gap + word_surf.get_width()
    pw = min(SCREEN_WIDTH - 40, max(260, content_w + 60))
    ph = 80
    px = SCREEN_WIDTH // 2 - pw // 2
    py = cy - ph // 2
    pygame.draw.rect(surface, (40, 36, 60), (px, py, pw, ph), border_radius=16)
    pygame.draw.rect(surface, (100, 85, 140), (px, py, pw, ph),
                     width=2, border_radius=16)
    cx = SCREEN_WIDTH // 2 - content_w // 2
    _draw_vocab_icon(surface, cx + icon_sz, cy, icon_hint, size=icon_sz)
    surface.blit(word_surf, (cx + icon_sz * 2 + gap,
                             cy - word_surf.get_height() // 2))


def _calc_edu_result(score, max_score):
    """Calculate happiness + XP reward for an edu game."""
    happiness = min(EDU_GAME_HAPPINESS_CAP,
                    EDU_GAME_BASE_HAPPINESS + score * EDU_GAME_PER_SCORE)
    xp = score * XP_PER_CORRECT
    if score == max_score:
        xp += XP_BONUS_PERFECT
    return {"happiness": happiness, "xp": xp, "is_edu": True}


# ---------------------------------------------------------------------------
# PlayMenu — Game Selection
# ---------------------------------------------------------------------------

class PlayMenu:
    """Overlay to select which game to play (follows FoodMenu pattern)."""

    ITEMS = [
        ("fun",      "Fun Games",    "Catch, Pop, Chase!",   ("star",     (255, 220, 80))),
        ("memory",   "Memory Match", "Match Polish-English", ("rect",     (180, 130, 255))),
        ("falling",  "Catch the Word", "Catch translations", ("drop",     (100, 180, 255))),
        ("spelling", "Spell It!",    "Spell English words",  ("triangle", (100, 200, 120))),
        ("quiz",     "Quick Quiz",   "Multiple choice",      ("circle",   (255, 160, 100))),
        ("wordbook", "Word Book",    "See your progress",    ("book",     (180, 140, 120))),
    ]

    def __init__(self):
        self.done = False
        self.result = None
        h = 48 + len(self.ITEMS) * PLAY_MENU_ROW_HEIGHT + 8
        self.rect = pygame.Rect(
            (SCREEN_WIDTH - PLAY_MENU_WIDTH) // 2,
            (SCREEN_HEIGHT - h) // 2 - 20,
            PLAY_MENU_WIDTH, h,
        )
        self._row_rects = []
        y = self.rect.y + 48
        for _ in self.ITEMS:
            r = pygame.Rect(self.rect.x + 8, y,
                            PLAY_MENU_WIDTH - 16, PLAY_MENU_ROW_HEIGHT)
            self._row_rects.append(r)
            y += PLAY_MENU_ROW_HEIGHT

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.done = True
                self.result = None
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3,
                               pygame.K_4, pygame.K_5, pygame.K_6):
                idx = event.key - pygame.K_1
                if 0 <= idx < len(self.ITEMS):
                    self.result = self.ITEMS[idx][0]
                    self.done = True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._row_rects):
                if r.collidepoint(mouse_pos):
                    self.result = self.ITEMS[i][0]
                    self.done = True
                    return
            if not self.rect.collidepoint(mouse_pos):
                self.done = True
                self.result = None

    def update(self, dt):
        pass

    def draw(self, surface, mouse_pos):
        _draw_overlay_bg(surface)
        pygame.draw.rect(surface, FOOD_MENU_BG, self.rect, border_radius=12)
        pygame.draw.rect(surface, FOOD_MENU_BORDER, self.rect,
                         width=3, border_radius=12)

        font_title = pygame.font.SysFont("Arial", 34, bold=True)
        font_name = pygame.font.SysFont("Arial", 26)
        font_sub = pygame.font.SysFont("Arial", 20)

        title = font_title.render("Play", True, OVERLAY_TITLE_COLOR)
        surface.blit(title, (self.rect.centerx - title.get_width() // 2,
                             self.rect.y + 12))

        for i, (r, item) in enumerate(zip(self._row_rects, self.ITEMS)):
            key, name, subtitle, icon_hint = item
            hovered = r.collidepoint(mouse_pos)
            if hovered:
                pygame.draw.rect(surface, FOOD_MENU_HOVER, r, border_radius=8)

            _draw_vocab_icon(surface, r.x + 28, r.centery, icon_hint, size=12)

            label = font_name.render(f"{i + 1}. {name}", True, FOOD_MENU_TEXT)
            surface.blit(label, (r.x + 56, r.y + 6))

            sub = font_sub.render(subtitle, True, (160, 160, 180))
            surface.blit(sub, (r.x + 56, r.y + 32))


# ---------------------------------------------------------------------------
# Base Edu Game
# ---------------------------------------------------------------------------

class _EduGameBase:
    """Shared logic for timed educational mini games."""

    title = "Edu Game"
    duration = 10.0
    max_score = 1

    def __init__(self, sound):
        self.sound = sound
        self.timer = self.duration
        self.score = 0
        self.done = False
        self.result = None
        self._phase = "play"
        self._results_timer = 0.0
        self._flash_timer = 0.0
        self._flash_color = None
        self.word_results = []  # [(english_word, correct_bool), ...]

    def handle_event(self, event, mouse_pos):
        if self._phase != "play":
            return
        self._on_event(event, mouse_pos)

    def _on_event(self, event, mouse_pos):
        pass

    def update(self, dt):
        if self._flash_timer > 0:
            self._flash_timer = max(0, self._flash_timer - dt)

        if self._phase == "play":
            self.timer -= dt
            self._update_play(dt)
            if self.timer <= 0:
                self.timer = 0
                self._finish()
        elif self._phase == "results":
            self._results_timer -= dt
            if self._results_timer <= 0:
                self.done = True

    def _update_play(self, dt):
        pass

    def _finish(self):
        self._phase = "results"
        self.result = _calc_edu_result(self.score, self.max_score)
        self._results_timer = MINIGAME_RESULTS_DURATION

    def draw(self, surface, mouse_pos):
        _draw_overlay_bg(surface)
        if self._phase == "play":
            self._draw_play(surface, mouse_pos)
            self._draw_hud(surface)
        else:
            self._draw_results(surface)

    def _draw_play(self, surface, mouse_pos):
        pass

    def _draw_hud(self, surface):
        font_title = pygame.font.SysFont("Arial", 38, bold=True)
        font_score = pygame.font.SysFont("Arial", 32)

        title_surf = font_title.render(self.title, True, OVERLAY_TITLE_COLOR)
        surface.blit(title_surf,
                     (SCREEN_WIDTH // 2 - title_surf.get_width() // 2, 16))

        bar_w = 300
        bar_h = 14
        bar_x = (SCREEN_WIDTH - bar_w) // 2
        bar_y = 54
        pygame.draw.rect(surface, OVERLAY_TIMER_BG,
                         (bar_x, bar_y, bar_w, bar_h), border_radius=7)
        fill_w = int(bar_w * max(0, self.timer / self.duration))
        if fill_w > 0:
            pygame.draw.rect(surface, OVERLAY_TIMER_FG,
                             (bar_x, bar_y, fill_w, bar_h), border_radius=7)

        score_surf = font_score.render(
            f"Score: {self.score}/{self.max_score}", True, OVERLAY_SCORE_COLOR)
        surface.blit(score_surf,
                     (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, 74))

    def _draw_results(self, surface):
        font_big = pygame.font.SysFont("Arial", 50, bold=True)
        font_med = pygame.font.SysFont("Arial", 36)

        cy = SCREEN_HEIGHT // 2 - 60

        if self.score == self.max_score:
            heading = "Perfect!"
        elif self.score > 0:
            heading = "Good Job!"
        else:
            heading = "Keep Trying!"

        t1 = font_big.render(heading, True, OVERLAY_TITLE_COLOR)
        surface.blit(t1, (SCREEN_WIDTH // 2 - t1.get_width() // 2, cy))

        t2 = font_med.render(
            f"Score: {self.score}/{self.max_score}", True, OVERLAY_SCORE_COLOR)
        surface.blit(t2, (SCREEN_WIDTH // 2 - t2.get_width() // 2, cy + 55))

        if self.result and isinstance(self.result, dict):
            happiness = self.result.get("happiness", 0)
            xp = self.result.get("xp", 0)
            t3 = font_med.render(f"+{happiness} Happiness  +{xp} XP",
                                 True, (255, 220, 100))
            surface.blit(t3, (SCREEN_WIDTH // 2 - t3.get_width() // 2, cy + 95))

    def _play_correct(self):
        self.score += 1
        self._flash_timer = 0.4
        self._flash_color = QUIZ_CORRECT_COLOR
        if self.sound:
            self.sound.play("correct")

    def _play_incorrect(self):
        self._flash_timer = 0.4
        self._flash_color = QUIZ_WRONG_COLOR
        if self.sound:
            self.sound.play("incorrect")


# ---------------------------------------------------------------------------
# QuizGame — Multiple Choice
# ---------------------------------------------------------------------------

class QuizGame(_EduGameBase):
    title = "Quick Quiz"
    duration = QUIZ_DURATION

    def __init__(self, sound, mastery_data=None, day_count=0, level=1):
        diff = _get_difficulty(level)
        self._num_questions = QUIZ_COUNT_BY_DIFF[diff]
        self._num_options = QUIZ_OPTIONS_BY_DIFF[diff]
        self.max_score = self._num_questions
        super().__init__(sound)
        self._mastery_data = mastery_data
        self._tier_unlock = (get_unlocked_tier(mastery_data)
                             if mastery_data is not None else None)
        if mastery_data is not None:
            self._words = get_smart_words(self._num_questions, mastery_data,
                                          day_count, self._tier_unlock)
        else:
            self._words = get_random_words(self._num_questions)
        self._qi = 0
        self._options = []
        self._button_rects = []
        self._answer_flash = None  # (index, color)
        self._correct_idx = 0
        self._show_correct = False  # after wrong answer, highlight correct
        self._advance_timer = 0.0
        self._setup_question()

    def _setup_question(self):
        if self._qi >= len(self._words):
            self._finish()
            return
        correct = self._words[self._qi]
        n_dist = self._num_options - 1
        distractors = get_distractors(correct, n_dist, tier_unlock=self._tier_unlock)
        self._options = [correct] + distractors
        random.shuffle(self._options)
        self._correct_idx = next(
            i for i, o in enumerate(self._options) if o[1] == correct[1])
        self._answer_flash = None
        self._show_correct = False
        self._advance_timer = 0.0

        # Stacked buttons
        cx = SCREEN_WIDTH // 2
        n_opts = len(self._options)
        gap = 16
        total_h = n_opts * QUIZ_BUTTON_H + (n_opts - 1) * gap
        start_y = SCREEN_HEIGHT // 2 - total_h // 2 + 20
        self._button_rects = []
        for i in range(n_opts):
            bx = cx - QUIZ_BUTTON_W // 2
            by = start_y + i * (QUIZ_BUTTON_H + gap)
            self._button_rects.append(
                pygame.Rect(bx, by, QUIZ_BUTTON_W, QUIZ_BUTTON_H))

    def _on_event(self, event, mouse_pos):
        if self._advance_timer > 0:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._button_rects):
                if r.collidepoint(mouse_pos):
                    correct = self._words[self._qi]
                    if self._options[i][1] == correct[1]:
                        self._play_correct()
                        self._answer_flash = (i, QUIZ_CORRECT_COLOR)
                        self._advance_timer = 0.6
                        self.word_results.append((correct[1], True))
                        if self.sound:
                            self.sound.speak(correct[1])
                    else:
                        self._play_incorrect()
                        self._answer_flash = (i, QUIZ_WRONG_COLOR)
                        self._show_correct = True
                        self._advance_timer = 1.2  # longer so kid sees correct
                        self.word_results.append((correct[1], False))
                    return

    def _update_play(self, dt):
        if self._advance_timer > 0:
            self._advance_timer -= dt
            if self._advance_timer <= 0:
                self._qi += 1
                self._setup_question()

    def _draw_play(self, surface, mouse_pos):
        if self._qi >= len(self._words):
            return
        word = self._words[self._qi]
        font_btn = pygame.font.SysFont("Arial", 32)
        font_hint = pygame.font.SysFont("Arial", 22)

        # Centred word panel with large icon
        _draw_word_panel(surface, word[0], word[3], PLAY_TOP + 50)

        # Question hint below panel
        hint = font_hint.render(
            f"Question {self._qi + 1}/{self._num_questions}  —  What does this mean?",
            True, (180, 180, 200))
        surface.blit(hint,
                     (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                      PLAY_TOP + 96))

        # Answer buttons
        for i, (r, opt) in enumerate(zip(self._button_rects, self._options)):
            hovered = r.collidepoint(mouse_pos)

            # Determine button color
            if self._answer_flash and self._answer_flash[0] == i:
                color = self._answer_flash[1]
            elif self._show_correct and i == self._correct_idx:
                color = QUIZ_CORRECT_COLOR  # hint: show correct answer
            elif hovered and self._advance_timer <= 0:
                color = QUIZ_BUTTON_HOVER
            else:
                color = QUIZ_BUTTON_COLOR

            pygame.draw.rect(surface, color, r, border_radius=12)
            pygame.draw.rect(surface, (140, 130, 170), r,
                             width=2, border_radius=12)

            label = font_btn.render(opt[1], True, WHITE)
            surface.blit(label,
                         (r.centerx - label.get_width() // 2,
                          r.centery - label.get_height() // 2))


# ---------------------------------------------------------------------------
# FallingWordGame — Catch the Translation
# ---------------------------------------------------------------------------

class FallingWordGame(_EduGameBase):
    title = "Catch the Word"
    duration = FALLING_WORD_DURATION

    def __init__(self, sound, mastery_data=None, day_count=0, level=1):
        diff = _get_difficulty(level)
        self._num_rounds = FALLING_ROUNDS_BY_DIFF[diff]
        self._fall_speed = FALLING_SPEED_BY_DIFF[diff]
        self.max_score = self._num_rounds
        super().__init__(sound)
        self._tier_unlock = (get_unlocked_tier(mastery_data)
                             if mastery_data is not None else None)
        if mastery_data is not None:
            self._words = get_smart_words(self._num_rounds, mastery_data,
                                          day_count, self._tier_unlock)
        else:
            self._words = get_random_words(self._num_rounds)
        self._round = 0
        self._pills = []  # [(x, y, vocab_entry, is_correct)]
        self._advance_timer = 0.0
        self._show_correct_pill = False  # after wrong, highlight correct
        self._setup_round()

    def _setup_round(self):
        if self._round >= len(self._words):
            self._finish()
            return
        correct = self._words[self._round]
        distractors = get_distractors(correct, 2, tier_unlock=self._tier_unlock)
        options = [correct] + distractors
        random.shuffle(options)
        self._pills = []
        pw = FALLING_WORD_PILL_W
        total_w = 3 * pw + 2 * 20
        start_x = (SCREEN_WIDTH - total_w) // 2 + pw // 2
        for i, opt in enumerate(options):
            px = start_x + i * (pw + 20)
            py = PLAY_TOP + 140 + random.randint(0, 20)
            is_correct = (opt[1] == correct[1])
            self._pills.append([px, py, opt, is_correct])
        self._advance_timer = 0.0
        self._show_correct_pill = False

    def _on_event(self, event, mouse_pos):
        if self._advance_timer > 0:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = mouse_pos
            for pill in self._pills:
                px, py, opt, is_correct = pill
                pr = pygame.Rect(px - FALLING_WORD_PILL_W // 2,
                                 int(py) - FALLING_WORD_PILL_H // 2,
                                 FALLING_WORD_PILL_W, FALLING_WORD_PILL_H)
                if pr.collidepoint(mx, my):
                    correct_word = self._words[self._round]
                    if is_correct:
                        self._play_correct()
                        self._advance_timer = 0.5
                        self.word_results.append((correct_word[1], True))
                        if self.sound:
                            self.sound.speak(opt[1])
                    else:
                        self._play_incorrect()
                        self._show_correct_pill = True
                        self._advance_timer = 1.2  # longer so kid sees correct
                        self.word_results.append((correct_word[1], False))
                    return

    def _update_play(self, dt):
        if self._advance_timer > 0:
            self._advance_timer -= dt
            if self._advance_timer <= 0:
                self._round += 1
                self._setup_round()
            return

        # Move pills down
        for pill in self._pills:
            pill[1] += self._fall_speed * dt

        # If all pills fell off screen, advance (counts as miss)
        if all(p[1] > PLAY_BOTTOM + 20 for p in self._pills):
            if self._round < len(self._words):
                self.word_results.append((self._words[self._round][1], False))
            self._round += 1
            self._setup_round()

    def _draw_play(self, surface, mouse_pos):
        if self._round >= len(self._words):
            return
        word = self._words[self._round]
        font_pill = pygame.font.SysFont("Arial", 26)
        font_hint = pygame.font.SysFont("Arial", 22)

        # Centred word panel with large icon
        _draw_word_panel(surface, word[0], word[3], PLAY_TOP + 50)

        # Round info below panel
        hint = font_hint.render(
            f"Round {self._round + 1}/{self._num_rounds}  —  Click the English word!",
            True, (180, 180, 200))
        surface.blit(hint,
                     (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                      PLAY_TOP + 96))

        # Falling pills
        for px, py, opt, is_correct in self._pills:
            pr = pygame.Rect(int(px) - FALLING_WORD_PILL_W // 2,
                             int(py) - FALLING_WORD_PILL_H // 2,
                             FALLING_WORD_PILL_W, FALLING_WORD_PILL_H)
            hovered = pr.collidepoint(mouse_pos)

            # Color: highlight correct pill green after wrong answer
            if self._show_correct_pill and is_correct:
                color = QUIZ_CORRECT_COLOR
            elif hovered and self._advance_timer <= 0:
                color = (100, 90, 140)
            else:
                color = (70, 65, 100)

            pygame.draw.rect(surface, color, pr, border_radius=20)
            pygame.draw.rect(surface, (140, 130, 170), pr,
                             width=2, border_radius=20)
            label = font_pill.render(opt[1], True, WHITE)
            surface.blit(label,
                         (pr.centerx - label.get_width() // 2,
                          pr.centery - label.get_height() // 2))


# ---------------------------------------------------------------------------
# SpellingGame — Letter Tiles
# ---------------------------------------------------------------------------

class SpellingGame(_EduGameBase):
    title = "Spell It!"
    duration = SPELLING_DURATION

    def __init__(self, sound, mastery_data=None, day_count=0, level=1):
        diff = _get_difficulty(level)
        self._num_words = SPELLING_COUNT_BY_DIFF[diff]
        self._easy = (diff == 0)
        self.max_score = self._num_words
        super().__init__(sound)
        if mastery_data is not None:
            self._words = get_smart_words(self._num_words, mastery_data, day_count)
        else:
            self._words = get_random_words(self._num_words)
        # On easy, filter to short words only (<=5 chars)
        if self._easy:
            short = [w for w in self._words if len(w[1]) <= 5]
            if len(short) < self._num_words:
                from vocabulary import ALL_VOCAB
                extras = [w for w in ALL_VOCAB if len(w[1]) <= 5
                          and w not in short]
                random.shuffle(extras)
                short.extend(extras[:self._num_words - len(short)])
            self._words = short[:self._num_words]
            self.max_score = len(self._words)
        self._wi = 0
        self._target = ""   # english word to spell
        self._polish = ""   # polish word shown as prompt
        self._icon_hint = None
        self._letters = []  # [[char, used, flash_timer], ...]
        self._filled = []   # correctly placed chars so far
        self._advance_timer = 0.0
        self._hint_timer = 0.0  # time since last correct letter
        self._tile_rects = []
        self._setup_word()

    def _setup_word(self):
        if self._wi >= len(self._words):
            self._finish()
            return
        entry = self._words[self._wi]
        self._target = entry[1]
        self._polish = entry[0]
        self._icon_hint = entry[3]
        chars = list(self._target)
        random.shuffle(chars)
        self._letters = [[c, False, 0.0] for c in chars]
        self._filled = []
        self._advance_timer = 0.0
        self._hint_timer = 0.0

        # Pre-fill the first letter as a hint
        first_char = self._target[0]
        for letter in self._letters:
            if letter[0] == first_char and not letter[1]:
                letter[1] = True
                self._filled.append(first_char)
                break

        self._recalc_tile_rects()

    def _recalc_tile_rects(self):
        n = len(self._letters)
        ts = SPELLING_TILE_SIZE
        gap = 8
        total_w = n * ts + (n - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        ty = SCREEN_HEIGHT // 2 + 30
        self._tile_rects = []
        for i in range(n):
            tx = start_x + i * (ts + gap)
            self._tile_rects.append(pygame.Rect(tx, ty, ts, ts))

    def _on_event(self, event, mouse_pos):
        if self._advance_timer > 0:
            return
        if len(self._filled) >= len(self._target):
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._tile_rects):
                if r.collidepoint(mouse_pos) and not self._letters[i][1]:
                    expected = self._target[len(self._filled)]
                    if self._letters[i][0] == expected:
                        self._letters[i][1] = True
                        self._filled.append(self._letters[i][0])
                        self._hint_timer = 0.0
                        if self.sound:
                            self.sound.play("correct")
                        if len(self._filled) == len(self._target):
                            self.score += 1
                            self._advance_timer = 0.6
                            self.word_results.append((self._target, True))
                            if self.sound:
                                self.sound.speak(self._target)
                    else:
                        self._letters[i][2] = 0.3
                        if self.sound:
                            self.sound.play("incorrect")
                    return

    def _finish(self):
        # Mark current incomplete word as failed
        if self._wi < len(self._words) and len(self._filled) < len(self._target):
            self.word_results.append((self._target, False))
        super()._finish()

    def _update_play(self, dt):
        for letter in self._letters:
            if letter[2] > 0:
                letter[2] = max(0, letter[2] - dt)

        if self._advance_timer > 0:
            self._advance_timer -= dt
            if self._advance_timer <= 0:
                self._wi += 1
                self._setup_word()
            return

        # Hint timer: time since last correct letter placed
        if len(self._filled) < len(self._target):
            self._hint_timer += dt

    def _get_hint_tile_index(self):
        """After SPELLING_HINT_DELAY, return index of next correct tile to pulse."""
        if self._hint_timer < SPELLING_HINT_DELAY:
            return -1
        if len(self._filled) >= len(self._target):
            return -1
        expected = self._target[len(self._filled)]
        for i, letter in enumerate(self._letters):
            if letter[0] == expected and not letter[1]:
                return i
        return -1

    def _draw_play(self, surface, mouse_pos):
        if self._wi >= len(self._words):
            return
        font_hint = pygame.font.SysFont("Arial", 22)
        font_blank = pygame.font.SysFont("Arial", 42, bold=True)
        font_tile = pygame.font.SysFont("Arial", 34, bold=True)

        # Centred word panel with large icon
        if self._icon_hint:
            _draw_word_panel(surface, self._polish, self._icon_hint,
                             PLAY_TOP + 50)
        else:
            font_prompt = pygame.font.SysFont("Arial", 44, bold=True)
            ps = font_prompt.render(self._polish, True, WHITE)
            surface.blit(ps, (SCREEN_WIDTH // 2 - ps.get_width() // 2,
                              PLAY_TOP + 30))

        # Word info below panel
        hint = font_hint.render(
            f"Word {self._wi + 1}/{self._num_words}  —  Spell the English word",
            True, (180, 180, 200))
        surface.blit(hint,
                     (SCREEN_WIDTH // 2 - hint.get_width() // 2,
                      PLAY_TOP + 96))

        # Blanks / filled letters
        n = len(self._target)
        blank_w = 30
        blank_gap = 8
        total_bw = n * blank_w + (n - 1) * blank_gap
        bx = (SCREEN_WIDTH - total_bw) // 2
        by = SCREEN_HEIGHT // 2 - 40
        for i in range(n):
            x = bx + i * (blank_w + blank_gap)
            if i < len(self._filled):
                ch = font_blank.render(self._filled[i], True,
                                       SPELLING_TILE_CORRECT)
                surface.blit(ch, (x + blank_w // 2 - ch.get_width() // 2,
                                  by - ch.get_height() // 2))
            pygame.draw.line(surface, WHITE,
                             (x, by + 20), (x + blank_w, by + 20), 2)

        # Scrambled letter tiles with hint pulse
        hint_idx = self._get_hint_tile_index()
        for i, (r, letter_data) in enumerate(
                zip(self._tile_rects, self._letters)):
            char, used, flash = letter_data
            if used:
                color = SPELLING_TILE_CORRECT
            elif flash > 0:
                color = QUIZ_WRONG_COLOR
            elif i == hint_idx:
                # Pulse hint: oscillate between normal and bright
                pulse = 0.5 + 0.5 * math.sin(self._hint_timer * 4)
                color = (
                    int(80 + 100 * pulse),
                    int(70 + 80 * pulse),
                    int(120 + 80 * pulse),
                )
            elif r.collidepoint(mouse_pos):
                color = (100, 90, 140)
            else:
                color = SPELLING_TILE_COLOR

            pygame.draw.rect(surface, color, r, border_radius=10)
            pygame.draw.rect(surface, (140, 130, 170), r,
                             width=2, border_radius=10)

            if not used:
                ch = font_tile.render(char, True, WHITE)
                surface.blit(ch,
                             (r.centerx - ch.get_width() // 2,
                              r.centery - ch.get_height() // 2))


# ---------------------------------------------------------------------------
# MemoryGame — Word-Picture Matching
# ---------------------------------------------------------------------------

class MemoryGame(_EduGameBase):
    title = "Memory Match"
    duration = MEMORY_DURATION

    def __init__(self, sound, mastery_data=None, day_count=0, level=1):
        diff = _get_difficulty(level)
        self._num_pairs = MEMORY_PAIRS_BY_DIFF[diff]
        self.max_score = self._num_pairs
        super().__init__(sound)
        if mastery_data is not None:
            self._words = get_smart_words(self._num_pairs, mastery_data, day_count)
        else:
            self._words = get_random_words(self._num_pairs)
        self._cards = []
        self._flipped = []
        self._matched = set()
        self._mismatch_timer = 0.0
        self._peek_timer = MEMORY_PEEK_DURATION  # show all cards at start
        self._setup_cards()

    def _setup_cards(self):
        cards = []
        for i, word in enumerate(self._words):
            cards.append({
                "pair_id": i,
                "type": "polish",
                "text": word[0],
                "icon_hint": None,
                "word": word,
            })
            cards.append({
                "pair_id": i,
                "type": "english",
                "text": word[1],
                "icon_hint": word[3],
                "word": word,
            })
        random.shuffle(cards)
        self._cards = cards

        # Layout grid based on number of cards
        cw = MEMORY_CARD_W
        ch = MEMORY_CARD_H
        gap = MEMORY_CARD_SPACING
        n = len(self._cards)
        cols = 4 if n > 6 else 3
        rows = (n + cols - 1) // cols
        total_w = cols * cw + (cols - 1) * gap
        total_h = rows * ch + (rows - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        start_y = (SCREEN_HEIGHT - total_h) // 2 + 10
        for idx, card in enumerate(self._cards):
            row = idx // cols
            col = idx % cols
            card["rect"] = pygame.Rect(
                start_x + col * (cw + gap),
                start_y + row * (ch + gap),
                cw, ch)

    def _on_event(self, event, mouse_pos):
        if self._peek_timer > 0:
            return  # ignore clicks during peek
        if self._mismatch_timer > 0:
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, card in enumerate(self._cards):
                if (i not in self._matched and i not in self._flipped
                        and card["rect"].collidepoint(mouse_pos)):
                    self._flipped.append(i)
                    if self.sound:
                        self.sound.play("click")
                    if len(self._flipped) == 2:
                        a, b = self._flipped
                        if self._cards[a]["pair_id"] == self._cards[b]["pair_id"]:
                            self._matched.add(a)
                            self._matched.add(b)
                            self._flipped = []
                            self._play_correct()
                            english = self._cards[a]["word"][1]
                            self.word_results.append((english, True))
                            if self.sound:
                                self.sound.speak(english)
                            if len(self._matched) == len(self._cards):
                                self._finish()
                        else:
                            self._mismatch_timer = MEMORY_MISMATCH_DELAY
                            if self.sound:
                                self.sound.play("incorrect")
                    return

    def _update_play(self, dt):
        if self._peek_timer > 0:
            self._peek_timer -= dt
            return  # don't count peek time against game timer
        if self._mismatch_timer > 0:
            self._mismatch_timer -= dt
            if self._mismatch_timer <= 0:
                self._flipped = []

    def update(self, dt):
        """Override to pause game timer during peek phase."""
        if self._flash_timer > 0:
            self._flash_timer = max(0, self._flash_timer - dt)

        if self._phase == "play":
            if self._peek_timer <= 0:
                self.timer -= dt  # only tick timer after peek
            self._update_play(dt)
            if self.timer <= 0:
                self.timer = 0
                self._finish()
        elif self._phase == "results":
            self._results_timer -= dt
            if self._results_timer <= 0:
                self.done = True

    def _draw_play(self, surface, mouse_pos):
        font_card = pygame.font.SysFont("Arial", 20, bold=True)
        font_q = pygame.font.SysFont("Arial", 42, bold=True)
        font_peek = pygame.font.SysFont("Arial", 22, bold=True)

        peeking = self._peek_timer > 0

        # Peek countdown message
        if peeking:
            msg = font_peek.render(
                f"Memorise the cards! {int(self._peek_timer) + 1}...",
                True, (255, 220, 100))
            surface.blit(msg,
                         (SCREEN_WIDTH // 2 - msg.get_width() // 2,
                          PLAY_TOP + 10))

        for i, card in enumerate(self._cards):
            r = card["rect"]
            is_revealed = (peeking
                           or i in self._flipped
                           or i in self._matched)

            if i in self._matched:
                pygame.draw.rect(surface, MEMORY_CARD_MATCHED, r,
                                 border_radius=12)
                pygame.draw.rect(surface, (100, 180, 120), r,
                                 width=2, border_radius=12)
            elif is_revealed:
                pygame.draw.rect(surface, (50, 45, 70), r,
                                 border_radius=12)
                pygame.draw.rect(surface, (140, 130, 170), r,
                                 width=2, border_radius=12)
            else:
                hovered = r.collidepoint(mouse_pos)
                back_color = (100, 90, 140) if hovered else MEMORY_CARD_BACK
                pygame.draw.rect(surface, back_color, r,
                                 border_radius=12)
                pygame.draw.rect(surface, (140, 130, 170), r,
                                 width=2, border_radius=12)
                q = font_q.render("?", True, (180, 170, 210))
                surface.blit(q, (r.centerx - q.get_width() // 2,
                                 r.centery - q.get_height() // 2))
                continue

            # Draw card content
            if card["type"] == "polish":
                text = font_card.render(card["text"], True, WHITE)
                surface.blit(text,
                             (r.centerx - text.get_width() // 2,
                              r.centery - text.get_height() // 2))
            else:
                if card["icon_hint"]:
                    _draw_vocab_icon(surface, r.centerx, r.centery - 16,
                                     card["icon_hint"], size=16)
                text = font_card.render(card["text"], True, WHITE)
                surface.blit(text,
                             (r.centerx - text.get_width() // 2,
                              r.centery + 20))


# ---------------------------------------------------------------------------
# WordBook — Vocabulary Progress Screen
# ---------------------------------------------------------------------------

def _draw_mini_star(surface, cx, cy, size, color):
    """Draw a small filled star polygon."""
    pts = []
    for i in range(10):
        angle = i * math.pi / 5 - math.pi / 2
        r = size if i % 2 == 0 else size * 0.4
        pts.append((cx + math.cos(angle) * r, cy + math.sin(angle) * r))
    pygame.draw.polygon(surface, color, pts)


class WordBook:
    """Fullscreen overlay showing all words with mastery cards, tabs, and arc progress."""

    TAB_LABELS = ["All", "Mastered", "Learning", "New"]

    def __init__(self, mastery_data, tier_unlock):
        self.done = False
        self.result = None
        self._mastery = mastery_data
        self._tier = tier_unlock
        self._scroll_y = 0.0
        self._scroll_vel = 0.0
        self._max_scroll = 0
        self._anim_time = 0.0
        self._active_tab = 0  # 0=All, 1=Mastered, 2=Learning, 3=New
        self._scroll_idle_time = 0.0  # for scroll indicator fade
        self._arc_fill = 0.0
        self._arc_target = 0.0

        # Pre-compute tab rects
        tab_w = 108
        tab_gap = 6
        total_tw = 4 * tab_w + 3 * tab_gap
        tab_start_x = (SCREEN_WIDTH - total_tw) // 2
        tab_y = WORDBOOK_HEADER_H + 2
        self._tab_rects = []
        for i in range(4):
            self._tab_rects.append(pygame.Rect(
                tab_start_x + i * (tab_w + tab_gap), tab_y,
                tab_w, WORDBOOK_TAB_H))

        self._build_all_data()
        self._build_filtered_entries()

    def _build_all_data(self):
        """Organize all vocab into tier-grouped lists and compute stats."""
        from vocabulary import ALL_VOCAB, VOCAB_TIER1, VOCAB_TIER2, VOCAB_TIER3
        self._tier_vocab = [VOCAB_TIER1, VOCAB_TIER2, VOCAB_TIER3]
        self._all_unlocked = [w for w in ALL_VOCAB if w[4] <= self._tier]

        # Stats
        self._mastered_words = []
        self._learning_words = []
        self._new_words = []
        for word in self._all_unlocked:
            data = self._mastery.get(word[1], {})
            box = data.get("box", -1)
            if box == 2:
                self._mastered_words.append(word)
            elif box >= 0:
                self._learning_words.append(word)
            else:
                self._new_words.append(word)

        total = len(self._all_unlocked)
        mastered_count = len(self._mastered_words)
        learning_count = len(self._learning_words)
        self._total_unlocked = total
        self._mastered_count = mastered_count
        self._learning_count = learning_count
        self._new_count = len(self._new_words)

        # Arc target
        if total > 0:
            self._arc_target = (mastered_count + learning_count) / total
        else:
            self._arc_target = 0.0

        # Tier stats: for each tier, count learned (box >= 1) words
        self._tier_stats = []
        for tier_idx, tier_words in enumerate(self._tier_vocab):
            tier_num = tier_idx + 1
            total_in_tier = len(tier_words)
            learned = sum(1 for w in tier_words
                          if self._mastery.get(w[1], {}).get("box", 0) >= 1)
            mastered = sum(1 for w in tier_words
                           if self._mastery.get(w[1], {}).get("box", 0) == 2)
            locked = tier_num > self._tier
            self._tier_stats.append({
                "tier": tier_num, "total": total_in_tier,
                "learned": learned, "mastered": mastered, "locked": locked,
            })

    def _build_filtered_entries(self):
        """Build the list of (type, data) entries for current tab."""
        self._entries = []  # list of ("tier_header", tier_info) or ("card", word)

        # Choose word pool based on tab
        if self._active_tab == 0:
            pool = self._all_unlocked
        elif self._active_tab == 1:
            pool = self._mastered_words
        elif self._active_tab == 2:
            pool = self._learning_words
        else:
            pool = self._new_words

        # Group by tier
        for tier_idx, tier_info in enumerate(self._tier_stats):
            tier_num = tier_idx + 1
            tier_words = [w for w in pool if w[4] == tier_num]
            if not tier_words and tier_info["locked"]:
                # Show locked tier header
                self._entries.append(("tier_header", tier_info))
                continue
            if not tier_words and not tier_info["locked"]:
                continue
            self._entries.append(("tier_header", tier_info))
            for word in tier_words:
                self._entries.append(("card", word))

        # Compute max scroll
        content_h = self._get_content_height()
        list_h = SCREEN_HEIGHT - self._get_list_top() - 10
        self._max_scroll = max(0, content_h - list_h)
        self._scroll_y = min(self._scroll_y, self._max_scroll)

    def _get_list_top(self):
        return WORDBOOK_HEADER_H + WORDBOOK_TAB_H + 10

    def _get_content_height(self):
        h = 0
        for entry_type, _ in self._entries:
            if entry_type == "tier_header":
                h += 36
            else:
                h += WORDBOOK_CARD_H + WORDBOOK_CARD_GAP
        return h

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.done = True
            elif event.key == pygame.K_UP:
                self._scroll_vel -= 150
                self._scroll_idle_time = 0
            elif event.key == pygame.K_DOWN:
                self._scroll_vel += 150
                self._scroll_idle_time = 0
            elif event.key == pygame.K_PAGEUP:
                self._scroll_vel -= 400
                self._scroll_idle_time = 0
            elif event.key == pygame.K_PAGEDOWN:
                self._scroll_vel += 400
                self._scroll_idle_time = 0
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                idx = event.key - pygame.K_1
                if 0 <= idx < 4:
                    self._active_tab = idx
                    self._scroll_y = 0.0
                    self._scroll_vel = 0.0
                    self._build_filtered_entries()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # scroll up
                self._scroll_vel -= WORDBOOK_SCROLL_IMPULSE
                self._scroll_idle_time = 0
            elif event.button == 5:  # scroll down
                self._scroll_vel += WORDBOOK_SCROLL_IMPULSE
                self._scroll_idle_time = 0
            elif event.button == 1:
                for i, r in enumerate(self._tab_rects):
                    if r.collidepoint(mouse_pos):
                        self._active_tab = i
                        self._scroll_y = 0.0
                        self._scroll_vel = 0.0
                        self._build_filtered_entries()
                        return

    def update(self, dt):
        self._anim_time += dt
        # Smooth scroll with friction
        self._scroll_y += self._scroll_vel * dt
        self._scroll_vel *= 0.9 ** (dt * 60)
        self._scroll_y = max(0, min(self._max_scroll, self._scroll_y))
        if abs(self._scroll_vel) < 1:
            self._scroll_vel = 0
        # Scroll indicator idle timer
        if abs(self._scroll_vel) > 0.5:
            self._scroll_idle_time = 0
        else:
            self._scroll_idle_time += dt
        # Arc animation
        self._arc_fill += (self._arc_target - self._arc_fill) * min(1, 5 * dt)

    def draw(self, surface, mouse_pos):
        _draw_overlay_bg(surface)

        font_title = pygame.font.SysFont("Arial", 30, bold=True)
        font_stats = pygame.font.SysFont("Arial", 18)
        font_tab = pygame.font.SysFont("Arial", 16, bold=True)
        font_word = pygame.font.SysFont("Arial", 20)
        font_tier = pygame.font.SysFont("Arial", 16, bold=True)
        font_tier_sub = pygame.font.SysFont("Arial", 14)

        # --- Header ---
        self._draw_header(surface, font_title, font_stats, font_tier_sub)

        # --- Tabs ---
        self._draw_tabs(surface, font_tab, mouse_pos)

        # --- Word list ---
        list_top = self._get_list_top()
        list_bottom = SCREEN_HEIGHT - 10
        clip_rect = pygame.Rect(0, list_top, SCREEN_WIDTH, list_bottom - list_top)
        surface.set_clip(clip_rect)

        card_x = (SCREEN_WIDTH - WORDBOOK_CARD_W) // 2
        y = list_top - int(self._scroll_y)

        for entry_idx, (entry_type, data) in enumerate(self._entries):
            if entry_type == "tier_header":
                tier_info = data
                header_h = 36
                if y + header_h >= list_top - header_h and y < list_bottom + header_h:
                    self._draw_tier_header(surface, y, tier_info, font_tier, font_tier_sub)
                y += header_h
            else:
                word = data
                # Stagger animation
                card_t = max(0, self._anim_time - entry_idx * 0.03)
                x_offset = int(max(0, 1.0 - card_t * 5) * 50)

                if y + WORDBOOK_CARD_H >= list_top - 10 and y < list_bottom + 10:
                    self._draw_card(surface, card_x + x_offset, y,
                                    word, mouse_pos, font_word)
                y += WORDBOOK_CARD_H + WORDBOOK_CARD_GAP

        surface.set_clip(None)

        # --- Scroll indicator ---
        self._draw_scroll_indicator(surface, list_top, list_bottom)

    def _draw_header(self, surface, font_title, font_stats, font_small):
        # Title
        title = font_title.render("Word Book", True, OVERLAY_TITLE_COLOR)
        surface.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 10))

        # Arc progress bar (half-circle)
        arc_cx, arc_cy = SCREEN_WIDTH // 2, 62
        arc_radius = 38
        arc_thick = 7
        # Background arc
        arc_rect = pygame.Rect(arc_cx - arc_radius, arc_cy - arc_radius,
                                arc_radius * 2, arc_radius * 2)
        pygame.draw.arc(surface, (50, 50, 50), arc_rect,
                        0, math.pi, arc_thick)
        # Filled arc (mastered = gold, learning = blue)
        if self._total_unlocked > 0 and self._arc_fill > 0.01:
            fill_angle = self._arc_fill * math.pi
            # Learning portion (blue)
            if self._learning_count > 0:
                pygame.draw.arc(surface, WORDBOOK_LEARNING_COLOR, arc_rect,
                                0, fill_angle, arc_thick)
            # Mastered portion (gold, narrower arc on top)
            if self._mastered_count > 0:
                mastered_ratio = self._mastered_count / self._total_unlocked
                mastered_angle = min(self._arc_fill, mastered_ratio) * math.pi
                pygame.draw.arc(surface, WORDBOOK_MASTERED_COLOR, arc_rect,
                                0, mastered_angle, arc_thick)

        # Count text below arc
        count_text = f"{self._mastered_count + self._learning_count} / {self._total_unlocked} learned"
        ct = font_stats.render(count_text, True, (200, 200, 220))
        surface.blit(ct, (SCREEN_WIDTH // 2 - ct.get_width() // 2, 88))

        # Tier badges
        badge_w = 140
        badge_h = 28
        badge_gap = 8
        total_bw = 3 * badge_w + 2 * badge_gap
        badge_start_x = (SCREEN_WIDTH - total_bw) // 2
        badge_y = 110

        for i, tier_info in enumerate(self._tier_stats):
            bx = badge_start_x + i * (badge_w + badge_gap)
            locked = tier_info["locked"]
            active = (tier_info["tier"] == self._tier and not locked)

            if locked:
                bg_color = (35, 33, 45)
                border_color = (60, 60, 70)
            else:
                bg_color = (50, 45, 70)
                border_color = (100, 90, 130)
                if active:
                    border_color = (140, 120, 180)

            br = pygame.Rect(bx, badge_y, badge_w, badge_h)
            pygame.draw.rect(surface, bg_color, br, border_radius=6)
            pygame.draw.rect(surface, border_color, br, width=1, border_radius=6)

            if locked:
                # Padlock icon
                lx = bx + 12
                ly = badge_y + badge_h // 2
                pygame.draw.rect(surface, (80, 80, 90),
                                 (lx - 4, ly - 2, 8, 7), border_radius=1)
                pygame.draw.arc(surface, (80, 80, 90),
                                pygame.Rect(lx - 3, ly - 7, 6, 8),
                                0, math.pi, 2)
                label = font_small.render("Locked", True, (80, 80, 100))
                surface.blit(label, (lx + 10, badge_y + badge_h // 2 - label.get_height() // 2))
            else:
                # Stars for tier
                star_x = bx + 10
                star_y = badge_y + badge_h // 2
                for s in range(tier_info["tier"]):
                    _draw_mini_star(surface, star_x + s * 10, star_y,
                                    4, WORDBOOK_MASTERED_COLOR)
                label_x = bx + 10 + tier_info["tier"] * 10 + 4
                label = font_small.render(
                    f"Tier {tier_info['tier']}  {tier_info['learned']}/{tier_info['total']}",
                    True, (200, 200, 220))
                surface.blit(label, (label_x, badge_y + badge_h // 2 - label.get_height() // 2))

    def _draw_tabs(self, surface, font_tab, mouse_pos):
        tab_colors = [
            (220, 220, 240),       # All — white
            WORDBOOK_MASTERED_COLOR,
            WORDBOOK_LEARNING_COLOR,
            WORDBOOK_NEW_COLOR,
        ]
        tab_counts = [
            self._total_unlocked,
            self._mastered_count,
            self._learning_count,
            self._new_count,
        ]

        for i, (rect, label) in enumerate(zip(self._tab_rects, self.TAB_LABELS)):
            active = (i == self._active_tab)
            hovered = rect.collidepoint(mouse_pos)
            color = tab_colors[i]

            if active:
                pygame.draw.rect(surface, color, rect, border_radius=14)
                text_color = (20, 18, 30)
            else:
                bg = (60, 55, 75) if hovered else (50, 45, 65)
                pygame.draw.rect(surface, bg, rect, border_radius=14)
                text_color = (170, 170, 190)

            text = f"{label} ({tab_counts[i]})"
            ts = font_tab.render(text, True, text_color)
            surface.blit(ts, (rect.centerx - ts.get_width() // 2,
                              rect.centery - ts.get_height() // 2))

    def _draw_tier_header(self, surface, y, tier_info, font_tier, font_small):
        """Draw a tier divider row with line and label."""
        cx = SCREEN_WIDTH // 2
        tier_num = tier_info["tier"]

        if tier_info["locked"]:
            # Figure out how many more words needed
            prev_tier_idx = tier_num - 2  # tier 2 -> check tier 1 stats (idx 0)
            if 0 <= prev_tier_idx < len(self._tier_stats):
                prev = self._tier_stats[prev_tier_idx]
                needed = max(0, TIER_UNLOCK_THRESHOLD - prev["learned"])
                text = f"Tier {tier_num}: Locked — learn {needed} more Tier {tier_num - 1} words!"
            else:
                text = f"Tier {tier_num}: Locked"
            color = (80, 80, 100)
        else:
            text = f"Tier {tier_num}: {tier_info['learned']}/{tier_info['total']} learned"
            tier_colors = [WORDBOOK_MASTERED_COLOR, WORDBOOK_LEARNING_COLOR, (180, 140, 255)]
            color = tier_colors[min(tier_num - 1, 2)]

        label = font_tier.render(text, True, color)
        lw = label.get_width()
        label_x = cx - lw // 2
        label_y = y + 10

        # Lines on each side
        line_y = label_y + label.get_height() // 2
        margin = 20
        if label_x - margin > margin:
            pygame.draw.line(surface, (60, 58, 75),
                             (margin, line_y), (label_x - 8, line_y), 1)
        if label_x + lw + 8 < SCREEN_WIDTH - margin:
            pygame.draw.line(surface, (60, 58, 75),
                             (label_x + lw + 8, line_y),
                             (SCREEN_WIDTH - margin, line_y), 1)

        surface.blit(label, (label_x, label_y))

        # Inline progress bar for locked tiers
        if tier_info["locked"] and 0 <= tier_num - 2 < len(self._tier_stats):
            prev = self._tier_stats[tier_num - 2]
            bar_w = 60
            bar_h = 6
            bar_x = cx - bar_w // 2
            bar_y = label_y + label.get_height() + 2
            pygame.draw.rect(surface, (50, 50, 50),
                             (bar_x, bar_y, bar_w, bar_h), border_radius=3)
            fill = min(1.0, prev["learned"] / max(1, TIER_UNLOCK_THRESHOLD))
            fill_w = int(fill * bar_w)
            if fill_w > 0:
                pygame.draw.rect(surface, WORDBOOK_LEARNING_COLOR,
                                 (bar_x, bar_y, fill_w, bar_h), border_radius=3)

    def _draw_card(self, surface, x, y, word, mouse_pos, font_word):
        """Draw a single word card with icon, text, and mastery stars."""
        english = word[1]
        data = self._mastery.get(english, {})
        box = data.get("box", -1)
        streak = data.get("streak", 0)

        card_rect = pygame.Rect(x, y, WORDBOOK_CARD_W, WORDBOOK_CARD_H)
        hovered = card_rect.collidepoint(mouse_pos)

        # Card background
        bg = (48, 45, 65) if hovered else (38, 35, 55)
        pygame.draw.rect(surface, bg, card_rect, border_radius=8)

        # Left accent line
        if box == 2:
            accent = WORDBOOK_MASTERED_COLOR
        elif box >= 0:
            accent = WORDBOOK_LEARNING_COLOR
        else:
            accent = (100, 100, 110)
        pygame.draw.rect(surface, accent,
                         (x, y + 4, 2, WORDBOOK_CARD_H - 8), border_radius=1)

        # Icon
        cy = y + WORDBOOK_CARD_H // 2
        _draw_vocab_icon(surface, x + 22, cy, word[3], size=11)

        # Word text
        text = f"{word[0]} = {word[1]}"
        ts = font_word.render(text, True, (220, 220, 240))
        surface.blit(ts, (x + 42, cy - ts.get_height() // 2))

        # Mastery stars (right side)
        star_start_x = x + WORDBOOK_CARD_W - 56
        star_y = cy
        star_size = WORDBOOK_STAR_SIZE
        gray_star = (80, 75, 100)
        gold_star = WORDBOOK_MASTERED_COLOR

        if box == 2:
            # 3 gold stars
            for s in range(3):
                _draw_mini_star(surface, star_start_x + s * 14, star_y,
                                star_size, gold_star)
        elif box == 1:
            # 2 gold, 1 gray
            _draw_mini_star(surface, star_start_x, star_y, star_size, gold_star)
            _draw_mini_star(surface, star_start_x + 14, star_y, star_size, gold_star)
            _draw_mini_star(surface, star_start_x + 28, star_y, star_size, gray_star)
        elif box == 0:
            # 1 gold, 2 gray
            _draw_mini_star(surface, star_start_x, star_y, star_size, gold_star)
            _draw_mini_star(surface, star_start_x + 14, star_y, star_size, gray_star)
            _draw_mini_star(surface, star_start_x + 28, star_y, star_size, gray_star)
        else:
            # 3 gray outline stars
            for s in range(3):
                _draw_mini_star(surface, star_start_x + s * 14, star_y,
                                star_size, gray_star)

        # Streak flame
        if streak >= 3:
            fx = star_start_x + 42
            fy = star_y
            flame_color = (255, 160, 60)
            pygame.draw.circle(surface, flame_color, (fx, fy + 2), 3)
            pygame.draw.polygon(surface, flame_color, [
                (fx - 2, fy + 2), (fx + 2, fy + 2), (fx, fy - 4)])
            pygame.draw.circle(surface, (255, 200, 80), (fx, fy), 2)

    def _draw_scroll_indicator(self, surface, list_top, list_bottom):
        """Draw a scroll bar indicator on the right edge."""
        if self._max_scroll <= 0:
            return

        # Fade out when idle
        alpha = max(0, min(1.0, 1.0 - (self._scroll_idle_time - 1.0) * 2))
        if alpha <= 0:
            return

        bar_x = SCREEN_WIDTH - 6
        bar_h = list_bottom - list_top
        visible_ratio = bar_h / (bar_h + self._max_scroll)
        thumb_h = max(20, int(bar_h * visible_ratio))
        scroll_ratio = self._scroll_y / self._max_scroll if self._max_scroll > 0 else 0
        thumb_y = list_top + int(scroll_ratio * (bar_h - thumb_h))

        color = (100, 90, 130)
        indicator_surf = pygame.Surface((4, thumb_h), pygame.SRCALPHA)
        pygame.draw.rect(indicator_surf, (*color, int(alpha * 180)),
                         (0, 0, 4, thumb_h), border_radius=2)
        surface.blit(indicator_surf, (bar_x, thumb_y))
