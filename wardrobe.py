"""Wardrobe overlay — progressive cosmetic customization system."""

import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    PET_CENTER_X, PET_CENTER_Y, GROUND_Y,
    BADGE_RANKS, WARDROBE_TAB_TIERS,
    WARDROBE_HEADER_H, WARDROBE_PREVIEW_H, WARDROBE_TAB_BAR_H,
    WARDROBE_HINT_BAR_H, WARDROBE_ACCENT_BORDER,
    WARDROBE_CHIP_W, WARDROBE_CHIP_H, WARDROBE_CHIP_GAP,
    WARDROBE_CHIPS_PER_ROW,
    WARDROBE_HAT_TIERS, WARDROBE_GLASSES_TIERS,
    WARDROBE_SCARF_TIERS, WARDROBE_COLLAR_TIERS,
    WARDROBE_SPECIAL_TIERS, WARDROBE_STYLE_TIER, WARDROBE_PATTERN_TIER,
    WARDROBE_COLOR_TIERS,
    WARDROBE_NATURAL_COLORS, WARDROBE_EXOTIC_COLORS,
    WARDROBE_ACCENT_COLORS, WARDROBE_ACCENT_EXPERT,
    WARDROBE_SWATCH_SIZE, WARDROBE_SWATCH_GAP,
    GROWTH_SCALE,
)

# Tab definitions: (key, label)
TABS = [
    ("hats", "Hats"),
    ("glasses", "Glasses"),
    ("colors", "Colors"),
    ("styles", "Styles"),
    ("extras", "Extras"),
    ("special", "Special"),
]

# Style sub-tabs
STYLE_SUB_TABS = ["Fur", "Eyes", "Ears", "Tail"]
EXTRAS_SUB_TABS = ["Scarves", "Collars"]

# Colors
_BG = (35, 22, 74)
_HEADER_BG = (45, 31, 94)
_HEADER_BORDER = (68, 51, 136)
_TAB_ACTIVE = (102, 68, 204)
_TAB_UNLOCKED = (58, 40, 112)
_TAB_LOCKED = (42, 30, 80)
_TAB_ACTIVE_BORDER = (180, 140, 255)
_CHIP_BG = (58, 40, 112)
_CHIP_HOVER = (74, 56, 144)
_CHIP_LOCKED_BG = (42, 30, 80)
_HINT_BG = (30, 20, 69)
_HINT_BORDER = (51, 34, 102)

# Tier badge colors
_TIER_COLORS = {
    2: (100, 180, 255),   # Scholar
    3: (200, 140, 255),   # Expert
    4: (255, 210, 80),    # Master
}
_TIER_NAMES = {1: "Learner", 2: "Scholar", 3: "Expert", 4: "Master"}


