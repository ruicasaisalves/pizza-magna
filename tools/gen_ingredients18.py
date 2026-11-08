#!/usr/bin/env python3
"""Pizza Magna: eighteenth batch, a redraw. Grated mozzarella as a thick white layer.

The old handful was loose beige strands with sauce showing between them, so a pizza
covered in mozzarella still looked red and stripy. Now each handful is an opaque,
melted-looking white patch with a grated texture on top and a few loose strands at
the edge: handfuls side by side make an even white surface, good to draw on
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
    'mozzedge': hexs(['#d6cebb', '#e8e3d6']),                                    # soft edge: handfuls side by side melt into one layer
})

def mozz_layer(seed, W=60, H=56):
    rng = np.random.default_rng(seed + 5500)
    ys, xs = np.mgrid[0:H, 0:W]
    cx, cy = (W - 1) / 2, (H - 1) / 2
    # body: a few overlapping round lumps, with a ragged edge
    blob = np.zeros((H, W))
    for _ in range(8):
        a, d = rng.random() * 6.28, rng.random() * 9
        r = rng.uniform(10, 14)
        bx, by = cx + np.cos(a) * d, cy + np.sin(a) * d * .9
        blob = np.maximum(blob, 1 - np.hypot(xs - bx, ys - by) / r)
    n = noise(H, W, 4, rng)
    mask = blob + (n - .5) * .35 > .12
    # height: soft melted bumps plus a fine grated grain
    grain = noise(H, W, 2, rng)
    height = np.clip(blob, 0, 1) * 3 + (n - .5) * 1.5 + (grain - .5) * .9
    light = np.clip(shade(height, mask) * .55 + .45, 0, 1) * mask
    mat = [['mozzw'] * W for _ in range(H)]
    img = render(mat, light, mask, {'mozzw': 'mozzedge'})
    px = img.load()
    ramp = R['mozzw']
    # grated texture: short strands, a light top and a soft shadow under each
    for _ in range(90):
        x0, y0 = rng.uniform(0, W), rng.uniform(0, H)
        if not mask[int(y0), int(x0)]: continue
        L, ang = int(rng.integers(3, 6)), rng.random() * 3.14
        pts = [(int(round(x0 + np.cos(ang) * t)), int(round(y0 + np.sin(ang) * t * .7))) for t in range(L)]
        for x, y in pts:
            if 0 <= x < W and 0 <= y + 1 < H and mask[y + 1, x]: px[x, y + 1] = ramp[1] + (255,)
        for x, y in pts:
            if 0 <= x < W and 0 <= y < H and mask[y, x]: px[x, y] = ramp[4 if rng.random() < .6 else 3] + (255,)
    # loose strands just past the edge, so the handful doesn't end in a hard line
    for _ in range(22):
        a = rng.random() * 6.28
        r = rng.uniform(15, 21)
        x0, y0 = cx + np.cos(a) * r, cy + np.sin(a) * r * .92
        L, ang = int(rng.integers(3, 6)), rng.random() * 3.14
        pts = [(int(round(x0 + np.cos(ang) * t)), int(round(y0 + np.sin(ang) * t * .7))) for t in range(L)]
        for x, y in pts:
            if 0 <= x < W and 0 <= y + 1 < H and px[x, y + 1][3] == 0: px[x, y + 1] = R['mozzedge'][0] + (255,)
        for i, (x, y) in enumerate(pts):
            if 0 <= x < W and 0 <= y < H: px[x, y] = ramp[2 + (i == 1) + int(rng.random() * 2)] + (255,)
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
