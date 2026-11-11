#!/usr/bin/env python3
"""Pizza Magna: twentieth batch. A roast chicken drumstick (coxa de frango) and the whole
banana. Same method as gen_ingredients.py (see tools/CLAUDE.md).

- Drumstick: a roast leg with golden, blistered skin and the bone sticking out with its
  knob. Rotates with 4 positions; with ang=0 the bone points right. Chopped: a chunk of
  leg meat with the roast skin on one side, like the suckling pig's.
- Banana: a big whole peeled banana (about 110 px, almost as long as the pizza, smaller
  than the lobster), cream flesh on a curve (ends up with ang=0, so a row of them can make
  a smile), a blunt end on the right and a small dark tip on the left. Rotates with 4 positions.
  Chopped: the slices drawn in gen_ingredients10.py.
Usage: python3 tools/gen_ingredients20.py <folder>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from gen_ingredients import R, hexs, render, shade, noise
from gen_ingredients5 import axes
import gen_ingredients10 as G10

OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'preview')) + '/'

R.update({
    'roast': hexs(['#5a2808', '#8a4212', '#b8661e', '#dc8e34', '#f4bc62']),      # roast chicken skin
    'chkmeat': hexs(['#9a6a46', '#c08e62', '#dcb084', '#eecca2', '#f8e4c4']),    # pale leg meat
    'cbone': hexs(['#8e7c62', '#b8a888', '#dcd0b6', '#f6f0e2']),
    'banflesh': hexs(['#a08a4a', '#ccb672', '#e6d698', '#f6ecc2', '#fffae4']),   # peeled banana
    'banend': hexs(['#2a1c0c', '#4a3414', '#6e5422']),                         # stalk and tip
})

def turn(W, H, ang):
    if ang is not None and abs(np.sin(ang)) > .5: return H, W
    return W, H

# ---------------- DRUMSTICK (bone to the right) ----------------
def drumstick(seed, ang=None, L=40):
    a = 0 if ang is None else ang
    W, H = turn(L + 6, 24, ang)
    u, v = axes(W, H, a)
    rng = np.random.default_rng(seed + 6300)
    n = noise(H, W, 3, rng)
    um = u + 1                                                       # the meat sits left of centre
    bulb = np.sqrt(np.clip(1 - ((um + 8) / 10.5) ** 2, 0, 1)) * 10.5
    taper = 3.4 + 7.1 * np.clip((6 - um) / 14, 0, 1) ** 1.3
    w = np.where(um <= -8, bulb, taper) * (1 + (n - .5) * .14)
    meat = (um >= -18.5) & (um <= 6) & (np.abs(v) <= w)
    shaft = (um > 3) & (um <= 15) & (np.abs(v) <= 1.9)
    knob = (np.hypot(um - 15.5, v - 2) <= 2.6) | (np.hypot(um - 15.5, v + 2) <= 2.6)
    bonem = (shaft | knob) & ~meat
    mask = meat | bonem
    height = np.where(meat, np.sqrt(np.clip(1 - (v / (w + .3)) ** 2, 0, 1)) * (2 + np.clip(-um, 0, 10) * .25) + (n - .5) * .8, 0)
    height = np.where(bonem, 1.4 * np.sqrt(np.clip(1 - (v / 3) ** 2, 0, 1)), height)
    blister = meat & (rng.random((H, W)) < .1)                       # crisp dark spots on the skin
    shine = meat & (np.abs(v + w * .45) < 1.1) & (um < 1) & (um > -15) & (n < .62)
    mat = [['cbone' if bonem[y, x] else 'roast' for x in range(W)] for y in range(H)]
    light = np.clip(shade(height, mask) * .82 + .16 - np.where(blister, .22, 0) + np.where(shine, .35, 0), 0, 1) * mask
    return render(mat, light, mask, {'cbone': 'cbone', 'roast': 'roast'})

def drumstick_chunk(seed, W=18, H=16):
    """chopped: a chunk of leg meat with the roast skin on one side"""
    rng = np.random.default_rng(seed + 6400)
    a = rng.random() * 6.28
    u, v = axes(W, H, a)
    n = noise(H, W, 2, rng)
    mask = (np.abs(u) / 7.6) ** 4 + (np.abs(v) / 6.4) ** 4 <= 1 + (n - .5) * .3
    skin = mask & (u > 3.4 + (n - .5) * 1.4)
    fibre = np.sin(v * 2.0 + n * 3) * .35
    height = np.clip(1 - (v / 7) ** 2, 0, 1) + np.where(skin, .7 + (rng.random((H, W)) - .5) * .6, fibre)
    mat = [['roast' if skin[y, x] else 'chkmeat' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .85 + .16, 0, 1) * mask, mask, {'roast': 'roast', 'chkmeat': 'chkmeat'})

# ---------------- BANANA (whole, curved; ends up with ang=0) ----------------
def banana(seed, ang=None, L=104, T=22):
    """a whole peeled banana: cream flesh with faint long strings, a small dark tip on the left"""
    a = 0 if ang is None else ang
    SAG = 18
    W, H = turn(L + 6, T + SAG + 6, ang)
    u, v = axes(W, H, a)
    rng = np.random.default_rng(seed + 6500)
    n = noise(H, W, 3, rng)
    half = L / 2
    vv = v + SAG * (u / half) ** 2 - SAG / 2 - 1                     # a smile: the middle low, the ends up
    t = np.clip(np.abs(u) / half, 0, 1)
    w = (T / 2) * np.sqrt(np.clip(1 - t ** np.where(u > 0, 4.5, 2.6), 0, 1)) * (1 + (n - .5) * .07)   # blunt right end, rounder tip left
    body = (np.abs(u) <= half) & (np.abs(vv) <= w)
    mask = body
    vn = vv / (w + .2)                                               # -1..1 across the banana
    facet = np.abs(np.sin((vn + 1) * np.pi * 1.5)) ** .5 * .3        # the soft faces the peel leaves
    height = np.where(body, np.sqrt(np.clip(1 - vn ** 2, 0, 1)) * 5 + facet + (n - .5) * .15, 0)
    strings = body & (rng.random((H, W)) < .5) & ((np.abs(vn + .45) < .06) | (np.abs(vn - .2) < .06)) & (np.abs(u) < half - 6)
    tip = body & (u < -half + 3)                                     # the little dark point
    bruise = body & (noise(H, W, 6, np.random.default_rng(seed + 6550)) > .86) & (rng.random((H, W)) < .3)
    mat = [['banend' if tip[y, x] else 'banflesh' for x in range(W)] for y in range(H)]
    light = np.clip(shade(height, mask) * .72 + .28 - np.where(strings, .22, 0) - np.where(bruise, .15, 0), 0, 1) * mask
    return render(mat, light, mask, {'banflesh': 'banflesh', 'banend': 'banend'})

def banana_slices(seed): return G10.banana(seed)                     # chopped: the old slices

SETS = [('Coxa de frango', drumstick, drumstick_chunk), ('Banana', banana, banana_slices)]

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    from build_atlas import drop
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    ROW = 170
    sheet = Image.new('RGB', (1240, 40 + ROW * len(SETS) + 260), (27, 20, 16)); dr = ImageDraw.Draw(sheet)
    dr.text((20, 10), 'Whole (lying, turned, other seeds) / chopped', fill=(240, 220, 180), font=fs)
    for i, (name, fn, gr) in enumerate(SETS):
        y = 36 + i * ROW; x = 20
        for im in [fn(1, ang=0), fn(2, ang=np.pi / 2), fn(3), gr(41), gr(58)]:
            d = drop(im); K = 4
            m = d.resize((d.width * K, d.height * K), Image.NEAREST)
            bg = Image.new('RGB', (230, ROW - 12), (196, 52, 28))
            bg.paste(m, ((230 - m.width) // 2, (ROW - 12 - m.height) // 2), m)
            sheet.paste(bg, (x, y)); x += 240
    # a smile on a pizza-sized disc: two slices for eyes and a banana for the mouth
    y = 36 + ROW * len(SETS); K = 2
    disc = Image.new('RGBA', (170, 170), (0, 0, 0, 0)); ImageDraw.Draw(disc).ellipse((0, 0, 169, 169), fill=(196, 52, 28, 255))
    for (px, py, im) in [(55, 55, banana_slices(1)), (100, 55, banana_slices(2)), (60, 100, banana(1, ang=0))]:
        d = drop(im); disc.alpha_composite(d, (px, py))
    sheet.paste(disc.resize((340, 340), Image.NEAREST).crop((0, 0, 340, 250)), (20, y), disc.resize((340, 340), Image.NEAREST).crop((0, 0, 340, 250)))
    sheet.save(OUT + 'preview_ingredientes20.png'); print('ok', sheet.size)
