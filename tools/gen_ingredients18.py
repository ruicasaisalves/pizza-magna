#!/usr/bin/env python3
"""Pizza Magna: eighteenth batch, a redraw. Grated mozzarella as a thick white layer.

The old handful was loose beige strands with sauce showing between them, so a pizza
covered in mozzarella still looked red and stripy. Now each handful is a dense pile
of white strands on a white bed (the strands show, the sauce doesn't), with strands
poking out a little at the edge: handfuls side by side make an even white surface, good to draw on
(a heart of ham, a face...). It lies flat, so the atlas gives it no drop shadow
(NO_DROP in build_atlas.py). Same method as gen_ingredients.py (see tools/CLAUDE.md).
Usage: python3 tools/gen_ingredients18.py <folder>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from gen_ingredients import R, hexs, render, shade, noise

OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'preview')) + '/'

R.update({
    'mozzw': hexs(['#b8ad94', '#ddd6c4', '#efebe0', '#f9f7f1', '#ffffff']),     # melted fresh mozzarella, near white
    'mozzsh': hexs(['#a89a7c', '#c9bea6']),                                      # strand shadows: past the edge / on the bed
})

def mozz_layer(seed, W=60, H=56):
    """a dense pile of grated strands on a white bed: the strands show (light top, thin shadow),
    the sauce doesn't show through, and the edge is strands poking out a little, not loose bits"""
    rng = np.random.default_rng(seed + 5500)
    ys, xs = np.mgrid[0:H, 0:W]
    cx, cy = (W - 1) / 2, (H - 1) / 2
    # the bed: a few overlapping round lumps, with a ragged edge
    blob = np.zeros((H, W))
    for _ in range(8):
        a, d = rng.random() * 6.28, rng.random() * 8
        r = rng.uniform(10, 13)
        bx, by = cx + np.cos(a) * d, cy + np.sin(a) * d * .9
        blob = np.maximum(blob, 1 - np.hypot(xs - bx, ys - by) / r)
    n = noise(H, W, 4, rng)
    bed = (blob > .05) & (blob + (n - .5) * .3 > .14)        # no islands away from the handful
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); px = img.load()
    ramp = R['mozzw']
    for y in range(H):                                       # the bed itself is in shade: it is what lies under the strands
        for x in range(W):
            if bed[y, x]: px[x, y] = R['mozzsh'][1] + (255,)
    # strands: many short ones, each lit on top with a 1 px shadow under it; later ones lie on earlier ones
    near = np.argwhere(bed)
    for k in range(300):
        y0, x0 = near[rng.integers(len(near))] + rng.uniform(-.5, .5, 2)
        L, ang = int(rng.integers(4, 8)), rng.random() * 3.14
        pts = [(int(round(x0 + np.cos(ang) * t)), int(round(y0 + np.sin(ang) * t * .7))) for t in range(L)]
        for x, y in pts:                                     # shadow first (may hang just past the bed)
            if 0 <= x < W and 0 <= y + 1 < H: px[x, y + 1] = R['mozzsh'][0 if not bed[min(H - 1, y + 1), x] else 1] + (255,)
        for t, (x, y) in enumerate(pts):
            if 0 <= x < W and 0 <= y < H:
                px[x, y] = ramp[4 if t in (1, 2) else 3] + (255,)          # bright in the middle of the strand
    # round off the edge: a lone pixel sticking out on its own is dropped
    a = np.array(img)[:, :, 3] > 0
    for y in range(H):
        for x in range(W):
            if a[y, x] and not bed[y, x]:
                nb = sum(a[y + dy, x + dx] for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= y + dy < H and 0 <= x + dx < W)
                if nb == 0: px[x, y] = (0, 0, 0, 0)
    return img

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
