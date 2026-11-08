#!/usr/bin/env python3
"""Pizza Magna: seventeenth batch. Beef, lobster and ribs. Same method as
gen_ingredients.py (see tools/CLAUDE.md).

- Beef (carne de vaca): a thin seared slice, pink in the middle with a brown crust.
  Doesn't rotate. Chopped: browned cubes.
- Lobster (lagosta): one whole cooked lobster, big enough to fill the sauce disc
  (inside the crust). Rotates with 4 positions (claws one way, tail the other);
  with ang=0 the claws point right. In the game it always lands in the middle.
  Chopped: big seafood-stick chunks, white flesh with a red-orange top.
- Ribs (entrecosto): one glazed pork rib with the bone sticking out at one end.
  Rotates with 4 positions; with ang=0 the bone points right. Chopped: glazed cubes.
Usage: python3 tools/gen_ingredients17.py <folder>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from gen_ingredients import R, hexs, render, shade, noise
from gen_ingredients2 import grid
from gen_ingredients5 import axes, erode

OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'preview')) + '/'

R.update({
    'steak': hexs(['#4a1a10', '#6e2a1a', '#8e4028', '#a85a3a', '#c27a56']),        # seared crust
    'steakin': hexs(['#8e2a2e', '#b2404a', '#cc5e66', '#e08a8c', '#f0b0aa']),      # pink middle
    'lob': hexs(['#4a0c04', '#8e2a0e', '#d0521c', '#f48236', '#ffbc80']),          # cooked shell
    'lobdark': hexs(['#2e0804', '#56120a', '#7a1e10']),                           # joints and eyes
    'surimi': hexs(['#c8b8a6', '#e4d8ca', '#f6eee4', '#fffaf4']),                 # white flesh
    'surred': hexs(['#8e200e', '#c43c1c', '#e8603a', '#fa8c62']),                 # orange-red skin
    'ribglz': hexs(['#2e0e06', '#4e1a0c', '#742c14', '#9a4420', '#c06432']),       # BBQ glaze
    'bone': hexs(['#8e7c62', '#b8a888', '#dcd0b6', '#f4ecdc']),
})

def turn(W, H, ang):
    """canvas size for a piece turned to ang (W, H given lying down)"""
    if ang is not None and abs(np.sin(ang)) > .5: return H, W
    return W, H

# ---------------- BEEF (thin seared slice) ----------------
def beef(seed, W=26, H=20):
    rng = np.random.default_rng(seed + 5000)
    a = rng.random() * 3.14
    u, v = axes(W, H, a)
    n = noise(H, W, 3, rng)
    edge = 1 + (n - .5) * .22
    d = np.hypot(u / 11.5, v / 7.5) / edge
    mask = d <= 1
    rim = mask & ~erode(erode(mask))
    height = np.clip(1 - d ** 2, 0, 1) * 1.3 + (noise(H, W, 2, rng) - .5) * .5   # a slice with folds
    grain = ((u * .9 + v * .4 + n * 3) % 3.2) < .7                                # fibres across the slice
    mat = [['steak' if rim[y, x] or (grain[y, x] and n[y, x] > .7) else 'steakin' for x in range(W)] for y in range(H)]
    light = np.clip(shade(height, mask) * .8 + .2 - np.where(grain & ~rim, .12, 0), 0, 1) * mask
    return render(mat, light, mask, {'steakin': 'steak'})

def beef_cubes(seed):
    from gen_ingredients2 import grated
    return grated('steak', seed, 'cube', n_bits=12)

# ---------------- LOBSTER (whole, claws to the right) ----------------
LOB_W, LOB_H = 140, 112
def lobster(seed, ang=None):
    a = 0 if ang is None else ang                            # rotates: always drawn lying down
    W, H = turn(LOB_W, LOB_H, ang)
    u, v = axes(W, H, a)
    av = np.abs(v)
    parts = np.zeros((H, W), int)                            # 1 tail fan, 2 tail, 3 body, 4 arm, 5 claw, 6 leg
    # tail fan: five plates
    fan = (u >= -68) & (u < -54) & (av <= 8 + (-54 - u) * 1.1)
    # abdomen: six segments, a little wider towards the body
    tw = 13 + (u + 54) / 50 * 4
    tail = (u >= -56) & (u < -4) & (av <= tw)
    # carapace: an egg, narrow at the head
    cu = (u - 14) / 26
    body = (np.abs(cu) <= 1) & (av <= 19 * np.sqrt(np.clip(1 - cu ** 2, 0, 1)) * (1 - np.clip(cu, 0, 1) * .35))
    head = (u >= 38) & (u <= 46) & (av <= (46 - u) * .45)   # rostrum
    # arms and claws, both sides: the arm goes from the head out to the claw
    arm = np.zeros_like(fan); claw = np.zeros_like(fan); gap = np.zeros_like(fan)
    for s in (-1, 1):
        sv = v * s
        t = np.clip((u - 24) / 18, 0, 1)                     # arm from (24, 10) to (42, 28)
        ax, ay = 24 + t * 18, 10 + t * 18
        arm |= (np.hypot(u - ax, sv - ay) <= 4.2) & (u >= 22) & (u <= 44)
        ku, kv = (u - 54) / 16, (sv - 33) / 12               # claw: a big ellipse, tilted outwards
        rku = ku * np.cos(.25) + kv * .9 * np.sin(.25); rkv = -ku * np.sin(.25) * 1.5 + kv * np.cos(.25)
        cl = rku ** 2 + rkv ** 2 <= 1
        cl |= ((u - 66) / 5) ** 2 + ((sv - 35) / 7) ** 2 <= 1   # tips
        g = (u > 58) & (np.abs(sv - 34 - (u - 58) * .15) < 1.0)  # the opening of the pincer
        claw |= cl; gap |= cl & g
        for k, lu in enumerate((2, 10, 18)):                 # legs: thin, pointing out and back
            lt = np.clip((sv - 14) / 14, 0, 1)
            lx = lu - lt * 10
            arm_leg = (np.abs(u - lx) <= 1.4) & (sv >= 13) & (sv <= 30 - k * 2)
            parts[arm_leg & (parts == 0)] = 6
    parts[fan] = 1; parts[tail & (parts == 0)] = 2; parts[(body | head)] = 3
    parts[arm & (parts == 0)] = 4; parts[claw & ~gap] = 5
    mask = parts > 0
    n = noise(H, W, 4, np.random.default_rng(5100))
    # height: each part a rounded hump, with grooves between tail segments
    seg = ((u + 56) % (52 / 6))
    height = np.zeros((H, W))
    height = np.where(parts == 3, np.sqrt(np.clip(1 - cu ** 2, 0, 1)) * np.sqrt(np.clip(1 - (av / 20) ** 2, 0, 1)) * 8, height)
    height = np.where(parts == 2, np.sqrt(np.clip(1 - (av / (tw + .1)) ** 2, 0, 1)) * 5 - np.where(seg < 1.4, 1.6, 0), height)
    height = np.where(parts == 1, 1.5 - np.where(((v + 30) % 6) < 1, .8, 0), height)
    height = np.where(parts == 5, 5.5 * np.sqrt(np.clip(1 - np.minimum(1, (np.abs(v) - 33) ** 2 / 150 + (u - 54) ** 2 / 300), 0, 1)) + .5, height)
    height = np.where(parts == 4, 2.0, height)
    height = np.where(parts == 6, .8, height)
    height = height + (n - .5) * .8
    joint = (parts == 2) & (seg < 1.4) | (parts == 3) & (np.abs(u - 10) < 1) & (av < 13)   # dark grooves
    mat = [['lobdark' if joint[y, x] or parts[y, x] == 6 else 'lob' for x in range(W)] for y in range(H)]
    light = np.clip(shade(height, mask) * .85 + .15, 0, 1) * mask
    img = render(mat, light, mask, {'lobdark': 'lobdark'})
    px = img.load()
    def put(uu, vv, col):                                    # a point given along/across the piece
        x = W / 2 - .5 + uu * np.cos(a) - vv * np.sin(a); y = H / 2 - .5 + uu * np.sin(a) + vv * np.cos(a)
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi < W and 0 <= yi < H: px[xi, yi] = col + (255,)
    for s in (-1, 1):
        put(36, 6 * s, R['lobdark'][0]); put(37, 6 * s, R['lobdark'][0]); put(36, 7 * s, R['lobdark'][0])        # eyes
        for k in range(46):                                                  # antennae: thin, curving back along the sides
            t = k / 45
            put(44 + 20 * np.sin(t * 2.6), s * (3 + 46 * t ** 1.4), R['lob'][1] if k % 7 else R['lob'][3])
    return img

def lobster_chunks(seed, W=30, H=26):
    """chopped: 3 or 4 big seafood-stick chunks, white with a red-orange top"""
    rng = np.random.default_rng(seed + 5200)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    placed = []
    for _ in range(60):
        if len(placed) >= 4: break
        cw, ch = int(rng.integers(10, 13)), int(rng.integers(7, 9))
        x, y = int(rng.integers(0, W - cw)), int(rng.integers(0, H - ch))
        if any(abs(x - px_) < 9 and abs(y - py_) < 7 for px_, py_ in placed): continue
        placed.append((x, y))
        ys, xs = np.mgrid[0:ch, 0:cw]
        e = (np.abs(xs - (cw - 1) / 2) / (cw / 2)) ** 4 + (np.abs(ys - (ch - 1) / 2) / (ch / 2)) ** 4
        mask = e <= 1
        height = np.clip(1 - e, 0, 1) * 2.2
        tilt = rng.uniform(-.3, .3)
        top = ys < ch * .42 + (xs - cw / 2) * tilt                 # the coloured skin on top
        mat = [['surred' if top[j, i] else 'surimi' for i in range(cw)] for j in range(ch)]
        light = np.clip(shade(height, mask) * .75 + .3, 0, 1) * mask
        chunk = render(mat, light, mask, {'surimi': 'surimi', 'surred': 'surred'})
        cp = chunk.load()
        for i in range(1, cw - 1, 3):                               # fibres on the white side
            j = ch - 2
            if mask[j, i] and not top[j, i]: cp[i, j] = R['surimi'][0] + (255,)
        img.alpha_composite(chunk, (x, y))
    return img

# ---------------- RIBS (one glazed rib, bone to the right) ----------------
def rib(seed, ang=None, L=40, T=12):
    a = 0 if ang is None else ang
    W, H = turn(L + 4, T + 6, ang)
    u, v = axes(W, H, a)
    rng = np.random.default_rng(seed + 5300)
    n = noise(H, W, 3, rng)
    bend = .9 * ((u / (L / 2)) ** 2 - .5)                        # a gentle curve, like a real rib
    vv = v - bend
    meat_len = L - 9
    mu = u + 4.5                                                 # the meat sits left of centre
    edge = 1 + (n - .5) * .25
    meat = (np.abs(mu) <= meat_len / 2) & (np.abs(vv) <= (T / 2) * edge * np.sqrt(np.clip(1 - (np.abs(mu) / (meat_len / 2 + .5)) ** 6, 0, 1)))
    bone = (u > meat_len / 2 - 6) & (u <= L / 2) & (np.abs(vv) <= 2.2)
    knob = np.hypot(u - (L / 2 - 1.5), vv) <= 3                  # the bone end
    bonem = (bone | knob) & ~meat
    mask = meat | bonem
    height = np.where(meat, np.sqrt(np.clip(1 - (vv / (T / 2 + .1)) ** 2, 0, 1)) * 3.5 + (n - .5) * 1.4, 0)
    height = np.where(bonem, 1.6 * np.sqrt(np.clip(1 - (vv / 3) ** 2, 0, 1)), height)
    char = meat & (n > .68)                                      # charred spots on the glaze
    mat = [['bone' if bonem[y, x] else 'ribglz' for x in range(W)] for y in range(H)]
    light = np.clip(shade(height, mask) * .9 + .15 - np.where(char, .25, 0), 0, 1) * mask
    return render(mat, light, mask, {'bone': 'bone', 'ribglz': 'ribglz'})

def rib_cubes(seed):
    from gen_ingredients2 import grated
    return grated('ribglz', seed, 'cube', n_bits=12)

SETS = [('Carne de vaca', beef, beef_cubes), ('Lagosta', lobster, lobster_chunks), ('Ribs', rib, rib_cubes)]

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    from build_atlas import drop
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    # the lobster on its own: drawn on a sauce-sized disc to check it fits inside the crust
    ROW = 200
    sheet = Image.new('RGB', (1000, 40 + ROW * 2 + 380), (27, 20, 16)); dr = ImageDraw.Draw(sheet)
    dr.text((20, 10), 'Whole (the 1st lies down) / chopped', fill=(240, 220, 180), font=fs)
    y = 36
    for name, fn, gr in (SETS[0], SETS[2]):
        arr = [fn(1, ang=0) if fn is rib else fn(1), fn(2), fn(3), gr(41)]
        x = 20
        for im in arr:
            d = drop(im); K = 4
            m = d.resize((d.width * K, d.height * K), Image.NEAREST)
            bg = Image.new('RGB', (230, ROW - 12), (196, 52, 28))
            bg.paste(m, ((230 - m.width) // 2, (ROW - 12 - m.height) // 2), m)
            sheet.paste(bg, (x, y)); x += 240
        y += ROW
    K = 2; D = 170
    disc = Image.new('RGB', (D * K + 20, D * K + 20), (27, 20, 16)); dd = ImageDraw.Draw(disc)
    dd.ellipse((10, 10, 10 + D * K, 10 + D * K), fill=(214, 168, 100))           # crust
    rr = int(D * K / 2 * .86); c0 = 10 + D * K // 2
    dd.ellipse((c0 - rr, c0 - rr, c0 + rr, c0 + rr), fill=(196, 52, 28))          # sauce
    lb = drop(lobster(1, ang=0)); lm = lb.resize((lb.width * K, lb.height * K), Image.NEAREST)
    disc.paste(lm, (c0 - lm.width // 2, c0 - lm.height // 2), lm)
    sheet.paste(disc, (20, y))
    ch = drop(lobster_chunks(41)); cm = ch.resize((ch.width * 5, ch.height * 5), Image.NEAREST)
    bg = Image.new('RGB', (230, 200), (196, 52, 28)); bg.paste(cm, ((230 - cm.width) // 2, (200 - cm.height) // 2), cm)
    sheet.paste(bg, (420, y))
    sheet.save(OUT + 'preview_ingredientes17.png'); print('ok', sheet.size)
