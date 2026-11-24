# Integration notes (index.html)

How the game uses this pack, and what was adjusted. It was the /dev pilot `dev/pilots/cast-01` until 0.04k, when it became the default for everyone. `README.md` is the pack's own contract.

- **Looks:** folder NN is look NN − 1. Customers are matched by `rlook`; waiters and cooks by `staffV(p,1)`: a woman's name (`STAFF_WOMEN`) picks among the women's folders, any other name among the men's (`CAST_STAFF`), from the person's `v` (`castCustomer()`, `castWaiter()`, `castCook()`).
- **Loading:** `devSheet()` loads each sheet when first needed; the atlas is drawn until it has decoded.
- **Feet:** on the walking, service and idle sheets the feet end on row 55 with no shadow. The atlas's end on row 54, with a soft 2-row shadow under them. These sheets are drawn 1 px higher with the same shadow (`drawPilotFoot()`, `pilotShadow()`).
- **Seated:** the seated sheets end on row 45, as the atlas's do, so they are drawn exactly at the atlas layout's place. Seen from behind (up) only rows 0–36 are drawn, like the atlas, so the chair's back hides the legs.
- **Head nudges:** in a few side-view strides the head jumps 2–4 px backwards and back. Those frames are drawn moved (`PILOT_DX`); the PNGs are unchanged.
  - customers 01, 08, 12, 14, 17, 20 and 21;
  - waiters 01 and 04.
- **Waiters:** the pizza is in the carrying frames (no overlay, no bob). At the table the waiter faces the customer with the empty row's column 5 for 0.3 s (`PILOT_HANDOFF`).
- **Open point:** seen from the side, a waiter carrying leans back 2.5–4.5 px compared with the empty-handed rows, so his head moves at the hand-off.
- **Replaced:** this pack replaces the earlier pilots in the game's code (trio-01, waiter-01, cooks-01-05). Their folders stay in `dev/pilots/` for reference.

- **Staff expansion (0.04o):** four waitresses (05 rose bob, 06 copper curls, 07 straight black hair, 08 gothic) and six cooks (06 rose braid, 07 copper waves, 08 straight black hair, all women; 09 grey moustache, 10 dark curls, 11 blue mohawk, men). Same cells and foot line (row 55); their heads don't jump in the side strides and don't lean when carrying, so they need no nudges. Women: waiters 02, 05–08 and cooks 02, 05–08; men: waiters 01, 03, 04 and cooks 01, 03, 04, 09–11.

- **v2 of the pack:** only the five cooks changed. Their faces were 16 px wide against the waiters' and customers' 21–22 px; the new ones have 20–22 px heads, the same shoulders and the same foot line (row 55).

## Going back to the classic characters

- **For one player:** Options › Characters › Classic. The choice is stored in the browser (`pm-cast`).
- **For everyone:** set `CAST_ON=false` in `index.html`. The classic people are the room atlas's (`assets/room.js`), which is still loaded, so nothing else has to change.
- **The whole game as it was:** main before this change is commit `40807a3`.
