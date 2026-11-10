# Sprite generators

`gen_ingredients.py` to `gen_ingredients20.py` draw the toppings in Python (numpy + PIL); `gen_bases.py` draws the doughs and sauces. `build_atlas.py` packs them into `../assets/ingredients.js`.

`gen_room.py` draws the dining room with the same method at 32 px per tile (floors, walls, chairs, tables, decor, wall pieces, kitchen, street, customers seated (`p<look>_<dir>`) and on foot (`w<look>_<dir>_<step>`, 32×58 like the waiter), waiter and cook) and writes `../assets/room.js`: the frames plus the layout of each piece (parts, chairs, sitters and table top, in px from its top-left tile). Run `python3 tools/gen_room.py <scratchpad>` and look at `room_atlas.png`; `docs/drafts/room.html` uses it. Every view of a seated person puts the hips at y = 33, so a person is drawn 18 px above its chair (24 px for a chair seen from behind). Code comments and docs are in English.

`pilot_people.py` draws the people (21 customers, the waiter and the cook): cel shading with no dithering, front / side / back with a walk, and seated poses. `gen_room.py` imports it for the atlas (`walk()`, `seated()`, `staff()`); the first people (`person()`, `walker()`, `standing()` in `gen_room.py`) are kept only for its comparison sheets. Run on its own (`python3 tools/pilot_people.py <folder>`) it writes previews: `pilot_people.png`, `pilot_seated.png`, `pilot_walk.gif`. A new customer is a new entry in its `LOOKS` (keep 21, or change the `21` in the game's `rlook` and in `layout_json`).

`gen_icon.py` makes the game's icon (`../assets/icon-32.png`, `icon-180/192/512.png`): run `python3 tools/gen_icon.py <scratchpad>` and look at `icons.png`.

## After changing a generator
1. `python3 tools/gen_ingredientsN.py <scratchpad>/gN` makes the preview sheet (`preview_ingredientesN.png`). **Look at it** with Read.
2. `python3 tools/build_atlas.py` rebuilds the atlas.
3. `node tools/test_ingredients.js <ids> <scratchpad>`, and look at `bench.png`.

The `preview/` folder is in `.gitignore`; previews go to the scratchpad.

## Drawing method
- **Scale:** 320×200 logical screen and a 170 px pizza. Pieces are 15 to 30 px, long ones up to 42 px.
- **Light:** volume is a height field; `shade()` gives the light, always from the top left.
- **Colour:** each material has a short ramp in `R`, 4 or 5 tones, dark to light.
- **`render(mat, light, mask, map)`:** applies the 4×4 ordered dithering and the selective outline. The outline uses the material's own dark tone, never black. The `map` says which ramp outlines each material.
- **Helpers:**
  - `grid` and `axes(W, H, ang)` give coordinates along (u) and across (v) the piece;
  - `erode` makes layers from the edge;
  - `noise` gives texture;
  - `drop` makes the 2 px shadow, applied by `build_atlas.py`.
- **Variants:** 3 per topping, with seeds 1, 2 and 3. Each function uses `np.random.default_rng(seed + base)` with its own base. Batch 20 reaches `+6500`; carry on from there.

## Rotation (`ING.rot` in the game)
It is always the **same image** turned in quarter turns by the game, without losing pixels; the shadow is computed afterwards.
- **1:** round or without a front. Doesn't rotate and has 3 variants.
- **2:** symmetric, like bacon (lying or standing).
- **4:** has a front (tail, stem, tip).

The function takes `ang`. With `ang=0` the piece lies down with its front to the right, and the canvas swaps W/H when `|sin(ang)| > .5`. In the atlas it goes into `ROTATE` as `<id>_n`, without shadow.

## Chopped (`grated()` in `gen_ingredients2.py`)
- Herbs, vegetables and cheeses → `flake`; cheeses that get grated → `shred`.
- Meats and sausages → `cube`.
- Fish and seafood → `chunk`.
- Nuts → `dice`.
- Things already small, or only drizzled → none.
- To mix colours, pass a function `f(seed)` (see `gorgonzola_crumbs`).
- Grated cheeses use a big loose handful: in `build_atlas.py`, `('ramp', 'shred', 130, BIG)` with `BIG = {'W': 60, 'H': 56}`. In the game they are listed in `BIG_SHRED` (one handful = 1.5 portions).
- Grated mozzarella uses the same strands with a near-white ramp and 250 bits (`gen_ingredients18.py`), with no drop shadow (`NO_DROP` in `build_atlas.py`), so handfuls side by side make an even surface to draw on.

## Atlas keys
- `<id>_0..2`: whole.
- `<id>_n`: whole piece that rotates.
- `<id>_g0..2`: chopped.
- `sauce_<id>`, `crust_<id>`: sauce and crust, 170 px.
- `marble`, `bowl`: the bench and the bowl.
