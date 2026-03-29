"""Constants and configuration for the Tamagotchi game."""

# Window
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 640

# Render-then-scale: internal design resolution stays 480x640,
# window opens at this multiple for a bigger display.
DESIGN_WIDTH = 480
DESIGN_HEIGHT = 640
DEFAULT_WINDOW_SCALE = 1.5
FPS = 60
TITLE = "Tamagotchi"

# Game states
STATE_MENU = "MENU"
STATE_PET_SELECT = "PET_SELECT"
STATE_PLAYING = "PLAYING"
STATE_NAMING = "NAMING"
STATE_PET_RAN_AWAY = "PET_RAN_AWAY"
STATE_PET_DESIGN = "PET_DESIGN"

# Pet types
PET_CAT = "cat"
PET_DOG = "dog"

# Pet action states
ACTION_IDLE = "idle"
ACTION_EATING = "eating"
ACTION_PLAYING = "playing"
ACTION_SLEEPING = "sleeping"
ACTION_CLEANING = "cleaning"
ACTION_SICK = "sick"
ACTION_RUNNING_AWAY = "running_away"

# Stats
STAT_MAX = 100
STAT_START = 80
STAT_SICK_THRESHOLD = 15

# Decay rates (per second) — tuned for relaxed pacing
HUNGER_DECAY_DAY = 0.35
HUNGER_DECAY_NIGHT = 0.12
HAPPINESS_DECAY = 0.25
ENERGY_DECAY_DAY = 0.2
ENERGY_DECAY_NIGHT_AWAKE = 0.25
ENERGY_RESTORE_SLEEPING = 1.0
CLEANLINESS_DECAY = 0.12

# Action restore amounts
FEED_AMOUNT = 50
PLAY_AMOUNT = 40
CLEAN_AMOUNT = 40

# Action durations (seconds)
ACTION_DURATION = 2.0

# Sickness
SICK_TIMER_LIMIT = 60.0  # seconds before pet runs away

# Day/night cycle (seconds) — doubled for slower pacing
DAY_LENGTH = 600  # 10 minutes total
DAY_PHASE_LENGTH = 420  # 7 minutes of day
NIGHT_PHASE_LENGTH = 180  # 3 minutes of night

# Evolution thresholds
EVOLUTION_THRIVING = 70
EVOLUTION_SCRUFFY = 40

# --- Compact HUD strip ---
HUD_HEIGHT = 68
HUD_ROW1_Y = 14            # center y of name/day text
HUD_ROW2_Y = 34            # top of stat bar icons row
HUD_BAR_W = 78             # each mini stat bar width
HUD_BAR_H = 12             # each mini stat bar height
HUD_ICON_SIZE = 12          # icon bounding box
HUD_XP_Y = 54              # thin XP bar y
HUD_XP_H = 5               # thin XP bar height

PET_CENTER_X = SCREEN_WIDTH // 2
PET_CENTER_Y = 385

GROUND_Y = 460

BUTTON_Y = 540
BUTTON_WIDTH = 90
BUTTON_HEIGHT = 50
BUTTON_SPACING = 15
BUTTON_COUNT = 4

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (200, 200, 200)
MID_GRAY = (130, 130, 130)

# Sky colors
SKY_DAY = (135, 206, 235)
SKY_SUNSET = (255, 140, 60)
SKY_NIGHT = (25, 25, 80)
SKY_DAWN = (255, 180, 120)

# Grass
GRASS_GREEN = (80, 160, 60)
GRASS_DARK = (60, 130, 45)

# Stat bar colors
COLOR_HUNGER = (230, 120, 50)
COLOR_HAPPINESS = (255, 200, 50)
COLOR_ENERGY = (100, 180, 255)
COLOR_CLEANLINESS = (130, 220, 130)
COLOR_STAT_BG = (50, 50, 50)
COLOR_STAT_BORDER = (80, 80, 80)

