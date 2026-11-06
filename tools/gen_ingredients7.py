#!/usr/bin/env python3
"""Pizza Magna: seventh batch in detailed pixel art. Goat's cheese, garlic, turnip greens, sardine,
smoked salmon and octopus, with the chopped form following the rule in docs/ingredients.md.
Same method as gen_ingredients.py.

Pieces with a front (sardine, octopus tentacle) take `ang`: with ang=0 they lie down,
with the front to the right, and the game turns that image in quarter turns.
Usage: python3 tools/gen_ingredients7.py <folder>"""
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
    'goat': hexs(['#b8b2a2', '#dcd8cc', '#f0eee6', '#fbfaf6', '#ffffff']),
    'goatrind': hexs(['#8a8678', '#aca898', '#cfccbe', '#e6e4da']),
    'goattoast': hexs(['#9a6a34', '#c48c4c', '#dfac68']),
    'garlic': hexs(['#b8a888', '#d8ccae', '#eee6cc', '#faf6e6', '#fffef6']),
    'garlicc': hexs(['#d8cc8a', '#ece2a8', '#f8f2cc']),
    'grelo': hexs(['#0e3410', '#1a5018', '#2a6e24', '#428e34', '#6eb050']),
    'grelostem': hexs(['#2e5a20', '#4e8236', '#78a854', '#a4c87c']),
    'bud': hexs(['#5a6a14', '#8a9a1e', '#b8c234', '#dce060']),
    'sardback': hexs(['#0e1c22', '#1a3238', '#2a4c50', '#40686a', '#64908c']),
    'sardbelly': hexs(['#7e8288', '#a8acb4', '#ccd0d6', '#eef0f2']),
    'sardchar': hexs(['#140a06', '#2e1a0e', '#4a2c16']),
    'salmon': hexs(['#8a2e14', '#c04a22', '#e8703a', '#f8945a', '#ffbc8a']),
    'salmfat': hexs(['#e8b090', '#f8d4bc', '#fff0e2']),
    'octo': hexs(['#3a0a1a', '#6a1a2e', '#9a2e44', '#c44e5e', '#e27c84']),
    'sucker': hexs(['#c49088', '#e2b8ae', '#f6dcd4', '#fff4f0']),
})

# ---------------- GOAT'S CHEESE (round slice with a white rind) ----------------
def goat(seed, D=20):
    rng = np.random.default_rng(seed + 3000)
    ys, xs, c, _ = grid(D, D)
    ang = np.arctan2(ys - c, xs - c)
    r = np.hypot(xs - c, ys - c) / (D / 2 - .4) / (1 + .03 * np.sin(ang * 4 + seed))
    mask = r <= 1
    n = noise(D, D, 2, rng)
    height = np.clip(1 - r ** 2, 0, 1) ** .4 * 1.5 + (n - .5) * .5
    toast = (n > .78) & (r < .7)                              # toasted spots from the oven
    mat = [['goatrind' if r[y, x] > .8 else 'goattoast' if toast[y, x] else 'goat' for x in range(D)] for y in range(D)]
    return render(mat, np.clip(shade(height, mask) * .7 + .3, 0, 1) * mask, mask, {'goat': 'goatrind', 'goattoast': 'goatrind'})

# ---------------- GARLIC (two thin slivers) ----------------
def garlic(seed, W=17, H=14):
    rng = np.random.default_rng(seed + 3100)
    ys, xs, cx, cy = grid(W, H)
    mask = np.zeros((H, W), bool); height = np.zeros((H, W)); core = np.zeros((H, W), bool)
    for k in range(2):
        ox, oy = cx + (k - .5) * 5 + rng.random() - .5, cy + (k - .5) * 3 + rng.random() - .5
        a = rng.random() * 3.14
        u = (xs - ox) * np.cos(a) + (ys - oy) * np.sin(a); v = -(xs - ox) * np.sin(a) + (ys - oy) * np.cos(a)
        e = (u / 4.6) ** 2 + (np.maximum(v, -1.8 + u * u * .04) / 3.2) ** 2          # sliver with one flat side
        m = (e <= 1) & (v >= -2.2 + u * u * .05)
        if k == 1: mask &= ~m                                  # the top one covers the bottom one
        mask |= m
        height = np.where(m, np.sqrt(np.clip(1 - e, 0, 1)) * .9 + k * .3, height)
        core = np.where(m, (np.abs(v - .4) < .7) & (np.abs(u) < 3), core)
    mat = [['garlicc' if core[y, x] else 'garlic' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .6 + .38, 0, 1) * mask, mask, {'garlicc': 'garlic'})

