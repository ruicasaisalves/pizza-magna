#!/usr/bin/env python3
"""Pizza Magna: more toppings in detailed pixel art (mushrooms, tuna, pepperoni,
ham) and the GRATED/CHOPPED form of each. Same method as gen_ingredients.py.
Usage: python3 tools/gen_ingredients2.py <folder>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import gen_ingredients as G
from gen_ingredients import R, hexs, noise, shade, render, drop, pizza_base, marble

OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'preview')) + '/'
os.makedirs(OUT, exist_ok=True)

R.update({
    'cap': hexs(['#4e3018', '#74492a', '#9a6a40', '#bd8d5e', '#d8ae80']),
    'gill': hexs(['#9c8566', '#c2ab88', '#dccaa8', '#efe3c8', '#fbf4e2']),
    'tuna': hexs(['#7a5640', '#a77e62', '#c99f80', '#e2c0a0', '#f3dcc2']),
    'pep': hexs(['#5a1208', '#86200f', '#b0331a', '#d24c2c', '#ec7048']),
    'pepfat': hexs(['#c98a72', '#e6b29a', '#f6d4c0']),
    'chour': hexs(['#3a0c08', '#5c160e', '#7e2416', '#a03a24', '#bf5434']),
    'chfat': hexs(['#d8b8a0', '#f0dcc8', '#fff4e8']),
    'chskin': hexs(['#24070a', '#3e0e0c', '#5a1a12']),
    'ham': hexs(['#a04e52', '#c86f70', '#e2908c', '#f2b2aa', '#fbd2c8']),
    'hamfat': hexs(['#d8b8a8', '#efd6c8', '#fff0e6']),
})

def grid(W, H):
    ys, xs = np.mgrid[0:H, 0:W]
    return ys, xs, (W - 1) / 2, (H - 1) / 2

# ---------------- MUSHROOM (slice: cap + stem) ----------------
def mushroom(seed, W=26, H=24):
    rng = np.random.default_rng(seed + 300)
    ys, xs, cx, cy = grid(W, H)
    rot = (rng.random() - .5) * .7
    u = (xs - cx) * np.cos(rot) + (ys - cy) * np.sin(rot)
    v = -(xs - cx) * np.sin(rot) + (ys - cy) * np.cos(rot) + 2
    capr = 11 + rng.random()
    cap = (u / capr) ** 2 + (v / 9.5) ** 2 <= 1
    cap &= v <= 1.5
    stem = (np.abs(u - (rng.random() - .5) * 2) <= 3.6 + v * .12) & (v > 0) & (v < 10.5)
    mask = cap | stem
    n = noise(H, W, 3, rng)
    inner = ((u / (capr - 3)) ** 2 + ((v + .5) / 6.5) ** 2 <= 1) & (v <= .5)
    height = np.where(cap, np.clip(1 - (u / capr) ** 2 - ((v) / 9.5) ** 2, 0, 1) ** .5 * 2.6, 1.2) + (n - .5) * .6
    mat = [['gill' if (inner[y, x] or stem[y, x]) else 'cap' for x in range(W)] for y in range(H)]
    light = np.clip(shade(height, mask) * .9 + .15, 0, 1) * mask
    img = render(mat, light, mask, {'gill': 'cap'})
    # gills: thin lines inside the cap
    px = img.load()
    for x in range(W):
        for y in range(H):
            if inner[y, x] and not stem[y, x] and (x + seed) % 3 == 0 and v[y, x] < -.5:
                px[x, y] = R['gill'][1] + (255,)
    return img

# ---------------- TUNA (flakes) ----------------
def tuna(seed, W=28, H=24):
    rng = np.random.default_rng(seed + 400)
    ys, xs, cx, cy = grid(W, H)
    mask = np.zeros((H, W), bool); height = np.zeros((H, W))
    for _ in range(6):
        bx, by = cx + (rng.random() - .5) * 12, cy + (rng.random() - .5) * 9
        rx, ry, a = 5 + rng.random() * 3, 3.5 + rng.random() * 2, rng.random() * 3.14
        u = (xs - bx) * np.cos(a) + (ys - by) * np.sin(a); v = -(xs - bx) * np.sin(a) + (ys - by) * np.cos(a)
        d = (u / rx) ** 2 + (v / ry) ** 2
        m = d <= 1; mask |= m
        height = np.maximum(height, np.clip(1 - d, 0, 1) ** .6 * 2.2)
    n = noise(H, W, 2, rng)
    height += (np.sin(xs * 1.1 + ys * .5 + n * 3) * .15)      # fibres
    mat = [['tuna'] * W for _ in range(H)]
    light = np.clip(shade(height, mask) * .9 + .12, 0, 1) * mask
    return render(mat, light, mask, {})

# ---------------- PEPPERONI (slice that curls at the edges) ----------------
def pepperoni(seed, D=20):
    rng = np.random.default_rng(seed + 500)
    ys, xs, c, _ = grid(D, D)
    dx, dy = xs - c, ys - c
    ang = np.arctan2(dy, dx)
    r = np.hypot(dx, dy) / (D / 2 - .4) / (1 + .04 * np.sin(ang * 3 + seed))
    mask = r <= 1
    height = (r ** 2) * 1.6 - np.clip(1 - r ** 2, 0, 1) * .4          # cup: the edge rises
    n = noise(D, D, 2, rng)
    mat = [['pepfat' if (mask[y, x] and r[y, x] < .82 and n[y, x] > .82) else 'pep' for x in range(D)] for y in range(D)]
    light = np.clip(shade(height, mask) * .85 + .2, 0, 1) * mask
    img = render(mat, light, mask, {'pepfat': 'pep'})
    px = img.load()
    for x in range(D):            # toasted edge
        for y in range(D):
            if mask[y, x] and .82 < r[y, x] <= .93 and (x + y + seed) % 3: px[x, y] = R['pep'][1] + (255,)
    for (x, y) in [(int(c - 3), int(c - 4)), (int(c - 4), int(c - 3))]:
        px[x, y] = R['pep'][4] + (255,)
    return img

# ---------------- CHOURIÇO (slice with fat and skin) ----------------
def chourico(seed, D=20):
    rng = np.random.default_rng(seed + 700)
    ys, xs, c, _ = grid(D, D)
    r = np.hypot(xs - c, ys - c) / (D / 2 - .4)
    mask = r <= 1
    height = np.clip(1 - r ** 2, 0, 1) ** .5 * 1.6
    n = noise(D, D, 2, rng)
    mat = [['chfat' if (mask[y, x] and r[y, x] < .8 and n[y, x] > .7) else ('chskin' if r[y, x] > .84 else 'chour')
            for x in range(D)] for y in range(D)]
    light = np.clip(shade(height, mask) * .8 + .22, 0, 1) * mask
    return render(mat, light, mask, {'chfat': 'chour'})

# ---------------- HAM (folded slice) ----------------
def ham(seed, W=24, H=22):
    rng = np.random.default_rng(seed + 600)
    ys, xs, cx, cy = grid(W, H)
    a = (rng.random() - .5) * 1.2
    u = (xs - cx) * np.cos(a) + (ys - cy) * np.sin(a); v = -(xs - cx) * np.sin(a) + (ys - cy) * np.cos(a)
    hw, hh, rad = 9.5, 7.5, 3.5
    qx, qy = np.clip(np.abs(u) - (hw - rad), 0, None), np.clip(np.abs(v) - (hh - rad), 0, None)
    n = noise(H, W, 4, rng)
    mask = np.hypot(qx, qy) <= rad + (n - .5) * 1.2
    fold = u * .55 + v * .2                                  # diagonal fold
    height = np.where(fold > 1, 2.2 - (fold - 1) * .25, fold * 1.1) + (n - .5) * .5
    fat = (np.hypot(qx, qy) > rad - 1.6) & mask
    mat = [['hamfat' if fat[y, x] else 'ham' for x in range(W)] for y in range(H)]
    light = np.clip(shade(height, mask) * .85 + .2, 0, 1) * mask
    return render(mat, light, mask, {'hamfat': 'ham'})

# ---------------- GRATED / CHOPPED ----------------
def grated(ramp, seed, kind='shred', W=26, H=24, n_bits=26, edge_ramp=None):
    """Pile of little bits: 'shred' = thin strips (grated cheese),
    'dice' = small cubes (ham, pepperoni, chopped mushroom), 'flake' = crumbs."""
    rng = np.random.default_rng(seed + 900)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); px = img.load()
    ramp = R[ramp]; dark = R[edge_ramp or 0] if edge_ramp else None
    cx, cy = (W - 1) / 2, (H - 1) / 2
    for _ in range(n_bits):
        a, r = rng.random() * 6.28, np.sqrt(rng.random()) * min(W, H) * .42
        x0, y0 = int(cx + np.cos(a) * r), int(cy + np.sin(a) * r)
        if kind == 'shred':
            L_ = rng.integers(3, 6); ang = rng.random() * 3.14
            pts = [(int(round(x0 + np.cos(ang) * t)), int(round(y0 + np.sin(ang) * t * .7))) for t in range(L_)]
            for i, (x, y) in enumerate(pts):
                if 0 <= x < W and 0 <= y + 1 < H:
                    px[x, y + 1] = ramp[0] + (255,)               # shadow underneath
            for i, (x, y) in enumerate(pts):
                if 0 <= x < W and 0 <= y < H:
                    px[x, y] = ramp[min(len(ramp) - 1, 2 + (i == 1) + int(rng.random() * 2))] + (255,)
        elif kind == 'chunk':
            # irregular 4-6 px flake lit from the top left (fish, shredded meats)
            rw, rh = rng.uniform(2, 3.2), rng.uniform(1.6, 2.4)
            for yy in range(-3, 4):
                for xx in range(-4, 5):
                    d = (xx / rw) ** 2 + (yy / rh) ** 2
                    if d > 1 + rng.uniform(-.25, .1): continue
                    x, y = x0 + xx, y0 + yy
                    if not (0 <= x < W and 0 <= y < H): continue
                    if d > .7: col = ramp[0] if (xx + yy) > 0 else ramp[1]
                    elif xx + yy < -1: col = ramp[-1]
                    else: col = ramp[len(ramp) // 2 + (rng.random() < .3)]
                    px[x, y] = col + (255,)
        elif kind == 'cube':
            sz = int(rng.integers(3, 5))
            for yy in range(sz + 2):
                for xx in range(sz + 1):
                    x, y = x0 + xx, y0 + yy
                    if not (0 <= x < W and 0 <= y < H): continue
                    if yy < 2:   col = ramp[-1] if xx < sz else ramp[-2]   # lit top
                    elif xx == sz: col = ramp[0]                            # side in shadow
                    else:        col = ramp[len(ramp) // 2]                 # front face
                    if yy == sz + 1: col = ramp[0]                          # dark base
                    px[x, y] = col + (255,)
        else:
            s = 2 if kind == 'dice' else 1
            for yy in range(s + 1):
                for xx in range(s + 1):
                    x, y = x0 + xx, y0 + yy
                    if not (0 <= x < W and 0 <= y < H): continue
                    if xx == s or yy == s: px[x, y] = ramp[0] + (255,)         # dark edge
                    elif xx == 0 and yy == 0: px[x, y] = ramp[-1] + (255,)     # lit corner
                    else: px[x, y] = ramp[len(ramp) // 2] + (255,)
    return img

if __name__ == '__main__':
    sets = [
        ('Cogumelos', [mushroom(s) for s in (1, 2, 3)], grated('gill', 1, 'flake', n_bits=40)),
        ('Atum', [tuna(s) for s in (1, 2, 3)], grated('tuna', 2, 'chunk', n_bits=9)),
        ('Pepperoni', [pepperoni(s) for s in (1, 2, 3)], grated('pep', 3, 'cube', n_bits=11)),
        ('Chouriço', [chourico(s) for s in (1, 2, 3)], grated('chour', 6, 'cube', n_bits=11)),
        ('Fiambre', [ham(s) for s in (1, 2, 3)], grated('ham', 4, 'cube', n_bits=12)),
        ('Mozzarella', [G.mozz(s) for s in (1, 2, 3)], grated('mozz', 5, 'shred', n_bits=40)),
    ]
    for name, arr, gr in sets:
        for i, im in enumerate(arr): im.save(f'{OUT}{name.lower()}_{i + 1}.png')
        gr.save(f'{OUT}{name.lower()}_ralado.png')

    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    K, ROW = 6, 170
    sheet = Image.new('RGB', (1000, 40 + ROW * len(sets) + 40 + 600 + 20), (27, 20, 16))
    dr = ImageDraw.Draw(sheet)
    dr.text((20, 10), 'Whole / sliced (x6, 3 variants)', fill=(240, 220, 180), font=fs)
    dr.text((760, 10), 'Grated / chopped (x6)', fill=(240, 220, 180), font=fs)
    for i, (name, arr, gr) in enumerate(sets):
        y = 36 + i * ROW
        dr.text((20, y + 4), name, fill=(240, 220, 180), font=f)
        x = 150
        for im in arr + [gr]:
            if im is gr: x = 760
            m = im.resize((im.width * K, im.height * K), Image.NEAREST)
            bg = Image.new('RGB', (190, ROW - 12), (196, 52, 28))
            bg.paste(m, ((190 - m.width) // 2, (ROW - 12 - m.height) // 2), m)
            sheet.paste(bg, (x, y)); x += 200
    # scene: pizza with a mix, half with grated cheese
    rng = np.random.default_rng(9)
    SW, SH = 320, 200
    scene = marble(SW, SH, rng).convert('RGBA')
    pz = pizza_base(170, rng)
    layer = Image.new('RGBA', (170, 170), (0, 0, 0, 0))
    prng = np.random.default_rng(3)
    # grated cheese spread over the whole pizza
    for k in range(14):
        a, r = prng.random() * 6.28, np.sqrt(prng.random()) * 56
        layer.alpha_composite(grated('mozz', 50 + k, 'shred', n_bits=40), (int(85 + np.cos(a) * r - 13), int(85 + np.sin(a) * r - 12)))
    pieces = [s[1][i % 3] for s in sets[:5] for i in range(3)] + [grated(k, 70 + i, 'cube', n_bits=9) for i, k in enumerate(['ham', 'chour', 'ham'])]
    prng.shuffle(pieces); spots = []
    for p in pieces:
        for _ in range(300):
            a, r = prng.random() * 6.28, np.sqrt(prng.random()) * 58
            x, y = 85 + np.cos(a) * r, 85 + np.sin(a) * r
            if all(np.hypot(x - sx, y - sy) > 18 for sx, sy in spots): break
        spots.append((x, y))
        layer.alpha_composite(drop(p), (int(x - p.width / 2), int(y - p.height / 2)))
    pz.alpha_composite(layer)
    sh = Image.new('RGBA', (176, 176), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((4, 6, 174, 176), fill=(40, 30, 20, 90))
    scene.alpha_composite(sh, (70, 12)); scene.alpha_composite(pz, (72, 12))
    y0 = 36 + ROW * len(sets) + 8
    dr.text((20, y0), 'On the pizza (320x200 x3): grated mozzarella below, the 4 new ones on top', fill=(240, 220, 180), font=fs)
    sheet.paste(scene.convert('RGB').resize((SW * 3, SH * 3), Image.NEAREST), (20, y0 + 24))
    sheet.save(OUT + 'preview_ingredientes2.png')
    print('ok', sheet.size)
