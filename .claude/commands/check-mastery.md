Inspect the current save file's word mastery data. Read the save file and display:

1. Read the save file at `~/Documents/GitHub/tamagotchi/tamagotchi_save.json`
2. Extract `pet.word_mastery` from the save data
3. Display a summary:
   - Total words seen
   - Words by box: Box 0 (struggling), Box 1 (learning), Box 2 (mastered)
   - Current unlocked tier
   - Top 5 most-practiced words (by total attempts)
   - Words with the most errors (candidates for more practice)
4. If no save file exists, tell the user

Use the vocabulary module to calculate the unlocked tier:
```python
from vocabulary import get_unlocked_tier
tier = get_unlocked_tier(mastery_data)
```
