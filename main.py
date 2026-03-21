"""Tamagotchi — Virtual Pet Game. Main entry point."""

import sys
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    STATE_MENU, STATE_PET_SELECT, STATE_PLAYING, STATE_PET_RAN_AWAY,
    PET_CAT, PET_DOG, SAMPLE_RATE, AUDIO_CHANNELS, AUDIO_BUFFER,
)
from pet import Pet
from drawing import PetDrawer
from ui import UI
from audio import SoundManager


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=SAMPLE_RATE, channels=AUDIO_CHANNELS,
                          buffer=AUDIO_BUFFER)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.ui = UI()
        self.sound = SoundManager()
        self.pet_drawer = PetDrawer()

        self.state = STATE_MENU
        self.pet = None
        self.time = 0.0
        self.runaway_sound_played = False

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.time += dt
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self._handle_event(event, mouse_pos)

            self._update(dt)
            self._draw(mouse_pos)
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _handle_event(self, event, mouse_pos):
        if self.state == STATE_MENU:
            self._handle_menu_event(event)
        elif self.state == STATE_PET_SELECT:
            self._handle_pet_select_event(event, mouse_pos)
        elif self.state == STATE_PLAYING:
            self._handle_playing_event(event, mouse_pos)
        elif self.state == STATE_PET_RAN_AWAY:
            self._handle_ran_away_event(event)

    def _handle_menu_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.sound.play("select")
                self.state = STATE_PET_SELECT
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
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
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.ui.buttons["feed"].is_clicked(mouse_pos):
                self._do_feed()
            elif self.ui.buttons["play"].is_clicked(mouse_pos):
                self._do_play()
            elif self.ui.buttons["clean"].is_clicked(mouse_pos):
                self._do_clean()
            elif self.ui.buttons["sleep"].is_clicked(mouse_pos):
                self._do_sleep()

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
        self.state = STATE_PLAYING
        self.runaway_sound_played = False

    def _do_feed(self):
        if self.pet:
            self.pet.feed()
            self.sound.play("feed")

    def _do_play(self):
        if self.pet:
            self.pet.play()
            self.sound.play("play")

    def _do_clean(self):
        if self.pet:
            self.pet.clean()
            self.sound.play("clean")

    def _do_sleep(self):
        if self.pet:
            was_sleeping = self.pet.action == "sleeping"
            self.pet.toggle_sleep()
            self.sound.play("wake" if was_sleeping else "sleep")

    def _update(self, dt):
        if self.state == STATE_PLAYING and self.pet:
            self.pet.update(dt)
            self.pet_drawer.update(dt)

            # Check if pet just started running away
            if self.pet.action == "running_away" and not self.runaway_sound_played:
                self.sound.play("runaway")
                self.runaway_sound_played = True

            # Transition to ran away state
            if self.pet.has_run_away:
                self.state = STATE_PET_RAN_AWAY

    def _draw(self, mouse_pos):
        if self.state == STATE_MENU:
            self.ui.draw_menu(self.screen, self.time)

        elif self.state == STATE_PET_SELECT:
            self.ui.draw_pet_select(self.screen, mouse_pos, self.time)

        elif self.state == STATE_PLAYING and self.pet:
            # Sky and ground
            self.ui.draw_sky(self.screen, self.pet.day_progress)
            self.ui.draw_ground(self.screen, self.pet.day_progress)

            # Pet
            self.pet_drawer.draw(self.screen, self.pet)

            # UI overlays
            self.ui.draw_day_info(self.screen, self.pet)
            self.ui.draw_stat_bars(self.screen, self.pet)
            self.ui.draw_mood_text(self.screen, self.pet)
            self.ui.draw_sick_warning(self.screen, self.pet)
            self.ui.draw_action_buttons(self.screen, mouse_pos)

        elif self.state == STATE_PET_RAN_AWAY and self.pet:
            self.ui.draw_ran_away(self.screen, self.pet, self.time)


if __name__ == "__main__":
    Game().run()
