# Waiters 02–04 — dev integration handoff

The three sheets follow the same cell layout, feet baseline and delivery timing as waiter-01 from PR #76. Each is a transparent 192 × 464 PNG, with 48 cells of 32 × 58. The paths are ../waiter-02/waiter-02.png (blonde hair), ../waiter-03/waiter-03.png (short side part) and ../waiter-04/waiter-04.png (rounded curls). turnaround.png shows a contact pose from the front, side and rear, then the empty-handed delivery smile from the side and front. service.gif shows all three at native size and 2×.

For Claude: reuse the existing dev-only renderer and its fallback while the image decodes. Select the sheet for the relevant waiter; when reviewing all four in one shop, assign sheets 01–04 to scene slots 0–3. Use a separate image/decode state per sheet. Preserve the pilot's hand-off direction, depth ordering and 0.3-second pause. Each sheet already contains the tray and vertical movement.

Rows are down, right, up and left, with empty hands first and carrying second for each direction. Column 0 is idle A, 1–4 are the walk with expression A, and 5 is delivery B. The live hand-off uses the empty row once the pizza is on the table. The rear view has no facial expression. These assets are staged for review; the main game and dev loader are untouched on this branch.
