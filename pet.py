"""Pet class — stats, state machine, decay, sickness, evolution."""

import time
from settings import (
    STAT_MAX, STAT_START, STAT_SICK_THRESHOLD,
    HUNGER_DECAY_DAY, HUNGER_DECAY_NIGHT,
    HAPPINESS_DECAY, ENERGY_DECAY_DAY, ENERGY_DECAY_NIGHT_AWAKE,
    ENERGY_RESTORE_SLEEPING, CLEANLINESS_DECAY,
    FEED_AMOUNT, PLAY_AMOUNT, CLEAN_AMOUNT,
    ACTION_DURATION, SICK_TIMER_LIMIT,
    DAY_LENGTH, DAY_PHASE_LENGTH,
    EVOLUTION_THRIVING, EVOLUTION_SCRUFFY,
    ACTION_IDLE, ACTION_EATING, ACTION_PLAYING,
    ACTION_SLEEPING, ACTION_SICK, ACTION_RUNNING_AWAY,
    PET_CAT, PET_DOG,
)


class Pet:
    def __init__(self, pet_type):
        self.pet_type = pet_type  # PET_CAT or PET_DOG
        self.hunger = STAT_START
        self.happiness = STAT_START
        self.energy = STAT_START
        self.cleanliness = STAT_START

        self.action = ACTION_IDLE
        self.action_timer = 0.0

        self.is_sick = False
        self.sick_timer = 0.0
        self.has_run_away = False

        self.day_count = 1
        self.cycle_time = 0.0  # 0..DAY_LENGTH

        # Evolution tracking
        self.care_samples = []
        self.care_avg = STAT_START
        self.evolution_tier = "normal"  # "thriving", "normal", "scruffy"

        # Runaway animation progress (0..1)
        self.runaway_progress = 0.0

    @property
    def is_daytime(self):
        return self.cycle_time < DAY_PHASE_LENGTH

    @property
    def day_progress(self):
        """0.0 to 1.0 through the full day cycle."""
        return self.cycle_time / DAY_LENGTH

    @property
    def time_of_day_label(self):
        p = self.day_progress
        if p < 0.15:
            return "Morning"
        elif p < 0.45:
            return "Afternoon"
        elif p < 0.6:
            return "Evening"
        elif p < 0.7:
            return "Sunset"
        else:
            return "Night"

    @property
    def avg_stat(self):
        return (self.hunger + self.happiness + self.energy + self.cleanliness) / 4.0

    @property
    def mood_text(self):
        if self.action == ACTION_SLEEPING:
            return "Zzz... sleeping..."
        if self.is_sick:
            return "Not feeling well..."
        avg = self.avg_stat
        if avg > 80:
            return "Feeling amazing!"
        elif avg > 60:
            return "Feeling happy!"
        elif avg > 40:
            return "Doing okay."
        elif avg > 25:
            return "Feeling down..."
        else:
            return "Please help me..."

    def feed(self):
        if self.action == ACTION_RUNNING_AWAY:
            return
        if self.action == ACTION_SLEEPING:
            self.action = ACTION_IDLE
        self.action = ACTION_EATING
        self.action_timer = ACTION_DURATION
        self.hunger = min(STAT_MAX, self.hunger + FEED_AMOUNT)

    def play(self):
        if self.action == ACTION_RUNNING_AWAY:
            return
        if self.action == ACTION_SLEEPING:
            self.action = ACTION_IDLE
        self.action = ACTION_PLAYING
        self.action_timer = ACTION_DURATION
        self.happiness = min(STAT_MAX, self.happiness + PLAY_AMOUNT)

    def clean(self):
        if self.action == ACTION_RUNNING_AWAY:
            return
        if self.action == ACTION_SLEEPING:
            self.action = ACTION_IDLE
        self.action = ACTION_EATING  # reuse head-bob for cleaning
        self.action_timer = ACTION_DURATION
        self.cleanliness = min(STAT_MAX, self.cleanliness + CLEAN_AMOUNT)

    def toggle_sleep(self):
        if self.action == ACTION_RUNNING_AWAY:
            return
        if self.action == ACTION_SLEEPING:
            self.action = ACTION_IDLE
        else:
            self.action = ACTION_SLEEPING

    def update(self, dt):
        if self.has_run_away:
            return

        # Running away animation
        if self.action == ACTION_RUNNING_AWAY:
            self.runaway_progress += dt * 0.4  # takes ~2.5s
            if self.runaway_progress >= 1.0:
                self.runaway_progress = 1.0
                self.has_run_away = True
            return

        # Advance day/night cycle
        self.cycle_time += dt
        if self.cycle_time >= DAY_LENGTH:
            self.cycle_time -= DAY_LENGTH
            self.day_count += 1

        daytime = self.is_daytime

        # Action timer
        if self.action_timer > 0:
            self.action_timer -= dt
            if self.action_timer <= 0:
                self.action_timer = 0
                if self.action != ACTION_SLEEPING:
                    self.action = ACTION_IDLE

        # Stat decay
        hunger_rate = HUNGER_DECAY_DAY if daytime else HUNGER_DECAY_NIGHT
        self.hunger = max(0, self.hunger - hunger_rate * dt)
        self.happiness = max(0, self.happiness - HAPPINESS_DECAY * dt)
        self.cleanliness = max(0, self.cleanliness - CLEANLINESS_DECAY * dt)

        if self.action == ACTION_SLEEPING:
            if not daytime:
                self.energy = min(STAT_MAX, self.energy + ENERGY_RESTORE_SLEEPING * dt)
            else:
                # Sleeping during day: slow restore
                self.energy = min(STAT_MAX, self.energy + ENERGY_RESTORE_SLEEPING * 0.5 * dt)
        else:
            if daytime:
                self.energy = max(0, self.energy - ENERGY_DECAY_DAY * dt)
            else:
                self.energy = max(0, self.energy - ENERGY_DECAY_NIGHT_AWAKE * dt)

        # Sickness check
        any_critical = (
            self.hunger < STAT_SICK_THRESHOLD
            or self.happiness < STAT_SICK_THRESHOLD
            or self.energy < STAT_SICK_THRESHOLD
            or self.cleanliness < STAT_SICK_THRESHOLD
        )

        if any_critical:
            if not self.is_sick:
                self.is_sick = True
                self.sick_timer = 0.0
            self.sick_timer += dt
            if self.sick_timer >= SICK_TIMER_LIMIT:
                self.action = ACTION_RUNNING_AWAY
                self.runaway_progress = 0.0
        else:
            self.is_sick = False
            self.sick_timer = 0.0

        # Evolution tracking (sample every ~1 second)
        self.care_samples.append(self.avg_stat)
        # Keep last 300 samples (~5 seconds at 60fps... we'll thin it)
        if len(self.care_samples) > 300:
            self.care_samples = self.care_samples[-300:]
        self.care_avg = sum(self.care_samples) / len(self.care_samples)

        if self.care_avg > EVOLUTION_THRIVING:
            self.evolution_tier = "thriving"
        elif self.care_avg < EVOLUTION_SCRUFFY:
            self.evolution_tier = "scruffy"
        else:
            self.evolution_tier = "normal"
