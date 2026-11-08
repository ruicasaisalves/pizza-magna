#!/usr/bin/env python3
"""Pizza Magna: eighteenth batch, a redraw. Whiter grated mozzarella.

The handful keeps the original loose strands (grated() 'shred', 60x56), but the
strands are near white with a soft grey shadow instead of beige with a brown one,
and there are more of them (250 instead of 130). Handfuls piled together make a
white layer to draw on (a heart of ham...). It lies flat, so the atlas gives it no
drop shadow (NO_DROP in build_atlas.py). Same method as gen_ingredients.py.
Usage: python3 tools/gen_ingredients18.py <folder>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from gen_ingredients import R, hexs, render, shade, noise

OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'preview')) + '/'

R.update({
    'mozzw': hexs(['#c4b9a2', '#e2dccd', '#f4f1e9', '#fcfbf7', '#ffffff']),     # [0] the soft shadow under a strand, then near-white strands
})

def mozz_layer(seed, W=60, H=56):
    """the original grated handful (loose strands, same shape and size), but white strands with
    soft grey shadows and more of them, so handfuls piled together make a white layer"""
    from gen_ingredients2 import grated
    return grated('mozzw', seed, 'shred', W=W, H=H, n_bits=250)

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    from build_atlas import drop
    sys.path.insert(0, os.path.dirname(__file__))
    import gen_ingredients2 as G2
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    sheet = Image.new('RGB', (1000, 640), (27, 20, 16)); dr = ImageDraw.Draw(sheet)
    dr.text((20, 10), 'Old handful / new handfuls (3 variants) / a pizza covered with 22 new handfuls', fill=(240, 220, 180), font=fs)
    arr = [drop(G2.grated('mozz', 41, 'shred', n_bits=130, W=60, H=56))] + [mozz_layer(s) for s in (41, 58, 75)]
    x = 20
    for d in arr:
        m = d.resize((d.width * 3, d.height * 3), Image.NEAREST)
        bg = Image.new('RGB', (230, 190), (196, 52, 28)); bg.paste(m, ((230 - m.width) // 2, (190 - m.height) // 2), m)
        sheet.paste(bg, (x, 36)); x += 240
    # a pizza: sauce disc with handfuls on a loose grid, as a player would tap them
    D = 170; pz = Image.new('RGBA', (D, D), (0, 0, 0, 0)); dp = ImageDraw.Draw(pz)
    dp.ellipse((0, 0, D - 1, D - 1), fill=(214, 168, 100)); dp.ellipse((10, 10, D - 11, D - 11), fill=(196, 52, 28))
    rng = np.random.default_rng(3)
    for k in range(22):
        a, r = k * 2.4, np.sqrt((k + .5) / 22) * 58
        h = mozz_layer(41 + k % 3 * 17)
        pz.alpha_composite(h, (int(D / 2 + np.cos(a) * r - h.width / 2), int(D / 2 + np.sin(a) * r - h.height / 2)))
    ring = Image.new('RGBA', (D, D), (0, 0, 0, 0)); dg = ImageDraw.Draw(ring)
    dg.ellipse((0, 0, D - 1, D - 1), fill=(214, 168, 100, 255)); dg.ellipse((9, 9, D - 10, D - 10), fill=(0, 0, 0, 0))
    pz.alpha_composite(ring)
    sheet.paste(pz.resize((D * 2, D * 2), Image.NEAREST), (20, 250), pz.resize((D * 2, D * 2), Image.NEAREST))
    sheet.save(OUT + 'preview_ingredientes18.png'); print('ok', sheet.size)
