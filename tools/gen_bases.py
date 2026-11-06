#!/usr/bin/env python3
"""Pizza Magna: new doughs and sauces. Each dough is a crust ring and each sauce a disc,
both at pizza scale (170 px); the game lays the sauce, the pieces and the crust on top.
Same method as gen_ingredients4.base() (light from the top left, short ramps, 4x4 dithering).

Doughs: wholemeal, gluten-free, slow-rise, stuffed crust.
Sauces: barbecue, arrabbiata, olive oil & garlic, truffle, roasted peppers.
Usage: python3 tools/gen_bases.py <folder>   (makes the preview sheet)"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from gen_ingredients import hexs, noise, quant

OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'preview')) + '/'

CRUST = hexs(['#7a4214', '#a8642a', '#cf8a42', '#e9ad62', '#f8cf8e'])

# game id -> (crust width, ramp, relief)
DOUGHS = {
    'integral':   (.13, hexs(['#4e2a0e', '#74431c', '#98602c', '#b87e44', '#d29e62']), 1.0),
    'sem_gluten': (.08, hexs(['#a08458', '#c2a474', '#dabe90', '#ecd6ae', '#f8eacc']), .55),
    'lenta':      (.16, CRUST, 1.25),
    'recheado':   (.21, CRUST, 1.1),
}
SAUCES = {
    'barbecue':    hexs(['#2a0a04', '#481608', '#682410', '#88381c']),
    'arrabbiata':  hexs(['#6e140a', '#962010', '#ba2e18', '#d64424']),
    'azeite_alho': hexs(['#c08a46', '#d6a45e', '#e8bc7a', '#f4d294']),
    'trufa':       hexs(['#9a9080', '#bab09e', '#d4ccba', '#e8e2d4']),
    'pimentos':    hexs(['#86280a', '#b2421a', '#d4602a', '#ea8442']),
}

def crust(D, kind, seed=0):
    """crust ring: the relief rises and falls across its width, light from the top left"""
    rng = np.random.default_rng(seed + 300)
    w, ramp, relief = DOUGHS[kind]
    img = Image.new('RGBA', (D, D), (0, 0, 0, 0)); px = img.load()
    c = (D - 1) / 2
    n = noise(D, D, 5, rng); n2 = noise(D, D, 2, rng); n4 = noise(D, D, 4, rng); fine = rng.random((D, D))
    cheese = hexs(['#d8a01c', '#f0c032', '#ffdc5a', '#fff09a'])
    for y in range(D):
        for x in range(D):
            dx, dy = x - c, y - c; r = np.hypot(dx, dy) / (D / 2 - .5)
            if r > 1 or r <= 1 - w: continue
            t = (r - (1 - w)) / w
            lit = np.sqrt(max(0, 1 - (2 * t - 1) ** 2)) * (.45 + w * 2) * relief + (-dx - dy) / D * .7 + .2 + (n[y, x] - .5) * .45
            col = quant(np.clip(lit, 0, 1), ramp, y, x)
            if kind == 'integral' and fine[y, x] > .9:                  # bran: dark and light specks
                col = ramp[0] if fine[y, x] > .95 else ramp[4]
            elif kind == 'sem_gluten':
                if n2[y, x] > .9 and .3 < t < .8: col = ramp[1]           # fine cracks, crumbly dough
            elif kind == 'lenta':
                if n4[y, x] > .8 and t > .15: col = hexs(['#2a1408'])[0]   # leopard spots from the oven
                elif n4[y, x] > .72 and t > .15: col = ramp[0]
            elif kind == 'recheado':
                ang = np.arctan2(dy, dx)
                gap = np.sin(ang * 14 + seed) > .55                       # openings where the cheese comes out
                if gap and .18 < t < .58:
                    col = quant(np.clip(.6 + (-dx - dy) / D * .4, 0, 1), cheese, y, x)
            elif n2[y, x] > .93:
                col = ramp[1]
            px[x, y] = col + (255,)
    return img

def sauce(D, kind, seed=0):
    """sauce disc; its edge sits under the dough ring"""
    rng = np.random.default_rng(seed + 400)
    ramp = SAUCES[kind]
    img = Image.new('RGBA', (D, D), (0, 0, 0, 0)); px = img.load()
    c = (D - 1) / 2
    n = noise(D, D, 5, rng); n2 = noise(D, D, 2, rng); n6 = noise(D, D, 7, rng); fine = rng.random((D, D))
    for y in range(D):
        for x in range(D):
            dx, dy = x - c, y - c; r = np.hypot(dx, dy) / (D / 2 - .5)
            if r > .95: continue
            lit = .5 + (-dx - dy) / D * .25 + (n[y, x] - .5) * .5
            if kind == 'barbecue':
                lit += np.sin((dx + dy * .4) * .35 + n[y, x] * 6) * .18       # shiny spoon drags
            col = quant(np.clip(lit, 0, 1), ramp, y, x)
            if kind == 'arrabbiata' and fine[y, x] > .975:                    # chilli flakes
                col = hexs(['#ff6a2a', '#5a0a04'])[int(fine[y, x] > .99)]
            elif kind == 'azeite_alho':
                if n6[y, x] > .66: col = quant(np.clip(lit + .1, 0, 1), hexs(['#8a8a22', '#b4ac34', '#d6cc56', '#efe486']), y, x)   # pools of olive oil
                if fine[y, x] > .985: col = hexs(['#fffbea'])[0]               # garlic slivers
            elif kind == 'trufa' and fine[y, x] > .97:
                col = hexs(['#1a120c', '#3a2a1e'])[int(fine[y, x] > .985)]    # black truffle specks
            elif kind == 'pimentos' and n6[y, x] > .74:
                col = quant(np.clip(lit - .35, 0, 1), hexs(['#3a1206', '#5e1e0a', '#82300e']), y, x)   # toasted patches
            px[x, y] = col + (255,)
    return img

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    D = 170
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    sheet = Image.new('RGB', (5 * 190 + 20, 2 * 220 + 40), (27, 20, 16)); dr = ImageDraw.Draw(sheet)
    dr.text((20, 8), 'Doughs (on the preview tomato sauce)', fill=(240, 220, 180), font=fs)
    tom = Image.new('RGBA', (D, D), (0, 0, 0, 0)); dt = ImageDraw.Draw(tom); dt.ellipse((6, 6, D - 7, D - 7), fill=(196, 52, 28, 255))
    for i, k in enumerate(DOUGHS):
        im = tom.copy(); im.alpha_composite(crust(D, k, i)); sheet.paste(im, (20 + i * 190, 30), im)
        dr.text((20 + i * 190, 205), k, fill=(240, 220, 180), font=fs)
    dr.text((20, 232), 'Sauces (with a thin crust)', fill=(240, 220, 180), font=fs)
    for i, k in enumerate(SAUCES):
        im = sauce(D, k, i); im.alpha_composite(crust(D, 'sem_gluten', 9)); sheet.paste(im, (20 + i * 190, 254), im)
        dr.text((20 + i * 190, 430), k, fill=(240, 220, 180), font=fs)
    sheet.save(OUT + 'preview_bases.png'); print('ok', sheet.size)
