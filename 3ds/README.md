# Pizza Magna for the Nintendo 3DS (prototype)

Homebrew port with [LÖVE Potion](https://lovebrew.org) 3 (LÖVE for the 3DS, in Lua). For now the **Kitchen** and the **Menu** (SELECT switches between them).

**Kitchen**
- **Bottom screen (touch):** the bench, as in the browser game. Tap or drag on the pizza to put pieces, tap a bowl for whole / chopped (tapping whole again turns the next piece), tap the name on top to name the pizza. Buttons at the bottom: New pizza (press twice if the pizza was never saved), Add to menu (Save changes when editing a menu pizza), Menu, and `EN|pt` for the language (English by default; the choice is saved).
- **Top screen:** the topping picker, dough and sauce, and the analysis (quality, cost, suggested price, appeal by customer type, notes). A toast shows each combo found.
- **Buttons:** D-pad left/right picks a topping (hold to scroll), L/R picks a group, D-pad up picks the dough, D-pad down picks the sauce, A switches whole/chopped, X turns the piece, B undoes (on an empty pizza it brings back what Y cleared), Y clears, SELECT opens the Menu, START saves and quits.
- Adding a pizza needs at least 3 pieces. It goes on the menu at the suggested price; with no name it takes the name of its first combo, or "Pizza N".

**Menu**
- **Top screen:** the house menu, one row a pizza (small picture, name, dough and sauce, price, quality, margin), and a last row to create a new pizza. A pizza sold at a loss shows the warning on top.
- **Bottom screen:** the chosen pizza, its price with - and +, quality, cost and margin, and Edit recipe, Rename and Remove (press twice).
- **Buttons:** D-pad up/down picks a pizza, left/right changes the price by $0.50 ($1 to $30, as in the browser game), A edits (or creates, on the last row), X renames, Y removes (press twice), SELECT goes back to the Kitchen.
- Names use the console's keyboard (on a PC, type and press Enter).
- A new game starts with the three starter pizzas of the browser game.

Everything is saved to `save.txt`: the pizza on the bench, the menu and the combos found. Pieces are stored in the same compact format as the browser game (`packPieces`, recipe links `#p=`).

## Files

- `game/main.lua`: screens, input and drawing. `game/pizza.lua`: the rules (`analyze()`, portions, weights, `packPieces`) ported by hand from `index.html`. **When `analyze()` changes in the browser game, change it here too.**
- `game/data.lua`: toppings, doughs, sauces, combos, customer groups, weights and the whole `I18N` table. **Generated** from `index.html` by `node tools/export_3ds.js`; never edit it by hand.
- `game/atlas.lua` and `game/gfx/atlas*.png`: the toppings atlas packed again in 1024x1024 pages (the 3DS limit), with the turning pieces already turned and shadowed (`<id>_q0..q3`). `icon.png` (48x48). **Generated** from `assets/ingredients.js` by `python3 tools/export_3ds.py`.
- `lovebrew.toml`: settings for the bundler.

After adding toppings or changing data in the browser game, run both exporters again.

## Putting it on a 3DS

1. Zip `lovebrew.toml`, `icon.png` and the `game/` folder (all three at the top of the zip).
2. Upload the zip to <https://bundle.lovebrew.org> and download the `.3dsx`. The bundler converts the PNGs to the 3DS texture format.
3. Copy the `.3dsx` to `sdmc:/3ds/` and open it from the Homebrew Launcher.

Text uses the console's system font, loaded once and scaled to each size (each new font copies the whole system font, about 3 MB, and four of them crashed a New 3DS). To use the game's own pixel fonts, they first have to be converted to TTF (they're stored as woff2), and the bundler then converts them for the 3DS.

## Trying it on a PC

With [LÖVE](https://love2d.org) 11.4 or newer: `love 3ds/game`. The window shows the top screen above the bottom one, and the mouse works as the stylus (right-click turns the piece). Keys: arrows, Q/W = L/R, Z = A, X = B, S = X, A = Y, Tab = SELECT, Esc = START.

## Not tested yet

Runs on a New 3DS (Homebrew Launcher, bundled with bundle.lovebrew.org). Still to check: speed with many pieces (up to 300) on an old 3DS, the circular clip of big pieces (it uses a stencil; if the 3DS lacks it, a lobster's legs show past the crust), the touch coordinates, and the button names.
