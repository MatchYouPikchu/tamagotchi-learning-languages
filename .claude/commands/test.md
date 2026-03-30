Run the tamagotchi headless test suite to verify core systems work:

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

print('All tests passed!')
"
```

Report which tests passed and which failed. If any fail, investigate the root cause.