class WardrobeOverlay:
    """Full-screen wardrobe overlay for pet customization."""

    def __init__(self, pet, pet_drawer):
        self.pet = pet
        self.pet_drawer = pet_drawer
        self.done = False
        self.result = None

        # Get current rank
        _, self._rank_index = pet.vocab_badge

        # Snapshot original appearance so Back can revert
        self._original_appearance = dict(pet.appearance)
        # Working copy for live preview
        self._preview = dict(pet.appearance)

        # Active tab
        self._active_tab = self._first_unlocked_tab()
        self._active_sub_tab = 0  # for styles/extras

        # Button rects (computed during draw)
        self._back_rect = pygame.Rect(8, 8, 90, 38)
        self._done_rect = pygame.Rect(SCREEN_WIDTH - 98, 8, 90, 38)
        self._tab_rects = []  # (rect, tab_key) list
        self._chip_rects = []  # (rect, item_key, tier) list
        self._sub_tab_rects = []  # (rect, index) list
        self._swatch_rects = []  # (rect, color_list, field, tier) list
        self._pattern_rects = []  # (rect, pattern_key, tier) list
        self._scroll_y = 0  # scroll offset for colors tab

        # LLM text designer (Special tab, Master rank)
        self._llm_text = ""
        self._llm_loading = False
        self._llm_response = ""
        self._llm_cursor_timer = 0.0
        self._llm_send_rect = pygame.Rect(0, 0, 0, 0)

        # Preview surface for pet rendering
        self._preview_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT),
                                            pygame.SRCALPHA)

        # Fonts
        self._font_large = pygame.font.SysFont("Arial", 22, bold=True)
        self._font_medium = pygame.font.SysFont("Arial", 15, bold=True)
        self._font_small = pygame.font.SysFont("Arial", 13)
        self._font_tiny = pygame.font.SysFont("Arial", 10, bold=True)

    def _first_unlocked_tab(self):
        for key, _ in TABS:
            if WARDROBE_TAB_TIERS.get(key, 99) <= self._rank_index:
                return key
        return "hats"

    def _is_tab_unlocked(self, tab_key):
        return WARDROBE_TAB_TIERS.get(tab_key, 99) <= self._rank_index

    # ---- Event handling ----

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._revert()
            return

        # LLM text input (Special tab at Master rank)
        if (self._active_tab == "special" and self._rank_index >= 4
                and event.type == pygame.KEYDOWN and not self._llm_loading):
            if event.key == pygame.K_RETURN:
                self._send_llm_request()
                return
            elif event.key == pygame.K_BACKSPACE:
                self._llm_text = self._llm_text[:-1]
                return
            elif event.unicode and event.unicode.isprintable() and len(self._llm_text) < 80:
                self._llm_text += event.unicode
                return

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        # Back
        if self._back_rect.collidepoint(mouse_pos):
            self._revert()
            return

        # Done
        if self._done_rect.collidepoint(mouse_pos):
            self._commit()
            return

        # Tab clicks
        for rect, tab_key in self._tab_rects:
            if rect.collidepoint(mouse_pos):
                if self._is_tab_unlocked(tab_key):
                    self._active_tab = tab_key
                    self._active_sub_tab = 0
                return

        # Sub-tab clicks
        for rect, idx in self._sub_tab_rects:
            if rect.collidepoint(mouse_pos):
                self._active_sub_tab = idx
                return

        # Item chip clicks
        for rect, item_key, tier in self._chip_rects:
            if rect.collidepoint(mouse_pos) and tier <= self._rank_index:
                self._select_item(item_key)
                return

        # Color swatch clicks
        for rect, color_val, field, tier in self._swatch_rects:
            if rect.collidepoint(mouse_pos) and tier <= self._rank_index:
                self._preview[field] = color_val
                for k, v in self._preview.items():
                    self.pet.appearance[k] = v
                return

        # Pattern chip clicks
        for rect, pattern_key, tier in self._pattern_rects:
            if rect.collidepoint(mouse_pos) and tier <= self._rank_index:
                self._preview["pattern"] = pattern_key
                if pattern_key == "solid":
                    self._preview["pattern_color"] = None
                for k, v in self._preview.items():
                    self.pet.appearance[k] = v
                return

        # LLM send button
        if (self._llm_send_rect.collidepoint(mouse_pos)
                and self._active_tab == "special" and not self._llm_loading
                and self._llm_text.strip()):
            self._send_llm_request()
            return

    def _revert(self):
        for k, v in self._original_appearance.items():
            self.pet.appearance[k] = v
        self.done = True

    def _commit(self):
        for k, v in self._preview.items():
            self.pet.appearance[k] = v
        self.done = True

    def _select_item(self, item_key):
        """Handle item selection based on active tab."""
        tab = self._active_tab
        if tab == "hats":
            self._preview["hat"] = item_key
        elif tab == "glasses":
            self._preview["glasses"] = item_key
        elif tab == "extras":
            sub = EXTRAS_SUB_TABS[self._active_sub_tab]
            if sub == "Scarves":
                self._preview["scarf"] = item_key
            else:
                self._preview["collar"] = item_key
        elif tab == "special":
            self._preview["special"] = item_key
        elif tab == "styles":
            sub = STYLE_SUB_TABS[self._active_sub_tab]
            key_map = {"Fur": "fur_style", "Eyes": "eye_style",
                       "Ears": "ear_style", "Tail": "tail_style"}
            self._preview[key_map[sub]] = item_key

        # Apply to pet for live preview
        for k, v in self._preview.items():
            self.pet.appearance[k] = v

    def _send_llm_request(self):
        """Send text to LLM for appearance generation."""
        import threading
        self._llm_loading = True
        prompt_text = self._llm_text.strip()
        self._llm_text = ""
        self._llm_response = "Designing..."

        def _run():
            try:
                from llm_designer import generate_appearance
                result = generate_appearance(
                    self.pet.pet_type, prompt_text,
                    [],  # no conversation history in wardrobe
                    current_appearance=self.pet.appearance)
                if result:
                    for key in self.pet.appearance:
                        if key in result:
                            self._preview[key] = result[key]
                            self.pet.appearance[key] = result[key]
                    self._llm_response = result.get("flavor_text", "Done!")
                else:
                    self._llm_response = "No changes generated."
            except Exception as e:
                self._llm_response = f"Error: {e}"
            finally:
                self._llm_loading = False

        threading.Thread(target=_run, daemon=True).start()

    # ---- Update ----

    def update(self, dt):
        self._llm_cursor_timer += dt

    # ---- Drawing ----

    def draw(self, surface, mouse_pos):
        surface.fill(_BG)
        self._draw_header(surface, mouse_pos)
        self._draw_preview(surface)
        self._draw_tabs(surface, mouse_pos)

        # Content area
        content_y = WARDROBE_HEADER_H + WARDROBE_PREVIEW_H + WARDROBE_TAB_BAR_H
        tab = self._active_tab
        if tab in ("styles", "extras"):
            content_y += self._draw_sub_tabs(surface, content_y, mouse_pos)

        if self._is_tab_unlocked(tab):
            if tab == "colors":
                self._draw_colors_tab(surface, content_y, mouse_pos)
            else:
                self._draw_items(surface, content_y, mouse_pos)
                if tab == "special" and self._rank_index >= 4:
                    self._draw_llm_input(surface, content_y, mouse_pos)
        else:
            # Locked tab message
            tier = WARDROBE_TAB_TIERS.get(tab, 4)
            rank_name = _TIER_NAMES.get(tier, "Master")
            threshold = BADGE_RANKS[tier][1] if tier < len(BADGE_RANKS) else 50
            msg = f"Reach {rank_name} rank ({threshold} mastered words) to unlock!"
            txt = self._font_small.render(msg, True, (120, 100, 160))
            txt_rect = txt.get_rect(center=(SCREEN_WIDTH // 2,
                                            content_y + 80))
            surface.blit(txt, txt_rect)

        self._draw_hint_bar(surface)

    def _draw_header(self, surface, mouse_pos):
        pygame.draw.rect(surface, _HEADER_BG,
                         (0, 0, SCREEN_WIDTH, WARDROBE_HEADER_H))
        pygame.draw.line(surface, _HEADER_BORDER,
                         (0, WARDROBE_HEADER_H - 1),
                         (SCREEN_WIDTH, WARDROBE_HEADER_H - 1), 2)

        # Back button
        back_hover = self._back_rect.collidepoint(mouse_pos)
        back_color = (80, 60, 130) if back_hover else (68, 51, 136)
        pygame.draw.rect(surface, back_color, self._back_rect, border_radius=8)
        back_txt = self._font_medium.render("\u2190 Back", True, (220, 220, 220))
        back_txt_rect = back_txt.get_rect(center=self._back_rect.center)
        surface.blit(back_txt, back_txt_rect)

        # Title
        title = self._font_large.render("WARDROBE", True, (255, 220, 100))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2,
                                            WARDROBE_HEADER_H // 2))
        surface.blit(title, title_rect)

        # Done button
        done_hover = self._done_rect.collidepoint(mouse_pos)
        done_color = (120, 80, 220) if done_hover else (102, 68, 204)
        pygame.draw.rect(surface, done_color, self._done_rect, border_radius=8)
        done_txt = self._font_medium.render("Done", True, (255, 255, 255))
        done_txt_rect = done_txt.get_rect(center=self._done_rect.center)
        surface.blit(done_txt, done_txt_rect)

    def _draw_preview(self, surface):
        """Draw live pet preview in the preview area."""
        area_y = WARDROBE_HEADER_H
        # Sky + grass background
        sky_rect = (0, area_y, SCREEN_WIDTH, int(WARDROBE_PREVIEW_H * 0.6))
        grass_rect = (0, area_y + int(WARDROBE_PREVIEW_H * 0.6),
                      SCREEN_WIDTH, WARDROBE_PREVIEW_H - int(WARDROBE_PREVIEW_H * 0.6))
        pygame.draw.rect(surface, (135, 206, 235), sky_rect)
        pygame.draw.rect(surface, (80, 160, 60), grass_rect)

        # Render pet onto temp surface at standard position, then scale and blit
        self._preview_surf.fill((0, 0, 0, 0))
        self.pet_drawer.draw(self._preview_surf, self.pet)

        # Crop around pet center and scale to fit preview
        pet_scale = GROWTH_SCALE.get(self.pet.growth_stage, 1.0)
        crop_w = int(180 * pet_scale)
        crop_h = int(160 * pet_scale)
        crop_x = PET_CENTER_X - crop_w // 2
        crop_y = PET_CENTER_Y - int(crop_h * 0.55)
        crop_rect = pygame.Rect(crop_x, crop_y, crop_w, crop_h)
        crop_rect.clamp_ip(self._preview_surf.get_rect())

        pet_crop = self._preview_surf.subsurface(crop_rect).copy()

        # Scale to fit preview area
        preview_scale = 0.85
        target_h = int(WARDROBE_PREVIEW_H * preview_scale)
        aspect = crop_w / max(1, crop_h)
        target_w = int(target_h * aspect)
        scaled = pygame.transform.smoothscale(pet_crop, (target_w, target_h))

        dest_x = (SCREEN_WIDTH - target_w) // 2
        dest_y = area_y + (WARDROBE_PREVIEW_H - target_h) // 2
        surface.blit(scaled, (dest_x, dest_y))

    def _draw_tabs(self, surface, mouse_pos):
        """Draw category tab bar."""
        bar_y = WARDROBE_HEADER_H + WARDROBE_PREVIEW_H
        pygame.draw.rect(surface, (45, 31, 94),
                         (0, bar_y, SCREEN_WIDTH, WARDROBE_TAB_BAR_H))
        pygame.draw.line(surface, _HEADER_BORDER,
                         (0, bar_y + WARDROBE_TAB_BAR_H - 1),
                         (SCREEN_WIDTH, bar_y + WARDROBE_TAB_BAR_H - 1), 2)

        self._tab_rects = []
        total_tabs = len(TABS)
        tab_w = 68
        gap = 4
        total_w = total_tabs * tab_w + (total_tabs - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        tab_y = bar_y + 6
        tab_h = WARDROBE_TAB_BAR_H - 12

        for i, (key, label) in enumerate(TABS):
            x = start_x + i * (tab_w + gap)
            rect = pygame.Rect(x, tab_y, tab_w, tab_h)
            self._tab_rects.append((rect, key))

            unlocked = self._is_tab_unlocked(key)
            active = (key == self._active_tab)
            hover = rect.collidepoint(mouse_pos) and unlocked

            if active:
                bg = _TAB_ACTIVE
                border = _TAB_ACTIVE_BORDER
            elif unlocked:
                bg = _CHIP_HOVER if hover else _TAB_UNLOCKED
                border = None
            else:
                bg = _TAB_LOCKED
                border = None

            pygame.draw.rect(surface, bg, rect, border_radius=14)
            if border:
                pygame.draw.rect(surface, border, rect, 2, border_radius=14)

            # Label
            color = (255, 255, 255) if active else (
                (200, 200, 200) if unlocked else (100, 100, 100))
            alpha = 255 if unlocked else 140
            txt = self._font_small.render(label, True, color)
            if not unlocked:
                txt.set_alpha(alpha)
            txt_rect = txt.get_rect(center=rect.center)

            if not unlocked:
                # Shift text left to make room for lock icon
                txt_rect.centerx = rect.centerx - 6
            surface.blit(txt, txt_rect)

            # Lock icon for locked tabs
            if not unlocked:
                lock_txt = self._font_tiny.render("\U0001F512", True, (100, 100, 100))
                lock_txt.set_alpha(alpha)
                surface.blit(lock_txt, (txt_rect.right + 2, txt_rect.top + 1))

    def _draw_sub_tabs(self, surface, y, mouse_pos):
        """Draw sub-tab row for Styles or Extras. Returns height used."""
        sub_tabs = STYLE_SUB_TABS if self._active_tab == "styles" else EXTRAS_SUB_TABS
        self._sub_tab_rects = []
        h = 28
        pygame.draw.line(surface, (51, 34, 102), (0, y + h - 1),
                         (SCREEN_WIDTH, y + h - 1), 1)

        x = 16
        for i, label in enumerate(sub_tabs):
            txt = self._font_small.render(label, True,
                                          WARDROBE_ACCENT_BORDER if i == self._active_sub_tab
                                          else (136, 136, 136))
            rect = pygame.Rect(x, y, txt.get_width() + 16, h)
            self._sub_tab_rects.append((rect, i))

            surface.blit(txt, (x + 8, y + 6))

            if i == self._active_sub_tab:
                pygame.draw.line(surface, WARDROBE_ACCENT_BORDER,
                                 (x + 4, y + h - 2), (x + txt.get_width() + 12, y + h - 2), 2)

            x += txt.get_width() + 20

        return h

    def _draw_items(self, surface, y, mouse_pos):
        """Draw item chip grid for the active tab."""
        self._chip_rects = []
        items = self._get_items_for_tab()
        if not items:
            return

        # Grid layout
        grid_x = (SCREEN_WIDTH - (WARDROBE_CHIPS_PER_ROW * WARDROBE_CHIP_W +
                  (WARDROBE_CHIPS_PER_ROW - 1) * WARDROBE_CHIP_GAP)) // 2
        row_y = y + 12

        for i, (item_key, label, tier) in enumerate(items):
            col = i % WARDROBE_CHIPS_PER_ROW
            row = i // WARDROBE_CHIPS_PER_ROW
            cx = grid_x + col * (WARDROBE_CHIP_W + WARDROBE_CHIP_GAP)
            cy = row_y + row * (WARDROBE_CHIP_H + WARDROBE_CHIP_GAP)
            rect = pygame.Rect(cx, cy, WARDROBE_CHIP_W, WARDROBE_CHIP_H)
            self._chip_rects.append((rect, item_key, tier))

            unlocked = tier <= self._rank_index
            selected = self._is_selected(item_key)
            hover = rect.collidepoint(mouse_pos) and unlocked

            # Background
            if not unlocked:
                bg = _CHIP_LOCKED_BG
            elif selected:
                bg = _CHIP_HOVER
            elif hover:
                bg = _CHIP_HOVER
            else:
                bg = _CHIP_BG

            pygame.draw.rect(surface, bg, rect, border_radius=10)

            # Selected border
            if selected:
                pygame.draw.rect(surface, WARDROBE_ACCENT_BORDER, rect, 2,
                                 border_radius=10)

            # Label
            color = (255, 255, 255) if (unlocked and (selected or hover)) else (
                (200, 200, 200) if unlocked else (119, 119, 119))
            txt = self._font_medium.render(label, True, color)
            if not unlocked:
                txt.set_alpha(100)
            txt_rect = txt.get_rect(center=rect.center)

            # None icon (circle with slash)
            if item_key is None:
                icon_r = 9
                icon_cx = rect.x + 22
                icon_cy = rect.centery
                ic = (136, 136, 136) if unlocked else (85, 85, 85)
                pygame.draw.circle(surface, ic, (icon_cx, icon_cy), icon_r, 2)
                pygame.draw.line(surface, ic,
                                 (icon_cx - 5, icon_cy + 5),
                                 (icon_cx + 5, icon_cy - 5), 2)
                txt_rect.centerx = rect.centerx + 8

            surface.blit(txt, txt_rect)

            # Tier badge for locked items
            if not unlocked and tier in _TIER_COLORS:
                badge_color = _TIER_COLORS[tier]
                badge_name = _TIER_NAMES.get(tier, "")
                badge_txt = self._font_tiny.render(badge_name, True, badge_color)
                badge_bg = pygame.Surface((badge_txt.get_width() + 8, 14),
                                          pygame.SRCALPHA)
                pygame.draw.rect(badge_bg,
                                 (badge_color[0], badge_color[1], badge_color[2], 50),
                                 badge_bg.get_rect(), border_radius=6)
                badge_x = rect.right - badge_bg.get_width() - 4
                badge_y = rect.top + 3
                surface.blit(badge_bg, (badge_x, badge_y))
                surface.blit(badge_txt, (badge_x + 4, badge_y + 1))

    def _draw_hint_bar(self, surface):
        """Draw the unlock hint bar at the bottom."""
        bar_y = SCREEN_HEIGHT - WARDROBE_HINT_BAR_H
        pygame.draw.rect(surface, _HINT_BG,
                         (0, bar_y, SCREEN_WIDTH, WARDROBE_HINT_BAR_H))
        pygame.draw.line(surface, _HINT_BORDER,
                         (0, bar_y), (SCREEN_WIDTH, bar_y), 1)

        # Find next locked tier
        hint = ""
        for tier_idx in range(self._rank_index + 1, len(BADGE_RANKS)):
            name = BADGE_RANKS[tier_idx][0]
            threshold = BADGE_RANKS[tier_idx][1]
            hint = f"Master {threshold} words to unlock {name} items!"
            break

        if hint:
            txt = self._font_small.render(hint, True, (136, 120, 187))
            txt_rect = txt.get_rect(center=(SCREEN_WIDTH // 2,
                                            bar_y + WARDROBE_HINT_BAR_H // 2))
            surface.blit(txt, txt_rect)

    # ---- LLM text input (Special tab) ----

    def _draw_llm_input(self, surface, content_y, mouse_pos):
        """Draw LLM text input box below the special effects chips."""
        items = self._get_items_for_tab()
        rows = (len(items) + WARDROBE_CHIPS_PER_ROW - 1) // WARDROBE_CHIPS_PER_ROW
        input_y = content_y + 12 + rows * (WARDROBE_CHIP_H + WARDROBE_CHIP_GAP) + 16

        pad_x = 16

        # Section label
        label = self._font_tiny.render("AI DESIGNER", True, WARDROBE_ACCENT_BORDER)
        surface.blit(label, (pad_x, input_y))
        input_y += 18

        # Text input box
        box_w = SCREEN_WIDTH - 2 * pad_x - 70  # leave room for send button
        box_h = 36
        box_rect = pygame.Rect(pad_x, input_y, box_w, box_h)
        pygame.draw.rect(surface, (50, 40, 80), box_rect, border_radius=8)
        pygame.draw.rect(surface, (100, 80, 150), box_rect, 2, border_radius=8)

        # Text content
        display = self._llm_text
        cursor_on = int(self._llm_cursor_timer * 2) % 2 == 0
        if cursor_on and not self._llm_loading:
            display += "|"
        if self._llm_loading:
            display = "Designing..."
        txt = self._font_small.render(display or "Describe your pet's look...",
                                      True,
                                      (200, 200, 220) if display else (120, 110, 150))
        # Clip text to box
        clip_rect = pygame.Rect(pad_x + 8, input_y + 2, box_w - 16, box_h - 4)
        surface.set_clip(clip_rect)
        surface.blit(txt, (pad_x + 10, input_y + 10))
        surface.set_clip(None)

        # Send button
        send_x = pad_x + box_w + 6
        send_rect = pygame.Rect(send_x, input_y, 60, box_h)
        self._llm_send_rect = send_rect
        can_send = self._llm_text.strip() and not self._llm_loading
        send_hover = send_rect.collidepoint(mouse_pos) and can_send
        send_bg = (120, 80, 220) if send_hover else (
            (90, 60, 170) if can_send else (60, 50, 90))
        pygame.draw.rect(surface, send_bg, send_rect, border_radius=8)
        send_txt = self._font_medium.render("Send", True,
                                            (255, 255, 255) if can_send else (120, 120, 140))
        send_txt_rect = send_txt.get_rect(center=send_rect.center)
        surface.blit(send_txt, send_txt_rect)

        # Response text
        if self._llm_response:
            input_y += box_h + 8
            resp_txt = self._font_small.render(self._llm_response[:60], True,
                                               (180, 170, 210))
            surface.blit(resp_txt, (pad_x, input_y))

    # ---- Colors tab ----

    def _draw_colors_tab(self, surface, y, mouse_pos):
        """Draw the Colors tab with palette grids, pattern selector."""
        self._swatch_rects = []
        self._pattern_rects = []
        pad_x = 16
        cur_y = y + 8
        sw = WARDROBE_SWATCH_SIZE
        sg = WARDROBE_SWATCH_GAP
        natural_tier = WARDROBE_COLOR_TIERS["natural"]
        exotic_tier = WARDROBE_COLOR_TIERS["exotic"]

        # --- Body Color ---
        cur_y = self._draw_section_label(surface, "Body Color", pad_x, cur_y)
        cur_y = self._draw_swatch_grid(surface, WARDROBE_NATURAL_COLORS,
                                       "body_color", natural_tier,
                                       pad_x, cur_y, mouse_pos)
        # Exotic colors (locked until Expert)
        cur_y = self._draw_swatch_grid(surface, WARDROBE_EXOTIC_COLORS,
                                       "body_color", exotic_tier,
                                       pad_x, cur_y, mouse_pos)

        cur_y += 4

        # --- Accent Color ---
        cur_y = self._draw_section_label(surface, "Accent Color", pad_x, cur_y)
        cur_y = self._draw_swatch_grid(surface, WARDROBE_ACCENT_COLORS,
                                       "accent_color", natural_tier,
                                       pad_x, cur_y, mouse_pos)
        cur_y = self._draw_swatch_grid(surface, WARDROBE_ACCENT_EXPERT,
                                       "accent_color", exotic_tier,
                                       pad_x, cur_y, mouse_pos)

        cur_y += 4

        # --- Pattern ---
        cur_y = self._draw_section_label(surface, "Pattern", pad_x, cur_y)
        patterns = [
            ("solid", "Solid", natural_tier),
            ("spots", "Spots", WARDROBE_PATTERN_TIER),
            ("stripes", "Stripes", WARDROBE_PATTERN_TIER),
        ]
        cx = pad_x
        for pat_key, pat_label, tier in patterns:
            unlocked = tier <= self._rank_index
            selected = self._preview.get("pattern") == pat_key
            pw = 80
            ph = 28
            rect = pygame.Rect(cx, cur_y, pw, ph)
            self._pattern_rects.append((rect, pat_key, tier))

            if not unlocked:
                bg = _CHIP_LOCKED_BG
            elif selected:
                bg = _CHIP_HOVER
            else:
                bg = _CHIP_BG
            pygame.draw.rect(surface, bg, rect, border_radius=10)
            if selected:
                pygame.draw.rect(surface, WARDROBE_ACCENT_BORDER, rect, 2,
                                 border_radius=10)

            color = (255, 255, 255) if (unlocked and selected) else (
                (200, 200, 200) if unlocked else (100, 100, 100))
            txt = self._font_small.render(pat_label, True, color)
            if not unlocked:
                txt.set_alpha(100)
                # Tier badge
                tier_color = _TIER_COLORS.get(tier, (160, 160, 160))
                badge = self._font_tiny.render(_TIER_NAMES.get(tier, ""), True, tier_color)
                badge.set_alpha(140)
                surface.blit(badge, (rect.right - badge.get_width() - 4, rect.top + 2))
            txt_rect = txt.get_rect(center=rect.center)
            surface.blit(txt, txt_rect)
            cx += pw + 8
        cur_y += ph + 8

        # --- Pattern Color (only if spots or stripes selected) ---
        pat = self._preview.get("pattern")
        if pat in ("spots", "stripes"):
            cur_y = self._draw_section_label(surface, "Pattern Color", pad_x, cur_y)
            pat_colors = [
                [230, 160, 60], [255, 255, 255], [50, 50, 50],
                [255, 136, 136], [136, 200, 255], [255, 210, 100],
            ]
            cur_y = self._draw_swatch_grid(surface, pat_colors, "pattern_color",
                                           WARDROBE_PATTERN_TIER, pad_x, cur_y,
                                           mouse_pos)
        elif pat == "solid":
            label_alpha = 100
            cur_y = self._draw_section_label(surface, "Pattern Color (select Spots or Stripes)",
                                             pad_x, cur_y, alpha=label_alpha)

    def _draw_section_label(self, surface, text, x, y, alpha=255):
        """Draw a section label. Returns y after the label."""
        txt = self._font_tiny.render(text.upper(), True, WARDROBE_ACCENT_BORDER)
        if alpha < 255:
            txt.set_alpha(alpha)
        surface.blit(txt, (x, y))
        return y + txt.get_height() + 4

    def _draw_swatch_grid(self, surface, colors, field, tier, x, y, mouse_pos):
        """Draw a grid of color swatches. Returns y after the grid."""
        sw = WARDROBE_SWATCH_SIZE
        sg = WARDROBE_SWATCH_GAP
        max_per_row = (SCREEN_WIDTH - 2 * x + sg) // (sw + sg)
        cx, cy = x, y
        unlocked = tier <= self._rank_index
        current_val = self._preview.get(field)

        for i, color in enumerate(colors):
            col = i % max_per_row
            if col == 0 and i > 0:
                cx = x
                cy += sw + sg
            rect = pygame.Rect(cx, cy, sw, sw)
            self._swatch_rects.append((rect, list(color), field, tier))

            # Draw swatch
            c = tuple(color)
            if not unlocked:
                # Dimmed
                dimmed = tuple(max(30, v // 3) for v in c)
                pygame.draw.rect(surface, dimmed, rect, border_radius=8)
                # Slash
                pygame.draw.line(surface, (100, 100, 100),
                                 (rect.x + 4, rect.bottom - 4),
                                 (rect.right - 4, rect.y + 4), 2)
            else:
                pygame.draw.rect(surface, c, rect, border_radius=8)
                hover = rect.collidepoint(mouse_pos)
                if hover:
                    pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=8)

            # Selected highlight
            if current_val and list(current_val) == list(color) and unlocked:
                pygame.draw.rect(surface, WARDROBE_ACCENT_BORDER, rect, 3,
                                 border_radius=8)

            # Dark border for very light colors
            brightness = sum(c) / 3
            if brightness > 220 and unlocked:
                pygame.draw.rect(surface, (100, 100, 100), rect, 1, border_radius=8)

            cx += sw + sg

        return cy + sw + sg

    # ---- Item data ----

    def _get_items_for_tab(self):
        """Return list of (item_key, label, min_tier) for current tab."""
        tab = self._active_tab
        if tab == "hats":
            items = [(None, "None", 1)]
            for key, tier in sorted(WARDROBE_HAT_TIERS.items(), key=lambda x: (x[1], x[0])):
                label = key.replace("_", " ").title()
                items.append((key, label, tier))
            return items
        elif tab == "glasses":
            items = [(None, "None", 1)]
            for key, tier in sorted(WARDROBE_GLASSES_TIERS.items(), key=lambda x: (x[1], x[0])):
                label = key.replace("_", " ").title()
                items.append((key, label, tier))
            return items
        elif tab == "styles":
            return self._get_style_items()
        elif tab == "extras":
            return self._get_extras_items()
        elif tab == "special":
            items = [(None, "None", 4)]
            for key, tier in sorted(WARDROBE_SPECIAL_TIERS.items(), key=lambda x: (x[1], x[0])):
                label = key.replace("_", " ").title()
                items.append((key, label, tier))
            return items
        elif tab == "colors":
            return []  # Colors use palette grid, handled separately in Part 4
        return []

    def _get_style_items(self):
        sub = STYLE_SUB_TABS[self._active_sub_tab]
        tier = WARDROBE_STYLE_TIER
        items = [(None, "None", tier)]
        if sub == "Fur":
            for s in ["short", "fluffy", "long", "curly", "spiky", "mohawk"]:
                items.append((s, s.title(), tier))
        elif sub == "Eyes":
            for s in ["big", "sleepy", "sparkly", "wink", "dot"]:
                items.append((s, s.title(), tier))
        elif sub == "Ears":
            for s in ["tiny", "big", "pointy", "floppy", "round"]:
                items.append((s, s.title(), tier))
        elif sub == "Tail":
            for s in ["short", "long", "fluffy", "curly", "ribbon"]:
                items.append((s, s.title(), tier))
        return items

    def _get_extras_items(self):
        sub = EXTRAS_SUB_TABS[self._active_sub_tab]
        if sub == "Scarves":
            items = [(None, "None", 3)]
            for key, tier in sorted(WARDROBE_SCARF_TIERS.items(), key=lambda x: (x[1], x[0])):
                items.append((key, key.title(), tier))
            return items
        else:  # Collars
            items = [(None, "None", 3)]
            for key, tier in sorted(WARDROBE_COLLAR_TIERS.items(), key=lambda x: (x[1], x[0])):
                items.append((key, key.title(), tier))
            return items

    def _is_selected(self, item_key):
        """Check if item_key is currently selected in the preview."""
        tab = self._active_tab
        if tab == "hats":
            return self._preview.get("hat") == item_key
        elif tab == "glasses":
            return self._preview.get("glasses") == item_key
        elif tab == "special":
            return self._preview.get("special") == item_key
        elif tab == "styles":
            sub = STYLE_SUB_TABS[self._active_sub_tab]
            key_map = {"Fur": "fur_style", "Eyes": "eye_style",
                       "Ears": "ear_style", "Tail": "tail_style"}
            return self._preview.get(key_map[sub]) == item_key
        elif tab == "extras":
            sub = EXTRAS_SUB_TABS[self._active_sub_tab]
            if sub == "Scarves":
                return self._preview.get("scarf") == item_key
            else:
                return self._preview.get("collar") == item_key
        return False
