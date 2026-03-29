"""Tamagotchi — Virtual Pet Game. Main entry point."""

import json
import sys
from dotenv import load_dotenv
load_dotenv()
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    DESIGN_WIDTH, DESIGN_HEIGHT, DEFAULT_WINDOW_SCALE,
    STATE_MENU, STATE_PET_SELECT, STATE_NAMING, STATE_PLAYING,
    STATE_PET_RAN_AWAY, STATE_PET_DESIGN,
    PET_CAT, PET_DOG, SAMPLE_RATE, AUDIO_CHANNELS, AUDIO_BUFFER,
    FOODS, CLEANINGS,
    SESSION_SOFT_LIMIT, SESSION_HARD_LIMIT, SESSION_WARNING_INTERVAL,
    AUTOSAVE_INTERVAL, ACTION_SLEEPING,
    DESIGN_THEMES,
    PET_CENTER_X, PET_CENTER_Y,
    KAWAII_BODY_W, KAWAII_TOTAL_H, GROWTH_SCALE,
    WARDROBE_HINT_DURATION, BADGE_RANKS,
)
from pet import Pet
from drawing import PetDrawer
from ui import UI
from audio import SoundManager
from minigames import FoodMenu, CleanMenu, MedicineGame, create_random_minigame
from edu_games import PlayMenu, MemoryGame, FallingWordGame, SpellingGame, QuizGame, WordBook
from save import (list_saves, save_game, load_game, delete_save,
                  find_empty_slot, has_any_save)


