#!/usr/bin/env python3
"""Pizza Magna: décimo sexto lote. Salsicha Frankfurt de lata: comprida, lisa, rosada e
brilhante, com as pontas redondas. Mesmo método de gen_ingredients.py (ver tools/CLAUDE.md).

Roda com 2 posições (é igual de ponta a ponta); com ang=0 sai deitada.
Picada: rodelas, com o miolo claro e a pele mais escura à volta.
Uso: python3 tools/gen_ingredients16.py <pasta>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from gen_ingredients import R, hexs, render, shade
from gen_ingredients2 import grid
from gen_ingredients5 import axes

OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'preview')) + '/'

R.update({
    'frank': hexs(['#7a2e1c', '#a8482c', '#cc6a44', '#e48c62', '#f6b48c']),       # pele cozida
    'frankin': hexs(['#c47a66', '#de9a84', '#f0b8a2', '#fad4c2']),               # miolo da rodela
})

# ---------------- SALSICHA FRANKFURT (de lata: grande, lisa, pontas redondas) ----------------
def frankfurt(seed, ang=None, L=38, T=11):
    rng = np.random.default_rng(seed + 4800)
    a = 0 if ang is None else ang                              # roda: as variantes saem todas deitadas
    W, H = int(np.ceil(L * abs(np.cos(a)) + T * abs(np.sin(a)))) + 4, int(np.ceil(L * abs(np.sin(a)) + T * abs(np.cos(a)))) + 4
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    u, v = axes(W, H, a)
    bend = (.8, -.6, 1.2)[(seed - 1) % 3]                            # curva ligeira, como sai da lata
    vv = v - bend * ((2 * u / L) ** 2 - .5)
    half = T / 2
    cap = np.clip(np.abs(u) - (L / 2 - half), 0, None)        # pontas em meia-lua
    d = np.hypot(cap, vv) / half
    mask = d <= 1
    height = np.sqrt(np.clip(1 - d ** 2, 0, 1)) * 3
    shine = mask & (np.abs(vv + half * .5) < 1) & (np.abs(u) < L / 2 - 4)   # brilho comprido da pele
    mat = [['frank'] * W for _ in range(H)]
    light = np.clip(shade(height, mask) * .9 + .12 + np.where(shine, .6, 0), 0, 1) * mask
    img = render(mat, light, mask, {})
    px = img.load()
    for end in (-1, 1):                                       # o nó da tripa em cada ponta, um pouco mais escuro
        x, y = W / 2 + np.cos(a) * end * (L / 2 - 1), H / 2 + np.sin(a) * end * (L / 2 - 1)
        if ang is not None and abs(np.sin(ang)) > .5: x, y = W / 2 + np.sin(a) * end * (L / 2 - 1), H / 2 + np.cos(a) * end * (L / 2 - 1)
        xi, yi = int(round(x - .5)), int(round(y - .5))
        if 0 <= xi < W and 0 <= yi < H and mask[yi, xi]: px[xi, yi] = R['frank'][1] + (255,)
    return img

def slices(seed, W=26, H=24):
    """picado: 4 ou 5 rodelas espalhadas, miolo claro e anel de pele"""
    rng = np.random.default_rng(seed + 4900)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    placed = []
    for _ in range(30):
        if len(placed) >= 5: break
        D = 9
        x, y = int(rng.integers(0, W - D)), int(rng.integers(0, H - D))
        if any(abs(x - px) < 7 and abs(y - py) < 7 for px, py in placed): continue
        placed.append((x, y))
        ys, xs, c, _ = grid(D, D)
        r = np.hypot(xs - c, ys - c) / (D / 2 - .3)
        mask = r <= 1
        height = (1 - r ** 2) * .6
        mat = [['frank' if r[j, i] > .72 else 'frankin' for i in range(D)] for j in range(D)]
        light = np.clip(shade(height, mask) * .6 + .45, 0, 1) * mask
        img.alpha_composite(render(mat, light, mask, {'frankin': 'frank'}), (x, y))
    return img

SETS = [('Frankfurt', frankfurt, slices)]

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    from build_atlas import drop
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    ROW = 200
    sheet = Image.new('RGB', (1000, 40 + ROW * len(SETS)), (27, 20, 16)); dr = ImageDraw.Draw(sheet)
    dr.text((20, 10), 'Inteiro (a 1.ª é a deitada) / picado', fill=(240, 220, 180), font=fs)
    for i, (name, fn, gr) in enumerate(SETS):
        arr = [fn(1, ang=0), fn(2), fn(3), gr(1)]
        y = 36 + i * ROW; x = 20
        for im in arr:
            d = drop(im); K = 4
            m = d.resize((d.width * K, d.height * K), Image.NEAREST)
            bg = Image.new('RGB', (230, ROW - 12), (196, 52, 28))
            bg.paste(m, ((230 - m.width) // 2, (ROW - 12 - m.height) // 2), m)
            sheet.paste(bg, (x, y)); x += 240
    sheet.save(OUT + 'preview_ingredientes16.png'); print('ok', sheet.size)
