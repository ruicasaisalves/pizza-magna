#!/usr/bin/env python3
"""Pizza Magna: sexto lote em pixel detalhado. Espinafres, tomate cherry, jalapeños,
anchovas, ricotta e pera, com a forma picada pela regra de docs/ingredientes.md.
Mesmo método de gen_ingredients.py.

As peças com frente (anchova com cauda, meia pera com pé) aceitam `ang`: com ang=0 saem
deitadas, com a frente para a direita, e o jogo roda essa imagem em quartos de volta.
Uso: python3 tools/gen_ingredients6.py <pasta>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from gen_ingredients import R, hexs, noise, shade, render
from gen_ingredients2 import grated, grid
from gen_ingredients5 import axes, erode

OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'preview')) + '/'
os.makedirs(OUT, exist_ok=True)

R.update({
    'spin': hexs(['#0a2a10', '#123e18', '#1e5a24', '#2e7a30', '#56a046']),
    'spinvein': hexs(['#2e6a2a', '#5a9a46', '#8cc46a']),
    'cherry': hexs(['#5e0e08', '#8e1a10', '#c02a1a', '#e44a2e', '#ff8a64']),
    'cherryj': hexs(['#a64f16', '#d47b24', '#f2a83e', '#ffd36e']),
    'jal': hexs(['#0e3010', '#1a4c18', '#2a6a24', '#468a34', '#72b052']),
    'jalpith': hexs(['#a8b884', '#ccdaa4', '#e6efc8', '#f6fae6']),
    'anch': hexs(['#3a1a10', '#5e2a18', '#8a4426', '#b06838', '#d49a62']),
    'anchskin': hexs(['#3e3e48', '#6a6a78', '#a4a4b4', '#d4d4e0']),
    'anchback': hexs(['#101c2a', '#1e3448', '#305068', '#4a7290', '#7aa0bc']),
    'anchbelly': hexs(['#7a808e', '#a4aab8', '#ccd2dc', '#eef0f6']),
    'anchsilver': hexs(['#a8b4c4', '#d0dae6', '#f4f8fc', '#ffffff']),
    'ricotta': hexs(['#b4ac9c', '#d6d0c2', '#ece8de', '#f8f6f0', '#ffffff']),
    'pear': hexs(['#c8b47c', '#e2d4a2', '#f2eac8', '#fbf6e4', '#fffdf4']),
    'pearskin': hexs(['#5e5a14', '#8a8420', '#b4ac34', '#d4c852']),
    'pearseed': hexs(['#1e0e06', '#3e200e', '#5e3416']),
    'pstem': hexs(['#2e1a0a', '#4e2e14', '#6e4420']),
})

# ---------------- ESPINAFRE (folha oval, um pouco murcha do forno) ----------------
def spinach(seed, W=26, H=20):
    rng = np.random.default_rng(seed + 2400)
    u, v = axes(W, H, rng.random() * 6.28)
    n = noise(H, W, 3, rng)
    t = (u + 10) / 20                                       # 0 no pé, 1 na ponta
    halfw = np.sin(np.clip(t, 0, 1) * np.pi) ** .55 * 7.2 * (1 + (n - .5) * .35)
    leaf = (t >= 0) & (t <= 1) & (np.abs(v) <= halfw)
    stem = (u >= -13) & (u < -9.5) & (np.abs(v) <= .9)
    mask = leaf | stem
    height = np.clip(1 - (v / (halfw + .01)) ** 2, 0, 1) * 1.3 + (n - .5) * .9    # ondulada
    lat = (np.abs((u - np.abs(v) * .9) % 4.5 - 2.2) < .45) & (np.abs(v) > 1) & (np.abs(v) < halfw - 1.2)
    mat = [['spinvein' if mask[y, x] and (stem[y, x] or abs(v[y, x]) < .55 and t[y, x] < .9 or lat[y, x]) else 'spin'
            for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .8 + .22, 0, 1) * mask, mask, {'spinvein': 'spin'})

# ---------------- TOMATE CHERRY (metade) ----------------
def cherry(seed, D=14):
    rng = np.random.default_rng(seed + 2500)
    ys, xs, c, _ = grid(D, D)
    sq = 1 + (rng.random() - .5) * .16
    r = np.hypot((xs - c) * sq, (ys - c) / sq) / (D / 2 - .3)
    ang = np.arctan2(ys - c, xs - c) - rng.random() * 3.14
    mask = r <= 1
    height = np.sqrt(np.clip(1 - r ** 2, 0, 1)) * 2.2
    # dois lóbulos de sementes, um de cada lado do septo
    lobe = (r > .25) & (r < .72) & (np.abs(np.sin(ang)) > .42)
    mat = [['cherry' if r[y, x] > .8 or not lobe[y, x] else 'cherryj' for x in range(D)] for y in range(D)]
    img = render(mat, np.clip(shade(height, mask) * .85 + .2, 0, 1) * mask, mask, {'cherryj': 'cherry'})
    px = img.load()
    for k in range(4):                                       # sementes
        a = ang[0, 0] * 0 + (k // 2) * np.pi + (k % 2 - .5) * .5 + np.pi / 2 + rng.random() * .2
        x, y = int(round(c + np.cos(a) * 3.2)), int(round(c + np.sin(a) * 3.2))
        if mask[y, x]: px[x, y] = (255, 240, 190, 255)
    px[int(c - 3), int(c - 3)] = R['cherry'][4] + (255,)      # brilho
    return img

# ---------------- JALAPEÑO (rodela) ----------------
def jalapeno(seed, D=15):
    rng = np.random.default_rng(seed + 2600)
    ys, xs, c, _ = grid(D, D)
    ang = np.arctan2(ys - c, xs - c)
    r = np.hypot(xs - c, ys - c) / (D / 2 - .4) / (1 + .07 * np.sin(ang * 3 + seed))
    mask = (r <= 1) & (r >= .3)
    height = np.clip(1 - ((r - .65) / .36) ** 2, 0, 1) * 1.4
    mat = [['jal' if r[y, x] > .7 else 'jalpith' for x in range(D)] for y in range(D)]
    img = render(mat, np.clip(shade(height, mask) * .85 + .2, 0, 1) * mask, mask, {'jalpith': 'jal'})
    px = img.load()
    for k in range(3 + seed % 2):                            # sementes coladas à polpa
        a = rng.random() * 6.28
        x, y = int(round(c + np.cos(a) * 3)), int(round(c + np.sin(a) * 3))
        if 0 <= x < D and 0 <= y < D: px[x, y] = (246, 240, 206, 255)
    return img

# ---------------- ANCHOVA (peixinho inteiro: cabeça à esquerda, cauda à direita) ----------------
def anchovy(seed, L=28, ang=None):
    rng = np.random.default_rng(seed + 2700)
    a = (rng.random() - .5) * .8 if ang is None else ang
    W, H = L + 4, int(np.ceil(L * abs(np.sin(a)) + 10 * abs(np.cos(a)))) + 8
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    u, v = axes(W, H, a)
    t = (u + L / 2) / L                                     # 0 no focinho, 1 na cauda
    vv = v - .7 * np.sin(t * 3 + seed)                      # corpo levemente curvado
    half = np.select([t < .14, t < .62, t < .86],
                     [3.6 * np.sqrt(np.clip(t / .14, 0, 1)),            # focinho redondo
                      3.6 + 0 * t,                                       # corpo
                      3.6 - (t - .62) / .24 * 2.6], .9)                  # afina até à cauda
    body = (t >= 0) & (t <= .88) & (np.abs(vv) <= half)
    fork = (t > .84) & (t <= 1) & (np.abs(np.abs(vv) - (t - .84) * 26) <= 1.3)   # cauda em forquilha
    mask = body | fork
    height = np.clip(1 - (vv / (half + .01)) ** 2, 0, 1) * 1.5
    gill = body & (np.abs(t - .2 - (vv / 3.6) ** 2 * .04) < .55 / L)
    stripe = body & (np.abs(vv - .3) < .55) & (t > .24) & (t < .84)
    def m(y, x):
        if not mask[y, x]: return 'anchback'
        if fork[y, x] and not body[y, x]: return 'anchback'
        if gill[y, x]: return 'anchback'
        if stripe[y, x]: return 'anchsilver'
        return 'anchback' if vv[y, x] < 0 else 'anchbelly'
    mat = [[m(y, x) for x in range(W)] for y in range(H)]
    light = np.clip(shade(height, mask) * .8 + .25 + np.where(stripe, .35, 0), 0, 1) * mask
    img = render(mat, light, mask, {'anchbelly': 'anchback', 'anchsilver': 'anchback'})
    # olho: ponto escuro com brilho, na cabeça, acima do meio
    ex, ey = -L / 2 + .1 * L, -1.0
    ca, sa = np.cos(a), np.sin(a)
    cx, cy = (W - 1) / 2, (H - 1) / 2
    def at(uu, ww):
        ww = ww + .7 * np.sin((uu + L / 2) / L * 3 + seed)
        return int(round(cx + uu * ca - ww * sa)), int(round(cy + uu * sa + ww * ca))
    px = img.load()
    x, y = at(ex, ey)
    if 0 <= x < W and 0 <= y < H: px[x, y] = (12, 14, 20, 255)
    x, y = at(ex - 1, ey - 1)
    if 0 <= x < W and 0 <= y < H and mask[y, x]: px[x, y] = (236, 240, 248, 255)
    return img

# ---------------- RICOTTA (colherada granulosa) ----------------
def ricotta(seed, W=22, H=18):
    rng = np.random.default_rng(seed + 2800)
    ys, xs, cx, cy = grid(W, H)
    dx, dy = (xs - cx) / (W / 2 - 1.5), (ys - cy) / (H / 2 - 1.5)
    ang = np.arctan2(dy, dx); a, b = rng.random(2) * 6.28
    rr = np.hypot(dx, dy) / (1 + .1 * np.sin(ang * 3 + a) + .07 * np.sin(ang * 6 + b))
    mask = rr <= 1
    grain = rng.random((H, W))
    height = np.clip(1 - rr ** 2, 0, 1) ** .6 * 2.2 + (grain - .5) * .7            # grãos de coalho
    mat = [['ricotta'] * W for _ in range(H)]
    return render(mat, np.clip(shade(height, mask) * .7 + .3, 0, 1) * mask, mask, {})

# ---------------- PERA (metade cortada ao comprido, pé para a direita) ----------------
def pear(seed, ang=None, W=28, H=22):
    rng = np.random.default_rng(seed + 2900)
    a = (rng.random() - .5) * 1.0 if ang is None else ang
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    u, v = axes(W, H, a)
    u = u + 1.5
    w = np.where(u <= -3, 8 * np.sqrt(np.clip(1 - ((u + 3) / 8) ** 2, 0, 1)),      # bojo
                 np.where(u <= 5, 8 - (u + 3) * .45, 4.4 * np.sqrt(np.clip(1 - ((u - 5) / 5.5) ** 2, 0, 1))))   # pescoço
    body = (u >= -11) & (u <= 10.5) & (np.abs(v) <= w)
    stem = (u > 9.5) & (u <= 13) & (np.abs(v - (u - 9.5) * .35) <= .9)
    mask = body | stem
    e2 = erode(erode(body))
    core = np.hypot((u + 3.5) / 3.2, v / 2.2) <= 1
    seeds = (np.hypot((u + 3.5 - np.abs(v) * .4) / 1.5, (np.abs(v) - 1.7) / .75) <= 1)    # duas pevides em V
    height = np.clip(1 - (v / (w + .01)) ** 2, 0, 1) * 1.4 + np.where(core, -.3, 0)
    mat = [[('pstem' if stem[y, x] and not body[y, x] else 'pearskin' if not e2[y, x]
             else 'pearseed' if seeds[y, x] else 'pear') for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .75 + .28, 0, 1) * mask, mask, {'pear': 'pearskin', 'pearseed': 'pearseed'})

SETS = [
    ('Espinafres', spinach, ('spin', 'flake', 44)),
    ('Tomate cherry', cherry, ('cherry', 'cube', 11)),
    ('Jalapeños', jalapeno, ('jal', 'flake', 40)),
    ('Anchovas', anchovy, ('anch', 'chunk', 9)),
    ('Ricotta', ricotta, ('ricotta', 'flake', 40)),
    ('Pera', pear, ('pear', 'cube', 11)),
]

if __name__ == '__main__':
    from gen_ingredients import drop
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 17)
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    K, ROW = 6, 150
    sheet = Image.new('RGB', (1000, 40 + ROW * len(SETS)), (27, 20, 16))
    dr = ImageDraw.Draw(sheet)
    dr.text((20, 10), 'Inteiro / fatiado (×6, 3 variantes)', fill=(240, 220, 180), font=fs)
    dr.text((760, 10), 'Ralado / picado (×6)', fill=(240, 220, 180), font=fs)
    for i, (name, fn, gr) in enumerate(SETS):
        key = name.lower().replace(' ', '_').replace('ñ', 'n')
        arr = [fn(s) for s in (1, 2, 3)]
        g = grated(gr[0], 70 + i, gr[1], n_bits=gr[2])
        for j, im in enumerate(arr): im.save(f'{OUT}{key}_{j + 1}.png')
        g.save(f'{OUT}{key}_picado.png')
        y = 36 + i * ROW
        dr.text((20, y + 4), name.replace(' ', '\n'), fill=(240, 220, 180), font=f)
        x = 150
        for im in arr + [g]:
            if im is g: x = 760
            m = drop(im).resize(((im.width + 2) * K, (im.height + 2) * K), Image.NEAREST)
            if m.width > 186: m = drop(im).resize(((im.width + 2) * 4, (im.height + 2) * 4), Image.NEAREST)
            bg = Image.new('RGB', (190, ROW - 12), (196, 52, 28))
            bg.paste(m, ((190 - m.width) // 2, (ROW - 12 - m.height) // 2), m)
            sheet.paste(bg, (x, y)); x += 200
    sheet.save(OUT + 'preview_ingredientes6.png')
    print('ok', sheet.size)
