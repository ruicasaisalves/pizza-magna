#!/usr/bin/env python3
"""Pizza Magna — terceiro lote em pixel detalhado: azeitonas, cebola, pimento,
manjericão, ananás e presunto, com a forma picada pela regra de docs/ingredients.md.
Uso: python3 tools/gen_ingredients3.py <pasta>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from gen_ingredients import R, hexs, noise, shade, render, drop, pizza_base, marble
from gen_ingredients2 import grated, grid
import gen_ingredients as G

OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'preview')) + '/'
os.makedirs(OUT, exist_ok=True)

R.update({
    'olive': hexs(['#0e0b10', '#1f1a22', '#332b36', '#4c4250', '#706476']),
    'onion': hexs(['#6a3a74', '#9a62a4', '#c79ccc', '#e8d4ea', '#fbf4fb']),
    'pepper': hexs(['#123e16', '#1f6324', '#2f8a34', '#4fae4a', '#86d26e']),
    'basil': hexs(['#0f3a14', '#1a5a20', '#28802c', '#46a23e', '#7cc65e']),
    'vein': hexs(['#123e16', '#3a8a34', '#7cc65e']),
    'pine': hexs(['#8a5a0e', '#c48a14', '#e8b42a', '#f8d454', '#fff094']),
    'pinecore': hexs(['#c4961c', '#e8c450', '#fbe68c']),
    'pros': hexs(['#5a141c', '#86222a', '#ad3a3e', '#cf5e5a', '#e88a80']),
    'prosfat': hexs(['#d8c0b0', '#efe0d4', '#fff8f0']),
})

def olive(seed, D=16):
    ys, xs, c, _ = grid(D, D)
    sq = [1, .86, 1.1][seed % 3]
    r = np.hypot((xs - c) * sq, (ys - c) / sq) / (D / 2 - .3 - (seed % 2))
    mask = (r <= 1) & (r >= .38)
    height = np.clip(1 - ((r - .7) / .32) ** 2, 0, 1) * 1.8
    mat = [['olive'] * D for _ in range(D)]
    img = render(mat, np.clip(shade(height, mask) + .1, 0, 1) * mask, mask, {})
    px = img.load()
    for (x, y) in [(4, 5), (5, 4), (4, 4)]: px[x, y] = R['olive'][4] + (255,)
    return img

def onion(seed, D=24):
    rng = np.random.default_rng(seed + 800)
    ys, xs, c, _ = grid(D, D)
    r = np.hypot(xs - c, ys - c); ang = np.arctan2(ys - c, xs - c)
    a0 = rng.random() * 6.28
    mask = np.zeros((D, D), bool); height = np.zeros((D, D))
    for rr, span in ((10.5, 4.6), (7.5, 3.6), (4.6, 2.6)):        # anéis concêntricos, em arco
        da = np.angle(np.exp(1j * (ang - a0 - rng.random() * .6)))
        m = (np.abs(r - rr) <= 1.1) & (np.abs(da) <= span / 2)
        mask |= m; height = np.maximum(height, np.where(m, 1.4 - np.abs(r - rr), 0))
    mat = [['onion'] * D for _ in range(D)]
    return render(mat, np.clip(shade(height, mask) * .7 + .3, 0, 1) * mask, mask, {})

def pepper(seed, W=24, H=18):
    rng = np.random.default_rng(seed + 900)
    ys, xs, cx, cy = grid(W, H)
    R0, a0 = 15 + rng.random() * 4, rng.random() * .8 - .4
    ox, oy = cx + np.cos(a0 + 1.57) * R0 * .1, cy + R0 * .72
    r = np.hypot(xs - ox, ys - oy); ang = np.arctan2(ys - oy, xs - ox) + 1.57
    mask = (np.abs(r - R0) <= 2.2) & (np.abs(ang - a0) <= .62)
    height = np.clip(1 - ((r - R0) / 2.2) ** 2, 0, 1) * 1.8
    mat = [['pepper'] * W for _ in range(H)]
    return render(mat, np.clip(shade(height, mask) * .9 + .15, 0, 1) * mask, mask, {})

def basil(seed, W=22, H=16):
    rng = np.random.default_rng(seed + 1000)
    ys, xs, cx, cy = grid(W, H)
    a = (rng.random() - .5) * 1.4
    u = (xs - cx) * np.cos(a) + (ys - cy) * np.sin(a); v = -(xs - cx) * np.sin(a) + (ys - cy) * np.cos(a)
    t = (u + 9.5) / 19
    halfw = np.sin(np.clip(t, 0, 1) * np.pi) ** .8 * 5.4
    mask = (t >= 0) & (t <= 1) & (np.abs(v) <= halfw)
    height = np.clip(1 - (v / (halfw + .01)) ** 2, 0, 1) * 1.6 + np.abs(v) * .12
    mat = [['vein' if (abs(v[y, x]) < .6 and .08 < t[y, x] < .92) else 'basil' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .8 + .2, 0, 1) * mask, mask, {'vein': 'basil'})

def pineapple(seed, W=26, H=24):
    rng = np.random.default_rng(seed + 1100)
    ys, xs, cx, cy = grid(W, H)
    a = rng.random() * 6.28
    u = (xs - cx) * np.cos(a) + (ys - cy) * np.sin(a); v = -(xs - cx) * np.sin(a) + (ys - cy) * np.cos(a)
    mask = (v >= -8) & (v <= 8) & (np.abs(u) <= (v + 8) * .6 + 1.4)     # cunha
    n = noise(H, W, 2, rng)
    height = 1.6 - (v + 6) * .08 + np.sin(u * 1.6 + n * 2) * .25            # fibras
    mat = [['pinecore' if (mask[y, x] and v[y, x] < -5) else 'pine' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .8 + .22, 0, 1) * mask, mask, {'pinecore': 'pine'})

def presunto(seed, W=28, H=20):
    rng = np.random.default_rng(seed + 1200)
    ys, xs, cx, cy = grid(W, H)
    a = (rng.random() - .5) * 1.0; ph = rng.random() * 6.28
    u = (xs - cx) * np.cos(a) + (ys - cy) * np.sin(a); v = -(xs - cx) * np.sin(a) + (ys - cy) * np.cos(a)
    vv = v - 1.0 * np.sin(u * .3 + ph)                                       # fatia larga, levemente dobrada
    half = 6.2 + .6 * np.sin(u * .5 + ph)
    mask = (np.abs(vv) <= half) & (np.abs(u) <= 12.5)
    n = noise(H, W, 3, rng)
    height = .9 * np.cos(u * .3 + ph) + np.clip(1 - (vv / half) ** 2, 0, 1) * 1.2 + (n - .5) * .5
    streak = np.abs(np.sin(u * .55 + vv * .9 + n * 2)) < .14   # veios de gordura
    mat = [['prosfat' if (mask[y, x] and (vv[y, x] < -half[y, x] + 1.6 or streak[y, x])) else 'pros' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .85 + .18, 0, 1) * mask, mask, {'prosfat': 'pros'})

if __name__ == '__main__':
    sets = [
        ('Azeitonas', [olive(s) for s in (1, 2, 3)], grated('olive', 11, 'flake', n_bits=40)),
        ('Cebola', [onion(s) for s in (1, 2, 3)], grated('onion', 12, 'flake', n_bits=44)),
        ('Pimento', [pepper(s) for s in (1, 2, 3)], grated('pepper', 13, 'flake', n_bits=40)),
        ('Manjericão', [basil(s) for s in (1, 2, 3)], grated('basil', 14, 'flake', n_bits=46)),
        ('Ananás', [pineapple(s) for s in (1, 2, 3)], grated('pine', 15, 'cube', n_bits=11)),
        ('Presunto', [presunto(s) for s in (1, 2, 3)], grated('pros', 16, 'chunk', n_bits=9)),
    ]
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 18)
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    K, ROW = 6, 150
    sheet = Image.new('RGB', (1000, 40 + ROW * len(sets) + 40 + 600 + 20), (27, 20, 16))
    dr = ImageDraw.Draw(sheet)
    dr.text((20, 10), 'Inteiro / fatiado (×6, 3 variantes)', fill=(240, 220, 180), font=fs)
    dr.text((760, 10), 'Ralado / picado (×6)', fill=(240, 220, 180), font=fs)
    for i, (name, arr, gr) in enumerate(sets):
        for j, im in enumerate(arr): im.save(f'{OUT}{name.lower()}_{j + 1}.png')
        gr.save(f'{OUT}{name.lower()}_picado.png')
        y = 36 + i * ROW
        dr.text((20, y + 4), name, fill=(240, 220, 180), font=f)
        x = 150
        for im in arr + [gr]:
            if im is gr: x = 760
            m = im.resize((im.width * K, im.height * K), Image.NEAREST)
            bg = Image.new('RGB', (190, ROW - 12), (196, 52, 28))
            bg.paste(m, ((190 - m.width) // 2, (ROW - 12 - m.height) // 2), m)
            sheet.paste(bg, (x, y)); x += 200
    rng = np.random.default_rng(21)
    SW, SH = 320, 200
    scene = marble(SW, SH, rng).convert('RGBA')
    pz = pizza_base(170, rng)
    layer = Image.new('RGBA', (170, 170), (0, 0, 0, 0))
    prng = np.random.default_rng(8)
    for k in range(14):
        a, r = prng.random() * 6.28, np.sqrt(prng.random()) * 56
        layer.alpha_composite(grated('mozz', 80 + k, 'shred', n_bits=40), (int(85 + np.cos(a) * r - 13), int(85 + np.sin(a) * r - 12)))
    pieces = [s[1][i % 3] for s in sets for i in range(3)] + [G.mozz(s) for s in (1, 2)]
    prng.shuffle(pieces); spots = []
    for p in pieces:
        for _ in range(300):
            a, r = prng.random() * 6.28, np.sqrt(prng.random()) * 58
            x, y = 85 + np.cos(a) * r, 85 + np.sin(a) * r
            if all(np.hypot(x - sx, y - sy) > 17 for sx, sy in spots): break
        spots.append((x, y))
        layer.alpha_composite(drop(p), (int(x - p.width / 2), int(y - p.height / 2)))
    pz.alpha_composite(layer)
    sh = Image.new('RGBA', (176, 176), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse((4, 6, 174, 176), fill=(40, 30, 20, 90))
    scene.alpha_composite(sh, (70, 12)); scene.alpha_composite(pz, (72, 12))
    y0 = 36 + ROW * len(sets) + 8
    dr.text((20, y0), 'Na pizza (320×200 ×3)', fill=(240, 220, 180), font=fs)
    sheet.paste(scene.convert('RGB').resize((SW * 3, SH * 3), Image.NEAREST), (20, y0 + 24))
    sheet.save(OUT + 'preview_ingredientes3.png')
    print('ok', sheet.size)