# Button colors
COLOR_BUTTON = (70, 70, 90)
COLOR_BUTTON_HOVER = (90, 90, 120)
COLOR_BUTTON_TEXT = (240, 240, 240)

# Pet colors - Cat (orange tabby)
CAT_BODY = (230, 160, 60)
CAT_BODY_DARK = (200, 130, 40)
CAT_BELLY = (250, 220, 170)
CAT_STRIPE = (180, 110, 30)
CAT_NOSE = (230, 130, 130)

# Pet colors - Dog (golden)
DOG_BODY = (200, 160, 80)
DOG_BODY_DARK = (170, 130, 60)
DOG_BELLY = (240, 210, 160)
DOG_NOSE = (60, 40, 30)
DOG_TONGUE = (230, 120, 120)

# Evolution color modifiers
THRIVING_TINT = 20   # add brightness
SCRUFFY_TINT = -30   # subtract brightness

# Particle colors
SPARKLE_COLOR = (255, 255, 180)
STAR_COLOR = (255, 220, 80)
ZZZ_COLOR = (180, 180, 220)
SWEAT_COLOR = (150, 200, 255)
FOOD_COLOR = (200, 140, 60)

# UI
COLOR_TITLE = (255, 220, 100)
COLOR_SUBTITLE = (200, 200, 220)
COLOR_MOOD_TEXT = (220, 220, 240)
COLOR_DAY_TEXT = (255, 255, 255)

# Audio
SAMPLE_RATE = 22050
AUDIO_CHANNELS = 1
AUDIO_BUFFER = 512

# --- Batch 1: Animation Foundation ---
BLINK_DURATION = 0.15          # seconds for one blink (close+open)
BLINK_MIN_INTERVAL = 2.5       # min seconds between blinks
BLINK_MAX_INTERVAL = 5.0       # max seconds between blinks
FIDGET_MIN_INTERVAL = 3.0      # min seconds between fidgets
FIDGET_MAX_INTERVAL = 7.0      # max seconds between fidgets
FIDGET_DURATION = 0.6          # seconds a fidget lasts

# --- Batch 2: Depth & Shadows ---
SHADOW_BASE_ALPHA = 50         # base alpha for ground shadow
HIGHLIGHT_TINT = 35            # brightness added for highlight ellipses
BLUSH_COLOR = (255, 130, 150)  # cheek blush pink
BLUSH_THRESHOLD = 30           # happiness above which blush appears (kawaii permanent blush)

# --- Batch 3: Particles & Environment ---
GRASS_SWAY_SPEED_BACK = 1.2    # back grass layer sway speed
GRASS_SWAY_SPEED_FRONT = 1.8   # front grass layer sway speed
STAR_COUNT = 40                 # number of background stars at night
STAR_TWINKLE_MIN_SPEED = 1.0   # min twinkle frequency
STAR_TWINKLE_MAX_SPEED = 3.5   # max twinkle frequency

# --- Kawaii proportions ---
KAWAII_HEAD_RADIUS = 38        # dominant head
KAWAII_BODY_W = 44             # half-width of body ellipse
KAWAII_BODY_H = 36             # half-height of body ellipse
KAWAII_HEAD_BODY_OVERLAP = 12  # head overlaps body by this much
KAWAII_LEG_W = 11              # stubby leg width
KAWAII_LEG_H = 15              # stubby leg height

# --- Clean kawaii outline style ---
OUTLINE_WIDTH = 3
KAWAII_TOTAL_H = 80
KAWAII_HEAD_RATIO = 0.65
KAWAII_BODY_TAPER = 0.85
KAWAII_PAW_BUMP_R = 5
KAWAII_PAW_SPACING = 12
KAWAII_EYE_Y_RATIO = 0.55
KAWAII_BLUSH_RADIUS = 8
KAWAII_WHISKER_LEN = 20
KAWAII_WHISKER_COUNT = 2
CAT_EAR_INNER_COLOR = (80, 60, 30)
DOG_EAR_INNER_COLOR = (150, 110, 50)

