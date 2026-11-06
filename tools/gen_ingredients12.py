#!/usr/bin/env python3
"""Pizza Magna: twelfth batch in detailed pixel art. Provolone, minced beef, red onion,
rosemary, apple and potato sticks, with the chopped form following the rule in docs/ingredients.md.
Same method as gen_ingredients.py (see tools/CLAUDE.md).

Pieces with a front (rosemary sprig, apple slice) take `ang`: with ang=0 they lie down,
with the front to the right, and the game turns that image in quarter turns.
Potato sticks are already small and aren't chopped.
Usage: python3 tools/gen_ingredients12.py <folder>"""
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
    'prov': hexs(['#b09a5a', '#d2be7e', '#e8d8a2', '#f6ecc8', '#fffbe8']),
    'provrind': hexs(['#7a5a14', '#a47a22', '#c89a36', '#e2b852']),
    'beef': hexs(['#2e140a', '#4a2212', '#6a361e', '#8a4e2e', '#ac6c44']),
    'redon': hexs(['#3e0a2e', '#62124a', '#8a2468', '#b0408a', '#d070a8']),
    'redonw': hexs(['#a8789a', '#c89ab8', '#e2bcd4', '#f4dcea']),
    'rosem': hexs(['#142418', '#22382a', '#34503c', '#4e6c54', '#7a9a7e']),
    'rosestem': hexs(['#3a2a1a', '#5a4428', '#7a603a']),
    'apple': hexs(['#c4b47a', '#e0d29e', '#f2eacc', '#fcf8ea']),
    'appleskin': hexs(['#4a0808', '#7e1612', '#b02818', '#d84a30', '#f07a5a']),
    'appleseed': hexs(['#2a1208', '#4a2410', '#6a3a1a']),
    'straw': hexs(['#8a5a10', '#b8801c', '#dca434', '#f4c85a', '#ffe69a']),
})

# ---------------- PROVOLONE (smooth round slice with a wax rind) ----------------
def provolone(seed, D=21):
    rng = np.random.default_rng(seed + 6000)
    ys, xs, c, _ = grid(D, D)
    ang = np.arctan2(ys - c, xs - c)
    r = np.hypot(xs - c, ys - c) / (D / 2 - .4) / (1 + .025 * np.sin(ang * 3 + seed))
    mask = r <= 1
    n = noise(D, D, 3, rng)
    height = np.clip(1 - r ** 2, 0, 1) ** .3 * 1.0 + (n - .5) * .2       # smooth: almost no texture
    mat = [['provrind' if r[y, x] > .88 else 'prov' for x in range(D)] for y in range(D)]
    img = render(mat, np.clip(shade(height, mask) * .6 + .36, 0, 1) * mask, mask, {'prov': 'provrind'})
    px = img.load()
    for (dx, dy) in ((-4, -4), (-3, -4), (-4, -3)):            # shine of the smooth surface
        px[int(c + dx), int(c + dy)] = R['prov'][4] + (255,)
    return img

# ---------------- MINCED BEEF (handful of cooked meat crumbs) ----------------
def minced_beef(seed, W=19, H=16):
    rng = np.random.default_rng(seed + 6100)
    ys, xs, cx, cy = grid(W, H)
    mask = np.zeros((H, W), bool); height = np.zeros((H, W))
    for _ in range(8 + seed % 3):                             # small loose lumps
        bx, by = cx + (rng.random() - .5) * 11, cy + (rng.random() - .5) * 8
        rr = np.hypot((xs - bx) / (1.6 + rng.random() * 1.2), (ys - by) / (1.4 + rng.random() * 1.0))
        m = rr <= 1
        mask |= m; height = np.maximum(height, np.where(m, np.sqrt(np.clip(1 - rr ** 2, 0, 1)) * 1.6, 0))
    height += (rng.random((H, W)) - .5) * .7                  # grain of the meat
    mat = [['beef'] * W for _ in range(H)]
    return render(mat, np.clip(shade(height, mask) * .9 + .16, 0, 1) * mask, mask, {})

# ---------------- RED ONION (ring arcs: purple edge, pale inside) ----------------
def red_onion(seed, D=24):
    rng = np.random.default_rng(seed + 6200)
    ys, xs, c, _ = grid(D, D)
    r = np.hypot(xs - c, ys - c); ang = np.arctan2(ys - c, xs - c)
    a0 = rng.random() * 6.28
    mask = np.zeros((D, D), bool); height = np.zeros((D, D)); outer = np.zeros((D, D), bool)
    for rr, span in ((10.4, 4.4), (7.3, 3.6), (4.4, 2.6)):    # concentric rings, in an arc
        da = np.angle(np.exp(1j * (ang - a0 - rng.random() * .6)))
        m = (np.abs(r - rr) <= 1.3) & (np.abs(da) <= span / 2)
        mask |= m; height = np.maximum(height, np.where(m, 1.5 - np.abs(r - rr), 0))
        outer |= m & (r - rr > -.2)                           # the purple skin is on the outside of each ring
    mat = [['redon' if outer[y, x] else 'redonw' for x in range(D)] for y in range(D)]
    return render(mat, np.clip(shade(height, mask) * .7 + .3, 0, 1) * mask, mask, {'redonw': 'redon'})

