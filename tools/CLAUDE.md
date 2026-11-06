# Sprite generators

`gen_ingredients.py` to `gen_ingredients16.py` draw the toppings in Python (numpy + PIL); `gen_bases.py` draws the doughs and sauces. `build_atlas.py` packs them into `../assets/ingredients.js`. Older generators have comments in Portuguese; write new ones in English.

## After changing a generator
1. `python3 tools/gen_ingredientsN.py <scratchpad>/gN` makes the preview sheet (`preview_ingredientesN.png`). **Look at it** with Read.
2. `python3 tools/build_atlas.py` rebuilds the atlas.
3. `node tools/test_ingredients.js <ids> <scratchpad>`, and look at `bancada.png`.

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
- **Variants:** 3 per topping, with seeds 1, 2 and 3. Each function uses `np.random.default_rng(seed + base)` with its own base. Batch 16 reaches `+4900`; carry on from there.

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

## Atlas keys
- `<id>_0..2`: whole.
- `<id>_n`: whole piece that rotates.
- `<id>_g0..2`: chopped.
- `sauce_<id>`, `crust_<id>`: sauce and crust, 170 px.
- `marble`, `bowl`: the bench and the bowl.
