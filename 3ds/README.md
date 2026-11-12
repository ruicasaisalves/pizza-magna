# Pizza Magna for the Nintendo 3DS (prototype)

Homebrew port with [LÖVE Potion](https://lovebrew.org) 3 (LÖVE for the 3DS, in Lua): the **Kitchen**, the **Menu**, the **Day**, the **Contest** and the **Shop**. SELECT goes to the next screen; outside the Kitchen, L/R go back and forth too. The header shows the screens, the cash and the reputation.

**Kitchen** and the **Menu** (SELECT switches between them).

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

**Day** ("Open")
- **Top screen:** the LCD (day, clock, popularity, customers expected / in the street, served, went to the rival, gave up, local share, pizzaiolos, ovens, tables and seats, capacity, the rival's price, takings, cash), the contest banner on contest days, the neighbourhood news and the manager's notes.
- **Bottom screen:** the street, with our pizzeria and the rival's. A opens the doors: customers walk down the street in their group's colour and go into one of the doors or walk past; a bubble shows each sale. x1/x2/x4 (or left/right) set the speed, Skip to closing (or A) ends the day.
- **Report:** sales, toppings, rent, wages and the result, customers served, lost to the rival, in the queue or for a seat, reputation before and after, the topping, least wanted topping and combo of the week; on the bottom screen what some customers said, the contest result and a tip. Bankrupt (debts over $500) starts a new game; the goal ($4000 and 3 stars) is announced once.
- The simulation is the browser game's `simulateDay()` and `finishDay()` (same averages over 400 days). For now the 3DS has one room (the browser game's starter room: 5 tables, 10 seats), no Pantry (toppings are bought on the day at +25%, as the browser game's manager does, with no manager fee) and no manager setting prices or hiring.

**Contest**
- Every 5 days. The top screen shows the next theme and its rules, the prizes, the entry fee, how many points the rivals score, and the last contests. The bottom screen lists the menu pizzas with the points they would score (or why they're disqualified); tap one, or A, to enter it (the fee is paid once; swapping is free).

**Shop**
- Extra oven, hire a pizzaiolo (or let one go), neighbourhood flyers, the supplier (1/2/3: more quality, dearer toppings), the weekly market study (tips listed below it) and restart the game (press twice).

Everything is saved to `save.txt`: the pizza on the bench, the menu, the combos found and the restaurant (day, cash, reputation, staff, rival, news, contests, tips). Pieces are stored in the same compact format as the browser game (`packPieces`, recipe links `#p=`).

## Files

- `game/main.lua`: screens, input and drawing. `game/pizza.lua`: the pizza rules (`analyze()` with the topping of the week and the supplier, `contestScore()`, portions, weights, `packPieces`) and `game/day.lua`: the restaurant (`simulateDay()`, `finishDay()`, `resolveContest()`, the shop, the market study), both ported by hand from `index.html`. **When those change in the browser game, change them here too.**
- `game/data.lua`: toppings, doughs, sauces, combos, customer groups, weights, the economy constants, the starter room's seats and atmosphere, the topping and combo of the week for 400 weeks, and the whole `I18N` table. **Generated** from `index.html` by `node tools/export_3ds.js`; never edit it by hand.
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