# Prop / bubble colors
BUBBLE_COLOR = (200, 230, 255)
BOWL_COLOR = (180, 100, 60)
BOWL_FOOD_COLOR = (220, 160, 80)
BALL_COLOR = (230, 80, 80)

# --- Food Selection ---
# (name, hunger, happiness, energy, icon_color)
FOODS = [
    ("Apple",  25, 5,  0,  (100, 200, 80)),
    ("Fish",   40, 0,  0,  (120, 160, 220)),
    ("Cake",   20, 15, 0,  (240, 180, 200)),
    ("Milk",   15, 0,  10, (240, 240, 250)),
]

FOOD_MENU_WIDTH = 320
FOOD_MENU_HEIGHT = 280
FOOD_ROW_HEIGHT = 56
FOOD_MENU_BG = (50, 45, 65)
FOOD_MENU_BORDER = (120, 100, 160)
FOOD_MENU_HOVER = (80, 70, 110)
FOOD_MENU_TEXT = (240, 240, 255)
FOOD_MENU_STAT_TEXT = (180, 220, 180)

# --- Mini Games ---
MINIGAME_DURATION = 8.0
MINIGAME_RESULTS_DURATION = 2.0
MINIGAME_BASE_HAPPINESS = 15
MINIGAME_PER_SCORE = 3
MINIGAME_HAPPINESS_CAP = 45

# Treat game (CatchTreats)
TREAT_SPAWN_INTERVAL = 0.6
TREAT_FALL_SPEED = 120
TREAT_RADIUS = 16
TREAT_COLOR = (255, 180, 100)

# Bubble game (PopBubbles)
BUBBLE_SPAWN_INTERVAL = 0.7
BUBBLE_FLOAT_SPEED = 60
BUBBLE_MIN_RADIUS = 18
BUBBLE_MAX_RADIUS = 30
BUBBLE_WOBBLE_AMP = 30
BUBBLE_WOBBLE_SPEED = 2.0
MINIGAME_BUBBLE_COLOR = (180, 220, 255)

# Ball game (ChaseBall)
CHASE_BALL_START_SPEED = 150
CHASE_BALL_SPEED_INCREASE = 25
CHASE_BALL_RADIUS = 20
CHASE_BALL_COLOR = (230, 80, 80)

# Mini game overlay
OVERLAY_ALPHA = 230
OVERLAY_TITLE_COLOR = (255, 240, 180)
OVERLAY_SCORE_COLOR = (255, 255, 255)
OVERLAY_TIMER_BG = (60, 60, 60)
OVERLAY_TIMER_FG = (100, 220, 140)

# --- Poop System ---
POOP_DELAY = 120.0           # seconds after eating before poop
POOP_MAX_PILES = 3
POOP_CLEANLINESS_MULTIPLIER = 2.0  # cleanliness decays 2x faster per pile
POOP_COLOR = (140, 100, 60)
POOP_COLOR_DARK = (100, 70, 40)

# --- Cleaning Menu ---
# (name, cleanliness, happiness, energy, icon_color)
CLEANINGS = [
    ("Bath",     40, 0,  -5, (100, 180, 255)),
    ("Brush",    20, 5,   0, (240, 160, 200)),
    ("Towel",    15, 0,   0, (240, 240, 240)),
    ("Pick Up",   5, 0,   0, (180, 140, 90)),
]

# --- Medicine Game ---
MEDICINE_DURATION = 6.0
MEDICINE_SPAWN_INTERVAL = 0.8
MEDICINE_FALL_SPEED = 100
MEDICINE_BOTTLE_W = 24
MEDICINE_BOTTLE_H = 32
MEDICINE_COLORS = [
    (220, 80, 80),    # red
    (80, 180, 80),    # green
    (80, 120, 220),   # blue
    (220, 180, 60),   # yellow
]
MEDICINE_STAT_RESTORE = 15
MEDICINE_SICK_TIMER_RESET = 15.0