class NamePetScreen:
    """Full-screen naming prompt shown after pet type selection."""

    MAX_NAME_LEN = 12

    def __init__(self, pet_type):
        self.pet_type = pet_type
        self.text = ""
        self.done = False
        self.cancelled = False
        self.result = ""
        self._cursor_timer = 0.0
        self._font_large = pygame.font.SysFont("Arial", 44, bold=True)
        self._font_medium = pygame.font.SysFont("Arial", 26)
        self._font_small = pygame.font.SysFont("Arial", 20)

    def handle_event(self, event, mouse_pos):
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self.done = True
            self.cancelled = True
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.done = True
            self.result = self.text.strip() or self.pet_type.capitalize()
        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.unicode and event.unicode.isprintable():
            if len(self.text) < self.MAX_NAME_LEN:
                self.text += event.unicode

    def update(self, dt):
        self._cursor_timer += dt

    def draw(self, surface, mouse_pos):
        # Dark background matching edu-game style
        surface.fill((35, 20, 65))

        # Prompt
        prompt = f"Name your {self.pet_type}:"
        prompt_surf = self._font_large.render(prompt, True, (255, 220, 100))
        prompt_rect = prompt_surf.get_rect(center=(SCREEN_WIDTH // 2, 200))
        surface.blit(prompt_surf, prompt_rect)

        # Text field box
        box_w, box_h = 300, 50
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = 260
        pygame.draw.rect(surface, (50, 45, 80),
                         (box_x, box_y, box_w, box_h), border_radius=8)
        pygame.draw.rect(surface, (120, 100, 160),
                         (box_x, box_y, box_w, box_h), 2, border_radius=8)

        # Text + blinking cursor
        display = self.text
        cursor_on = int(self._cursor_timer * 2) % 2 == 0
        if cursor_on:
            display += "|"
        text_surf = self._font_medium.render(display, True, (240, 240, 255))
        text_rect = text_surf.get_rect(midleft=(box_x + 12, box_y + box_h // 2))
        surface.blit(text_surf, text_rect)

        # Hints
        hint = "Press Enter to confirm   |   Esc to go back"
        hint_surf = self._font_small.render(hint, True, (160, 160, 180))
        hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH // 2, 340))
        surface.blit(hint_surf, hint_rect)

        default = self.pet_type.capitalize()
        default_hint = f"Leave blank for \"{default}\""
        dh_surf = self._font_small.render(default_hint, True, (130, 130, 150))
        dh_rect = dh_surf.get_rect(center=(SCREEN_WIDTH // 2, 370))
        surface.blit(dh_surf, dh_rect)

        # Small kawaii pet preview
        from ui import _draw_outline_pet
        _draw_outline_pet(surface, SCREEN_WIDTH // 2, 480, self.pet_type,
                          0.7, self._cursor_timer)


class PetDesignerScreen:
    """Pet designer screen: style chips + live preview + optional text input."""

    def __init__(self, pet):
        self.pet = pet
        self.done = False
        self.cancelled = False
        self._time = 0.0
        self._font_large = pygame.font.SysFont("Arial", 36, bold=True)
        self._font_medium = pygame.font.SysFont("Arial", 22)
        self._font_small = pygame.font.SysFont("Arial", 18)
        self._font_tiny = pygame.font.SysFont("Arial", 14)
        self._pet_drawer = PetDrawer()

        # Theme chips
        self._themes = list(DESIGN_THEMES.keys())
        self._chip_rects = []
        self._build_chip_rects()
        self._selected_theme = None

        # Text input for LLM
        self._text = ""
        self._has_api = self._check_api()
        self._llm_response = ""
        self._llm_loading = False
        self._suggested_name = ""
        self._cursor_timer = 0.0
        self._conversation_history = []

        # Done/Reset buttons
        btn_w, btn_h = 100, 40
        gap = 20
        total = btn_w * 2 + gap
        start_x = (SCREEN_WIDTH - total) // 2
        btn_y = 560
        self._done_rect = pygame.Rect(start_x, btn_y, btn_w, btn_h)
        self._reset_rect = pygame.Rect(start_x + btn_w + gap, btn_y, btn_w, btn_h)

    def _check_api(self):
        import os
        return bool(os.environ.get("ANTHROPIC_API_KEY"))

    def _build_chip_rects(self):
        chip_w = 90
        chip_h = 32
        gap = 10
        cols = 3
        rows = 2
        total_w = cols * chip_w + (cols - 1) * gap
        start_x = (SCREEN_WIDTH - total_w) // 2
        start_y = 80
        self._chip_rects = []
        for i, name in enumerate(self._themes):
            row = i // cols
            col = i % cols
            x = start_x + col * (chip_w + gap)
            y = start_y + row * (chip_h + gap)
            self._chip_rects.append(pygame.Rect(x, y, chip_w, chip_h))

    def _apply_theme(self, theme_name):
        theme = DESIGN_THEMES.get(theme_name)
        if not theme:
            return
        self._selected_theme = theme_name
        for key, value in theme.items():
            if key in self.pet.appearance:
                self.pet.appearance[key] = value

    def _reset_appearance(self):
        self._selected_theme = None
        self.pet.appearance = {
            "body_color": None, "accent_color": None,
            "pattern": "solid", "pattern_color": None,
            "hat": None, "glasses": None, "scarf": None,
            "collar": None, "special": None,
            "fur_style": None, "tail_style": None,
            "eye_style": None, "ear_style": None,
        }
        self._llm_response = ""
        self._suggested_name = ""
        self._text = ""
        self._conversation_history = []

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.done = True
                self.cancelled = True
                return
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if self._text.strip() and self._has_api and not self._llm_loading:
                    self._send_llm_request()
                return
            # Text input (only if API available)
            if self._has_api:
                if event.key == pygame.K_BACKSPACE:
                    self._text = self._text[:-1]
                elif event.unicode and event.unicode.isprintable():
                    if len(self._text) < 60:
                        self._text += event.unicode
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check theme chips
            for i, rect in enumerate(self._chip_rects):
                if rect.collidepoint(mouse_pos):
                    self._apply_theme(self._themes[i])
                    return

            # Done button
            if self._done_rect.collidepoint(mouse_pos):
                self.done = True
                return

            # Reset button
            if self._reset_rect.collidepoint(mouse_pos):
                self._reset_appearance()
                return

    def _send_llm_request(self):
        """Send text to LLM for appearance generation (runs in background)."""
        import threading
        self._llm_loading = True
        prompt_text = self._text.strip()
        self._text = ""

        def _run():
            try:
                from llm_designer import generate_appearance
                result = generate_appearance(
                    self.pet.pet_type, prompt_text,
                    self._conversation_history,
                    current_appearance=self.pet.appearance)
                if result:
                    self._conversation_history.append(
                        {"role": "user", "content": prompt_text})
                    self._conversation_history.append(
                        {"role": "assistant", "content": json.dumps(result)})
                    # Apply result to appearance
                    for key in self.pet.appearance:
                        if key in result:
                            self.pet.appearance[key] = result[key]
                    if result.get("flavor_text"):
                        self._llm_response = result["flavor_text"]
                    if result.get("suggested_name"):
                        self._suggested_name = result["suggested_name"]
            except Exception as e:
                self._llm_response = f"Error: {e}"
            finally:
                self._llm_loading = False

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()

    def update(self, dt):
        self._time += dt
        self._pet_drawer.update(dt)
        self._cursor_timer += dt

    def draw(self, surface, mouse_pos):
        # Background
        surface.fill((35, 20, 65))

        # Title
        title = self._font_large.render("Design Your Pet!", True, (255, 220, 100))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 40))
        surface.blit(title, title_rect)

        # Theme chips
        for i, rect in enumerate(self._chip_rects):
            name = self._themes[i]
            hovered = rect.collidepoint(mouse_pos)
            selected = name == self._selected_theme

            if selected:
                bg = (100, 80, 140)
                border = (180, 160, 220)
            elif hovered:
                bg = (70, 55, 100)
                border = (140, 120, 180)
            else:
                bg = (50, 40, 75)
                border = (100, 90, 140)

            pygame.draw.rect(surface, bg, rect, border_radius=16)
            pygame.draw.rect(surface, border, rect, 2, border_radius=16)
            txt = self._font_small.render(name, True, (220, 215, 240))
            txt_rect = txt.get_rect(center=rect.center)
            surface.blit(txt, txt_rect)

        # Live pet preview (centered)
        preview_y = 280
        self._pet_drawer.draw(surface, self.pet)

        # Text input box
        input_y = 420
        box_w = 340
        box_h = 36
        box_x = (SCREEN_WIDTH - box_w) // 2
        pygame.draw.rect(surface, (50, 45, 80),
                         (box_x, input_y, box_w, box_h), border_radius=8)
        pygame.draw.rect(surface, (120, 100, 160),
                         (box_x, input_y, box_w, box_h), 2, border_radius=8)

        if self._has_api:
            if self._text:
                display = self._text
                cursor_on = int(self._cursor_timer * 2) % 2 == 0
                if cursor_on:
                    display += "|"
                txt = self._font_small.render(display, True, (240, 240, 255))
            else:
                txt = self._font_small.render("Describe your dream pet...", True,
                                               (120, 110, 150))
        else:
            txt = self._font_tiny.render("Set ANTHROPIC_API_KEY for AI design!",
                                          True, (120, 110, 150))
        surface.blit(txt, (box_x + 10, input_y + box_h // 2 - txt.get_height() // 2))

        # Loading indicator
        if self._llm_loading:
            dots = "." * (int(self._time * 3) % 4)
            loading = self._font_small.render(f"Thinking{dots}", True, (180, 170, 220))
            surface.blit(loading, loading.get_rect(center=(SCREEN_WIDTH // 2, input_y + 50)))
        elif self._llm_response:
            # Flavor text from LLM
            resp = self._font_tiny.render(self._llm_response[:60], True, (180, 200, 220))
            surface.blit(resp, resp.get_rect(center=(SCREEN_WIDTH // 2, input_y + 50)))

        # Suggested name
        if self._suggested_name:
            name_hint = self._font_tiny.render(
                f"Suggested name: {self._suggested_name}", True, (200, 180, 255))
            surface.blit(name_hint, name_hint.get_rect(center=(SCREEN_WIDTH // 2, input_y + 70)))

        # Done + Reset buttons
        for rect, label in [(self._done_rect, "Done!"), (self._reset_rect, "Reset")]:
            hovered = rect.collidepoint(mouse_pos)
            bg = (80, 65, 110) if hovered else (60, 50, 90)
            pygame.draw.rect(surface, bg, rect, border_radius=10)
            pygame.draw.rect(surface, (140, 130, 180), rect, 2, border_radius=10)
            txt = self._font_medium.render(label, True, (240, 235, 255))
            surface.blit(txt, txt.get_rect(center=rect.center))

        # ESC hint
        hint = self._font_tiny.render("ESC to go back", True, (120, 120, 140))
        surface.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, 610)))


class SaveListScreen:
    """Overlay showing 3 save slots for loading or overwriting."""

    SLOT_W = 320
    SLOT_H = 72
    SLOT_GAP = 10

    def __init__(self, mode="load"):
        self.mode = mode  # "load" or "overwrite"
        self.done = False
        self.result = None  # ("load", slot) or ("overwrite", slot) or None
        self._saves = list_saves()
        self._font_large = pygame.font.SysFont("Arial", 32, bold=True)
        self._font_medium = pygame.font.SysFont("Arial", 20, bold=True)
        self._font_small = pygame.font.SysFont("Arial", 16)
        self._font_hint = pygame.font.SysFont("Arial", 14)
        self._time = 0.0

        # Compute slot rects (centered)
        total_h = 3 * self.SLOT_H + 2 * self.SLOT_GAP
        start_y = (SCREEN_HEIGHT - total_h) // 2 + 20
        sx = (SCREEN_WIDTH - self.SLOT_W) // 2
        self._slot_rects = []
        for i in range(3):
            y = start_y + i * (self.SLOT_H + self.SLOT_GAP)
            self._slot_rects.append(pygame.Rect(sx, y, self.SLOT_W, self.SLOT_H))

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.done = True
            self.result = None
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self._slot_rects):
                if rect.collidepoint(mouse_pos):
                    slot_num = i + 1
                    save_info = self._saves[i]
                    if self.mode == "load":
                        if save_info is not None:
                            self.result = ("load", slot_num)
                            self.done = True
                    else:  # overwrite
                        self.result = ("overwrite", slot_num)
                        self.done = True

    def update(self, dt):
        self._time += dt

    def draw(self, surface, mouse_pos):
        from ui import _draw_outline_pet

        # Full overlay background
        surface.fill((20, 18, 30))

        # Title
        if self.mode == "load":
            title = "Continue"
            subtitle = "Pick a save to load"
        else:
            title = "New Game"
            subtitle = "Pick a save to replace"

        title_surf = self._font_large.render(title, True, (255, 220, 100))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
        surface.blit(title_surf, title_rect)

        sub_surf = self._font_small.render(subtitle, True, (180, 180, 200))
        sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 115))
        surface.blit(sub_surf, sub_rect)

        # Draw 3 slot rows
        for i, rect in enumerate(self._slot_rects):
            save_info = self._saves[i]
            hovered = rect.collidepoint(mouse_pos)

            if save_info is not None:
                # Occupied slot
                bg = (60, 55, 85) if hovered else (45, 40, 70)
                pygame.draw.rect(surface, bg, rect, border_radius=12)
                pygame.draw.rect(surface, (120, 100, 160), rect, 2,
                                 border_radius=12)

                # Pet icon (small kawaii head)
                icon_cx = rect.x + 45
                icon_cy = rect.y + rect.height // 2
                _draw_outline_pet(surface, icon_cx, icon_cy,
                                  save_info["pet_type"], 0.35, self._time,
                                  ow=1)

                # Pet name
                name_surf = self._font_medium.render(save_info["name"], True,
                                                     (240, 240, 255))
                surface.blit(name_surf, (rect.x + 80, rect.y + 15))

                # Date
                date_str = save_info.get("date", "")
                if date_str:
                    date_surf = self._font_small.render(date_str, True,
                                                        (140, 140, 160))
                    surface.blit(date_surf, (rect.x + 80, rect.y + 42))

                # Slot number
                slot_surf = self._font_hint.render(f"Slot {i + 1}", True,
                                                    (100, 100, 120))
                surface.blit(slot_surf, (rect.right - 50, rect.y + 8))

            else:
                # Empty slot — dashed border look
                bg = (35, 32, 50) if hovered and self.mode == "overwrite" else (30, 28, 45)
                pygame.draw.rect(surface, bg, rect, border_radius=12)
                # Dashed border (simulated with dotted rect)
                dash_color = (80, 75, 100)
                for dx in range(0, rect.width, 8):
                    pygame.draw.line(surface, dash_color,
                                     (rect.x + dx, rect.y),
                                     (rect.x + min(dx + 4, rect.width), rect.y), 1)
                    pygame.draw.line(surface, dash_color,
                                     (rect.x + dx, rect.bottom - 1),
                                     (rect.x + min(dx + 4, rect.width), rect.bottom - 1), 1)
                for dy in range(0, rect.height, 8):
                    pygame.draw.line(surface, dash_color,
                                     (rect.x, rect.y + dy),
                                     (rect.x, rect.y + min(dy + 4, rect.height)), 1)
                    pygame.draw.line(surface, dash_color,
                                     (rect.right - 1, rect.y + dy),
                                     (rect.right - 1, rect.y + min(dy + 4, rect.height)), 1)

                # "Empty" text
                empty_surf = self._font_small.render("Empty", True,
                                                      (100, 100, 120))
                empty_rect = empty_surf.get_rect(center=rect.center)
                surface.blit(empty_surf, empty_rect)

                # Slot number
                slot_surf = self._font_hint.render(f"Slot {i + 1}", True,
                                                    (80, 80, 100))
                surface.blit(slot_surf, (rect.right - 50, rect.y + 8))

        # ESC hint
        hint_surf = self._font_hint.render("ESC to go back", True,
                                            (120, 120, 140))
        hint_rect = hint_surf.get_rect(center=(SCREEN_WIDTH // 2,
                                                SCREEN_HEIGHT - 40))
        surface.blit(hint_surf, hint_rect)


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=SAMPLE_RATE, channels=AUDIO_CHANNELS,
                          buffer=AUDIO_BUFFER)
        win_w = int(DESIGN_WIDTH * DEFAULT_WINDOW_SCALE)
        win_h = int(DESIGN_HEIGHT * DEFAULT_WINDOW_SCALE)
        self.screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
        pygame.display.set_caption(TITLE)
        self.design_surface = pygame.Surface((DESIGN_WIDTH, DESIGN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.ui = UI()
        self.sound = SoundManager()
        self.pet_drawer = PetDrawer()

        self.state = STATE_MENU
        self.pet = None
        self.time = 0.0
        self.last_dt = 1 / 60
        self.runaway_sound_played = False
        self.sub_state = None

        # Session limits
        self.session_seconds = 0.0
        self.session_paused = False
        self.session_warning_shown = 0.0
        self._show_break_warning = False
        self._break_warning_timer = 0.0

        # Save system
        self._active_slot = None
        self.autosave_timer = 0.0
        self._save_toast_timer = 0.0

        # Wardrobe hint tooltip
        self._wardrobe_hint_timer = 0.0

        # Badge rank tracking for celebration
        self._last_badge_rank = 0
        self._badge_celebration_timer = 0.0
        self._badge_celebration_data = None  # (rank_name, rank_color, unlocked_items)

    def _transform_mouse(self, pos):
        """Map window mouse coordinates to design surface coordinates."""
        mx, my = pos
        sw, sh = self.screen.get_size()
        return (int(mx * DESIGN_WIDTH / sw), int(my * DESIGN_HEIGHT / sh))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.time += dt
            mouse_pos = self._transform_mouse(pygame.mouse.get_pos())

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(
                        (event.w, event.h), pygame.RESIZABLE)
                self._handle_event(event, mouse_pos)

            self._update(dt)
            self._draw(mouse_pos)

            # Scale design surface to window and present
            scaled = pygame.transform.smoothscale(
                self.design_surface, self.screen.get_size())
            self.screen.blit(scaled, (0, 0))
            pygame.display.flip()

        if self.pet:
            self._save()
        pygame.quit()
        sys.exit()

    def _handle_event(self, event, mouse_pos):
        if self.state == STATE_MENU:
            self._handle_menu_event(event, mouse_pos)
        elif self.state == STATE_PET_SELECT:
            self._handle_pet_select_event(event, mouse_pos)
        elif self.state == STATE_PET_DESIGN:
            self._designer_screen.handle_event(event, mouse_pos)
        elif self.state == STATE_NAMING:
            self._naming_screen.handle_event(event, mouse_pos)
        elif self.state == STATE_PLAYING:
            self._handle_playing_event(event, mouse_pos)
        elif self.state == STATE_PET_RAN_AWAY:
            self._handle_ran_away_event(event)

    def _handle_menu_event(self, event, mouse_pos):
        # If a sub-state (SaveListScreen) is active, delegate to it
        if self.sub_state is not None:
            self.sub_state.handle_event(event, mouse_pos)
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.ui.menu_new_btn.is_clicked(mouse_pos):
                self.sound.play("select")
                self._do_new_game()
            elif self.ui.menu_continue_btn.is_clicked(mouse_pos):
                self.sound.play("select")
                self._do_continue()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == pygame.K_n:
                self.sound.play("select")
                self._do_new_game()
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_c):
                self.sound.play("select")
                self._do_continue()

    def _do_new_game(self):
        """Handle 'New' button press."""
        empty = find_empty_slot()
        if empty is not None:
            self._active_slot = empty
            self.state = STATE_PET_SELECT
        else:
            self.sub_state = SaveListScreen(mode="overwrite")

    def _do_continue(self):
        """Handle 'Continue' button press."""
        if has_any_save():
            self.sub_state = SaveListScreen(mode="load")

    def _handle_pet_select_event(self, event, mouse_pos):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = STATE_MENU
            elif event.key == pygame.K_1:
                self._start_game(PET_CAT)
            elif event.key == pygame.K_2:
                self._start_game(PET_DOG)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.ui.cat_button.is_clicked(mouse_pos):
                self._start_game(PET_CAT)
            elif self.ui.dog_button.is_clicked(mouse_pos):
                self._start_game(PET_DOG)

    def _handle_playing_event(self, event, mouse_pos):
        if self.session_paused:
            # Only allow ESC when session is hard-capped
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._save()
                self.state = STATE_MENU
                self.pet = None
            return
        if self.sub_state is not None:
            self.sub_state.handle_event(event, mouse_pos)
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._save()
                self.state = STATE_MENU
                self.pet = None
            elif event.key == pygame.K_1:
                self._do_feed()
            elif event.key == pygame.K_2:
                self._do_play()
            elif event.key == pygame.K_3:
                self._do_clean()
            elif event.key == pygame.K_4:
                self._do_sleep()
            elif event.key == pygame.K_5:
                self._do_medicine()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.ui.buttons["feed"].is_clicked(mouse_pos):
                self.ui.buttons["feed"].click()
                self._do_feed()
            elif self.ui.buttons["play"].is_clicked(mouse_pos):
                self.ui.buttons["play"].click()
                self._do_play()
            elif self.ui.buttons["clean"].is_clicked(mouse_pos):
                self.ui.buttons["clean"].click()
                self._do_clean()
            elif self.ui.buttons["sleep"].is_clicked(mouse_pos):
                self.ui.buttons["sleep"].click()
                self._do_sleep()
            elif "medicine" in self.ui.buttons and self.ui.buttons["medicine"].is_clicked(mouse_pos):
                self.ui.buttons["medicine"].click()
                self._do_medicine()
            elif self.ui.save_btn_rect.collidepoint(mouse_pos):
                self.sound.play("click")
                self.ui._save_press_timer = 0.15
                self._save()
                self._save_toast_timer = 1.5
            elif self._badge_celebration_timer > 0:
                # Click anywhere to dismiss celebration toast
                self._badge_celebration_timer = 0.0
            elif self._pet_hit_rect().collidepoint(mouse_pos):
                self._do_wardrobe_tap()

    def _handle_ran_away_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.sound.play("select")
                self.state = STATE_PET_SELECT
            elif event.key == pygame.K_ESCAPE:
                self.state = STATE_MENU

    def _start_game(self, pet_type):
        self.sound.play("select")
        self.pet = Pet(pet_type)
        self.pet_drawer = PetDrawer()
        self._designer_screen = PetDesignerScreen(self.pet)
        self.state = STATE_PET_DESIGN
        self.runaway_sound_played = False
        self._last_badge_rank = 0
        self.sub_state = None

    def _do_feed(self):
        if self.pet and self.pet.action != "running_away":
            self.sound.play("click")
            self.sub_state = FoodMenu()

    def _do_play(self):
        if self.pet and self.pet.action != "running_away":
            self.sound.play("click")
            self.sub_state = PlayMenu()

    def _do_clean(self):
        if self.pet and self.pet.action != "running_away":
            self.sound.play("click")
            self.sub_state = CleanMenu(self.pet.poop_piles)

    def _do_medicine(self):
        if self.pet and self.pet.is_sick and self.pet.action != "running_away":
            self.sound.play("click")
            self.sub_state = MedicineGame(self.sound)

    def _pet_hit_rect(self):
        """Return a pygame.Rect bounding box around the pet for click detection."""
        import pygame as _pg
        scale = GROWTH_SCALE.get(self.pet.growth_stage, 1.0)
        w = int(KAWAII_BODY_W * 2 * scale) + 30
        h = int(KAWAII_TOTAL_H * scale) + 30
        return _pg.Rect(PET_CENTER_X - w // 2, PET_CENTER_Y - h // 2 - 10, w, h)

    def _do_wardrobe_tap(self):
        """Handle tapping on the pet — show hint or open wardrobe."""
        if not self.pet or self.pet.action == "running_away":
            return
        rank_name, rank_index = self.pet.vocab_badge
        if rank_index < 1:
            # Novice — show tooltip hint
            self._wardrobe_hint_timer = WARDROBE_HINT_DURATION
            self.sound.play("click")
        else:
            # Learner+ — open wardrobe overlay
            self.sound.play("click")
            from wardrobe import WardrobeOverlay
            self.sub_state = WardrobeOverlay(self.pet, self.pet_drawer)

    def _check_badge_rank_up(self):
        """Check if vocab badge rank increased and trigger celebration."""
        if not self.pet:
            return
        _, new_rank = self.pet.vocab_badge
        if new_rank > self._last_badge_rank:
            rank_name = BADGE_RANKS[new_rank][0]
            rank_color = BADGE_RANKS[new_rank][3]
            # Build unlocked items list
            unlocked = self._get_rank_unlocks(new_rank)
            self._badge_celebration_data = (rank_name, rank_color, unlocked)
            self._badge_celebration_timer = 4.0
            self._last_badge_rank = new_rank
            self.sound.play("level_up")

    def _get_rank_unlocks(self, rank_index):
        """Return list of item labels that just unlocked at this rank."""
        from settings import (WARDROBE_HAT_TIERS, WARDROBE_GLASSES_TIERS,
                              WARDROBE_TAB_TIERS)
        items = []
        # Hats
        for key, tier in WARDROBE_HAT_TIERS.items():
            if tier == rank_index:
                items.append(key.replace("_", " ").title())
        # Glasses
        for key, tier in WARDROBE_GLASSES_TIERS.items():
            if tier == rank_index:
                items.append(key.replace("_", " ").title())
        # Tab unlocks
        for tab_key, tier in WARDROBE_TAB_TIERS.items():
            if tier == rank_index:
                items.append(f"{tab_key.title()} Tab")
        return items

    def _do_sleep(self):
        if self.pet:
            was_sleeping = self.pet.action == "sleeping"
            self.pet.toggle_sleep()
            self.sound.play("wake" if was_sleeping else "sleep")

    def _update(self, dt):
        self.last_dt = dt
        self.ui.update(dt)

        # Break warning countdown
        if self._show_break_warning:
            self._break_warning_timer += dt
            if self._break_warning_timer >= 4.0:
                self._show_break_warning = False
                self._break_warning_timer = 0.0

        if self.state == STATE_MENU and self.sub_state is not None:
            self.sub_state.update(dt)
            if self.sub_state.done:
                sub = self.sub_state
                self.sub_state = None
                if sub.result:
                    action, slot = sub.result
                    if action == "load":
                        self._active_slot = slot
                        self._load_slot(slot)
                    elif action == "overwrite":
                        delete_save(slot)
                        self._active_slot = slot
                        self.state = STATE_PET_SELECT
        elif self.state == STATE_PET_DESIGN:
            self._designer_screen.update(dt)
            if self._designer_screen.done:
                if self._designer_screen.cancelled:
                    self.state = STATE_PET_SELECT
                    self.pet = None
                else:
                    # Pre-fill suggested name if LLM suggested one
                    suggested = self._designer_screen._suggested_name
                    self._naming_screen = NamePetScreen(self.pet.pet_type)
                    if suggested:
                        self._naming_screen.text = suggested
                    self.state = STATE_NAMING
        elif self.state == STATE_NAMING:
            self._naming_screen.update(dt)
            if self._naming_screen.done:
                if self._naming_screen.cancelled:
                    # Go back to designer, not pet select
                    self._designer_screen = PetDesignerScreen(self.pet)
                    self.state = STATE_PET_DESIGN
                else:
                    self.pet.name = self._naming_screen.result
                    self.state = STATE_PLAYING
                    self._last_badge_rank = self.pet.vocab_badge[1]
        elif self.state == STATE_PLAYING and self.pet:
            # Session timer
            if not self.session_paused:
                self.session_seconds += dt
                self.pet.total_play_seconds += dt

                # Hard cap
                if self.session_seconds >= SESSION_HARD_LIMIT:
                    self.session_paused = True
                    if self.pet.action != ACTION_SLEEPING:
                        self.pet.toggle_sleep()
                    self._save()
                # Soft warning
                elif self.session_seconds >= SESSION_SOFT_LIMIT:
                    if (self.session_seconds - self.session_warning_shown
                            >= SESSION_WARNING_INTERVAL):
                        self.session_warning_shown = self.session_seconds
                        self._show_break_warning = True
                        self._break_warning_timer = 0.0

            # Auto-save
            self.autosave_timer += dt
            if self.autosave_timer >= AUTOSAVE_INTERVAL:
                self.autosave_timer = 0.0
                self._save()

            # Save toast countdown
            if self._save_toast_timer > 0:
                self._save_toast_timer = max(0.0, self._save_toast_timer - dt)

            # Wardrobe hint countdown
            if self._wardrobe_hint_timer > 0:
                self._wardrobe_hint_timer = max(0.0, self._wardrobe_hint_timer - dt)

            # Badge celebration countdown
            if self._badge_celebration_timer > 0:
                self._badge_celebration_timer = max(0.0, self._badge_celebration_timer - dt)

            if self.sub_state is not None:
                self.sub_state.update(dt)
                self.pet_drawer.update(dt)  # keep idle animations alive
                if self.sub_state.done:
                    self._resolve_sub_state()
            else:
                prev_poop = self.pet.poop_piles
                self.pet.update(dt)
                self.pet_drawer.update(dt)

                if self.pet.poop_piles > prev_poop:
                    self.sound.play("poop")

                # Dynamic button rebuild
                show_meds = self.pet.is_sick and self.pet.action != "running_away"
                if ("medicine" in self.ui.buttons) != show_meds:
                    self.ui.rebuild_buttons(show_meds)

                # Check if pet just started running away
                if self.pet.action == "running_away" and not self.runaway_sound_played:
                    self.sound.play("runaway")
                    self.runaway_sound_played = True

                # Transition to ran away state
                if self.pet.has_run_away:
                    if self._active_slot:
                        delete_save(self._active_slot)
                    self.state = STATE_PET_RAN_AWAY

    def _resolve_sub_state(self):
        sub = self.sub_state
        self.sub_state = None

        # PlayMenu → launch selected game
        if isinstance(sub, PlayMenu):
            if sub.result:
                if sub.result == "fun":
                    self.sub_state = create_random_minigame(self.sound)
                elif sub.result == "memory":
                    self.sub_state = MemoryGame(
                        self.sound, mastery_data=self.pet.word_mastery,
                        day_count=self.pet.day_count,
                        level=self.pet.level)
                elif sub.result == "falling":
                    self.sub_state = FallingWordGame(
                        self.sound, mastery_data=self.pet.word_mastery,
                        day_count=self.pet.day_count,
                        level=self.pet.level)
                elif sub.result == "spelling":
                    self.sub_state = SpellingGame(
                        self.sound, mastery_data=self.pet.word_mastery,
                        day_count=self.pet.day_count,
                        level=self.pet.level)
                elif sub.result == "quiz":
                    self.sub_state = QuizGame(
                        self.sound, mastery_data=self.pet.word_mastery,
                        day_count=self.pet.day_count,
                        level=self.pet.level)
                elif sub.result == "wordbook":
                    from vocabulary import get_unlocked_tier
                    self.sub_state = WordBook(
                        self.pet.word_mastery,
                        get_unlocked_tier(self.pet.word_mastery))
            return

        # WordBook (no rewards, just close)
        if isinstance(sub, WordBook):
            return

        # Educational games (result is a dict with happiness + xp)
        if isinstance(sub, (MemoryGame, FallingWordGame,
                            SpellingGame, QuizGame)):
            if sub.result and isinstance(sub.result, dict):
                happiness = sub.result.get("happiness", 0)
                xp = sub.result.get("xp", 0)
                if happiness > 0:
                    self.pet.boost_happiness(happiness)
                if xp > 0:
                    if self.pet.add_xp(xp):
                        self.sound.play("level_up")
                self.pet.record_edu_game()
                self.sound.play("play")
            if hasattr(sub, 'word_results'):
                for english_word, was_correct in sub.word_results:
                    self.pet.record_word_result(english_word, was_correct)
            # Check for rank-up
            self._check_badge_rank_up()
            return

        # Food / Clean / Medicine / Fun games
        if isinstance(sub, FoodMenu):
            if sub.result:
                name, hunger, happiness, energy = sub.result
                # Look up food index and color from FOODS list
                food_index = -1
                food_color = None
                for i, (fn, _h, _hp, _e, fc) in enumerate(FOODS):
                    if fn == name:
                        food_index = i
                        food_color = fc
                        break
                self.pet.feed_food(hunger, happiness, energy,
                                   food_index=food_index, food_color=food_color)
                self.sound.play("feed")
                self.sound.speak(name.lower())
        elif isinstance(sub, CleanMenu):
            if sub.result:
                name, cleanliness, happiness, energy = sub.result
                # Look up clean index from CLEANINGS list
                clean_index = -1
                for i, (cn, _c, _h, _e, _cc) in enumerate(CLEANINGS):
                    if cn == name:
                        clean_index = i
                        break
                if name == "Pick Up":
                    self.pet.pick_up_poop()
                    # Also trigger cleaning animation for visual feedback
                    self.pet.clean_with(0, 0, 0, clean_index=clean_index)
                else:
                    self.pet.clean_with(cleanliness, happiness, energy,
                                        clean_index=clean_index)
                self.sound.play("clean")
        elif isinstance(sub, MedicineGame):
            if sub.result:
                outcome, value = sub.result
                if outcome == "full":
                    self.pet.cure_sickness(stat_restore=value)
                    self.sound.play("medicine")
                elif outcome == "partial":
                    self.pet.cure_sickness(stat_restore=0)
                    self.sound.play("medicine")
                else:  # fail
                    self.pet.sick_timer = max(0, self.pet.sick_timer - value)
                    self.sound.play("wrong")
        else:  # fun mini game (CatchTreats, PopBubbles, ChaseBall)
            if sub.result and sub.result > 0:
                self.pet.boost_happiness(sub.result)
                self.sound.play("play")

    def _save(self):
        if self.pet and not self.pet.has_run_away and self._active_slot:
            from datetime import date
            save_game(self._active_slot, self.pet,
                      session_date=str(date.today()))

    def _load_slot(self, slot):
        data = load_game(slot)
        if data and "pet" in data:
            self._active_slot = slot
            self.pet = Pet.from_dict(data["pet"])
            self.pet_drawer = PetDrawer()
            self.state = STATE_PLAYING
            self.session_seconds = 0.0
            self.session_paused = False
            self.session_warning_shown = 0.0
            self.runaway_sound_played = False
            self.sub_state = None
            self._last_badge_rank = self.pet.vocab_badge[1]

    def _draw(self, mouse_pos):
        surface = self.design_surface

        if self.state == STATE_MENU:
            self.ui.draw_menu(surface, self.time, mouse_pos)
            if self.sub_state is not None:
                self.sub_state.draw(surface, mouse_pos)

        elif self.state == STATE_PET_SELECT:
            self.ui.draw_pet_select(surface, mouse_pos, self.time)

        elif self.state == STATE_PET_DESIGN:
            self._designer_screen.draw(surface, mouse_pos)

        elif self.state == STATE_NAMING:
            self._naming_screen.draw(surface, mouse_pos)

        elif self.state == STATE_PLAYING and self.pet:
            # Room background
            self.ui.draw_room(surface, self.pet.day_progress)

            if self.sub_state is not None:
                # Game overlay active — skip pet/poop/HUD for a clean overlay
                self.sub_state.draw(surface, mouse_pos)
            else:
                # Pet
                self.pet_drawer.draw(surface, self.pet)

                # Poop piles on floor
                if self.pet.poop_piles > 0:
                    self.ui.draw_poop_piles(surface, self.pet.poop_piles)

                # UI overlays (only when no game overlay)
                self.ui.draw_day_info(surface, self.pet)
                self.ui.draw_stat_bars(surface, self.pet)
                self.ui.draw_xp_bar(surface, self.pet)
                self.ui.draw_vocab_badge(surface, self.pet)
                if not self.session_paused:
                    self.ui.draw_save_button(surface, mouse_pos)
                    if self._save_toast_timer > 0:
                        self.ui.draw_save_toast(surface, self._save_toast_timer)
                self.ui.draw_mood_text(surface, self.pet)
                self.ui.draw_sick_warning(surface, self.pet)
                if not self.session_paused:
                    self.ui.draw_action_buttons(surface, mouse_pos, self.last_dt)

                # Wardrobe hint tooltip (novice rank)
                if self._wardrobe_hint_timer > 0:
                    mastered = sum(1 for d in self.pet.word_mastery.values()
                                   if d.get("box") == 2)
                    needed = BADGE_RANKS[1][1] - mastered  # words until Learner
                    self.ui.draw_wardrobe_hint(surface, self._wardrobe_hint_timer,
                                               mastered_needed=max(1, needed))

                # Badge rank-up celebration
                if self._badge_celebration_timer > 0 and self._badge_celebration_data:
                    rname, rcolor, ritems = self._badge_celebration_data
                    self.ui.draw_badge_celebration(surface, rname, rcolor,
                                                   ritems, self._badge_celebration_timer)

                # Stage-up celebration
                if self.pet.stage_just_changed:
                    self.ui.draw_stage_up(surface, self.pet)

                # Session warnings
                if self.session_paused:
                    self.ui.draw_hard_cap_overlay(surface, self.pet)
                elif self._show_break_warning:
                    self.ui.draw_break_warning(surface)

        elif self.state == STATE_PET_RAN_AWAY and self.pet:
            self.ui.draw_ran_away(surface, self.pet, self.time)


if __name__ == "__main__":
    Game().run()
