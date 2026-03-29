# Tamagotchi Project Guidelines

## Project Scope
- This project is **Tamagotchi** (not GameJulia or other projects). Only edit files within this project directory. Double-check file paths before editing.

## Workflow Rules
- **ALWAYS pause for design approval before implementing features.** When a plan has multiple parts, present the design/approach for each part and wait for explicit user approval before writing any code.
- STOP before writing any code. If the task involves ANY of the following, you MUST use `EnterPlanMode` and get explicit user approval before implementing:
  - Touches 2+ files
  - Adds a new UI element, screen, or overlay
  - Changes game behavior or state machine
  - Adds or modifies save, audio, or vocabulary systems
  - Takes more than ~20 lines of changes total
- The ONLY exceptions are single-file bug fixes, typo corrections, or constant tweaks where the change is obvious and self-contained.
- **Workflow: Design → User approves → Implement → Verify**
- If the user's message includes an already-approved plan (e.g., "Implement the following plan:"), you may proceed directly to implementation.

## Multi-Step Feature Plans
- For plans with 3+ features, implement **ONE feature at a time**. After each feature: summarize what was done, verify it works, then ask if you should proceed to the next.
- Do not start part 2 until part 1 is confirmed working.
- After each part, run the game and check for visual regressions.

## Project Overview

A kid-friendly virtual pet game with Polish-English vocabulary learning, built with Python + pygame. Procedural drawing only (no sprite assets). Target audience: young children learning Polish.

## Architecture

| File | Purpose |
|------|---------|
| `main.py` | Game loop, state machine, sub-state routing |
| `pet.py` | Pet model — stats, decay, XP/levels, growth stages, word mastery |
| `settings.py` | All constants, tuning values, colors |
| `drawing.py` | `PetDrawer` — procedural kawaii pet rendering |
| `ui.py` | `UI` class — HUD, stat bars, room, menus, overlays |
| `edu_games.py` | `PlayMenu`, 4 edu games (`QuizGame`, `FallingWordGame`, `SpellingGame`, `MemoryGame`), `WordBook` progress screen |
| `minigames.py` | Fun mini-games (`CatchTreats`, `PopBubbles`, `ChaseBall`), `FoodMenu`, `CleanMenu`, `MedicineGame` |
| `vocabulary.py` | ~90 Polish-English words in 3 tiers, spaced-repetition selection (`get_smart_words`), tier unlocking |
| `audio.py` | `SoundManager` — procedural sound effects + TTS speech |
| `save.py` | JSON save/load for pet state |

## Key Patterns

- **Sub-state system**: `main.py` sets `self.sub_state` to any overlay (menu/game). Each sub-state has `handle_event()`, `update(dt)`, `draw(surface, mouse_pos)`, `.done`, `.result`. When `.done` is True, `_resolve_sub_state()` processes the result.
- **Drawing style**: Clean kawaii outline technique — draw BLACK at `size+OUTLINE_WIDTH`, then body color at normal size. All icons/shapes are procedural via `_draw_vocab_icon()`.
- **Vocab entry format**: `(polish, english, category, icon_hint, tier)` where `icon_hint = (shape_name, color_tuple)`.
- **Word mastery**: Leitner box system in `pet.word_mastery` dict. Box 0=struggling, 1=learning, 2=mastered. Streak 2 promotes to box 1, streak 4 to box 2, wrong answer demotes.
- **Difficulty scaling**: `_get_difficulty(level)` returns 0/1/2 (easy/medium/hard). Game params (pairs, rounds, speed, question count) index into `*_BY_DIFF` tuples in settings.
- **Tier system**: 3 vocabulary tiers. Tier N+1 unlocks when 10 tier-N words reach box >= 1.

## Testing

Run headless tests (no display needed):
```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python3 -c "from pet import Pet; ..."
```

Full interactive test:
```bash
python3 main.py
```

## UI Development Rules

**Visual preview before implementation is MANDATORY.** Any change to characters, UI elements, drawing code, or visual appearance MUST be previewed first by generating an HTML catalog or PNG comparison image (using `generate_catalog.py` or a standalone script with monkey-patching). The preview must be opened in the browser and explicitly approved by the user before modifying the actual source code. Never apply visual changes to the codebase without prior approval of the rendered preview.

When making UI changes, always verify that EVERY element affected by the change is visually correct — never leave partial implementations (e.g., some icons updated but others left as placeholders). After any UI modification, do a systematic audit of all related elements before reporting completion.

When changing font sizes, spacing, or layout dimensions, trace ALL downstream effects on screen layout before committing. Check for: overflow/clutter, overlay visibility, stat bar sizing, and test at the actual game resolution (480x640 design, 1.5x window scale). Never change sizes in isolation.


## Vocabulary Icon Rule

Every vocab entry in `vocabulary.py` must have a specific icon shape in its `icon_hint` — not the generic `"circle"`. The only exception is color words (category `"colors"`), which intentionally use `"circle"` to display a colored swatch. When adding new words, always create a matching `elif shape == "..."` handler in `_draw_vocab_icon()` in `edu_games.py`.

Verify with the headless icon coverage test:
```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python3 -c "
import pygame; pygame.init()
screen = pygame.display.set_mode((480, 640))
surface = pygame.Surface((480, 640))
from vocabulary import ALL_VOCAB
from edu_games import _draw_vocab_icon
color_words = {'red','blue','green','yellow','white','black','pink','orange'}
fails = [e[1] for e in ALL_VOCAB if e[3][0]=='circle' and e[1] not in color_words]
for e in ALL_VOCAB: _draw_vocab_icon(surface, 100, 100, e[3], size=20)
print('FAIL: ' + str(fails)) if fails else print('PASS: All vocab words have specific icons')
"
```

## Important Constraints

- No external sprite/image assets — all graphics are procedural pygame drawing
- Keep vocabulary appropriate for young children
- Polish diacritics must be correct (ą, ę, ć, ł, ń, ó, ś, ź, ż)
- Old saves must load without errors (backward-compatible serialization)
- Design resolution is 480x640; UI elements must fit within these bounds
- Session time limits exist for child safety (30min soft, 45min hard cap)
