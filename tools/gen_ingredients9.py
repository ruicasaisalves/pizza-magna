#!/usr/bin/env python3
"""Pizza Magna: ninth batch in detailed pixel art. Parmesan, artichoke, courgette, Italian
sausage, padrón peppers and pine nuts, with the chopped form following the rule in docs/ingredients.md.
Same method as gen_ingredients.py.

Pieces with a front (artichoke quarter, padrón) take `ang`: with ang=0 they lie down,
with the front to the right, and the game turns that image in quarter turns.
Usage: python3 tools/gen_ingredients9.py <folder>"""
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
    'parm': hexs(['#a8904e', '#cdb470', '#e4d090', '#f4e6b4', '#fff6d8']),
    'artleaf': hexs(['#2a3a1a', '#435a26', '#5e7a34', '#7e9a4a', '#a4ba6e']),
    'artheart': hexs(['#a89c5a', '#c8be7c', '#e2d8a0', '#f2ecc4']),
    'artchoke': hexs(['#5a3a4a', '#7e5a6a', '#a4808a']),
    'artstem': hexs(['#4e5a2a', '#6e7e3a', '#94a256']),
    'zuc': hexs(['#8a9a5a', '#aebc7a', '#ccd69a', '#e4ecbc', '#f4f8dc']),
    'zucskin': hexs(['#0e260e', '#1a3c18', '#2a5626', '#3e7034']),
    'sals': hexs(['#4a2014', '#6e341e', '#94502e', '#b46c44', '#d08c62']),
    'fennel': hexs(['#8a8a4a', '#b0b06a', '#d4d48e']),
    'padron': hexs(['#0e2a0c', '#1a4216', '#2a5e22', '#3e7a30', '#62a04a']),
    'char': hexs(['#141008', '#2a2010', '#40321a']),
    'pine': hexs(['#a07a3a', '#c89e58', '#e2c07c', '#f4dca4', '#fff2d0']),
    'stem': hexs(['#123e16', '#2a6a24', '#4fa040']),
})

# ---------------- PARMESAN (thin curled shaving) ----------------
def parmesan(seed, W=22, H=17):
    rng = np.random.default_rng(seed + 4200)
    u, v = axes(W, H, rng.random() * 3.14)
    n = noise(H, W, 2, rng)
    edge = (rng.random((H, W)) - .5) * 1.2
    mask = (np.abs(u) <= 8.5 + edge + (n - .5) * 2) & (np.abs(v) <= 4.8 + edge * .6 + (n - .5) * 1.5)
    curl = np.sin((v + 4.8) / 9.6 * np.pi * 1.4)             # the shaving curls lengthwise
    height = curl * 1.4 + (n - .5) * .4
    mat = [['parm'] * W for _ in range(H)]
    img = render(mat, np.clip(shade(height, mask) * .75 + .28, 0, 1) * mask, mask, {})
    px = img.load()
    for _ in range(6):                                       # tyrosine crystals
        x, y = int(rng.integers(0, W)), int(rng.integers(0, H))
        if mask[y, x] and 0 < x < W - 1 and mask[y, x - 1] and mask[y, x + 1]: px[x, y] = R['parm'][4] + (255,)
    return img

# ---------------- ARTICHOKE (quarter of the heart; base on the left, leaves to the right) ----------------
def artichoke(seed, ang=None, W=28, H=22):
    rng = np.random.default_rng(seed + 4300)
    a = (rng.random() - .5) * 1.2 if ang is None else ang
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    u, v = axes(W, H, a)
    u = u + 1
    rad = np.hypot(u + 9, v * 1.15)                          # distance to the base of the heart
    tips = 1.1 * np.abs(np.sin(np.arctan2(v, u + 9) * 9 + seed))     # jagged leaf tips
    body = (u >= -9) & (rad <= 19 - tips) & (np.abs(v) <= (u + 9) * .62 + 1.5)
    stem = (u >= -13) & (u < -8.5) & (np.abs(v) <= 1.8)
    mask = body | stem
    layer = (rad % 3.4) < .9                                 # lines between layers of leaves
    height = np.clip(1 - (v / ((u + 9) * .62 + 2)) ** 2, 0, 1) * 1.3 + np.where(layer, -.4, 0)
    def m(y, x):
        if stem[y, x] and not body[y, x]: return 'artstem'
        r_ = rad[y, x]
        if r_ < 6.5: return 'artheart'
        if r_ < 9: return 'artchoke' if abs(v[y, x]) < 2.5 else 'artheart'   # purplish hairs in the centre
        if r_ < 12.5: return 'artheart' if not layer[y, x] else 'artleaf'
        return 'artleaf'
    mat = [[m(y, x) if mask[y, x] else 'artleaf' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .8 + .24, 0, 1) * mask, mask,
                  {'artheart': 'artleaf', 'artchoke': 'artleaf', 'artstem': 'artstem'})

