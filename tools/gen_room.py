#!/usr/bin/env python3
"""Pizza Magna: dining room in detailed pixel art, at twice the room's current scale (32 px tiles).
Same method as the toppings (see tools/CLAUDE.md): each pixel has a material and a light value
(from a height field or per face, light from the top left), quantised onto the material's ramp with
4x4 ordered dithering, and a selective outline in the material's own dark tone, never black.
Parts in front get a crisp edge against the parts behind them.

It draws every piece of the dining room (floors, walls, chairs, tables, decor, wall pieces, the
kitchen, the street and the people) and packs them into ../assets/room.js: the frames, plus the
layout of each piece (where its parts, seats and table top are), which docs/drafts/room.html reads.
Usage: python3 tools/gen_room.py <folder>   -> assets/room.js and <folder>/room_atlas.png"""
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
                v = np.clip(s.lit[y, x] * (k - 1) + BAYER[y % 4, x % 4] * (.12 if s.mat[y, x] in SKINS else .35 if s.mat[y, x] in SOFT else .9), 0, k - 1)
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

RAMP.update({
    'formica': hexs(['#8e8e88', '#b8b8b2', '#d8d8d2', '#eeeeea', '#fbfbf8', '#ffffff']),
    'chrome':  hexs(['#3a3e44', '#6a7078', '#9aa2aa', '#c8ced4', '#eef2f6', '#ffffff']),
    'velvet':  hexs(['#2a0610', '#4a0c1c', '#6e142a', '#92203a', '#b4364e']),
    'leather': hexs(['#3a0806', '#62100c', '#8c1c14', '#b02a1e', '#d04434', '#e8705a']),
    'marbleW': hexs(['#a8a296', '#c8c2b6', '#ddd8ce', '#ece8e0', '#f8f6f0', '#ffffff']),
    'marbleV': hexs(['#8a8478', '#a8a296', '#c2bcb0']),
    'onyx':    hexs(['#0e0e12', '#1c1c22', '#2e2e36', '#44444e']),
    'lacquer': hexs(['#08080a', '#141418', '#24242a', '#3c3c46', '#6a6a78', '#b0b0c0']),
    'stone':   hexs(['#4e4840', '#6c645a', '#8a8276', '#a8a094', '#c6beb2', '#e2dace']),
    'water':   hexs(['#12305e', '#1e4c8a', '#2e6cb4', '#4a92d4', '#7ab8ec', '#c0e2fa']),
    'terraz':  hexs(['#a8a49c', '#c4c0b8', '#dad6ce', '#e8e4dc', '#f4f2ec']),
    'terra':   hexs(['#5e2410', '#84361a', '#a84a24', '#c45e30', '#dc7a44', '#f09a62']),
    'tileK':   hexs(['#6c7276', '#868c90', '#a0a6aa', '#babfc2', '#d2d6d8']),
    'tileW':   hexs(['#a8b0b4', '#c8ced2', '#e0e4e6', '#f0f2f2', '#ffffff']),
    'paper':   hexs(['#a89462', '#c8b47e', '#e0cc98', '#eee0b4', '#faf0d0']),
    'green':   hexs(['#08241a', '#0e3426', '#164a36', '#206046', '#2e7a58']),
    'brick':   hexs(['#4a1a0e', '#6e2a18', '#924024', '#b05632', '#c87048', '#de9068']),
    'mortar':  hexs(['#8a7a62', '#a8987c', '#c4b698', '#dccfb2']),
    'slate':   hexs(['#141c18', '#1e2a24', '#2a3a32', '#3a4c42']),
    'chalk':   hexs(['#a8b4a8', '#d0dad0', '#f0f6f0']),
    'purple':  hexs(['#1e0a2a', '#361448', '#52206a', '#72348c', '#9452ae', '#b87ad0']),
    'neonP':   hexs(['#5a1040', '#a02070', '#e040a0', '#ff80d0', '#ffd0f0']),
    'neonC':   hexs(['#104a5a', '#2090a0', '#40d0e0', '#a0f8ff', '#e8ffff']),
    'screen':  hexs(['#0a2a0a', '#165a16', '#28a028', '#6ae86a', '#c8ffc8']),
    'lamp':    hexs(['#b89a5a', '#dcc080', '#f2dca8', '#fff2d0', '#fffcf0']),
    'fish':    hexs(['#8a2a08', '#d8541a', '#ff8a2a', '#ffc070']),
    'sand':    hexs(['#8a7448', '#b09a68', '#d0bc8a', '#e8d8ac']),
    'iron2':   hexs(['#26262c', '#3a3a42', '#565660', '#7a7a86', '#a4a4b0']),
    'apron':   hexs(['#9a9a96', '#c4c4c0', '#e2e2de', '#f6f6f2', '#ffffff']),
    'vest':    hexs(['#08080a', '#16161a', '#26262c', '#3a3a44']),
    'sepia':   hexs(['#3a2818', '#6a5034', '#9a7a54', '#c8a87c', '#ecd8b4']),
    'box':     hexs(['#8a7450', '#b09a72', '#d0bc94', '#e8d8b4', '#f8eed6']),
    'skinD':   hexs(['#5a3420', '#8a5434', '#b47a52', '#d8a074', '#f0c49c']),
})
RAMP.update({
    'irisBr': hexs(['#2a1408', '#5a3416', '#8a5a2e']), 'irisBl': hexs(['#14284a', '#2e5a96', '#6a9ad0']),
    'irisGr': hexs(['#14301a', '#2e6a3a', '#62a06a']), 'irisHz': hexs(['#3a2a10', '#7a6028', '#b09a50']),
    'irisDk': hexs(['#120a06', '#2e1c10', '#4e3420']),
    'lash':   hexs(['#1a0e08', '#3a2418', '#5a3a28']),
    'lip':    hexs(['#7a2a24', '#b04a40', '#d87a6a', '#f0a898']),
    'white':  hexs(['#c8c4bc', '#eeeae4', '#ffffff']),
})
SKINS = {'skinA', 'skinB', 'skinC', 'skinD'}
SOFT |= {'formica', 'chrome', 'marbleW', 'lacquer', 'water', 'skinD', 'apron', 'lamp', 'tileW'}

