Analyze game balance by reading settings.py and pet.py. Do NOT modify any files.

Run a headless Python script that computes and prints a balance report:

```bash
cd ~/Documents/GitHub/tamagotchi && SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python3 -c "
from settings import *
from pet import Pet

print('=== TAMAGOTCHI BALANCE REPORT ===')
print()

# --- Stat Decay Timelines ---
print('--- STAT DECAY (time from 100 to 0) ---')
decay_stats = [
    ('Hunger (day)',       HUNGER_DECAY_DAY),
    ('Hunger (night)',     HUNGER_DECAY_NIGHT),
    ('Happiness',          HAPPINESS_DECAY),
    ('Energy (day)',       ENERGY_DECAY_DAY),
    ('Energy (night awake)', ENERGY_DECAY_NIGHT_AWAKE),
    ('Cleanliness (0 poop)', CLEANLINESS_DECAY),
]
for name, rate in decay_stats:
    secs = STAT_MAX / rate
    mins = secs / 60
    print(f'  {name:25s}: {mins:5.1f} min ({secs:.0f}s) at {rate}/sec')

# Cleanliness with poop
for piles in [1, 2, 3]:
    effective = CLEANLINESS_DECAY * (1.0 + piles * (POOP_CLEANLINESS_MULTIPLIER - 1.0))
    secs = STAT_MAX / effective
    print(f'  Cleanliness ({piles} poop)      : {secs/60:5.1f} min ({secs:.0f}s) at {effective:.2f}/sec')

print()

# --- Stat Restore Actions ---
print('--- STAT RESTORE ACTIONS ---')
print(f'  Feed (simple):     +{FEED_AMOUNT} hunger')
foods = [('Apple', 25, 5, 0), ('Fish', 40, 0, 0), ('Cake', 20, 15, 0), ('Milk', 15, 0, 10)]
for name, h, hp, e in foods:
    print(f'  Feed ({name:6s}):    +{h} hunger, +{hp} happiness, +{e} energy')

cleanings = [('Bath', 40, 0, -5), ('Brush', 20, 5, 0), ('Towel', 15, 0, 0), ('Pick Up', 5, 0, 0)]
for name, c, hp, e in cleanings:
    print(f'  Clean ({name:7s}):   +{c} clean, +{hp} happiness, {e:+d} energy')

print(f'  Sleep energy restore:  +{ENERGY_RESTORE_SLEEPING}/sec (night), +{ENERGY_RESTORE_SLEEPING*0.5}/sec (day)')
print(f'  Time to full energy (0->100): {STAT_MAX/ENERGY_RESTORE_SLEEPING/60:.1f} min night, {STAT_MAX/(ENERGY_RESTORE_SLEEPING*0.5)/60:.1f} min day')

print()

# --- Day/Night Cycle ---
print('--- DAY/NIGHT CYCLE ---')
print(f'  Total cycle:  {DAY_LENGTH/60:.1f} min ({DAY_LENGTH}s)')
print(f'  Day phase:    {DAY_PHASE_LENGTH/60:.1f} min ({DAY_PHASE_LENGTH}s)')
print(f'  Night phase:  {NIGHT_PHASE_LENGTH/60:.1f} min ({NIGHT_PHASE_LENGTH}s)')
print(f'  Poop delay after eating: {POOP_DELAY}s ({POOP_DELAY/60:.1f} min)')

print()

# --- XP & Leveling ---
print('--- XP & LEVELING ---')
print(f'  Thresholds: {XP_LEVEL_THRESHOLDS}')
for i in range(1, len(XP_LEVEL_THRESHOLDS)):
    delta = XP_LEVEL_THRESHOLDS[i] - XP_LEVEL_THRESHOLDS[i-1]
    # Perfect quiz at that level's difficulty
    diff = 0 if i <= 3 else (1 if i <= 6 else 2)
    q_count = QUIZ_COUNT_BY_DIFF[diff]
    perfect_xp = q_count * XP_PER_CORRECT + XP_BONUS_PERFECT
    games_needed = delta / perfect_xp if perfect_xp > 0 else 999
    print(f'  Level {i} -> {i+1}: {delta} XP needed, ~{games_needed:.1f} perfect games (quiz gives {perfect_xp} XP)')

print()

# --- Edu Game Rewards ---
print('--- EDU GAME REWARDS ---')
for diff_name, diff_idx in [('Easy (L1-3)', 0), ('Medium (L4-6)', 1), ('Hard (L7+)', 2)]:
    q = QUIZ_COUNT_BY_DIFF[diff_idx]
    perfect_xp = q * XP_PER_CORRECT + XP_BONUS_PERFECT
    perfect_hp = min(EDU_GAME_HAPPINESS_CAP, EDU_GAME_BASE_HAPPINESS + q * EDU_GAME_PER_SCORE)
    zero_hp = EDU_GAME_BASE_HAPPINESS
    print(f'  {diff_name}: Quiz {q}Q -> perfect: +{perfect_xp} XP, +{perfect_hp} happiness | zero: +0 XP, +{zero_hp} happiness')

print()

# --- Difficulty Scaling ---
print('--- DIFFICULTY SCALING ---')
print(f'  Memory pairs:      {MEMORY_PAIRS_BY_DIFF}')
print(f'  Falling rounds:    {FALLING_ROUNDS_BY_DIFF}')
print(f'  Falling speed:     {FALLING_SPEED_BY_DIFF} px/s')
print(f'  Spelling words:    {SPELLING_COUNT_BY_DIFF}')
print(f'  Quiz questions:    {QUIZ_COUNT_BY_DIFF}')
print(f'  Quiz options:      {QUIZ_OPTIONS_BY_DIFF}')

print()

# --- Growth & Evolution ---
print('--- GROWTH STAGES ---')
for stage, days, care in GROWTH_THRESHOLDS:
    print(f'  {stage:10s}: day >= {days}, care_avg >= {care}')
print(f'  Evolution tiers: thriving > {EVOLUTION_THRIVING}, scruffy < {EVOLUTION_SCRUFFY}')

print()

# --- Session Limits ---
print('--- SESSION LIMITS ---')
print(f'  Soft limit (warning): {SESSION_SOFT_LIMIT/60:.0f} min')
print(f'  Hard limit (forced):  {SESSION_HARD_LIMIT/60:.0f} min')
print(f'  Warning interval:     {SESSION_WARNING_INTERVAL/60:.0f} min')

print()

# --- Sickness ---
print('--- SICKNESS ---')
print(f'  Sick threshold:      any stat < {STAT_SICK_THRESHOLD}')
print(f'  Sick runaway timer:  {SICK_TIMER_LIMIT}s ({SICK_TIMER_LIMIT/60:.1f} min)')
print(f'  Medicine restore:    +{MEDICINE_STAT_RESTORE} to sick stat')

print()

# --- Word Mastery ---
print('--- WORD MASTERY ---')
print(f'  Box 0 -> 1: streak >= 2 correct')
print(f'  Box 1 -> 2: streak >= 4 correct')
print(f'  Demotion:   1 wrong answer drops box by 1')
print(f'  Tier unlock: {TIER_UNLOCK_THRESHOLD} words at box >= 1')

from vocabulary import ALL_VOCAB, VOCAB_TIER1, VOCAB_TIER2, VOCAB_TIER3
print(f'  Total vocab: {len(ALL_VOCAB)} (T1: {len(VOCAB_TIER1)}, T2: {len(VOCAB_TIER2)}, T3: {len(VOCAB_TIER3)})')

print()

# --- Sustainability Check ---
print('--- BALANCE WARNINGS ---')
warnings = []

# Check if hunger decays faster than a child can reasonably feed
hunger_drain_per_min = HUNGER_DECAY_DAY * 60
if hunger_drain_per_min > 30:
    warnings.append(f'HIGH hunger drain: {hunger_drain_per_min:.0f}/min during day — child must feed often')

# Check if happiness drains faster than can be restored
happy_drain_per_min = HAPPINESS_DECAY * 60
if happy_drain_per_min > 20:
    warnings.append(f'HIGH happiness drain: {happy_drain_per_min:.0f}/min — needs frequent play')

# Check if energy can sustain a full day phase
energy_lifetime = STAT_MAX / ENERGY_DECAY_DAY
if energy_lifetime < DAY_PHASE_LENGTH:
    warnings.append(f'Energy runs out ({energy_lifetime:.0f}s) before day ends ({DAY_PHASE_LENGTH}s)')

# Check level gap jumps
for i in range(1, len(XP_LEVEL_THRESHOLDS) - 1):
    gap = XP_LEVEL_THRESHOLDS[i+1] - XP_LEVEL_THRESHOLDS[i]
    prev_gap = XP_LEVEL_THRESHOLDS[i] - XP_LEVEL_THRESHOLDS[i-1]
    if prev_gap > 0 and gap / prev_gap > 2.5:
        warnings.append(f'XP jump L{i+1}->L{i+2} is {gap/prev_gap:.1f}x previous gap ({prev_gap}->{gap})')

if warnings:
    for w in warnings:
        print(f'  WARNING: {w}')
else:
    print('  No balance warnings detected.')

print()
print('=== END REPORT ===')
"
```

Present the full output to the user, highlighting any WARNINGS found.