# ---------------- COURGETTE (slice) ----------------
def zucchini(seed, D=18):
    rng = np.random.default_rng(seed + 4400)
    ys, xs, c, _ = grid(D, D)
    sq = 1 + (rng.random() - .5) * .14
    r = np.hypot((xs - c) * sq, (ys - c) / sq) / (D / 2 - .4)
    mask = r <= 1
    n = noise(D, D, 2, rng)
    height = np.clip(1 - r ** 2, 0, 1) ** .4 * 1.1 + (n - .5) * .3
    seeds = (np.abs(r - .42) < .08) & (rng.random((D, D)) > .55)
    speck = rng.random((D, D)) > .75
    mat = [['zucskin' if r[y, x] > .84 else 'zuc' for x in range(D)] for y in range(D)]
    light = np.clip(shade(height, mask) * .75 + .3 - np.where(seeds, .2, 0) + np.where((r > .84) & speck, .35, 0), 0, 1) * mask
    return render(mat, light, mask, {'zuc': 'zucskin'})

# ---------------- ITALIAN SAUSAGE (crumbly piece, with fennel seeds) ----------------
def sausage(seed, W=18, H=16):
    rng = np.random.default_rng(seed + 4500)
    ys, xs, cx, cy = grid(W, H)
    mask = np.zeros((H, W), bool); height = np.zeros((H, W))
    for _ in range(4):                                       # pieces stuck together
        bx, by = cx + (rng.random() - .5) * 7, cy + (rng.random() - .5) * 5
        rr = np.hypot((xs - bx) / (3 + rng.random() * 1.6), (ys - by) / (2.6 + rng.random() * 1.4))
        m = rr <= 1
        mask |= m; height = np.maximum(height, np.where(m, np.sqrt(np.clip(1 - rr ** 2, 0, 1)) * 1.8, 0))
    height += (rng.random((H, W)) - .5) * .5                 # grainy texture
    mat = [['sals'] * W for _ in range(H)]
    img = render(mat, np.clip(shade(height, mask) * .85 + .2, 0, 1) * mask, mask, {})
    px = img.load()
    for _ in range(5):                                       # fennel seeds: little light streaks
        x, y = int(rng.integers(1, W - 2)), int(rng.integers(1, H - 1))
        if mask[y, x] and mask[y, x + 1]:
            px[x, y] = R['fennel'][2] + (255,); px[x + 1, y] = R['fennel'][1] + (255,)
    return img

