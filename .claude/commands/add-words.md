Add new Polish-English vocabulary words to the tamagotchi game. The user will specify the words to add.

Steps:
1. Read `vocabulary.py` to understand the current word list and tier structure
2. Add the new words to the appropriate tier list (`VOCAB_TIER1`, `VOCAB_TIER2`, or `VOCAB_TIER3`)
3. Each entry format: `(polish, english, category, (shape, color), tier)`
4. Choose an appropriate shape from existing ones: `circle`, `rect`, `triangle`, `ellipse`, `drop`, `heart`, `star`, `smiley`, `frowny`, `sleepy`, `book`, `ball`, `running`, `fork`, `moon`, `sun_rays`, `cloud_rain`, `snowflake`, `wind_icon`, `cat_face`, `dog_face`, `fish_icon`, `bird_icon`, `apple_icon`, `bottle`, `cake_icon`, `loaf`, `head_icon`, `hand_icon`, `eye_icon`, `plate`, or `num_N`
5. Pick a fitting color tuple (R, G, B)
6. Ensure Polish diacritics are correct (ą, ę, ć, ł, ń, ó, ś, ź, ż)
7. Run `/test` to verify the word count and that nothing broke

$ARGUMENTS
