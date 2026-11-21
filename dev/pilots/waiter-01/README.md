# Waiter 01 — isolated /dev art pilot

Only the first waiter look is in scope. The PNG is a complete standalone sheet. No live renderer loads it. Open service.gif for the visual rehearsal.

## Sheet contract

waiter-01.png is an RGBA 192 × 464 image. Each cell is 32 × 58. Columns are idle A, walk A (four successive frames), and hand-off B. Each pair of rows is empty first and carrying second. Pairs are ordered down, right, up, left. The back view deliberately hides facial expressions. The serving tray is part of the carrying frames.

In canvas, use source coordinates (column × 32, row × 58, 32, 58). Draw at (round(w.x), round(w.y) + T − 58), with nearest-neighbour sampling. The walk already contains vertical motion. Keep the existing foot-depth sort.

## Handoff for Claude

1. For the first test load the pilot only under the existing /dev loader (window.PM_DEV), when the sheet has decoded. Target the first waiter look (w.v modulo the number of waiter looks equals 0). For a repeatable visual test force that look on the first waiter of a temporary dev scene. Leave other employees on the current atlas.
2. During movement use column 1 + (floor(w.ph) % 4), otherwise column 0. Take direction from w.dir, and choose the carrying row from w.carry. Skip the game's separate pizza overlay and staff bob for this pilot.
3. Trigger B once, when the go phase actually reaches the table in the waiter update. Snapshot a facing direction toward the customer from the waiter tile and seat, before the return path overwrites it. Show the final column for about 0.3 seconds of scene time. Switch to the empty row once the pizza is on the table. Keep the face and feet steady during the brief hand-off, then return to A. Keep simulation results, billing, saves and service speed independent of the visual test.
4. Check a route around chairs at normal and fast day speeds. Watch front and both profiles at hand-off, the back-view tray occlusion, feet on turns, and that the pizza appears exactly once. Compare native size and phone scale before extending the design to the remaining people.
