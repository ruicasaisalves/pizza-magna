#!/usr/bin/env python3
"""Pizza Magna: twenty-first batch. Carrot, cherry, bone-in steak, and a new green pepper.
Same method as gen_ingredients.py (see tools/CLAUDE.md).

- Carrot (cenoura): a whole carrot without its tops, the tapering orange root with rings
  across it; with ang=0 the thick end is on the right. Rotates with 4 positions.
  Chopped: one round slice, orange rim and a paler core with faint rays.
- Cherry (cereja): a whole glossy cherry with its stem curving off to the right.
  Rotates with 4 positions. Chopped: pitted halves, cut side up.
- Bone-in steak (bife com osso): a big thick grilled steak (as big as the whole beef) seen at
  three quarters, a round white spot of bone in the middle, grill marks, fat round one side
  and the seared side below. Doesn't rotate (it has a side); 3 variants. Chopped: one beef
  slice, like the beef's (gen_ingredients17.py).
- Green pepper (pimento): replaces the old arc from gen_ingredients3.py with a whole
  sliced ring, three or four lobes and pale ribs pointing in from the folds. Doesn't rotate.
Usage: python3 tools/gen_ingredients21.py <folder>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from gen_ingredients import R, hexs, render, shade, noise
from gen_ingredients2 import grated
from gen_ingredients5 import axes, erode
import gen_ingredients3 as G3                                   # the 'pepper' ramp
import gen_ingredients17 as G17                                 # 'steak', 'steakin', 'bone' and the beef slice

OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'preview')) + '/'

R.update({
    'carrot': hexs(['#7a2c06', '#b8480c', '#e06a14', '#f68e2c', '#ffb25a']),
    'carrotin': hexs(['#a85a14', '#d8801e', '#f4a23a', '#ffc464', '#ffdc96']),   # paler core
    'cherry': hexs(['#2e0208', '#5a0612', '#8e0e1e', '#c42a34', '#f07a78']),
    'cherryin': hexs(['#5a0a14', '#8e1a26', '#b83242', '#d85a64', '#f08a8e']),   # cut flesh
    'cstem': hexs(['#2e3a10', '#4e5e1c', '#76862e', '#a0aa4e']),
    'pepperib': hexs(['#5e8a3a', '#9ec46e', '#cfe6a6', '#eef6d6']),             # pale ribs inside the ring
    'pepperg': hexs(['#1a5a12', '#2e8a1e', '#4cb02c', '#7cd44a', '#b4f07a']),   # bright fresh green
    'grill': hexs(['#1e0a04', '#341408', '#4a1e0c']),                           # grill marks
    'tfat': hexs(['#a0805a', '#d0b48a', '#ecd8b2', '#fbf0d8']),                 # the fat on the steak's edge
})

def turn(W, H, ang):
    if ang is not None and abs(np.sin(ang)) > .5: return H, W
    return W, H

# ---------------- GREEN PEPPER (a sliced ring, lobed) ----------------
def pepper_ring(seed, D=27):
    rng = np.random.default_rng(seed + 6600)
    lobes = (4, 3, 4)[(seed - 1) % 3]
    ph = rng.random() * 6.28
    c = (D - 1) / 2
    ys, xs = np.mgrid[0:D, 0:D]
    dx, dy = xs - c, (ys - c) * 1.08                            # a little squashed, lying on the pizza
    r, th = np.hypot(dx, dy), np.arctan2(dy, dx)
    n = noise(D, D, 2, rng)
    wave = np.cos(lobes * th + ph)
    Ro = 11.2 + 1.5 * wave + (n - .5) * .5                      # the lobes of the outline
    T = 3.2
    wall = (r <= Ro) & (r >= Ro - T)
    # ribs: where the outline folds in (wave near -1), a pale tongue points to the centre
    fold = np.cos(lobes * th + ph) < -.9
    rib = fold & (r < Ro - T + .5) & (r >= Ro - T - 4.2 + (1 + wave) * 4)
    mask = wall | rib
    height = np.where(wall, np.sqrt(np.clip(1 - ((r - (Ro - T / 2)) / (T / 2 + .3)) ** 2, 0, 1)) * 1.8, .6)
    inner = wall & (r < Ro - T + 1)                              # the pale inside face of the wall
    mat = [['pepperib' if ((rib[y, x] and not wall[y, x]) or inner[y, x]) else 'pepperg' for x in range(D)] for y in range(D)]
    light = np.clip(shade(height, mask) * .6 + .38, 0, 1) * mask
    return render(mat, light, mask, {'pepperib': 'pepperg', 'pepperg': 'pepperg'})

# ---------------- CARROT (a round slice) ----------------
def carrot(seed, D=16):
    rng = np.random.default_rng(seed + 6700)
    c = (D - 1) / 2 + (rng.random() - .5) * .3
    ys, xs = np.mgrid[0:D, 0:D]
    th = np.arctan2(ys - c, xs - c)
    n = noise(D, D, 2, rng)
    r = np.hypot(xs - c, ys - c) / (D / 2 - .5) / (1 + (n - .5) * .08)
    mask = r <= 1
    core = r < .52 + .05 * np.cos(th * 5 + seed)
    ring = ~core & (r < .68)                                  # a darker ring around the core
    rays = core & (np.abs(np.sin(th * 3 + seed)) < .2) & (r > .15)   # faint lines from the centre
    height = np.clip(1 - r ** 6, 0, 1) * .8                   # a flat coin with a rounded edge
    mat = [['carrotin' if core[y, x] else 'carrot' for x in range(D)] for y in range(D)]
    light = np.clip(shade(height, mask) * .5 + .45 + np.where(core, .2, 0) - np.where(rays, .22, 0) - np.where(ring, .1, 0), 0, 1) * mask
    return render(mat, light, mask, {'carrotin': 'carrot', 'carrot': 'carrot'})

def carrot_whole(seed, ang=None, L=34, T=13):
    """a whole carrot: tapering orange root with rings across it, the thick end on the right"""
    a = 0 if ang is None else ang
    W, H = turn(L + 4, 16, ang)
    u, v = axes(W, H, a)
    rng = np.random.default_rng(seed + 6760)
    n = noise(H, W, 3, rng)
    x0 = -L / 2                                           # the tip, on the left
    t = np.clip((u - x0) / L, 0, 1)                              # 0 at the tip, 1 at the top of the root
    w = (T / 2) * np.clip(t * 1.05 + .04, 0, 1) ** .5 * (1 + (n - .5) * .1)
    root = (u >= x0) & (u <= x0 + L) & (np.abs(v) <= w + .3)
    cap = u > x0 + L - 5                                       # round off the thick end
    root &= ~cap | (((u - (x0 + L - 5)) / 5) ** 2 + (v / (w + .3)) ** 2 <= 1)
    rings = root & (np.abs(np.sin((u - x0) * 1.3 + n * 2)) < .22) & (t > .1)   # the little rings across the root
    mask = root
    height = np.where(root, np.sqrt(np.clip(1 - (v / (w + .4)) ** 2, 0, 1)) * 2.5, 0)
    mat = [['carrot'] * W for _ in range(H)]
    light = np.clip(shade(height, mask) * .75 + .25 - np.where(rings, .2, 0), 0, 1) * mask
    return render(mat, light, mask, {'carrot': 'carrot'})

def carrot_slice(seed): return carrot(seed, D=13)                 # chopped: one round slice

# ---------------- CHERRY (whole, stem to the right) ----------------
def cherry(seed, ang=None, D=14):
    a = 0 if ang is None else ang
    W, H = turn(D + 11, D + 4, ang)
    u, v = axes(W, H, a)
    rng = np.random.default_rng(seed + 6800)
    cu, cv = u + 5, v + 1                                     # the fruit sits left, the stem goes right
    r = np.hypot(cu, cv * 1.05) / (D / 2 - .3)
    body = r <= 1
    # the stem: from the top-right of the fruit, curving up and out to the right
    t = np.clip((u - 0) / 11, 0, 1)
    sv = -3.5 - 4 * t ** 1.6
    stem = (u >= -1) & (u <= 11) & (np.abs(v - sv) <= .8) & ~body
    dimple = body & (np.hypot(cu - 4.2, cv + 3.2) < 1.6)       # where the stem goes in
    mask = body | stem
    height = np.where(body, np.sqrt(np.clip(1 - r ** 2, 0, 1)) * 3.2 - np.where(dimple, .8, 0), np.where(stem, .8, 0))
    shine = body & (np.hypot(cu + 2.2, cv + 2.4) < 1.5)
    mat = [['cstem' if stem[y, x] else 'cherry' for x in range(W)] for y in range(H)]
    light = np.clip(shade(height, mask) * .85 + .1 + np.where(shine, .5, 0), 0, 1) * mask
    return render(mat, light, mask, {'cherry': 'cherry', 'cstem': 'cstem'})

def cherry_halves(seed, n=4, W=24, H=22, D=9):
    """chopped: pitted halves, cut side up, a dark hollow where the stone was"""
    rng = np.random.default_rng(seed + 6850)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); placed = []
    for _ in range(60):
        if len(placed) >= n: break
        x, y = int(rng.integers(0, W - D)), int(rng.integers(0, H - D))
        if any(abs(x - a) < 7 and abs(y - b) < 7 for a, b in placed): continue
        placed.append((x, y))
        ys, xs = np.mgrid[0:D, 0:D]
        r = np.hypot(xs - (D - 1) / 2, ys - (D - 1) / 2) / (D / 2 - .3)
        mask = r <= 1
        mat = [['cherry' if r[j, i] > .72 else 'cherryin' for i in range(D)] for j in range(D)]
        light = np.clip(shade((1 - r ** 2) * .5, mask) * .6 + .4 - np.where(r < .3, .5, 0), 0, 1) * mask
        img.alpha_composite(render(mat, light, mask, {'cherryin': 'cherry'}), (x, y))
    return img

# ---------------- T-BONE STEAK (bone's long arm to the right) ----------------
def bone_steak(seed, ang=None, W=44, H=36):
    """a thick grilled steak seen at three quarters, a round white spot of bone in the middle.
    It has a side, so it doesn't turn; the variants mirror it or change its proportions"""
    rng = np.random.default_rng(seed + 6900)
    flip = -1 if seed % 3 == 2 else 1
    k = 1 + (seed % 3 == 0) * .08                                # the third variant: a bit rounder
    TH = 6                                                       # thickness of the side, in px
    ys, xs = np.mgrid[0:H, 0:W].astype(float)
    fx = (xs - (W - 1) / 2) * flip
    fy = (ys - (H - TH - 1) / 2) / .74                           # the top seen from above at an angle
    n = noise(H, W, 4, rng)
    # an oval, a little fuller on the left, with a soft dip in the top edge
    d = (fx / 20) ** 2 + ((fy - fx * .08) / (16 * k)) ** 2 - .12 * np.exp(-((fx - 6) / 5) ** 2 - ((fy + 15 * k) / 4) ** 2)
    top = d <= 1 + (n - .5) * .1
    side = np.zeros_like(top)
    for dd in range(1, TH + 1): side[dd:] |= top[:-dd]
    side &= ~top
    bx, by = 1.5, -1                                             # the bone: a round dot a little off centre
    rb = np.hypot(fx - bx, (fy - by) * .74)
    bone = top & (rb <= 3.8 + (n - .5) * .8)                      # a solid white spot
    rim = top & ~erode(erode(top))
    fat = top & ~bone & ~erode(erode(top)) & (fx < 0) & (fy > -12)       # a thin band of fat round the left
    marks = top & ~bone & ~fat & (np.abs(((fx * .55 + fy * .9) % 7) - 3.5) < .75)   # parallel grill marks
    streak = side & (np.sin(fx * 1.7 + n * 4) > .35)              # the fibres on the cut side
    mask = top | side
    dome = np.clip(1 - ((fx / 22) ** 2 + (fy / 17) ** 2), 0, 1) * 3
    height = np.where(top, dome + np.where(bone, .8, 0) + (noise(H, W, 2, rng) - .5) * .4, 0)
    def m(y, x):
        if side[y, x]: return 'steak'
        if bone[y, x]: return 'bone'
        if fat[y, x]: return 'tfat'
        if marks[y, x]: return 'grill'
        return 'steak'
    mat = [[m(y, x) for x in range(W)] for y in range(H)]
    light = np.where(top, shade(height, top) * .55 + .45, .12 + np.where(streak, .16, 0))
    light = np.clip(light - np.where(rim & ~fat & ~bone, .08, 0), 0, 1) * mask
    return render(mat, light, mask, {'grill': 'grill', 'tfat': 'tfat', 'bone': 'bone', 'steak': 'steak'})

