#!/usr/bin/env python3
"""Pizza Magna: the people. gen_room.py builds the game's customers, waiter and cook from here (walk(), seated(),
staff()); run on its own it makes preview images against the first people (still in gen_room.py).

Same frame as today's walkers (32 x 58, feet on the same line) so the new people could replace
them one for one, but drawn differently:
- clean cel shading (bands of the ramp, almost no dithering), so small shapes read clearly;
- a real figure: neck, shoulders, arms with cuffs and hands, hips, legs with a gap, shoes with soles;
- faces with brows, lashes, a smile; hair with a shine band and its own shapes;
- clothes with their own details (hood and pocket, lapels and tie, ribbed hems, cardigan, studs);
- a four-step walk (contact, passing with a 1 px bob, contact, passing) with swinging arms;
- three views: front, side (with a nose, and the near arm standing out from the body) and back;
- seated at the table (32 x 48, like today's seated people: facing down, up, right and left);
- the waiter and the cook.
Usage: python3 tools/pilot_people.py <folder>  -> pilot_people.png, pilot_seated.png, pilot_walk.gif"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
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
    'rose':    hexs(['#7a2a4a', '#a8486a', '#cc6c8c', '#e496b0', '#f6c4d4']),
    'bagB':    hexs(['#2a1408', '#4e2a12', '#74441e', '#9a6430', '#c08a4a']),
    'hawaii':  hexs(['#0a3a44', '#12606c', '#1c8a94', '#3cb4b8', '#7cdcd8']),
    'strawH':  hexs(['#7a5a1c', '#a8822c', '#d0aa48', '#ecd070', '#fbe9a0']),
    'dressK':  hexs(['#0c0c12', '#1c1c26', '#30303e', '#4a4a5c', '#6c6c80']),
    'polo':    hexs(['#2a4a7a', '#4470a8', '#6c9ad0', '#9cc0ea', '#cfe4fa']),
    'hatW':    hexs(['#8a8672', '#b8b49c', '#dcd8c4', '#f4f0e2', '#ffffff']),
    'tang':    hexs(['#101a4a', '#1c2c7a', '#2c44a8', '#4866cc', '#7c96e6']),
    'qipao':   hexs(['#5a0a14', '#8e1420', '#c0202c', '#e0483c', '#f47a5c']),
})

def render(s, dither=0):
    """like Canvas.image, with no dithering (clean bands of each ramp). The outline is the material's own dark tone; on
    skin it is softer (one tone lighter on the lit side), so faces and bald heads keep a gentle edge"""
    h, w = s.h, s.w
    out = np.zeros((h, w, 4), np.uint8)
    filled = s.mat != None
    for y in range(h):
        for x in range(w):
            if not filled[y, x]:
                a = s.shadow[y, x]
                if a > 0 and a + BAYER[y % 4, x % 4] * .25 > .2: out[y, x] = G.SHADOW + (int(min(1, a) * 150),)
                continue
            m = s.mat[y, x]; ramp = RAMP[m]; k = len(ramp)
            v = int(round(float(np.clip(s.lit[y, x] * (k - 1) + BAYER[y % 4, x % 4] * dither, 0, k - 1))))
            col = ramp[v]
            if not s.noline[y, x]:
                edge = front = False
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    yy, xx = y + dy, x + dx
                    if not (0 <= yy < h and 0 <= xx < w) or not filled[yy, xx]: edge = True
                    elif s.part[yy, xx] > s.part[y, x] and not s.noline[yy, xx]: front = True      # small details (eyes, buttons) cast no edge
                if edge: col = ramp[1 if m in G.SKINS and s.lit[y, x] > .5 else 0]
                elif front: col = ramp[max(0, v - (1 if m in G.SKINS else 2))]
            out[y, x] = col + (255,)
    return Image.fromarray(out, 'RGBA')

HX = 16
def band(c, cx, cy, rx, ry, lo=.25, hi=.95):
    """cel light of a ball: clean bands, light from the top left"""
    return np.clip(lo + (hi - lo) * c.sphere(cx - rx * .15, cy - ry * .2, rx * 1.15, ry * 1.15), 0, 1)

def shoe(c, cx, yb, L, part, w=3.6):
    m = c.ell(cx, yb + 1.2, w, 2.5) & (c.ys <= yb + 2)
    c.paint(m, L.get('shoe', 'shoe'), band(c, cx, yb + .5, w, 2.5, .3, 1), part=part)
    c.paint(m & (c.ys >= yb + 2), 'sole', 1 if L.get('shoe') in ('shoeR', 'shoeW') else 0, part=part, noline=True)

def curls(c, pts, r=3.7):
    """a cloud of round curls: the mask and a light where every curl is its own little ball"""
    m = np.zeros((c.h, c.w), bool); lit = np.zeros((c.h, c.w))
    for cx, cy in pts:
        e = c.ell(cx, cy, r, r); m |= e
        lit = np.where(e, np.maximum(lit, band(c, cx, cy, r, r, .2, 1)), lit)
    return m & (c.ys >= 0), lit

def hair(c, L, o, side=False):
    """paints the hair of a head centred on (HX, 11 + o)"""
    st = L.get('style', 'short'); und = L.get('under'); hy = 11 + o; hx = c.xs + .5 - HX; col = L['hair']; skin = L['skin']
    cap = c.ell(HX - (1 if side else 0), hy - 1.2, 10.6, 9.9)
    ear = c.ell(HX - 2, hy + 2, 2, 2.6)
    shine = (np.abs(np.hypot((c.xs + .5 - HX + 1.5) / 1.1, c.ys + .5 - hy + 1.5) - 6.4) < .75) & (c.xs < HX + 3) & (c.ys < hy - 2)
    lit = band(c, HX, hy - 3, 11, 10, .2, .7) + np.where(shine, .3, 0)
    if st == 'bouffant':                                                # the old lady's big set of curls
        if side:
            pts = [(HX - 2 + 8.4 * np.cos(a), hy - 2.4 + 7.4 * np.sin(a)) for a in np.arange(.72, 1.95, .13) * np.pi]
            pts += [(HX - 2 + 4.4 * np.cos(a), hy - 4 + 4.2 * np.sin(a)) for a in np.arange(.8, 1.9, .26) * np.pi]
            win = c.ell(HX + 4, hy + 3.5, 7.6, 8) & (c.ys > hy - 5)
        else:
            pts = [(HX + 8.8 * np.cos(a), hy - 2 + 7.6 * np.sin(a)) for a in np.arange(.94, 2.07, .125) * np.pi]
            pts += [(HX + 4.6 * np.cos(a), hy - 3.6 + 4 * np.sin(a)) for a in np.arange(1.05, 2, .22) * np.pi]
            win = c.ell(HX, hy + 4.2, 8.3, 8.2) & (c.ys > hy - 4.6)
        m, cl = curls(c, pts, 3.4)
        fill = c.ell(HX - (2 if side else 0), hy - 3.5, 10.5, 9) & (c.ys >= 0)
        hm = (fill | m) & ~win
        if side: hm &= ~ear
        c.paint(hm, col, np.where(m, cl * .9 + .05, .4), part=9)
        return
    if st == 'bald':                                                    # a shiny scalp and grey tufts over the ears
        if side:
            c.paint(c.ell(HX - 6.5, hy + 1.5, 4.2, 5) & c.ell(HX - 1, hy, 10.2, 9.6) & ~ear, col, band(c, HX - 6.5, hy + 1, 4.2, 5, .3, .9), part=9)
            c.paint(c.rect(HX - 1, hy - 8, HX + 3, hy - 6) & c.ell(HX, hy, 9, 9), skin, 1, part=8, noline=True)
        else:
            for sx in (-1, 1):
                c.paint(c.ell(HX + sx * 9.2, hy + .5, 2.6, 4.2), col, band(c, HX + sx * 9.2, hy, 2.6, 4.2, .3, .9), part=9)
            c.paint(c.rect(HX - 5, hy - 8, HX - 1, hy - 6), skin, 1, part=8, noline=True)
        return
    if st == 'mohawk':
        stub = c.ell(HX - (1 if side else 0), hy - 1, 10.2, 9.6) & (c.ys < hy - 3.2)
        c.paint(stub, skin, .5, part=8, noline=False)                   # shaved sides: one flat tone darker
        if side:                                                        # a crest from the forehead to the nape, spikes pointing out
            dx = c.xs + .5 - (HX - 1); dy = c.ys + .5 - (hy - 1)
            rr = np.hypot(dx / 10.2, dy / 9.6) * 9.9; a = np.degrees(np.arctan2(-dy, dx))
            spike = np.abs(((a / 24) % 1) - .5) * 2
            m = (a > 40) & (a < 170) & (rr > 8.3) & (rr < 10.6 + spike * 2.6) & (c.ys >= 0)
            c.paint(m, col, np.clip(.3 + (rr - 8.3) * .17, 0, 1), part=9)
        else:                                                           # a fin down the middle with a jagged top
            k = c.xs - HX; top = np.select([k == -3, k == -2, k == -1, k == 0, k == 1, k == 2], [3, 1, 0, 2, 0, 2], 99)
            m = (top < 99) & (c.ys >= max(0, hy - 14) + top) & (c.ys < hy - 2)
            c.paint(m, col, np.where(k < -1, .95, np.where(k < 1, .65, .35)) - (c.ys > hy - 6) * .12, part=9)
        return
    if side:
        m = cap & ((c.ys < hy - 3.5 + (c.xs > HX + 4) * 1.5) | (c.xs < HX - 3) | ((c.xs < HX + 1) & (c.ys < hy)))
        if 'long' in (st, und): m |= c.ell(HX - 6, hy + 8, 5.5, 12) & (c.ys > hy - 2)
        if 'bob' in (st, und): m |= c.ell(HX - 6, hy + 3, 5.6, 7.4) & (c.ys > hy - 2)
        if st == 'quiff': m |= c.ell(HX + 5, hy - 8.6, 5.4, 3.8) & (c.ys >= 0)
        if st == 'afro': m = c.ell(HX - 2, hy - 1.5, 11.6, 10) & ~(c.ell(HX + 4, hy + 3, 7, 8) & (c.ys > hy - 5))
        if st == 'cap': m = cap & (c.xs < HX - 4) & (c.ys > hy - 2) & (c.ys < hy + 5)
        m &= ~ear
    else:
        fringe = c.ys < hy - 3.6 + 1.6 * np.abs(np.sin(hx * .5 + .6))
        m = cap & (fringe | (np.abs(hx) > 8.6) & (c.ys < hy + 3))
        if 'long' in (st, und): m |= (c.ell(HX - 9, hy + 8, 3.2, 11) | c.ell(HX + 9, hy + 8, 3.2, 11)) & (c.ys > hy - 3)
        if 'bob' in (st, und): m |= (c.ell(HX - 9, hy + 3.5, 3.4, 6.4) | c.ell(HX + 9, hy + 3.5, 3.4, 6.4)) & (c.ys > hy - 3)
        if st == 'quiff': m |= c.ell(HX + 1.5, hy - 9.4, 6.4, 3.4) & (c.ys >= 0)
        if st == 'afro': m = (c.ell(HX, hy - 1.5, 12.6, 10) & (c.ys >= 0)) & ~(c.ell(HX, hy + 4.5, 8.6, 8.5) & (c.ys > hy - 4.4))
        if st == 'cap': m = cap & (np.abs(hx) > 8.4) & (c.ys > hy - 2) & (c.ys < hy + 4)
    if st == 'afro': lit = band(c, HX, hy - 2, 12.6, 10, .15, .75) + (G.noise(c.h, c.w, 2, G.rng(31)) - .5) * .35
    if 'long' in (st, und) and not side: lit = np.where((c.ys > hy + 1) & (np.abs(hx) < 9), .2, np.where(c.ys > hy + 1, np.where(hx < 0, .7, .45), lit))
    c.paint(m, col, np.clip(lit, 0, 1), part=9)
    if st == 'bun': bun(c, col, *((HX - 10, hy - 8.5) if side else (HX, hy - 10.5)))
    if st == 'buns':                                                                                          # two little buns
        for x in ((HX - 5,) if side else (HX - 7.5, HX + 7.5)): bun(c, col, x, hy - 9, 3.5)
    if st == 'bucket': bucket_hat(c, HX - (1 if side else 0), hy)
    if st == 'toque': toque(c, hy)
    if st == 'cap':                                                                                           # a baseball cap
        dome = c.ell(HX - (1 if side else 0), hy - 2, 10.6, 9.2) & (c.ys < hy - 2.6)
        c.paint(dome, 'capB', band(c, HX, hy - 4, 10, 8, .3, 1), part=10)
        peak = c.rect(HX + 2, hy - 4, HX + 14, hy - 1) & c.ell(HX + 6, hy - 2.5, 8, 2.2) if side else c.ell(HX, hy - 2.2, 9.8, 2.2) & (c.ys >= hy - 4)
        c.paint(peak, 'capB', .25 if not side else .5, part=11)
        if not side: c.paint(c.rect(HX - 1, hy - 8, HX + 1, hy - 6), 'white', 1, part=11, noline=True)
    if st == 'hat': straw_hat(c, HX - (1 if side else 0), hy)

def bun(c, col, x, y, rr=4):
    """a round bun, its own shape over the hair"""
    c.paint(c.ell(x, y, rr, rr - .2) & (c.ys >= 0), col, np.clip(band(c, x, y, rr, rr - .2, .3, 1), 0, 1), part=10)

def bucket_hat(c, x, hy):
    """a soft white bucket hat: a low crown and a short brim that slopes down"""
    crown = c.ell(x, hy - 5, 9.4, 6.4) & (c.ys < hy - 3.5) & (c.ys >= 0)
    c.paint(crown, 'hatW', band(c, x, hy - 6, 9.4, 6.4, .4, 1), part=10)
    c.paint(crown & (c.ys >= hy - 5), 'hatW', .3, part=10, noline=True)                                         # the seam
    c.paint(c.ell(x, hy - 2.8, 12.4, 3) & (c.ys >= hy - 4.5) & (c.ys < hy - 1), 'hatW', np.where(c.ys < hy - 3, .85, .5), part=11)

def toque(c, hy):
    """the cook's tall hat (squashed, as it has to fit the frame): three puffs over a band"""
    puff = (c.ell(HX - 6, hy - 9, 5, 4.6) | c.ell(HX, hy - 10, 5.6, 5) | c.ell(HX + 6, hy - 9, 5, 4.6)) & (c.ys >= 0)
    c.paint(puff, 'apron', np.clip(band(c, HX, hy - 10, 11, 5, .5, 1), 0, 1), part=12)
    c.paint(c.rect(HX - 9, hy - 7, HX + 9, hy - 3) & c.ell(HX, hy - 1, 10.4, 9.8), 'apron', np.where(c.ys < hy - 5, .75, .5), part=12)

