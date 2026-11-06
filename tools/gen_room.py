#!/usr/bin/env python3
"""Pizza Magna: dining room in detailed pixel art, at twice the room's current scale (32 px tiles).
Same method as the toppings (see tools/CLAUDE.md): each pixel has a material and a light value
(from a height field or per face, light from the top left), quantised onto the material's ramp with
4x4 ordered dithering, and a selective outline in the material's own dark tone, never black.
Parts in front get a crisp edge against the parts behind them.

This first version is a preview: a corner of the room (floor, tiled wall, windows, a round tasca
table and a checked trattoria table with chairs, seated customers, pizzas, a plant).
Usage: python3 tools/gen_room.py <folder>   -> preview_room.png"""
import os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from gen_ingredients import hexs, BAYER, noise

OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'preview')) + '/'

RAMP = {
    'oak':     hexs(['#3a1d0c', '#5e3418', '#7e4a24', '#9c6232', '#bb7e44', '#d49a5e']),
    'oakD':    hexs(['#1e0e05', '#3a1d0c', '#5a3016', '#764220', '#93582c']),
    'plank':   hexs(['#4a2610', '#6a3a1a', '#8a5026', '#a86834', '#c48446', '#d9a066']),
    'straw':   hexs(['#5a3e14', '#86642a', '#b08c42', '#d2b064', '#ead088', '#f8e8b0']),
    'linen':   hexs(['#8a7a5e', '#b3a484', '#d6caac', '#ece3cc', '#faf5e8', '#ffffff']),
    'blue':    hexs(['#142c56', '#24508e', '#3e70b4', '#6e98d0', '#a8c4e8']),
    'glaze':   hexs(['#9aa4b0', '#c4ccd6', '#e2e8ee', '#f4f7fa', '#ffffff']),
    'plaster': hexs(['#a89878', '#c6b896', '#ddd2b4', '#ede4ca', '#f8f2e2']),
    'clay':    hexs(['#4a1a0a', '#7a3216', '#a84a22', '#cc6a34', '#e8925a', '#f8bc8a']),
    'red':     hexs(['#4a0c08', '#7a1810', '#a8261a', '#cc3a2a', '#e46048', '#f49274']),
    'cream':   hexs(['#9a8a6a', '#c2b08c', '#ddcca8', '#eee2c4', '#fbf4e2', '#ffffff']),
    'curtain': hexs(['#3e0a08', '#68140e', '#921e16', '#b82e22', '#d84a36', '#f07658']),
    'gold':    hexs(['#5a3c0c', '#8a6018', '#b8862a', '#e0b048', '#f8da7a', '#fff4c0']),
    'sky':     hexs(['#5a86b0', '#7ea8d0', '#a4c8e8', '#c8e2f6', '#eef8ff']),
    'leaf':    hexs(['#0e2a14', '#184a20', '#26682c', '#3c8a38', '#62ac4a', '#98d070']),
    'plate':   hexs(['#8e949a', '#b8bec4', '#dadee2', '#eef0f2', '#fbfcfd', '#ffffff']),
    'crust':   hexs(['#6a3a12', '#9a5a1e', '#c4802e', '#e0a448', '#f4c86e']),
    'sauce':   hexs(['#5a0e06', '#8a1a0c', '#b42a14', '#d8442a']),
    'cheese':  hexs(['#c0902e', '#e0b44a', '#f4d474', '#fff0a8', '#fffbe0']),
    'pepp':    hexs(['#4a0806', '#7a120c', '#a42018', '#c8382a']),
    'bottle':  hexs(['#0a2a12', '#14461e', '#20662c', '#3a8a40', '#78c070']),
    'wax':     hexs(['#b8a888', '#ddd0b0', '#f2e8d0', '#fffaf0']),
    'flame':   hexs(['#e8461a', '#ff8a1e', '#ffd35a', '#fff4c0']),
    'iron':    hexs(['#1a1a1e', '#2e2e34', '#46464e', '#62626c']),
    # people: skins, hair and shirts are picked per customer
    'skinA':   hexs(['#7a4a30', '#b0704c', '#d89a74', '#f0c09c', '#fcdcc0']),
    'skinB':   hexs(['#4a2a18', '#7a4a2e', '#a46a44', '#c88c62', '#e2ae84']),
    'skinC':   hexs(['#2a160c', '#4a2a18', '#6a4028', '#8a5838', '#a87452']),
    'hairK':   hexs(['#0a0808', '#1a1414', '#2e2420', '#463830']),
    'hairB':   hexs(['#2a1408', '#4a2610', '#6e3c1c', '#94582c']),
    'hairY':   hexs(['#6a4a14', '#9a7428', '#c8a040', '#e8c868', '#f8e49c']),
    'hairR':   hexs(['#4a1408', '#7a2410', '#a8401c', '#cc6230']),
    'hairG':   hexs(['#4a4a4e', '#76767c', '#a0a0a6', '#c8c8ce', '#ececf0']),
    'shirtB':  hexs(['#0e2448', '#1a3c74', '#2a5aa4', '#4a80cc', '#7aa8e8']),
    'shirtG':  hexs(['#0e3418', '#1a5228', '#2a7a3a', '#48a050', '#78c878']),
    'shirtY':  hexs(['#6a4a08', '#a07818', '#d0a42a', '#f0cc48', '#fce88a']),
    'shirtP':  hexs(['#2a1040', '#46205e', '#663486', '#8a52ae', '#b07ed0']),
    'shirtW':  hexs(['#8a8a88', '#b4b4b0', '#d6d6d2', '#ececea', '#ffffff']),
    'shirtR':  hexs(['#4a0c08', '#7a1810', '#a8261a', '#cc3a2a', '#e46048']),
    'eye':     hexs(['#140c08', '#2b1b14', '#4a3428']),
    'mouth':   hexs(['#5a1810', '#8a2a1e', '#b0463a']),
}
SHADOW = (30, 14, 6)
SOFT = {'skinA', 'skinB', 'skinC', 'plate', 'glaze', 'sky', 'wax'}   # smooth materials: weaker dithering
L3 = np.array([-.55, -.65, .52]); L3 /= np.linalg.norm(L3)

