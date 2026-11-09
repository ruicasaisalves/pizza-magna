# Roadmap

Where Pizza Magna is today and what is still missing to make it a full pizzeria tycoon game. The pizza bench comes first; the systems below are built on top of it.

## Today

| System | State |
|---|---|
| **Kitchen** | Complete: about 180 toppings, 95 combos, weights, zoom, recipe sharing and import. |
| **Menu** | Unlimited pizzas, cost-based suggested price, adjustable prices. |
| **Service day** | Top-down room (20×17 tiles), 4 customer groups choosing between you and the rival, weekday multiplier. |
| **Competition** | One fixed rival (Pizza Rápida) with fixed quality and price, and a 2-for-1 promo every 6 days. |
| **Shop** | Extra oven (up to 3), pizzaiolo (up to 5, $40/day), room renovation (levels 0–3, just a number), flyers (+45% customers for 1 day), 2 suppliers. |
| **Contest** | Every 5 days, 5 themes, prizes. |
| **Goal** | $4,000 and 3★. |

The public site only shows the Kitchen and the Menu (sandbox mode).

## Missing

### 1. City and property
The biggest block. A first visual draft of the map is in `docs/drafts/city.html` (standalone, not wired to the game): 6×5 square blocks, drag to move, zoom and a minimap.
- A pixel-art city map with neighbourhoods (university, tourist, residential, upmarket). Each has its own mix of the 4 customer groups.
- Shops to **rent** (monthly rent, cheap to start) or **buy** (expensive, gains value, can be sold).
- Each property has a size, a number of tables, street traffic, rent and condition (new or needing work).
- Run several pizzerias at once, each with its own room, staff and menu (or a shared menu).
- Bank: loans with interest, to afford the first purchase.

### 2. Room decoration
- **Done (first version):** Shop › Decorate the room is the room editor from the draft, in the game. Furniture is bought and placed on the tile grid, sold back for half. The room is saved (`state.room`; old saves rebuilt from the old 0–3 level).
- **Seats count:** customers come in a lunch and a dinner rush; each one holds a seat while eating, and with no seat free for a moment they leave ("no table"), which costs reputation. Tables a waiter can't reach don't count.
- **Atmosphere counts:** each piece's appeal per customer group, a style bonus when the room is mostly one style, and a penalty when it is crowded, shift the customer mix, their choice and their satisfaction.
- **Economy (first version):** a beginner with the starter room makes about $100 a day at a normal price (regulars, gentler rival promos); more tables, atmosphere, staff, a well-run pantry and better prices make more.
- Still to do: lighting, a counter you can move, a second room size per property, animated pieces in the editor.
- The furniture comes from the room atlas `assets/room.js` (made by `tools/gen_room.py`), like the rest of the room.
- Draft: `docs/drafts/room.html` (standalone): four styles, 8 table sets, 14 floor pieces, 9 wall pieces, 6 floors and 5 walls; atmosphere per customer group, seats, free floor and reachability checks.

### 3. Staff
- **Roles**: pizzaiolo, waiter, cashier, dishwasher/cleaner. Today there are only pizzaiolos, as a count.
- **Individual profiles**: name, skill, speed, salary and morale. Different candidates every day.
- Training, raises and firing.
- Effects in the simulation: a slow waiter makes customers wait and leave; a weak pizzaiolo lowers pizza quality.

### 4. Real competition
- **Several rivals** across the neighbourhoods (the names are already in `NPCS`), each with a strategy: cheap, gourmet, themed.
- Rivals that react to you: price cuts, copied pizzas, new shops nearby.
- A way to see their menus and prices.

### 5. Advertising
- Several channels, each with a cost, a duration and an audience:
  - posters in the neighbourhood;
  - newspaper;
  - radio;
  - social media (students react more);
  - tourist guides (tourists react more).
- Campaigns per neighbourhood. The effect fades gradually instead of stopping after one day.

### 6. Purchasing and stock
See also "Shopping by weight" in `docs/ideas.md`.
- Buy toppings by the kilo from suppliers with different prices and quality. Weights already exist (`GRAMS`, `portion()`).
- Each pizza sold uses its weight from the stock.
- Use-by dates and waste.
- A pizza is off the menu when one of its toppings runs out.

### 7. Economy and progression
- Monthly report: income, costs, profit per shop, charts.
- Reputation per shop and per customer group.
- Staged goals instead of a single $4,000 goal.
- Random events: health inspection, food critic, neighbourhood festival, oven breakdown, rain.
- Home delivery (already promised in the shop's "Coming soon").

### 8. Finishing
- Move the remaining screens (day, shop, contest, messages) into `I18N`; only the kitchen and sharing are migrated.
- Balance prices and customer preferences (still a first estimate).
- Logo generator (see `docs/ideas.md`).
- Save format for several shops, with defaults so old saves still open.

## Suggested order

1. **Staff profiles** and **placed furniture**: they deepen the one shop that exists, and the current simulation can take them without touching the rest.
2. **Advertising channels** and **multiple rivals**: fairly small, and they build on the 4 customer groups.
3. **Purchasing and stock**: the weights are already in place.
4. **City, property and bank**: the biggest change (several shops, new save format, new screen). Best done once a single shop is interesting on its own.
5. Events, reports and translating the remaining screens as each system lands.
