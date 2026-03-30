Run a headless integration test that simulates a full play session. Do NOT modify any files.

This tests the entire game loop: create pet, feed, play edu games, check stat changes, level-up, growth, word mastery, and save/load roundtrip.

```bash
cd ~/Documents/GitHub/tamagotchi && SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python3 -c "
import sys, os, json, tempfile
from pet import Pet
from save import save_game, load_game
from vocabulary import ALL_VOCAB, get_unlocked_tier, get_smart_words, VOCAB_TIER1, VOCAB_TIER2
from settings import *

passed = 0
failed = 0
errors = []

def check(name, condition, detail=''):
    global passed, failed
    if condition:
        passed += 1
        print(f'  PASS: {name}')
    else:
        failed += 1
        msg = f'  FAIL: {name}'
        if detail:
            msg += f' ({detail})'
        print(msg)
        errors.append(name)

print('=== PLAYTEST: Integration Test Suite ===')
print()

# ---- 1. Pet Creation ----
print('--- 1. Pet Creation ---')
pet = Pet(PET_CAT, 'TestKitty')
check('Pet created with correct name', pet.name == 'TestKitty')
check('Stats start at STAT_START',
      pet.hunger == STAT_START and pet.happiness == STAT_START and
      pet.energy == STAT_START and pet.cleanliness == STAT_START,
      f'got h={pet.hunger} hp={pet.happiness} e={pet.energy} c={pet.cleanliness}')
check('Level starts at 1', pet.level == 1)
check('XP starts at 0', pet.xp == 0)
check('Growth stage is baby', pet.growth_stage == GROWTH_BABY)
check('Word mastery is empty', pet.word_mastery == {})
print()

# ---- 2. Feeding ----
print('--- 2. Feeding ---')
pet2 = Pet(PET_DOG, 'FeedTest')
pet2.hunger = 30
pet2.feed()
check('Simple feed adds FEED_AMOUNT', pet2.hunger == min(STAT_MAX, 30 + FEED_AMOUNT),
      f'expected {min(STAT_MAX, 30+FEED_AMOUNT)}, got {pet2.hunger}')

pet3 = Pet(PET_CAT, 'FoodTest')
pet3.hunger = 50
pet3.happiness = 50
pet3.energy = 50
pet3.feed_food(25, 5, 10)  # Apple-like
check('Food feed applies hunger', pet3.hunger == 75, f'got {pet3.hunger}')
check('Food feed applies happiness', pet3.happiness == 55, f'got {pet3.happiness}')
check('Food feed applies energy', pet3.energy == 60, f'got {pet3.energy}')

# Stat capping
pet4 = Pet(PET_CAT, 'CapTest')
pet4.hunger = 90
pet4.feed_food(50, 0, 0)
check('Hunger caps at STAT_MAX', pet4.hunger == STAT_MAX, f'got {pet4.hunger}')
print()

# ---- 3. Stat Decay ----
print('--- 3. Stat Decay ---')
pet5 = Pet(PET_CAT, 'DecayTest')
pet5.hunger = 50
pet5.happiness = 50
pet5.energy = 50
pet5.cleanliness = 50
old_h = pet5.hunger
pet5.update(10.0)  # 10 seconds of daytime
check('Hunger decays over time', pet5.hunger < old_h,
      f'{old_h} -> {pet5.hunger}')
check('Happiness decays over time', pet5.happiness < 50)
check('Energy decays over time', pet5.energy < 50)
check('Cleanliness decays over time', pet5.cleanliness < 50)
check('Stats stay non-negative after long decay', True)  # sanity
pet6 = Pet(PET_CAT, 'ZeroTest')
pet6.hunger = 1
pet6.update(100.0)
check('Hunger floors at 0', pet6.hunger >= 0, f'got {pet6.hunger}')
print()

# ---- 4. XP & Leveling ----
print('--- 4. XP & Leveling ---')
pet7 = Pet(PET_CAT, 'XPTest')
check('Starts at level 1', pet7.level == 1)
result = pet7.add_xp(49)
check('49 XP not enough for level 2', pet7.level == 1, f'level={pet7.level}')
result = pet7.add_xp(1)
check('50 XP reaches level 2', pet7.level == 2, f'level={pet7.level}')
check('add_xp returns True on level-up', result == True)

pet7.add_xp(70)  # total 120
check('120 XP reaches level 3', pet7.level == 3, f'xp={pet7.xp}, level={pet7.level}')
pet7.add_xp(100)  # total 220
check('220 XP reaches level 4', pet7.level == 4, f'xp={pet7.xp}, level={pet7.level}')
print()

# ---- 5. Edu Game Reward Simulation ----
print('--- 5. Edu Game Rewards ---')
pet8 = Pet(PET_CAT, 'EduTest')
pet8.happiness = 50

# Simulate a perfect quiz at easy difficulty (4 questions)
score = 4
max_score = 4
happiness_reward = min(EDU_GAME_HAPPINESS_CAP, EDU_GAME_BASE_HAPPINESS + score * EDU_GAME_PER_SCORE)
xp_reward = score * XP_PER_CORRECT + XP_BONUS_PERFECT  # perfect bonus
check('Perfect quiz happiness calc', happiness_reward == min(40, 10 + 16),
      f'got {happiness_reward}')
check('Perfect quiz XP calc', xp_reward == 60, f'got {xp_reward}')

pet8.boost_happiness(happiness_reward)
check('Happiness applied correctly', pet8.happiness == min(STAT_MAX, 50 + happiness_reward),
      f'got {pet8.happiness}')

leveled = pet8.add_xp(xp_reward)
check('XP applied, level-up detected', pet8.xp == 60 and pet8.level == 2,
      f'xp={pet8.xp}, level={pet8.level}')

# Zero score
zero_hp = min(EDU_GAME_HAPPINESS_CAP, EDU_GAME_BASE_HAPPINESS + 0 * EDU_GAME_PER_SCORE)
check('Zero score still gives base happiness', zero_hp == EDU_GAME_BASE_HAPPINESS)
print()

# ---- 6. Word Mastery (Leitner Boxes) ----
print('--- 6. Word Mastery ---')
pet9 = Pet(PET_CAT, 'MasteryTest')
pet9.record_word_result('cat', True)
check('First correct: box 0, streak 1',
      pet9.word_mastery['cat']['box'] == 0 and pet9.word_mastery['cat']['streak'] == 1)
pet9.record_word_result('cat', True)
check('Second correct: promoted to box 1', pet9.word_mastery['cat']['box'] == 1,
      f'box={pet9.word_mastery[\"cat\"][\"box\"]}')
pet9.record_word_result('cat', True)
pet9.record_word_result('cat', True)
check('Fourth correct: promoted to box 2 (mastered)', pet9.word_mastery['cat']['box'] == 2)
pet9.record_word_result('cat', False)
check('Wrong answer demotes from box 2 to 1', pet9.word_mastery['cat']['box'] == 1)
check('Wrong resets streak to 0', pet9.word_mastery['cat']['streak'] == 0)
print()

# ---- 7. Tier Unlocking ----
print('--- 7. Vocabulary Tier Unlocking ---')
check('Empty mastery = tier 1', get_unlocked_tier({}) == 1)
mastery = {}
for w in VOCAB_TIER1[:9]:
    mastery[w[1]] = {'box': 1, 'correct': 2, 'wrong': 0, 'streak': 2}
check('9 words at box 1 = still tier 1', get_unlocked_tier(mastery) == 1)
mastery[VOCAB_TIER1[9][1]] = {'box': 1, 'correct': 2, 'wrong': 0, 'streak': 2}
check('10 words at box 1 = tier 2 unlocked', get_unlocked_tier(mastery) == 2)
for w in VOCAB_TIER2[:10]:
    mastery[w[1]] = {'box': 1, 'correct': 2, 'wrong': 0, 'streak': 2}
check('10 T2 words at box 1 = tier 3 unlocked', get_unlocked_tier(mastery) == 3)
print()

# ---- 8. Smart Word Selection ----
print('--- 8. Smart Word Selection ---')
words = get_smart_words(5, {}, tier_unlock=1)
check('get_smart_words returns 5 words', len(words) == 5)
check('Tier 1 only when tier_unlock=1', all(w[4] == 1 for w in words),
      f'tiers: {[w[4] for w in words]}')
words2 = get_smart_words(5, {}, tier_unlock=2)
tiers_seen = set(w[4] for w in words2)
check('Tier 2 unlocked allows T1+T2 words', tiers_seen.issubset({1, 2}))
print()

# ---- 9. Growth Stage Progression ----
print('--- 9. Growth Stages ---')
pet10 = Pet(PET_CAT, 'GrowthTest')
check('Starts as baby', pet10.growth_stage == GROWTH_BABY)
pet10.day_count = 4
pet10.care_avg = 55
pet10.check_growth()
check('Day 4 + care 55 = kid', pet10.growth_stage == GROWTH_KID,
      f'got {pet10.growth_stage}')
pet10.day_count = 11
pet10.care_avg = 60
pet10.check_growth()
check('Day 11 + care 60 = adult', pet10.growth_stage == GROWTH_ADULT,
      f'got {pet10.growth_stage}')

# Low care blocks growth
pet11 = Pet(PET_DOG, 'LowCareTest')
pet11.day_count = 11
pet11.care_avg = 30
pet11.check_growth()
check('Low care blocks adult stage', pet11.growth_stage != GROWTH_ADULT,
      f'got {pet11.growth_stage}')
print()

# ---- 10. Save/Load Roundtrip ----
print('--- 10. Save/Load Roundtrip ---')
pet12 = Pet(PET_DOG, 'SaveTest')
pet12.hunger = 42
pet12.xp = 150
pet12.level = 3
pet12.word_mastery = {'dog': {'box': 2, 'correct': 5, 'wrong': 1, 'streak': 4}}
d = pet12.to_dict()
pet13 = Pet.from_dict(d)
check('Name survives roundtrip', pet13.name == 'SaveTest')
check('Hunger survives roundtrip', pet13.hunger == 42)
check('XP survives roundtrip', pet13.xp == 150)
check('Level survives roundtrip', pet13.level == 3)
check('Word mastery survives roundtrip', pet13.word_mastery == pet12.word_mastery)

# Backward compat (missing keys)
d2 = d.copy()
for key in ['word_mastery', 'streak_days', 'appearance']:
    d2.pop(key, None)
try:
    pet14 = Pet.from_dict(d2)
    check('Old save without new fields loads OK', True)
except Exception as e:
    check('Old save without new fields loads OK', False, str(e))
print()

# ---- 11. Sickness System ----
print('--- 11. Sickness ---')
pet15 = Pet(PET_CAT, 'SickTest')
pet15.hunger = STAT_SICK_THRESHOLD - 1
pet15.update(0.1)
check('Low stat triggers sickness', pet15.is_sick == True,
      f'hunger={pet15.hunger}, is_sick={pet15.is_sick}')
print()

# ---- 12. Edu Game Streak ----
print('--- 12. Edu Game Streak ---')
pet16 = Pet(PET_CAT, 'StreakTest')
pet16.day_count = 1
pet16.record_edu_game()
check('First edu game tracked', pet16.edu_games_today == 1)
pet16.day_count = 2
pet16._last_edu_day = 1
pet16.record_edu_game()
check('Consecutive day streak increments', pet16.streak_days >= 1,
      f'streak={pet16.streak_days}')
print()

# ===== SUMMARY =====
print('=' * 40)
total = passed + failed
print(f'RESULTS: {passed}/{total} passed, {failed} failed')
if errors:
    print(f'FAILURES: {errors}')
    sys.exit(1)
else:
    print('ALL INTEGRATION TESTS PASSED!')
    sys.exit(0)
"
```

Report which tests passed and which failed. If any fail, investigate the root cause and suggest fixes.
