# Review Skill

Self-check before presenting changes to the user. Go through EVERY item below:

## Code Quality
- [ ] No syntax errors (run `python3 -c "import py_compile; py_compile.compile('FILE')"` for each changed file)
- [ ] No unused imports introduced
- [ ] No hardcoded values that should be in settings.py
- [ ] Backward compatible with old saves (if pet.py changed)

## UI/Layout (if UI was changed)
- [ ] All elements fit within 480x640 design resolution
- [ ] No overlapping elements or clutter
- [ ] Font sizes don't cause overflow in their containers
- [ ] Hover/click states work correctly
- [ ] Day/night modes both look correct

## Completeness
- [ ] EVERY item in the original request was implemented (list them all)
- [ ] No placeholders or TODO comments left behind
- [ ] No half-implemented features (e.g., icons that are just colors)

## Testing
- [ ] Run headless smoke test for each changed module
- [ ] Verify all 6 pet combos render (cat/dog x baby/kid/adult) if drawing.py changed

Report results as a checklist. Flag any failures BEFORE telling the user "done".
