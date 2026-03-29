"""Polish-English vocabulary for educational mini-games.

~100 words across 3 tiers. Each entry is a tuple:
    (polish, english, category, icon_hint, tier)
where icon_hint = (shape, color) for procedural drawing.

Tier 1: basic nouns (always unlocked)
Tier 2: colors, numbers, adjectives (unlock when 10 tier-1 words reach box >= 1)
Tier 3: verbs, polite phrases (unlock when 10 tier-2 words reach box >= 1)
"""

import random
import datetime
from settings import (
    TIER_UNLOCK_THRESHOLD, SESSION_NEW_WORDS, SESSION_REVIEW_WORDS,
    SESSION_MIN_WORDS, SESSION_MAX_WORDS, RUSTY_DAYS_THRESHOLD,
)

# ===================================================================
# Tier 1 — Basic nouns (~35 words, always unlocked)
# ===================================================================

VOCAB_TIER1 = [
    # Animals
    ("kot",    "cat",    "animals", ("cat_face",   (230, 160, 60)),  1),
    ("pies",   "dog",    "animals", ("dog_face",   (200, 160, 80)),  1),
    ("ryba",   "fish",   "animals", ("fish_icon",  (120, 160, 220)), 1),
    ("ptak",   "bird",   "animals", ("bird_icon",  (100, 180, 100)), 1),
    ("koń",    "horse",  "animals", ("horse_face",  (160, 120, 80)),  1),
    ("mysz",   "mouse",  "animals", ("mouse_face",  (180, 180, 180)), 1),
    ("żaba",   "frog",   "animals", ("frog_face",   (80, 180, 60)),   1),
    # Food & drink
    ("mleko",  "milk",   "food", ("bottle",     (240, 240, 250)), 1),
    ("jabłko", "apple",  "food", ("apple_icon", (100, 200, 80)),  1),
    ("ciasto", "cake",   "food", ("cake_icon",  (240, 180, 200)), 1),
    ("chleb",  "bread",  "food", ("loaf",       (210, 170, 100)), 1),
    ("woda",   "water",  "food", ("drop",       (100, 180, 255)), 1),
    ("jajko",  "egg",    "food", ("ellipse",    (250, 240, 210)), 1),
    ("banan",  "banana", "food", ("ellipse",    (240, 220, 80)),  1),
    ("ser",    "cheese", "food", ("triangle",   (240, 210, 80)),  1),
    # Body
    ("głowa",  "head",   "body", ("head_icon", (240, 200, 170)), 1),
    ("ręka",   "hand",   "body", ("hand_icon", (240, 200, 170)), 1),
    ("oko",    "eye",    "body", ("eye_icon",  (120, 180, 220)), 1),
    ("nos",    "nose",   "body", ("nose_icon",  (240, 190, 160)), 1),
    ("ucho",   "ear",    "body", ("ear_icon",   (240, 200, 180)), 1),
    ("noga",   "leg",    "body", ("rect",      (240, 200, 170)), 1),
    ("ząb",    "tooth",  "body", ("rect",      (250, 250, 250)), 1),
    # Feelings
    ("serce",      "heart",  "feelings", ("heart",  (220, 80, 100)),  1),
    ("szczęśliwy", "happy",  "feelings", ("smiley", (255, 220, 80)),  1),
    ("smutny",     "sad",    "feelings", ("frowny", (120, 150, 220)), 1),
    ("zmęczony",   "tired",  "feelings", ("sleepy", (160, 140, 180)), 1),
    ("głodny",     "hungry", "feelings", ("plate",  (220, 160, 80)),  1),
    # Nature / places
    ("dom",    "house",  "nature", ("rect",    (180, 140, 100)), 1),
    ("drzewo", "tree",   "nature", ("tree_icon", (60, 160, 60)),  1),
    ("kwiat",  "flower", "nature", ("star",    (240, 120, 180)), 1),
    # Objects
    ("piłka",  "ball",   "objects", ("ball",   (240, 180, 100)), 1),
    # Family
    ("mama",   "mom",    "family", ("heart",   (240, 140, 180)), 1),
    ("tata",   "dad",    "family", ("heart",   (120, 160, 220)), 1),
    ("dziecko","child",  "family", ("smiley",  (255, 200, 140)), 1),
]