class Canvas:
    """material, light and part per pixel; rendered with dithering and selective outlines"""
    def __init__(s, w, h):
        s.w, s.h = w, h
        s.mat = np.full((h, w), None, object)
        s.lit = np.zeros((h, w))
        s.part = np.zeros((h, w), int)
        s.noline = np.zeros((h, w), bool)
        s.shadow = np.zeros((h, w))
        s.ys, s.xs = np.mgrid[0:h, 0:w]

    def paint(s, mask, mat, lit, part=0, noline=False):
        lit = np.broadcast_to(lit, (s.h, s.w)) if np.ndim(lit) else np.full((s.h, s.w), float(lit))
        s.mat[mask] = mat; s.lit[mask] = lit[mask]; s.part[mask] = part; s.noline[mask] = noline

    def ell(s, cx, cy, rx, ry): return ((s.xs + .5 - cx) / rx) ** 2 + ((s.ys + .5 - cy) / ry) ** 2 <= 1
    def rect(s, x0, y0, x1, y1): return (s.xs >= x0) & (s.xs < x1) & (s.ys >= y0) & (s.ys < y1)

    def sphere(s, cx, cy, rx, ry, k=1.0):
        """light of a dome (height field) over an ellipse"""
        dx, dy = (s.xs + .5 - cx) / rx, (s.ys + .5 - cy) / ry
        r2 = np.clip(dx * dx + dy * dy, 0, 1)
        nz = np.sqrt(1 - r2) + .35 / k
        n = np.dstack([dx, dy, nz]); n /= np.linalg.norm(n, axis=2, keepdims=True)
        return np.clip((n @ L3 - .1) / .9, 0, 1)

    def cyl_x(s, x0, x1, lo=.25, hi=.85):
        """light across a vertical cylinder (lit on the left)"""
        t = np.clip((s.xs + .5 - x0) / max(1, x1 - x0), 0, 1)
        return lo + (hi - lo) * np.clip(np.cos((t - .3) * np.pi * .9), 0, 1)

    def cast(s, mask, a=.45):
        s.shadow = np.maximum(s.shadow, mask * a)

    def image(s):
        h, w = s.h, s.w
        out = np.zeros((h, w, 4), np.uint8)
        filled = s.mat != None
        for y in range(h):
            for x in range(w):
                if not filled[y, x]:
                    a = s.shadow[y, x]
                    if a > 0 and a + BAYER[y % 4, x % 4] * .25 > .2:     # dithered soft shadow
                        out[y, x] = SHADOW + (int(min(1, a) * 150),)
                    continue
                ramp = RAMP[s.mat[y, x]]; k = len(ramp)
                v = np.clip(s.lit[y, x] * (k - 1) + BAYER[y % 4, x % 4] * (.35 if s.mat[y, x] in SOFT else .9), 0, k - 1)
                col = ramp[int(round(v))]
                if not s.noline[y, x]:
                    edge = False; front = False
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        yy, xx = y + dy, x + dx
                        if not (0 <= yy < h and 0 <= xx < w) or not filled[yy, xx]: edge = True
                        elif s.part[yy, xx] > s.part[y, x]: front = True
                    if edge: col = ramp[0 if s.lit[y, x] < .55 else 1]
                    elif front: col = ramp[max(0, min(1, int(v) - 1))]
                out[y, x] = col + (255,)
        return Image.fromarray(out, 'RGBA')

