#!/usr/bin/env python3
"""Pizza Magna: fourteenth batch in detailed pixel art, closing the original list. Emmental,
Edam, kebab, thyme, black pepper, quince paste and truffle, with the chopped form following the rule in
docs/ingredients.md. Same method as gen_ingredients.py (see tools/CLAUDE.md).

The thyme sprig has a front and takes `ang`: with ang=0 it lies down with the tip to the
right, and the game turns that image in quarter turns.
Usage: python3 tools/gen_ingredients14.py <folder>"""
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
    'emm': hexs(['#a8904a', '#ccb46a', '#e4d08c', '#f4e6b0', '#fff6d6']),
    'flam': hexs(['#b4801c', '#d6a032', '#ecbe50', '#f8d878', '#fff0a8']),
    'flamwax': hexs(['#5e0a0a', '#8e1612', '#b8261c', '#dc4a34']),
    'kebab': hexs(['#3a1a0a', '#5e2e14', '#844822', '#a86636', '#c88a52']),
    'thyme': hexs(['#1a2e1a', '#2a4428', '#3e5e38', '#5a7c4e', '#82a070']),
    'thymestem': hexs(['#3a2a1a', '#5a4228', '#7a5e3a']),
    'pepcorn': hexs(['#0e0a08', '#1e1814', '#342a22', '#4e4234', '#6e604c']),
    'quince': hexs(['#6a1a0a', '#9a2e12', '#c24a1e', '#e06e30', '#f49a56']),
    'truf': hexs(['#120c0a', '#221812', '#34261c', '#4a382a', '#64503c']),
    'trufvein': hexs(['#6a5c4c', '#8e7e6a', '#b0a08a']),
})

# ---------------- EMMENTAL (slice with big holes you can see through) ----------------
def emmental(seed, W=24, H=21):
    rng = np.random.default_rng(seed + 7200)
    u, v = axes(W, H, (rng.random() - .5) * .9)
    n = noise(H, W, 3, rng)
    mask = (np.abs(u) / 10) ** 4 + (np.abs(v) / 8.2) ** 4 <= 1 + (n - .5) * .2
    holes = np.zeros_like(mask); rims = np.zeros_like(mask)
    for _ in range(4):                                        # holes: real holes in the slice
        hu, hv, hr = rng.uniform(-6, 6), rng.uniform(-5, 5), rng.uniform(1.6, 2.6)
        d = np.hypot(u - hu, v - hv)
        holes |= d <= hr; rims |= (d > hr) & (d <= hr + 1.1)
    mask &= ~holes
    height = np.clip(1 - (v / 9) ** 2, 0, 1) * .5 + (n - .5) * .2 - np.where(rims, .5, 0)
    mat = [['emm'] * W for _ in range(H)]
    return render(mat, np.clip(shade(height, mask) * .7 + .32, 0, 1) * mask, mask, {})

# ---------------- EDAM (smooth round slice with a red wax rind) ----------------
def flamengo(seed, D=20):
    rng = np.random.default_rng(seed + 7300)
    ys, xs, c, _ = grid(D, D)
    r = np.hypot(xs - c, ys - c) / (D / 2 - .4)
    mask = r <= 1
    n = noise(D, D, 3, rng)
    height = np.clip(1 - r ** 2, 0, 1) ** .3 + (n - .5) * .15
    mat = [['flamwax' if r[y, x] > .87 else 'flam' for x in range(D)] for y in range(D)]
    img = render(mat, np.clip(shade(height, mask) * .6 + .36, 0, 1) * mask, mask, {'flam': 'flam', 'flamwax': 'flamwax'})
    px = img.load()
    for _ in range(3):                                        # tiny eyes
        x, y = int(c + (rng.random() - .5) * 9), int(c + (rng.random() - .5) * 9)
        if mask[y, x]: px[x, y] = R['flam'][1] + (255,)
    return img

# ---------------- KEBAB (thin shavings cut from the spit) ----------------
def kebab(seed, W=22, H=18):
    rng = np.random.default_rng(seed + 7400)
    ys, xs, cx, cy = grid(W, H)
    mask = np.zeros((H, W), bool); height = np.zeros((H, W)); edge = np.zeros((H, W), bool)
    for k in range(3):                                        # three overlapping, curled shavings
        a = rng.random() * 3.14
        ox, oy = cx + (rng.random() - .5) * 7, cy + (rng.random() - .5) * 5
        uu = (xs - ox) * np.cos(a) + (ys - oy) * np.sin(a); vv = -(xs - ox) * np.sin(a) + (ys - oy) * np.cos(a)
        vv = vv - .8 * np.sin(uu * .5 + k)
        e = (uu / 7.5) ** 2 + (vv / 2.6) ** 2
        m = e <= 1
        top = m & ~mask if k else m
        mask |= m
        height = np.where(m, np.sqrt(np.clip(1 - e, 0, 1)) * 1.2 + k * .3 + np.sin(uu * 1.4) * .2, height)
        edge = np.where(m, e > .55, edge)                     # toasted edge of each shaving
    mat = [['kebab'] * W for _ in range(H)]
    light = np.clip(shade(height, mask) * .8 + .24 - np.where(edge, .3, 0), 0, 1) * mask
    return render(mat, light, mask, {})