# --- Compact Buttons (when 5 buttons shown) ---
BUTTON_WIDTH_COMPACT = 78
BUTTON_SPACING_COMPACT = 8

# --- Educational Mini Games ---
EDU_GAME_BASE_HAPPINESS = 10
EDU_GAME_PER_SCORE = 4
EDU_GAME_HAPPINESS_CAP = 40
XP_PER_CORRECT = 10
XP_BONUS_PERFECT = 20
XP_LEVEL_THRESHOLDS = [0, 50, 120, 220, 350, 520, 730, 1000, 1350, 1800]

# XP bar colors
XP_BAR_COLOR = (180, 130, 255)
XP_BAR_BG = (50, 50, 50)
XP_LEVEL_COLOR = (220, 200, 255)
STREAK_ICON_COLOR = (255, 160, 60)

# Memory game
MEMORY_PAIRS = 4
MEMORY_CARD_W = 86
MEMORY_CARD_H = 105
MEMORY_CARD_SPACING = 10
MEMORY_CARD_BACK = (80, 70, 120)
MEMORY_CARD_MATCHED = (60, 120, 80)
MEMORY_MISMATCH_DELAY = 0.8
MEMORY_DURATION = 80.0
MEMORY_PEEK_DURATION = 3.0

# Falling Word game
FALLING_WORD_DURATION = 40.0
FALLING_WORD_ROUNDS = 5
FALLING_WORD_SPEED = 35
FALLING_WORD_PILL_W = 120
FALLING_WORD_PILL_H = 42

# Spelling game
SPELLING_DURATION = 60.0
SPELLING_WORD_COUNT = 5
SPELLING_TILE_SIZE = 40
SPELLING_TILE_COLOR = (80, 70, 120)
SPELLING_TILE_CORRECT = (80, 180, 100)
SPELLING_HINT_DELAY = 4.0

# Quiz game
QUIZ_DURATION = 50.0
QUIZ_QUESTION_COUNT = 6
QUIZ_BUTTON_W = 240
QUIZ_BUTTON_H = 56
QUIZ_BUTTON_COLOR = (70, 65, 100)
QUIZ_BUTTON_HOVER = (100, 90, 140)
QUIZ_CORRECT_COLOR = (80, 180, 100)
QUIZ_WRONG_COLOR = (200, 80, 80)

# Vocabulary tier unlock
TIER_UNLOCK_THRESHOLD = 10  # words at box >= 1 needed to unlock next tier

# Difficulty scaling by pet level: (easy, medium, hard)
MEMORY_PAIRS_BY_DIFF = (3, 4, 5)
FALLING_ROUNDS_BY_DIFF = (4, 5, 7)
FALLING_SPEED_BY_DIFF = (30, 35, 45)
SPELLING_COUNT_BY_DIFF = (3, 5, 6)
QUIZ_COUNT_BY_DIFF = (4, 6, 8)
QUIZ_OPTIONS_BY_DIFF = (3, 3, 4)

# Play Menu
PLAY_MENU_WIDTH = 340
PLAY_MENU_HEIGHT = 360
PLAY_MENU_ROW_HEIGHT = 56

# --- Session Limits ---
SESSION_SOFT_LIMIT = 30 * 60       # 30 minutes — show warning
SESSION_HARD_LIMIT = 45 * 60       # 45 minutes — force sleep
SESSION_WARNING_INTERVAL = 5 * 60  # re-show warning every 5 min after soft limit

# --- Growth Stages ---
GROWTH_BABY = "baby"
GROWTH_KID = "kid"
GROWTH_ADULT = "adult"

# (stage, min_days, min_care_avg) — pet must reach BOTH thresholds to evolve
GROWTH_THRESHOLDS = [
    (GROWTH_BABY, 0, 0),
    (GROWTH_KID, 4, 55),
    (GROWTH_ADULT, 11, 60),
]

