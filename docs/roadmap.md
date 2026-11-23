# Roadmap

Where Pizza Magna is today and what is still missing to make it a full pizzeria tycoon game. The pizza bench comes first; the systems below are built on top of it.

## Today

| System | State |
|---|---|
| **Kitchen** | Complete: 104 toppings, 7 doughs, 9 sauces, 110 combos, weights, zoom, recipe sharing and import. |
| **Menu** | Unlimited pizzas, cost-based suggested price, adjustable prices; demand curve and "who picks it" with Options › Advanced analytics; sales history. |
| **Service day** | Top-down room (20×17 tiles), 4 customer groups choosing between you and the rival, weekday multiplier; the cast-01 characters (21 customers, 4 waiters, 5 cooks), plus guests and VIPs who visit from 3, 4 and 5 stars (looks only). |
| **Competition** | A rival in each neighbourhood with its own strategy (cheap, tourist, family, gourmet; Pizza Rápida next to the first shop is classic). |
| **Shop** | Extra oven (up to 3), the team (pizzaiolos and waiters with names, skills and wages, new candidates every day), the room editor, flyers (+45% customers for 1 day), supplier quality 1/2/3; who runs the pizzeria (manager, buyer or you), the pantry, the weekly market study, the bank; no topping is locked. |
| **Contest** | Every 5 days, 5 themes, prizes. |
| **City** | Porto Magno: four neighbourhoods; rent or buy more shops, each with its own menu, room, team and rival. |
| **Goal** | Off for now (`GOAL_ON=false`); was $4,000 and 3★. |

The public site runs the full game (it showed only the Kitchen and the Menu until the restaurant went live).

## Missing

### 1. City and property
- **Done (first version):** the City tab shows Porto Magno (`city.js`, also used by `docs/drafts/city.html`). With $4000 of your own money you can rent a lot (rent per day) or buy one; the new shop opens empty, with its neighbourhood's customers, its street's traffic and the nearest rival. Each shop has its own menu (the other shops' pizzas are offered as a recipe book), room, staff, pantry, reputation and history; the header arrows switch shops; one day runs every shop (the others in the background with their manager) and the report shows each one and the total. A bank lends up to $20,000 at 0.5% a day.
- Your shops are painted as open pizzerias; a rented shop can be closed, a bought one sold for 70%.
- Still to do: the number of tables of a lot. (Rivals have a strategy per neighbourhood; the 3DS has the City since 0.04f.)
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
- **Done (first version):** pizzaiolos and waiters are people with a name, two skills from 1 to 5 (pizzaiolos: speed and cooking; waiters: speed and charm) and their own wage; new candidates every day in the Shop's Team card; speed sets how many pizzas the kitchen makes and how many customers the waiters serve, cooking and charm make customers happier. Waiters are paid now (they used to be free, one more than the pizzaiolos).
- Still to do: cashier and dishwasher, morale, training and raises. (The 3DS has the staff since 0.04f, without the manager hiring.)
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
- ~~Move the remaining screens into `I18N`~~: done, every screen is translated (English and Portuguese).
- Balance prices and customer preferences (still a first estimate).
- Logo generator (see `docs/ideas.md`).
- ~~Save format for several shops, with defaults so old saves still open~~: done with the City (`SHOP_KEYS`, `ensureShops()`).

## Suggested order

1. **Staff profiles** and **placed furniture**: they deepen the one shop that exists, and the current simulation can take them without touching the rest.
2. **Advertising channels** and **multiple rivals**: fairly small, and they build on the 4 customer groups.
3. **Purchasing and stock**: the weights are already in place.
4. **City, property and bank**: the biggest change (several shops, new save format, new screen). Best done once a single shop is interesting on its own.
5. Events, reports and translating the remaining screens as each system lands.