def rng(seed): return np.random.default_rng(seed + 7000)

# ---------------- FLOORS AND WALLS (tiles, no outline) ----------------
def floor_planks(W=384, H=192, seed=1):
    c = Canvas(W, H); g = rng(seed)
    grain = noise(H, W, 3, g) * .6 + noise(H, W, 1, g) * .25
    grain = np.repeat(noise(H, W // 8 + 2, 2, g)[:, :W // 8 + 1], 8, axis=1)[:, :W] * .5 + grain * .5
    lit = np.zeros((H, W))
    for b in range(H // 8):
        y0 = b * 8; tone = g.uniform(-.12, .12)
        lit[y0:y0 + 8] = .5 + tone + (grain[y0:y0 + 8] - .5) * .45
        lit[y0] += .16; lit[y0 + 7] = .08                       # bevel on top, seam below
        x = int(g.integers(0, 60))
        while x < W:
            lit[y0:y0 + 7, x] = .12; lit[y0 + 1:y0 + 6, min(W - 1, x + 1)] += .1
            if x + 3 < W: lit[y0 + 2, x + 3] = .05; lit[y0 + 5, x + 3] = .05   # nails
            x += int(g.integers(56, 110))
    c.paint(np.ones((H, W), bool), 'plank', np.clip(lit, 0, 1), noline=True)
    return c

def floor_check(W=384, H=192, seed=1):
    c = Canvas(W, H); g = rng(seed + 10)
    sq = ((c.xs // 32) + (c.ys // 32)) % 2 == 0
    glaze = noise(H, W, 6, g) * .2
    inner = (c.xs % 32 > 0) & (c.ys % 32 > 0)
    lit = .55 + glaze + np.where((c.xs % 32 < 2) | (c.ys % 32 < 2), .2, 0) - np.where((c.xs % 32 > 29) | (c.ys % 32 > 29), .18, 0)
    c.paint(sq & inner, 'red', lit, noline=True); c.paint(~sq & inner, 'cream', lit, noline=True)
    c.paint(~inner, 'plaster', .2, noline=True)
    return c

def wall_azulejo(W=384, seed=1):
    """64 px high back wall: wooden cornice, plaster, a band of blue and white tiles, skirting"""
    H = 64; c = Canvas(W, H); g = rng(seed + 20)
    c.paint(c.rect(0, 0, W, 6), 'oakD', np.where(c.ys == 1, .9, np.where(c.ys >= 4, .2, .5)), noline=True)
    c.paint(c.rect(0, 6, W, 22), 'plaster', .55 + noise(H, W, 4, g) * .3 - np.where(c.ys == 6, .3, 0), noline=True)
    c.paint(c.rect(0, 22, W, 24), 'blue', .45, noline=True)
    # 16 px azulejos: a circle cut by its neighbours makes a continuous pattern
    tx, ty = (c.xs % 16) + .5, ((c.ys - 24) % 16) + .5
    d = np.hypot(tx - 8, ty - 8); dc = np.min([np.hypot(tx - a, ty - b) for a in (0, 16) for b in (0, 16)], axis=0)
    motif = (np.abs(d - 5.5) < 1.1) | (dc < 3.2) | ((np.abs(tx - 8) + np.abs(ty - 8)) < 2.2)
    tiles = c.rect(0, 24, W, 56)
    glaze_lit = .62 + noise(H, W, 5, g) * .2 + np.where((tx < 1.2) | (ty < 1.2), .25, 0) - np.where((tx > 15) | (ty > 15), .3, 0)
    c.paint(tiles, 'glaze', glaze_lit, noline=True)
    c.paint(tiles & motif, 'blue', .45 + (glaze_lit - .62) * .6, noline=True)
    c.paint(c.rect(0, 56, W, 58), 'blue', .3, noline=True)
    c.paint(c.rect(0, 58, W, 64), 'oakD', np.where(c.ys == 58, .85, .3), noline=True)
    return c

def window(seed=1):
    """68 x 50: wooden frame, sky with reflections, mullions, sill and red curtains"""
    W, H = 68, 50; c = Canvas(W, H); g = rng(seed + 30)
    frame = c.rect(10, 2, 58, 42)
    c.paint(frame, 'oak', np.where(c.xs < 13, .75, np.where(c.ys < 5, .8, .45)), part=1)
    glass = c.rect(14, 6, 54, 38)
    sky = .85 - (c.ys - 6) / 32 * .6 + np.where(((c.xs - c.ys * .7) % 22 < 3) | ((c.xs - c.ys * .7) % 22 > 20.5), .35, 0)
    c.paint(glass, 'sky', np.clip(sky, 0, 1), part=1, noline=True)
    mull = (c.rect(32, 6, 36, 38) | c.rect(14, 20, 54, 23)) & glass
    c.paint(mull, 'oak', np.where((c.xs == 32) | (c.ys == 20), .8, .4), part=2)
    c.paint(c.rect(7, 40, 61, 46), 'oak', np.where(c.ys < 42, .9, .35), part=3)
    for x0, side in ((0, 1), (W - 16, -1)):
        cur = c.rect(x0, 0, x0 + 16, 44)
        t = (c.xs - x0) / 16
        fold = .45 + .35 * np.sin((c.xs - x0) * 1.2 + side) + (c.ys / 44) * -.1
        waist = (np.abs(c.ys - 30) < 3)
        narrow = cur & ~(((t > .75) if side == 1 else (t < .25)) & (c.ys > 22) & (c.ys < 38))
        c.paint(narrow, 'curtain', np.clip(fold, 0, 1), part=4)
        c.paint(narrow & waist, 'gold', .7, part=5)
    c.paint(c.rect(0, 0, W, 2), 'gold', .6, part=6)
    return c

# ---------------- FURNITURE ----------------
def table_round(seed=1):
    """80 x 70 round tasca table: planked top with a linen runner, clay jug, pedestal"""
    W, H = 80, 70; c = Canvas(W, H); g = rng(seed + 40)
    c.cast(c.ell(42, 62, 30, 7), .5)
    ped = c.rect(34, 40, 46, 62); c.paint(ped, 'oakD', c.cyl_x(34, 46), part=1)
    foot = c.ell(40, 62, 14, 4); c.paint(foot, 'oakD', .35 + (c.xs < 36) * .3, part=2)
    side = c.ell(40, 30, 38, 22) & ~c.ell(40, 24, 38, 22); c.paint(side, 'oak', .25 + (c.xs < 30) * .15, part=3)
    top = c.ell(40, 24, 38, 22)
    r = np.sqrt(((c.xs + .5 - 40) / 38) ** 2 + ((c.ys + .5 - 24) / 22) ** 2)
    grain = np.repeat(noise(H, 12, 2, g), 8, axis=1)[:, :W] if False else noise(H, W * 4, 3, g)[:, ::4][:, :W]
    planks = ((c.ys - 4) % 9 == 0)
    lit = .62 + (grain - .5) * .35 - planks * .35 + np.where(r > .9, (r - .9) * -4, 0) + np.where((r > .82) & (c.ys < 20), .2, 0)
    c.paint(top, 'oak', np.clip(lit, 0, 1), part=4)
    run = top & c.rect(0, 18, W, 30)
    weave = ((c.xs + c.ys) % 3 == 0) * -.08
    c.paint(run, 'linen', .7 + weave - (c.ys == 29) * .3, part=5)
    c.paint(run & ((c.ys == 20) | (c.ys == 27)), 'blue', .5, part=5)
    jug = c.rect(36, 13, 44, 24) | c.ell(40, 23.5, 4.5, 2)
    c.paint(jug, 'clay', c.cyl_x(36, 44, .2, .9), part=6)
    c.paint(c.ell(40, 13.5, 4, 1.6), 'clay', .1, part=7)
    handle = (np.abs(np.hypot(c.xs + .5 - 44, c.ys + .5 - 18) - 3) < 1.1) & (c.xs >= 44)
    c.paint(handle, 'clay', .55, part=6)
    return c

def table_check2(seed=1):
    """76 x 50 trattoria table for two: checked cloth with folds, Chianti bottle with a candle"""
    W, H = 76, 50; c = Canvas(W, H)
    c.cast(c.rect(8, 42, 72, 49), .45)
    for lx in (8, 64): c.paint(c.rect(lx, 34, lx + 5, 46), 'oakD', c.cyl_x(lx, lx + 5), part=1)
    top = c.rect(2, 2, 74, 30); drape = c.rect(2, 30, 74, 40)
    sq = (((c.xs - 2) // 8) + ((c.ys - 2) // 8)) % 2 == 0
    both = ((c.xs - 2) // 8) % 2 == 0
    c.paint(top & sq, 'red', .62, part=2); c.paint(top & ~sq, 'cream', .7, part=2)
    c.paint(top & ((c.ys - 2) % 8 == 0) & (c.xs > 2), 'red', .78, part=2, noline=True)
    fold = .38 + .22 * np.sin((c.xs - 2) * .8)
    c.paint(drape & both, 'red', fold, part=3); c.paint(drape & ~both, 'cream', fold + .05, part=3)
    c.paint(c.rect(2, 2, 74, 3), 'cream', .95, part=2)
    # Chianti: green bottle in a straw basket, a candle with drips
    c.paint(c.ell(38, 22, 6, 6), 'straw', c.sphere(38, 22, 6, 6) * .9, part=5)
    c.paint(c.ell(38, 22, 6, 6) & ((c.xs + c.ys) % 3 == 0), 'straw', .25, part=5)
    c.paint(c.rect(36, 6, 40, 17), 'bottle', c.cyl_x(36, 40, .3, .9), part=6)
    c.paint(c.rect(36, 1, 40, 7), 'wax', c.cyl_x(36, 40, .4, 1), part=7)
    c.paint(c.rect(35, 6, 37, 10) | c.rect(39, 7, 41, 9), 'wax', .8, part=7)
    c.paint(c.ell(38, 0.5, 1.6, 2.5) & (c.ys >= 0), 'flame', .8, part=8, noline=True)
    return c

CHAIR = {'tasca': ('oak', 'straw'), 'tratt': ('oak', 'red')}

def chair(style='tasca', d='down', layer=None):
    """32 x 32 chair. down = seen from the front (backrest at the top), up = from behind,
    right = seen from the side with the backrest on the left (the sitter faces right).
    A chair seen from behind has the sitter between its seat and its backrest: layer='seat'
    or layer='back' draws only one of them, so the person can go in between."""
    wood, seat = CHAIR[style]
    c = Canvas(32, 32)
    weave = (((c.xs // 2) + (c.ys // 2)) % 2) * .14 if seat == 'straw' else 0
    if d == 'down':
        c.cast(c.rect(6, 27, 30, 31), .35)
        for lx in (5, 24): c.paint(c.rect(lx, 18, lx + 3, 30), wood, c.cyl_x(lx, lx + 3), part=1)
        c.paint(c.rect(5, 14, 27, 20), seat, .62 + weave - (c.ys >= 18) * .3, part=2)
        for lx in (5, 24): c.paint(c.rect(lx, 1, lx + 3, 15), wood, c.cyl_x(lx, lx + 3), part=3)
        c.paint(c.rect(5, 2, 27, 6), wood, np.where(c.ys == 2, .9, .55), part=4)
        c.paint(c.rect(13, 6, 19, 13), wood, c.cyl_x(13, 19, .3, .8), part=4)
    elif d == 'up':
        c.cast(c.rect(6, 27, 30, 31), .35)
        if layer != 'back': c.paint(c.rect(5, 6, 27, 12), seat, .75 + weave, part=1)
        if layer == 'seat': return c
        for lx in (5, 24): c.paint(c.rect(lx, 4, lx + 3, 31), wood, c.cyl_x(lx, lx + 3, .2, .6), part=2)
        c.paint(c.rect(5, 12, 27, 16), wood, np.where(c.ys == 12, .75, .4), part=3)
        c.paint(c.rect(13, 16, 19, 24), wood, c.cyl_x(13, 19, .2, .6), part=3)
        c.paint(c.rect(5, 23, 27, 25), wood, .35, part=3)
    else:
        c.cast(c.rect(6, 28, 30, 31), .35)
        c.paint(c.rect(25, 18, 28, 30), wood, c.cyl_x(25, 28, .2, .55), part=1)
        c.paint(c.rect(6, 15, 28, 20), seat, .65 + weave - (c.ys >= 18) * .32, part=2)
        c.paint(c.rect(5, 1, 9, 30), wood, c.cyl_x(5, 9), part=3)
        c.paint(c.rect(9, 4, 11, 15), wood, .4, part=3)
        if d == 'left': c = flip(c)
    return c

def flip(c):
    for a in ('mat', 'lit', 'part', 'noline', 'shadow'): setattr(c, a, getattr(c, a)[:, ::-1].copy())
    return c

def plant(seed=1):
    """36 x 58 potted plant: clay pot, round clumps of leaves"""
    W, H = 36, 58; c = Canvas(W, H); g = rng(seed + 50)
    c.cast(c.ell(20, 55, 12, 3), .5)
    pot = c.rect(9, 38, 27, 55) & ~(c.rect(9, 52, 11, 55) | c.rect(25, 52, 27, 55))
    c.paint(pot, 'clay', c.cyl_x(9, 27, .2, .85), part=1)
    c.paint(c.rect(7, 36, 29, 41), 'clay', np.where(c.ys == 36, .95, .6), part=2)
    leafy = noise(H, W, 2, g)
    for cx, cy, r in [(18, 22, 13), (11, 28, 8), (25, 27, 8), (18, 11, 9), (10, 17, 7), (27, 16, 7)]:
        m = c.ell(cx, cy, r, r * .95)
        c.paint(m, 'leaf', np.clip(c.sphere(cx, cy, r, r) * .85 + (leafy - .5) * .5, 0, 1), part=3)
    c.paint(c.rect(17, 30, 19, 37), 'oakD', .4, part=2)
    return c

def pizza(seed=1):
    """24 x 15: pizza on a white plate, seen at the same slant as the table tops"""
    W, H = 24, 15; c = Canvas(W, H); g = rng(seed + 60)
    c.paint(c.ell(12, 8, 11.5, 6.5), 'plate', .7 + (c.ys < 5) * .2, part=1)
    c.paint(c.ell(12, 7.5, 9.5, 5.2), 'crust', c.sphere(12, 7.5, 9.5, 5.2) * .8 + .1, part=2)
    c.paint(c.ell(12, 7.5, 7.3, 3.8), 'sauce', .55, part=3, noline=True)
    ch = c.ell(12, 7.5, 7.3, 3.8) & (noise(H, W, 2, g) > .45)
    c.paint(ch, 'cheese', .55 + noise(H, W, 1, g) * .3, part=3, noline=True)
    for px, py in [(9, 6.5), (15, 6), (12, 9), (16, 9)]:
        c.paint(c.ell(px, py, 1.7, 1.1), 'pepp', c.sphere(px, py, 1.7, 1.1) * .9, part=4)
    return c

# ---------------- PEOPLE (seated, whole body, 32 x 48) ----------------
# Every view puts the hips at y = 33, so a person is drawn 18 px above the chair it sits on
# (24 px for a chair seen from behind, whose seat is further back).
PANTS = ['jeans', 'pantsK', 'pantsB']
RAMP.update({
    'jeans':  hexs(['#101c34', '#1c2e52', '#2c4674', '#46649a', '#6a88bc']),
    'pantsK': hexs(['#141418', '#24242a', '#383840', '#50505a', '#6c6c78']),
    'pantsB': hexs(['#2a1a0c', '#46301a', '#644628', '#866238', '#a8804c']),
    'shoe':   hexs(['#0c0808', '#1e1410', '#36261c', '#5a4030']),
})
def person(d='down', skin='skinA', hair='hairB', shirt='shirtB', long=False, pants='jeans'):
    c = Canvas(32, 48)
    stripes = lambda: ((c.xs * 2 + c.ys) % 5 == 0) * -.15
    if d in ('left', 'right'):
        c.paint(c.rect(23, 36, 27, 46), pants, c.cyl_x(23, 27, .2, .6), part=1)          # shin down to the floor
        c.paint(c.rect(22, 44, 30, 48) & ~c.rect(22, 44, 24, 46), 'shoe', np.where(c.ys == 44, .9, .4), part=2)
        c.paint(c.rect(12, 31, 28, 37) | c.ell(26, 34, 2.5, 3), pants, np.where(c.ys < 33, .75, .4), part=3)   # thigh on the seat
        c.paint(c.rect(11, 20, 22, 34) | c.ell(16.5, 21, 5.5, 2.5), shirt, c.cyl_x(11, 22), part=4)
        c.paint(c.rect(14, 16, 19, 21), skin, .35, part=4)
        c.paint(c.rect(14, 21, 19, 28), shirt, c.cyl_x(14, 19, .3, .75), part=5)          # upper arm
        c.paint(c.rect(16, 25, 29, 29), shirt, np.where(c.ys < 27, .7, .35), part=6)       # forearm towards the table
        c.paint(c.rect(28, 25, 32, 29), skin, .65, part=7)
        head = c.ell(17, 10, 7, 8); c.paint(head, skin, .45 + c.sphere(17, 10, 7, 8) * .45, part=8)
        c.paint(c.rect(23, 10, 25, 13), skin, .6, part=8)                                 # nose
        hm = c.ell(16, 8, 8, 7.5) & ((c.ys < 7) | (c.xs < 15))
        if long: hm |= c.rect(9, 7, 16, 23) & c.ell(13, 13, 6, 10)
        c.paint(hm, hair, c.sphere(16, 8, 8, 8) * .9 + stripes(), part=9)
        c.paint(c.rect(20, 10, 22, 13), 'eye', .1, part=10, noline=True)
        c.paint(c.rect(21, 10, 22, 11), 'plate', 1, part=10, noline=True)
        c.paint(c.rect(20, 8, 23, 9), hair, .2, part=10, noline=True)
        c.paint(c.rect(15, 10, 17, 13), skin, .3, part=10, noline=True)                   # ear
        c.paint(c.rect(21, 15, 23, 16), 'mouth', .6, part=10, noline=True)
        return flip(c) if d == 'left' else c
    if d == 'down':
        for lx in (9, 18): c.paint(c.rect(lx, 38, lx + 5, 45), pants, c.cyl_x(lx, lx + 5, .25, .65), part=1)
        for lx in (8, 17): c.paint(c.rect(lx, 44, lx + 7, 48), 'shoe', np.where(c.ys == 44, .9, .4), part=2)
        c.paint(c.rect(8, 33, 24, 39), pants, np.where(c.ys < 35, .8, .5), part=3)        # lap
        c.paint(c.rect(15, 33, 17, 39), pants, .3, part=3, noline=True)
    body = c.rect(8, 20, 24, 34) | c.ell(16, 22, 9.5, 3.5)
    c.paint(body, shirt, c.cyl_x(8, 24), part=4)
    for ax in (4, 24):
        c.paint(c.rect(ax, 21, ax + 4, 32) | c.ell(ax + 2, 21.5, 2.5, 2), shirt, c.cyl_x(ax, ax + 4, .25, .7), part=5)
    c.paint(c.rect(14, 16, 18, 21), skin, .3, part=4)
    if d == 'down':
        c.paint(c.ell(16, 20, 3, 2.5) & (c.ys > 19), skin, .45, part=5)                  # neckline
        for ax in (4, 24): c.paint(c.rect(ax, 31, ax + 4, 35), skin, .6, part=6)          # hands on the lap
    head = c.ell(16, 10, 7.5, 8.5); c.paint(head, skin, .45 + c.sphere(16, 10, 7.5, 8.5) * .45, part=8)
    c.paint(c.ell(8.5, 11, 1.6, 2.4) | c.ell(23.5, 11, 1.6, 2.4), skin, .35, part=7)
    if d == 'down':
        hm = c.ell(16, 8, 8.5, 8) & ((c.ys < 6.5 + np.abs(c.xs - 16) * .25) | (np.abs(c.xs - 16) > 6))
        if long: hm |= (c.rect(7, 6, 10, 24) | c.rect(22, 6, 25, 24))
        c.paint(hm & (c.ys < 24), hair, c.sphere(16, 8, 8.5, 8.5) * .9 + stripes(), part=9)
        for ex in (12, 19):
            c.paint(c.rect(ex, 11, ex + 2, 14), 'eye', .1, part=10, noline=True)
            c.paint(c.rect(ex, 11, ex + 1, 12), 'plate', 1, part=10, noline=True)      # catch light
            c.paint(c.rect(ex, 9, ex + 2, 10), hair, .2, part=10, noline=True)        # eyebrow
        c.paint(c.rect(15, 16, 18, 17), 'mouth', .6, part=10, noline=True)
        c.paint(c.rect(16, 13, 17, 15), skin, .25, part=10, noline=True)            # nose shadow
    else:
        hm = c.ell(16, 9, 8.5, 9.5)
        if long: hm |= c.rect(8, 8, 24, 25) & c.ell(16, 14, 8.5, 12)
        c.paint(hm, hair, c.sphere(16, 9, 8.5, 9.5) * .85 + stripes(), part=9)
    return c

# ---------------- PREVIEW SCENE ----------------
def scene():
    W, H = 384, 224
    img = Image.new('RGBA', (W, H))
    img.alpha_composite(wall_azulejo(W).image(), (0, 0))
    img.alpha_composite(floor_planks(W, H - 64).image(), (0, 64))
    img.alpha_composite(floor_check(128, 160).image(), (256, 64))
    for x in (60, 188): img.alpha_composite(window().image(), (x, 4))
    D = []   # (z, image, x, y)
    def add(z, cv, x, y): D.append((z, cv.image() if isinstance(cv, Canvas) else cv, x, y))
    # round table for four, origin (16, 64) on a 4 x 4 tile footprint
    ox, oy = 16, 70
    add(oy + 34, chair('tasca', 'down'), ox + 48, oy + 4)
    add(oy + 35, person('down', 'skinA', 'hairY', 'shirtR', long=True, pants='pantsK'), ox + 48, oy + 4 - 18)
    add(oy + 84, chair('tasca', 'right'), ox + 0, oy + 52)
    add(oy + 85, person('right', 'skinB', 'hairK', 'shirtG'), ox + 0, oy + 52 - 18)
    add(oy + 84, chair('tasca', 'left'), ox + 96, oy + 52)
    add(oy + 85, person('left', 'skinA', 'hairG', 'shirtW', pants='pantsB'), ox + 96, oy + 52 - 18)
    add(oy + 92, table_round(), ox + 24, oy + 24)
    for px, py in ((64, 34), (38, 48), (90, 48), (64, 62)): add(oy + 92.5, pizza(px), ox + px - 12, oy + py - 7)
    add(oy + 125, person('up', 'skinC', 'hairB', 'shirtP'), ox + 48, oy + 94 - 24)
    add(oy + 100, chair('tasca', 'up', 'seat'), ox + 48, oy + 94)
    add(oy + 126, chair('tasca', 'up', 'back'), ox + 48, oy + 94)
    # checked table for two, origin (184, 112)
    ox, oy = 176, 120
    add(oy + 58, chair('tratt', 'right'), ox + 0, oy + 28)
    add(oy + 59, person('right', 'skinB', 'hairR', 'shirtY', long=True, pants='pantsK'), ox + 0, oy + 28 - 18)
    add(oy + 58, chair('tratt', 'left'), ox + 96, oy + 28)
    add(oy + 59, person('left', 'skinC', 'hairK', 'shirtB', pants='pantsB'), ox + 96, oy + 28 - 18)
    add(oy + 64, table_check2(), ox + 26, oy + 10)
    add(oy + 64.5, pizza(7), ox + 32, oy + 20)
    add(oy + 64.5, pizza(8), ox + 70, oy + 20)
    add(120, plant(), 340, 68)
    add(222, plant(2), 2, 168)
    for z, im, x, y in sorted(D, key=lambda d: d[0]): img.alpha_composite(im, (int(x), int(y)))
    return img

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    s = scene()
    s.save(OUT + 'room_hd.png')
    s.resize((s.width * 2, s.height * 2), Image.NEAREST).save(OUT + 'preview_room.png')
    print('ok', s.size)