def bone_steak_slice(seed): return G17.beef_cubes(seed)              # chopped: one beef slice

SETS = [('Pimento', lambda s, ang=None: pepper_ring(s), lambda s: grated('pepper', 13 + s, 'flake', n_bits=40)),
        ('Cenoura', carrot_whole, carrot_slice),
        ('Cereja', cherry, cherry_halves),
        ('Bife com osso', bone_steak, bone_steak_slice)]

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    from build_atlas import drop
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    ROW = 200
    sheet = Image.new('RGB', (1240, 40 + ROW * len(SETS)), (27, 20, 16)); dr = ImageDraw.Draw(sheet)
    dr.text((20, 10), 'Whole (lying, turned, other seed) / chopped', fill=(240, 220, 180), font=fs)
    for i, (name, fn, gr) in enumerate(SETS):
        y = 36 + i * ROW; x = 20
        for im in [fn(1, ang=0), fn(2, ang=np.pi / 2), fn(3), gr(41), gr(58)]:
            d = drop(im); K = 4 if max(d.size) > 40 else 6
            m = d.resize((d.width * K, d.height * K), Image.NEAREST)
            bg = Image.new('RGB', (230, ROW - 12), (196, 52, 28))
            bg.paste(m, ((230 - m.width) // 2, (ROW - 12 - m.height) // 2), m)
            sheet.paste(bg, (x, y)); x += 240
    sheet.save(OUT + 'preview_ingredientes21.png'); print('ok', sheet.size)
