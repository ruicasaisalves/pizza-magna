#!/usr/bin/env python3
"""Pizza Magna: nineteenth batch. Three berries: blackberry (amora), blueberry (mirtilo)
and raspberry (framboesa). Same method as gen_ingredients.py (see tools/CLAUDE.md).

None of them rotates (seen from above they have no front). Each whole berry is a small
cluster or ball, 11 to 15 px; the chopped form is a few halves, cut side up.
- Blackberry: a cluster of glossy black-purple drupelets, a little longer than wide.
- Blueberry: a dusty blue ball with a lighter bloom and the dark star-shaped crown.
- Raspberry: a ring of red drupelets seen from the top, with the hollow in the middle.
Usage: python3 tools/gen_ingredients19.py <folder>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from gen_ingredients import R, hexs, render, shade

OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'preview')) + '/'

R.update({
    'amora': hexs(['#12060f', '#2a0e24', '#48183c', '#6e2a5c', '#a05a8c']),     # black-purple, glossy
    'amorain': hexs(['#5a0e2a', '#8a1a40', '#b8325a', '#d8608a']),             # inside of a cut blackberry
    'mirt': hexs(['#141a3a', '#26345e', '#3e5288', '#6a7eb0', '#a2b2d4']),      # blueberry skin, dusty
    'mirtin': hexs(['#6a7a4a', '#9aa86a', '#c4cc92', '#e2e4b8']),              # pale green-yellow flesh
    'fram': hexs(['#5a0612', '#8e0e22', '#c2203a', '#e8485e', '#ff8a96']),      # raspberry red
    'framin': hexs(['#a01a34', '#d03c58', '#f07088', '#ffb0bc']),
})

def drupes(seed, base, ramp, W, H, ry, rx, hole=0, step=2.7):
    """a berry made of little round drupelets on a hexagonal grid inside an ellipse (rx, ry):
    each one is its own small lit ball, so the bumps read clearly; hole > 0 leaves the hollow
    of a raspberry in the middle"""
    rng = np.random.default_rng(seed + base)
    ys, xs = np.mgrid[0:H, 0:W]
    cx, cy = (W - 1) / 2 + (rng.random() - .5) * .5, (H - 1) / 2 + (rng.random() - .5) * .5
    pts = []
    for row in range(-8, 9):
        for col in range(-8, 9):
            x = cx + (col + (row % 2) * .5) * step + (rng.random() - .5) * .3
            y = cy + row * step * .87 + (rng.random() - .5) * .3
            e = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            if e <= 1 and not (hole and e < hole): pts.append((x, y))
    height = np.zeros((H, W)); mask = np.zeros((H, W), bool)
    rad = step * .62
    for x, y in pts:
        d = np.hypot(xs - x, ys - y) / rad
        m = d <= 1
        height = np.where(m, np.maximum(height, np.sqrt(np.clip(1 - d ** 2, 0, 1)) * 1.4), height)
        mask |= m
    bulge = np.clip(1 - ((xs - cx) / (rx + 2)) ** 2 - ((ys - cy) / (ry + 2)) ** 2, 0, 1)   # the berry as a whole is round
    light = np.clip(shade(height, mask) * .75 + bulge * .3 - .05, 0, 1) * mask
    mat = [[ramp] * W for _ in range(H)]
    return render(mat, light, mask, {ramp: ramp}), pts

# ---------------- BLACKBERRY ----------------
def blackberry(seed, W=16, H=19):
    img, pts = drupes(seed, 5700, 'amora', W, H, 7.6, 6.2, step=2.5)
    px = img.load()
    for x, y in pts:                                          # a glint on each drupelet: it is glossy
        X, Y = int(round(x - .8)), int(round(y - .8))
        if 0 <= X < W and 0 <= Y < H and px[X, Y][3]: px[X, Y] = R['amora'][4] + (255,)
    return img

# ---------------- BLUEBERRY ----------------
def blueberry(seed, D=13):
    rng = np.random.default_rng(seed + 5800)
    ys, xs = np.mgrid[0:D, 0:D]
    c = (D - 1) / 2 + (rng.random() - .5) * .4
    r = np.hypot(xs - c, ys - c) / (D / 2 - .4)
    mask = r <= 1
    height = np.sqrt(np.clip(1 - r ** 2, 0, 1)) * 3
    light = np.clip(shade(height, mask) * .9 + .12, 0, 1) * mask
    img = render([['mirt'] * D for _ in range(D)], light, mask, {'mirt': 'mirt'})
    px = img.load()
    cx, cy = int(round(c - .3)), int(round(c - .3))          # the crown, where the light falls: a dark star with a hollow
    for dx in range(-2, 3):                                   # a light rim around the crown so it stands out on the skin
        for dy in range(-2, 3):
            if abs(dx) + abs(dy) in (2, 3): px[cx + dx, cy + dy] = R['mirt'][3] + (255,)
    for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):   # the dark star
        px[cx + dx, cy + dy] = R['mirt'][0] + (255,)
    return img

# ---------------- RASPBERRY (seen from the top, hollow in the middle) ----------------
def raspberry(seed, D=15):
    img, pts = drupes(seed, 5900, 'fram', D, D, 6.2, 6.2, hole=.1)
    px = img.load()
    c = (D - 1) / 2
    for y in range(D):                                        # the hollow where the stem was
        for x in range(D):
            if np.hypot(x - c, y - c) <= 1.6: px[x, y] = R['fram'][0] + (255,)
    for x, y in pts:
        X, Y = int(round(x - .8)), int(round(y - .8))
        if 0 <= X < D and 0 <= Y < D and px[X, Y][3] and np.hypot(X - c, Y - c) > 2: px[X, Y] = R['fram'][4] + (255,)
    return img

# ---------------- CHOPPED: a few halves, cut side up ----------------
def halves(seed, skin, flesh, base, n=4, W=24, H=22, D=8):
    rng = np.random.default_rng(seed + base)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    placed = []
    for _ in range(60):
        if len(placed) >= n: break
        x, y = int(rng.integers(0, W - D)), int(rng.integers(0, H - D))
        if any(abs(x - a) < 6 and abs(y - b) < 6 for a, b in placed): continue
        placed.append((x, y))
        ys, xs = np.mgrid[0:D, 0:D]
        r = np.hypot(xs - (D - 1) / 2, ys - (D - 1) / 2) / (D / 2 - .3)
        mask = r <= 1
        height = (1 - r ** 2) * .5
        mat = [[skin if r[j, i] > .66 else flesh for i in range(D)] for j in range(D)]
        light = np.clip(shade(height, mask) * .6 + .4, 0, 1) * mask
        img.alpha_composite(render(mat, light, mask, {flesh: skin, skin: skin}), (x, y))
    return img

def blackberry_halves(seed): return halves(seed, 'amora', 'amorain', 6000)
def blueberry_halves(seed): return halves(seed, 'mirt', 'mirtin', 6100, n=5, D=7)
def raspberry_halves(seed): return halves(seed, 'fram', 'framin', 6200)

SETS = [('Amora', blackberry, blackberry_halves), ('Mirtilo', blueberry, blueberry_halves), ('Framboesa', raspberry, raspberry_halves)]

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    from build_atlas import drop
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    ROW = 150
    sheet = Image.new('RGB', (1000, 40 + ROW * len(SETS)), (27, 20, 16)); dr = ImageDraw.Draw(sheet)
    dr.text((20, 10), 'Whole (3 variants) / chopped', fill=(240, 220, 180), font=fs)
    for i, (name, fn, gr) in enumerate(SETS):
        y = 36 + i * ROW; x = 20
        for im in [fn(1), fn(2), fn(3), gr(41)]:
            d = drop(im); K = 6
            m = d.resize((d.width * K, d.height * K), Image.NEAREST)
            bg = Image.new('RGB', (230, ROW - 12), (196, 52, 28))
            bg.paste(m, ((230 - m.width) // 2, (ROW - 12 - m.height) // 2), m)
            sheet.paste(bg, (x, y)); x += 240
    sheet.save(OUT + 'preview_ingredientes19.png'); print('ok', sheet.size)
