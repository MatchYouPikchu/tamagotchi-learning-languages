"""UI elements — stat bars, buttons, backgrounds, day/night sky, menus."""

import math
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    STAT_BAR_X, STAT_BAR_Y_START, STAT_BAR_WIDTH, STAT_BAR_HEIGHT,
    STAT_BAR_SPACING, STAT_BAR_LABEL_WIDTH,
    BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_SPACING, BUTTON_COUNT,
    GROUND_Y,
    COLOR_HUNGER, COLOR_HAPPINESS, COLOR_ENERGY, COLOR_CLEANLINESS,
    COLOR_STAT_BG, COLOR_STAT_BORDER,
    COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_BUTTON_TEXT,
    COLOR_TITLE, COLOR_SUBTITLE, COLOR_MOOD_TEXT, COLOR_DAY_TEXT,
    SKY_DAY, SKY_SUNSET, SKY_NIGHT, SKY_DAWN,
    GRASS_GREEN, GRASS_DARK,
    WHITE, BLACK, DARK_GRAY, LIGHT_GRAY,
    STAT_MAX,
    DAY_PHASE_LENGTH, DAY_LENGTH,
)


def _lerp_color(c1, c2, t):
    """Linearly interpolate between two colors."""
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


class Button:
    def __init__(self, x, y, width, height, text, shortcut_label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.shortcut_label = shortcut_label
        self.hovered = False

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface, font, small_font=None):
        color = COLOR_BUTTON_HOVER if self.hovered else COLOR_BUTTON
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect, 2, border_radius=8)

        text_surf = font.render(self.text, True, COLOR_BUTTON_TEXT)
        text_rect = text_surf.get_rect(center=(self.rect.centerx,
                                                self.rect.centery - (4 if self.shortcut_label else 0)))
        surface.blit(text_surf, text_rect)

        if self.shortcut_label and small_font:
            key_surf = small_font.render(self.shortcut_label, True, LIGHT_GRAY)
            key_rect = key_surf.get_rect(center=(self.rect.centerx,
                                                  self.rect.bottom - 12))
            surface.blit(key_surf, key_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


class UI:
    def __init__(self):
        self.font_large = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 22)
        self.font_small = pygame.font.SysFont("Arial", 16)
        self.font_tiny = pygame.font.SysFont("Arial", 13)
        self.font_title = pygame.font.SysFont("Arial", 48, bold=True)

        # Create action buttons
        total_width = (BUTTON_COUNT * BUTTON_WIDTH
                       + (BUTTON_COUNT - 1) * BUTTON_SPACING)
        start_x = (SCREEN_WIDTH - total_width) // 2
        self.buttons = {}
        btn_data = [
            ("feed", "Feed", "[1]"),
            ("play", "Play", "[2]"),
            ("clean", "Clean", "[3]"),
            ("sleep", "Zzz", "[4]"),
        ]
        for i, (key, label, shortcut) in enumerate(btn_data):
            x = start_x + i * (BUTTON_WIDTH + BUTTON_SPACING)
            self.buttons[key] = Button(x, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT,
                                       label, shortcut)

        # Pet select buttons
        sel_w = 160
        sel_h = 80
        gap = 40
        sel_y = 380
        self.cat_button = Button(SCREEN_WIDTH // 2 - sel_w - gap // 2, sel_y,
                                 sel_w, sel_h, "Cat")
        self.dog_button = Button(SCREEN_WIDTH // 2 + gap // 2, sel_y,
                                 sel_w, sel_h, "Dog")

    def draw_sky(self, surface, day_progress):
        """Draw day/night sky gradient based on progress through the day."""
        p = day_progress  # 0.0 to 1.0

        if p < 0.1:
            # Dawn
            sky_color = _lerp_color(SKY_NIGHT, SKY_DAWN, p / 0.1)
        elif p < 0.2:
            # Dawn -> Day
            sky_color = _lerp_color(SKY_DAWN, SKY_DAY, (p - 0.1) / 0.1)
        elif p < 0.55:
            # Full day
            sky_color = SKY_DAY
        elif p < 0.65:
            # Day -> Sunset
            sky_color = _lerp_color(SKY_DAY, SKY_SUNSET, (p - 0.55) / 0.1)
        elif p < 0.75:
            # Sunset -> Night
            sky_color = _lerp_color(SKY_SUNSET, SKY_NIGHT, (p - 0.65) / 0.1)
        else:
            # Night
            sky_color = SKY_NIGHT

        surface.fill(sky_color)

        # Stars at night
        if p > 0.75 or p < 0.1:
            alpha = 1.0
            if 0.75 < p < 0.8:
                alpha = (p - 0.75) / 0.05
            elif 0.05 < p < 0.1:
                alpha = (0.1 - p) / 0.05
            if alpha > 0:
                import random
                rng = random.Random(42)  # fixed seed for stable stars
                for _ in range(30):
                    sx = rng.randint(0, SCREEN_WIDTH)
                    sy = rng.randint(0, GROUND_Y - 50)
                    brightness = int(200 * alpha * rng.uniform(0.5, 1.0))
                    star_color = (brightness, brightness, brightness + 20)
                    pygame.draw.circle(surface, star_color, (sx, sy), 1)

    def draw_ground(self, surface, day_progress):
        """Draw ground/grass area."""
        is_night = day_progress > 0.7 or day_progress < 0.1
        grass_color = GRASS_DARK if is_night else GRASS_GREEN
        pygame.draw.rect(surface, grass_color,
                         (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))

        # Grass blades
        blade_color = _lerp_color(grass_color, (40, 100, 30), 0.3)
        for i in range(0, SCREEN_WIDTH, 12):
            h = 8 + (i * 7 % 11)
            pygame.draw.line(surface, blade_color,
                             (i, GROUND_Y), (i + 3, GROUND_Y - h), 1)

    def draw_stat_bars(self, surface, pet):
        """Draw the stat bars at the top."""
        stats = [
            ("Hunger", pet.hunger, COLOR_HUNGER),
            ("Happy", pet.happiness, COLOR_HAPPINESS),
            ("Energy", pet.energy, COLOR_ENERGY),
            ("Clean", pet.cleanliness, COLOR_CLEANLINESS),
        ]

        for i, (label, value, color) in enumerate(stats):
            y = STAT_BAR_Y_START + i * STAT_BAR_SPACING

            # Label
            label_surf = self.font_small.render(label, True, WHITE)
            surface.blit(label_surf, (STAT_BAR_X, y))

            # Bar background
            bar_x = STAT_BAR_X + STAT_BAR_LABEL_WIDTH
            bar_rect = pygame.Rect(bar_x, y + 2, STAT_BAR_WIDTH, STAT_BAR_HEIGHT)
            pygame.draw.rect(surface, COLOR_STAT_BG, bar_rect, border_radius=4)

            # Bar fill
            fill_width = int((value / STAT_MAX) * STAT_BAR_WIDTH)
            if fill_width > 0:
                fill_rect = pygame.Rect(bar_x, y + 2, fill_width, STAT_BAR_HEIGHT)
                # Red warning if low
                if value < 20:
                    bar_color = (220, 50, 50)
                else:
                    bar_color = color
                pygame.draw.rect(surface, bar_color, fill_rect, border_radius=4)

            # Border
            pygame.draw.rect(surface, COLOR_STAT_BORDER, bar_rect, 1, border_radius=4)

            # Value text
            val_text = self.font_tiny.render(f"{int(value)}", True, WHITE)
            surface.blit(val_text, (bar_x + STAT_BAR_WIDTH + 8, y + 2))

    def draw_day_info(self, surface, pet):
        """Draw day counter and time of day."""
        # Sun/moon icon
        is_night = not pet.is_daytime
        icon = "Moon" if is_night else "Sun"

        text = f"Day {pet.day_count}   {icon}   {pet.time_of_day_label}"
        text_surf = self.font_small.render(text, True, COLOR_DAY_TEXT)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 25))

        # Background bar
        bg_rect = pygame.Rect(0, 0, SCREEN_WIDTH, 35)
        bg_surf = pygame.Surface((SCREEN_WIDTH, 35), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 80))
        surface.blit(bg_surf, (0, 0))

        surface.blit(text_surf, text_rect)

    def draw_mood_text(self, surface, pet):
        """Draw mood text above the pet."""
        text_surf = self.font_medium.render(pet.mood_text, True, COLOR_MOOD_TEXT)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 210))
        surface.blit(text_surf, text_rect)

    def draw_action_buttons(self, surface, mouse_pos):
        """Draw the four action buttons."""
        for btn in self.buttons.values():
            btn.update(mouse_pos)
            btn.draw(surface, self.font_medium, self.font_tiny)

    def draw_sick_warning(self, surface, pet):
        """Draw sick warning bar if pet is sick."""
        if not pet.is_sick:
            return
        remaining = 30 - pet.sick_timer
        if remaining < 0:
            remaining = 0
        text = f"Pet is sick! Help within {int(remaining)}s or it will run away!"
        text_surf = self.font_small.render(text, True, (255, 80, 80))
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 190))
        surface.blit(text_surf, text_rect)

    def draw_menu(self, surface, time_val):
        """Draw the main menu screen."""
        # Background
        surface.fill((30, 20, 50))

        # Animated background circles
        for i in range(5):
            r = 50 + i * 30 + math.sin(time_val + i) * 20
            alpha_val = max(0, min(255, int(40 - i * 6)))
            color = (100 + i * 20, 80 + i * 15, 150 + i * 10)
            pygame.draw.circle(surface, color,
                               (SCREEN_WIDTH // 2, 250), int(r), 2)

        # Title
        title_y = 140 + math.sin(time_val * 1.5) * 8
        title_surf = self.font_title.render("Tamagotchi", True, COLOR_TITLE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, title_y))
        surface.blit(title_surf, title_rect)

        # Subtitle
        sub_surf = self.font_medium.render("Virtual Pet", True, COLOR_SUBTITLE)
        sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, title_y + 50))
        surface.blit(sub_surf, sub_rect)

        # Start prompt (blinking)
        if int(time_val * 2) % 2 == 0:
            start_surf = self.font_medium.render("Press SPACE to start",
                                                  True, WHITE)
            start_rect = start_surf.get_rect(center=(SCREEN_WIDTH // 2, 450))
            surface.blit(start_surf, start_rect)

        # Animated preview pets
        self._draw_menu_pet_preview(surface, time_val)

    def _draw_menu_pet_preview(self, surface, time_val):
        """Draw small animated pet silhouettes on the menu."""
        # Small cat silhouette
        cx, cy = 140, 340
        bounce = math.sin(time_val * 3) * 5
        # Body
        pygame.draw.ellipse(surface, (200, 140, 50),
                            (cx - 20, cy - 10 + bounce, 40, 25))
        # Head
        pygame.draw.circle(surface, (200, 140, 50),
                           (cx, cy - 25 + bounce), 15)
        # Ears
        for side in [-1, 1]:
            pygame.draw.polygon(surface, (200, 140, 50), [
                (cx + side * 8, cy - 35 + bounce),
                (cx + side * 15, cy - 48 + bounce),
                (cx + side * 18, cy - 32 + bounce),
            ])

        # Small dog silhouette
        cx, cy = 340, 340
        bounce = math.sin(time_val * 3 + 1) * 5
        pygame.draw.ellipse(surface, (180, 140, 70),
                            (cx - 22, cy - 10 + bounce, 44, 28))
        pygame.draw.circle(surface, (180, 140, 70),
                           (cx, cy - 25 + bounce), 16)
        # Floppy ears
        for side in [-1, 1]:
            pygame.draw.ellipse(surface, (150, 110, 50),
                                (cx + side * 14 - 6, cy - 30 + bounce, 12, 22))

    def draw_pet_select(self, surface, mouse_pos, time_val):
        """Draw the pet selection screen."""
        surface.fill((30, 25, 55))

        # Title
        title_surf = self.font_large.render("Choose Your Pet", True, COLOR_TITLE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
        surface.blit(title_surf, title_rect)

        # Cat preview
        cat_cx = SCREEN_WIDTH // 2 - 100
        cat_cy = 260
        bounce = math.sin(time_val * 2.5) * 5
        pygame.draw.ellipse(surface, (230, 160, 60),
                            (cat_cx - 30, cat_cy - 15 + bounce, 60, 35))
        pygame.draw.circle(surface, (230, 160, 60),
                           (cat_cx, cat_cy - 38 + bounce), 22)
        for side in [-1, 1]:
            pygame.draw.polygon(surface, (230, 160, 60), [
                (cat_cx + side * 10, cat_cy - 52 + bounce),
                (cat_cx + side * 18, cat_cy - 70 + bounce),
                (cat_cx + side * 24, cat_cy - 50 + bounce),
            ])
        # Eyes
        for side in [-1, 1]:
            pygame.draw.circle(surface, WHITE,
                               (cat_cx + side * 7, cat_cy - 40 + bounce), 4)
            pygame.draw.ellipse(surface, BLACK,
                                (cat_cx + side * 7 - 1, cat_cy - 43 + bounce, 3, 7))

        cat_label = self.font_medium.render("Cat", True, WHITE)
        surface.blit(cat_label, cat_label.get_rect(center=(cat_cx, cat_cy + 40)))

        # Dog preview
        dog_cx = SCREEN_WIDTH // 2 + 100
        dog_cy = 260
        bounce2 = math.sin(time_val * 2.5 + 1) * 5
        pygame.draw.ellipse(surface, (200, 160, 80),
                            (dog_cx - 32, dog_cy - 15 + bounce2, 64, 38))
        pygame.draw.circle(surface, (200, 160, 80),
                           (dog_cx, dog_cy - 38 + bounce2), 24)
        for side in [-1, 1]:
            pygame.draw.ellipse(surface, (170, 130, 60),
                                (dog_cx + side * 18 - 7, dog_cy - 48 + bounce2, 14, 26))
        # Eyes
        for side in [-1, 1]:
            pygame.draw.circle(surface, WHITE,
                               (dog_cx + side * 8, dog_cy - 40 + bounce2), 4)
            pygame.draw.circle(surface, BLACK,
                               (dog_cx + side * 8, dog_cy - 40 + bounce2), 3)

        dog_label = self.font_medium.render("Dog", True, WHITE)
        surface.blit(dog_label, dog_label.get_rect(center=(dog_cx, dog_cy + 40)))

        # Buttons
        self.cat_button.update(mouse_pos)
        self.dog_button.update(mouse_pos)
        self.cat_button.draw(surface, self.font_large)
        self.dog_button.draw(surface, self.font_large)

    def draw_ran_away(self, surface, pet, time_val):
        """Draw the pet ran away screen."""
        surface.fill((40, 25, 35))

        # Sad message
        title_surf = self.font_large.render("Your pet ran away...", True,
                                             (220, 140, 140))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 150))
        surface.blit(title_surf, title_rect)

        msg = f"Your {pet.pet_type} left after {pet.day_count} day{'s' if pet.day_count != 1 else ''}."
        msg_surf = self.font_medium.render(msg, True, LIGHT_GRAY)
        msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, 230))
        surface.blit(msg_surf, msg_rect)

        tip_surf = self.font_small.render("Remember to keep all stats above 15!",
                                           True, (180, 180, 200))
        tip_rect = tip_surf.get_rect(center=(SCREEN_WIDTH // 2, 280))
        surface.blit(tip_surf, tip_rect)

        # Animated footprints fading away
        for i in range(5):
            fx = SCREEN_WIDTH // 2 + i * 50 - 100
            fy = 380 + math.sin(i * 0.8) * 10
            alpha = max(0, 200 - i * 40)
            pygame.draw.ellipse(surface, (alpha, alpha // 2, alpha // 2),
                                (fx, fy, 12, 8))
            pygame.draw.ellipse(surface, (alpha, alpha // 2, alpha // 2),
                                (fx + 5, fy + 12, 12, 8))

        # Restart prompt
        if int(time_val * 2) % 2 == 0:
            restart_surf = self.font_medium.render("Press SPACE to try again",
                                                    True, WHITE)
            restart_rect = restart_surf.get_rect(center=(SCREEN_WIDTH // 2, 480))
            surface.blit(restart_surf, restart_rect)
