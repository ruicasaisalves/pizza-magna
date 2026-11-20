# Staff: how it works, and how to simulate it

A brief for anyone, person or AI, who wants to check or rebalance the staff system (pizzaiolos and waiters with their own skills). Everything here is on the branch `claude/eager-goodall-s1savj` of `ruicasaisalves/pizza-magna`; it isn't merged into `main` yet.

- Branch: https://github.com/ruicasaisalves/pizza-magna/tree/claude/eager-goodall-s1savj
- The game (one file): https://github.com/ruicasaisalves/pizza-magna/blob/claude/eager-goodall-s1savj/index.html
- Raw, for tools that read plain text: https://raw.githubusercontent.com/ruicasaisalves/pizza-magna/claude/eager-goodall-s1savj/index.html
- The simulation script: [`tools/sim_staff.js`](../tools/sim_staff.js)

`index.html` has about 2,700 lines. Don't read it all: search for the names below.

## The rules

**People.** `state.staff` holds the open shop's team. Each person is `{id, n: name, r: 'cook' | 'waiter', sp: speed 1-5, sk: second skill 1-5, w: wage a day, v: look}`. The second skill is **cooking** for a pizzaiolo and **charm** for a waiter. The game shows both skills as `3/5`.

| Name in `index.html` | Value | What it does |
|---|---|---|
| `COOK_CAP` | 30 | Pizzas a day from a pizzaiolo at speed 3 |
| `OVEN_CAP` | 36 | Pizzas a day per oven (the kitchen can't make more than its ovens) |
| `WAITER_CAP` | 40 | Customers a day served by a waiter at speed 3 |
| `spMul(sp)` | 0.7 + 0.15 × (sp − 1) | Speed multiplier: 0.70, 0.85, 1.00, 1.15, 1.30 |
| `SALARY` | $30 | Base wage of a pizzaiolo |
| `WAITER_SALARY` | $24 | Base wage of a waiter |
| `wageOf(r, sp, sk)` | base + 3 × (sp − 3) + 2 × (sk − 3) | Wage a day; a candidate gets ±$1 on top |
| `HIRE_COST` | $100 | Paid once to hire |
| `MAX_STAFF` | 5 cooks, 4 waiters | Team limits (at least one of each always stays) |

**Capacity.**
- Kitchen: `capacity()` = min(ovens × `OVEN_CAP`, Σ over cooks of `COOK_CAP` × `spMul(sp)`).
- Room: `serviceCap()` = Σ over waiters of `WAITER_CAP` × `spMul(sp)`.
- `simulateDay()` serves at most min(kitchen, room). A customer who wants to eat past that limit leaves (`full`, "I waited ages and gave up") and reputation drops by 0.012.
- The room's seats are a separate limit: a customer who finds no free seat leaves too (`noseat`).

**Satisfaction.**
- Each served customer's satisfaction is `ap + noise×5 − max(0, over)×7 + (atm − 35)/7 + crewSat`.
- `crewSat` = 1.5 × (average cooking − 3) + 1.5 × (average charm − 3), so from −6 to +6.
- A customer is happy at `happyAt()` = 55 + 5 × stars. A happy customer adds 0.008 to reputation, an unhappy one takes away 0.03.

**Hiring.**
- `candidates()` brings 3 new pizzaiolos and 3 new waiters each day, shared by all shops (`state.cands`, `state.candDay`).
- Each skill is drawn as 1 + ⌊(rand + rand) × 2.5⌋, so 1 to 5 and mostly 2 to 4.
- In the Shop's Team card the player hires (`hirePerson()`) and lets people go.
- With the manager in charge (`state.tier === 1`), `managerMorning()` hires the fastest candidate (the cheaper one on a tie) while the kitchen or the room is below what it expects to need.

**Money.** Wages, rent and the manager or buyer fee come out in `shopDay()` (`sal = wages()`). A new game starts with 1 pizzaiolo 3/3 ($30) and 1 waiter 3/3 ($24).

**Old saves.** Older saves only had a count of pizzaiolos (`cooks`) and free waiters. `ensureShops()` turns them into average people: n pizzaiolos and ⌈2n/3⌉ waiters.

## Running the simulation

The day simulation lives in the page, so the script opens `index.html` in Chromium with Playwright and calls the game's own functions. A day is `managerMorning()` + `simulateDay()` + `finishDay()`, as the Day screen does.

```bash
npm i playwright && npx playwright install chromium   # only where Playwright isn't installed yet
node tools/sim_staff.js 60 1    # 60 days, starting at 1 star
node tools/sim_staff.js 60 4    # 60 days, starting at 4 stars
```

Every team starts from the same new game, with the buyer running the pantry (tier 2, so no hiring on its own). Each team is a list of `[role, speed, second skill]` in `TEAMS` at the top of the script; add your own there.

### Results on 2026-11-20 (they vary a little from run to run: customers are random)

60 days, starting at 1 star, starter room (5 tables, 10 seats), one oven:

| Team | Kitchen | Room | Served a day | Lost to the queue a day | Happy | Wages a day | Profit a day | Stars at the end |
|---|---|---|---|---|---|---|---|---|
| Start: 1 cook 3/3, 1 waiter 3/3 | 30 | 40 | 22.9 | 0.0 | 89% | $54 | $55 | 3.38 |
| Slow cook (1/3) | 21 | 40 | 20.4 | 2.4 | 91% | $48 | $43 | 2.81 |
| Fast cook (5/3) | 36 | 40 | 23.2 | 0.0 | 88% | $60 | $49 | 3.20 |
| Slow waiter (1/3) | 30 | 28 | 22.3 | 0.1 | 88% | $48 | $56 | 3.10 |
| Fast waiter (5/3) | 30 | 52 | 22.1 | 0.0 | 89% | $60 | $42 | 3.16 |
| Good cooking + charm (3/5) | 30 | 40 | 24.5 | 0.1 | 93% | $62 | $57 | 3.80 |
| Poor cooking + charm (3/1) | 30 | 40 | 19.9 | 0.0 | 83% | $46 | $41 | 2.01 |
| All 5/5 | 36 | 52 | 24.0 | 0.0 | 93% | $74 | $41 | 4.11 |
| 2 cooks + 2 waiters 3/3 | 36 | 80 | 23.1 | 0.0 | 88% | $108 | $1 | 3.19 |

### What the first run shows

- **Speed hardly matters in the starter shop.** About 23 to 25 customers want a table, and the 10 seats and the single oven limit the day before the staff does. A fast cook or a fast waiter only costs more; a slow waiter even comes out ahead. Only the slow cook (21 pizzas) loses customers.
- **Cooking and charm matter a lot.** From 3/1 to 3/5 the share of happy customers goes from 83% to 93%, and the stars after 60 days from 2.0 to 3.8. The profit gap is small at first ($41 against $57 a day) but grows as reputation brings more customers.
- **Extra staff doesn't pay off yet.** Two of each costs $108 a day for no more sales.

## Questions to explore

1. Speed should be worth paying for at some point. With how many seats and ovens does it start to pay? Should `COOK_CAP`, `WAITER_CAP` or `spMul` change so it matters sooner? The room can be changed in the script through `state.room.items` (see `ITEMS` and `starterRoom()`) and the ovens through `state.ovens`.
2. Is ±6 satisfaction from `crewSat` too strong next to the pizza itself (appeal, `ap`, roughly 40 to 90)? It decides a lot of the reputation.
3. Do wages follow value? Right now speed adds $3 a point and the second skill $2. The table suggests the second skill is worth more than speed.
4. A new player now pays $24 a day for a waiter who used to be free. Is the first week still comfortable? The goal on record is a beginner making about $100 a day at a normal price once the room is decent.
5. Is the manager's rule (always the fastest candidate) sensible, given the answers above?

## Rules for changes to the game

- Plain HTML and JS, no build and no dependencies. Every visible text goes through `t()` with the same key in `I18N.en` and `I18N.pt`.
- New saved fields need a default, so old saves still open.
- `3ds/game/day.lua` is a hand port of the simulation and doesn't have the staff system yet. Say so if a proposal touches `simulateDay()`.
- More in [`CLAUDE.md`](../CLAUDE.md).