# Visual scale per stage
GROWTH_SCALE = {
    GROWTH_BABY: 0.7,
    GROWTH_KID: 0.9,
    GROWTH_ADULT: 1.0,
}

# --- Save ---
SAVE_FILENAME = "tamagotchi_save.json"  # legacy single-file save
AUTOSAVE_INTERVAL = 60.0  # seconds between auto-saves
MAX_SAVE_SLOTS = 3
SAVES_DIR = "saves"

# --- WordBook ---
WORDBOOK_CARD_H = 48
WORDBOOK_CARD_W = 440
WORDBOOK_CARD_GAP = 4
WORDBOOK_HEADER_H = 155
WORDBOOK_TAB_H = 28
WORDBOOK_SCROLL_IMPULSE = 200
WORDBOOK_STAR_SIZE = 6
WORDBOOK_MASTERED_COLOR = (255, 210, 80)
WORDBOOK_LEARNING_COLOR = (100, 180, 255)
WORDBOOK_NEW_COLOR = (160, 160, 180)

# Badge ranks: (name, threshold, icon_shape, color)
BADGE_RANKS = [
    ("Novice",  0,  "star",   (160, 160, 180)),
    ("Learner", 5,  "book",   (100, 200, 120)),
    ("Scholar", 15, "star2",  (100, 180, 255)),
    ("Expert",  30, "star3",  (200, 140, 255)),
    ("Master",  50, "crown",  (255, 210, 80)),
]

# --- Wardrobe System ---
WARDROBE_HINT_DURATION = 2.5   # seconds tooltip stays visible
WARDROBE_HINT_COLOR = (232, 221, 255)
WARDROBE_HINT_BG = (40, 30, 70, 235)
WARDROBE_HINT_BORDER = (180, 140, 255)
WARDROBE_HINT_Y = 295          # tooltip y position (above pet)

# Item unlock tiers: {item_key: min_rank_index}
# Rank indices: 0=Novice, 1=Learner, 2=Scholar, 3=Expert, 4=Master
WARDROBE_HAT_TIERS = {
    "beret": 1, "bow": 1, "flower": 1,
    "crown": 2, "tophat": 2, "cat_ears": 2,
    "helmet": 3, "propeller": 3,
}
WARDROBE_GLASSES_TIERS = {
    "round": 1,
    "cat_eye": 2, "sunglasses": 2,
    "monocle": 3,
}
WARDROBE_SCARF_TIERS = {
    "red": 3, "blue": 3, "green": 3, "striped": 3, "rainbow": 3,
}
WARDROBE_COLLAR_TIERS = {
    "bell": 3, "bowtie": 3, "bandana": 3, "tag": 3,
}
WARDROBE_SPECIAL_TIERS = {
    "sparkle_eyes": 4, "freckles": 4, "star_cheeks": 4,
    "rosy_cheeks": 4,
}
WARDROBE_COLOR_TIERS = {
    # Scholar (rank 2): natural/pastel body colors
    "natural": 2,
    # Expert (rank 3): exotic/vibrant body colors + patterns
    "exotic": 3,
}
WARDROBE_STYLE_TIER = 3   # fur/eye/ear/tail styles unlock at Expert
WARDROBE_PATTERN_TIER = 3  # spots/stripes unlock at Expert

# Tab unlock tiers (min rank_index to see tab)
WARDROBE_TAB_TIERS = {
    "hats": 1, "glasses": 1,
    "colors": 2,
    "styles": 3, "extras": 3,
    "special": 4,
}

