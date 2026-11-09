#!/usr/bin/env python3
"""Pizza Magna: PILOT for better people. Not used by the game; it only makes preview images.

Same frame as today's walkers (32 x 58, feet on the same line) so the new people could replace
them one for one, but drawn differently:
- clean cel shading (bands of the ramp, almost no dithering), so small shapes read clearly;
- a real figure: neck, shoulders, arms with cuffs and hands, hips, legs with a gap, shoes with soles;
- faces with brows, lashes, a smile; hair with a shine band and its own shapes;
- clothes with their own details (hood and pocket, lapels and tie, ribbed hems, cardigan, studs);
- a four-step walk (contact, passing with a 1 px bob, contact, passing) with swinging arms.
Usage: python3 tools/pilot_people.py <folder>  -> pilot_people.png, pilot_walk.gif"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
_out = sys.argv[1] if len(sys.argv) > 1 else '.'
sys.argv = sys.argv[:1] + [_out]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_room as G
from gen_room import Canvas, RAMP, hexs, BAYER

RAMP.update({
    'hood':    hexs(['#12301c', '#1e4a2a', '#2e6a3c', '#46904e', '#6cb46c']),
    'sweater': hexs(['#4a0a0c', '#7a1414', '#a82220', '#cc3c30', '#e86a54']),
    'teeO':    hexs(['#7a3408', '#b05410', '#dc7a1c', '#f6a23c', '#ffc878']),
    'capB':    hexs(['#0c1c44', '#16306e', '#24489c', '#3c68c8']),
    'pack':    hexs(['#3a1a4a', '#5a2a70', '#7c4098', '#a060bc']),
    'cardi':   hexs(['#3a1e4c', '#583070', '#784894', '#9a68b4', '#bc90d0']),
    'blouse':  hexs(['#b8a890', '#dccfb8', '#f2e8d8', '#fffaf0']),
    'denim':   hexs(['#0e1a34', '#1a2c54', '#2a4478', '#40629e', '#6088c0']),
    'sole':    hexs(['#1a120e', '#3a2a22', '#e8e0d0']),
    'shoeR':   hexs(['#4a0c08', '#8a1810', '#c42a1c', '#ec5a40']),
    'shoeW':   hexs(['#8a8a90', '#c0c0c8', '#ececf2', '#ffffff']),
    'boot':    hexs(['#08080a', '#16161a', '#2a2a30', '#48484e']),
})

def render(s, dither=.14):
    """like Canvas.image, with almost no dithering and a firm dark outline round the figure"""
    h, w = s.h, s.w
    out = np.zeros((h, w, 4), np.uint8)
    filled = s.mat != None
    for y in range(h):
        for x in range(w):
            if not filled[y, x]:
                a = s.shadow[y, x]
                if a > 0 and a + BAYER[y % 4, x % 4] * .25 > .2: out[y, x] = G.SHADOW + (int(min(1, a) * 150),)
                continue
            ramp = RAMP[s.mat[y, x]]; k = len(ramp)
            v = int(round(float(np.clip(s.lit[y, x] * (k - 1) + BAYER[y % 4, x % 4] * dither, 0, k - 1))))
            col = ramp[v]
            if not s.noline[y, x]:
                edge = front = False
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, x + dx
                    if not (0 <= yy < h and 0 <= xx < w) or not filled[yy, xx]: edge = True
                    elif s.part[yy, xx] > s.part[y, x] and not s.noline[yy, xx]: front = True      # small details (eyes, buttons) cast no edge
                if edge: col = tuple(int(c * .72) for c in ramp[0])
                elif front: col = ramp[max(0, v - 2)]
            out[y, x] = col + (255,)
    return Image.fromarray(out, 'RGBA')

HX = 16
def band(c, cx, cy, rx, ry, lo=.25, hi=.95):
    """cel light of a ball: three clean bands, light from the top left"""
    return np.clip(lo + (hi - lo) * c.sphere(cx - rx * .15, cy - ry * .2, rx * 1.15, ry * 1.15), 0, 1)

def shoe(c, cx, yb, L, part, w=3.6):
    m = c.ell(cx, yb + 1.2, w, 2.5) & (c.ys <= yb + 2)
    c.paint(m, L.get('shoe', 'shoe'), band(c, cx, yb + .5, w, 2.5, .3, 1), part=part)
    c.paint(m & (c.ys >= yb + 2), 'sole', 1 if L.get('shoe') in ('shoeR', 'shoeW') else 0, part=part, noline=True)

def hair_mask(c, L, o, side=False):
    st = L.get('style', 'short'); hy = 11 + o; hx = c.xs + .5 - HX
    cap = c.ell(HX - (1 if side else 0), hy - 1.2, 10.3, 9.6)
    if side:
        m = cap & ((c.ys < hy - 3.5 + (c.xs > HX + 4) * 1.5) | (c.xs < HX - 3) | ((c.xs < HX + 1) & (c.ys < hy)))
        if st == 'long': m |= c.ell(HX - 6, hy + 8, 5.5, 12) & (c.ys > hy - 2)
        if st == 'bun': m |= c.ell(HX - 9.5, hy - 5, 3.8, 3.6)
        if st == 'afro': m = c.ell(HX - 2, hy - 3, 12, 11) & ~(c.ell(HX + 4, hy + 3, 7, 8) & (c.ys > hy - 5))
        if st == 'mohawk': m = (c.xs > HX - 9) & (c.xs < HX + 6) & (c.ys >= o + 2.4 * np.abs((c.xs % 4) - 2) - 1) & (c.ys < hy - 4) & (c.ys >= 0)
        if st == 'cap': m = cap & (c.xs < HX - 4) & (c.ys > hy - 2) & (c.ys < hy + 5)
        return m & ~c.ell(HX - 2, hy + 2, 2, 2.6)
    fringe = c.ys < hy - 3.6 + 1.6 * np.abs(np.sin(hx * .5 + .6))
    m = cap & (fringe | (np.abs(hx) > 8.3) & (c.ys < hy + 3))
    if st == 'long': m |= (c.ell(HX - 8.5, hy + 8, 3.2, 11) | c.ell(HX + 8.5, hy + 8, 3.2, 11)) & (c.ys > hy - 3)
    if st == 'bun': m = cap & ((c.ys < hy - 4.5 + (hx > 1) * 2) | (np.abs(hx) > 8.6) & (c.ys < hy + 1)) | c.ell(HX, o + 1.6, 4.2, 3.4)
    if st == 'afro': m = (c.ell(HX, hy - 3, 13, 11.5) & (c.ys >= 0)) & ~(c.ell(HX, hy + 4.5, 8.4, 8.5) & (c.ys > hy - 4.4))
    if st == 'mohawk': m = (np.abs(hx) < 3) & (c.ys >= o + 2.2 * np.abs((c.xs % 3) - 1)) & (c.ys < hy - 3)
    if st == 'cap': m = cap & (np.abs(hx) > 8) & (c.ys > hy - 2) & (c.ys < hy + 4)
    return m

def head(c, L, o, side=False):
    skin, hair, eye = L['skin'], L['hair'], L['eye']; hy = 11 + o; st = L.get('style', 'short'); ex_ = L.get('extras', ())
    if not side:
        c.paint(c.ell(HX - 9.8, hy + 2, 1.7, 2.3) | c.ell(HX + 9.8, hy + 2, 1.7, 2.3), skin, .45, part=7)      # ears
    face = c.ell(HX, hy - .5, 9.4, 8.8) | c.ell(HX + (1 if side else 0), hy + 2.5, 8.2 if not side else 7.6, 7)
    c.paint(face, skin, band(c, HX, hy, 10, 9.5, .5, .95), part=8)
    if side: c.paint(c.ell(HX - 2, hy + 2, 1.8, 2.4), skin, .4, part=8)
    hm = hair_mask(c, L, o, side)
    shine = np.abs(np.hypot((c.xs + .5 - HX + 1.5) / 1.1, c.ys + .5 - hy + 1.5) - 6.4) < .75                  # a shine band
    shine &= (c.xs < HX + 3) & (c.ys < hy - 2)
    lit = band(c, HX, hy - 3, 11, 10, .2, .7) + np.where(shine, .3, 0)
    if st == 'afro': lit = band(c, HX, hy - 3, 13, 11.5, .15, .7) + (G.noise(c.h, c.w, 2, G.rng(31)) - .5) * .5
    c.paint(hm, hair, np.clip(lit, 0, 1), part=9)
    if st == 'cap':                                                                                           # a baseball cap
        dome = c.ell(HX - (1 if side else 0), hy - 2, 10.4, 9) & (c.ys < hy - 2.6)
        c.paint(dome, 'capB', band(c, HX, hy - 4, 10, 8, .3, 1), part=10)
        peak = c.rect(HX + 2, hy - 4, HX + 14, hy - 1) & c.ell(HX + 6, hy - 2.5, 8, 2.2) if side else c.ell(HX, hy - 2.2, 9.5, 2.2) & (c.ys >= hy - 4)
        c.paint(peak, 'capB', .25 if not side else .5, part=11)
        if not side: c.paint(c.rect(HX - 1, hy - 8, HX + 1, hy - 6), 'white', 1, part=11, noline=True)
    def eye_at(ex):
        """a big glossy eye, 3 x 5 with soft corners: dark on top, the iris colour below, one catch light"""
        e = c.rect(ex, hy - 1, ex + 3, hy + 4) & ~(c.rect(ex, hy + 3, ex + 1, hy + 4) | c.rect(ex + 2, hy + 3, ex + 3, hy + 4))
        c.paint(e, eye, np.where(c.ys >= hy + 2, .6, .05), part=10, noline=True)
        c.paint(c.rect(ex, hy - 1, ex + 3, hy), 'lash', 0, part=10, noline=True)
        c.paint(c.rect(ex, hy, ex + 1, hy + 2), 'white', 1, part=11, noline=True)
    brow = skin; bl = .12                                             # brows: a darker skin tone, never a hard line
    if side:
        ex = HX + 4; eye_at(ex)
        c.paint(c.rect(ex - 1, hy + 4, ex + 1, hy + 5), 'blush' + skin, 0, part=10, noline=True)
        c.paint(c.rect(HX + 6, hy + 6, HX + 8, hy + 7), skin, .1, part=10, noline=True)
        if 'glasses' in ex_:
            c.paint((c.rect(ex - 1, hy - 2, ex + 4, hy + 5) & ~c.rect(ex, hy - 1, ex + 3, hy + 4)) | c.rect(HX - 1, hy, ex - 1, hy + 1), 'gold', .42, part=12, noline=True)
        return
    for ex in (HX - 5, HX + 2):
        eye_at(ex)
    c.paint(c.rect(HX - 7, hy + 4, HX - 5, hy + 5) | c.rect(HX + 5, hy + 4, HX + 7, hy + 5), 'blush' + skin, 0, part=10, noline=True)
    if 'moustache' in ex_:
        c.paint(c.rect(HX - 3, hy + 5, HX + 3, hy + 7) & ~c.rect(HX - 1, hy + 6, HX + 1, hy + 7), hair, .9, part=11, noline=True)
    else:                                                                                                      # a small smile
        c.paint(c.rect(HX - 1, hy + 6, HX + 1, hy + 7) | c.rect(HX - 2, hy + 5, HX - 1, hy + 6) | c.rect(HX + 1, hy + 5, HX + 2, hy + 6), skin, .12, part=10, noline=True)
    if 'glasses' in ex_:
        for ex in (HX - 6, HX + 1):
            c.paint(c.rect(ex, hy - 2, ex + 5, hy + 5) & ~c.rect(ex + 1, hy - 1, ex + 4, hy + 4), 'gold', .42, part=12, noline=True)
        c.paint(c.rect(HX - 1, hy, HX + 1, hy + 1), 'gold', .42, part=12, noline=True)

def top_front(c, L, o):
    top, shirt, skin = L['top'], L['shirt'], L['skin']
    torso = (c.ell(16, 27 + o, 7.6, 5.5) & (c.ys >= 22 + o)) | (c.rect(9, 26 + o, 23, 39 + o) & (np.abs(c.xs + .5 - 16) < 7.2 - (c.ys - 26 - o) * .07))
    lit = c.cyl_x(8, 24, .3, .9) - np.where(c.ys > 34 + o, .12, 0)
    c.paint(c.rect(14, 19 + o, 18, 23 + o), skin, .35, part=3)                                                 # neck
    if top == 'hoodie': c.paint(c.ell(16, 22.5 + o, 8.5, 3.6), shirt, .3, part=3)                               # the hood, behind the neck
    c.paint(torso, shirt, lit, part=4)
    cx = 16
    if top == 'sweater':
        c.paint(torso & (c.ys >= 37 + o), shirt, .2 + (c.xs % 2) * .2, part=4)                                 # ribbed hem
        c.paint(c.ell(cx, 22.6 + o, 3.2, 1.6), shirt, .25, part=5)                                               # round collar
    elif top == 'hoodie':
        c.paint(c.rect(11, 32 + o, 21, 37 + o) & (np.abs(c.xs + .5 - cx) < 5.5 - (36 + o - c.ys) * .35), shirt, .28, part=5)   # pocket
        for x in (14, 17): c.paint(c.rect(x, 23 + o, x + 1, 28 + o), 'white', .8, part=6, noline=True)               # strings
        c.paint(c.ell(cx, 22.4 + o, 3, 1.5), skin, .4, part=5)
    elif top == 'tee':
        c.paint(c.ell(cx, 22.4 + o, 3, 1.6), skin, .4, part=5)
        star = [(2, 0), (1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (1, 3), (2, 3), (3, 3), (1, 4), (3, 4)]
        for dx, dy in star: c.paint(c.rect(cx - 2.5 + dx, 27 + o + dy, cx - 1.5 + dx, 28 + o + dy), 'white', 1, part=6, noline=True)
    elif top == 'suit':
        v = (np.abs(c.xs + .5 - cx) < (31 + o - c.ys) * .42) & (c.ys >= 22 + o) & (c.ys < 31 + o)
        c.paint(v & torso, 'white', .9, part=5)
        c.paint(c.rect(cx - 1, 23 + o, cx + 1, 31 + o), L.get('tie', 'tie'), np.where(c.xs < cx, .9, .45), part=6)
        c.paint(c.rect(cx - 1, 22 + o, cx + 1, 24 + o), L.get('tie', 'tie'), .2, part=6, noline=True)
        for y in (33, 36): c.paint(c.rect(cx, y + o, cx + 1, y + o + 1), 'gold', .8, part=6, noline=True)
        c.paint(c.rect(19, 28 + o, 22, 29 + o), 'white', .9, part=6, noline=True)                                   # pocket square
    elif top == 'cardigan':
        c.paint(c.rect(cx - 2, 22 + o, cx + 2, 39 + o) & torso, 'blouse', np.where(c.xs < cx, .95, .6), part=5)
        for y in (27, 31, 35): c.paint(c.rect(cx + 2, y + o, cx + 3, y + o + 1), 'gold', .8, part=6, noline=True)
        for k in range(-2, 3): c.paint(c.rect(cx + k * 2 - .5, 23 + o + (2 - abs(k)) * .8, cx + k * 2 + .5, 24 + o + (2 - abs(k)) * .8), 'plate', 1, part=7, noline=True)   # pearls
    elif top == 'leather':
        c.paint(c.rect(cx, 23 + o, cx + 1, 39 + o), 'chrome', .8, part=5, noline=True)                             # zip
        c.paint((np.abs(c.xs + .5 - cx) < (27 + o - c.ys) * .8) & (c.ys >= 22 + o) & (c.ys < 27 + o) & torso, 'shirtW', .8, part=5)
        for x in (11, 20): c.paint(c.rect(x, 25 + o, x + 1, 26 + o), 'chrome', 1, part=6, noline=True)
        c.paint(c.rect(10, 36 + o, 22, 37 + o) & torso, 'chrome', .5, part=6, noline=True)                         # belt of studs
    return torso

def arms_front(c, L, o, al, ar):
    shirt, skin, top = L['shirt'], L['skin'], L['top']
    for ax, d in ((7.4, al), (24.6, ar)):
        y = 29 + o + d
        arm = c.ell(ax, y, 2.5, 6.6)
        c.paint(arm, shirt, band(c, ax, y, 2.5, 6.6, .3, .9) - (.15 if ax > 16 else 0), part=5)
        if top == 'tee': c.paint(arm & (c.ys > y - 1), skin, .6 if ax < 16 else .45, part=5)
        elif top in ('sweater', 'hoodie', 'cardigan'): c.paint(arm & (c.ys > y + 4), shirt, .22, part=5)             # cuff
        elif top == 'suit': c.paint(arm & (c.ys > y + 5), 'white', .9, part=5)
        hx_ = ax + (.8 if ax < 16 else -.8)
        c.paint(c.ell(hx_, y + 7.2, 2.2, 2.1), skin, band(c, hx_, y + 7.2, 2.2, 2.1, .45, .9), part=6)                 # hand
    if 'pack' in L.get('extras', ()):                                                                           # backpack straps
        for x in (10, 20): c.paint(c.rect(x, 23 + o, x + 2, 33 + o), 'pack', np.where(c.xs < x + 1, .9, .5), part=6)
    if 'phone' in L.get('extras', ()):
        c.paint(c.rect(22, 33 + o + ar, 26, 39 + o + ar), 'onyx', .6, part=7); c.paint(c.rect(23, 34 + o + ar, 25, 38 + o + ar), 'neonC', .7, part=8, noline=True)

def legs_front(c, L, o, ld, rd):
    pants, skin, legs = L['pants'], L['skin'], L.get('legs', 'pants')
    shin = skin if legs in ('shorts', 'skirt') else pants
    for k, (x0, d) in enumerate(((10, ld), (17, rd))):
        yb = 52 + d
        c.paint(c.rect(x0, 40 + o, x0 + 5, yb), shin, c.cyl_x(x0, x0 + 5, .3, .9) - (.12 if d < 0 else 0), part=1)
        if legs == 'pants': c.paint(c.rect(x0, yb - 1, x0 + 5, yb), pants, .15, part=1, noline=True)             # hem
        if legs == 'shorts': c.paint(c.rect(x0, yb - 3, x0 + 5, yb), 'white', .8 - (c.ys == yb - 2) * .5, part=1)   # socks
        shoe(c, x0 + 2.5, yb, L, 2, 3.6 + (.4 if d > 0 else 0))
    if legs == 'skirt':
        sk = (c.ys >= 37 + o) & (c.ys < 47 + o) & (np.abs(c.xs + .5 - 16) < 6.4 + (c.ys - 37 - o) * .28)
        c.paint(sk, pants, c.cyl_x(8, 24, .3, .9) - ((c.xs + 1) % 4 == 0) * .2, part=3)
    else:
        hips = c.rect(10, 37 + o, 22, 43 + o if legs == 'pants' else 46 + o) & ~(c.rect(15, 43 + o, 17, 60))
        c.paint(hips, pants, c.cyl_x(9, 23, .3, .9), part=3)
        if legs == 'shorts':
            for x0 in (10, 17): c.paint(c.rect(x0, 40 + o, x0 + 5, 46 + o), pants, c.cyl_x(x0, x0 + 5, .3, .9), part=3)
        c.paint(c.rect(10, 38 + o, 22, 39 + o), 'shoe' if L['top'] != 'leather' else 'chrome', .5, part=4, noline=True)   # belt

STEP_F = {None: (0, 0, 0, 0, 0), 0: (0, 1, -2, -1, 1), 1: (-1, 0, 0, 0, 0), 2: (0, -2, 1, 1, -1), 3: (-1, 0, 0, 0, 0)}   # body, left foot, right foot, left arm, right arm
def front(L, f=None):
    c = Canvas(32, 58); o, ld, rd, al, ar = STEP_F[f]
    c.cast(c.ell(16, 55.2, 8.5, 2.2), .4)
    legs_front(c, L, o, ld, rd); top_front(c, L, o); arms_front(c, L, o, al, ar); head(c, L, o)
    return render(c)

def side(L, f=None):
    """facing right"""
    c = Canvas(32, 58); skin, shirt, pants, top, legs = L['skin'], L['shirt'], L['pants'], L['top'], L.get('legs', 'pants')
    o = -1 if f in (1, 3) else 0
    c.cast(c.ell(16, 55.2, 8, 2.2), .4)
    shin = skin if legs in ('shorts', 'skirt') else pants
    lean = {None: (0, 0), 0: (-5, 5), 1: (-1, 1), 2: (5, -5), 3: (1, -1)}[f]                                     # far leg, near leg: how far the foot is from the hip
    for k, ln in enumerate(lean):
        lift = 2 if (f in (1, 3) and k == (0 if f == 1 else 1)) else 0                                        # the passing foot comes up
        x0 = 13.5 + (c.ys - 40 - o) / 12 * ln
        leg = (c.ys >= 40 + o) & (c.ys < 52 - lift) & (c.xs + .5 >= x0) & (c.xs + .5 < x0 + 5)
        c.paint(leg, shin, np.clip(.75 - (c.xs + .5 - x0) * .09 - (0 if k else .2), 0, 1), part=1 + k * 2)
        if legs == 'shorts': c.paint(leg & (c.ys >= 49 - lift), 'white', .8, part=1 + k * 2)
        fx = 13.5 + (52 - lift - 40 - o) / 12 * ln + 3.6
        m = c.ell(fx, 53.2 - lift, 4.6, 2.5) & (c.ys <= 54 - lift)
        c.paint(m, L.get('shoe', 'shoe'), band(c, fx, 52.5 - lift, 4.6, 2.5, .3, 1) - (0 if k else .15), part=2 + k * 2)
        c.paint(m & (c.ys >= 54 - lift), 'sole', 1 if L.get('shoe') in ('shoeR', 'shoeW') else 0, part=2 + k * 2, noline=True)
    if legs == 'skirt':
        c.paint((c.ys >= 37 + o) & (c.ys < 47 + o) & (np.abs(c.xs + .5 - 16) < 4.6 + (c.ys - 37 - o) * .28), pants, c.cyl_x(10, 22, .3, .9), part=5)
    else:
        c.paint(c.rect(11, 37 + o, 20, 43 + o if legs == 'pants' else 46 + o), pants, c.cyl_x(11, 20, .3, .9), part=5)
    c.paint(c.rect(14, 19 + o, 18, 23 + o), skin, .35, part=3)
    if top == 'hoodie': c.paint(c.ell(11.5, 23.5 + o, 4.5, 4), shirt, .3, part=5)                                # the hood on the back
    if 'pack' in L.get('extras', ()): c.paint(c.ell(8.5, 30 + o, 4, 7), 'pack', band(c, 8.5, 30 + o, 4, 7, .3, 1), part=5)
    torso = (c.ell(15.5, 27 + o, 5.6, 5.5) & (c.ys >= 22 + o)) | c.rect(10, 26 + o, 21, 39 + o) & c.ell(15.5, 31 + o, 5.8, 9)
    c.paint(torso, shirt, c.cyl_x(9, 22, .3, .9), part=6)
    if top == 'sweater': c.paint(torso & (c.ys >= 37 + o), shirt, .2 + (c.xs % 2) * .2, part=6)
    if top == 'suit': c.paint(c.rect(19, 23 + o, 21, 30 + o) & torso, 'white', .9, part=7); c.paint(c.rect(20, 24 + o, 21, 31 + o), L.get('tie', 'tie'), .7, part=7, noline=True)
    if top == 'cardigan': c.paint(c.rect(19, 23 + o, 21, 39 + o) & torso, 'blouse', .9, part=7)
    if top == 'leather': c.paint(c.rect(20, 23 + o, 21, 39 + o) & torso, 'chrome', .8, part=7, noline=True)
    sw = {None: 0, 0: 3, 1: 1, 2: -3, 3: -1}[f]                                                                  # near arm swings against the near leg
    ax = 15.5 + (c.ys - 24 - o) / 12 * sw
    arm = (c.ys >= 24 + o) & (c.ys < 36 + o) & (np.abs(c.xs + .5 - ax) < 2.6)
    c.paint(arm, shirt, np.clip(.85 - np.abs(c.xs + .5 - ax + .8) * .2, 0, 1), part=8)
    if top == 'tee': c.paint(arm & (c.ys > 29 + o), skin, .6, part=8)
    elif top == 'suit': c.paint(arm & (c.ys > 34 + o), 'white', .9, part=8)
    elif top != 'leather': c.paint(arm & (c.ys > 33 + o), shirt, .22, part=8)
    c.paint(c.ell(15.5 + sw * 1.05, 37 + o, 2.3, 2.1), skin, .75, part=9)
    if 'phone' in L.get('extras', ()): c.paint(c.rect(16 + sw, 33 + o, 19 + sw, 38 + o), 'onyx', .6, part=10)
    head(c, L, o, side=True)
    return render(c)

LOOKS = [
    dict(skin='skinA', hair='hairY', eye='irisBl', shirt='sweater', pants='denim', top='sweater', style='long', shoe='boot'),
    dict(skin='skinB', hair='hairK', eye='irisBr', shirt='hood', pants='pantsK', top='hoodie', style='short', shoe='shoeW'),
    dict(skin='skinC', hair='hairK', eye='irisDk', shirt='teeO', pants='denim', top='tee', legs='shorts', style='cap', shoe='shoeR', extras=('pack',)),
    dict(skin='skinD', hair='hairK', eye='irisHz', shirt='suitN', pants='suitN', top='suit', tie='tie', style='short', extras=('glasses',)),
    dict(skin='skinA', hair='hairLilac', eye='irisGr', shirt='cardi', pants='skirtP', top='cardigan', legs='skirt', style='bun', extras=('glasses',)),
    dict(skin='skinA', hair='hairGreen', eye='irisBr', shirt='jacket', pants='denim', top='leather', style='mohawk', shoe='boot'),
    dict(skin='skinC', hair='hairB', eye='irisBr', shirt='shirtY', pants='pantsB', top='sweater', style='afro', shoe='shoeW'),
    dict(skin='skinB', hair='hairPink', eye='irisBl', shirt='crop', pants='denim', top='tee', style='long', shoe='shoeW', extras=('phone',)),
]
OLD = [0, 1, 3, 13, 14, 15, 5, 17]     # today's looks closest to each pilot look

if __name__ == '__main__':
    OUT = _out + '/'; os.makedirs(OUT, exist_ok=True)
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
    K = 5; n = len(LOOKS); BG = (206, 178, 136)
    W = n * 34 * K + 190
    sheet = Image.new('RGB', (W, 4 * 62 * K + 20), BG); dr = ImageDraw.Draw(sheet)
    def put(im, col, row):
        b = im.resize((im.width * K, im.height * K), Image.NEAREST); sheet.paste(b, (180 + col * 34 * K, 10 + row * 62 * K), b)
    for row, t in enumerate(['TODAY', 'PILOT', 'TODAY  side', 'PILOT  side']): dr.text((14, 10 + row * 62 * K + 130), t, fill=(60, 30, 10), font=fs)
    for i, L in enumerate(LOOKS):
        put(G.walker('down', G.LOOKS[OLD[i]], 0).image(), i, 0); put(front(L), i, 1)
        put(G.walker('right', G.LOOKS[OLD[i]], 1).image(), i, 2); put(side(L, 0), i, 3)
    sheet.save(OUT + 'pilot_people.png')
    # the walk, old (2 steps) against the pilot (4 steps), at the game's size x4
    K = 4; frames = []
    for t in range(8):
        fr = Image.new('RGB', (n * 34 * K + 16, 2 * 62 * K * 2 + 16), BG)
        for i, L in enumerate(LOOKS):
            for r, im in enumerate([G.walker('down', G.LOOKS[OLD[i]], (t // 2) % 2).image(), front(L, t % 4), G.walker('right', G.LOOKS[OLD[i]], (t // 2) % 2).image(), side(L, t % 4)]):
                b = im.resize((im.width * K, im.height * K), Image.NEAREST); fr.paste(b, (8 + i * 34 * K, 8 + r * 62 * K), b)
        frames.append(fr)
    frames[0].save(OUT + 'pilot_walk.gif', save_all=True, append_images=frames[1:], duration=140, loop=0)
    print('ok')
