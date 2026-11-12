# Pizza Magna for the Nintendo 3DS (prototype)

Homebrew port with [LÖVE Potion](https://lovebrew.org) 3 (LÖVE for the 3DS, in Lua). For now only the **Kitchen**:

- **Bottom screen (touch):** the bench, as in the browser game. Tap or drag on the pizza to put pieces, tap a bowl for whole / chopped (tapping whole again turns the next piece), and tap `EN|pt` to change language (English by default; the choice is saved).
- **Top screen:** the topping picker, dough and sauce, and the analysis (quality, cost, suggested price, appeal by customer type, notes). A toast shows each combo found.
- **Buttons:** D-pad left/right picks a topping (hold to scroll), L/R picks a group, D-pad up picks the dough, D-pad down picks the sauce, A switches whole/chopped, X turns the piece, B undoes (on an empty pizza it brings back what Y cleared), Y clears, SELECT switches language, START saves and quits.
- The pizza and the combos found are saved to `save.txt`, with pieces in the same compact format as the browser game (`packPieces`, recipe links `#p=`).

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

The prototype was tested with LÖVE 11.5 on a PC, not on a real 3DS. Things to check on the console: speed with many pieces (up to 300) on an old 3DS, the circular clip of big pieces (it uses a stencil; if the 3DS lacks it, a lobster's legs show past the crust), the touch coordinates, and the button names.