# Preset body color palettes
WARDROBE_NATURAL_COLORS = [
    [230, 160, 60],   # default orange
    [200, 160, 80],   # golden
    [240, 180, 200],  # pink
    [224, 224, 224],   # white
    [200, 180, 150],  # tan
    [160, 120, 90],   # brown
    [240, 200, 160],  # peach
    [80, 80, 100],    # gray
    [45, 45, 60],     # dark
]
WARDROBE_EXOTIC_COLORS = [
    [180, 130, 220],  # purple
    [100, 150, 220],  # blue
    [80, 200, 120],   # green
    [220, 80, 80],    # red
    [255, 210, 100],  # yellow
    [255, 150, 80],   # vivid orange
    [100, 220, 220],  # teal
    [220, 200, 240],  # lavender
    [255, 250, 240],  # cream
]
WARDROBE_ACCENT_COLORS = [
    [255, 212, 100],  # gold
    [255, 255, 255],  # white
    [255, 136, 136],  # red
    [136, 204, 255],  # blue
    [255, 180, 212],  # pink
    [136, 232, 136],  # green
]
WARDROBE_ACCENT_EXPERT = [
    [200, 160, 255],  # purple
    [255, 160, 80],   # orange
    [100, 220, 220],  # teal
]

# Wardrobe overlay UI constants
WARDROBE_HEADER_H = 55
WARDROBE_PREVIEW_H = 195
WARDROBE_TAB_BAR_H = 40
WARDROBE_CHIP_W = 140
WARDROBE_CHIP_H = 44
WARDROBE_CHIP_GAP = 8
WARDROBE_CHIPS_PER_ROW = 3
WARDROBE_HINT_BAR_H = 35
WARDROBE_SWATCH_SIZE = 38
WARDROBE_SWATCH_GAP = 6
WARDROBE_ACCENT_BORDER = (180, 140, 255)

# --- Stage Accessory Colors ---
BABY_BOW_COLOR = (255, 160, 180)
KID_BELL_COLOR = (255, 220, 80)
ADULT_GEM_COLOR = (120, 80, 220)
BANDANA_COLOR = (80, 140, 220)
BONE_TAG_COLOR = (240, 230, 210)
KID_BANDANA_COLOR = (220, 70, 70)
ADULT_COLLAR_COLOR = (100, 70, 50)

# --- Pet Designer Presets (offline mode, no LLM needed) ---
DESIGN_THEMES = {
    "Magical": {
        "body_color": [180, 130, 220], "accent_color": [255, 210, 100],
        "pattern": "solid", "pattern_color": None,
        "hat": "crown", "glasses": None, "scarf": None, "collar": None,
        "special": "sparkle_eyes",
    },
    "Sporty": {
        "body_color": [80, 160, 220], "accent_color": [240, 240, 240],
        "pattern": "solid", "pattern_color": None,
        "hat": None, "glasses": "sunglasses", "scarf": None, "collar": None,
        "special": None,
    },
    "Cool": {
        "body_color": [80, 80, 100], "accent_color": [220, 60, 60],
        "pattern": "solid", "pattern_color": None,
        "hat": None, "glasses": "sunglasses", "scarf": None, "collar": None,
        "special": None, "ear_style": "pointy", "eye_style": "sleepy",
    },
    "Cute": {
        "body_color": [240, 180, 200], "accent_color": [255, 255, 255],
        "pattern": "solid", "pattern_color": None,
        "hat": "flower", "glasses": None, "scarf": None, "collar": None,
        "special": "rosy_cheeks", "fur_style": "fluffy",
    },
    "Silly": {
        "body_color": [255, 180, 50], "accent_color": [80, 220, 120],
        "pattern": "solid", "pattern_color": None,
        "hat": "propeller", "glasses": "round", "scarf": None, "collar": None,
        "special": "freckles", "fur_style": "mohawk", "tail_style": "curly",
    },
    "Royal": {
        "body_color": [160, 50, 60], "accent_color": [255, 210, 80],
        "pattern": "solid", "pattern_color": None,
        "hat": "crown", "glasses": "monocle", "scarf": None, "collar": None,
        "special": "star_cheeks", "fur_style": "long", "eye_style": "sparkly",
    },
}