def pnoise(h, w, cell, g):
    """value noise that wraps around (h and w are multiples of cell), for tiles that repeat"""
    gh, gw = max(1, h // cell), max(1, w // cell); G = g.random((gh, gw))
    ys, xs = np.mgrid[0:h, 0:w]; fy, fx = ys / cell, xs / cell
    y0, x0 = np.floor(fy).astype(int), np.floor(fx).astype(int); ty, tx = fy - y0, fx - x0
    ty, tx = ty * ty * (3 - 2 * ty), tx * tx * (3 - 2 * tx)
    a, b = G[y0 % gh, x0 % gw], G[y0 % gh, (x0 + 1) % gw]
    c, d = G[(y0 + 1) % gh, x0 % gw], G[(y0 + 1) % gh, (x0 + 1) % gw]
    return (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty

def flip(c):
    for a in ('mat', 'lit', 'part', 'noline', 'shadow'): setattr(c, a, getattr(c, a)[:, ::-1].copy())
    return c

# ======================= FLOORS (128 x 128 tiles that repeat, no outline) =======================
FT = 128
def floor_check():
    c = Canvas(FT, FT); g = rng(10)
    sq = ((c.xs // 32) + (c.ys // 32)) % 2 == 0
    tx, ty = c.xs % 32, c.ys % 32
    lit = .55 + pnoise(FT, FT, 8, g) * .18 + pnoise(FT, FT, 2, g) * .08 + np.where((tx < 2) | (ty < 2), .18, 0) - np.where((tx > 29) | (ty > 29), .16, 0)
    inner = (tx > 0) & (ty > 0)
    c.paint(sq & inner, 'red', lit, noline=True); c.paint(~sq & inner, 'cream', lit, noline=True)
    c.paint(~inner, 'mortar', .3, noline=True)
    return c

def floor_planks():
    c = Canvas(FT, FT); g = rng(11)
    grain = pnoise(FT, FT, 2, g) * .35 + np.repeat(np.repeat(g.random((FT // 8, FT // 16)), 8, 0), 16, 1) * 0
    streak = pnoise(FT, FT, 16, g)
    lit = np.zeros((FT, FT))
    for b in range(FT // 8):
        y0 = b * 8; tone = g.uniform(-.12, .12)
        lit[y0:y0 + 8] = .5 + tone + (grain[y0:y0 + 8] - .17) * .7 + (streak[y0:y0 + 8] - .5) * .2
        lit[y0] += .16; lit[y0 + 7] = .07
        x = int(g.integers(0, 64))
        for _ in range(2):
            lit[y0:y0 + 7, x % FT] = .1; lit[y0 + 1:y0 + 6, (x + 1) % FT] += .1
            lit[y0 + 2, (x + 3) % FT] = .04; lit[y0 + 5, (x + 3) % FT] = .04
            x += 64
    c.paint(np.ones((FT, FT), bool), 'plank', np.clip(lit, 0, 1), noline=True)
    return c

def floor_hydraulic():
    c = Canvas(FT, FT); g = rng(12)
    tx, ty = (c.xs % 32) + .5, (c.ys % 32) + .5
    glaze = .62 + pnoise(FT, FT, 8, g) * .15 + np.where((tx < 1.2) | (ty < 1.2), .2, 0) - np.where((tx > 31) | (ty > 31), .25, 0)
    c.paint(np.ones((FT, FT), bool), 'cream', glaze, noline=True)
    dc = np.min([np.hypot(tx - a, ty - b) for a in (0, 32) for b in (0, 32)], axis=0)
    c.paint((dc < 7) & (dc >= 4.5), 'terra', .55, noline=True)
    c.paint(dc < 3, 'terra', .4, noline=True)
    d = np.abs(tx - 16) + np.abs(ty - 16)
    petal = (np.abs(tx - 16) < 2.2) & (np.abs(ty - 16) < 11) | (np.abs(ty - 16) < 2.2) & (np.abs(tx - 16) < 11)
    c.paint((d < 13) & (d > 10.5) | petal, 'blue', .45 + (glaze - .62) * .5, noline=True)
    c.paint(d < 3.5, 'gold', .55, noline=True)
    return c

def floor_terrazzo():
    c = Canvas(FT, FT); g = rng(13)
    c.paint(np.ones((FT, FT), bool), 'terraz', .6 + pnoise(FT, FT, 8, g) * .2, noline=True)
    for _ in range(120):
        x, y = int(g.integers(0, FT)), int(g.integers(0, FT)); r = g.uniform(.6, 1.6)
        m = ((((c.xs - x + FT // 2) % FT) - FT // 2) ** 2 + (((c.ys - y + FT // 2) % FT) - FT // 2) ** 2) <= r * r
        mat = ['stone', 'stone', 'sand', 'terra', 'marbleV', 'iron2'][int(g.integers(0, 6))]
        c.paint(m, mat, g.uniform(.45, .8), noline=True)
    c.paint(((c.xs % 64) == 0) | ((c.ys % 64) == 0), 'terraz', .15, noline=True)
    return c

def floor_marble():
    c = Canvas(FT, FT); g = rng(14)
    n = pnoise(FT, FT, 16, g) * 3 + pnoise(FT, FT, 4, g)
    vein = np.abs(np.sin((c.xs * .7 + c.ys * .4) / 64 * np.pi * 2 + n * 2.2)) < .08
    lit = .62 + pnoise(FT, FT, 8, g) * .15
    c.paint(np.ones((FT, FT), bool), 'marbleW', lit, noline=True)
    c.paint(vein, 'marbleV', .6, noline=True)
    tx, ty = c.xs % 64, c.ys % 64
    c.paint((tx == 0) | (ty == 0), 'marbleV', .3, noline=True)
    dia = (np.abs(((c.xs + 32) % 64) - 32) + np.abs(((c.ys + 32) % 64) - 32)) < 9
    dia = (np.abs(((c.xs) % 64) - 0 + 0) >= 0) & ((np.minimum(c.xs % 64, 64 - c.xs % 64) + np.minimum(c.ys % 64, 64 - c.ys % 64)) < 9)
    c.paint(dia, 'onyx', .4 + ((c.xs % 64 + c.ys % 64) % 64 < 32) * .3, noline=True)
    c.paint((np.minimum(c.xs % 64, 64 - c.xs % 64) + np.minimum(c.ys % 64, 64 - c.ys % 64)) < 2.5, 'gold', .7, noline=True)
    return c

def floor_terracotta():
    c = Canvas(FT, FT); g = rng(15)
    tone = np.repeat(np.repeat(g.uniform(-.14, .14, (FT // 16, FT // 16)), 16, 0), 16, 1)
    tx, ty = c.xs % 16, c.ys % 16
    lit = .52 + tone + pnoise(FT, FT, 4, g) * .14 + np.where((tx < 2) | (ty < 2), .14, 0) - np.where((tx > 13) | (ty > 13), .14, 0)
    c.paint(np.ones((FT, FT), bool), 'terra', lit, noline=True)
    c.paint((tx == 15) | (ty == 15), 'mortar', .25, noline=True)
    return c

def floor_kitchen():
    c = Canvas(FT, FT); g = rng(16)
    tx, ty = c.xs % 16, c.ys % 16
    alt = ((c.xs // 16) + (c.ys // 16)) % 2
    lit = .45 + alt * .15 + pnoise(FT, FT, 4, g) * .12 + np.where((tx < 1) | (ty < 1), .15, 0)
    c.paint(np.ones((FT, FT), bool), 'tileK', lit, noline=True)
    c.paint((tx == 15) | (ty == 15), 'tileK', .05, noline=True)
    return c

def sidewalk():
    c = Canvas(FT, 64); g = rng(17)
    tx, ty = c.xs % 32, c.ys % 32
    c.paint(np.ones((64, FT), bool), 'stone', .62 + pnoise(64, FT, 4, g) * .2 + np.where((tx < 1) | (ty < 1), .12, 0), noline=True)
    c.paint((tx == 31) | (ty == 31), 'stone', .2, noline=True)
    return c

def curb():
    c = Canvas(FT, 32); g = rng(18)
    c.paint(c.rect(0, 0, FT, 20), 'stone', .62 + pnoise(32, FT, 4, g) * .18, noline=True)
    c.paint(c.rect(0, 18, FT, 23), 'stone', np.where(c.ys == 18, .85, .3), noline=True)
    c.paint(c.rect(0, 23, FT, 32), 'iron2', .35 + pnoise(32, FT, 2, g) * .2, noline=True)
    c.paint(c.rect(8, 28, 24, 30) | c.rect(72, 28, 88, 30), 'sand', .8, noline=True)
    return c

# ======================= BACK WALLS (128 x 64 strips that repeat) =======================
def cornice(c):
    c.paint(c.rect(0, 0, c.w, 6), 'oakD', np.where(c.ys == 1, .9, np.where(c.ys >= 4, .2, .5)), noline=True)
def skirting(c, mat='oakD'):
    c.paint(c.rect(0, 58, c.w, 64), mat, np.where(c.ys == 58, .85, .3), noline=True)

def wall_cream():
    c = Canvas(FT, 64); g = rng(20); cornice(c)
    c.paint(c.rect(0, 6, FT, 40), 'paper', .62 + pnoise(64, FT, 4, g) * .12 - ((c.xs % 8) == 0) * .14 - (c.ys == 6) * .3, noline=True)
    c.paint(c.rect(0, 40, FT, 44), 'oak', np.where(c.ys == 40, .9, .45), noline=True)
    px = c.xs % 32
    c.paint(c.rect(0, 44, FT, 58), 'oak', .35, noline=True)
    panel = (px > 3) & (px < 29) & (c.ys > 46) & (c.ys < 56)
    c.paint(panel, 'oak', .5 + (c.ys == 47) * -.25 + (px == 4) * -.2 + (c.ys == 55) * .3, noline=True)
    skirting(c); return c

def wall_azulejo():
    c = Canvas(FT, 64); g = rng(21); cornice(c)
    c.paint(c.rect(0, 6, FT, 22), 'plaster', .55 + pnoise(64, FT, 4, g) * .3 - (c.ys == 6) * .3, noline=True)
    c.paint(c.rect(0, 22, FT, 24), 'blue', .45, noline=True)
    tx, ty = (c.xs % 16) + .5, ((c.ys - 24) % 16) + .5
    d = np.hypot(tx - 8, ty - 8); dc = np.min([np.hypot(tx - a, ty - b) for a in (0, 16) for b in (0, 16)], axis=0)
    motif = (np.abs(d - 5.5) < 1.1) | (dc < 3.2) | ((np.abs(tx - 8) + np.abs(ty - 8)) < 2.2)
    tiles = c.rect(0, 24, FT, 56)
    gl = .62 + pnoise(64, FT, 4, g) * .2 + np.where((tx < 1.2) | (ty < 1.2), .25, 0) - np.where((tx > 15) | (ty > 15), .3, 0)
    c.paint(tiles, 'glaze', gl, noline=True); c.paint(tiles & motif, 'blue', .45 + (gl - .62) * .6, noline=True)
    c.paint(c.rect(0, 56, FT, 58), 'blue', .3, noline=True); skirting(c); return c

def wall_brick():
    c = Canvas(FT, 64); g = rng(22); cornice(c)
    c.paint(c.rect(0, 6, FT, 58), 'mortar', .5, noline=True)
    tone = g.uniform(-.15, .15, (13, 9))
    for row in range(13):
        y0 = 6 + row * 4 * 1
        y0 = 6 + row * 4
        if y0 >= 58: break
        off = 8 if row % 2 else 0
        for k in range(9):
            x0 = k * 16 - off
            m = c.rect(max(0, x0), y0, min(FT, x0 + 15), min(58, y0 + 3)) | (c.rect(FT + x0, y0, FT, min(58, y0 + 3)) if x0 < 0 else False)
            c.paint(m, 'brick', np.clip(.5 + tone[row, k] + (c.ys == y0) * .18 + pnoise(64, FT, 2, g) * .12, 0, 1), noline=True)
    skirting(c); return c

def wall_modern():
    c = Canvas(FT, 64); g = rng(23)
    c.paint(c.rect(0, 0, FT, 6), 'onyx', np.where(c.ys == 1, .8, .3), noline=True)
    c.paint(c.rect(0, 6, FT, 38), 'formica', .7 + pnoise(64, FT, 8, g) * .1 - (c.ys == 6) * .3, noline=True)
    c.paint(c.rect(0, 38, FT, 42), 'onyx', .3, noline=True)
    sl = c.xs % 8
    c.paint(c.rect(0, 42, FT, 58), 'oak', .55 + (sl == 0) * .3 - (sl == 7) * .35 + pnoise(64, FT, 2, g) * .1, noline=True)
    skirting(c, 'onyx'); return c

def wall_damask():
    c = Canvas(FT, 64); g = rng(24); cornice(c)
    c.paint(c.rect(0, 6, FT, 38), 'green', .55 + pnoise(64, FT, 4, g) * .1, noline=True)
    tx, ty = c.xs % 16, (c.ys - 6) % 16
    sh = ((c.ys - 6) // 16) % 2 * 8
    tx = (c.xs + sh) % 16
    m = (np.abs(tx - 8) * 1.2 + np.abs(ty - 8)) < 6
    m &= ~((np.abs(tx - 8) * 1.2 + np.abs(ty - 8)) < 3.5)
    c.paint(m & c.rect(0, 7, FT, 37), 'gold', .5, noline=True)
    c.paint(((np.abs(tx - 8) < 1) & (np.abs(ty - 8) < 1.5)) & c.rect(0, 7, FT, 37), 'gold', .8, noline=True)
    c.paint(c.rect(0, 38, FT, 41), 'gold', np.where(c.ys == 38, .9, .45), noline=True)
    px = c.xs % 32
    c.paint(c.rect(0, 41, FT, 58), 'oakD', .35, noline=True)
    c.paint((px > 3) & (px < 29) & (c.ys > 43) & (c.ys < 56), 'oakD', .55 + (c.ys == 44) * -.3 + (c.ys == 55) * .3, noline=True)
    skirting(c); return c

def wall_kitchen():
    c = Canvas(FT, 64); g = rng(25)
    c.paint(c.rect(0, 0, FT, 6), 'iron2', np.where(c.ys == 1, .8, .35), noline=True)
    row = (c.ys - 6) // 8; tx = (c.xs + (row % 2) * 8) % 16; ty = (c.ys - 6) % 8
    c.paint(c.rect(0, 6, FT, 60), 'tileW', .62 + (ty == 1) * .25 - ((tx == 15) | (ty == 7)) * .45 + pnoise(64, FT, 4, g) * .08, noline=True)
    c.paint(c.rect(0, 60, FT, 64), 'iron2', .35, noline=True); return c

def divider():
    """the wall between the dining room and the kitchen, seen from above (32 x 224)"""
    c = Canvas(32, 224); g = rng(26)
    c.paint(c.rect(0, 0, 32, 224), 'oakD', .3 + pnoise(224, 32, 4, g) * .2 + (c.xs < 3) * .35 - (c.xs > 28) * .2)
    return c

def front_wall():
    c = Canvas(64, 32); g = rng(27)
    c.paint(c.rect(0, 0, 64, 32), 'oakD', .3 + pnoise(32, 64, 4, g) * .15 + (c.ys < 4) * .4 - (c.ys > 28) * .2, noline=True)
    return c

def door_mat():
    c = Canvas(32, 32); g = rng(28)
    c.paint(c.rect(0, 0, 32, 32), 'terra', .3, noline=True)
    c.paint(c.rect(2, 2, 30, 30), 'straw', .5 + ((c.xs + c.ys) % 4 < 2) * .15 + ((c.ys % 6) == 0) * -.2, noline=True)
    return c

# ======================= CHAIRS =======================
CH = {'tasca': ('oak', 'straw', 'slats', 3), 'tratt': ('oak', 'red', 'slats', 3),
      'moder': ('iron2', 'formica', 'shell', 2), 'luxo': ('gold', 'velvet', 'pad', 3)}
def chair(style='tasca', d='down', layer=None):
    """32 x 32. down = seen from the front (backrest at the top), up = from behind,
    right = from the side with the backrest on the left (the sitter faces right).
    A chair seen from behind has the sitter between its seat and its backrest: layer='seat'
    or layer='back' draws only one of them."""
    wood, seat, back, lw = CH[style]
    c = Canvas(32, 32)
    weave = (((c.xs // 2) + (c.ys // 2)) % 2) * .14 if seat == 'straw' else 0
    tuft = ((c.xs % 6 == 3) & (c.ys % 4 == 2)) * -.25 if seat == 'velvet' else 0
    sl = .62 + weave + tuft
    if d == 'down':
        c.cast(c.rect(6, 27, 30, 31), .35)
        for lx in (5, 27 - lw): c.paint(c.rect(lx, 18, lx + lw, 30), wood, c.cyl_x(lx, lx + lw), part=1)
        c.paint(c.rect(5, 14, 27, 20), seat, sl - (c.ys >= 18) * .3, part=2)
        if back == 'slats':
            for lx in (5, 24): c.paint(c.rect(lx, 1, lx + 3, 15), wood, c.cyl_x(lx, lx + 3), part=3)
            c.paint(c.rect(5, 2, 27, 6), wood, np.where(c.ys == 2, .9, .55), part=4)
            c.paint(c.rect(13, 6, 19, 13), wood, c.cyl_x(13, 19, .3, .8), part=4)
        elif back == 'shell':
            c.paint(c.rect(6, 2, 26, 15) & ~(c.rect(6, 2, 8, 4) | c.rect(24, 2, 26, 4)), seat, .55 + (c.ys < 5) * .3 - (c.xs > 22) * .2, part=3)
        else:
            c.paint(c.ell(16, 8, 11, 8), wood, c.sphere(16, 8, 11, 8) * .9, part=3)
            c.paint(c.ell(16, 8, 8.5, 5.8), seat, .5 + c.sphere(16, 8, 8.5, 5.8) * .4 + tuft, part=4)
    elif d == 'up':
        c.cast(c.rect(6, 27, 30, 31), .35)
        if layer != 'back': c.paint(c.rect(5, 6, 27, 12), seat, .75 + weave + tuft, part=1)
        if layer == 'seat': return c
        for lx in (5, 27 - lw): c.paint(c.rect(lx, 4, lx + lw, 31), wood, c.cyl_x(lx, lx + lw, .2, .6), part=2)
        if back == 'slats':
            c.paint(c.rect(5, 12, 27, 16), wood, np.where(c.ys == 12, .75, .4), part=3)
            c.paint(c.rect(13, 16, 19, 24), wood, c.cyl_x(13, 19, .2, .6), part=3)
            c.paint(c.rect(5, 23, 27, 25), wood, .35, part=3)
        elif back == 'shell':
            c.paint(c.rect(6, 11, 26, 25), seat, .35 + (c.ys < 13) * .3 - (c.xs > 22) * .15, part=3)
        else:
            c.paint(c.ell(16, 18, 11, 8), wood, c.sphere(16, 18, 11, 8) * .7, part=3)
            c.paint(c.ell(16, 18, 8.5, 5.8), seat, .3 + c.sphere(16, 18, 8.5, 5.8) * .3, part=4)
    else:
        c.cast(c.rect(6, 28, 30, 31), .35)
        c.paint(c.rect(27 - lw, 18, 27, 30), wood, c.cyl_x(25, 28, .2, .55), part=1)
        c.paint(c.rect(6, 15, 28, 20), seat, sl - (c.ys >= 18) * .32, part=2)
        c.paint(c.rect(5, 18, 5 + lw, 30), wood, c.cyl_x(5, 5 + lw), part=3)
        if back == 'slats':
            c.paint(c.rect(5, 1, 9, 19), wood, c.cyl_x(5, 9), part=3)
            c.paint(c.rect(9, 4, 11, 15), wood, .4, part=3)
        elif back == 'shell':
            c.paint(c.rect(5, 2, 9, 18) | c.rect(5, 14, 12, 18), seat, .55 + (c.xs < 6) * .3, part=3)
        else:
            c.paint(c.rect(4, 1, 10, 18), wood, c.cyl_x(4, 10), part=3)
            c.paint(c.rect(6, 3, 10, 16), seat, .55, part=4)
        if d == 'left': c = flip(c)
    return c

# ======================= TABLES =======================
def chianti(c, x, y, part):
    c.paint(c.ell(x, y + 16, 6, 6), 'straw', c.sphere(x, y + 16, 6, 6) * .9, part=part)
    c.paint(c.ell(x, y + 16, 6, 6) & ((c.xs + c.ys) % 3 == 0), 'straw', .25, part=part)
    c.paint(c.rect(x - 2, y, x + 2, y + 11), 'bottle', c.cyl_x(x - 2, x + 2, .3, .9), part=part + 1)
    c.paint(c.rect(x - 2, y - 6, x + 2, y + 1), 'wax', c.cyl_x(x - 2, x + 2, .4, 1), part=part + 2)
    c.paint(c.rect(x - 3, y, x - 1, y + 4) | c.rect(x + 1, y + 1, x + 3, y + 3), 'wax', .8, part=part + 2)
    c.paint(c.ell(x, y - 6.5, 1.6, 2.5), 'flame', .8, part=part + 3, noline=True)

def table_check(W=76, D=30, candle=True):
    """W x D checked cloth top with a hanging drape and folds"""
    H = D + 22; c = Canvas(W, H)
    c.cast(c.rect(8, H - 8, W - 4, H - 1), .45)
    for lx in (8, W - 12): c.paint(c.rect(lx, D + 4, lx + 5, H - 4), 'oakD', c.cyl_x(lx, lx + 5), part=1)
    top = c.rect(2, 2, W - 2, D); drape = c.rect(2, D, W - 2, D + 10)
    sq = (((c.xs - 2) // 8) + ((c.ys - 2) // 8)) % 2 == 0; col = ((c.xs - 2) // 8) % 2 == 0
    c.paint(top & sq, 'red', .62, part=2); c.paint(top & ~sq, 'cream', .7, part=2)
    fold = .38 + .22 * np.sin((c.xs - 2) * .8)
    c.paint(drape & col, 'red', fold, part=3); c.paint(drape & ~col, 'cream', fold + .05, part=3)
    c.paint(c.rect(2, 2, W - 2, 3), 'cream', .95, part=2)
    if candle: chianti(c, W // 2, D // 2 - 8, 5)
    return c

def table_round():
    W, H = 80, 70; c = Canvas(W, H); g = rng(40)
    c.cast(c.ell(42, 62, 30, 7), .5)
    c.paint(c.rect(34, 40, 46, 62), 'oakD', c.cyl_x(34, 46), part=1)
    c.paint(c.ell(40, 62, 14, 4), 'oakD', .35 + (c.xs < 36) * .3, part=2)
    c.paint(c.ell(40, 30, 38, 22) & ~c.ell(40, 24, 38, 22), 'oak', .25 + (c.xs < 30) * .15, part=3)
    top = c.ell(40, 24, 38, 22)
    r = np.sqrt(((c.xs + .5 - 40) / 38) ** 2 + ((c.ys + .5 - 24) / 22) ** 2)
    grain = noise(H, W * 4, 3, g)[:, ::4][:, :W]
    lit = .62 + (grain - .5) * .35 - ((c.ys - 4) % 9 == 0) * .35 + np.where(r > .9, (r - .9) * -4, 0) + np.where((r > .82) & (c.ys < 20), .2, 0)
    c.paint(top, 'oak', np.clip(lit, 0, 1), part=4)
    run = top & c.rect(0, 18, W, 30)
    c.paint(run, 'linen', .7 + ((c.xs + c.ys) % 3 == 0) * -.08 - (c.ys == 29) * .3, part=5)
    c.paint(run & ((c.ys == 20) | (c.ys == 27)), 'blue', .5, part=5)
    c.paint(c.rect(36, 13, 44, 24) | c.ell(40, 23.5, 4.5, 2), 'clay', c.cyl_x(36, 44, .2, .9), part=6)
    c.paint(c.ell(40, 13.5, 4, 1.6), 'clay', .1, part=7)
    c.paint((np.abs(np.hypot(c.xs + .5 - 44, c.ys + .5 - 18) - 3) < 1.1) & (c.xs >= 44), 'clay', .55, part=6)
    return c

def table_long():
    W, H = 148, 76; c = Canvas(W, H); g = rng(41)
    c.cast(c.rect(6, H - 8, W - 2, H - 1), .45)
    for lx in (6, W - 12): c.paint(c.rect(lx, 56, lx + 6, H - 3), 'oakD', c.cyl_x(lx, lx + 6), part=1)
    grain = noise(H, W * 4, 3, g)[:, ::4][:, :W]
    c.paint(c.rect(2, 52, W - 2, 60), 'oakD', .35 + (c.ys == 52) * .4, part=2)
    c.paint(c.rect(2, 2, W - 2, 52), 'oak', np.clip(.6 + (grain - .5) * .35 - ((c.ys - 2) % 10 == 0) * .35 + (c.ys == 2) * .3 - ((c.xs % 37) == 0) * .25, 0, 1), part=3)
    c.paint(c.rect(68, 16, 78, 34) | c.ell(73, 33, 6, 2.5), 'clay', c.cyl_x(68, 78, .2, .9), part=5)
    c.paint(c.ell(73, 16.5, 5, 2), 'clay', .1, part=6)
    for bx in (38, 108):
        c.paint(c.ell(bx, 27, 10, 6), 'straw', c.sphere(bx, 27, 10, 6) * .8 + ((c.xs + c.ys) % 3 == 0) * -.15, part=5)
        for k in range(3): c.paint(c.ell(bx - 4 + k * 4, 24 + k % 2 * 2, 3, 2), 'crust', c.sphere(bx - 4 + k * 4, 24, 3, 2) * .9, part=6)
    return c

def bench():
    W, H = 148, 22; c = Canvas(W, H)
    c.cast(c.rect(4, 17, W - 2, 21), .35)
    for lx in (6, W // 2 - 2, W - 10): c.paint(c.rect(lx, 10, lx + 4, 20), 'oakD', c.cyl_x(lx, lx + 4), part=1)
    c.paint(c.rect(2, 2, W - 2, 12), 'oak', np.where(c.ys < 4, .9, np.where(c.ys > 8, .35, .6)), part=2)
    return c

def table_white():
    W, H = 80, 64; c = Canvas(W, H)
    c.cast(c.rect(8, 56, W - 4, 63), .4)
    for lx in (8, 70): c.paint(c.rect(lx, 44, lx + 3, 60), 'iron2', .4, part=1)
    c.paint(c.rect(2, 2, W - 2, 44), 'formica', .78 - ((c.ys - 2) / 42) * .2 + (c.ys == 2) * .2, part=2)
    c.paint(c.rect(2, 44, W - 2, 48), 'chrome', np.where(c.ys == 44, .9, .45), part=3)
    c.paint(c.rect(36, 12, 44, 28), 'onyx', c.cyl_x(36, 44, .2, .8), part=4)
    c.paint(c.rect(39, 6, 41, 13), 'leaf', .5, part=5)
    c.paint(c.ell(40, 5, 3.5, 3), 'curtain', c.sphere(40, 5, 3.5, 3), part=6)
    return c

def table_gala():
    W, H = 80, 74; c = Canvas(W, H)
    c.cast(c.ell(42, 68, 36, 6), .5)
    for i in range(2, 78):
        dx = abs(i + .5 - 40) / 38
        if dx > 1: continue
        top = 24 + int(np.sqrt(1 - dx * dx) * 20); bot = 60 + int(np.sqrt(1 - dx * dx) * 6)
        col = (c.xs == i) & (c.ys >= top) & (c.ys <= bot)
        c.paint(col, 'linen', .45 + .3 * np.sin(i * .9) + (i < 30) * .1, part=1)
        c.paint((c.xs == i) & (c.ys == bot), 'gold', .7, part=2)
    c.paint(c.ell(40, 24, 38, 20), 'linen', .85, part=3)
    c.paint(c.ell(40, 22, 22, 9), 'linen', .97, part=3, noline=True)
    for cx in (26, 54):
        c.paint(c.rect(cx - 1, 10, cx + 2, 22), 'gold', .7, part=4)
        c.paint(c.rect(cx - 1, 2, cx + 2, 10), 'wax', .8, part=5)
        c.paint(c.ell(cx + .5, 1, 1.5, 2.2), 'flame', .8, part=6, noline=True)
    c.paint(c.rect(37, 14, 44, 24), 'glaze', c.cyl_x(37, 44, .4, .95), part=4)
    for fx, fy, m in ((38, 11, 'leaf'), (42, 10, 'curtain'), (36, 10, 'curtain'), (40, 8, 'curtain'), (44, 12, 'leaf')):
        c.paint(c.ell(fx, fy, 2.5, 2.2), m, c.sphere(fx, fy, 2.5, 2.2), part=5)
    return c

def table_bistro():
    W, H = 64, 54; c = Canvas(W, H)
    c.cast(c.ell(34, 49, 16, 4), .5)
    c.paint(c.rect(29, 28, 35, 48), 'gold', c.cyl_x(29, 35, .3, .9), part=1)
    c.paint(c.ell(32, 48, 11, 3.5), 'gold', .5 + (c.xs < 28) * .3, part=2)
    c.paint(c.ell(32, 22, 30, 16) & ~c.ell(32, 18, 30, 16), 'marbleV', .3, part=3)
    g = rng(42); n = noise(H, W, 6, g)
    c.paint(c.ell(32, 18, 30, 16), 'marbleW', .75 + c.sphere(32, 18, 30, 16) * .1 + (np.abs(np.sin(c.xs * .3 + c.ys * .5 + n * 4)) < .1) * -.35, part=4)
    c.paint(c.rect(31, 4, 34, 14), 'wax', c.cyl_x(31, 34, .5, 1), part=5)
    c.paint(c.rect(29, 13, 36, 16), 'gold', .7, part=5)
    c.paint(c.ell(32.5, 3, 1.5, 2.2), 'flame', .8, part=6, noline=True)
    return c

def sofa(top=True):
    W, H = 92, 44; c = Canvas(W, H)
    tuft = ((c.xs % 12 == 6) & (c.ys % 8 == 4)) * -.3
    if top:   # backrest at the top, seat towards the table
        c.paint(c.rect(2, 2, W - 2, 22), 'leather', .62 + tuft - (c.ys > 18) * .25 + (c.ys < 4) * .25, part=1)
        c.paint(c.rect(2, 22, W - 2, 38), 'leather', .7 - (c.ys > 33) * .35 + (c.ys == 22) * .2, part=2)
        c.paint(c.rect(2, 38, W - 2, 42), 'chrome', np.where(c.ys == 38, .9, .4), part=3)
    else:     # seen from behind: seat far, high backrest near
        c.paint(c.rect(2, 2, W - 2, 12), 'leather', .75, part=1)
        c.paint(c.rect(2, 12, W - 2, 40), 'leather', .45 + tuft - (c.ys > 34) * .2 + (c.ys < 14) * .25, part=2)
        c.paint(c.rect(2, 40, W - 2, 43), 'chrome', np.where(c.ys == 40, .9, .4), part=3)
    for x0 in (0, W - 6): c.paint(c.rect(x0, 0 if top else 8, x0 + 6, 42), 'leather', c.cyl_x(x0, x0 + 6, .3, .8), part=4)
    return c

def table_booth():
    W, H = 88, 54; c = Canvas(W, H)
    c.cast(c.rect(10, 46, W - 6, 53), .4)
    c.paint(c.rect(40, 40, 48, 52), 'chrome', c.cyl_x(40, 48), part=1)
    c.paint(c.rect(2, 2, W - 2, 38), 'formica', .75 + (c.ys == 2) * .2 - ((c.xs - c.ys) % 23 == 0) * .1, part=2)
    c.paint(c.rect(2, 38, W - 2, 42), 'chrome', np.where(c.ys == 38, .9, .4), part=3)
    c.paint(c.rect(38, 12, 50, 24), 'chrome', c.cyl_x(38, 50), part=4)
    c.paint(c.rect(40, 14, 48, 23), 'formica', .9, part=5)
    for x0, m in ((66, 'curtain'), (72, 'gold')): c.paint(c.rect(x0, 12, x0 + 4, 24), m, c.cyl_x(x0, x0 + 4, .3, .9), part=4)
    return c

def pizza():
    W, H = 24, 15; c = Canvas(W, H); g = rng(60)
    c.paint(c.ell(12, 8, 11.5, 6.5), 'plate', .7 + (c.ys < 5) * .2, part=1)
    c.paint(c.ell(12, 7.5, 9.5, 5.2), 'crust', c.sphere(12, 7.5, 9.5, 5.2) * .8 + .1, part=2)
    c.paint(c.ell(12, 7.5, 7.3, 3.8), 'sauce', .55, part=3, noline=True)
    c.paint(c.ell(12, 7.5, 7.3, 3.8) & (noise(H, W, 2, g) > .45), 'cheese', .55 + noise(H, W, 1, g) * .3, part=3, noline=True)
    for px, py in [(9, 6.5), (15, 6), (12, 9), (16, 9)]:
        c.paint(c.ell(px, py, 1.7, 1.1), 'pepp', c.sphere(px, py, 1.7, 1.1) * .9, part=4)
    return c

def plate():
    W, H = 24, 15; c = Canvas(W, H)
    c.paint(c.ell(12, 8, 11.5, 6.5), 'plate', .7 + (c.ys < 5) * .2, part=1)
    c.paint(c.ell(12, 8, 7, 3.8), 'plate', .5, part=2, noline=True)
    c.paint(c.rect(4, 5, 21, 6), 'iron2', .8, part=3); return c

# ======================= DECOR (floor) =======================
def pot(c, x0, x1, y0, y1, mat='clay', part=1):
    c.paint(c.rect(x0 + 1, y0 + 3, x1 - 1, y1), mat, c.cyl_x(x0, x1, .2, .85), part=part)
    c.paint(c.rect(x0, y0, x1, y0 + 4), mat, np.where(c.ys == y0, .95, .6), part=part + 1)

def foliage(c, clumps, g, part=3, ramp='leaf'):
    leafy = noise(c.h, c.w, 2, g)
    for cx, cy, r in clumps:
        c.paint(c.ell(cx, cy, r, r * .95), ramp, np.clip(c.sphere(cx, cy, r, r) * .85 + (leafy - .5) * .5, 0, 1), part=part)

def d_plant():
    c = Canvas(36, 58); g = rng(50)
    c.cast(c.ell(20, 55, 12, 3), .5); pot(c, 9, 27, 36, 55)
    foliage(c, [(18, 22, 13), (11, 28, 8), (25, 27, 8), (18, 11, 9), (10, 17, 7), (27, 16, 7)], g)
    return c

def d_ficus():
    c = Canvas(40, 84); g = rng(51)
    c.cast(c.ell(22, 81, 12, 3), .5); pot(c, 11, 29, 62, 81, 'formica')
    c.paint(c.rect(19, 30, 22, 63), 'oakD', c.cyl_x(19, 22), part=2)
    foliage(c, [(20, 26, 13), (11, 34, 9), (29, 33, 9), (20, 12, 10), (12, 20, 8), (29, 19, 8), (20, 44, 8)], g)
    return c

def d_olive():
    c = Canvas(48, 80); g = rng(52)
    c.cast(c.ell(26, 77, 15, 4), .5); pot(c, 10, 38, 54, 77, 'terra')
    c.paint(c.rect(22, 30, 26, 55) | c.rect(25, 34, 31, 37), 'stone', c.cyl_x(22, 26, .2, .7), part=2)
    leafy = noise(80, 48, 1, g)
    for cx, cy, r in [(24, 22, 17), (12, 28, 9), (36, 28, 9), (24, 10, 11)]:
        m = c.ell(cx, cy, r, r * .85) & (leafy > .25)
        c.paint(m, 'leaf', np.clip(c.sphere(cx, cy, r, r) * .6 + .1 + (leafy - .5) * .4, 0, 1) * .8, part=3)
    olives = np.zeros((80, 48), bool)
    for _ in range(10): olives |= c.ell(g.uniform(10, 38), g.uniform(8, 34), 1.2, 1.6)
    c.paint(olives, 'onyx', .6, part=4)
    return c

def d_barrel():
    c = Canvas(32, 44); g = rng(53)
    c.cast(c.ell(17, 41, 13, 3), .5)
    body = c.rect(3, 8, 29, 41) | c.ell(16, 40, 13, 3)
    bulge = 1 - ((c.ys - 24) / 18) ** 2
    c.paint(body, 'oak', np.clip(c.cyl_x(3, 29) * .9 + bulge * .1 - ((c.xs % 5) == 0) * .2, 0, 1), part=1)
    for y in (12, 22, 32): c.paint(c.rect(3, y, 29, y + 2), 'iron2', np.where(c.ys == y, .8, .4), part=2)
    c.paint(c.ell(16, 8, 13, 4), 'oak', .55 + ((c.xs % 5) == 0) * -.2, part=3)
    c.paint(c.ell(16, 8, 10, 3), 'oakD', .55, part=4)
    c.paint(c.rect(14, 26, 19, 29), 'gold', .7, part=5); c.paint(c.rect(16, 29, 18, 33), 'gold', .5, part=5)
    return c

def d_wine_rack():
    c = Canvas(68, 80); g = rng(54)
    c.cast(c.rect(4, 74, 66, 79), .45)
    c.paint(c.rect(2, 2, 66, 76), 'oakD', .35, part=1)
    c.paint(c.rect(2, 2, 66, 6), 'oak', .8, part=2)
    for y0 in range(8, 72, 12):
        c.paint(c.rect(4, y0 + 10, 64, y0 + 12), 'oak', .6, part=3)
        for x0 in range(8, 62, 9):
            m = 'bottle' if g.random() < .6 else 'velvet'
            c.paint(c.ell(x0 + 1, y0 + 5, 4, 4), m, c.sphere(x0 + 1, y0 + 5, 4, 4), part=4)
            c.paint(c.ell(x0 + 1, y0 + 5, 1.6, 1.6), 'gold' if m == 'velvet' else 'wax', .6, part=5)
    return c

def d_jukebox():
    c = Canvas(36, 64); g = rng(55)
    c.cast(c.rect(4, 58, 34, 63), .45)
    body = c.rect(3, 18, 33, 60) | c.ell(18, 18, 15, 14)
    c.paint(body, 'purple', c.cyl_x(3, 33, .25, .8), part=1)
    for k, m in enumerate(['neonP', 'gold', 'neonC', 'screen']):
        ring = c.ell(18, 18, 13 - k * 2.4, 12 - k * 2.4) & ~c.ell(18, 18, 11.6 - k * 2.4, 10.6 - k * 2.4) & (c.ys < 30)
        c.paint(ring, m, .75, part=2 + k)
    c.paint(c.rect(9, 18, 27, 30), 'lamp', .6 + (c.ys < 20) * .3, part=6)
    for x in range(11, 26, 3): c.paint(c.rect(x, 21, x + 2, 28), 'velvet', .5, part=7)
    c.paint(c.rect(6, 32, 30, 34), 'chrome', .8, part=6)
    c.paint(c.rect(7, 36, 29, 54), 'chrome', .35 + ((c.xs % 3) == 0) * .4, part=6)
    return c

def d_arcade():
    c = Canvas(36, 68)
    c.cast(c.rect(4, 62, 34, 67), .45)
    c.paint(c.rect(3, 2, 33, 64), 'shirtB', c.cyl_x(3, 33, .25, .75), part=1)
    c.paint(c.rect(5, 4, 31, 12), 'neonP', .6 + ((c.xs // 3) % 2) * .2, part=2)
    c.paint(c.rect(6, 16, 30, 36), 'onyx', .3, part=2)
    c.paint(c.rect(8, 18, 28, 34), 'screen', .45 + ((c.ys % 2) == 0) * .1, part=3)
    c.paint(c.rect(12, 22, 16, 26), 'neonP', .7, part=4); c.paint(c.rect(20, 27, 24, 31), 'gold', .7, part=4)
    c.paint(c.rect(4, 38, 32, 46), 'onyx', .35 + (c.ys == 38) * .3, part=2)
    c.paint(c.ell(11, 41, 2.5, 2), 'red', .7, part=4); c.paint(c.rect(10, 37, 12, 41), 'iron2', .6, part=4)
    for bx, m in ((20, 'gold'), (25, 'neonC'), (29, 'red')): c.paint(c.ell(bx, 42, 1.8, 1.5), m, .7, part=4)
    c.paint(c.rect(14, 52, 22, 56), 'gold', .6, part=2)
    return c

def d_aquarium(f=0):
    c = Canvas(68, 60); g = rng(56)
    c.cast(c.rect(4, 54, 66, 59), .45)
    c.paint(c.rect(2, 34, 66, 56), 'oakD', .4 + (c.ys == 34) * .4, part=1)
    c.paint(c.rect(6, 38, 64, 54) & ((c.xs - 6) % 20 < 18), 'oak', .5, part=2)
    c.paint(c.rect(2, 2, 66, 34), 'iron2', .3, part=3)
    tank = c.rect(4, 5, 64, 32)
    c.paint(tank, 'water', .55 + (c.ys < 10) * .25 - (c.ys > 26) * .1 + (((c.xs - c.ys * .6) % 25) < 2) * .25, part=4, noline=True)
    c.paint(c.rect(4, 28, 64, 32), 'sand', .6 + noise(60, 68, 2, g) * .3, part=4, noline=True)
    for x0, h in ((10, 18), (15, 12), (52, 20), (58, 14), (30, 9)):
        c.paint((np.abs(c.xs - x0 - np.sin(c.ys * .4 + f) * 1.2) < 1.3) & c.rect(0, 30 - h, 68, 30), 'leaf', .6, part=5, noline=True)
    for fx0, fy, sp, m in ((14, 13, 7, 'fish'), (44, 19, -5, 'fish'), (30, 10, 4, 'neonC')):
        fx = 8 + ((fx0 + f * sp - 8) % 52)
        c.paint(c.ell(fx, fy, 3.5, 2), m, .7, part=6, noline=True)
        tail = c.ell(fx - 4 * np.sign(sp), fy, 1.5, 2)
        c.paint(tail, m, .5, part=6, noline=True)
    for k in range(3): c.paint(c.rect(40, 26 - ((k * 6 + f * 3) % 20), 41, 27 - ((k * 6 + f * 3) % 20)), 'glaze', 1, part=7, noline=True)
    c.paint(c.rect(4, 5, 64, 6), 'glaze', .9, part=7, noline=True)
    return c

def d_lamp():
    c = Canvas(28, 76)
    c.cast(c.ell(15, 73, 9, 2.5), .5)
    c.paint(c.rect(13, 22, 16, 72), 'gold', c.cyl_x(13, 16), part=1)
    c.paint(c.ell(14, 72, 8, 2.5), 'gold', .5 + (c.xs < 11) * .3, part=2)
    shade = c.rect(4, 4, 24, 22) & ~(c.rect(4, 4, 7, 8) & (c.xs - 4 < 3 - (c.ys - 4) * .7)) & ~(c.rect(21, 4, 24, 8) & (24 - c.xs < 3 - (c.ys - 4) * .7))
    shade = c.rect(4, 4, 24, 22) & (np.abs(c.xs + .5 - 14) < 6 + (c.ys - 4) * .25)
    c.paint(shade, 'lamp', .55 + ((c.xs % 3) == 0) * -.12 + c.cyl_x(4, 24, -.2, .3), part=3)
    c.paint(c.rect(5, 21, 23, 23), 'gold', .7, part=4)
    return c

def d_statue():
    c = Canvas(36, 84)
    c.cast(c.ell(20, 81, 13, 3), .5)
    c.paint(c.rect(6, 52, 30, 82), 'marbleW', c.cyl_x(6, 30, .3, .8), part=1)
    c.paint(c.rect(4, 50, 32, 55) | c.rect(4, 78, 32, 82), 'marbleW', np.where((c.ys == 50) | (c.ys == 78), .95, .5), part=2)
    c.paint(c.rect(8, 58, 28, 74), 'marbleV', .4 + ((c.xs % 5) == 0) * .2, part=2, noline=True)
    bust = c.ell(18, 44, 12, 7) | c.rect(8, 40, 28, 50)
    c.paint(bust, 'marbleW', c.sphere(18, 42, 12, 9) * .8 + .15, part=3)
    c.paint(c.rect(15, 28, 21, 38), 'marbleW', c.cyl_x(15, 21, .3, .85), part=3)
    c.paint(c.ell(18, 22, 7, 9), 'marbleW', c.sphere(18, 22, 7, 9) * .85 + .1, part=4)
    hair = c.ell(18, 18, 7.5, 6) & (c.ys < 19)
    c.paint(hair | c.ell(18, 12, 4, 3.5), 'marbleW', c.sphere(18, 16, 8, 8) * .7 + ((c.xs + c.ys) % 3 == 0) * -.15, part=5)
    c.paint(c.rect(15, 23, 17, 24) | c.rect(20, 23, 22, 24), 'marbleV', .3, part=6, noline=True)
    return c

def d_fountain(f=0):
    c = Canvas(68, 68)
    c.cast(c.ell(36, 60, 32, 8), .5)
    c.paint(c.ell(34, 52, 32, 13), 'stone', .35 + (c.xs < 20) * .2, part=1)
    c.paint(c.ell(34, 48, 32, 13), 'stone', .75, part=2)
    c.paint(c.ell(34, 48, 27, 10), 'water', .5 + ((np.hypot((c.xs - 34) / 27, (c.ys - 48) / 10) * 6 + f) % 2 < .4) * .3, part=3, noline=True)
    c.paint(c.rect(30, 22, 38, 48), 'stone', c.cyl_x(30, 38, .3, .9), part=4)
    c.paint(c.ell(34, 24, 12, 4.5), 'stone', .7, part=5)
    c.paint(c.ell(34, 23, 9, 3), 'water', .6, part=6, noline=True)
    c.paint(c.rect(32, 10, 36, 23), 'stone', c.cyl_x(32, 36, .3, .9), part=7)
    for k in range(5):
        y = 2 + ((k * 2 + f * 2) % 8)
        c.paint(c.rect(33, y, 35, y + 2), 'glaze', 1, part=8, noline=True)
        for side in (-1, 1):
            xx = 34 + side * (6 + k * 2.5); yy = 26 + k * 4 + (f % 2)
            c.paint(c.rect(int(xx), int(yy), int(xx) + 1, int(yy) + 2), 'glaze', 1, part=8, noline=True)
    return c

def d_piano():
    c = Canvas(100, 72)
    c.cast(c.ell(52, 64, 46, 7), .5)
    body = (c.rect(2, 2, 60, 54)) | c.ell(60, 28, 38, 26)
    c.paint(body & (c.xs < 98), 'lacquer', .35 + (((c.xs - c.ys) % 40) < 4) * .4 + (c.ys < 5) * .3, part=1)
    c.paint(c.rect(6, 6, 56, 50) & body, 'lacquer', .22 + (((c.xs - c.ys) % 40) < 4) * .35, part=2, noline=True)
    c.paint((np.abs(c.xs - c.ys * 1.3 - 10) < 1) & c.rect(8, 8, 56, 48), 'gold', .7, part=3, noline=True)
    c.paint(c.rect(2, 50, 62, 58), 'lacquer', .4, part=4)
    keys = c.rect(4, 52, 60, 58)
    c.paint(keys, 'plate', .85 - ((c.xs % 3) == 0) * .3, part=5, noline=True)
    c.paint(keys & c.rect(0, 52, 100, 55) & ((c.xs % 6) < 2) & ((c.xs % 21) != 5), 'onyx', .3, part=6, noline=True)
    for lx in (8, 52): c.paint(c.rect(lx, 58, lx + 4, 70), 'lacquer', c.cyl_x(lx, lx + 4), part=7)
    c.paint(c.rect(88, 40, 92, 56), 'lacquer', .4, part=7)
    c.paint(c.rect(18, 62, 46, 70), 'velvet', .55 + (c.ys == 62) * .3, part=8)
    return c

def d_rug(kind):
    c = Canvas(96, 64); g = rng(57)
    if kind == 'persa':
        c.paint(c.rect(0, 0, 96, 64), 'velvet', .5)
        c.paint(c.rect(4, 4, 92, 60), 'gold', .55 + ((c.xs + c.ys) % 4 == 0) * .2, noline=True)
        c.paint(c.rect(7, 7, 89, 57), 'blue', .3, noline=True)
        c.paint(c.rect(12, 12, 84, 52), 'red', .45 + ((((c.xs - 48) // 4) + ((c.ys - 32) // 4)) % 2) * .1, noline=True)
        d = np.abs((c.xs + .5 - 48) / 30) + np.abs((c.ys + .5 - 32) / 16)
        c.paint(d < 1, 'blue', .35, noline=True); c.paint(d < .7, 'gold', .6, noline=True); c.paint(d < .4, 'velvet', .5, noline=True)
        for cx, cy in ((18, 18), (78, 18), (18, 46), (78, 46)):
            dd = np.abs(c.xs + .5 - cx) + np.abs(c.ys + .5 - cy); c.paint(dd < 5, 'gold', .6, noline=True); c.paint(dd < 2, 'blue', .4, noline=True)
        c.paint(c.rect(7, 7, 89, 57) & ~c.rect(9, 9, 87, 55) & ((c.xs + c.ys) % 6 < 3), 'gold', .7, noline=True)
        c.paint(((c.ys < 2) | (c.ys > 61)) & ((c.xs % 2) == 0), 'linen', .8, noline=True)
    else:
        cols = ['shirtB', 'curtain', 'shirtY', 'shirtG', 'linen', 'red']
        for k in range(16):
            c.paint(c.rect(2, k * 4, 94, k * 4 + 4), cols[k % 6], .55 + ((c.xs + k) % 3 == 0) * -.15 + (c.ys % 4 == 0) * .15, noline=True)
        c.paint((c.xs < 2) | (c.xs > 93), 'linen', .7, noline=True)
    return c

# ======================= WALL PIECES (a 64 px slot, wall 64 px high) =======================
def window():
    W, H = 68, 50; c = Canvas(W, H)
    c.paint(c.rect(10, 2, 58, 42), 'oak', np.where(c.xs < 13, .75, np.where(c.ys < 5, .8, .45)), part=1)
    glass = c.rect(14, 6, 54, 38)
    sky = .85 - (c.ys - 6) / 32 * .6 + np.where(((c.xs - c.ys * .7) % 22 < 3) | ((c.xs - c.ys * .7) % 22 > 20.5), .35, 0)
    c.paint(glass, 'sky', np.clip(sky, 0, 1), part=1, noline=True)
    c.paint((c.rect(32, 6, 36, 38) | c.rect(14, 20, 54, 23)) & glass, 'oak', np.where((c.xs == 32) | (c.ys == 20), .8, .4), part=2)
    c.paint(c.rect(7, 40, 61, 46), 'oak', np.where(c.ys < 42, .9, .35), part=3)
    for x0, side in ((0, 1), (W - 16, -1)):
        t = (c.xs - x0) / 16
        cur = c.rect(x0, 0, x0 + 16, 44) & ~(((t > .75) if side == 1 else (t < .25)) & (c.ys > 22) & (c.ys < 38))
        c.paint(cur, 'curtain', np.clip(.45 + .35 * np.sin((c.xs - x0) * 1.2 + side) - c.ys / 440, 0, 1), part=4)
        c.paint(cur & (np.abs(c.ys - 30) < 3), 'gold', .7, part=5)
    c.paint(c.rect(0, 0, W, 2), 'gold', .6, part=6)
    return c

def w_painting():
    c = Canvas(44, 34)
    c.paint(c.rect(0, 0, 44, 34), 'gold', .55 + ((c.xs + c.ys) % 4 == 0) * .2 + (c.xs < 2) * .3 - (c.ys > 31) * .3, part=1)
    art = c.rect(4, 4, 40, 30)
    c.paint(art, 'sky', .8 - (c.ys - 4) / 26 * .5, part=2, noline=True)
    c.paint(art & (c.ys > 18), 'water', .5 + ((c.xs + c.ys * 3) % 7 == 0) * .3, part=2, noline=True)
    c.paint(art & c.ell(14, 21, 11, 6) & (c.ys < 21), 'leaf', .4, part=3, noline=True)
    c.paint(art & c.ell(32, 9, 3, 3), 'lamp', .9, part=3, noline=True)
    c.paint(art & (c.rect(24, 16, 32, 20) | c.rect(27, 10, 28, 16)), 'linen', .8, part=3, noline=True)
    return c

def w_chalkboard():
    c = Canvas(68, 48); g = rng(58)
    c.paint(c.rect(0, 0, 68, 46), 'oak', np.where((c.ys < 2) | (c.xs < 2), .85, .45), part=1)
    c.paint(c.rect(4, 4, 64, 42), 'slate', .45 + noise(48, 68, 4, g) * .2, part=2, noline=True)
    for y, w in ((8, 26), (14, 34), (20, 28), (26, 36), (32, 22), (38, 30)):
        c.paint(c.rect(8, y, 8 + w, y + 1) & ((c.xs % 5) != 0), 'chalk', .6, part=3, noline=True)
        c.paint(c.rect(46, y, 50, y + 1), 'chalk', .4, part=3, noline=True)
    c.paint(c.ell(54, 14, 7, 7) & ~c.ell(54, 14, 5.6, 5.6), 'chalk', .8, part=3, noline=True)
    c.paint(c.ell(54, 14, 2, 2), 'curtain', .7, part=3, noline=True)
    c.paint(c.rect(2, 44, 66, 48), 'oak', .6, part=4)
    return c

def w_azulejos():
    c = Canvas(64, 50)
    c.paint(c.rect(0, 0, 64, 50), 'blue', .3, part=1)
    tiles = c.rect(3, 3, 61, 47)
    c.paint(tiles, 'glaze', .75 + (((c.xs - 3) % 14 == 0) | ((c.ys - 3) % 11 == 0)) * -.35, part=2, noline=True)
    c.paint(tiles & (c.ys > 33), 'blue', .55 + (((c.xs + c.ys * 2) % 9) < 2) * .3, part=3, noline=True)
    hull = tiles & (c.ys > 26) & (c.ys < 33) & (np.abs(c.xs - 32) < 16 - (c.ys - 26) * 1.2)
    c.paint(hull, 'blue', .25, part=3, noline=True)
    c.paint(tiles & c.rect(31, 8, 33, 27), 'blue', .3, part=3, noline=True)
    c.paint(tiles & (c.ys > 9) & (c.ys < 25) & (c.xs > 33) & (c.xs < 33 + (c.ys - 8) * .8), 'blue', .55, part=3, noline=True)
    c.paint(tiles & (c.ys > 11) & (c.ys < 24) & (c.xs < 31) & (c.xs > 31 - (c.ys - 10) * .6), 'blue', .6, part=3, noline=True)
    c.paint(tiles & c.ell(12, 12, 4, 4), 'blue', .45, part=3, noline=True)
    return c

def w_shelf():
    c = Canvas(64, 44); g = rng(59)
    for y in (18, 40): c.paint(c.rect(0, y, 64, y + 4), 'oak', np.where(c.ys == y, .9, .4), part=1)
    mats = ['bottle', 'velvet', 'gold', 'blue', 'bottle', 'clay', 'bottle', 'velvet']
    for k in range(8):
        x = 3 + k * 7 + int(g.integers(0, 2)); h = int(g.integers(11, 16)); m = mats[k]
        c.paint(c.rect(x, 18 - h + 4, x + 5, 18), m, c.cyl_x(x, x + 5, .3, .95), part=2)
        c.paint(c.rect(x + 1, 18 - h, x + 4, 18 - h + 4), m, .4, part=2)
        c.paint(c.rect(x, 18 - h + 7, x + 5, 18 - h + 11), 'paper', .7, part=3)
    for k in range(6):
        x = 4 + k * 10; h = int(g.integers(9, 15))
        c.paint(c.rect(x, 40 - h, x + 7, 40), ['clay', 'glaze', 'straw', 'terra', 'glaze', 'clay'][k], c.cyl_x(x, x + 7, .3, .9), part=2)
    return c

def w_mirror():
    c = Canvas(44, 54)
    c.paint(c.ell(22, 27, 21, 26), 'gold', c.sphere(22, 27, 21, 26) * .7 + .15 + ((c.xs + c.ys) % 5 == 0) * .15, part=1)
    c.paint(c.ell(22, 27, 16, 21), 'sky', .55 + (((c.xs - c.ys * .5) % 16) < 3) * .35 - c.ys / 200, part=2)
    c.paint(c.ell(22, 3, 5, 3) | c.ell(22, 51, 6, 3), 'gold', .8, part=3)
    return c

def w_neon(f=0):
    c = Canvas(64, 30)
    c.paint(c.rect(0, 0, 64, 30), 'onyx', .3 + (c.ys < 2) * .3, part=1)
    on = f % 8 != 0
    glow = c.rect(4, 6, 60, 24)
    if on: c.paint(glow, 'purple', .2, part=2, noline=True)
    L = {'P': ['111', '101', '111', '100', '100'], 'I': ['1', '1', '1', '1', '1'],
         'Z': ['111', '001', '010', '100', '111'], 'A': ['010', '101', '111', '101', '101']}
    x0 = 9
    for ch in 'PIZZA':
        gph = L[ch]
        for j, row in enumerate(gph):
            for i, b in enumerate(row):
                if b == '1':
                    m = c.rect(x0 + i * 3, 7 + j * 3, x0 + i * 3 + 3, 7 + j * 3 + 3)
                    c.paint(m, 'neonC' if ch == 'A' else 'neonP', (.85 if on else .2), part=3, noline=True)
        x0 += len(gph[0]) * 3 + 3
    return c

def w_clock():
    c = Canvas(32, 32)
    c.paint(c.ell(16, 16, 15, 15), 'oak', c.sphere(16, 16, 15, 15) * .8 + .1, part=1)
    c.paint(c.ell(16, 16, 12, 12), 'linen', .85, part=2)
    for a in range(12):
        x, y = 16 + np.cos(a * np.pi / 6) * 10, 16 + np.sin(a * np.pi / 6) * 10
        c.paint(c.rect(int(x), int(y), int(x) + 1, int(y) + 1), 'onyx', .3, part=3, noline=True)
    c.paint(c.rect(15, 8, 17, 17) | c.rect(16, 15, 23, 17), 'onyx', .3, part=3, noline=True)
    c.paint(c.ell(16, 16, 1.5, 1.5), 'gold', .8, part=4, noline=True)
    return c

def w_photos():
    c = Canvas(64, 46); g = rng(61)
    for x, y, w, h in ((2, 4, 24, 18), (30, 2, 18, 24), (8, 26, 18, 16), (36, 30, 26, 14), (52, 6, 10, 16)):
        c.paint(c.rect(x, y, x + w, y + h), 'oakD', .4 + (c.ys == y) * .4, part=1)
        c.paint(c.rect(x + 2, y + 2, x + w - 2, y + h - 2), 'sepia', .7 - (c.ys - y) / (h * 3) + noise(46, 64, 1, g) * .1, part=2, noline=True)
        c.paint(c.ell(x + w / 2, y + h / 2 - 1, w / 7, h / 5), 'sepia', .25, part=3, noline=True)
        c.paint(c.rect(x + 2, y + h - 6, x + w - 2, y + h - 2) & c.ell(x + w / 2, y + h, w / 3.5, h / 3), 'sepia', .3, part=3, noline=True)
    return c

# ======================= KITCHEN =======================
def oven(f=0):
    W, H = 68, 88; c = Canvas(W, H); g = rng(62)
    c.paint(c.rect(28, 0, 40, 22), 'stone', c.cyl_x(28, 40), part=1)
    c.paint(c.rect(26, 0, 42, 3), 'stone', .8, part=2)
    dome = c.ell(34, 58, 31, 44) & (c.ys < 62)
    row = (c.ys // 5); bx = (c.xs + (row % 2) * 4) % 8
    c.paint(dome, 'brick', np.clip(c.sphere(34, 50, 31, 36) * .75 + .1 - ((c.ys % 5) == 0) * .3 - (bx == 0) * .25 + noise(H, W, 2, g) * .1, 0, 1), part=3)
    mouth = c.ell(34, 62, 15, 17) & (c.ys < 62)
    c.paint(mouth, 'onyx', .15, part=4)
    fire = c.ell(34, 60, 11 - f, 10) & (c.ys < 62)
    c.paint(fire, 'flame', np.clip(.15 + (c.ys - 48) / 14 + (np.sin(c.xs * 1.3 + f * 2) * .2), 0, 1), part=5, noline=True)
    c.paint(c.ell(34, 62, 17, 19) & ~c.ell(34, 62, 15, 17) & (c.ys < 62), 'stone', .7, part=6)
    c.paint(c.rect(2, 60, 66, 88), 'stone', .45 + ((c.ys - 60) % 9 == 0) * -.25 + (((c.xs + ((c.ys - 60) // 9) * 11) % 21) == 0) * -.25 + (c.ys == 60) * .4, part=7)
    c.paint(c.rect(18, 60, 50, 64), 'oak', np.where(c.ys == 60, .9, .45), part=8)
    return c

def counter(n=8):
    W = n * 32 + 2; c = Canvas(W, 56); g = rng(63)
    c.paint(c.rect(1, 1, W - 1, 18), 'marbleW', .72 + noise(56, W, 6, g) * .1 + (c.ys < 3) * .2 - (np.abs(np.sin(c.xs * .2 + noise(56, W, 8, g) * 6)) < .06) * .3, part=1)
    c.paint(c.rect(1, 18, W - 1, 21), 'marbleV', .5, part=2)
    c.paint(c.rect(1, 21, W - 1, 54), 'oak', .5 + (c.ys == 21) * .4 - (c.ys > 51) * .3, part=3)
    for i in range(n):
        x0 = 1 + i * 32
        c.paint(c.rect(x0 + 4, 26, x0 + 28, 48), 'oak', .35 + (c.ys == 26) * -.15 + (c.ys == 47) * .4 + (c.xs == x0 + 4) * -.15, part=4)
        c.paint(c.rect(x0 + 6, 28, x0 + 26, 46), 'oak', .58 + noise(56, W, 3, g) * .1, part=5, noline=True)
    return c

def register():
    c = Canvas(32, 28)
    c.paint(c.rect(3, 10, 29, 26), 'iron2', .45 + (c.ys == 10) * .4, part=1)
    c.paint(c.rect(7, 2, 25, 11), 'iron2', .3, part=2)
    c.paint(c.rect(9, 4, 23, 8), 'screen', .7, part=3, noline=True)
    for y in (14, 18):
        for x in range(6, 26, 5): c.paint(c.rect(x, y, x + 3, y + 2), 'linen', .8, part=3)
    c.paint(c.rect(3, 22, 29, 26), 'chrome', .55, part=3)
    return c

def boxes():
    c = Canvas(32, 34)
    for k in range(4):
        y = 24 - k * 7
        c.paint(c.rect(1, y, 31, y + 7), 'box', .6 + (c.ys == y) * .3 - (c.ys == y + 6) * .35, part=1 + k)
        c.paint(c.rect(13, y + 2, 19, y + 4), 'red', .6, part=1 + k)
    return c

def logs():
    c = Canvas(34, 22)
    for k, (x, y) in enumerate(((1, 10), (12, 10), (23, 10), (6, 2), (17, 2))):
        c.paint(c.rect(x, y, x + 10, y + 9), 'oak', .5 + (c.ys == y) * .3, part=1 + k)
        c.paint(c.ell(x + 2.5, y + 4.5, 2, 3.5), 'straw', .7, part=1 + k)
    return c

def rack():
    c = Canvas(36, 36)
    c.paint(c.rect(2, 4, 34, 8), 'iron2', .6 + (c.ys == 4) * .3, part=1)
    for x, h, m in ((8, 14, 'chrome'), (18, 10, 'iron2'), (28, 20, 'chrome')):
        c.paint(c.rect(x, 8, x + 2, 8 + h), 'iron2', .5, part=2)
        c.paint(c.ell(x + 1, 10 + h, 5, 4), m, c.sphere(x + 1, 10 + h, 5, 4), part=3)
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
SKINS = {'skinA', 'skinB', 'skinC', 'skinD'}
# a blush close to each skin tone, so it reads as warm cheeks and not as a pink stroke
BLUSH = {'skinA': '#f0aa9a', 'skinB': '#d8947c', 'skinC': '#8e5a46', 'skinD': '#c8866e'}
for k, v in BLUSH.items(): RAMP['blush' + k] = hexs([v])
# Kawaii (chibi) people: a big round head about as tall as the body, big glossy eyes set low on the
# face, rosy cheeks and a tiny mouth. Head centre (16, 11), radius 10; hips at y = 33 as before.
HX, HY, HR = 16, 11, 10

def head_front(c, skin, hair, eye, long=False, back=False):
    c.paint(c.ell(HX - 10.5, 13, 1.8, 2.4) | c.ell(HX + 10.5, 13, 1.8, 2.4), skin, .5, part=7)   # ears
    c.paint(c.ell(HX, HY, HR, HR * .95), skin, .6 + c.sphere(HX, HY, HR, HR) * .28, part=8)
    sheen = ((c.xs + c.ys * 2) % 6 == 0) * -.12
    if back:
        hm = c.ell(HX, HY - .5, HR + .8, HR + .3)
        if long: hm |= c.rect(HX - 10, HY, HX + 11, 27) & c.ell(HX, 17, 10.5, 11)
        c.paint(hm, hair, c.sphere(HX, HY - 2, HR + 1, HR + 1) * .85 + sheen, part=9)
        return
    bangs = c.ys < 7.5 + 1.8 * np.abs(np.sin((c.xs - HX) * .45))                    # scalloped fringe
    hm = c.ell(HX, HY - 1, HR + .8, HR) & (bangs | (np.abs(c.xs + .5 - HX) > 8.2))
    if long: hm |= (c.rect(HX - 11, 9, HX - 7, 27) | c.rect(HX + 7, 9, HX + 11, 27)) & (c.ys < 27 - (np.abs(c.xs + .5 - HX) < 9) * 0)
    c.paint(hm, hair, c.sphere(HX, HY - 3, HR + 1, HR + 1) * .85 + sheen, part=9)
    c.paint(c.rect(HX - 5, 3, HX - 2, 4) & hm, hair, 1, part=9, noline=True)            # shine on the hair
    for ex in (HX - 5, HX + 3):                                                    # big glossy eyes
        e = c.rect(ex, 11, ex + 3, 16) & ~(c.rect(ex, 11, ex + 1, 12) | c.rect(ex + 2, 11, ex + 3, 12) | c.rect(ex, 15, ex + 1, 16) | c.rect(ex + 2, 15, ex + 3, 16))
        c.paint(e, eye, np.where(c.ys >= 13, .55, .05), part=10, noline=True)
        c.paint(c.rect(ex, 12, ex + 1, 14), 'white', 1, part=11, noline=True)          # catch lights
        c.paint(c.rect(ex + 2, 14, ex + 3, 15), 'white', .8, part=11, noline=True)
    c.paint(c.rect(HX - 7, 16, HX - 5, 17) | c.rect(HX + 5, 16, HX + 7, 17), 'blush' + skin, 0, part=10, noline=True)
    c.paint(c.rect(HX - 1, 17, HX + 1, 18), skin, .05, part=10, noline=True)              # tiny mouth, a darker skin tone

def head_side(c, skin, hair, eye, long=False):
    c.paint(c.ell(HX, HY, HR - .3, HR * .95), skin, .6 + c.sphere(HX + 1, HY, HR, HR) * .28, part=8)
    c.paint(c.ell(HX - 2, 13, 1.8, 2.4), skin, .45, part=8)                           # ear
    sheen = ((c.xs + c.ys * 2) % 6 == 0) * -.12
    hm = c.ell(HX - .5, HY - 1, HR + .6, HR) & ((c.ys < 7 + (c.xs > HX + 4) * 1.5) | (c.xs < HX - 3) | ((c.xs < HX) & (c.ys < 11)))
    hm &= ~c.ell(HX - 2, 13, 2, 2.6)
    if long: hm |= c.rect(HX - 10, 9, HX - 3, 27) & c.ell(HX - 6, 17, 6, 11)
    c.paint(hm, hair, c.sphere(HX - 2, HY - 3, HR + 1, HR + 1) * .85 + sheen, part=9)
    ex = HX + 4
    e = c.rect(ex, 11, ex + 3, 16) & ~(c.rect(ex, 11, ex + 1, 12) | c.rect(ex + 2, 11, ex + 3, 12) | c.rect(ex, 15, ex + 1, 16) | c.rect(ex + 2, 15, ex + 3, 16))
    c.paint(e, eye, np.where(c.ys >= 13, .55, .05), part=10, noline=True)
    c.paint(c.rect(ex, 12, ex + 1, 14), 'white', 1, part=11, noline=True)
    c.paint(c.rect(ex, 16, ex + 2, 17), 'blush' + skin, 0, part=10, noline=True)
    c.paint(c.rect(HX + 6, 17, HX + 7, 18), skin, .05, part=10, noline=True)

def person(d='down', skin='skinA', hair='hairB', shirt='shirtB', long=False, pants='jeans', eye='irisBr'):
    c = Canvas(32, 48)
    if d in ('left', 'right'):
        c.paint(c.rect(21, 35, 25, 43), pants, c.cyl_x(21, 25, .2, .6), part=1)            # shin
        c.paint(c.ell(25, 44.5, 4.5, 2.6), 'shoe', c.sphere(25, 44, 4.5, 2.6), part=2)
        c.paint(c.rect(12, 30, 25, 36) | c.ell(24, 33, 2.8, 3), pants, np.where(c.ys < 32, .75, .4), part=3)   # thigh
        c.paint(c.ell(16, 27, 6, 7.5) & (c.ys > 19), shirt, c.sphere(15, 25, 7, 8) * .8 + .1, part=4)          # round body
        c.paint(c.rect(15, 23, 25, 27) | c.ell(15, 25, 2.5, 2.5), shirt, np.where(c.ys < 25, .75, .4), part=5) # short arm
        c.paint(c.ell(26, 25, 2.4, 2.2), skin, .65, part=6)
        head_side(c, skin, hair, eye, long)
        return flip(c) if d == 'left' else c
    if d == 'down':
        for lx in (11, 17): c.paint(c.rect(lx, 36, lx + 4, 43), pants, c.cyl_x(lx, lx + 4, .25, .65), part=1)
        for cx in (12.5, 19.5): c.paint(c.ell(cx, 44.5, 3.5, 2.6), 'shoe', c.sphere(cx, 44, 3.5, 2.6), part=2)
        c.paint(c.ell(16, 34, 7.5, 3.5), pants, np.where(c.ys < 34, .8, .5), part=3)         # lap
    c.paint(c.ell(16, 27, 7.5, 7.5) & (c.ys > 19), shirt, c.sphere(15, 25, 8, 8) * .8 + .1, part=4)
    for ax in (7.5, 24.5):
        c.paint(c.ell(ax, 26, 2.6, 4.5), shirt, c.sphere(ax, 25, 2.6, 4.5) * .7 + .1, part=5)
        if d == 'down': c.paint(c.ell(ax + (1 if ax < 16 else -1), 30.5, 2.3, 2), skin, .65, part=6)   # mitten hands
    if d == 'down': c.paint(c.ell(16, 21, 2.5, 1.6) & (c.ys > 20), skin, .45, part=5)           # neckline
    head_front(c, skin, hair, eye, long, back=(d == 'up'))
    return c

def standing(role='waiter', skin='skinA', hair='hairB', eye='irisBr'):
    """32 x 58, standing and facing down: the waiter (white shirt, black waistcoat, long apron)
    or the cook (white jacket and a tall puffy hat). Head at the same place as a seated person's."""
    c = Canvas(32, 58)
    pants = 'vest' if role == 'waiter' else 'pantsK'
    for lx in (11, 17): c.paint(c.rect(lx, 38, lx + 4, 52), pants, c.cyl_x(lx, lx + 4, .25, .65), part=1)
    for cx in (12.5, 19.5): c.paint(c.ell(cx, 53.5, 3.5, 2.6), 'shoe', c.sphere(cx, 53, 3.5, 2.6), part=2)
    c.paint((c.ell(16, 29, 8, 10) & (c.ys > 19)) | c.rect(9, 29, 23, 40), 'apron', c.cyl_x(8, 24), part=3)
    if role == 'waiter':
        c.paint((c.rect(9, 21, 13, 34) | c.rect(19, 21, 23, 34)) & c.ell(16, 29, 8, 10), 'vest', c.cyl_x(8, 24, .2, .5), part=4)
        c.paint(c.rect(10, 32, 22, 46), 'apron', .7 - (c.ys > 42) * .2 + ((c.xs % 5) == 0) * -.1, part=5)
        c.paint(c.rect(14, 20, 18, 22), 'red', .6, part=5)
    else:
        for y in (24, 28, 32): c.paint(c.rect(15, y, 17, y + 2), 'chrome', .5, part=4)
        c.paint(c.rect(10, 36, 22, 44), 'red', .55 + ((c.xs + c.ys) % 4 < 2) * .2, part=5)
    for ax in (7, 25):
        c.paint(c.ell(ax, 28, 2.6, 6), 'apron', c.sphere(ax, 27, 2.6, 6) * .7 + .15, part=4)
        c.paint(c.ell(ax, 34.5, 2.3, 2), skin, .65, part=6)
    head_front(c, skin, hair, eye)
    if role == 'cook':
        hat = (c.ell(16, 0, 10, 5) | c.rect(8, 0, 24, 6)) & (c.ys >= 0)
        c.paint(hat, 'apron', .65 + c.sphere(16, 0, 10, 6) * .3, part=12)
        c.paint(c.rect(7, 4, 25, 7), 'apron', .5, part=12)
    return c

# customers: skin, hair, shirt, long hair, trousers, eyes
LOOKS = [('skinA', 'hairY', 'shirtR', True, 'pantsK', 'irisBl'), ('skinB', 'hairK', 'shirtG', False, 'jeans', 'irisBr'),
         ('skinA', 'hairG', 'shirtW', False, 'pantsB', 'irisGr'), ('skinC', 'hairB', 'shirtP', False, 'jeans', 'irisDk'),
         ('skinB', 'hairR', 'shirtY', True, 'pantsK', 'irisGr'), ('skinC', 'hairK', 'shirtB', False, 'pantsB', 'irisBr'),
         ('skinD', 'hairB', 'shirtR', True, 'jeans', 'irisHz'), ('skinA', 'hairB', 'shirtB', False, 'pantsK', 'irisBl'),
         ('skinD', 'hairK', 'shirtW', True, 'pantsB', 'irisDk'), ('skinB', 'hairY', 'shirtP', False, 'jeans', 'irisHz')]

# ======================= LAYOUT OF EACH PIECE (px from its top-left tile, 32 px tiles) =======================
# parts: [key, x, y, z, frames]; z is the depth baseline (bigger = in front).
# seats: d = which way the sitter faces; p = [x, y, z] of the person; chair / back = [key, x, y, z].
def chair_seat(style, d, x, y, pz=None):
    if d == 'up':
        return {'d': d, 'chair': [f'ch_{style}_upseat', x, y, y + 10], 'back': [f'ch_{style}_upback', x, y, y + 31], 'p': [x, y - 24, y + 28]}
    return {'d': d, 'chair': [f'ch_{style}_{d}', x, y, y + 30], 'p': [x, y - 18, pz if pz is not None else y + 31]}
def seat4(st, tz):
    return [chair_seat(st, 'down', 48, 4), chair_seat(st, 'up', 48, 94), chair_seat(st, 'right', 0, 52, tz + 1), chair_seat(st, 'left', 96, 52, tz + 1)]
def seat2(st, tz): return [chair_seat(st, 'right', 0, 28, tz + 1), chair_seat(st, 'left', 96, 28, tz + 1)]

LAYOUT = {
    'xadrez2': {'parts': [['t_check2', 26, 14, 64]], 'seats': seat2('tratt', 64), 'top': [64, 30, 36, 14]},
    'xadrez4': {'parts': [['t_check4', 24, 22, 86]], 'seats': seat4('tratt', 86), 'top': [64, 43, 38, 19]},
    'redonda': {'parts': [['t_round', 24, 24, 92]], 'seats': seat4('tasca', 92), 'top': [64, 48, 36, 20]},
    'branca':  {'parts': [['t_white', 24, 22, 86]], 'seats': seat4('moder', 86), 'top': [64, 45, 37, 20]},
    'gala':    {'parts': [['t_gala', 24, 20, 94]], 'seats': seat4('luxo', 94), 'top': [64, 44, 36, 18]},
    'bistro':  {'parts': [['t_bistro', 32, 12, 64]], 'seats': seat2('luxo', 64), 'top': [64, 30, 28, 14]},
    # the table top starts right below the sitters' hips, so their legs are under the table
    'corrida': {'parts': [['bench', 6, 14, 30], ['t_long', 6, 20, 96], ['bench', 6, 98, 120]],
                'seats': [{'d': 'down', 'p': [x, -13, 32]} for x in (24, 64, 104)] + [{'d': 'up', 'p': [x, 69, 126]} for x in (24, 64, 104)],
                'top': [80, 47, 70, 24]},
    'booth':   {'parts': [['sofa_top', 2, 0, 40], ['t_booth', 4, 24, 78], ['sofa_back', 2, 74, 118]],
                'seats': [{'d': 'down', 'p': [x, -7, 42]} for x in (14, 50)] + [{'d': 'up', 'p': [x, 45, 100]} for x in (14, 50)],
                'top': [48, 44, 42, 18]},
}
DECOR = {   # key, footprint w, h, frames
    'vaso': ('d_plant', 1, 1, 1), 'ficus': ('d_ficus', 1, 1, 1), 'oliveira': ('d_olive', 1, 1, 1), 'barril': ('d_barrel', 1, 1, 1),
    'garrafeira': ('d_winerack', 2, 1, 1), 'jukebox': ('d_jukebox', 1, 1, 1), 'arcade': ('d_arcade', 1, 1, 1), 'aquario': ('d_aquarium', 2, 1, 4),
    'candeeiro': ('d_lamp', 1, 1, 1), 'estatua': ('d_statue', 1, 1, 1), 'fonte': ('d_fountain', 2, 2, 4), 'piano': ('d_piano', 3, 2, 1),
    'persa': ('rug_persa', 3, 2, 1), 'trapos': ('rug_trapos', 3, 2, 1)}
WALLPIECES = {'janela': ('w_window', -2, 8), 'quadro': ('w_painting', 10, 12), 'giz': ('w_chalk', -2, 6), 'azulejos': ('w_azulejos', 0, 8),
              'prateleira': ('w_shelf', 0, 12), 'espelho': ('w_mirror', 10, 4), 'neon': ('w_neon', 0, 16), 'relogio': ('w_clock', 16, 14), 'fotos': ('w_photos', 0, 10)}

def sprites():
    out = {}
    def put(k, cv): out[k] = cv.image() if isinstance(cv, Canvas) else cv
    for k, f in (('check', floor_check), ('planks', floor_planks), ('hydraulic', floor_hydraulic), ('terrazzo', floor_terrazzo),
                 ('marble', floor_marble), ('terracotta', floor_terracotta), ('kitchen', floor_kitchen)): put('f_' + k, f())
    for k, f in (('cream', wall_cream), ('azulejo', wall_azulejo), ('brick', wall_brick), ('modern', wall_modern),
                 ('damask', wall_damask), ('kitchen', wall_kitchen)): put('w_' + k, f())
    put('sidewalk', sidewalk()); put('curb', curb()); put('divider', divider()); put('frontwall', front_wall()); put('doormat', door_mat())
    for st in CH:
        for d in ('down', 'right', 'left'): put(f'ch_{st}_{d}', chair(st, d))
        put(f'ch_{st}_upseat', chair(st, 'up', 'seat')); put(f'ch_{st}_upback', chair(st, 'up', 'back'))
    put('t_check2', table_check(76, 28)); put('t_check4', table_check(80, 40)); put('t_round', table_round()); put('t_long', table_long())
    put('bench', bench()); put('t_white', table_white()); put('t_gala', table_gala()); put('t_bistro', table_bistro())
    put('sofa_top', sofa(True)); put('sofa_back', sofa(False)); put('t_booth', table_booth()); put('pizza', pizza()); put('plate', plate())
    put('d_plant', d_plant()); put('d_ficus', d_ficus()); put('d_olive', d_olive()); put('d_barrel', d_barrel()); put('d_winerack', d_wine_rack())
    put('d_jukebox', d_jukebox()); put('d_arcade', d_arcade()); put('d_lamp', d_lamp()); put('d_statue', d_statue()); put('d_piano', d_piano())
    for f in range(4): put(f'd_aquarium_{f}', d_aquarium(f)); put(f'd_fountain_{f}', d_fountain(f))
    put('rug_persa', d_rug('persa')); put('rug_trapos', d_rug('trapos'))
    put('w_window', window()); put('w_painting', w_painting()); put('w_chalk', w_chalkboard()); put('w_azulejos', w_azulejos())
    put('w_shelf', w_shelf()); put('w_mirror', w_mirror()); put('w_clock', w_clock()); put('w_photos', w_photos())
    put('w_neon_0', w_neon(0)); put('w_neon_1', w_neon(1))
    put('k_oven_0', oven(0)); put('k_oven_1', oven(1)); put('k_counter', counter(8)); put('k_register', register())
    put('k_boxes', boxes()); put('k_logs', logs()); put('k_rack', rack())
    put('waiter', standing('waiter', 'skinB', 'hairB', 'irisBr')); put('cook', standing('cook', 'skinA', 'hairK', 'irisGr'))
    for i, (sk, hr, sh, lg, pa, ey) in enumerate(LOOKS):
        for d in ('down', 'up', 'right', 'left'): put(f'p{i}_{d}', person(d, sk, hr, sh, lg, pa, ey))
    return out

def layout_json(imgs):
    import json
    items = dict(LAYOUT)
    for id_, (k, w, h, frames) in DECOR.items():
        im = imgs[k + ('_0' if frames > 1 else '')]
        if id_ in ('persa', 'trapos'): items[id_] = {'parts': [[k, 0, 0, -1]], 'rug': 1}; continue
        x = (w * 32 - im.width) // 2; y = h * 32 - im.height + 2
        items[id_] = {'parts': [[k, x, y, h * 32] + ([frames] if frames > 1 else [])]}
    walls = {id_: [k + ('_1' if k == 'w_neon' else ''), x, y] for id_, (k, x, y) in WALLPIECES.items()}
    kitchen = [['k_oven', 414, 42, 128, 2], ['k_logs', 606, 104, 128], ['k_counter', 382, 202, 256], ['k_register', 388, 178, 256.1],
               ['k_boxes', 606, 190, 256.2], ['cook', 456, 58, 129]]
    return json.dumps({'items': items, 'walls': walls, 'kitchen': kitchen, 'looks': len(LOOKS)}, separators=(',', ':'))

def pack(imgs, width=1024):
    order = sorted(imgs, key=lambda k: (-imgs[k].height, -imgs[k].width))
    x = y = shelf = 0; frames = {}
    for k in order:
        w, h = imgs[k].size
        if x + w > width: x, y, shelf = 0, y + shelf + 1, 0
        frames[k] = [x, y, w, h]; x += w + 1; shelf = max(shelf, h)
    sheet = Image.new('RGBA', (width, y + shelf), (0, 0, 0, 0))
    for k, (x, y, w, h) in frames.items(): sheet.paste(imgs[k], (x, y))
    return sheet, frames

if __name__ == '__main__':
    import base64, io
    os.makedirs(OUT, exist_ok=True)
    imgs = sprites()
    sheet, frames = pack(imgs)
    buf = io.BytesIO(); sheet.save(buf, 'PNG', optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    fr = ',\n'.join(f'  {k}:[{",".join(map(str, v))}]' for k, v in sorted(frames.items()))
    js = ('/* Generated by tools/gen_room.py. Do not edit by hand. */\n'
          f'const ROOM_ART={{tile:32,frames:{{\n{fr}\n}},\nlayout:{layout_json(imgs)},\nsrc:"data:image/png;base64,{b64}"}};\n')
    root = os.path.join(os.path.dirname(__file__), '..')
    with open(os.path.join(root, 'assets', 'room.js'), 'w') as f: f.write(js)
    sheet.save(OUT + 'room_atlas.png')
    print('ok', sheet.size, len(frames), 'frames', len(js) // 1024, 'KB')
