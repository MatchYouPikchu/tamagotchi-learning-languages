Run all quality gates before pushing. Do NOT modify any files — only report results.

Run each check below in sequence. Report a pass/fail summary at the end.

## Step 1: Syntax Check
Compile-check every Python file:
```bash
cd ~/Documents/GitHub/tamagotchi && python3 -c "
import py_compile, glob, sys
errors = []
for f in sorted(glob.glob('*.py')):
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        errors.append(str(e))
if errors:
    print('SYNTAX FAIL:')
    for e in errors: print(f'  {e}')
    sys.exit(1)
else:
    print(f'SYNTAX: All {len(glob.glob(\"*.py\"))} files OK')
"
```

## Step 2: Import Check
Verify all modules import cleanly:
```bash
cd ~/Documents/GitHub/tamagotchi && SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python3 -c "
import sys
modules = ['settings', 'pet', 'vocabulary', 'save', 'audio', 'drawing', 'ui', 'edu_games', 'minigames', 'wardrobe']
errors = []
for m in modules:
    try:
        __import__(m)
    except Exception as e:
        errors.append(f'{m}: {e}')
if errors:
    print('IMPORT FAIL:')
    for e in errors: print(f'  {e}')
    sys.exit(1)
else:
    print(f'IMPORTS: All {len(modules)} modules OK')
"
```

## Step 3: Unit Tests (existing /test suite)
```bash
cd ~/Documents/GitHub/tamagotchi && SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python3 -c "
from pet import Pet
p = Pet('cat', 'Test')

# Mastery tracking
p.record_word_result('cat', True)
p.record_word_result('cat', True)
assert p.word_mastery['cat']['box'] == 1, 'Box promotion failed'
p.record_word_result('cat', True)
p.record_word_result('cat', True)
assert p.word_mastery['cat']['box'] == 2, 'Box 2 promotion failed'
p.record_word_result('cat', False)
assert p.word_mastery['cat']['box'] == 1, 'Demotion failed'

# Serialization roundtrip
d = p.to_dict()
p2 = Pet.from_dict(d)
assert p2.word_mastery == p.word_mastery, 'Serialization failed'

# Backward compat
d2 = d.copy()
del d2['word_mastery']
p3 = Pet.from_dict(d2)
assert p3.word_mastery == {}, 'Backward compat failed'

# Vocabulary
from vocabulary import ALL_VOCAB, get_unlocked_tier, get_smart_words, get_word_by_english, VOCAB_TIER1, VOCAB_TIER2
assert len(ALL_VOCAB) >= 90, f'Vocab too small: {len(ALL_VOCAB)}'
assert get_unlocked_tier({}) == 1
assert get_word_by_english('cat') is not None

# Tier unlocking
mastery = {w[1]: {'box': 1, 'correct': 2, 'wrong': 0, 'streak': 2} for w in VOCAB_TIER1[:10]}
assert get_unlocked_tier(mastery) == 2
for w in VOCAB_TIER2[:10]:
    mastery[w[1]] = {'box': 1, 'correct': 2, 'wrong': 0, 'streak': 2}
assert get_unlocked_tier(mastery) == 3

# Smart word selection respects tiers
words = get_smart_words(5, {}, tier_unlock=1)
assert all(w[4] == 1 for w in words), 'Tier filter failed'

# Edu game classes instantiate
import pygame; pygame.init()
from edu_games import QuizGame, FallingWordGame, SpellingGame, MemoryGame, WordBook, PlayMenu, _get_difficulty
assert _get_difficulty(1) == 0
assert _get_difficulty(5) == 1
assert _get_difficulty(8) == 2
q = QuizGame(None, level=1); assert q.max_score == 4
q = QuizGame(None, level=5); assert q.max_score == 6
q = QuizGame(None, level=8); assert q.max_score == 8
assert len(PlayMenu.ITEMS) == 6

print('UNIT TESTS: All passed')
"
```

## Step 4: Icon Coverage
```bash
cd ~/Documents/GitHub/tamagotchi && SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python3 -c "
import pygame; pygame.init()
screen = pygame.display.set_mode((480, 640))
surface = pygame.Surface((480, 640))
from vocabulary import ALL_VOCAB
from edu_games import _draw_vocab_icon
color_words = {'red','blue','green','yellow','white','black','pink','orange'}
fails = [e[1] for e in ALL_VOCAB if e[3][0]=='circle' and e[1] not in color_words]
for e in ALL_VOCAB: _draw_vocab_icon(surface, 100, 100, e[3], size=20)
if fails:
    print(f'ICON COVERAGE FAIL: {fails}')
    import sys; sys.exit(1)
else:
    print(f'ICON COVERAGE: All {len(ALL_VOCAB)} vocab words have specific icons')
"
```

## Step 5: Save Compatibility
```bash
cd ~/Documents/GitHub/tamagotchi && SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python3 -c "
from pet import Pet
from settings import PET_CAT, PET_DOG

# Test minimal old-format save (missing newer fields)
minimal = {'pet_type': 'cat', 'name': 'Old', 'hunger': 50, 'happiness': 50,
           'energy': 50, 'cleanliness': 50, 'action': 'idle', 'is_sick': False,
           'sick_timer': 0, 'day_count': 1, 'cycle_time': 0}
try:
    p = Pet.from_dict(minimal)
    assert p.name == 'Old'
    assert p.word_mastery == {} or p.word_mastery is not None
    print('SAVE COMPAT: Old-format save loads OK')
except Exception as e:
    print(f'SAVE COMPAT FAIL: {e}')
    import sys; sys.exit(1)

# Full roundtrip
for ptype in [PET_CAT, PET_DOG]:
    p = Pet(ptype, 'FullTest')
    p.xp = 500
    p.level = 5
    p.word_mastery = {'test': {'box': 2, 'correct': 10, 'wrong': 1, 'streak': 4}}
    d = p.to_dict()
    p2 = Pet.from_dict(d)
    assert p2.xp == 500 and p2.level == 5
    assert p2.word_mastery == p.word_mastery
print('SAVE COMPAT: Full roundtrip OK for both pet types')
"
```

## Summary
After running all 5 steps, present a summary table:

| Check | Status |
|-------|--------|
| Syntax | PASS/FAIL |
| Imports | PASS/FAIL |
| Unit Tests | PASS/FAIL |
| Icon Coverage | PASS/FAIL |
| Save Compat | PASS/FAIL |

If ALL pass, tell the user it's safe to push. If any fail, list the failures and suggest fixes before pushing.
