#!/usr/bin/env python3
"""Pizza Magna: eighth batch in detailed pixel art. Burrata, squid, aubergine, black pudding, walnuts
and potato, with the chopped form following the rule in docs/ingredients.md.
Same method as gen_ingredients.py. None of these pieces has a front, so they don't rotate.
Usage: python3 tools/gen_ingredients8.py <folder>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from gen_ingredients import R, hexs, noise, shade, render
from gen_ingredients2 import grated, grid
from gen_ingredients5 import axes

OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'preview')) + '/'
os.makedirs(OUT, exist_ok=True)

R.update({
    'burrata': hexs(['#a8a294', '#d0ccc0', '#ebe8e0', '#f8f7f2', '#ffffff']),
    'burcream': hexs(['#a8986a', '#c8b88a', '#e2d6aa', '#f4ecc8']),
    'squid': hexs(['#a89888', '#cebfae', '#e8ded0', '#f8f3ea', '#fffdf8']),
    'squidskin': hexs(['#6a3a4a', '#8e5262', '#b4747e']),
    'aub': hexs(['#7a7442', '#a09a5e', '#c2bc7e', '#dcd6a0', '#eeeac4']),
    'aubskin': hexs(['#140a1a', '#26122e', '#3e1e48', '#5a2e64']),
    'aubseed': hexs(['#5a4a26', '#7a6a36', '#9a8a4a']),
    'morc': hexs(['#120606', '#24090a', '#3a1012', '#561a1a', '#74282a']),
    'morcfat': hexs(['#b8a090', '#d8c4b4', '#f0e2d6']),
    'walnut': hexs(['#3e200c', '#623618', '#8a5226', '#b07438', '#d29c5c']),
    'pot': hexs(['#a8884a', '#ccb06a', '#e6cc8a', '#f6e4b0', '#fff4d4']),
    'potgold': hexs(['#8a5a1a', '#b47a2a', '#d89e40']),
    'char': hexs(['#2e1a0c', '#4a2a14', '#6a3e1e']),
})

# ---------------- BURRATA (open ball, with the creamy filling showing) ----------------
def burrata(seed, D=24):
    rng = np.random.default_rng(seed + 3600)
    ys, xs, c, _ = grid(D, D)
    ang = np.arctan2(ys - c, xs - c)
    r = np.hypot(xs - c, ys - c) / (D / 2 - .5) / (1 + .05 * np.sin(ang * 3 + seed))
    mask = r <= 1
    a0 = rng.random() * 6.28
    ox, oy = c + np.cos(a0) * 3, c + np.sin(a0) * 3                 # tear off-centre
    tear = np.hypot((xs - ox) / 6.5, (ys - oy) / 5.5) <= 1 + (rng.random((D, D)) - .5) * .4
    tear &= mask & (r < .9)
    grain = rng.random((D, D))
    height = np.sqrt(np.clip(1 - r ** 2, 0, 1)) * 2.4 - np.where(tear, 1.4 - grain * .9, 0)     # deep, stringy filling
    mat = [['burcream' if tear[y, x] else 'burrata' for x in range(D)] for y in range(D)]
    return render(mat, np.clip(shade(height, mask) * .7 + .3, 0, 1) * mask, mask, {'burcream': 'burrata'})

# ---------------- SQUID (ring) ----------------
def squid(seed, D=17):
    rng = np.random.default_rng(seed + 3700)
    ys, xs, c, _ = grid(D, D)
    sq = 1 + (rng.random() - .5) * .3
    ang = np.arctan2(ys - c, xs - c)
    r = np.hypot((xs - c) * sq, (ys - c) / sq) / (D / 2 - .5) / (1 + .05 * np.sin(ang * 2 + seed))
    mask = (r <= 1) & (r >= .5)
    height = np.clip(1 - ((r - .75) / .26) ** 2, 0, 1) * 1.6
    spots = (rng.random((D, D)) > .86) & (r > .8)                    # bits of skin, purplish
    mat = [['squidskin' if spots[y, x] else 'squid' for x in range(D)] for y in range(D)]
    return render(mat, np.clip(shade(height, mask) * .75 + .28, 0, 1) * mask, mask, {'squidskin': 'squid'})

# ---------------- AUBERGINE (grilled slice) ----------------
def aubergine(seed, D=22):
    rng = np.random.default_rng(seed + 3800)
    ys, xs, c, _ = grid(D, D)
    sq = 1 + (rng.random() - .5) * .2
    r = np.hypot((xs - c) * sq, (ys - c) / sq) / (D / 2 - .5)
    mask = r <= 1
    n = noise(D, D, 3, rng)
    height = np.clip(1 - r ** 2, 0, 1) ** .4 * 1.2 + (n - .5) * .4
    a = rng.random() * 3.14
    u = (xs - c) * np.cos(a) + (ys - c) * np.sin(a)
    grill = ((u + 40) % 5) < 1.1                                       # grill marks
    seeds = (np.abs(r - .5) < .07) & (rng.random((D, D)) > .45)        # ring of seeds
    mat = [['aubskin' if r[y, x] > .78 else 'char' if grill[y, x] and r[y, x] < .74 else 'aubseed' if seeds[y, x] else 'aub'
            for x in range(D)] for y in range(D)]
    return render(mat, np.clip(shade(height, mask) * .8 + .22, 0, 1) * mask, mask,
                  {'aub': 'aubskin', 'char': 'aubskin', 'aubseed': 'aubskin'})

# ---------------- BLACK PUDDING (dark slice with light grains) ----------------
def morcela(seed, D=18):
    rng = np.random.default_rng(seed + 3900)
    ys, xs, c, _ = grid(D, D)
    r = np.hypot(xs - c, ys - c) / (D / 2 - .4)
    mask = r <= 1
    height = np.clip(1 - r ** 2, 0, 1) ** .5 * 1.5
    fat = (rng.random((D, D)) > .9) & (r < .8)
    mat = [['morcfat' if fat[y, x] else 'morc' for x in range(D)] for y in range(D)]
    light = np.clip(shade(height, mask) * .9 + .15 - np.where(r > .86, .25, 0), 0, 1) * mask   # darker skin
    return render(mat, light, mask, {'morcfat': 'morc'})

# ---------------- WALNUT (half, in two lobes with grooves) ----------------
def walnut(seed, W=18, H=16):
    rng = np.random.default_rng(seed + 4000)
    u, v = axes(W, H, rng.random() * 6.28)
    lobes = (np.hypot((u + 3.6) / 4.4, v / 6.4) <= 1) | (np.hypot((u - 3.6) / 4.4, v / 6.4) <= 1)
    mask = lobes & (np.abs(u) > .6)                                    # middle groove
    n = noise(H, W, 2, rng)
    bump = np.sin(v * 1.3 + n * 2) * np.sin(np.abs(u) * 1.1) * .6       # wrinkles of the kernel
    height = np.clip(1 - (v / 6.4) ** 2, 0, 1) * 1.4 + bump
    mat = [['walnut'] * W for _ in range(H)]
    return render(mat, np.clip(shade(height, mask) * .9 + .15, 0, 1) * mask, mask, {})

# ---------------- POTATO (thin slice, golden from the oven) ----------------
def potato(seed, W=20, H=17):
    rng = np.random.default_rng(seed + 4100)
    u, v = axes(W, H, rng.random() * 3.14)
    r = np.hypot(u / 8.6, v / 7.0)
    mask = r <= 1
    n = noise(H, W, 3, rng)
    height = np.clip(1 - r ** 2, 0, 1) ** .3 * .9 + (n - .5) * .35
    gold = (r > .7) | (n > .78)                                        # toasted edge and spots
    mat = [['potgold' if r[y, x] > .9 else 'pot' if not gold[y, x] else 'potgold' if n[y, x] > .78 else 'pot' for x in range(W)] for y in range(H)]
    light = np.clip(shade(height, mask) * .7 + .3 - np.where((r > .72) & (r <= .9), .12, 0), 0, 1) * mask
    return render(mat, light, mask, {'pot': 'potgold'})

SETS = [
    ('Burrata', burrata, ('burcream', 'shred', 40)),
    ('Lulas', squid, ('squid', 'chunk', 9)),
    ('Beringela', aubergine, ('aub', 'flake', 40)),
    ('Morcela', morcela, ('morc', 'cube', 11)),
    ('Nozes', walnut, ('walnut', 'dice', 22)),
    ('Batata', potato, ('pot', 'flake', 40)),
]

if __name__ == '__main__':
    from gen_ingredients import drop
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 17)
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    ROW = 150
    sheet = Image.new('RGB', (1000, 40 + ROW * len(SETS)), (27, 20, 16))
    dr = ImageDraw.Draw(sheet)
    dr.text((20, 10), 'Whole / sliced (3 variants)', fill=(240, 220, 180), font=fs)
    dr.text((760, 10), 'Grated / chopped', fill=(240, 220, 180), font=fs)
    for i, (name, fn, gr) in enumerate(SETS):
        key = name.lower()
        arr = [fn(s) for s in (1, 2, 3)]
        g = grated(gr[0], 90 + i, gr[1], n_bits=gr[2])
        for j, im in enumerate(arr): im.save(f'{OUT}{key}_{j + 1}.png')
        g.save(f'{OUT}{key}_picado.png')
        y = 36 + i * ROW
        dr.text((20, y + 4), name, fill=(240, 220, 180), font=f)
        x = 150
        for im in arr + [g]:
            if im is g: x = 760
            d = drop(im); K = 6 if (d.width * 6 <= 186 and d.height * 6 <= ROW - 14) else 4
            m = d.resize((d.width * K, d.height * K), Image.NEAREST)
            bg = Image.new('RGB', (190, ROW - 12), (196, 52, 28))
            bg.paste(m, ((190 - m.width) // 2, (ROW - 12 - m.height) // 2), m)
            sheet.paste(bg, (x, y)); x += 200
    sheet.save(OUT + 'preview_ingredientes8.png')
    print('ok', sheet.size)
