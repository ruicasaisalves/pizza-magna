# Pizza Magna on itch.io: page kit

Everything the itch.io page needs. The images are made by `node itch/make_media.js` (from the game's own art, fonts and colours); run it again after the game's look changes. The upload zip is made with the command at the end (it is not committed).

## Files

| File | Where it goes on itch.io | Size |
|---|---|---|
| `cover-main.png` | Edit game › **Cover image** (shown in lists and search), the one to use: the title and slogan from the main banner, with a pizzaiola and a waitress from the game's characters in the corners; made by `python3 itch/make_cover.py` | 630 × 500 |
| `cover.png` | The older cover drawn by `make_media.js`, kept as a spare | 630 × 500 |
| `banner-main.png` | Edit game › Theme › **Banner**, the one in use: the chef by the oven and the slogan *Build your own little pizza empire.* (made with ChatGPT, not by the script; keep it when re-running `make_media.js`) | 2000 × 667 |
| `banner.png` | The older banner drawn by `make_media.js` (planks and pizzas), kept as a spare | 1920 × 480 |
| `background.png` | Edit game › Theme › **Background image**, set to *tiled* (the dining room from above: red and white check floor, tables, a fountain; seamless) | 768 × 768 |
| `logo.png` | Transparent logo for the description, the devlog, social posts, Discord (not an itch field) | 1108 × 380 |
| `shot-1.png` … `shot-7.png` | Edit game › **Screenshots**, in this order: kitchen, menu, the day, room, contest, city, shop (team and bank) | 1280 × 720 |
| `head-cook.png`, `head-run.png`, `head-grow.png`, `head-compete.png`, `head-also.png` | Pictures inside the **description**, one above each section (pixel-art headings, transparent) | ~700 × 80 |
| `gif-pizza.gif`, `gif-day.gif`, `gif-city.gif` | Animated pictures inside the **description** (a pizza built piece by piece, the dining room at the dinner rush, a pan over the city); made by `node itch/make_gifs.js`. The dining room has a full team (five pizzaiolos, four waiters) | 360–520 wide |
| `preview.html` | Open it in a browser to see roughly how the page looks with all of the above (not uploaded) | |

## Colours (Theme editor)

The same palette the game uses, so the page and the game feel like one thing. itch.io names some of these fields a little differently; use the nearest one.

| Field | Colour | |
|---|---|---|
| Background colour (page) | `#2A1407` | wood, darkest |
| Content / widget background | `#4A260F` | dark wood |
| Text | `#F3E6C6` | parchment |
| Link | `#FBE39A` | pale brass |
| Button | `#C4352A` | tomato red |
| Button text | `#FFF6E0` | cream |
| Border | `#94661A` | brass |
| Headings accent (if offered) | `#E3B34A` | brass |

Fonts: the section headings are pictures now, so the **text font must be a plain, readable one** (the page default, or Lato / Open Sans); a pixel font in capitals for the whole description is hard to read on a phone. Title font: a pixel one (Silkscreen or "Press Start 2P") if offered. Page width: leave at the default.

## Basics

- **Title:** Pizza Magna
- **Short description / tagline** (under 100 characters): `Build your own little pizza empire: a 90s pixel-art pizzeria tycoon.`
- **Kind of project:** HTML (playable in the browser)
- **Classification:** Games
- **Genre:** Simulation (Strategy as the second one, if allowed)
- **Release status:** In development (it is a prototype that keeps growing)
- **Pricing:** No payments (or "Name your own price" if you want tips)
- **Tags** (up to 10): `pizza`, `tycoon`, `management`, `pixel-art`, `cooking`, `restaurant`, `singleplayer`, `casual`, `relaxing`, `Family Friendly`
- **Embed options:** *Click to launch in fullscreen*, tick **Mobile friendly**, tick **Fullscreen button**; viewport 960 × 640 is fine (the game adapts to any size). Leave "SharedArrayBuffer" off.
- **Community:** comments on (it is a good place to collect pizza recipes: players can share `.pizza` files and links).

## Description (paste into the page)

In the itch.io editor, put the pictures where the `[picture: …]` lines are (the editor's image button uploads them; centre them). Bold as marked.

> **BE THE PIZZAIOLO. THEN BE THE BOSS.**
>
> A pizzeria tycoon in 90s pixel art. Invent pizzas topping by topping, fill the dining room, beat the rival next door, then open shops across the city.
>
> [picture: gif-pizza.gif]
>
> [picture: head-cook.png]
> - **100+ toppings**, 7 doughs and 9 sauces, all available from day one.
> - Place every piece yourself: whole, chopped or grated, turned the way you like. Real weights, real costs.
> - **100+ combos** to discover (Margherita, Hawaii, Piri-piri Chicken…) and a few terrible ones. Chicken with Nutella? The customers will tell you.
> - Share any pizza as a photo, a link or a `.pizza` file.
>
> [picture: head-run.png]
> [picture: gif-day.gif]
> - Students, families, tourists and gourmets: **each wants something different**.
> - Set prices, decorate the room, buy ovens, pick your supplier.
> - **Hire your team**: pizzaiolos and waiters with their own skills.
> - Earn your stars: five stars take a good menu and a couple of months.
> - Your pizzeria's name and symbol sign every pizza you share.
>
> [picture: head-grow.png]
> [picture: gif-city.gif]
> - The city of **Porto Magno**: four neighbourhoods, each with its own customers, rents and a rival with its own strategy.
> - Rent or buy more shops, each with its own menu, room and team.
> - A bank for when the next shop can't wait.
>
> [picture: head-compete.png]
> - A **contest every five days**: classic, sweet, cheese, spicy, seafood, veggie, creative and low-cost.
>
> [picture: head-also.png]
> - Calm Italian chiptune music.
> - English and Portuguese.
> - Plays in the browser, **phones too**. Saves by itself. Nothing to install.
>
> *A work in progress: new toppings, rooms and rivals keep arriving. Tell us what you want next in the comments.*

## Short devlog for the first post

> Pizza Magna is on itch.io. It is a pizzeria tycoon in 90s pixel art: invent pizzas, set prices, decorate the room and beat the rival next door. It runs in the browser, saves automatically and works on phones. Play it, share your best recipe, and tell us what is missing.

## Automatic upload

Every push to `main` sends the browser game to itch.io by itself (`.github/workflows/itch.yml`, with butler, the itch.io tool): the files below go to the `html5` channel of `aruvez/pizza-magna`, with the game's `VERSION` as the version shown on itch. It needs the repo secret `BUTLER_API_KEY`, an itch.io API key (itch.io › Settings › API keys; GitHub › repo Settings › Secrets and variables › Actions); without it the job sends nothing. After the first automatic upload, tick **This file will be played in the browser** on the new `html5` file in the game's Edit page (once) and delete the old hand-made upload. The same files also go to the `offline-windows-linux-mac` channel, the download for playing offline (itch tags Windows, Linux and macOS from the channel name); after its first upload, give it a display name once (e.g. `HTML to play offline`) and delete the old hand-made offline zip. The workflow can also be run by hand from the Actions tab.

## Making the upload zip by hand

From the repo root:

```
zip -r pizza-magna-itch.zip index.html music.js city.js sw.js manifest.webmanifest assets
```

On itch.io: Upload files › the zip › tick **This file will be played in the browser**. The game opens by itself from `index.html` at the root of the zip. (The zip is about 2.6 MB, most of it the characters in `assets/cast/`.) The game also lives at pizzamagna.xyz; players can use either, but the save is kept separately on each address.

### Offline download (Windows, Mac, Linux)

The same zip also plays offline: unzip it and open `index.html` (double-click). Everything it needs is inside, fonts and music included; only the visit counter needs the internet, and the game works without it.

To offer it, upload the same zip a second time (itch keeps the browser upload and the download apart): leave "played in the browser" unticked, tick **Windows**, **macOS** and **Linux**, and name it e.g. `Pizza Magna (offline, unzip and open index.html)`. The offline game keeps its own save in the browser that opens it; **Download save** / **Import save** in Options moves a game between versions.
