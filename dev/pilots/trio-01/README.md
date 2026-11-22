# Trio 01: two customers and a waiter, /dev pilot

AI-made sheets, shrunk for the game, brought in for evaluation under `window.PM_DEV` only (pizzamagna.xyz/dev or `#dev`).

## Sheets

- `red-walk.png`, `green-walk.png` (the red-haired woman, the man in green): 160 × 232, cells 32 × 58. Rows down, right, up, left; columns standing and four walking steps. Feet on y 56, as in the room atlas.
- `red-seated.png`, `green-seated.png`: 32 × 192, cells 32 × 48, one column, the same four rows. Hips at the atlas height; feet on y 46, one pixel lower than the atlas's 45.
- `waiter.png`: 192 × 464, cells 32 × 58. Rows in pairs, empty-handed then carrying, for down, right, up and left; columns standing, four walking steps and the smile after the delivery. The pizza is part of the carrying frames.

## How the game uses them (index.html, `devSheet()`, `PILOT_*`)

- Customers whose look has `rlook % 4` = 0 are the red-haired woman and 1 the man in green (about half of them), so they mix with the atlas looks.
  - Walking: column `1 + floor(ph) % 4`, standing 0; drawn at `(round(x), round(y) + T − 58)`.
  - Seated: at the atlas layout's place, 1 px higher. From behind (up) only rows 0–36 are drawn, like the atlas, so the chair's back hides the legs.
- The waiter is the room's first waiter (`PILOT_WAITERS[0]`); `waiter-01` moved to the second. It gets the same hand-off as `waiter-01`: 0.3 s facing the customer with the smile, empty-handed.
- A sheet is used once it has decoded; until then, and for every other look, the atlas.

## Corrections

In a few side-view strides the head jumped 3 to 4 px backwards and back, which made the walk shake. Those frames are drawn moved (`PILOT_DX`); the PNGs are unchanged:

- red, left: columns 1 and 3, −3;
- waiter, right empty: +3 and +1;
- waiter, right carrying: column 3, −2;
- waiter, left empty: −3 and −1;
- waiter, left carrying: +1 and +1.

The green walk and the front and back views stay within 1 px.

## Still to look at

- The waiter carrying, seen from the side, leans back: his head is about 4 px behind the empty-handed pose. The hand-off switches to the empty row, so his head moves when he puts the pizza down.
