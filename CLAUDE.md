# Pizza Magna

A pizzeria management game in 90s pixel art, for browser and phone. Plain HTML and JS, no build and no dependencies: open `index.html` straight from disk.

## Files
- `index.html`: the whole game (about 1500 lines). **Don't read it whole.** Find the section by its marker with grep and read only that:
  - `= LANGUAGE =`: `LANG` and the `I18N` table (en/pt)
  - `= DATA =`: `DOUGHS`, `SAUCES`, `ING`, `PACKS`, `COMBOS`, `SEG`, `THEMES` and the economy constants
  - `= PIZZA ANALYSIS =`: `analyze()` (quality, cost, appeal) and `contestScore()`
  - `= DRAWING`: atlas, `spr()`, rotating pieces (`turned()`), `composePizza()` (pieces are drawn in the order they were placed)
  - `= UI: KITCHEN =` and `-- the pizza bench`: the bench (320 wide, with a title strip on top; zoom mode), the bowls, `addPiece()`, `rotatePiece()`, `GRAMS` and `portion()` (weights)
  - `= UI: DAY =`, `-- simulation`, `-- restaurant room`: the day, the customers and the tiled room (32 px tiles, art and piece layouts from `assets/room.js`)
  - `-- room design` (state.room: pieces, seats, atmosphere per customer group, `roomAnalyse()`), `= UI: ROOM EDITOR =` (Shop › Decorate the room)
  - `-- stock` (pantry by weight: `state.stock`, nothing spoils) and who runs the pizzeria, `state.tier`: 1 the manager runs everything (buys at +25%, sets prices, hires; `TIER_FEE`), 2 a buyer refills the pantry every morning for `restockDays`, 3 the player does everything; `managerMorning()`, `= UI: PANTRY =` (Shop › Pantry), `= DEMAND CURVE =` (profit by price in the Menu)
  - `= UI: SHOP =`, `= UI: CONTEST =`, `= MODALS =`, `= RECIPES: LINK, FILE, IMPORT =`, `= SHARE =`
  - `= RENDER + EVENTS =`: `render()` and the button actions (`ACT`), plus `TRACK` (analytics events)
- `music.js`: 8-bit / lo-fi Italian music, synthesised with Web Audio (no sound files). Each tune is text: one note per eighth, `-` holds, `.` is silence. Lead, bass and harmony must have the same number of steps per part. Tunes play in a fixed order ("Next song" in Options). The public-domain classics come from ABC sheet music (abcnotation.com), converted with `tools/abc2music.py`. The on/off preference lives in `localStorage` (`pm-music`), apart from the save.
- `assets/ingredients.js`: the toppings atlas. **It is generated** by `tools/build_atlas.py`; never edit it by hand. See `tools/CLAUDE.md`.
- `assets/room.js`: the dining room atlas at 32 px tiles (furniture, decor, kitchen, people) with the layout of each piece. **Generated** by `tools/gen_room.py`; never edit it by hand. Used by the game's room (loaded only when the room is first shown, `roomArt()`) and by `docs/drafts/room.html`.
- `assets/icon-*.png` and `manifest.webmanifest`: the game's icon (a pizza slice) for the browser tab, the header button, the phone home screen and a future app. **Generated** by `tools/gen_icon.py`: 32 px drawn pixel by pixel; 180/192/512 cut from a real game pizza.
- `sw.js`: service worker (network first, keeps the last copy for offline play); registered only over http(s). Installing the game: `= INSTALL =` in `index.html` (Options section, and a one-time invitation on phones after the first pizza saved; `pm-install-asked` in `localStorage`).
- `old/`: earlier models kept in case we go back (the first 16 px room: `old/sprites.js` and `old/room-16px.js`). Not loaded by the game.
- `docs/ingredients.md`: the topping list (✓★ = in the game) and how things are cut.
- `docs/art-packs.md`: art packs considered and the style decision.
- `docs/ideas.md`: ideas on hold.
- `docs/roadmap.md`: what is still missing to make a full tycoon game, and in which order.

## Rules
- **Language of the game:** English by default and Portuguese when the browser is in `pt`; in Options the player can fix English or Português (`pm-lang` in `localStorage`). All visible text comes from `I18N`, with the same key in `en` and `pt`. Migrated so far: the kitchen, sharing, options and the names of toppings, doughs, sauces, combos and customer groups; the rest is still written in Portuguese in the code, and whatever you touch gets migrated.
- **Language of the repo:** documentation (`.md`), commit messages and new code comments in English, so the repo can be shared with English-speaking colleagues. Only game text in `I18N` (and Portuguese names like francesinha or alheira) stays in Portuguese. Reply to the user in the language they write in (they usually write Portuguese, pt-PT).
- **Saves:** state goes to `localStorage` (`massa-mestra-v1`); pieces are stored compactly (`packPieces`, 5 bytes per piece), the same format as recipe links (`#p=`) and `.pizza` files. No limit on pizzas in the menu; up to 300 pieces per pizza. New fields need a default value, so old saves still open.
- **Analytics:** GoatCounter (`pizzamagna.goatcounter.com`). Buttons worth counting are in `TRACK` and arrive as `ev/<name>` events; a new button worth counting goes there. Never send names or recipes.
- **Fonts:** body text is Jersey 10 (clear digits at small sizes); titles and buttons Silkscreen; live numbers VT323. Don't use Pixelify Sans: its digits muddle at small sizes (2/8, 5/S). Jersey 10 has no ª/º ordinals: write the word (segunda, primeiro lugar).
- Don't add dependencies or build steps.

## Testing
- Test mode: `index.html#sandbox` (or `window.PM_SANDBOX=true`) opens only the Kitchen and the Menu, everything unlocked and with a separate save. On the public site (`pizzamagna.xyz` and `*.github.io`, GitHub Pages from `main`) the game always opens in this mode: only the bench is live.
- Full game online: `pizzamagna.xyz/dev`. `dev/index.html` fetches `../index.html`, adds `<base href="../">` and sets `window.PM_DEV=true`, which turns off the forced bench mode. There is only one copy of the game: never copy `index.html` into `dev/`.
- `node tools/test_ingredients.js [id1,id2] <folder>`: checks sprites, translations, combos and weights, and places pieces on the bench.
- For other screens, use Playwright: `require('playwright')` works without installing anything.

## Tasks with their own procedure
- New toppings or fixing a sprite: use the `novo-lote` skill.
- Changing the sprite generators: read `tools/CLAUDE.md`.