# ===================================================================
# Tier 2 — Colors, numbers, adjectives (~35 words)
# ===================================================================

VOCAB_TIER2 = [
    # Colors
    ("czerwony",     "red",    "colors", ("circle", (220, 50, 50)),   2),
    ("niebieski",    "blue",   "colors", ("circle", (50, 100, 220)),  2),
    ("zielony",      "green",  "colors", ("circle", (50, 180, 50)),   2),
    ("żółty",        "yellow", "colors", ("circle", (240, 220, 50)),  2),
    ("biały",        "white",  "colors", ("circle", (240, 240, 240)), 2),
    ("czarny",       "black",  "colors", ("circle", (40, 40, 40)),    2),
    ("różowy",       "pink",   "colors", ("circle", (240, 140, 180)), 2),
    ("pomarańczowy", "orange", "colors", ("circle", (240, 160, 50)),  2),
    # Numbers
    ("jeden",     "one",   "numbers", ("num_1",  (180, 140, 200)), 2),
    ("dwa",       "two",   "numbers", ("num_2",  (140, 180, 200)), 2),
    ("trzy",      "three", "numbers", ("num_3",  (200, 180, 140)), 2),
    ("cztery",    "four",  "numbers", ("num_4",  (180, 160, 200)), 2),
    ("pięć",      "five",  "numbers", ("num_5",  (160, 200, 160)), 2),
    ("sześć",     "six",   "numbers", ("num_6",  (200, 160, 160)), 2),
    ("siedem",    "seven", "numbers", ("num_7",  (160, 180, 200)), 2),
    ("osiem",     "eight", "numbers", ("num_8",  (180, 200, 160)), 2),
    ("dziewięć",  "nine",  "numbers", ("num_9",  (200, 180, 180)), 2),
    ("dziesięć",  "ten",   "numbers", ("num_10", (180, 180, 200)), 2),
    # Adjectives
    ("duży",   "big",    "adjectives", ("big_icon",   (200, 100, 100)), 2),
    ("mały",   "small",  "adjectives", ("small_icon", (140, 180, 220)), 2),
    ("gorący", "hot",    "adjectives", ("sun_rays", (240, 100, 60)),  2),
    ("zimny",  "cold",   "adjectives", ("snowflake",(180, 200, 240)), 2),
    ("nowy",   "new",    "adjectives", ("star",     (255, 220, 100)), 2),
    ("stary",  "old",    "adjectives", ("old_icon",  (160, 140, 120)), 2),
    ("szybki", "fast",   "adjectives", ("running",  (100, 200, 120)), 2),
    ("wolny",  "slow",   "adjectives", ("snail_icon", (160, 160, 200)), 2),
    ("ładny",  "pretty", "adjectives", ("heart",    (240, 160, 200)), 2),
    ("brzydki","ugly",   "adjectives", ("frowny",   (140, 130, 120)), 2),
    ("miły",   "nice",   "adjectives", ("smiley",   (255, 220, 120)), 2),
    # Weather
    ("słońce", "sun",  "weather", ("sun_rays",   (255, 220, 60)),  2),
    ("deszcz", "rain", "weather", ("cloud_rain", (100, 160, 240)), 2),
    ("śnieg",  "snow", "weather", ("snowflake",  (220, 230, 250)), 2),
    ("wiatr",  "wind", "weather", ("wind_icon",  (180, 210, 240)), 2),
]

# ===================================================================
# Tier 3 — Verbs, polite phrases, nature (~30 words)
# ===================================================================

