"""Pet class — stats, state machine, decay, sickness, evolution."""

import time
import datetime
from settings import (
    STAT_MAX, STAT_START, STAT_SICK_THRESHOLD,
    HUNGER_DECAY_DAY, HUNGER_DECAY_NIGHT,
    HAPPINESS_DECAY, ENERGY_DECAY_DAY, ENERGY_DECAY_NIGHT_AWAKE,
    ENERGY_RESTORE_SLEEPING, CLEANLINESS_DECAY,
    FEED_AMOUNT, PLAY_AMOUNT, CLEAN_AMOUNT,
    ACTION_DURATION, SICK_TIMER_LIMIT,
    DAY_LENGTH, DAY_PHASE_LENGTH,
    EVOLUTION_THRIVING, EVOLUTION_SCRUFFY,
    ACTION_IDLE, ACTION_EATING, ACTION_PLAYING, ACTION_CLEANING,
    ACTION_SLEEPING, ACTION_SICK, ACTION_RUNNING_AWAY,
    PET_CAT, PET_DOG,
    POOP_DELAY, POOP_MAX_PILES, POOP_CLEANLINESS_MULTIPLIER,
    XP_LEVEL_THRESHOLDS,
    GROWTH_BABY, GROWTH_KID, GROWTH_ADULT, GROWTH_THRESHOLDS,
    BADGE_RANKS,
)


