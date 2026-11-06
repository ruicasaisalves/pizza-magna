# Art packs considered

Research notes (November 2026). Prices and licences change: check the page before buying.
**Never put pack files in git** (the licences forbid redistribution and the repository may be public). Keep only the scripts that read them.

## Likely choice: LimeZu, Modern Interiors
https://limezu.itch.io/moderninteriors

- Price: pay what you want from $1.50 for the full version; there is a free version to try.
- Licence: commercial use and editing allowed; reselling or distributing (edited or not) forbidden; **credit required** (link to https://limezu.itch.io/).
- 16, 32 and 48 px tiles. Top-down view, 2D and 3D walls.
- Modern setting, which suits a pizzeria better than a medieval pack. Rooms: kitchen, canteen, bakery, butcher, fishmonger, grocery. Thousands of furniture items and over 100 animated objects. Nothing pizza-specific in the description.
- Character generator: over 100 outfits, 200 hairstyles, 80 accessories, 9 skin tones. Listed animations: idle, run, give, shoot, punch, pick up, read, lift, throw.
- **To check with the free version:** sitting poses (comments report that the feet don't show when sitting and that the author would add a pose), eating and cooking (not listed).

## Other options

| Pack | Price | Tiles | Notes |
|---|---|---|---|
| Mana Seed, Cozy Furnishings (seliel-the-shaper) | $17.99 ($11.69 on sale) | 16 px | Style closest to Pizza Tycoon. Furniture only: walls and floors come from another pack (Iconic Homestead). Own licence (Mana Seed User License), not read yet. |
| Mana Seed, Character Base | paid | 32 px | Sitting-on-a-chair poses in 4 directions (devlog "Resting Poses Update"). |
| Mana Seed, NPC Pack 2 | $9.99 ($6.49) | 32 px cells | Barman and cook only walk (the cook also drinks from a flask). No use for cooking. |
| Faymus, Restaurant Interiors | $0.50 | 16 px | Chairs, tables, floors and wallpaper in 9 styles (Bistro, Diner…). Commercial use and editing allowed, no credit required, no redistribution. No characters or kitchen. |
| srpapitas12, Vintage Restaurant | $3 | 16 px | 145 sprites, top-down. Commercial use allowed, no reselling, credit requested (unclear if required). Contents not detailed. |
| alilali, Fast Food tileset | €6 | 32 px | Pizzeria and burgers, walls, floors and furniture. RPG Maker format. "May edit, may not resell, give credit". Commercial use not mentioned. |
| AintGotJack, Gritty Kitchen Interior | free for personal use, $3.99 commercial | | Kitchen. "Gritty" style, not looked at in detail. |
| GameBetweenTheLines, Top Down Pixel Art Characters | free (commercial allowed) | | 40 characters, idle and walking only. |
| Pixxiland, Topdown NPC Bartender | about $1 | 64 px | Different scale. |

## Open questions
- Try the free version of Modern Interiors: sitting, eating, carrying a tray, cooking.
- Read the Mana Seed User License, if the Mana Seed option goes ahead.
- Everything pizza-specific (ovens, pizzas, toppings, boxes, menu) is still drawn by us in `sprites.js`, at the same scale and palette as the chosen pack.

---

# Other saved references

## Pizza Legacy (open-source reimplementation of Pizza Tycoon)
https://pizzalegacy.nl/ · code: https://codeberg.org/cowomaly/pizzalegacy/

- Hobby project since 2010, in C++, **GNU GPL v3** licence. Version 1.0.0-beta.2 (November 2026), described as complete, tuning balance and bugs.
- **Does not include the original game's assets**: it asks for a legal copy of the English DOS version. Windows, Linux, macOS and Haiku.
- Useful as a **reference for rules and balance** (economy, competitors, toppings, management loop). Reading its code and ideas is fine.
- **Careful with GPL v3:** copying its code into Pizza Magna would force us to publish our game under GPL v3 too. To avoid that, read it only to understand the mechanics and write our code from scratch. The original's assets remain out of the question.

---

# Style decision (November 2026)

**Detailed pixel art, in the manner of 90s management games**, on a 320×200 logical screen scaled by whole numbers:
toppings of ~25–30 px, light from the top left, short ramps per material, 4×4 ordered dithering and selective outlining
(the darkest tone of the material itself, not black), 3 variants per topping, pizza on a marble bench.
Generator: `tools/gen_ingredients.py` (mozzarella, tomato, bacon; `python3 tools/gen_ingredients.py <folder>`).
