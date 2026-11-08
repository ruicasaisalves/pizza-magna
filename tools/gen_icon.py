#!/usr/bin/env python3
"""Pizza Magna: the game's icon, a pizza slice, in two drawings.

- Big (app icons, 180 to 512 px): a slice cut from a real game pizza, built from the game's own
  sprites (Napolitana crust, tomato sauce, grated mozzarella, pepperoni, basil), with a dark
  outline, on a wood background. 512 px is drawn at a whole-number scale; the smaller app
  icons are shrunk from it.
- Small (32 px: browser tab and the header button where you change the names): the same slice
  drawn pixel by pixel, because shrinking the big one would turn it to mush.

Writes assets/icon-32.png, icon-180.png, icon-192.png, icon-512.png.
Usage: python3 tools/gen_icon.py [preview_folder]"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
PREVIEW = sys.argv[1] if len(sys.argv) > 1 else None
sys.argv = sys.argv[:1] + [os.path.join(ROOT, 'preview')]       # the generators read the output folder from argv
sys.path.insert(0, HERE)
import build_atlas as BA
import gen_ingredients2 as G2, gen_ingredients3 as G3, gen_ingredients18 as G18
from gen_ingredients import R, hexs

OUTLINE = (42, 20, 7)            # --wood-deep
WOOD = [(74, 38, 15), (122, 69, 32)]   # --wood-lo .. --wood (background)
D = 170; C = D / 2
A0, A1 = np.radians(-78), np.radians(-12)      # the slice: tip at the centre, crust towards the top right

def in_slice(x, y, r_max=C - 1):
    a = np.arctan2(y - C, x - C); r = np.hypot(x - C, y - C)
    return (a >= A0) & (a <= A1) & (r <= r_max)

def game_pizza():
    """a pizza as the game draws it: sauce, toppings in order, crust ring on top"""
    b = BA.bases()
    pz = Image.new('RGBA', (D, D), (0, 0, 0, 0))
    pz.alpha_composite(b['sauce_tomate'])
    rng = np.random.default_rng(7)
    for k in range(26):                                        # grated mozzarella all over, like a player would
        a, r = k * 2.4, np.sqrt((k + .5) / 26) * 66
        h = G18.mozz_layer(41 + k % 3 * 17)
        pz.alpha_composite(h, (int(C + np.cos(a) * r - h.width / 2), int(C + np.sin(a) * r - h.height / 2)))
    mid = (A0 + A1) / 2
    def put(img, a, r):                                        # a piece at angle a, radius r from the centre
        pz.alpha_composite(img, (int(C + np.cos(a) * r - img.width / 2), int(C + np.sin(a) * r - img.height / 2)))
    for a, r, s in ((mid - .3, 58, 1), (mid + .28, 52, 2), (mid - .05, 33, 3), (mid + .2, 20, 1)):   # pepperoni
        put(BA.drop(G2.pepperoni(s)), a, r)
    for a, r, s in ((mid + .05, 66, 1), (mid - .32, 40, 2), (mid + .36, 34, 3)):                       # basil
        put(BA.drop(G3.basil(s)), a, r)
    pz.alpha_composite(b['crust_napo'])
    return pz

def big_slice():
    pz = np.array(game_pizza())
    ys, xs = np.mgrid[0:D, 0:D]
    keep = in_slice(xs + .5, ys + .5)
    pz[~keep] = 0
    tip = Image.fromarray(pz).copy()
    a = np.array(tip)
    m = a[:, :, 3] > 0
    ring = np.zeros_like(m)                                     # 2 px dark outline
    for dy in (-2, -1, 0, 1, 2):
        for dx in (-2, -1, 0, 1, 2):
            if abs(dx) + abs(dy) <= 3: ring |= np.roll(np.roll(m, dy, 0), dx, 1)
    out = np.zeros_like(a); out[ring & ~m] = OUTLINE + (255,); out[m] = a[m]
    img = Image.fromarray(out)
    return img.crop(img.getbbox())

def app_icon(sl, N):
    """the big slice on a wood square, scaled by a whole number and centred (inside the safe zone)"""
    k = max(1, int(N * .78 / max(sl.size)))
    s = sl.resize((sl.width * k, sl.height * k), Image.NEAREST)
    yy, xx = np.mgrid[0:N, 0:N]
    t = np.clip(np.hypot(xx - N * .45, yy - N * .4) / (N * .75), 0, 1)[..., None]
    bg = (np.array(WOOD[1]) * (1 - t) + np.array(WOOD[0]) * t).astype(np.uint8)
    img = Image.fromarray(np.dstack([bg, np.full((N, N), 255, np.uint8)]), 'RGBA')
    img.alpha_composite(s, ((N - s.width) // 2, (N - s.height) // 2 + N // 40))
    return img

def small_icon():
    """32x32, drawn pixel by pixel: a slice lying on the diagonal (tip bottom left, crust top
    right) that fills the square, cream cheese, three pepperoni, three basil leaves, dark outline, transparent background"""
    N = 32
    crust = hexs(['#8a4a12', '#b8691e', '#d89238', '#f0b860'])
    cheese = hexs(['#e8c070', '#f6dc96', '#fff2c8', '#fffbea'])
    pep = hexs(['#6e0e0c', '#a8201a', '#d8402e', '#f07050'])
    basil = hexs(['#1e5a1a', '#3a8a2a', '#5aae3a'])
    img = Image.new('RGBA', (N, N), (0, 0, 0, 0)); px = img.load()
    tx, ty, R0 = 4, 28, 28.5                                  # the tip, bottom left; the crust reaches the top right
    a0, a1 = np.radians(-45 - 25), np.radians(-45 + 25)
    rng = np.random.default_rng(3)
    speck = rng.random((N, N))
    inside = np.zeros((N, N), bool)
    for y in range(N):
        for x in range(N):
            a = np.arctan2(y + .5 - ty, x + .5 - tx); r = np.hypot(x + .5 - tx, y + .5 - ty)
            if not (a0 <= a <= a1 and r <= R0): continue
            inside[y, x] = True
            if r > R0 - 4.5:                                  # crust, lighter on its outer, upper side
                px[x, y] = crust[3 if r > R0 - 1.5 and a < -.75 else 2 if r > R0 - 3 else 1] + (255,)
            else:
                px[x, y] = cheese[int(np.clip(1.2 + r * .04 + (a < -.8) * .6 + (speck[y, x] > .82) - (speck[y, x] < .1), 0, 3))] + (255,)
    for cx, cy in ((11, 20), (19, 16), (14, 11)):              # pepperoni: 5x5 discs, lit top left
        for y in range(cy - 2, cy + 3):
            for x in range(cx - 2, cx + 3):
                d = (x - cx) ** 2 + (y - cy) ** 2
                if inside[y, x] and d <= 5:
                    px[x, y] = pep[3 if (x - cx, y - cy) == (-1, -1) else 2 if x - cx + y - cy < 0 else 1 if d < 4 else 0] + (255,)
    for pts in (((16, 21), (17, 21), (17, 20), (18, 20)), ((20, 9), (21, 9), (21, 8), (22, 8)), ((9, 15), (10, 15), (10, 14), (11, 14))):   # basil leaves
        for k, (x, y) in enumerate(pts):
            if inside[y, x]: px[x, y] = basil[(0, 1, 1, 2)[k]] + (255,)
    a = np.array(img); m = a[:, :, 3] > 0                      # 1 px dark outline
    ring = np.zeros_like(m)
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)): ring |= np.roll(np.roll(m, dy, 0), dx, 1)
    a[ring & ~m] = OUTLINE + (255,)
    return Image.fromarray(a)

if __name__ == '__main__':
    sl = big_slice()
    out = os.path.join(ROOT, 'assets')
    small = small_icon(); small.save(os.path.join(out, 'icon-32.png'))
    big = app_icon(sl, 512); big.save(os.path.join(out, 'icon-512.png'))
    for N in (180, 192): big.resize((N, N), Image.LANCZOS).save(os.path.join(out, f'icon-{N}.png'))
    if PREVIEW:
        os.makedirs(PREVIEW, exist_ok=True)
        sheet = Image.new('RGB', (1100, 560), (230, 230, 230))
        sheet.paste(app_icon(sl, 512), (20, 20))
        sheet.paste(big.resize((180, 180), Image.LANCZOS), (560, 20))
        s8 = small.resize((256, 256), Image.NEAREST); sheet.paste(s8, (760, 20), s8)
        for i, z in enumerate((1, 2)):                         # the small one at real sizes, on light and dark
            sz = small.resize((32 * z, 32 * z), Image.NEAREST)
            sheet.paste(sz, (560 + i * 80, 260), sz)
            dark = Image.new('RGB', (32 * z + 16, 32 * z + 16), (42, 20, 7)); dark.paste(sz, (8, 8), sz); sheet.paste(dark, (760 + i * 90, 300))
        sheet.save(os.path.join(PREVIEW, 'icons.png')); print('ok')