VOCAB_TIER3 = [
    # Verbs
    ("biegać",  "run",   "verbs", ("running", (100, 200, 120)), 3),
    ("jeść",    "eat",   "verbs", ("fork",    (230, 160, 80)),  3),
    ("spać",    "sleep", "verbs", ("moon",    (140, 130, 200)), 3),
    ("czytać",  "read",  "verbs", ("book",    (180, 120, 100)), 3),
    ("grać",    "play",  "verbs", ("ball",    (240, 180, 100)), 3),
    ("pływać",  "swim",  "verbs", ("drop",    (80, 160, 240)),  3),
    ("skakać",  "jump",  "verbs", ("running", (120, 200, 80)),  3),
    ("tańczyć", "dance", "verbs", ("star",    (240, 140, 220)), 3),
    ("śpiewać", "sing",  "verbs", ("music_note",  (220, 180, 240)), 3),
    ("rysować", "draw",  "verbs", ("pencil_icon", (240, 200, 100)), 3),
    ("pisać",   "write", "verbs", ("book",    (140, 120, 180)), 3),
    ("mówić",   "speak", "verbs", ("speech_icon", (200, 160, 140)), 3),
    ("myć",     "wash",  "verbs", ("drop",    (160, 200, 255)), 3),
    # Polite phrases
    ("proszę",       "please",  "phrases", ("heart",  (240, 180, 200)), 3),
    ("dziękuję",     "thanks",  "phrases", ("heart",  (255, 200, 140)), 3),
    ("cześć",        "hello",   "phrases", ("smiley", (255, 220, 100)), 3),
    ("do widzenia",  "goodbye", "phrases", ("wave_icon",  (180, 160, 200)), 3),
    ("tak",          "yes",     "phrases", ("checkmark",  (80, 200, 80)),   3),
    ("nie",          "no",      "phrases", ("cross_icon", (200, 80, 80)),   3),
    # Nature / places
    ("morze",  "sea",      "nature2", ("drop",      (60, 140, 220)),  3),
    ("góra",   "mountain", "nature2", ("triangle",  (160, 140, 120)), 3),
    ("las",    "forest",   "nature2", ("forest_icon", (40, 120, 50)),  3),
    ("ogród",  "garden",   "nature2", ("star",      (140, 200, 100)), 3),
]

# ===================================================================
# Combined vocabulary
# ===================================================================

ALL_VOCAB = VOCAB_TIER1 + VOCAB_TIER2 + VOCAB_TIER3

# Lookup by English word
_VOCAB_BY_ENGLISH = {entry[1]: entry for entry in ALL_VOCAB}


# ===================================================================
# Functions
# ===================================================================

def get_word_by_english(english):
    """Look up a vocab entry by English word."""
    return _VOCAB_BY_ENGLISH.get(english)


def get_unlocked_tier(mastery_data):
    """Determine the highest unlocked tier based on mastery progress.

    Tier 2 unlocked when 10+ tier-1 words in box >= 1.
    Tier 3 unlocked when 10+ tier-2 words in box >= 1.
    """
    tier = 1
    # Check tier 2 unlock
    t1_learning = sum(
        1 for w in VOCAB_TIER1
        if mastery_data.get(w[1], {}).get("box", 0) >= 1
    )
    if t1_learning >= TIER_UNLOCK_THRESHOLD:
        tier = 2
        # Check tier 3 unlock
        t2_learning = sum(
            1 for w in VOCAB_TIER2
            if mastery_data.get(w[1], {}).get("box", 0) >= 1
        )
        if t2_learning >= TIER_UNLOCK_THRESHOLD:
            tier = 3
    return tier


def get_random_words(count, exclude=None):
    """Return *count* random vocab entries, excluding any in *exclude*."""
    pool = ALL_VOCAB[:]
    if exclude:
        exclude_set = set(exclude)
        pool = [w for w in pool if w not in exclude_set]
    random.shuffle(pool)
    return pool[:count]


def get_smart_words(count, mastery_data, day_count=0, tier_unlock=None, exclude=None):
    """Select words using Leitner box algorithm for spaced repetition.

    Prioritises: 1 unseen word + ~60% struggling (box 0) + ~30% learning (box 1)
    + rest from mastered (box 2).
    """
    if tier_unlock is None:
        tier_unlock = get_unlocked_tier(mastery_data)

    pool = [w for w in ALL_VOCAB if w[4] <= tier_unlock]
    if exclude:
        exclude_set = set(exclude)
        pool = [w for w in pool if w not in exclude_set]

    unseen = [w for w in pool if w[1] not in mastery_data]
    box0 = [w for w in pool if mastery_data.get(w[1], {}).get("box") == 0]
    box1 = [w for w in pool if mastery_data.get(w[1], {}).get("box") == 1]
    box2 = [w for w in pool if mastery_data.get(w[1], {}).get("box") == 2]

    random.shuffle(unseen)
    random.shuffle(box0)
    random.shuffle(box1)
    random.shuffle(box2)

    result = []
    # 1 unseen word to introduce
    if unseen:
        result.append(unseen.pop(0))

    remaining = count - len(result)
    # Target mix: ~60% box0, ~30% box1, rest box2
    n_box0 = min(len(box0), max(1, int(remaining * 0.6)))
    n_box1 = min(len(box1), max(1, int(remaining * 0.3)))
    n_box2 = remaining - n_box0 - n_box1

    result.extend(box0[:n_box0])
    result.extend(box1[:n_box1])
    result.extend(box2[:max(0, n_box2)])

    # Fill any shortfall from whatever's available
    if len(result) < count:
        used = {w[1] for w in result}
        filler = [w for w in pool if w[1] not in used]
        random.shuffle(filler)
        result.extend(filler[:count - len(result)])

    random.shuffle(result)
    return result[:count]