def straw_hat(c, x, hy):
    """the tourist's straw hat: a round crown with a red band and a wide brim"""
    crown = c.ell(x, hy - 4.5, 8.6, 6.8) & (c.ys < hy - 3) & (c.ys >= 0)
    c.paint(crown, 'strawH', band(c, x, hy - 6, 9, 7, .35, 1) - ((c.xs + c.ys) % 3 == 0) * .12, part=10)
    c.paint(crown & (c.ys >= hy - 6), 'red', np.where(c.xs < x, .75, .45), part=10, noline=True)
    brim = c.ell(x, hy - 3, 14.5, 2.4)
    c.paint(brim, 'strawH', np.where(c.ys < hy - 3, .95, .5) - ((c.xs + c.ys) % 3 == 0) * .1, part=11)

def head(c, L, o, side=False):
    """the round head of today's people (20 px wide), with the hair, face and extras of the look"""
    skin, eye = L['skin'], L['eye']; hy = 11 + o; ex_ = L.get('extras', ())
    if not side:
        c.paint(c.ell(HX - 9.9, hy + 2, 1.6, 2.2) | c.ell(HX + 9.9, hy + 2, 1.6, 2.2), skin, .5, part=7)     # ears
    c.paint(c.ell(HX, hy, 10 - (.3 if side else 0), 9.5), skin, .6 + c.sphere(HX + (1 if side else 0), hy, 10, 10) * .3, part=8)
    if side: c.paint(c.ell(HX - 2, hy + 2, 1.6, 2.2), skin, .5, part=8, noline=True); c.paint(c.rect(HX - 2, hy + 1, HX - 1, hy + 3), skin, .25, part=8, noline=True)                                   # the ear, with its own edge
    if side: c.paint(c.ell(HX + 9.6, hy + 3.3, 1.7, 1.5), skin, .8, part=8)                                   # the nose
    hair(c, L, o, side)
    def eye_at(ex):
        """a big glossy eye, 3 x 4: a lash line, dark, then the iris colour along the bottom, and one catch light"""
        c.paint(c.rect(ex, hy - 1, ex + 3, hy + 3), eye, np.where(c.ys >= hy + 2, .6, .05), part=10, noline=True)
        c.paint(c.rect(ex, hy - 1, ex + 3, hy), 'lash', 0, part=10, noline=True)
        c.paint(c.rect(ex, hy, ex + 1, hy + 2), 'white', 1, part=11, noline=True)
    old = L.get('old')
    if side:
        ex = HX + 4; eye_at(ex)
        c.paint(c.rect(ex - 2, hy + 4, ex, hy + 5), 'blush' + skin, 0, part=10, noline=True)
        if 'moustache' in ex_: c.paint(c.rect(HX + 5, hy + 5, HX + 9, hy + 7) & c.ell(HX, hy, 9.6, 9.4), L['hair'], np.where(c.ys < hy + 6, .75, .5), part=11, noline=True)
        else: c.paint(c.rect(HX + 6, hy + 6, HX + 8, hy + 7), skin, 0, part=10, noline=True); c.paint(c.rect(HX + 5, hy + 5, HX + 6, hy + 6), skin, .25, part=10, noline=True)
        if 'glasses' in ex_:
            c.paint((c.rect(ex - 1, hy - 2, ex + 4, hy + 4) & ~c.rect(ex, hy - 1, ex + 3, hy + 3)) | c.rect(HX - 1, hy, ex - 1, hy + 1), 'gold', .55, part=12, noline=True)
        if 'piercing' in ex_: c.paint(c.rect(HX - 2, hy + 4, HX - 1, hy + 6), 'chrome', 1, part=12, noline=True)
        if 'beard' in ex_:
            bd = c.ell(HX, hy, 9.7, 9.5) & (c.ys >= hy + 4) & (c.xs >= HX - 3) & ~c.rect(HX + 5, hy + 5, HX + 10, hy + 7)
            c.paint(bd, L['hair'], np.where(c.ys < hy + 6, .7, .45), part=9, noline=True)
        return
    for ex in (HX - 5, HX + 2): eye_at(ex)
    c.paint(c.rect(HX - 7, hy + 4, HX - 5, hy + 5) | c.rect(HX + 5, hy + 4, HX + 7, hy + 5), 'blush' + skin, 0, part=10, noline=True)
    if old:                                                             # a line under each eye
        for ex in (HX - 5, HX + 2): c.paint(c.rect(ex, hy + 4, ex + 3, hy + 5), skin, .5, part=9, noline=True)
    if 'moustache' in ex_:
        mo = (c.rect(HX - 4, hy + 5, HX + 4, hy + 7) | c.rect(HX - 5, hy + 6, HX + 5, hy + 8)) & ~c.rect(HX - 1, hy + 7, HX + 1, hy + 8) & ~c.rect(HX - 5, hy + 6, HX - 4, hy + 7) & ~c.rect(HX + 4, hy + 6, HX + 5, hy + 7)
        c.paint(mo, L['hair'], np.where(c.ys < hy + 6, .75, .5) - (np.abs(c.xs + .5 - HX) < 1) * .25, part=11, noline=True)   # a bushy moustache, parted in the middle
    else:                                                               # a small smile
        c.paint(c.rect(HX - 1, hy + 6, HX + 1, hy + 7), skin, 0, part=10, noline=True)
        c.paint(c.rect(HX - 2, hy + 5, HX - 1, hy + 6) | c.rect(HX + 1, hy + 5, HX + 2, hy + 6), skin, .25, part=10, noline=True)
    if 'glasses' in ex_:
        for ex in (HX - 6, HX + 1):
            c.paint(c.rect(ex, hy - 2, ex + 5, hy + 4) & ~c.rect(ex + 1, hy - 1, ex + 4, hy + 3), 'gold', .55, part=12, noline=True)
        c.paint(c.rect(HX - 1, hy, HX + 1, hy + 1), 'gold', .55, part=12, noline=True)
    if 'piercing' in ex_: c.paint(c.rect(HX + 10, hy + 3, HX + 11, hy + 5), 'chrome', 1, part=12, noline=True)
    if 'beard' in ex_:
        bd = c.ell(HX, hy, 10, 9.5) & (c.ys >= hy + 4) & ~c.rect(HX - 3, hy + 4, HX + 3, hy + 7) & ~(c.rect(HX - 5, hy + 4, HX + 5, hy + 5))
        c.paint(bd, L['hair'], np.where(c.ys < hy + 6, .7, .45), part=9, noline=True)

