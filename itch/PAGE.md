# Pizza Magna on itch.io: page kit

Everything the itch.io page needs. The images are made by `node itch/make_media.js` (from the game's own art, fonts and colours); run it again after the game's look changes. The upload zip is made with the command at the end (it is not committed).

## Files

| File | Where it goes on itch.io | Size |
|---|---|---|
| `cover.png` | Edit game › **Cover image** (shown in lists and search) | 630 × 500 |
| `banner.png` | Edit game › Theme › **Banner** (the strip at the top of the page; itch scales it to the page width) | 1920 × 480 |
| `background.png` | Edit game › Theme › **Background image**, set to *tiled* (the dining room from above: red and white check floor, tables, a fountain; seamless) | 768 × 768 |
| `logo.png` | Transparent logo for the description, the devlog, social posts, Discord (not an itch field) | 1108 × 380 |
| `shot-1.png` … `shot-5.png` | Edit game › **Screenshots**, in this order: kitchen, menu, the day, room, contest | 1280 × 720 |

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

Fonts, if itch.io lets you pick them: headings a pixel font (Silkscreen or "Press Start 2P"), text the page default. Page width: leave at the default.

## Basics

- **Title:** Pizza Magna
- **Short description / tagline** (under 100 characters): `Run a 90s pixel-art pizzeria: invent pizzas, set prices, beat the rival.`
- **Kind of project:** HTML (playable in the browser)
- **Classification:** Games
- **Genre:** Simulation (Strategy as the second one, if allowed)
- **Release status:** In development (it is a prototype that keeps growing)
- **Pricing:** No payments (or "Name your own price" if you want tips)
- **Tags** (up to 10): `pizza`, `tycoon`, `management`, `pixel-art`, `cooking`, `restaurant`, `singleplayer`, `casual`, `relaxing`, `Family Friendly`
- **Embed options:** *Click to launch in fullscreen*, tick **Mobile friendly**, tick **Fullscreen button**; viewport 960 × 640 is fine (the game adapts to any size). Leave "SharedArrayBuffer" off.
- **Community:** comments on (it is a good place to collect pizza recipes: players can share `.pizza` files and links).

## Description (paste into the page)

> **Be the pizzaiolo. Then be the boss.**
>
> Pizza Magna is a pizzeria game in 90s pixel art. Make your own pizzas topping by topping, set the prices, fill the dining room and take on the pizzeria next door.
>
> **Cook**
> - 100+ toppings, 7 doughs and 9 sauces, and all of them are always available.
> - Place every piece yourself: whole, chopped or grated, turned the way you like. The weights and the cost are real.
> - 85+ combos to discover (Margherita, Hawaii, Piri-piri Chicken…) and a few terrible ones. Chicken with Nutella? The customers will tell you.
> - Share any pizza as a photo, a link or a `.pizza` file, and open friends' recipes on your own bench.
>
> **Run the place**
> - Four kinds of customers, and each wants something different: students look for a bargain and home toppings, families want a good deal, gourmets want quality, tourists want something unusual.
> - Set the prices, decorate the room (tables, plants, floors, walls, a jukebox), hire staff, buy ovens and pick your supplier.
> - Let a manager run everything, or do it all yourself.
> - A topping and a combo of the week, a market study to spot trends, and a rival who is not going to sit still.
>
> **Compete**
> - A contest every five days: sweet, cheese, spicy, seafood, vegetarian, creative and low-cost themes.
>
> **Also**
> - Calm Italian chiptune music, lively and relaxed tunes in turn.
> - English and Portuguese.
> - Runs in your browser (phones too) and saves your progress on your device. Nothing to install.
>
> *It is a work in progress: new toppings, new rooms and new rivals keep arriving. Tell us what you want next in the comments.*

## Short devlog for the first post

> Pizza Magna is on itch.io. It is a pizzeria tycoon in 90s pixel art: invent pizzas, set prices, decorate the room and beat the rival next door. It runs in the browser, saves automatically and works on phones. Play it, share your best recipe, and tell us what is missing.

## Making the upload zip

From the repo root:

```
zip -r pizza-magna-itch.zip index.html music.js sw.js manifest.webmanifest assets
zip -j pizza-magna-itch.zip itch/README.txt
```

The second line puts `itch/README.txt` at the root of the zip, for players who download it: open `index.html` to play, and the link to this repo.

On itch.io: Upload files › the zip › tick **This file will be played in the browser**. The game opens by itself from `index.html` at the root of the zip. (The zip is about 0.9 MB.) The game also lives at pizzamagna.xyz; players can use either, but the save is kept separately on each address.

### Offline download (Windows, Mac, Linux)

The same zip also plays offline: unzip it and open `index.html` (double-click). Everything it needs is inside, fonts and music included; only the visit counter needs the internet, and the game works without it.

To offer it, upload the same zip a second time (itch keeps the browser upload and the download apart): leave "played in the browser" unticked, tick **Windows**, **macOS** and **Linux**, and name it e.g. `Pizza Magna (offline, unzip and open index.html)`. The offline game keeps its own save in the browser that opens it; **Download save** / **Import save** in Options moves a game between versions.
