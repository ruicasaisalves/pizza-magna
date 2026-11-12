# Pizza Magna

A pizzeria management game in 90s pixel art, for browser and phone. Plain HTML and JS, no build and no dependencies: open `index.html` straight from disk.

## Files
- `index.html`: the whole game (about 1500 lines). **Don't read it whole.** Find the section by its marker with grep and read only that:
  - `= LANGUAGE =`: `LANG` and the `I18N` table (en/pt)
  - `= DATA =`: `DOUGHS`, `SAUCES`, `ING`, `PACKS`, `COMBOS`, `SEG` and `custU()` (what each customer group looks for: students a low price and home toppings `CASA`, families a good deal, gourmets quality, tourists a mix and unusual toppings `EXOTIC`; the price a customer finds fair, `fairPrice()`, comes mostly from appeal, and toppings add value only up to `VALUE_CAP` of cost, so a pizza piled with toppings and sold cheap doesn't take every customer), `THEMES` (contest themes by topping or flavour: classic, sweet, veggie, creative, cheese, spicy, sea, low-cost; names in `I18N` `th.*`) and the economy constants; `weekly()`: the topping, least wanted topping and combo of the week; `STUDY_COST`, `studyTips()`: the weekly market study in the Shop (tips in `state.tips`)
  - `= PIZZA ANALYSIS =`: `analyze()` (quality, cost, appeal) and `contestScore()`
  - `= DRAWING`: atlas, `spr()`, rotating pieces (`turned()`), `composePizza()` (pieces are drawn in the order they were placed)
  - `= UI: KITCHEN =` and `-- the pizza bench`: the bench (320 wide, with a title strip on top; zoom mode), the bowls, `addPiece()`, `rotatePiece()`, `GRAMS` and `portion()` (weights)
  - `= UI: DAY =`, `-- simulation` (regulars, about 45%, take their favourite pizza; the newcomers are `CURIOUS` 20% of the time and pick any pizza within `SLACK` of what they'd accept), `-- restaurant room`: the day, the customers and the tiled room (32 px tiles, art and piece layouts from `assets/room.js`); `RZ`: room zoom 1–3 (− / + buttons, two-finger pinch, ctrl+wheel) shared by the day and the room editor, the canvas scrolls inside `.rscroll`
  - `-- room design` (state.room: pieces, seats, atmosphere per customer group, `roomAnalyse()`), `= UI: ROOM EDITOR =` (Shop › Decorate the room)
  - `-- stock` (pantry by weight: `state.stock`, nothing spoils) and who runs the pizzeria, `state.tier`: 1 the manager runs everything (buys at +25%, sets prices, hires; `TIER_FEE`), 2 a buyer refills the pantry every morning for `restockDays`, 3 the player does everything; the supplier, `state.supplier` (`SUPPLIER`, `ingC()`): 1/2/3 adds quality to every pizza and makes toppings dearer, and no topping is ever locked; `managerMorning()`, `= UI: PANTRY =` (Shop › Pantry), `= DEMAND CURVE =` (the whole menu's profit by one pizza's price; shown in the Menu only with Options › Advanced analytics, `ADV`, `pm-adv` in `localStorage`; by default the Menu shows just quality, cost, margin and sold yesterday)
  - `= UI: HISTORY =`: the sales history page (Menu › Sales history, or from the end-of-day report): `state.hist` keeps the last `HIST_DAYS` (60) days, one record per day written by `finishDay()` (served, street, rival, profit, takings, reputation and the pizzas sold by name)
  - `= UI: SHOP =`, `= UI: CONTEST =`, `= MODALS =`, `= RECIPES: LINK, FILE, IMPORT =`, `= SHARE =`
  - `= RENDER + EVENTS =`: `render()` and the button actions (`ACT`), plus `TRACK` (analytics events)
- `music.js`: 8-bit / lo-fi Italian music, synthesised with Web Audio (no sound files). Each tune is text: one note per eighth, `-` holds, `.` is silence. Lead, bass and harmony must have the same number of steps per part. Tunes play in a fixed order ("Next song" in Options): every tune once, as listed in `SONGS`, then from the top (`ORDER`); songs marked `calm: true` (slow, quieter) are in the list like the others, not put in between. The public-domain classics come from ABC sheet music (abcnotation.com), converted with `tools/abc2music.py`. The on/off preference lives in `localStorage` (`pm-music`), apart from the save.
- `assets/ingredients.js`: the toppings atlas. **It is generated** by `tools/build_atlas.py`; never edit it by hand. See `tools/CLAUDE.md`.
- `assets/room.js`: the dining room atlas at 32 px tiles (furniture, decor, kitchen, people) with the layout of each piece. **Generated** by `tools/gen_room.py` (the people come from `tools/pilot_people.py`: 21 customers as `w<look>_<dir>_<0-2>` on foot, standing then two strides played 1, 0, 2, 0, and `p<look>_<dir>` seated, plus `waiter` and `cook`); never edit it by hand. Used by the game's room (loaded only when the room is first shown, `roomArt()`) and by `docs/drafts/room.html`.
- `assets/icon-*.png` and `manifest.webmanifest`: the game's icon (a pizza slice) for the browser tab, the header button, the phone home screen and a future app. **Generated** by `tools/gen_icon.py`: 32 px drawn pixel by pixel; 180/192/512 cut from a real game pizza.
- `sw.js`: service worker (network first, keeps the last copy for offline play); registered only over http(s). Installing the game: `= INSTALL =` in `index.html` (Options section, and a one-time invitation on phones after the first pizza saved; `pm-install-asked` in `localStorage`).
- `3ds/`: a Nintendo 3DS homebrew port with LÖVE Potion (Lua), a prototype with the Kitchen and the Menu; `3ds/README.md` explains it. `3ds/game/data.lua` is **generated** from `index.html` by `node tools/export_3ds.js`, and `3ds/game/atlas.lua` plus `3ds/game/gfx/` by `python3 tools/export_3ds.py`. Run both after changing toppings, combos or `I18N`. `3ds/game/pizza.lua` ports `analyze()` by hand, so change it too when `analyze()` changes.
- `old/`: earlier models kept in case we go back (the first 16 px room: `old/sprites.js` and `old/room-16px.js`; the first people of the 32 px room: `old/room-first-people.js` and `old/first-people.png`; `old/README.md` says how to go back). Not loaded by the game.
- `itch/`: the kit for the game's itch.io page: cover, banner, background tile, logo and screenshots (generated by `node itch/make_media.js` from the game itself) and `PAGE.md` (colours, tags, description, how to make the upload zip).
- `docs/ingredients.md`: the topping list (✓★ = in the game) and how things are cut.
- `docs/art-packs.md`: art packs considered and the style decision.
- `docs/ideas.md`: ideas on hold.
- `docs/roadmap.md`: what is still missing to make a full tycoon game, and in which order.

## Rules
- **Language of the game:** English by default and Portuguese when the browser is in `pt`; in Options the player can fix English or Português (`pm-lang` in `localStorage`). All visible text comes from `I18N`, with the same key in `en` and `pt`. Everything is migrated (only proper names, like the rival pizzerias and Portuguese dish names, stay as they are); new text must go through `t()`. The news (`state.news`) are saved as text; `newsText()` rewrites them in the current language when shown, so a news line needs a key in `NEWS_KEYS`. Inside `simulateDay()` a local `t` (time) hides `t()`: use its alias `tx()` there.
- **Language of the repo:** documentation (`.md`), commit messages and new code comments in English, so the repo can be shared with English-speaking colleagues. Only game text in `I18N` (and Portuguese names like francesinha or alheira) stays in Portuguese. Reply to the user in the language they write in (they usually write Portuguese, pt-PT).
- **Version:** `VERSION` in `index.html` (near `SAVE_KEY`) is shown at the bottom of Options and written into the save (`state.version`) so bug reports say which build. Every PR that gets merged bumps it one step in that PR: `0.01a`, `0.01b` … `0.01g`, then `0.02a` … `0.02g`, `0.03a` and so on.
- **Saves:** state goes to `localStorage` (`massa-mestra-v1`); pieces are stored compactly (`packPieces`, 5 bytes per piece), the same format as recipe links (`#p=`) and `.pizza` files. No limit on pizzas in the menu; up to 300 pieces per pizza. New fields need a default value, so old saves still open.
- **Analytics:** GoatCounter (`pizzamagna.goatcounter.com`). Buttons worth counting are in `TRACK` and arrive as `ev/<name>` events; a new button worth counting goes there. Never send names or recipes.
- **Fonts:** all are local, in `assets/fonts/` (latin and latin-ext woff2 files from Google Fonts, SIL Open Font License), so the game looks the same offline; no Google Fonts link. Body text is Pixelify Sans (the original font; the player tried VT323, Jersey 10 and Tiny5 and prefers it), but its digits muddle at small sizes (5 looks like S or 8, 2 like Z), so the digits 0-9 come from VT323: `'PM Digits'` (`assets/digits.woff2`, the ten digits only, `unicode-range`) goes first in `--f-body` and in canvas fonts. Titles and buttons Silkscreen; the green LCDs and the Menu figures VT323. Write ordinals as words (segunda, primeiro lugar).
- Don't add dependencies or build steps.
- Keep diffs surgical: every changed line should trace back to the request. Remove only what your own change made unused; flag other dead code, don't delete it unasked.
- Before saying a change works, verify it: `node tools/test_ingredients.js` for toppings, Playwright on `index.html#sandbox` (or the full game) for screens.

## Testing
- The public site (`pizzamagna.xyz`, GitHub Pages from `main`) runs the full game. It used to show only the bench, saved under the bench key; `load()` adopts that save for players who have no full-game save.
- Test mode: `index.html#sandbox` (or `window.PM_SANDBOX=true`) opens only the Kitchen and the Menu, with a separate save.
- `pizzamagna.xyz/dev` still works (`dev/index.html` fetches `../index.html` and adds `<base href="../">`) and is now the same as the site. There is only one copy of the game: never copy `index.html` into `dev/`.
- `node tools/test_ingredients.js [id1,id2] <folder>`: checks sprites, translations, combos and weights, and places pieces on the bench.
- For other screens, use Playwright: `require('playwright')` works without installing anything.

## Tasks with their own procedure
- New toppings or fixing a sprite: use the `novo-lote` skill.
- Changing the sprite generators: read `tools/CLAUDE.md`.