# ---------------- TURNIP GREENS (stalk with leaves and flower buds) ----------------
def grelos(seed, W=28, H=22):
    rng = np.random.default_rng(seed + 3200)
    u, v = axes(W, H, (rng.random() - .5) * 1.4)
    vv = v - .6 * np.sin(u * .2 + seed)
    stem = (np.abs(vv) <= 1.1) & (u >= -12) & (u <= 8)
    leaves = np.zeros_like(stem); lh = np.zeros_like(u)
    for (lu, side, sz) in ((-4, 1, 1), (2, -1, .9), (-9, -1, .7)):
        a = side * .7
        pu, pv = u - lu, vv - side * 4.2 * sz
        qu = pu * np.cos(a) + pv * np.sin(a); qv = -pu * np.sin(a) + pv * np.cos(a)
        e = (qu / (5.2 * sz)) ** 2 + (qv / (2.6 * sz)) ** 2
        leaves |= e <= 1; lh = np.maximum(lh, np.sqrt(np.clip(1 - e, 0, 1)) * 1.3)
    buds = np.zeros_like(stem); bh = np.zeros_like(u)
    for k in range(6):
        bu, bv = 9.5 + rng.random() * 3, (rng.random() - .5) * 5
        e = ((u - bu) ** 2 + (vv - bv) ** 2) / 2.0
        buds |= e <= 1; bh = np.maximum(bh, np.sqrt(np.clip(1 - e, 0, 1)) * 1.6)
    mask = stem | leaves | buds
    height = np.maximum.reduce([np.where(stem, 1.0, 0), lh, bh + .4 * buds])
    mat = [['bud' if buds[y, x] else 'grelo' if leaves[y, x] else 'grelostem' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .8 + .22, 0, 1) * mask, mask, {'grelostem': 'grelo', 'bud': 'bud'})

# ---------------- SARDINE (grilled, head on the left, tail on the right) ----------------
def sardine(seed, L=32, ang=None):
    rng = np.random.default_rng(seed + 3300)
    a = (rng.random() - .5) * .7 if ang is None else ang
    W, H = L + 4, int(np.ceil(L * abs(np.sin(a)) + 12 * abs(np.cos(a)))) + 8
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    u, v = axes(W, H, a)
    t = (u + L / 2) / L                                     # 0 at the snout, 1 at the tail
    vv = v - .5 * np.sin(t * 3 + seed)
    half = np.select([t < .16, t < .55, t < .86],
                     [4.6 * np.sqrt(np.clip(t / .16, 0, 1)), 4.6 + 0 * t, 4.6 - (t - .55) / .31 * 3.6], 1.0)
    body = (t >= 0) & (t <= .88) & (np.abs(vv) <= half)
    fork = (t > .84) & (t <= 1) & (np.abs(np.abs(vv) - (t - .84) * 30) <= 1.5)
    mask = body | fork
    height = np.clip(1 - (vv / (half + .01)) ** 2, 0, 1) * 1.7
    gill = body & (np.abs(t - .19 - (vv / 4.6) ** 2 * .05) < .55 / L)
    char = body & (((u * .9 - vv * .6 + 40) % 6.5) < 1.1) & (t > .22) & (t < .82)   # grill marks
    def m(y, x):
        if fork[y, x] and not body[y, x] or gill[y, x]: return 'sardback'
        if char[y, x]: return 'sardchar'
        return 'sardback' if vv[y, x] < -.6 else 'sardbelly'
    mat = [[m(y, x) if mask[y, x] else 'sardback' for x in range(W)] for y in range(H)]
    img = render(mat, np.clip(shade(height, mask) * .8 + .24, 0, 1) * mask, mask,
                 {'sardbelly': 'sardback', 'sardchar': 'sardback'})
    ca, sa = np.cos(a), np.sin(a); cx, cy = (W - 1) / 2, (H - 1) / 2
    def at(uu, ww):
        ww = ww + .5 * np.sin((uu + L / 2) / L * 3 + seed)
        return int(round(cx + uu * ca - ww * sa)), int(round(cy + uu * sa + ww * ca))
    px = img.load()
    for (du, dw, col) in ((0, 0, (10, 10, 14, 255)), (1, 0, (10, 10, 14, 255)), (0, -1, (236, 240, 244, 255))):
        x, y = at(-L / 2 + .09 * L + du, -1.4 + dw)
        if 0 <= x < W and 0 <= y < H and mask[y, x]: px[x, y] = col
    return img