# ---------------- ROSEMARY (sprig of needles; stem on the left, tip on the right) ----------------
def rosemary(seed, L=24, ang=None):
    rng = np.random.default_rng(seed + 6300)
    a = (rng.random() - .5) * 1.0 if ang is None else ang
    W, H = L + 4, int(np.ceil(L * abs(np.sin(a)) + 12 * abs(np.cos(a)))) + 4
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    u, v = axes(W, H, a)
    vv = v - .5 * np.sin(u * .18 + seed)
    stem = (np.abs(vv) <= .6) & (u >= -L / 2) & (u <= L / 2 - 1)
    needles = np.zeros_like(stem); nh = np.zeros_like(u)
    for k, nu in enumerate(np.arange(-L / 2 + 3, L / 2 - 1, 1.6)):
        ln = 4.2 - (nu + L / 2) / L * 1.8                     # shorter needles towards the tip
        for side in (-1, 1):
            # needle: a narrow strip leaving the stem, slanted towards the tip
            pu, pv = u - nu, vv * side
            t = pv / ln
            on = (t >= .05) & (t <= 1) & (np.abs(pu - pv * .55) <= .55 + .25 * (1 - t))
            needles |= on; nh = np.maximum(nh, np.where(on, 1.1 - t * .4, 0))
    mask = stem | needles
    height = np.maximum(np.where(stem, .5, 0), nh)
    mat = [['rosem' if needles[y, x] else 'rosestem' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .8 + .26, 0, 1) * mask, mask, {'rosestem': 'rosestem'})

# ---------------- APPLE (wedge slice; curved skin on the right, core cut on the left) ----------------
def apple(seed, ang=None, W=22, H=22):
    rng = np.random.default_rng(seed + 6400)
    a = rng.random() * 6.28 if ang is None else ang
    u, v = axes(W, H, a)
    u = u + 4
    r = np.hypot(u, v)
    core = np.hypot((u + 1.6) / 2.4, v / 3.0) <= 1            # where the core was: a notch
    mask = (r <= 9.6) & (u >= -2.2) & ~core
    skin = mask & (r > 8.2)
    seed_px = mask & (np.hypot((u - 1.6) / 1.3, (np.abs(v) - 2.0) / .8) <= 1)   # two pips by the core
    height = np.clip(1 - (r / 10) ** 2, 0, 1) ** .3 * 1.0 + np.clip((u + 2.2) / 3, 0, 1) * .4
    mat = [['appleskin' if skin[y, x] else 'appleseed' if seed_px[y, x] else 'apple' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .65 + .32, 0, 1) * mask, mask,
                  {'apple': 'apple', 'appleskin': 'appleskin', 'appleseed': 'apple'})

# ---------------- POTATO STICKS (little pile of thin golden sticks) ----------------
def straw_potato(seed, W=21, H=17):
    rng = np.random.default_rng(seed + 6500)
    rp = R['straw']
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); px = img.load()
    cx, cy = W / 2, H / 2
    for _ in range(16):
        a = rng.random() * 3.14; L = rng.uniform(5, 9)
        x0, y0 = cx + (rng.random() - .5) * 11, cy + (rng.random() - .5) * 8
        pts = [(x0 + np.cos(a) * t, y0 + np.sin(a) * t * .8) for t in np.arange(-L / 2, L / 2, .5)]
        for (x, y) in pts:                                     # shadow under the stick
            X, Y = int(round(x)), int(round(y)) + 1
            if 0 <= X < W and 0 <= Y < H and px[X, Y][3] == 0: px[X, Y] = rp[0] + (255,)
        tone = int(rng.integers(2, 4))
        for i, (x, y) in enumerate(pts):
            X, Y = int(round(x)), int(round(y))
            if 0 <= X < W and 0 <= Y < H:
                px[X, Y] = rp[tone + (1 if i % 5 == 1 else 0)] + (255,)
    return img

SETS = [
    ('Provolone', provolone, ('prov', 'shred', 40)),
    ('Carne picada', minced_beef, ('beef', 'cube', 12)),
    ('Cebola roxa', red_onion, ('redon', 'flake', 44)),
    ('Alecrim', rosemary, ('rosem', 'flake', 44)),
    ('Maçã', apple, ('apple', 'cube', 11)),
    ('Batata palha', straw_potato, None),
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
        key = name.lower().replace(' ', '_').replace('ç', 'c').replace('ã', 'a')
        arr = [fn(s) for s in (1, 2, 3)]
        g = grated(gr[0], 130 + i, gr[1], n_bits=gr[2]) if gr else None
        for j, im in enumerate(arr): im.save(f'{OUT}{key}_{j + 1}.png')
        if g: g.save(f'{OUT}{key}_picado.png')
        y = 36 + i * ROW
        dr.text((20, y + 4), name.replace(' ', '\n'), fill=(240, 220, 180), font=f)
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
    sheet.save(OUT + 'preview_ingredientes12.png')
    print('ok', sheet.size)
