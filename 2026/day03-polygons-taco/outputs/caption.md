# Day 3 Carto to Taco (Taco Tuesday): caption, methods reply, alt text
Drafts for funkchan to review and post himself. Nothing has been posted.

## Caption (272 characters, Python `len`; `×` and `á` count as 1 each on X)
```
Carto to Taco: real places shaped like taco ingredients. Wainwright, Alaska shell, Chonos beef, Iceland lettuce, Zadar cheese, Iowa tomato, La Pampa onion, Halmahera cilantro, Montalbán sour cream. Iceland is 768× bigger than its dollop.
#30DayMapChallenge Day 3: Polygons
```
Fun fact check: Iceland 102,361.8 km² / Montalbán 133.3 km² = 767.9×, computed in `scripts/18_final.py` from the equal-area geometry (`layout.json → true_scale_strip`).

## Methods reply (two replies: 263 + 258 characters)
```
How it was made: ~54,000 real boundaries (Natural Earth, geoBoundaries, US Census places for the shell), each in its own equal-area projection, scored by shape overlap (IoU) against a simple template per ingredient (half-dome, dice, frilly leaf, dollop) every 5°.
```
```
Top matches were checked by eye. Only uniform scaling and rotation, no stretching or mirroring. Repeats are marked ×N; 3 dice repeat real counties, and dice are spaced apart and shrunk 8% (true sizes in the strip). Credits are in the image; code in the repo.
```
Repo: https://github.com/funkchan/30daymapchallenge/tree/main/2026/day03-polygons-taco (this link works once the day folder is merged to main).

## Alt text (874 characters; X's limit is 1,000)
```
Infographic "Carto to Taco: Real places shaped like taco ingredients." Top left, a side-view hard-shell taco. The shell is the outline of Wainwright, Alaska, drawn twice as front and back walls. Its open end shows ground beef made of Chile's Chonos Archipelago. Along the rim: seven copies of Iceland as lettuce, four small cheese shreds shaped like Croatia's Zadar islands tucked between lettuce and shell, tomato dice from six square Iowa counties, onion dice from La Pampa departments in Argentina, four Halmahera (Indonesia) cilantro sprigs and a sour cream dollop shaped like Montalbán, Venezuela. On the right, an exploded view stacks the eight layers, labelled 1 to 8. Below the taco, all eight at true scale: Iceland 102,362 km², Halmahera 18,214, La Pampa 12,563, Iowa 8,933, Chonos 2,452, Zadar 264, Montalbán 133, Wainwright 37. Credits run along the bottom left.
```