def get_distractors(correct_entry, count=3, tier_unlock=None):
    """Return *count* random vocab entries different from *correct_entry*."""
    pool = ALL_VOCAB
    if tier_unlock is not None:
        pool = [w for w in pool if w[4] <= tier_unlock]
    pool = [w for w in pool if w[1] != correct_entry[1]]
    random.shuffle(pool)
    return pool[:count]


def _is_rusty(mastery_entry):
    """Check if a mastered word is rusty (not seen in RUSTY_DAYS_THRESHOLD+ days)."""
    last_seen = mastery_entry.get("last_seen")
    if not last_seen:
        return False  # no date = treat as recent (backward compat)
    try:
        last_date = datetime.date.fromisoformat(last_seen)
        days_ago = (datetime.date.today() - last_date).days
        return days_ago >= RUSTY_DAYS_THRESHOLD
    except (ValueError, TypeError):
        return False


def get_session_words(mastery_data, tier_unlock=None):
    """Select a balanced set of new + review words for a learning session.

    Returns: (new_words, review_words) — two lists of vocab entries.
    new_words = unseen words to introduce.
    review_words = rusty mastered words or struggling words to reinforce.
    Total size: SESSION_MIN_WORDS to SESSION_MAX_WORDS.
    """
    if tier_unlock is None:
        tier_unlock = get_unlocked_tier(mastery_data)

    pool = [w for w in ALL_VOCAB if w[4] <= tier_unlock]

    # Categorise
    unseen = [w for w in pool if w[1] not in mastery_data]
    rusty = [w for w in pool
             if mastery_data.get(w[1], {}).get("box") == 2
             and _is_rusty(mastery_data.get(w[1], {}))]
    box0 = [w for w in pool if mastery_data.get(w[1], {}).get("box") == 0]
    box1 = [w for w in pool if mastery_data.get(w[1], {}).get("box") == 1]

    random.shuffle(unseen)
    random.shuffle(rusty)
    random.shuffle(box0)
    random.shuffle(box1)

    # Pick new words (target SESSION_NEW_WORDS, min 2)
    n_new = min(len(unseen), SESSION_NEW_WORDS)
    n_new = max(n_new, min(2, len(unseen)))  # at least 2 if available
    new_words = unseen[:n_new]

    # Pick review words: prefer rusty, then box0 (struggling), then box1
    n_review = SESSION_REVIEW_WORDS
    review_words = []
    review_words.extend(rusty[:n_review])
    remaining_review = n_review - len(review_words)
    if remaining_review > 0:
        review_words.extend(box0[:remaining_review])
        remaining_review = n_review - len(review_words)
    if remaining_review > 0:
        review_words.extend(box1[:remaining_review])

    # Remove duplicates (a word shouldn't be in both lists)
    new_english = {w[1] for w in new_words}
    review_words = [w for w in review_words if w[1] not in new_english]

    # Enforce total bounds
    total = len(new_words) + len(review_words)
    if total < SESSION_MIN_WORDS:
        # Fill from any available pool words not already selected
        used = new_english | {w[1] for w in review_words}
        filler = [w for w in pool if w[1] not in used]
        random.shuffle(filler)
        needed = SESSION_MIN_WORDS - total
        review_words.extend(filler[:needed])
    elif total > SESSION_MAX_WORDS:
        # Trim review words first, then new words
        excess = total - SESSION_MAX_WORDS
        if len(review_words) > excess:
            review_words = review_words[:len(review_words) - excess]
        else:
            excess -= len(review_words)
            review_words = []
            new_words = new_words[:len(new_words) - excess]

    return new_words, review_words