# ---- the body seen from the front: one rounded line from the neck over the shoulders into the arms ----
def handbag(c, x, y):
    """a small leather handbag hanging from the hand at (x, y): two straps, a flap and a gold clasp"""
    c.paint(c.rect(x - 2, y, x - 1, y + 4) | c.rect(x + 1, y, x + 2, y + 4), 'bagB', .3, part=7, noline=True)
    body = c.rect(x - 4, y + 3, x + 4, y + 9) & ~(c.rect(x - 4, y + 8, x - 3, y + 9) | c.rect(x + 3, y + 8, x + 4, y + 9))
    c.paint(body, 'bagB', np.where(c.ys < y + 5, .9, np.where(c.xs < x, .65, .45)), part=7)
    c.paint(c.rect(x - 1, y + 5, x + 1, y + 6), 'gold', .9, part=8, noline=True)

def sil(c, o):
    """the body's outline from the front: it widens in rounded steps from the neck to the shoulders (3, 6, 8, then 9 px each side)"""
    ax = np.abs(c.xs + .5 - 16)
    hw = np.select([c.ys < 21 + o, c.ys == 21 + o, c.ys == 22 + o, c.ys == 23 + o], [0, 3, 6, 8], 9)
    return ax < hw
def torso_mask(c, o): return sil(c, o) & (np.abs(c.xs + .5 - 16) < 6) & (c.ys < 39 + o)

