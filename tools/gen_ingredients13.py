#!/usr/bin/env python3
"""Pizza Magna: thirteenth batch in detailed pixel art. São Jorge cheese, suckling pig, kale,
parsley, chocolate and sour cream, with the chopped form following the rule in docs/ingredients.md.
Same method as gen_ingredients.py (see tools/CLAUDE.md).

Pieces with a front (São Jorge wedge, suckling pig with its crackling, parsley sprig)
take `ang`: with ang=0 they lie down with the front to the right, and the game turns that image
in quarter turns. Sour cream is spread and isn't chopped.
Usage: python3 tools/gen_ingredients13.py <folder>"""
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
    'sj': hexs(['#a88a3e', '#cca85a', '#e2c47a', '#f2dc9e', '#fcf0c8']),
    'sjrind': hexs(['#6a4210', '#94621c', '#ba842e', '#d8a448']),
    'pork': hexs(['#7a4e36', '#9e6a4c', '#bc8a68', '#d4a884', '#e6c4a2']),
    'crackle': hexs(['#5a2a08', '#8a4410', '#b8681c', '#e09434', '#f8c062']),
    'porkfat': hexs(['#dccab4', '#f0e4d6', '#fdf8f0']),
    'kale': hexs(['#0e2a1e', '#18402c', '#26583c', '#3a7650', '#5e9670']),
    'kalevein': hexs(['#4e7a4c', '#7aa46e', '#a8cc96']),
    'parsley': hexs(['#0a2e0e', '#145018', '#1e7224', '#349432', '#5eb84a']),
    'parstem': hexs(['#2a5a1c', '#468430', '#6aac4a']),
    'choc': hexs(['#1a0a04', '#2e1408', '#4a2412', '#6a3a20', '#8e5634']),
    'sourcream': hexs(['#b4b0a4', '#d6d2c8', '#eceae2', '#f9f8f4', '#ffffff']),
})

