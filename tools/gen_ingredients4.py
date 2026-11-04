#!/usr/bin/env python3
"""Pizza Magna — quarto lote: piri-piri, ovo, bacalhau, queijo da Serra, mel, rúcula,
e as bases (3 massas x 4 molhos). Uso: python3 tools/gen_ingredients4.py <pasta>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from gen_ingredients import R, hexs, noise, shade, render, drop, marble, quant
from gen_ingredients2 import grated, grid
import gen_ingredients as G

OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'preview')) + '/'
os.makedirs(OUT, exist_ok=True)

R.update({
    'chili': hexs(['#4a0806', '#7a120a', '#b01e12', '#dc3a20', '#ff7a50']),
    'stem': hexs(['#123e16', '#2a6a24', '#4fa040']),
    'eggw': hexs(['#c9bfae', '#e6dece', '#f6f1e6', '#fffdf8', '#ffffff']),
    'yolk': hexs(['#a85a06', '#d8860e', '#f2aa1c', '#ffcc48', '#ffe88a']),
    'cod': hexs(['#a89c86', '#c9bea8', '#e2d8c4', '#f2ebdc', '#fdf9f0']),
    'serra': hexs(['#a8803a', '#cfa860', '#e6c886', '#f4e0ac', '#fff4d4']),
    'rind': hexs(['#7a5a24', '#a07a38', '#c49c54']),
    'honey': hexs(['#7a3c04', '#b0600a', '#e08e18', '#f8b838', '#ffe08a']),
    'vein': hexs(['#123e16', '#3a8a34', '#7cc65e']),
    'rocket': hexs(['#103a12', '#1c5a1c', '#2e7e28', '#4c9e3a', '#80c460']),
})

def chili(seed, W=20, H=12):
    rng = np.random.default_rng(seed + 1300)
    ys, xs, cx, cy = grid(W, H)
    a = (rng.random() - .5) * .8
    u = (xs - cx) * np.cos(a) + (ys - cy) * np.sin(a); v = -(xs - cx) * np.sin(a) + (ys - cy) * np.cos(a)
    t = (u + 8) / 15                                     # 0 no pé, 1 na ponta
    vv = v - .9 * np.sin(t * 3)
    half = 2.6 * (1 - np.clip(t, 0, 1) ** 1.6) + .4
    body = (t >= 0) & (t <= 1) & (np.abs(vv) <= half)
    stem = (u >= -10.5) & (u < -7.6) & (np.abs(v) <= 1.1)
    mask = body | stem
    height = np.clip(1 - (vv / (half + .01)) ** 2, 0, 1) * 1.6
    mat = [['stem' if stem[y, x] and not body[y, x] else 'chili' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .85 + .2, 0, 1) * mask, mask, {'stem': 'stem'})

def egg(seed, W=28, H=26):
    rng = np.random.default_rng(seed + 1400)
    ys, xs, cx, cy = grid(W, H)
    ang = np.arctan2(ys - cy, xs - cx); a, b = rng.random(2) * 6.28
    r = np.hypot(xs - cx, ys - cy) / (12.5 * (1 + .1 * np.sin(ang * 3 + a) + .07 * np.sin(ang * 5 + b)))
    mask = r <= 1
    yx, yy = cx + (rng.random() - .5) * 4, cy + (rng.random() - .5) * 3
    ry = np.hypot(xs - yx, ys - yy) / 5.2
    yolk = ry <= 1
    height = np.clip(1 - r ** 2, 0, 1) ** .3 * .8 + np.where(yolk, np.sqrt(np.clip(1 - ry ** 2, 0, 1)) * 2.4, 0)
    mat = [['yolk' if yolk[y, x] else 'eggw' for x in range(W)] for y in range(H)]
    img = render(mat, np.clip(shade(height, mask) * .75 + .25, 0, 1) * mask, mask, {'yolk': 'yolk'})
    px = img.load()
    for dx, dy in ((-2, -2), (-1, -2), (-2, -1)):
        px[int(yx + dx), int(yy + dy)] = R['yolk'][4] + (255,)
    return img

def cod(seed, W=26, H=20):
    rng = np.random.default_rng(seed + 1500)
    ys, xs, cx, cy = grid(W, H)
    mask = np.zeros((H, W), bool); height = np.zeros((H, W))
    for k in range(4):                                  # lascas em camadas (bacalhau desfaz-se em folhas)
        bx, by = cx + (rng.random() - .5) * 10, cy + (rng.random() - .5) * 6
        a = rng.random() * 3.14
        u = (xs - bx) * np.cos(a) + (ys - by) * np.sin(a); v = -(xs - bx) * np.sin(a) + (ys - by) * np.cos(a)
        d = (u / (6 + rng.random() * 2)) ** 2 + (v / (3 + rng.random())) ** 2
        m = d <= 1; mask |= m
        height = np.maximum(height, np.clip(1 - d, 0, 1) ** .5 * 1.8 + k * .15 + np.sin(u * 1.4) * .2 * m)
    mat = [['cod'] * W for _ in range(H)]
    return render(mat, np.clip(shade(height, mask) * .8 + .22, 0, 1) * mask, mask, {})

def serra(seed, W=26, H=22):
    """queijo amanteigado: uma colherada cremosa que escorre, com pedaço de casca"""
    rng = np.random.default_rng(seed + 1600)
    ys, xs, cx, cy = grid(W, H)
    ang = np.arctan2(ys - cy, xs - cx); a = rng.random() * 6.28
    r = np.hypot(xs - cx, ys - cy) / (10.5 * (1 + .12 * np.sin(ang * 2 + a) + .06 * np.sin(ang * 6 + a)))
    mask = r <= 1
    n = noise(H, W, 4, rng)
    height = np.clip(1 - r ** 2, 0, 1) ** .7 * 2 + (n - .5) * .5
    ra = rng.random() * 6.28
    rind = mask & (r > .78) & (np.cos(ang - ra) > .55)
    mat = [['rind' if rind[y, x] else 'serra' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .8 + .25, 0, 1) * mask, mask, {'rind': 'rind'})

def honey(seed, W=30, H=24):
    """fio de mel em zigue-zague, translúcido, com brilho"""
    rng = np.random.default_rng(seed + 1700)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); px = img.load()
    pts, x, y = [], 3.0, 4 + rng.random() * 4
    for i in range(60):
        x += .42; y += np.sin(i * .38 + seed) * 1.1 + (rng.random() - .5) * .3
        pts.append((x, y))
    for (x, y) in pts:
        for dy in (-1, 0, 1):
            X, Y = int(round(x)), int(round(y)) + dy + 6
            if 0 <= X < W and 0 <= Y < H:
                px[X, Y] = R['honey'][{-1: 3, 0: 2, 1: 0}[dy]] + (230,)
    for (x, y) in pts[::7]:
        X, Y = int(round(x)), int(round(y)) + 5
        if 0 <= X < W and 0 <= Y < H: px[X, Y] = R['honey'][4] + (255,)
    return img

def rocket(seed, W=24, H=16):
    """folha de rúcula: estreita, recortada em lóbulos"""
    rng = np.random.default_rng(seed + 1800)
    ys, xs, cx, cy = grid(W, H)
    a = (rng.random() - .5) * 1.4
    u = (xs - cx) * np.cos(a) + (ys - cy) * np.sin(a); v = -(xs - cx) * np.sin(a) + (ys - cy) * np.cos(a)
    t = (u + 10.5) / 21
    lobes = np.abs(np.sin(t * np.pi * 4.5)) ** .6
    halfw = (np.sin(np.clip(t, 0, 1) * np.pi) ** .5 * 2.2 + lobes * 2.6 * np.clip(t * 1.4, 0, 1)) * (t > 0)
    mask = (t >= 0) & (t <= 1) & (np.abs(v) <= halfw)
    height = np.clip(1 - (v / (halfw + .01)) ** 2, 0, 1) * 1.4
    mat = [['vein' if (abs(v[y, x]) < .55 and t[y, x] < .95) else 'rocket' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .85 + .2, 0, 1) * mask, mask, {'vein': 'rocket'})

# ---------------- bases: massa x molho ----------------
DOUGH = {'Fina': .07, 'Napolitana': .13, 'Alta': .19}            # largura do bordo
SAUCE = {
    'Tomate': hexs(['#7e1a0e', '#a42514', '#c4341c', '#d84a28']),
    'Natas': hexs(['#c9b89a', '#e2d4b8', '#f2e8d4', '#fdf8ee']),
    'Pesto': hexs(['#26401a', '#3a5c22', '#52782e', '#6e9440']),
    'Sem molho': hexs(['#c8904c', '#dcaa64', '#ecc282', '#f6d6a0']),
}

def base(D, dough, sauce, seed=0):
    rng = np.random.default_rng(seed + 50)
    img = Image.new('RGBA', (D, D), (0, 0, 0, 0)); px = img.load()
    c = (D - 1) / 2; w = DOUGH[dough]; sr = SAUCE[sauce]
    crust = hexs(['#7a4214', '#a8642a', '#cf8a42', '#e9ad62', '#f8cf8e'])
    n = noise(D, D, 5, rng); n2 = noise(D, D, 2, rng)
    for y in range(D):
        for x in range(D):
            dx, dy = x - c, y - c; r = np.hypot(dx, dy) / (D / 2 - .5)
            if r > 1: continue
            if r > 1 - w:
                t = (r - (1 - w)) / w
                lit = np.sqrt(max(0, 1 - (2 * t - 1) ** 2)) * (.45 + w * 2) + (-dx - dy) / D * .7 + .2 + (n[y, x] - .5) * .45
                col = quant(np.clip(lit, 0, 1), crust, y, x)
                if n2[y, x] > .93: col = crust[1]
            else:
                lit = .5 + (-dx - dy) / D * .25 + (n[y, x] - .5) * .5
                if sauce == 'Pesto' and n2[y, x] > .82: lit += .35          # grãos de manjericão/pinhão
                col = quant(np.clip(lit, 0, 1), sr, y, x)
            px[x, y] = col + (255,)
    return img

if __name__ == '__main__':
    sets = [
        ('Piri-piri', [chili(s) for s in (1, 2, 3)], grated('chili', 21, 'flake', n_bits=40)),
        ('Ovo', [egg(s) for s in (1, 2, 3)], grated('eggw', 22, 'chunk', n_bits=9)),
        ('Bacalhau', [cod(s) for s in (1, 2, 3)], grated('cod', 23, 'chunk', n_bits=9)),
        ('Queijo\nda Serra', [serra(s) for s in (1, 2, 3)], grated('serra', 24, 'flake', n_bits=40)),
        ('Mel', [honey(s) for s in (1, 2, 3)], None),
        ('Rúcula', [rocket(s) for s in (1, 2, 3)], grated('rocket', 26, 'flake', n_bits=44)),
    ]
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 17)
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    K, ROW = 6, 150
    BH = 3 * 130 + 40
    sheet = Image.new('RGB', (1000, 40 + ROW * len(sets) + BH + 20), (27, 20, 16))
    dr = ImageDraw.Draw(sheet)
    dr.text((20, 10), 'Inteiro / fatiado (×6, 3 variantes)', fill=(240, 220, 180), font=fs)
    dr.text((760, 10), 'Ralado / picado (×6)', fill=(240, 220, 180), font=fs)
    for i, (name, arr, gr) in enumerate(sets):
        key = name.lower().replace('\n', '_').replace(' ', '_')
        for j, im in enumerate(arr): im.save(f'{OUT}{key}_{j + 1}.png')
        if gr: gr.save(f'{OUT}{key}_picado.png')
        y = 36 + i * ROW
        dr.text((20, y + 4), name, fill=(240, 220, 180), font=f)
        x = 150
        for im in arr + ([gr] if gr else []):
            if im is gr: x = 760
            m = im.resize((im.width * K, im.height * K), Image.NEAREST)
            bg = Image.new('RGB', (190, ROW - 12), (196, 52, 28))
            bg.paste(m, ((190 - m.width) // 2, (ROW - 12 - m.height) // 2), m)
            sheet.paste(bg, (x, y)); x += 200
        if not gr:
            dr.text((770, y + 60), 'só em fio\n(não se rala)', fill=(200, 180, 150), font=fs)
    # bases: 3 massas x 4 molhos, a 64 px ×2
    yb = 36 + ROW * len(sets) + 4
    dr.text((20, yb), 'Bases: massa (linhas) × molho (colunas), 64 px ×2', fill=(240, 220, 180), font=fs)
    for i, d in enumerate(DOUGH):
        dr.text((20, yb + 70 + i * 130), d, fill=(240, 220, 180), font=f)
        for j, s in enumerate(SAUCE):
            if i == 0: dr.text((170 + j * 200, yb + 22), s, fill=(240, 220, 180), font=fs)
            b = base(64, d, s, seed=i * 4 + j).resize((128, 128), Image.NEAREST)
            sheet.paste(b, (170 + j * 200, yb + 42 + i * 130), b)
            b.save(f'{OUT}base_{d.lower()}_{s.lower().replace(" ", "_")}.png')
    sheet.save(OUT + 'preview_ingredientes4.png')
    print('ok', sheet.size)
