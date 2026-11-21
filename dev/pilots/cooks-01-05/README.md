# Five cook sheets for the dev kitchen

Use cook-01 through cook-05 in the order of COOKS in tools/pilot_people.py: short dark hair and tall toque, tied chestnut hair, moustache, full beard, copper bob. Each PNG lives in its matching sibling folder. The full cast is visible in turnaround.png. service.gif shows the walking and working poses; kitchen.gif stages the figures at COOK_POS with the room atlas and counter depth.

## Frame contract

Each sheet is a transparent 624 × 232 PNG. Rows 0–3 face down, right, up and left. The thirteen columns in each row are:

| Columns | Action |
| --- | --- |
| 0 | Standing |
| 1–4 | Four walking steps |
| 5–8 | Gather, lower, press and release the dough |
| 9–12 | Grip, advance, extend and withdraw the loaded peel |

Cells are **48 × 58**. The central 32 px contain the character; the additional 8 px on each side give the peel space to move. Draw at round(x) − 8, round(y) + T − 58, with z = y + T and image smoothing off. Working frames contain their own hand props. The character's foot anchor is the same as in the room atlas.

## Handoff for Claude

Stage the sheets in the dev-only cook drawing path. Decode one image per look and keep the existing atlas fallback until ready. The game currently stations cooks at COOK_POS. Use idle and work frames there, with phase offsets per cook so the shifts of weight do not line up; use walking frames only when a cook actually travels. Orient a peel toward the oven, and dough toward a preparation surface. The GIFs are visual rehearsals rather than a running integration. Check tool clearance and pose timing in the phone room before release. The art needs no changes to staffing capacity, saves, purchases, ovens or the 3DS.
