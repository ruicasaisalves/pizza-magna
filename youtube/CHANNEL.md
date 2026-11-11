# Pizza Magna on YouTube: channel kit

Everything for the channel and the first Short. The files are made by `node youtube/make_short.js` (from the game itself: its art, fonts, people and music); run it again after the game's look changes.

## Files

| File | Where it goes | Size |
|---|---|---|
| `short.mp4` | The first Short (upload from the YouTube app or YouTube Studio) | 1080 × 1920, 27 s, 30 fps, with the Tarantella |
| `banner.png` | Studio › Customisation › Branding › **Banner image** | 2560 × 1440 (the brass-lined middle band is what phones and computers show; TVs show all of it) |
| `avatar.png` | Studio › Customisation › Branding › **Picture** (YouTube cuts it into a circle) | 800 × 800 |
| `watermark.png` | Studio › Customisation › Branding › **Video watermark** (shown at the corner of long videos) | 150 × 150 |

## Setting up the channel (about 15 minutes, on a computer)

1. Sign in to YouTube with the Google account you want to use. If the channel should not be under your own name, use **Create a channel › Use a custom name** (this makes a "brand account", which you can later share with other people).
2. **Name:** Pizza Magna. **Handle:** `@pizzamagna` (or `@pizzamagnagame` if it is taken).
3. In YouTube Studio › **Customisation**:
   - **Branding:** upload the picture, the banner and the watermark above.
   - **Basic info:** the description, the links and the email below.
4. Studio › **Settings › Channel › Basic info › Keywords:** paste the keywords below. In **Country**, choose Portugal.
5. Studio › **Settings › Upload defaults:** the title, description and tags below, so every upload starts from them.
6. Studio › **Settings › Channel › Advanced settings › Audience:** "No, set this channel as not made for kids" (the game is fine for children, but "made for kids" turns off comments and notifications, which you need to grow). Mark single videos as made for kids only if they are aimed at children.
7. Make two playlists: **Shorts** and **Devlogs** (later: "Pizza recipes" for funny pizzas).
8. Phone verification (Studio › Settings › Channel › Feature eligibility) unlocks custom thumbnails and longer videos.

### Description

> Pizza Magna is a pizzeria tycoon in 90s pixel art that you play in your browser, free, on a computer or a phone.
> Make your own pizzas topping by topping, set the prices, decorate the room and beat the pizzeria next door. Four kinds of customers, 100+ toppings, 85+ combos to discover (and a few terrible ones).
>
> Here: short clips of funny pizzas, the making of the game (devlogs), and new features as they arrive.
>
> ▶ Play: https://pizzamagna.xyz
> ▶ itch.io: (your itch.io page)

### Links (Customisation › Basic info › Links)

- Play Pizza Magna → `https://pizzamagna.xyz/?ref=youtube`
- itch.io → your itch.io page address

The `?ref=youtube` makes GoatCounter show YouTube as where the visit came from.

### Keywords

`pizza game, pizzeria tycoon, tycoon game, pixel art, browser game, cooking game, restaurant game, management game, indie game, free game, web game`

## The first Short

**Title** (under 70 characters, the start is what people see):
> I made a pizza game where customers judge your toppings 🍕

**Description:**
> Build a pizza topping by topping, set the price, and watch the customers decide. Chicken with Nutella? They will tell you.
> Play free in your browser: https://pizzamagna.xyz/?ref=yt-short1
> #pixelart #indiegame #pizza #gamedev #shorts

**Tags:** pizza game, pixel art, indie game, tycoon, browser game, cooking game, gamedev

**Settings:** not made for kids; category Gaming; comments on. In the app, choose the first second (the big pizza) as the cover frame.

**Pinned comment** (post it yourself right after publishing and pin it):
> What's the worst pizza you can make? 🍍🐟 Try it at pizzamagna.xyz and tell me here.

## What to post next

Shorts work best when they are regular: one or two a week is better than five in one day and then nothing.

- **Terrible combos:** each Short builds one bad pizza and shows the customer's reaction (lobster and Nutella, anchovies and blueberries, pineapple and salt cod...). The game has 19 of them.
- **The best pizza for each customer:** the perfect student pizza, the perfect gourmet pizza.
- **Before and after:** the old people against the new ones, the first room against today's.
- **Devlogs:** a longer video now and then (2–5 minutes) showing a new feature.

`make_short.js` can be changed to make another Short: the scenes and captions are near the top of the page code (`SF()`), and the topping lists are `PIECES` and `CLASH`.
