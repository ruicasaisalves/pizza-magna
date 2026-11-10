# Ideas for the future

Ideas on hold, with no plan or date yet.

## Logo generator for the pizzeria
- After the player types the chef's and the pizzeria's names, generate a pixel-art logo.
- Parts to combine: badge shape (circle, shield, ribbon, sign), colours, an icon (pizza, oven, chef's hat, basil leaf) and the pizzeria's name in pixel lettering.
- An "Another one" button to generate variations; the chosen one is saved with the chef.
- Uses: at the top of the game instead of the current logo, and on the shared card, next to the "Made by …" signature.

## Shopping by weight
- Every topping already has a weight (`GRAMS` in `index.html`); grated pieces weigh less (`portion()`).
- Later: buy stock by the kilo, and each pizza sold uses its weight from the stock.

## Several suppliers
- Done in part: one supplier at a time, chosen in the Shop as a quality level (`SUPPLIER`). Still an idea: Later: several suppliers (the market, a wholesaler, a delicatessen, a farm) with different prices, quality and delivery days.
- Gives the player more to do in tier 3 (you run everything): find the cheapest or the best place for each topping and plan the pantry around deliveries.
- Quality from a better supplier could raise the pizza's quality a little; a cheap one could lower it.

## Better people (pilot on hold)
- `tools/pilot_people.py` is a pilot for redrawn people, kept for later: clean cel shading with no dithering, round shoulders, clothes with their own details. 13 customers (hoodie, cap and backpack, the old couple with cane and handbag, a punk, a tourist with a straw hat, a gourmet in a black dress, a Japanese tourist with a bucket hat and camera, a Chinese couple in a silk jacket and a qipao...), each from the front, the side and the back with a four-step walk, and seated facing down, up, right and left (32 x 48, like today's); plus the waiter and the cook. It only makes preview images (`python3 tools/pilot_people.py <folder>` → `pilot_people.png`, `pilot_seated.png`, `pilot_walk.gif`); the game still uses the people from `gen_room.py`. To put it in the game: have `gen_room.py` build `p<i>_<dir>`, `w<i>_<dir>_<step>`, `waiter` and `cook` from it (the game picks one of 21 looks and uses 2 walk steps today).
- Still missing before it could replace them: the back view, seated people, the waiter and the cook, and all 21 looks.

## Promotions (on hold)
- The rival's 2-for-1 comes every 6 days; the player has no promotions yet, only flyers.
- Ideas: a "Promotion" in the Shop for the next day (pick a pizza, 2 for 1: more customers and reputation, twice the cost and capacity; worse if repeated); answering the rival's 2-for-1 on the same day; group promotions (a student menu, a pizza of the day for families, a free tasting at contests for gourmets); showing when the rival's next 2-for-1 comes.