def top_front(c, L, o):
    top, shirt, skin = L['top'], L['shirt'], L['skin']
    torso = torso_mask(c, o); cx = 16
    lit = c.cyl_x(7, 25, .35, .9) - np.where(c.ys > 34 + o, .1, 0) - np.where(c.ys < 23 + o, .18, 0)          # darker under the chin and at the waist
    c.paint(c.rect(14, 19 + o, 18, 23 + o), skin, .5, part=3)                                                  # neck
    if top == 'hoodie': c.paint(c.ell(16, 22 + o, 8.6, 3), shirt, .3, part=3)                                 # the hood, behind the neck
    c.paint(torso, shirt, lit, part=4)
    if top == 'sweater':
        c.paint(torso & (c.ys >= 37 + o), shirt, .2 + (c.xs % 2) * .2, part=4)                                 # ribbed hem
        c.paint(c.ell(cx, 22 + o, 3.2, 1.5), shirt, .25, part=5)                                                 # round collar
    elif top == 'hoodie':
        c.paint(c.rect(11, 32 + o, 21, 37 + o) & (np.abs(c.xs + .5 - cx) < 5.5 - (36 + o - c.ys) * .35), shirt, .28, part=5)   # pocket
        for x in (14, 17): c.paint(c.rect(x, 24 + o, x + 1, 29 + o), 'white', .8, part=6, noline=True)               # strings
        c.paint(c.ell(cx, 22 + o, 3, 1.5), skin, .5, part=5)
    elif top == 'tee':
        c.paint(c.ell(cx, 22 + o, 3, 1.5), skin, .5, part=5)
        star = [(2, 0), (1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (1, 3), (2, 3), (3, 3), (1, 4), (3, 4)]
        for dx, dy in star: c.paint(c.rect(cx - 2.5 + dx, 28 + o + dy, cx - 1.5 + dx, 29 + o + dy), 'white', 1, part=6, noline=True)
    elif top == 'stripes':
        c.paint(torso & ((c.ys - o) % 3 == 0) & (c.ys > 23 + o), 'white', .95, part=4, noline=True)
        c.paint(c.ell(cx, 22 + o, 3.4, 1.6), skin, .5, part=5)
    elif top == 'hawaii':
        flowers(c, torso)
        c.paint((np.abs(c.xs + .5 - cx) < (27 + o - c.ys) * .55) & (c.ys >= 21 + o) & (c.ys < 27 + o) & torso, skin, .55, part=5)   # open collar
    elif top == 'dress':
        c.paint(c.ell(cx, 21.6 + o, 4.4, 2.6) & torso, skin, .55, part=5)                                          # round neckline
        for k in range(-3, 4): c.paint(c.rect(cx + k * 1.6 - .5, 22 + o + (3 - abs(k)) * .7, cx + k * 1.6 + .5, 23 + o + (3 - abs(k)) * .7), 'plate', 1, part=7, noline=True)
    elif top == 'polo':
        c.paint((np.abs(c.xs + .5 - cx) < (25 + o - c.ys) * .6) & (c.ys >= 21 + o) & (c.ys < 25 + o) & torso, skin, .55, part=5)
        for x in (cx - 5, cx + 2): c.paint(c.rect(x, 21 + o, x + 3, 23 + o) & torso, shirt, 1, part=6)             # collar
        c.paint(c.rect(cx, 25 + o, cx + 1, 30 + o), shirt, .2, part=5, noline=True)
    elif top == 'tang':                                                                                        # a silk jacket: stand collar and knot buttons
        c.paint(c.rect(cx - 3, 21 + o, cx + 3, 23 + o) & torso, shirt, .15, part=5)
        c.paint(c.rect(cx, 23 + o, cx + 1, 39 + o), shirt, .12, part=5, noline=True)
        for y in (25, 28, 31, 34): c.paint(c.rect(cx - 2, y + o, cx + 3, y + o + 1), 'gold', .85, part=6, noline=True)
    elif top == 'qipao':                                                                                       # stand collar, a gold line across to the arm
        gold_dots(c, torso & (c.ys > 27 + o))
        c.paint(c.rect(cx - 3, 21 + o, cx + 3, 23 + o) & torso, shirt, .2, part=5)
        c.paint((np.abs(c.ys - (23 + o) - (c.xs + .5 - cx) * .6) < .6) & (c.xs >= cx) & torso, 'gold', .85, part=6, noline=True)
    elif top == 'waiter':                                                                                      # white shirt, black waistcoat, red bow tie
        vest = torso & (c.ys >= 23 + o) & (c.ys < 37 + o) & ~((np.abs(c.xs + .5 - cx) < (31 + o - c.ys) * .4) & (c.ys < 31 + o))
        c.paint(vest, 'vest', c.cyl_x(7, 25, .3, .85), part=5)
        c.paint(c.rect(cx - 3, 22 + o, cx + 3, 24 + o) & ~c.rect(cx - 1, 22 + o, cx + 1, 23 + o), 'red', np.where(c.xs < cx, .8, .5), part=6)
        for y in (32, 35): c.paint(c.rect(cx, y + o, cx + 1, y + o + 1), 'gold', .8, part=6, noline=True)
    elif top == 'cook':                                                                                        # white jacket with two rows of buttons, red neckerchief
        for y in (26, 30, 34):
            for x in (13, 18): c.paint(c.rect(x, y + o, x + 1, y + o + 1), 'chrome', .35, part=5, noline=True)
        c.paint(c.ell(cx, 22.2 + o, 3.8, 2) & torso, 'red', .65, part=5)
        c.paint(c.rect(cx - 1, 23 + o, cx + 1, 26 + o), 'red', .45, part=6)
    elif top == 'suit':
        v = (np.abs(c.xs + .5 - cx) < (31 + o - c.ys) * .42) & (c.ys >= 21 + o) & (c.ys < 31 + o)
        c.paint(v & torso, 'white', .9, part=5)
        if L.get('tie', 'tie'):
            c.paint(c.rect(cx - 1, 23 + o, cx + 1, 31 + o), L.get('tie', 'tie'), np.where(c.xs < cx, .9, .45), part=6)
            c.paint(c.rect(cx - 1, 22 + o, cx + 1, 24 + o), L.get('tie', 'tie'), .2, part=6, noline=True)
        for y in (33, 36): c.paint(c.rect(cx, y + o, cx + 1, y + o + 1), 'gold', .8, part=6, noline=True)
        c.paint(c.rect(18, 28 + o, 21, 29 + o), 'white', .9, part=6, noline=True)                                   # pocket square
    elif top == 'granny':                                                                                      # a dotted dress under an open cardigan
        fr_ = c.rect(cx - 3, 21 + o, cx + 3, 39 + o) & torso
        c.paint(fr_, L['pants'], .55 + ((c.xs * 3 + c.ys * 5) % 7 == 0) * .4, part=5)
        for k in range(-3, 4): c.paint(c.rect(cx + k * 1.6 - .5, 22.6 + o + (3 - abs(k)) * .8, cx + k * 1.6 + .5, 23.6 + o + (3 - abs(k)) * .8), 'plate', 1, part=7, noline=True)   # pearls
    elif top == 'leather':
        c.paint(c.rect(cx, 24 + o, cx + 1, 39 + o), 'chrome', .8, part=5, noline=True)                             # zip
        c.paint((np.abs(c.xs + .5 - cx) < (27 + o - c.ys) * .8) & (c.ys >= 21 + o) & (c.ys < 27 + o) & torso, 'shirtW', .8, part=5)
        for x in (11, 20): c.paint(c.rect(x, 27 + o, x + 1, 28 + o), 'chrome', 1, part=6, noline=True)
        c.paint(c.rect(10, 36 + o, 22, 37 + o) & torso, 'chrome', .5, part=6, noline=True)                         # belt of studs
    if 'camera' in L.get('extras', ()):                                                                         # a camera round the neck
        strap = (np.abs(np.abs(c.xs + .5 - cx) - (1.5 + (30 + o - c.ys) * .4)) < .6) & (c.ys >= 22 + o) & (c.ys < 30 + o)
        c.paint(strap & torso, 'onyx', .3, part=6, noline=True)
        c.paint(c.rect(cx - 3, 29 + o, cx + 3, 34 + o), 'onyx', np.where(c.ys < 30 + o, .9, .5), part=7)           # the camera
        c.paint(c.ell(cx, 31.6 + o, 1.7, 1.7), 'chrome', band(c, cx, 31.6 + o, 1.7, 1.7, .3, 1), part=8, noline=True)

def gold_dots(c, m):
    """small gold flowers woven into the silk"""
    c.paint(m & ((c.xs * 7 + c.ys * 4) % 13 == 0), 'gold', .9, part=4, noline=True)

def flowers(c, m):
    """little cream and yellow flowers over a mask (the tourist's shirt)"""
    c.paint(m & ((c.xs * 5 + c.ys * 3) % 11 == 0), 'cream', 1, part=4, noline=True)
    c.paint(m & ((c.xs * 5 + c.ys * 3) % 11 == 5) & (c.ys % 2 == 0), 'shirtY', .9, part=4, noline=True)

BARE = {'tee': 29, 'stripes': 29, 'hawaii': 29, 'polo': 29, 'dress': 26, 'qipao': 26}     # tops with short sleeves: where the bare arm starts

def arms_front(c, L, o, al, ar, back=False):
    """arms hang from round shoulders: the shoulder is part of the body's outline, the arm only shows
    as its own shape lower down; a swinging arm gets a little longer or shorter, the shoulder stays"""
    shirt, skin, top = L['shirt'], L['skin'], L['top']; ex_ = L.get('extras', ())
    for sx, d in ((-1, al), (1, ar)):
        x0 = 7 if sx < 0 else 21; cx = x0 + 2; yb = 35 + o + d
        if sx == (-1 if back else 1) and 'cane' in ex_: yb = 33 + o
        arm = sil(c, o) & c.rect(x0, 0, x0 + 4, yb)
        lit = np.clip((.82 if sx < 0 else .55) - (c.xs + .5 - x0) * .06 + np.where(c.ys < 24 + o, .12, 0), 0, 1)
        c.paint(arm & (c.ys < 27 + o), shirt, lit, part=4)                                                       # shoulder: one outline with the body
        c.paint(arm & (c.ys >= 27 + o), shirt, lit, part=5)
        low = arm & (c.ys >= 27 + o)
        if top in BARE: c.paint(arm & (c.ys >= BARE[top] + o), skin, .7 if sx < 0 else .5, part=5)
        elif top in ('sweater', 'hoodie', 'granny', 'waiter', 'cook'): c.paint(low & (c.ys >= yb - 2), shirt, .22, part=5)            # cuff
        elif top in ('suit', 'tang'): c.paint(low & (c.ys >= yb - 1), 'white', .9, part=5)
        if top == 'stripes': c.paint(arm & (c.ys < 29 + o) & (c.ys > 23 + o) & ((c.ys - o) % 3 == 0), 'white', .95, part=5, noline=True)
        if top == 'hawaii': flowers(c, arm & (c.ys < 29 + o))
        c.paint(c.ell(cx, yb + 1, 2, 2), skin, band(c, cx, yb + 1, 2, 2, .5, .9), part=6)                           # hand
    if back:                                                                                                    # from behind: the cane and the bag change sides
        if 'cane' in ex_:
            c.paint(c.rect(7, 35 + o, 9, 55), 'oak', np.where(c.xs < 8, .8, .4), part=5)
            c.paint(c.rect(6, 33 + o, 11, 35 + o), 'oak', .6, part=5)
        if 'bag' in ex_: handbag(c, 23, 36 + o + ar)
        return
    if 'pack' in ex_:                                                                                           # backpack straps
        for x in (10, 20): c.paint(c.rect(x, 21 + o, x + 2, 33 + o) & sil(c, o), 'pack', np.where(c.xs < x + 1, .9, .5), part=6)
    if 'phone' in ex_:
        c.paint(c.rect(21, 34 + o + ar, 25, 40 + o + ar), 'onyx', .6, part=7); c.paint(c.rect(22, 35 + o + ar, 24, 39 + o + ar), 'neonC', .7, part=8, noline=True)
    if 'cane' in ex_:
        c.paint(c.rect(23, 35 + o, 25, 55), 'oak', np.where(c.xs < 24, .8, .4), part=5)
        c.paint(c.rect(21, 33 + o, 26, 35 + o), 'oak', .6, part=5)
        c.paint(c.rect(23, 54, 25, 55), 'iron', .3, part=5, noline=True)
    if 'bag' in ex_: handbag(c, 9, 36 + o + al)

def legs_front(c, L, o, ld, rd):
    pants, skin, legs = L['pants'], L['skin'], L.get('legs', 'pants')
    shin = skin if legs in ('shorts', 'skirt') else pants
    for k, (x0, d) in enumerate(((10, ld), (17, rd))):
        yb = 52 + d
        c.paint(c.rect(x0, 40 + o, x0 + 5, yb), shin, c.cyl_x(x0, x0 + 5, .3, .9) - (.12 if d < 0 else 0), part=1)
        if legs == 'pants': c.paint(c.rect(x0, yb - 1, x0 + 5, yb), pants, .15, part=1, noline=True)             # hem
        if legs == 'shorts': c.paint(c.rect(x0, yb - 3, x0 + 5, yb), 'white', .8 - (c.ys == yb - 2) * .5, part=1)   # socks
        if L.get('old') and legs == 'skirt': c.paint(c.rect(x0, 40 + o, x0 + 5, yb), 'cream', c.cyl_x(x0, x0 + 5, .3, .7), part=1)   # stockings
        shoe(c, x0 + 2.5, yb, L, 2, 3.6 + (.4 if d > 0 else 0))
    if legs == 'skirt':
        ln = L.get('skirt', 10)
        sk = (c.ys >= 37 + o) & (c.ys < 37 + ln + o) & (np.abs(c.xs + .5 - 16) < 6.4 + (c.ys - 37 - o) * .22)
        lit = c.cyl_x(8, 24, .3, .9) - ((c.xs + 1) % 4 == 0) * .2
        if L['top'] == 'granny': lit = c.cyl_x(8, 24, .35, .75) + ((c.xs * 3 + c.ys * 5) % 7 == 0) * .35
        c.paint(sk, pants, lit, part=3)
        if L['top'] == 'qipao': gold_dots(c, sk); c.paint(sk & (c.ys >= 36 + ln + o), 'gold', .7, part=3, noline=True)
    else:
        hips = c.rect(10, 37 + o, 22, 43 + o if legs == 'pants' else 46 + o) & ~(c.rect(15, 43 + o, 17, 60))
        c.paint(hips, pants, c.cyl_x(9, 23, .3, .9), part=3)
        if legs == 'shorts':
            for x0 in (10, 17): c.paint(c.rect(x0, 40 + o, x0 + 5, 46 + o), pants, c.cyl_x(x0, x0 + 5, .3, .9), part=3)
        c.paint(c.rect(10, 38 + o, 22, 39 + o), 'shoe' if L['top'] != 'leather' else 'chrome', .5, part=4, noline=True)   # belt
    if L['top'] == 'waiter': c.paint(c.rect(10, 37 + o, 22, 48 + o), 'apron', .9 - (c.xs % 4 == 1) * .12 - (c.ys > 45 + o) * .15, part=4)   # long apron
    if L['top'] == 'cook': c.paint(c.rect(10, 36 + o, 22, 44 + o), 'red', .55 + ((c.xs + c.ys) % 4 < 2) * .2, part=4)                      # checked apron

STEP_F = {None: (0, 0, 0, 0, 0), 0: (0, 1, -2, -1, 1), 1: (-1, 0, 0, 0, 0), 2: (0, -2, 1, 1, -1), 3: (-1, 0, 0, 0, 0)}   # body, left foot, right foot, left arm, right arm
def front(L, f=None):
    c = Canvas(32, 58); o, ld, rd, al, ar = STEP_F[f]; o += L.get('drop', 0)                                     # some people are a little shorter
    c.cast(c.ell(16, 55.2, 8.5, 2.2), .4)
    legs_front(c, L, o, ld, rd); top_front(c, L, o); arms_front(c, L, o, al, ar); head(c, L, o)
    return render(c)

def side_torso(c, L, o):
    """neck, torso and what is worn on it, seen from the side; returns the lean of the old and the torso's mask"""
    skin, shirt, pants, top = L['skin'], L['shirt'], L['pants'], L['top']; ex_ = L.get('extras', ()); old = L.get('old')
    lf = 1 if old else 0                                                                                       # old people lean forward a little
    c.paint(c.rect(14 + lf, 19 + o, 18 + lf, 23 + o), skin, .5, part=3)
    if top == 'hoodie': c.paint(c.ell(11.5, 23.5 + o, 4.5, 4), shirt, .3, part=5)                                # the hood on the back
    if 'pack' in ex_: c.paint(c.ell(8.5, 30 + o, 4, 7), 'pack', band(c, 8.5, 30 + o, 4, 7, .3, 1), part=5)
    torso = (c.ell(15.5 + lf, 26.5 + o, 5.6, 5.6) & (c.ys >= 21 + o)) | c.rect(10, 26 + o, 21 + lf, 39 + o) & c.ell(15.5 + lf * .5, 31 + o, 5.8 + lf * .5, 9)
    c.paint(torso, shirt, c.cyl_x(9, 22, .3, .9), part=6)
    if top == 'sweater': c.paint(torso & (c.ys >= 37 + o), shirt, .2 + (c.xs % 2) * .2, part=6)
    if top == 'suit': c.paint(c.rect(19, 23 + o, 22, 30 + o) & torso, 'white', .9, part=7); c.paint(c.rect(20 + lf, 24 + o, 21 + lf, 31 + o), L.get('tie', 'tie') or 'white', .7, part=7, noline=True)
    if top == 'granny': c.paint(c.rect(19, 23 + o, 23, 39 + o) & torso, pants, .55 + ((c.xs * 3 + c.ys * 5) % 7 == 0) * .4, part=7)
    if top == 'leather': c.paint(c.rect(20, 23 + o, 21, 39 + o) & torso, 'chrome', .8, part=7, noline=True)
    if top == 'stripes': c.paint(torso & ((c.ys - o) % 3 == 0) & (c.ys > 23 + o), 'white', .95, part=6, noline=True)
    if top == 'hawaii': flowers(c, torso)
    if 'camera' in ex_:
        c.paint(c.rect(20, 29 + o, 24, 34 + o), 'onyx', np.where(c.ys < 30 + o, .9, .5), part=7)                     # the camera on the chest
        c.paint(c.rect(23, 30 + o, 25, 33 + o), 'chrome', .7, part=7)
        c.paint((np.abs(c.xs + .5 - 17 - (c.ys - 22 - o) * .55) < .7) & (c.ys >= 22 + o) & (c.ys < 30 + o) & torso, 'onyx', .3, part=7, noline=True)
    if top == 'polo': c.paint(c.rect(18, 21 + o, 21, 23 + o), shirt, 1, part=7)
    if top in ('tang', 'qipao'): c.paint(c.rect(15 + lf, 21 + o, 20 + lf, 23 + o), shirt, .15, part=7)
    if top == 'tang':
        for y in (25, 28, 31, 34): c.paint(c.rect(19, y + o, 21, y + o + 1) & torso, 'gold', .85, part=7, noline=True)
    if top == 'qipao': gold_dots(c, torso & (c.ys > 27 + o))
    return lf, torso

def side(L, f=None):
    """facing right"""
    c = Canvas(32, 58); skin, shirt, pants, top, legs = L['skin'], L['shirt'], L['pants'], L['top'], L.get('legs', 'pants')
    ex_ = L.get('extras', ()); old = L.get('old')
    o = (-1 if f in (1, 3) else 0) + L.get('drop', 0)
    c.cast(c.ell(16, 55.2, 8, 2.2), .4)
    shin = skin if legs in ('shorts', 'skirt') else pants
    if old and legs == 'skirt': shin = 'cream'
    st = 3 if old else 5                                                                                       # old people take shorter steps
    lean = {None: (0, 0), 0: (-st, st), 1: (-1, 1), 2: (st, -st), 3: (1, -1)}[f]                                 # far leg, near leg: how far the foot is from the hip
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
        ln = L.get('skirt', 10)
        lit = c.cyl_x(10, 22, .3, .9)
        if top == 'granny': lit = c.cyl_x(10, 22, .35, .75) + ((c.xs * 3 + c.ys * 5) % 7 == 0) * .35
        skm = (c.ys >= 37 + o) & (c.ys < 37 + ln + o) & (np.abs(c.xs + .5 - 16) < 4.6 + (c.ys - 37 - o) * .25)
        c.paint(skm, pants, lit, part=5)
        if top == 'qipao': gold_dots(c, skm)
    else:
        c.paint(c.rect(11, 37 + o, 20, 43 + o if legs == 'pants' else 46 + o), pants, c.cyl_x(11, 20, .3, .9), part=5)
    lf, torso = side_torso(c, L, o)
    sw = {None: 0, 0: 3, 1: 1, 2: -3, 3: -1}[f]                                                                  # near arm swings against the near leg
    if 'cane' in ex_: sw = 4                                                                                     # the hand stays on the cane
    ax = 15.5 + lf + (c.ys - 24 - o) / 12 * sw
    yb = 36 + o - (2 if 'cane' in ex_ else 0)
    arm = (c.ys >= 24 + o) & (c.ys < yb) & (np.abs(c.xs + .5 - ax) < 2.6)
    behind = (np.roll(arm, 1, axis=1) | np.roll(arm, 2, axis=1)) & ~arm & (c.mat != None)                      # the arm's shadow on the body
    c.lit[behind] = np.clip(c.lit[behind] - .28, 0, 1)
    c.paint(arm, shirt, np.clip(1 - np.abs(c.xs + .5 - ax + .8) * .22, 0, 1), part=8)
    if top == 'stripes': c.paint(arm & (c.ys < 29 + o) & ((c.ys - o) % 3 == 0), 'white', .95, part=8, noline=True)
    if top == 'hawaii': flowers(c, arm & (c.ys < 29 + o))
    if top in BARE: c.paint(arm & (c.ys >= BARE[top] + o), skin, .7, part=8)
    elif top in ('suit', 'tang'): c.paint(arm & (c.ys >= yb - 1), 'white', .9, part=8)
    elif top != 'leather': c.paint(arm & (c.ys >= yb - 2), shirt, .22, part=8)
    hxp = 15.5 + lf + (yb - 24 - o) / 12 * sw
    if 'cane' in ex_:
        c.paint(c.rect(hxp - .5, yb + 1, hxp + 1.5, 55), 'oak', np.where(c.xs < hxp + .5, .8, .4), part=7)
        c.paint(c.rect(hxp - 2.5, yb, hxp + 2.5, yb + 2), 'oak', .6, part=7)
    c.paint(c.ell(hxp, yb + 1, 2.3, 2.1), skin, .75, part=9)
    if 'phone' in ex_: c.paint(c.rect(16 + sw, 33 + o, 19 + sw, 38 + o), 'onyx', .6, part=10)
    if 'bag' in ex_: handbag(c, int(round(hxp)), yb + 1)
    c.xs = c.xs - lf; head(c, L, o, side=True); c.xs = c.xs + lf                                              # the head a pixel forward for the old
    return render(c)

# ---- seen from behind (walking up): the same body, the back of each top and of each head of hair ----
def head_back(c, L, o):
    skin, col = L['skin'], L['hair']; st = L.get('style', 'short'); hy = 11 + o; hx = c.xs + .5 - HX
    c.paint(c.ell(HX - 9.9, hy + 2, 1.6, 2.2) | c.ell(HX + 9.9, hy + 2, 1.6, 2.2), skin, .5, part=7)            # ears
    c.paint(c.ell(HX, hy, 10, 9.5), skin, .55 + c.sphere(HX, hy, 10, 10) * .3, part=8)
    cap = c.ell(HX, hy - 1.2, 10.6, 9.9) & (c.ys >= 0)
    shine = (np.abs(np.hypot((hx + 1.5) / 1.1, c.ys + .5 - hy + 1.5) - 6.4) < .75) & (c.xs < HX + 3) & (c.ys < hy - 2)
    lit = band(c, HX, hy - 3, 11, 10, .2, .7) + np.where(shine, .3, 0)
    nape = c.ys < hy + 4.6 + (np.abs(hx) < 6) * 1.4                                                            # the hairline at the neck
    if st == 'bald':
        c.paint(cap & (c.ys > hy + .5) & nape, col, band(c, HX, hy + 2, 11, 5, .3, .9), part=9)                 # a grey band from ear to ear
        c.paint(c.rect(HX - 5, hy - 7, HX - 1, hy - 5), skin, 1, part=8, noline=True)
    elif st == 'mohawk':
        c.paint(c.ell(HX, hy - 1, 10.2, 9.6) & nape, skin, .5, part=8)
        k = c.xs - HX; top = np.select([k == -3, k == -2, k == -1, k == 0, k == 1, k == 2], [3, 1, 0, 2, 0, 2], 99)
        m = (top < 99) & (c.ys >= max(0, hy - 14) + top) & (c.ys < hy + 6 - np.abs(hx) * .8)
        c.paint(m, col, np.where(k < -1, .95, np.where(k < 1, .65, .35)) - (c.ys > hy - 6) * .12, part=9)
    elif st == 'bouffant':
        pts = [(HX + 8.8 * np.cos(a), hy - 2 + 7.6 * np.sin(a)) for a in np.arange(0, 2, .125) * np.pi]
        pts += [(HX + 4.6 * np.cos(a), hy - 2.5 + 4 * np.sin(a)) for a in np.arange(0, 2, .25) * np.pi] + [(HX, hy - 2.5)]
        m, cl = curls(c, pts, 3.4)
        c.paint((m | c.ell(HX, hy - 2.5, 10.5, 9)) & (c.ys < hy + 7) & (c.ys >= 0), col, np.where(m, cl * .9 + .05, .4), part=9)
    elif st == 'afro':
        m = c.ell(HX, hy - 1.5, 12.6, 10.6) & (c.ys >= 0)
        c.paint(m, col, np.clip(band(c, HX, hy - 2, 12.6, 10, .15, .75) + (G.noise(c.h, c.w, 2, G.rng(31)) - .5) * .35, 0, 1), part=9)
    else:
        m = cap & nape
        if st == 'bob': m = cap | (c.ell(HX, hy + 3, 10.9, 7.6) & (c.ys > hy - 2))
        if st == 'long':
            m = cap | (c.ell(HX, hy + 9, 10.6, 13) & (c.ys > hy - 2))
            lit = np.where(c.ys > hy + 1, np.clip(.75 - (hx + 4) * .035 - (c.xs % 3 == 0) * .14, 0, 1), lit)      # strands down the back
        c.paint(m, col, np.clip(lit, 0, 1), part=9)
        if st == 'bun': bun(c, col, HX, hy - 10.5)
        if st == 'cap':
            c.paint(cap & (c.ys < hy + 1.5), 'capB', band(c, HX, hy - 4, 10, 8, .3, 1), part=10)
            c.paint(c.ell(HX, hy + 1.5, 3, 2.4) & (c.ys < hy + 1.5), col, .3, part=10, noline=True)                # the gap over the strap
            c.paint(c.rect(HX - 3, hy + 1, HX + 3, hy + 2), 'capB', .2, part=10, noline=True)
        if st == 'hat': straw_hat(c, HX, hy)
        if st == 'bucket': bucket_hat(c, HX, hy)
        if st == 'buns':
            for x in (HX - 7.5, HX + 7.5): bun(c, col, x, hy - 9, 3.5)

def top_back(c, L, o):
    top, shirt, skin = L['top'], L['shirt'], L['skin']; ex_ = L.get('extras', ())
    torso = torso_mask(c, o); cx = 16
    lit = c.cyl_x(7, 25, .35, .9) - np.where(c.ys > 34 + o, .1, 0) - np.where(c.ys < 23 + o, .18, 0)
    c.paint(c.rect(14, 19 + o, 18, 23 + o), skin, .45, part=3)
    c.paint(torso, shirt, lit, part=4)
    if top == 'sweater':
        c.paint(torso & (c.ys >= 37 + o), shirt, .2 + (c.xs % 2) * .2, part=4)
        c.paint(c.rect(13, 21 + o, 19, 22 + o), shirt, .25, part=5, noline=True)
    elif top == 'hoodie':                                                                                      # the hood hangs on the back
        hood = c.ell(cx, 25 + o, 6.6, 5) & (c.ys >= 21 + o)
        c.paint(hood, shirt, np.clip(band(c, cx, 25 + o, 6.6, 5, .25, .85), 0, 1), part=5)
        c.paint(c.ell(cx, 23.6 + o, 4, 2.2) & hood, shirt, .12, part=5, noline=True)                               # its opening
    elif top == 'stripes':
        c.paint(torso & ((c.ys - o) % 3 == 0) & (c.ys > 23 + o), 'white', .95, part=4, noline=True)
    elif top == 'hawaii':
        flowers(c, torso)
    elif top == 'suit':
        c.paint(c.rect(13, 21 + o, 19, 22 + o) & torso, 'white', .9, part=5, noline=True)                          # shirt collar
        c.paint(c.rect(cx, 33 + o, cx + 1, 39 + o), shirt, .1, part=5, noline=True)                                # vent
    elif top == 'granny':
        c.paint(torso & (c.ys >= 37 + o), shirt, .25 + (c.xs % 2) * .15, part=4)
    elif top == 'leather':
        c.paint(c.rect(12, 21 + o, 20, 23 + o) & torso, shirt, .15, part=5, noline=True)                           # collar
        for dx, dy in ((0, 0), (1, 0), (2, 0), (0, 1), (2, 1), (0, 2), (1, 2), (2, 2), (1, 3)):                      # a badge
            c.paint(c.rect(cx - 1.5 + dx, 27 + o + dy, cx - .5 + dx, 28 + o + dy), 'chrome', .9, part=6, noline=True)
        c.paint(c.rect(10, 36 + o, 22, 37 + o) & torso, 'chrome', .5, part=6, noline=True)
    elif top == 'dress':
        c.paint(c.ell(cx, 21.2 + o, 4, 1.8) & torso, skin, .5, part=5)
    if top == 'polo': c.paint(c.rect(12, 21 + o, 20, 23 + o) & torso, shirt, 1, part=5)
    if top in ('tang', 'qipao'): c.paint(c.rect(13, 21 + o, 19, 23 + o) & torso, shirt, .15, part=5)
    if top == 'qipao': gold_dots(c, torso & (c.ys > 25 + o))
    if 'camera' in ex_: c.paint(c.rect(12, 22 + o, 20, 23 + o) & torso, 'onyx', .3, part=6, noline=True)        # the camera strap
    if 'pack' in ex_:                                                                                           # the backpack
        bp = c.rect(10, 23 + o, 22, 37 + o) & c.ell(cx, 30 + o, 6.6, 8.4)
        c.paint(bp, 'pack', band(c, cx, 29 + o, 7, 8, .3, 1), part=6)
        c.paint(c.rect(12, 31 + o, 20, 36 + o) & bp, 'pack', np.where(c.ys < 32 + o, .2, .55), part=7)             # pocket
        c.paint(c.rect(cx - 1, 24 + o, cx + 1, 25 + o), 'chrome', .8, part=7, noline=True)

def back(L, f=None):
    c = Canvas(32, 58); o, ld, rd, al, ar = STEP_F[f]; o += L.get('drop', 0)
    c.cast(c.ell(16, 55.2, 8.5, 2.2), .4)
    legs_front(c, L, o, ld, rd); top_back(c, L, o); arms_front(c, L, o, al, ar, back=True); head_back(c, L, o)
    return render(c)

# ---- seated at the table: 32 x 48, the head where the standing one has it, like today's seated people ----
def seated(L, d='down'):
    L = dict(L, extras=tuple(e for e in L.get('extras', ()) if e not in ('cane', 'bag')))                       # the cane and the bag stay by the chair
    o = L.get('drop', 0); skin, shirt, pants, top, legs = L['skin'], L['shirt'], L['pants'], L['top'], L.get('legs', 'pants')
    shin = skin if legs in ('shorts', 'skirt') else pants
    if L.get('old') and legs == 'skirt': shin = 'cream'
    if d in ('down', 'up'):                                                                                     # the standing upper body, arms shorter (hands in the lap), over a lap and shins
        c = Canvas(32, 58)
        if d == 'down': top_front(c, L, o); arms_front(c, L, o, -4, -4); head(c, L, o)
        else: top_back(c, L, o); arms_front(c, L, o, -4, -4, back=True); head_back(c, L, o)
        up = render(c).crop((0, 0, 32, 35 if d == 'down' else 37))
        b = Canvas(32, 48)
        if d == 'down':
            for lx in (11, 17):
                b.paint(b.rect(lx, 36, lx + 4, 43), shin, b.cyl_x(lx, lx + 4, .3, .85), part=1)
                if legs == 'shorts': b.paint(b.rect(lx, 40, lx + 4, 43), 'white', .8, part=1)
                shoe(b, lx + 2, 43, L, 2, 3.3)
            wide = legs == 'skirt'
            lap = b.ell(16, 35 if wide else 34.5, 8.6 if wide else 7.5, 4.6 if wide else 3.6)
            lit = np.where(b.ys < 35, .85, .5)
            if top == 'granny': lit = lit * .8 + ((b.xs * 3 + b.ys * 5) % 7 == 0) * .35
            b.paint(lap, pants, np.clip(lit, 0, 1), part=3)
            if top == 'qipao': gold_dots(b, lap)
            if top == 'waiter': b.paint(lap, 'apron', lit, part=3)
        out = render(b); out.paste(up, (0, 0), up)
        return out
    c = Canvas(32, 58)                                                                                          # from the side, facing right: the arm on the table, the thigh level, the shin down
    lf, torso = side_torso(c, L, o)
    c.mat[35:, :] = None; c.part[35:, :] = 0
    c.paint(c.rect(21, 35, 25, 43), shin, c.cyl_x(21, 25, .3, .8), part=1)
    if legs == 'shorts': c.paint(c.rect(21, 40, 25, 43), 'white', .8, part=1)
    m = c.ell(25, 44.4, 4.6, 2.5) & (c.ys <= 45)
    c.paint(m, L.get('shoe', 'shoe'), band(c, 25, 43.6, 4.6, 2.5, .3, 1), part=2)
    c.paint(m & (c.ys >= 45), 'sole', 1 if L.get('shoe') in ('shoeR', 'shoeW') else 0, part=2, noline=True)
    x1 = 22 if legs == 'skirt' else 25
    thigh = c.rect(11, 30, x1, 36) | c.ell(x1 - 1, 33, 2.8, 3)
    c.paint(thigh, pants, np.where(c.ys < 32, .85, .5), part=8)
    if legs == 'shorts': c.paint(c.rect(21, 31, 25, 36) | (c.ell(24, 33, 2.8, 3) & (c.xs >= 21)), skin, np.where(c.ys < 32, .8, .55), part=8)
    if top == 'granny': c.paint(thigh, pants, np.where(c.ys < 32, .7, .45) + ((c.xs * 3 + c.ys * 5) % 7 == 0) * .35, part=8)
    if top == 'qipao': gold_dots(c, thigh)
    ay = 23 + o
    arm = (c.rect(14, ay, 25, ay + 4) | c.ell(15, ay + 2, 2.6, 2.6)) & (c.ys < 34)
    under = np.roll(arm, 1, axis=0) & ~arm & (c.mat != None)
    c.lit[under] = np.clip(c.lit[under] - .28, 0, 1)
    c.paint(arm, shirt, np.where(c.ys < ay + 2, .95, .6), part=9)
    if top in BARE: c.paint(arm & (c.xs >= 19), skin, np.where(c.ys < ay + 2, .8, .55), part=9)
    elif top in ('suit', 'tang'): c.paint(arm & (c.xs >= 24), 'white', .9, part=9)
    elif top != 'leather': c.paint(arm & (c.xs >= 23), shirt, .22, part=9)
    c.paint(c.ell(26, ay + 2, 2.3, 2.1), skin, .75, part=10)
    if 'phone' in L['extras']: c.paint(c.rect(25, ay - 4, 28, ay + 2), 'onyx', .6, part=11); c.paint(c.rect(26, ay - 3, 27, ay), 'neonC', .7, part=12, noline=True)
    c.xs = c.xs - lf; head(c, L, o, side=True); c.xs = c.xs + lf
    im = render(c).crop((0, 0, 32, 48))
    return ImageOps.mirror(im) if d == 'left' else im

def walk(L, d='down', f=None):
    """a customer on foot facing d (down, up, right, left); f None = standing, 0-3 = the four steps"""
    if d == 'down': return front(L, f)
    if d == 'up': return back(L, f)
    im = side(L, f)
    return ImageOps.mirror(im) if d == 'left' else im

# the staff, standing and facing down (the game shows them like this). The first of each list is the atlas's
# 'waiter' / 'cook'; the others are 'waiter_1', 'cook_1' ... and the game hands them out in turn
def _waiter(**k): return dict(dict(eye='irisBr', shirt='apron', pants='vest', top='waiter', style='short'), **k)
def _cook(**k): return dict(dict(eye='irisBr', shirt='apron', pants='pantsK', top='cook', style='toque'), **k)
WAITERS = [_waiter(skin='skinB', hair='hairB'),
           _waiter(skin='skinA', hair='hairY', eye='irisBl', style='long'),            # a blonde waitress
           _waiter(skin='skinA', hair='hairK', eye='irisDk'),                          # a Chinese waiter
           _waiter(skin='skinC', hair='hairK', eye='irisDk', style='afro')]
COOKS = [_cook(skin='skinA', hair='hairK', eye='irisGr'),
         _cook(skin='skinD', hair='hairB', eye='irisHz', under='long'),                # a woman, long hair under the hat
         _cook(skin='skinC', hair='hairK', eye='irisDk', extras=('moustache',)),
         _cook(skin='skinB', hair='hairK', extras=('beard',)),
         _cook(skin='skinA', hair='hairR', eye='irisGr', under='bob')]                 # a redhead with a bob
WAITER, COOK = WAITERS[0], COOKS[0]
def staff(role, i=0): return front((WAITERS if role == 'waiter' else COOKS)[i])

LOOKS = [
    dict(skin='skinA', hair='hairY', eye='irisBl', shirt='sweater', pants='denim', top='sweater', style='long', shoe='boot'),
    dict(skin='skinB', hair='hairK', eye='irisBr', shirt='hood', pants='pantsK', top='hoodie', style='short', shoe='shoeW'),
    dict(skin='skinC', hair='hairK', eye='irisDk', shirt='teeO', pants='denim', top='tee', legs='shorts', style='cap', shoe='shoeR', extras=('pack',)),
    # the old gentleman (bald, grey tufts and moustache, glasses, suit, a cane) and the old lady (a big set of
    # lilac curls, glasses, pearls, a dotted dress under a cardigan, stockings, a handbag)
    dict(skin='skinA', hair='hairG', eye='irisBl', shirt='suitN', pants='suitN', top='suit', tie='tie', style='bald', old=True, drop=2, extras=('glasses', 'moustache', 'cane')),
    dict(skin='skinA', hair='hairLilac', eye='irisGr', shirt='rose', pants='shirtP', top='granny', legs='skirt', skirt=12, style='bouffant', old=True, drop=2, extras=('glasses', 'bag')),
    dict(skin='skinA', hair='hairGreen', eye='irisBr', shirt='jacket', pants='denim', top='leather', style='mohawk', shoe='boot', drop=3, extras=('piercing',)),
    dict(skin='skinC', hair='hairB', eye='irisBr', shirt='shirtY', pants='pantsB', top='sweater', style='afro', shoe='shoeW'),
    dict(skin='skinB', hair='hairPink', eye='irisBl', shirt='rose', pants='denim', top='stripes', legs='skirt', skirt=8, style='long', shoe='shoeW', extras=('phone',)),
    # the tourist (straw hat, flowered shirt, a camera round the neck, shorts and socks) and the gourmet (a bun,
    # a black dress, pearls, red shoes)
    dict(skin='skinA', hair='hairR', eye='irisGr', shirt='hawaii', pants='pantsB', top='hawaii', legs='shorts', style='hat', shoe='bagB', extras=('camera',)),
    dict(skin='skinD', hair='hairK', eye='irisHz', shirt='dressK', pants='dressK', top='dress', legs='skirt', skirt=11, style='bun', shoe='shoeR', drop=3),
    # a Japanese tourist (white bucket hat, polo, camera), and a Chinese couple: he in a blue silk jacket with
    # knot buttons, she in a red qipao with gold flowers and two buns
    dict(skin='skinA', hair='hairK', eye='irisDk', shirt='polo', pants='pantsB', top='polo', style='bucket', shoe='shoeW', extras=('camera',)),
    dict(skin='skinA', hair='hairK', eye='irisDk', shirt='tang', pants='pantsK', top='tang', style='short', shoe='boot'),
    dict(skin='skinA', hair='hairK', eye='irisBr', shirt='qipao', pants='qipao', top='qipao', legs='skirt', skirt=13, style='buns', shoe='boot', drop=2),
    # office people (a black suit, a jacket and skirt, a brown suit with a moustache), and more of the street:
    # a redhead in green, a bearded dad, a kid with a blue quiff, a girl with a green bob, a runner
    dict(skin='skinB', hair='hairK', eye='irisBr', shirt='suitK', pants='suitK', top='suit', tie='tieB', style='short'),
    dict(skin='skinA', hair='hairR', eye='irisGr', shirt='suitN', pants='suitN', top='suit', tie=None, legs='skirt', skirt=9, style='bob', shoe='boot'),
    dict(skin='skinC', hair='hairK', eye='irisDk', shirt='suitBr', pants='suitBr', top='suit', tie='tieY', style='short', extras=('moustache',)),
    dict(skin='skinA', hair='hairR', eye='irisGr', shirt='hood', pants='denim', top='sweater', style='long', shoe='boot'),
    dict(skin='skinB', hair='hairB', eye='irisHz', shirt='denim', pants='pantsB', top='hoodie', style='short', shoe='boot', extras=('beard',)),
    dict(skin='skinD', hair='hairBlue', eye='irisHz', shirt='shirtY', pants='denim', top='tee', legs='shorts', style='quiff', shoe='shoeW', drop=3),
    dict(skin='skinB', hair='hairGreen', eye='irisGr', shirt='jacket', pants='rose', top='leather', legs='skirt', skirt=8, style='bob', shoe='boot', drop=1),
    dict(skin='skinD', hair='hairK', eye='irisDk', shirt='hawaii', pants='pantsK', top='stripes', legs='shorts', style='afro', shoe='shoeR'),
]
OLD = [0, 1, 3, 13, 14, 15, 5, 17, 16, 11, 9, 7, 8, 10, 11, 12, 4, 2, 19, 20, 6]     # today's looks closest to each pilot look

if __name__ == '__main__':
    OUT = _out + '/'; os.makedirs(OUT, exist_ok=True)
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
    K = 5; n = len(LOOKS); BG = (206, 178, 136)
    W = n * 34 * K + 190
    sheet = Image.new('RGB', (W, 6 * 62 * K + 20), BG); dr = ImageDraw.Draw(sheet)
    def put(im, col, row):
        b = im.resize((im.width * K, im.height * K), Image.NEAREST); sheet.paste(b, (180 + col * 34 * K, 10 + row * 62 * K), b)
    for row, t in enumerate(['TODAY', 'PILOT', 'TODAY  side', 'PILOT  side', 'TODAY  back', 'PILOT  back']): dr.text((14, 10 + row * 62 * K + 130), t, fill=(60, 30, 10), font=fs)
    for i, L in enumerate(LOOKS):
        put(G.walker('down', G.LOOKS[OLD[i]], 0).image(), i, 0); put(front(L), i, 1)
        put(G.walker('right', G.LOOKS[OLD[i]], 1).image(), i, 2); put(side(L, 0), i, 3)
        put(G.walker('up', G.LOOKS[OLD[i]], 0).image(), i, 4); put(back(L), i, 5)
    sheet.save(OUT + 'pilot_people.png')
    # seated: today against the pilot, facing down, right and up; then the waiter and the cook
    K = 5; sheet = Image.new('RGB', (W, 6 * 52 * K + 62 * K + 30), BG); dr = ImageDraw.Draw(sheet)
    def put2(im, col, y):
        b = im.resize((im.width * K, im.height * K), Image.NEAREST); sheet.paste(b, (180 + col * 34 * K, y), b)
    for row, t in enumerate(['TODAY', 'PILOT', 'TODAY  side', 'PILOT  side', 'TODAY  back', 'PILOT  back']): dr.text((14, 10 + row * 52 * K + 110), t, fill=(60, 30, 10), font=fs)
    for i, L in enumerate(LOOKS):
        for k, d in enumerate(('down', 'right', 'up')):
            put2(G.person(d, G.LOOKS[OLD[i]]).image(), i, 10 + k * 2 * 52 * K); put2(seated(L, d), i, 10 + (k * 2 + 1) * 52 * K)
    y = 20 + 6 * 52 * K; dr.text((14, y + 130), 'STAFF', fill=(60, 30, 10), font=fs)
    put2(G.standing('waiter', 'skinB', 'hairB', 'irisBr').image(), 0, y); put2(staff('waiter'), 1, y)
    put2(G.standing('cook', 'skinA', 'hairK', 'irisGr').image(), 3, y); put2(staff('cook'), 4, y)
    sheet.save(OUT + 'pilot_seated.png')
    # the walk, old (2 steps) against the pilot (4 steps), at the game's size x3; the last row is the pilot from behind
    K = 3; frames = []
    for t in range(8):
        fr = Image.new('RGB', (n * 34 * K + 16, 5 * 62 * K + 16), BG)
        for i, L in enumerate(LOOKS):
            for r, im in enumerate([G.walker('down', G.LOOKS[OLD[i]], (t // 2) % 2).image(), front(L, t % 4), G.walker('right', G.LOOKS[OLD[i]], (t // 2) % 2).image(), side(L, t % 4), back(L, t % 4)]):
                b = im.resize((im.width * K, im.height * K), Image.NEAREST); fr.paste(b, (8 + i * 34 * K, 8 + r * 62 * K), b)
        frames.append(fr)
    frames[0].save(OUT + 'pilot_walk.gif', save_all=True, append_images=frames[1:], duration=140, loop=0)
    print('ok')