# ---------------- PADRÓN PEPPER (whole and charred; stem on the left, tip on the right) ----------------
def padron(seed, L=22, ang=None):
    rng = np.random.default_rng(seed + 4600)
    a = (rng.random() - .5) * .9 if ang is None else ang
    W, H = L + 4, int(np.ceil(L * abs(np.sin(a)) + 10 * abs(np.cos(a)))) + 6
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    u, v = axes(W, H, a)
    t = (u + L / 2 - 3) / (L - 3)                           # 0 at the stem, 1 at the tip
    vv = v - .8 * np.sin(t * 2.6 + seed)
    tc = np.clip(t, 0, 1)
    half = 4.3 * np.sqrt(np.clip(1 - tc ** 2.6, 0, 1)) * np.clip(.55 + tc * 3, 0, 1) + .3   # shoulder by the stem, round tip
    body = (t >= 0) & (t <= 1) & (np.abs(vv) <= half)
    stem = (u >= -L / 2 - 1) & (u < -L / 2 + 3.5) & (np.abs(v - .8 * np.sin(seed)) <= 1.2)
    mask = body | stem
    wrinkle = np.sin(t * 9 + vv * .6) * .3                   # wrinkled skin, only in the light
    height = np.clip(1 - (vv / (half + .01)) ** 2, 0, 1) * 1.8 + wrinkle
    blister = (rng.random((H, W)) > .93) & body & (np.abs(vv) < half - 1)     # a few charred blisters
    shine = body & (np.abs(vv + half * .45) < .6) & (t > .15) & (t < .75)     # lengthwise shine
    mat = [['stem' if stem[y, x] and not body[y, x] else 'char' if blister[y, x] else 'padron' for x in range(W)] for y in range(H)]
    light = np.clip(shade(height, mask) * .8 + .22 + np.where(shine, .45, 0), 0, 1) * mask
    return render(mat, light, mask, {'char': 'padron', 'stem': 'stem'})

# ---------------- PINE NUTS (handful of toasted kernels) ----------------
def pinenuts(seed, W=17, H=15):
    rng = np.random.default_rng(seed + 4700)
    ys, xs, cx, cy = grid(W, H)
    mask = np.zeros((H, W), bool); height = np.zeros((H, W))
    spots = [(-4.5, -3), (.5, -3.5), (5, -1.5), (-2, 1.5), (3, 3), (-5.5, 3.5)]
    rng.shuffle(spots)
    for ox, oy in spots[:5]:
        a = rng.random() * 3.14
        uu = (xs - cx - ox) * np.cos(a) + (ys - cy - oy) * np.sin(a)
        ww = -(xs - cx - ox) * np.sin(a) + (ys - cy - oy) * np.cos(a)
        e = (uu / 2.8) ** 2 + (ww / (1.6 - uu * .12)) ** 2     # elongated drop
        m = (e <= 1) & ~mask
        mask |= m; height = np.where(m, np.sqrt(np.clip(1 - e, 0, 1)) * 1.6, height)
    mat = [['pine'] * W for _ in range(H)]
    return render(mat, np.clip(shade(height, mask) * .8 + .25, 0, 1) * mask, mask, {})

SETS = [
    ('Parmesão', parmesan, ('parm', 'shred', 40)),
    ('Alcachofra', artichoke, ('artheart', 'flake', 40)),
    ('Curgete', zucchini, ('zuc', 'flake', 40)),
    ('Salsicha', sausage, ('sals', 'cube', 11)),
    ('Padrón', padron, ('padron', 'flake', 40)),
    ('Pinhões', pinenuts, None),
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
        key = name.lower().replace('ã', 'a').replace('õ', 'o').replace('ó', 'o')
        arr = [fn(s) for s in (1, 2, 3)]
        g = grated(gr[0], 100 + i, gr[1], n_bits=gr[2]) if gr else None
        for j, im in enumerate(arr): im.save(f'{OUT}{key}_{j + 1}.png')
        if g: g.save(f'{OUT}{key}_picado.png')
        y = 36 + i * ROW
        dr.text((20, y + 4), name, fill=(240, 220, 180), font=f)
        x = 150
        for im in arr + ([g] if g else []):
            if im is g: x = 760
            d = drop(im); K = 6 if (d.width * 6 <= 186 and d.height * 6 <= ROW - 14) else 4
            m = d.resize((d.width * K, d.height * K), Image.NEAREST)
            bg = Image.new('RGB', (190, ROW - 12), (196, 52, 28))
            bg.paste(m, ((190 - m.width) // 2, (ROW - 12 - m.height) // 2), m)
            sheet.paste(bg, (x, y)); x += 200
        if not g:
            dr.text((770, y + 60), 'already small\n(not chopped)', fill=(200, 180, 150), font=fs)
    sheet.save(OUT + 'preview_ingredientes9.png')
    print('ok', sheet.size)