# ---------------- SÃO JORGE CHEESE (wedge in 3/4; rind at the back, tip on the right) ----------------
def sao_jorge(seed, ang=None, W=24, H=20):
    rng = np.random.default_rng(seed + 6600)
    a = (rng.random() - .5) * 1.2 if ang is None else ang
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    u, v = axes(W, H, a)
    t = np.clip((u + 9) / 19, 0, 1)                           # 0 at the rind, 1 at the tip
    half = 7.2 * (1 - t) + .6
    top = (u >= -9) & (u <= 10) & (np.abs(v) <= half)
    side = (u >= -9) & (u <= 10) & (v > half) & (v <= half + 2.6 * (1 - t) + .4)   # side face, below
    mask = top | side
    rind = mask & (u < -6.8)
    holes = np.zeros_like(top)
    for _ in range(4):                                        # small eyes in the cheese
        hu, hv = rng.uniform(-5, 4), rng.uniform(-3, 3)
        holes |= np.hypot((u - hu) / 1.1, (v - hv) / .8) <= 1
    holes &= top & ~rind
    light = np.where(top, .82, .45) + (rng.random((H, W)) - .5) * .12 - np.where(holes, .45, 0)
    mat = [['sjrind' if rind[y, x] else 'sj' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(light, 0, 1) * mask, mask, {'sj': 'sjrind'})

# ---------------- SUCKLING PIG (roast piece; crisp crackling on the right) ----------------
def leitao(seed, ang=None, W=22, H=20):
    rng = np.random.default_rng(seed + 6700)
    a = (rng.random() - .5) * 1.0 if ang is None else ang
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    u, v = axes(W, H, a)
    n = noise(H, W, 2, rng)
    mask = (np.abs(u) / 9.2) ** 4 + (np.abs(v) / 7.6) ** 4 <= 1 + (n - .5) * .25
    skin = mask & (u > 4.2 + (n - .5) * 1.2)                 # crackling
    fat = mask & ~skin & (u > 2.8 + (n - .5) * 1.0)           # fat between the skin and the meat
    blister = rng.random((H, W))
    fibre = np.sin(v * 2.2 + n * 3) * .35                     # meat fibres
    height = np.clip(1 - (v / 8) ** 2, 0, 1) * 1.0 + np.where(skin, .6 + (blister - .5) * .8, fibre)
    mat = [['crackle' if skin[y, x] else 'porkfat' if fat[y, x] else 'pork' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .85 + .16, 0, 1) * mask, mask,
                  {'pork': 'pork', 'porkfat': 'pork', 'crackle': 'crackle'})

# ---------------- KALE (torn leaf piece, with veins) ----------------
def couve(seed, W=25, H=21):
    rng = np.random.default_rng(seed + 6800)
    u, v = axes(W, H, rng.random() * 6.28)
    ang = np.arctan2(v, u); a, b = rng.random(2) * 6.28
    r = np.hypot(u / 10.5, v / 8.5)
    rr = r / (1 + .1 * np.sin(ang * 5 + a) + .06 * np.sin(ang * 11 + b))   # torn, wavy edge
    mask = rr <= 1
    n = noise(H, W, 2, rng)
    crinkle = np.sin(u * 1.1 + n * 4) * np.sin(v * 1.3) * .35    # crinkled leaf
    height = np.clip(1 - rr ** 2, 0, 1) ** .5 * 1.0 + crinkle
    mid = np.abs(v + u * .12) < .6                                 # central vein
    side = (np.abs(((u - np.abs(v) * .9) % 5.5) - 2.7) < .45) & (np.abs(v) > 1) & (rr < .85)   # side veins
    mat = [['kalevein' if mask[y, x] and (mid[y, x] or side[y, x]) else 'kale' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .8 + .24, 0, 1) * mask, mask, {'kalevein': 'kale'})

# ---------------- PARSLEY (sprig of pointed leaves; stem on the left) ----------------
def parsley(seed, ang=None, W=28, H=26):
    """different from coriander: diamond leaflets with points, and a darker, glossier green"""
    rng = np.random.default_rng(seed + 6900)
    a = (rng.random() - .5) * 1.2 if ang is None else ang
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    u, v = axes(W, H, a)
    stem = (np.abs(v - (u + 12) * .03) <= .7) & (u >= -12) & (u <= 1.5)
    mask = stem.copy(); height = np.where(stem, .6, 0.)
    for (lu, lv, rr, la) in ((6, 0, 7.0, 0), (.5, -6, 5.6, -1.0), (.5, 6, 5.6, 1.0)):
        pu = (u - lu) * np.cos(la) + (v - lv) * np.sin(la)
        pv = -(u - lu) * np.sin(la) + (v - lv) * np.cos(la)
        dia = np.abs(pu) / rr + np.abs(pv) / (rr * .62)           # diamond
        teeth = .12 * np.abs(np.sin(np.arctan2(pv, pu) * 6 + seed))   # points on the edge
        m = dia <= 1 - teeth
        mask |= m; height = np.maximum(height, np.where(m, (1 - dia) * 1.6, 0))
    veins = ((np.abs(v) < .5) & (u > 1)) | ((np.abs(np.abs(v) - (u * -1.15 + .6)) < .5) & (u < .5) & (u > -5))
    mat = [['parstem' if stem[y, x] or (mask[y, x] and veins[y, x]) else 'parsley' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .9 + .18, 0, 1) * mask, mask, {'parstem': 'parsley'})

# ---------------- CHOCOLATE (broken piece of a bar, in 3/4) ----------------
def chocolate(seed, W=19, H=16):
    rng = np.random.default_rng(seed + 7000)
    cw, ch, d = int(rng.integers(12, 15)), int(rng.integers(8, 10)), 3
    x0, y0 = 1, 1
    lt = Image.new('L', (W, H), 0); dl = ImageDraw.Draw(lt)
    dl.polygon([(x0, y0 + d), (x0 + cw, y0 + d), (x0 + cw + d, y0), (x0 + d, y0)], fill=200)          # top
    dl.rectangle([x0, y0 + d, x0 + cw - 1, y0 + d + ch - 1], fill=150)                             # top face of the bar
    dl.rectangle([x0, y0 + d + ch, x0 + cw - 1, y0 + d + ch + 1], fill=60)                         # thickness (front)
    dl.polygon([(x0 + cw, y0 + d), (x0 + cw + d, y0), (x0 + cw + d, y0 + ch + 1), (x0 + cw, y0 + d + ch + 1)], fill=80)
    light = np.array(lt) / 255.0
    mask = light > 0
    gx = x0 + cw // 2                                         # grooves between the squares of the bar
    for y in range(y0 + d, y0 + d + ch):
        if mask[y, gx]: light[y, gx] = .3
        if gx + 1 < W and mask[y, gx + 1]: light[y, gx + 1] = .75
    gy = y0 + d + ch // 2
    for x in range(x0, x0 + cw):
        if mask[gy, x]: light[gy, x] = .3
        if mask[gy + 1, x]: light[gy + 1, x] = .75
    edge = mask & ~(np.roll(mask, 1, 1) & np.roll(mask, -1, 1))
    broken = rng.random((H, W)) > .55                          # one broken, irregular side
    mask &= ~(edge & broken & (np.arange(W)[None, :] < x0 + 2))
    mat = [['choc'] * W for _ in range(H)]
    return render(mat, np.clip(light, 0, 1) * mask, mask, {})

# ---------------- SOUR CREAM (spoonful with a peak, very white) ----------------
def sour_cream(seed, W=22, H=19):
    rng = np.random.default_rng(seed + 7100)
    ys, xs, cx, cy = grid(W, H)
    dx, dy = (xs - cx) / (W / 2 - 1.5), (ys - cy) / (H / 2 - 1.5)
    ang = np.arctan2(dy, dx); a, b = rng.random(2) * 6.28
    r = np.hypot(dx, dy)
    rr = r / (1 + .08 * np.sin(ang * 4 + a) + .05 * np.sin(ang * 7 + b))
    mask = rr <= 1
    px_, py_ = (rng.random() - .5) * .3, (rng.random() - .5) * .3
    peak = np.exp(-((dx - px_) ** 2 + (dy - py_) ** 2) / .06) * 1.2       # peak left by the spoon
    swirl = np.sin(ang * 2 + r * 7 + a) * .3 * np.clip(1 - rr, 0, 1)
    height = np.clip(1 - rr ** 2, 0, 1) ** .6 * 1.6 + peak + swirl
    mat = [['sourcream'] * W for _ in range(H)]
    return render(mat, np.clip(shade(height, mask) * .75 + .3, 0, 1) * mask, mask, {})

SETS = [
    ('São Jorge', sao_jorge, ('sj', 'shred', 40)),
    ('Leitão', leitao, ('pork', 'cube', 12)),
    ('Couve galega', couve, ('kale', 'shred', 40)),
    ('Salsa', parsley, ('parsley', 'flake', 44)),
    ('Chocolate', chocolate, ('choc', 'shred', 40)),
    ('Natas azedas', sour_cream, None),
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
        g = grated(gr[0], 140 + i, gr[1], n_bits=gr[2]) if gr else None
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
            dr.text((770, y + 60), 'spread\n(not chopped)', fill=(200, 180, 150), font=fs)
    sheet.save(OUT + 'preview_ingredientes13.png')
    print('ok', sheet.size)