class Pet:
    def __init__(self, pet_type, name=""):
        self.pet_type = pet_type  # PET_CAT or PET_DOG
        self.name = name if name else pet_type.capitalize()
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

        # Poop system
        self.poop_timer = 0.0      # countdown after eating (0 = inactive)
        self.poop_piles = 0        # visible poop piles on floor (0..3)

        # Last food/clean selection tracking (for drawing-specific props)
        self.last_food_index = -1
        self.last_food_color = None
        self.last_clean_index = -1

        # XP / education system
        self.xp = 0
        self.level = 1
        self.edu_games_today = 0
        self.streak_days = 0
        self._last_edu_day = 0

        # Growth stages
        self.growth_stage = GROWTH_BABY
        self.total_play_seconds = 0.0
        self.stage_just_changed = False

        # Word mastery tracking
        # Key = english word, Value = {"box": 0-2, "correct": N, "wrong": N,
        #   "streak": N, "last_seen": "YYYY-MM-DD"}
        # box 0 = new/struggling, box 1 = learning, box 2 = mastered
        self.word_mastery = {}

        # Longest correct-answer streak ever achieved (for badge/display)
        self.longest_streak = 0

        # Custom appearance (from pet designer)
        self.appearance = {
            "body_color": None,      # None = default per pet_type
            "accent_color": None,
            "pattern": "solid",
            "pattern_color": None,
            "hat": None,
            "glasses": None,
            "scarf": None,
            "collar": None,
            "special": None,
            "fur_style": None,
            "tail_style": None,
            "eye_style": None,
            "ear_style": None,
        }

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
        self.poop_timer = POOP_DELAY

    def feed_food(self, hunger_amount, happiness_amount=0, energy_amount=0,
                  food_index=-1, food_color=None):
        """Feed a specific food with individual stat amounts."""
        if self.action == ACTION_RUNNING_AWAY:
            return
        if self.action == ACTION_SLEEPING:
            self.action = ACTION_IDLE
        self.action = ACTION_EATING
        self.action_timer = ACTION_DURATION
        self.hunger = min(STAT_MAX, self.hunger + hunger_amount)
        self.happiness = min(STAT_MAX, self.happiness + happiness_amount)
        self.energy = min(STAT_MAX, self.energy + energy_amount)
        self.last_food_index = food_index
        self.last_food_color = food_color
        self.poop_timer = POOP_DELAY

    def boost_happiness(self, amount):
        """Apply happiness from a mini game."""
        if self.action == ACTION_RUNNING_AWAY:
            return
        if self.action == ACTION_SLEEPING:
            self.action = ACTION_IDLE
        self.action = ACTION_PLAYING
        self.action_timer = ACTION_DURATION
        self.happiness = min(STAT_MAX, self.happiness + amount)

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
        self.action = ACTION_CLEANING
        self.action_timer = ACTION_DURATION
        self.cleanliness = min(STAT_MAX, self.cleanliness + CLEAN_AMOUNT)

    def toggle_sleep(self):
        if self.action == ACTION_RUNNING_AWAY:
            return
        if self.action == ACTION_SLEEPING:
            self.action = ACTION_IDLE
        else:
            self.action = ACTION_SLEEPING

    # --- XP / Education ---

    def add_xp(self, amount):
        """Add XP, recalculate level. Return True if leveled up."""
        self.xp += amount
        old_level = self.level
        for i, threshold in enumerate(XP_LEVEL_THRESHOLDS):
            if self.xp >= threshold:
                self.level = i + 1
        return self.level > old_level

    def record_word_result(self, english_word, correct):
        """Track per-word mastery using a simple Leitner box system."""
        if english_word not in self.word_mastery:
            self.word_mastery[english_word] = {
                "box": 0, "correct": 0, "wrong": 0, "streak": 0,
            }
        entry = self.word_mastery[english_word]
        entry["last_seen"] = datetime.date.today().isoformat()
        if correct:
            entry["correct"] += 1
            entry["streak"] += 1
            if entry["streak"] >= 4 and entry["box"] < 2:
                entry["box"] = 2
            elif entry["streak"] >= 2 and entry["box"] < 1:
                entry["box"] = 1
        else:
            entry["wrong"] += 1
            entry["streak"] = 0
            if entry["box"] > 0:
                entry["box"] -= 1

    def get_mastery_stats(self):
        """Return (box0_count, box1_count, box2_count, total)."""
        counts = [0, 0, 0]
        for data in self.word_mastery.values():
            counts[data["box"]] += 1
        return (counts[0], counts[1], counts[2], sum(counts))

    @property
    def vocab_badge(self):
        """Return (rank_name, rank_index) based on mastered word count."""
        mastered = sum(1 for d in self.word_mastery.values() if d.get("box") == 2)
        for i, (name, threshold, _, _) in reversed(list(enumerate(BADGE_RANKS))):
            if mastered >= threshold:
                return (name, i)
        return (BADGE_RANKS[0][0], 0)

    def record_edu_game(self):
        """Track edu game completion for streak."""
        self.edu_games_today += 1
        if self._last_edu_day == self.day_count - 1:
            self.streak_days += 1
        elif self._last_edu_day != self.day_count:
            self.streak_days = 1
        self._last_edu_day = self.day_count

    @property
    def xp_for_current_level(self):
        base = XP_LEVEL_THRESHOLDS[min(self.level - 1,
                                        len(XP_LEVEL_THRESHOLDS) - 1)]
        return self.xp - base

    @property
    def xp_for_next_level(self):
        if self.level < len(XP_LEVEL_THRESHOLDS):
            return (XP_LEVEL_THRESHOLDS[self.level]
                    - XP_LEVEL_THRESHOLDS[self.level - 1])
        return 100

    def check_growth(self):
        """Check if pet should evolve to next growth stage."""
        self.stage_just_changed = False
        stage_order = [GROWTH_BABY, GROWTH_KID, GROWTH_ADULT]
        for stage, min_days, min_care in reversed(GROWTH_THRESHOLDS):
            if self.day_count >= min_days and self.care_avg >= min_care:
                if stage != self.growth_stage:
                    if stage_order.index(stage) > stage_order.index(self.growth_stage):
                        self.growth_stage = stage
                        self.stage_just_changed = True
                break

    def to_dict(self):
        """Serialize pet state to a plain dict for JSON saving."""
        return {
            "pet_type": self.pet_type,
            "name": self.name,
            "hunger": self.hunger,
            "happiness": self.happiness,
            "energy": self.energy,
            "cleanliness": self.cleanliness,
            "action": ACTION_IDLE,
            "is_sick": self.is_sick,
            "sick_timer": self.sick_timer,
            "day_count": self.day_count,
            "cycle_time": self.cycle_time,
            "care_avg": self.care_avg,
            "evolution_tier": self.evolution_tier,
            "poop_piles": self.poop_piles,
            "xp": self.xp,
            "level": self.level,
            "edu_games_today": self.edu_games_today,
            "streak_days": self.streak_days,
            "_last_edu_day": self._last_edu_day,
            "growth_stage": self.growth_stage,
            "total_play_seconds": self.total_play_seconds,
            "word_mastery": self.word_mastery,
            "appearance": self.appearance,
            "longest_streak": self.longest_streak,
        }

    @classmethod
    def from_dict(cls, data):
        """Restore a Pet from a saved dict."""
        pet = cls(data["pet_type"], data.get("name", ""))
        for key in [
            "hunger", "happiness", "energy", "cleanliness",
            "is_sick", "sick_timer", "day_count", "cycle_time",
            "care_avg", "evolution_tier", "poop_piles",
            "xp", "level", "edu_games_today", "streak_days",
            "_last_edu_day", "growth_stage", "total_play_seconds",
        ]:
            if key in data:
                setattr(pet, key, data[key])
        pet.word_mastery = data.get("word_mastery", {})
        pet.longest_streak = data.get("longest_streak", 0)
        # Restore appearance with backward compat (old saves lack this key)
        saved_appearance = data.get("appearance", {})
        if saved_appearance:
            for key in pet.appearance:
                if key in saved_appearance:
                    pet.appearance[key] = saved_appearance[key]
        return pet

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
            self.edu_games_today = 0

        daytime = self.is_daytime

        # Action timer
        if self.action_timer > 0:
            self.action_timer -= dt
            if self.action_timer <= 0:
                self.action_timer = 0
                if self.action != ACTION_SLEEPING:
                    self.action = ACTION_IDLE

        # Poop timer countdown
        if self.poop_timer > 0:
            self.poop_timer -= dt
            if self.poop_timer <= 0:
                self.poop_timer = 0
                self.poop_piles = min(POOP_MAX_PILES, self.poop_piles + 1)

        # Stat decay
        hunger_rate = HUNGER_DECAY_DAY if daytime else HUNGER_DECAY_NIGHT
        self.hunger = max(0, self.hunger - hunger_rate * dt)
        self.happiness = max(0, self.happiness - HAPPINESS_DECAY * dt)
        poop_multiplier = 1.0 + self.poop_piles * (POOP_CLEANLINESS_MULTIPLIER - 1.0)
        self.cleanliness = max(0, self.cleanliness - CLEANLINESS_DECAY * poop_multiplier * dt)

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

        self.check_growth()

    def clean_with(self, cleanliness_amt, happiness_amt=0, energy_amt=0,
                   clean_index=-1):
        """Apply a specific cleaning option."""
        if self.action == ACTION_RUNNING_AWAY:
            return
        if self.action == ACTION_SLEEPING:
            self.action = ACTION_IDLE
        self.action = ACTION_CLEANING
        self.action_timer = ACTION_DURATION
        self.cleanliness = min(STAT_MAX, self.cleanliness + cleanliness_amt)
        self.happiness = min(STAT_MAX, self.happiness + happiness_amt)
        self.energy = max(0, min(STAT_MAX, self.energy + energy_amt))
        self.last_clean_index = clean_index

    def pick_up_poop(self):
        """Remove one poop pile and gain small cleanliness."""
        if self.action == ACTION_RUNNING_AWAY:
            return False
        if self.poop_piles <= 0:
            return False
        self.poop_piles -= 1
        self.cleanliness = min(STAT_MAX, self.cleanliness + 5)
        return True

    def cure_sickness(self, stat_restore=0):
        """Cure sickness and optionally restore lowest stat."""
        self.is_sick = False
        self.sick_timer = 0.0
        if stat_restore > 0:
            stats = {"hunger": self.hunger, "happiness": self.happiness,
                     "energy": self.energy, "cleanliness": self.cleanliness}
            lowest = min(stats, key=stats.get)
            if lowest == "hunger":
                self.hunger = min(STAT_MAX, self.hunger + stat_restore)
            elif lowest == "happiness":
                self.happiness = min(STAT_MAX, self.happiness + stat_restore)
            elif lowest == "energy":
                self.energy = min(STAT_MAX, self.energy + stat_restore)
            elif lowest == "cleanliness":
                self.cleanliness = min(STAT_MAX, self.cleanliness + stat_restore)