# ---------------- SMOKED SALMON (folded slice with veins of fat) ----------------
def salmon(seed, W=28, H=20):
    rng = np.random.default_rng(seed + 3400)
    u, v = axes(W, H, (rng.random() - .5) * 1.0)
    ph = rng.random() * 6.28
    vv = v - 1.2 * np.sin(u * .32 + ph)                     # wavy slice, like a folded ribbon
    half = 5.6 + .7 * np.sin(u * .5 + ph)
    mask = (np.abs(vv) <= half) & (np.abs(u) <= 12)
    n = noise(H, W, 3, rng)
    height = 1.1 * np.cos(u * .32 + ph) + np.clip(1 - (vv / half) ** 2, 0, 1) * 1.1 + (n - .5) * .4
    streak = np.abs((u * .8 - vv * 1.2 + np.sin(vv * .5) * 1.2 + 40) % 4.4 - 2.2) < .5   # diagonal stripes of fat
    mat = [['salmfat' if mask[y, x] and streak[y, x] else 'salmon' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .8 + .22, 0, 1) * mask, mask, {'salmfat': 'salmon'})

# ---------------- OCTOPUS (curled tentacle, tip turned inwards) ----------------
def octopus(seed, D=24, ang=None):
    rng = np.random.default_rng(seed + 3500)
    a = rng.random() * 6.28 if ang is None else ang
    ys, xs, c, _ = grid(D, D)
    best = np.full((D, D), 9.0); along = np.zeros((D, D)); side = np.zeros((D, D))
    S = np.linspace(0, 1, 120)
    pts = []
    for s in S:                                             # spiral: thick at the base, thin and curled at the tip
        th = a + s * 1.75 * np.pi
        rho = 8.2 * (1 - .62 * s)
        w = 3.4 * (1 - .78 * s) + .55
        px_, py_ = c - 1 + np.cos(th) * rho, c + np.sin(th) * rho
        pts.append((s, th, rho, w, px_, py_))
        d = np.hypot(xs - px_, ys - py_) / w
        upd = d < best
        best = np.where(upd, d, best); along = np.where(upd, s, along)
        # inner side of the spiral: where the suckers go
        side = np.where(upd, (xs - px_) * -np.cos(th) + (ys - py_) * -np.sin(th), side)
    mask = best <= 1
    height = np.sqrt(np.clip(1 - best ** 2, 0, 1)) * 1.8
    mat = [['octo'] * D for _ in range(D)]
    img = render(mat, np.clip(shade(height, mask) * .85 + .2, 0, 1) * mask, mask, {})
    pxl = img.load()
    for (s, th, rho, w, px_, py_) in pts[4:100:9]:          # suckers: light dots on the inner side
        x = int(round(px_ - np.cos(th) * w * .55)); y = int(round(py_ - np.sin(th) * w * .55))
        if 0 <= x < D and 0 <= y < D and mask[y, x]:
            pxl[x, y] = R['sucker'][2] + (255,)
            if w > 2.4 and x + 1 < D and mask[y, x + 1]: pxl[x + 1, y] = R['sucker'][1] + (255,)
    return img

SETS = [
    ('Queijo de cabra', goat, ('goat', 'flake', 40)),
    ('Alho', garlic, ('garlic', 'flake', 36)),
    ('Grelos', grelos, ('grelo', 'flake', 44)),
    ('Sardinha', sardine, ('sardback', 'chunk', 9)),
    ('Salmão fumado', salmon, ('salmon', 'chunk', 9)),
    ('Polvo', octopus, ('octo', 'cube', 11)),
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
        key = name.lower().replace(' ', '_').replace('ã', 'a')
        arr = [fn(s) for s in (1, 2, 3)]
        g = grated(gr[0], 80 + i, gr[1], n_bits=gr[2])
        for j, im in enumerate(arr): im.save(f'{OUT}{key}_{j + 1}.png')
        g.save(f'{OUT}{key}_picado.png')
        y = 36 + i * ROW
        dr.text((20, y + 4), name.replace(' de ', '\nde ').replace(' fumado', '\nfumado'), fill=(240, 220, 180), font=f)
        x = 150
        for im in arr + [g]:
            if im is g: x = 760
            d = drop(im); K = 6 if (d.width * 6 <= 186 and d.height * 6 <= ROW - 14) else 4
            m = d.resize((d.width * K, d.height * K), Image.NEAREST)
            bg = Image.new('RGB', (190, ROW - 12), (196, 52, 28))
            bg.paste(m, ((190 - m.width) // 2, (ROW - 12 - m.height) // 2), m)
            sheet.paste(bg, (x, y)); x += 200
    sheet.save(OUT + 'preview_ingredientes7.png')
    print('ok', sheet.size)