# ---------------- THYME (woody sprig with tiny round leaves; tip on the right) ----------------
def thyme(seed, L=22, ang=None):
    """different from oregano (bigger oval leaves) and rosemary (needles): many 1-2 px leaves"""
    rng = np.random.default_rng(seed + 7500)
    a = (rng.random() - .5) * 1.0 if ang is None else ang
    W, H = L + 4, int(np.ceil(L * abs(np.sin(a)) + 9 * abs(np.cos(a)))) + 4
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    u, v = axes(W, H, a)
    vv = v - .5 * np.sin(u * .25 + seed)
    stem = (np.abs(vv) <= .55) & (u >= -L / 2) & (u <= L / 2 - 1)
    leaves = np.zeros_like(stem); lh = np.zeros_like(u)
    for k, lu in enumerate(np.arange(-L / 2 + 4, L / 2 - .5, 2.4)):
        side = 1 if k % 2 else -1                             # alternating leaves, apart from each other
        for sd, du in ((side, 0), (-side, 1.2)):
            off = 2.1 + rng.random() * .5
            e = ((u - lu - du) / 1.15) ** 2 + ((vv - sd * off) / 1.0) ** 2
            leaves |= e <= 1; lh = np.maximum(lh, np.sqrt(np.clip(1 - e, 0, 1)) * 1.2)
    mask = stem | leaves
    height = np.maximum(np.where(stem, .5, 0), lh)
    mat = [['thyme' if leaves[y, x] else 'thymestem' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .8 + .4, 0, 1) * mask, mask, {'thymestem': 'thymestem'})

# ---------------- BLACK PEPPER (black, wrinkled peppercorns) ----------------
def peppercorns(seed, W=17, H=15):
    rng = np.random.default_rng(seed + 7600)
    ys, xs, cx, cy = grid(W, H)
    mask = np.zeros((H, W), bool); height = np.zeros((H, W))
    spots = [(-4.5, -3), (.5, -3.5), (5, -1.5), (-2, 2), (3, 3), (-6, 3.5), (6.5, 3.5)]
    rng.shuffle(spots)
    for ox, oy in spots[:5 + seed % 2]:
        e = ((xs - cx - ox) ** 2 + (ys - cy - oy) ** 2) / 5.8
        m = (e <= 1) & ~mask
        mask |= m; height = np.where(m, np.sqrt(np.clip(1 - e, 0, 1)) * 2.0 + (rng.random((H, W)) - .5) * .4, height)
    mat = [['pepcorn'] * W for _ in range(H)]
    return render(mat, np.clip(shade(height, mask) * .9 + .2, 0, 1) * mask, mask, {})

# ---------------- QUINCE PASTE (translucent cube, in 3/4) ----------------
def marmelada(seed, W=17, H=17):
    rng = np.random.default_rng(seed + 7700)
    sz, d = int(rng.integers(10, 12)), 4
    x0, y0 = 1, 1
    lt = Image.new('L', (W, H), 0); dl = ImageDraw.Draw(lt)
    dl.polygon([(x0, y0 + d), (x0 + sz, y0 + d), (x0 + sz + d, y0), (x0 + d, y0)], fill=230)
    dl.rectangle([x0, y0 + d, x0 + sz - 1, y0 + d + sz - 1], fill=140)
    dl.polygon([(x0 + sz, y0 + d), (x0 + sz + d, y0), (x0 + sz + d, y0 + sz - 1), (x0 + sz, y0 + d + sz - 1)], fill=70)
    light = np.array(lt) / 255.0
    mask = light > 0
    light = light + (rng.random((H, W)) - .5) * .08            # smooth and glossy
    img = render([['quince'] * W for _ in range(H)], np.clip(light, 0, 1) * mask, mask, {})
    px = img.load()
    for (x, y) in ((x0 + 2, y0 + d + 2), (x0 + 3, y0 + d + 2), (x0 + 2, y0 + d + 3)):    # reflection on the front face
        px[x, y] = R['quince'][4] + (255,)
    return img

# ---------------- TRUFFLE (thin shaving, with white maze-like veins) ----------------
def truffle(seed, D=17):
    rng = np.random.default_rng(seed + 7800)
    ys, xs, c, _ = grid(D, D)
    ang = np.arctan2(ys - c, xs - c)
    r = np.hypot(xs - c, ys - c) / (D / 2 - .5) / (1 + .08 * np.sin(ang * 5 + seed))
    mask = r <= 1
    n = noise(D, D, 2, rng); n2 = noise(D, D, 3, rng)
    veins = (np.abs(n - .5) < .035) | (np.abs(n2 - .5) < .03)
    height = np.clip(1 - r ** 2, 0, 1) ** .4 * .6 + (n2 - .5) * .3
    mat = [['trufvein' if veins[y, x] and r[y, x] < .85 else 'truf' for x in range(D)] for y in range(D)]
    return render(mat, np.clip(shade(height, mask) * .7 + .3, 0, 1) * mask, mask, {'trufvein': 'truf'})

SETS = [
    ('Emmental', emmental, ('emm', 'shred', 40)),
    ('Flamengo', flamengo, ('flam', 'shred', 40)),
    ('Kebab', kebab, ('kebab', 'cube', 12)),
    ('Tomilho', thyme, ('thyme', 'flake', 44)),
    ('Pimenta', peppercorns, ('pepcorn', 'flake', 50)),
    ('Marmelada', marmelada, ('quince', 'cube', 11)),
    ('Trufa', truffle, ('truf', 'flake', 44)),
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
        g = grated(gr[0], 150 + i, gr[1], n_bits=gr[2])
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
    sheet.save(OUT + 'preview_ingredientes14.png')
    print('ok', sheet.size)
