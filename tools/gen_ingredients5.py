#!/usr/bin/env python3
"""Pizza Magna: quinto lote em pixel detalhado. Espargos, camarão, figo, milho, frango,
salame, gorgonzola e alheira, com a forma picada pela regra de docs/ingredientes.md.
Mesmo método de gen_ingredients.py (campo de altura, luz de cima-esquerda, rampas curtas,
dithering 4x4, contorno seletivo).

As peças com frente (espargos, camarão, meio figo) aceitam `ang`: com ang=0 saem deitadas,
com a frente para a direita, e o jogo roda essa mesma imagem em quartos de volta.
Uso: python3 tools/gen_ingredients5.py <pasta>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from gen_ingredients import R, hexs, noise, shade, render
from gen_ingredients2 import grated, grid

OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'preview')) + '/'
os.makedirs(OUT, exist_ok=True)

R.update({
    'asp': hexs(['#1e3a12', '#2f5a1c', '#4a7e2a', '#6ea040', '#9cc66a']),
    'asptip': hexs(['#2a1a2a', '#4a2e48', '#6a4a5a', '#8e7a6a']),
    'shrimp': hexs(['#8a2e14', '#c4502a', '#e87a48', '#f8a87a', '#ffd4b8']),
    'shrimpw': hexs(['#d8a890', '#f0d0bc', '#fff0e4']),
    'corn': hexs(['#9a6a08', '#d49a14', '#f2c22c', '#ffe064', '#fff4a8']),
    'chick': hexs(['#7a4a22', '#a8703a', '#cc9a5e', '#e6c08a', '#f6e0b8']),
    'char': hexs(['#2e1a0c', '#4a2a14', '#6a3e1e']),
    'salami': hexs(['#4a0c12', '#721820', '#9a2a30', '#bc4448', '#d86860']),
    'salfat': hexs(['#e0c8c0', '#f4e4dc', '#fff8f4']),
    'salskin': hexs(['#2a0a0c', '#46141a', '#6a2228']),
    'gorg': hexs(['#a89c78', '#d0c6a2', '#e8e0c4', '#f6f1e2', '#fffdf6']),
    'gvein': hexs(['#1a2a5e', '#2c4a96', '#4a72c8', '#82a4e6']),
    'figskin': hexs(['#2a0e2a', '#4a1a44', '#6e2a62', '#8e4480']),
    'fig': hexs(['#7a1a2a', '#b02a3a', '#d8505a', '#f08a8a', '#ffc4bc']),
    'figw': hexs(['#c8b890', '#e6dcbc', '#fbf4e2']),
    'alh': hexs(['#7a4a1c', '#a8702e', '#cc9848', '#e4bc70', '#f6dca0']),
    'alhskin': hexs(['#4a2a10', '#6e3e18', '#8e5424']),
    'stem': hexs(['#123e16', '#2a6a24', '#4fa040']),
})

def axes(W, H, a):
    """coordenadas ao longo (u) e através (v) de uma peça com ângulo a"""
    ys, xs, cx, cy = grid(W, H)
    u = (xs - cx) * np.cos(a) + (ys - cy) * np.sin(a)
    v = -(xs - cx) * np.sin(a) + (ys - cy) * np.cos(a)
    return u, v

def erode(m):
    e = m.copy()
    e[1:] &= m[:-1]; e[:-1] &= m[1:]; e[:, 1:] &= m[:, :-1]; e[:, :-1] &= m[:, 1:]
    return e

# ---------------- ESPARGO (lança deitada, cabeça para a direita) ----------------
def asparagus(seed, W=28, H=14, ang=None):
    rng = np.random.default_rng(seed + 1500)
    a = (rng.random() - .5) * .5 if ang is None else ang
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    u, v = axes(W, H, a)
    t = (u + 12.5) / 25                                    # 0 no corte, 1 na ponta
    tip = np.clip((t - .7) / .3, 0, 1)
    half = np.where(t > .7, 3.1 * np.sqrt(np.clip(1 - tip ** 2.2, 0, 1)) + .2, 2.3)      # cabeça mais gorda e em bico
    vv = v - .5 * np.sin(t * 2.4 + seed)
    mask = (t >= 0) & (t <= 1) & (np.abs(vv) <= half)
    height = np.clip(1 - (vv / (half + .01)) ** 2, 0, 1) * 1.6
    scales = ((u * 1.2 + np.abs(vv) * 1.8) % 3.2) < 1.2
    bract = (np.abs(t - .38) < .03) | (np.abs(t - .58) < .03)
    mat = [['asptip' if mask[y, x] and (t[y, x] > .7 and (scales[y, x] or t[y, x] > .9) or bract[y, x] and abs(vv[y, x]) > .9) else 'asp'
            for x in range(W)] for y in range(H)]
    light = np.clip(shade(height, mask) * .85 + .2 + np.where(t < .05, .25, 0), 0, 1) * mask
    return render(mat, light, mask, {'asptip': 'asptip'})

# ---------------- CAMARÃO (em C, cabeça à direita) ----------------
def shrimp(seed, D=22, ang=None):
    rng = np.random.default_rng(seed + 1600)
    a = rng.random() * 6.28 if ang is None else ang
    ys, xs, c, _ = grid(D, D)
    r = np.hypot(xs - c, ys - c)
    th = (np.arctan2(ys - c, xs - c) - a + .45) % (2 * np.pi)   # 0 = cabeça
    s = th / (2 * np.pi - 1.0)                                    # 0 cabeça .. 1 cauda
    R0 = 6.0
    half = 3.6 * (1 - np.clip(s, 0, 1) * .55)
    fan = np.clip((s - .9) * 26, 0, None)                         # leque da cauda
    mask = (s <= 1.04) & (np.abs(r - R0) <= half + fan)
    height = np.clip(1 - ((r - R0) / (half + fan + .01)) ** 2, 0, 1) * 1.8
    band = ((s * 7) % 1) < .14
    mat = [['shrimpw' if mask[y, x] and band[y, x] and .12 < s[y, x] < .9 else 'shrimp' for x in range(D)] for y in range(D)]
    img = render(mat, np.clip(shade(height, mask) * .85 + .2, 0, 1) * mask, mask, {'shrimpw': 'shrimp'})
    ex, ey = c + np.cos(a - .2) * (R0 + 1.2), c + np.sin(a - .2) * (R0 + 1.2)   # olho
    px = img.load(); x, y = int(round(ex)), int(round(ey))
    if mask[y, x]: px[x, y] = (30, 12, 8, 255)
    return img

# ---------------- FIGO (metade, pé para a direita) ----------------
def fig(seed, W=26, H=22, ang=None):
    rng = np.random.default_rng(seed + 1700)
    a = (rng.random() - .5) * 1.2 if ang is None else ang
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    u, v = axes(W, H, a)
    u = u + 1.5
    w = np.where(u <= 0, 8.6 * np.sqrt(np.clip(1 - (u / 9.2) ** 2, 0, 1)), 8.6 * np.clip(1 - u / 10.5, 0, 1) ** 1.1)
    body = (u >= -9.2) & (u <= 10.5) & (np.abs(v) <= w)
    stem = (u > 9.2) & (u <= 12.2) & (np.abs(v) <= 1.1)
    mask = body | stem
    e2 = erode(erode(body)); e4 = erode(erode(e2))
    n = noise(H, W, 2, rng)
    q = np.abs(v) / (w + .01)
    height = np.clip(1 - np.maximum(q, np.abs(u) / 10) ** 2, 0, 1) * 1.4 + (n - .5) * .3
    mat = [[('stem' if stem[y, x] and not body[y, x] else 'figskin' if not e2[y, x] else 'figw' if not e4[y, x] else 'fig')
            for x in range(W)] for y in range(H)]
    img = render(mat, np.clip(shade(height, mask) * .8 + .22, 0, 1) * mask, mask, {'figw': 'figskin', 'fig': 'figskin'})
    px = img.load()
    for y in range(H):                                     # sementes: pontinhos claros no miolo
        for x in range(W):
            if e4[y, x] and erode(e4)[y, x] and ((x * 7 + y * 13 + seed) % 9 == 0) and n[y, x] > .35:
                px[x, y] = R['figw'][2] + (255,)
    return img

# ---------------- MILHO (grãozinhos) ----------------
def corn(seed, W=18, H=15):
    rng = np.random.default_rng(seed + 1800)
    ys, xs, cx, cy = grid(W, H)
    mask = np.zeros((H, W), bool); height = np.zeros((H, W))
    # grãos soltos numa grelha torta, com 1 px de folga para cada um ter o seu contorno
    spots = [(-5, -3), (0, -3.5), (5, -2.5), (-2.5, 1.5), (2.5, 2), (-6, 3), (6.5, 2.5)]
    rng.shuffle(spots)
    for ox, oy in spots[:5 + seed % 2]:
        kx, ky = cx + ox + rng.random() - .5, cy + oy + rng.random() - .5
        rr = np.hypot((xs - kx) / 2.3, (ys - ky) / 2.0)
        m = rr <= 1
        mask |= m; height = np.maximum(height, np.where(m, np.sqrt(np.clip(1 - rr ** 2, 0, 1)) * 2.2, 0))
    mat = [['corn'] * W for _ in range(H)]
    return render(mat, np.clip(shade(height, mask) * .85 + .22, 0, 1) * mask, mask, {})

# ---------------- FRANGO (tira grelhada) ----------------
def chicken(seed, W=24, H=20):
    rng = np.random.default_rng(seed + 1900)
    u, v = axes(W, H, rng.random() * 6.28)
    n = noise(H, W, 3, rng)
    mask = (np.abs(u) <= 9 + (n - .5) * 3) & (np.abs(v) <= 5.2 + (n - .5) * 2)
    height = np.clip(1 - (v / 6) ** 2, 0, 1) * 1.4 + np.clip(1 - (u / 10) ** 2, 0, 1) * .6 + (n - .5) * .6
    grill = ((u * .8 + v * .5 + 40) % 5.5) < 1.2
    mat = [['char' if mask[y, x] and grill[y, x] else 'chick' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .8 + .2, 0, 1) * mask, mask, {'char': 'chick'})

# ---------------- SALAME (rodela com pintas de gordura) ----------------
def salami(seed, D=20):
    rng = np.random.default_rng(seed + 2000)
    ys, xs, c, _ = grid(D, D)
    r = np.hypot(xs - c, ys - c) / (D / 2 - .4)
    mask = r <= 1
    height = np.clip(1 - r ** 2, 0, 1) ** .5 * 1.4
    fat = rng.random((D, D)) > .86
    mat = [['salskin' if r[y, x] > .87 else 'salfat' if fat[y, x] and r[y, x] < .8 else 'salami' for x in range(D)] for y in range(D)]
    return render(mat, np.clip(shade(height, mask) * .8 + .22, 0, 1) * mask, mask, {'salfat': 'salami'})

# ---------------- GORGONZOLA (pedaço esfarelado com veios azuis) ----------------
def gorgonzola(seed, W=24, H=20):
    rng = np.random.default_rng(seed + 2100)
    ys, xs, cx, cy = grid(W, H)
    dx, dy = (xs - cx) / (W / 2 - 1.5), (ys - cy) / (H / 2 - 1.5)
    ang = np.arctan2(dy, dx); a, b = rng.random(2) * 6.28
    rr = np.hypot(dx, dy) / (1 + .12 * np.sin(ang * 4 + a) + .08 * np.sin(ang * 7 + b))
    mask = rr <= 1
    n = noise(H, W, 3, rng); n2 = noise(H, W, 2, rng)
    height = np.clip(1 - rr ** 2, 0, 1) ** .5 * 1.8 + (n2 - .5) * .9
    vein = (np.abs(n - .5) < .07) | (n2 > .84)
    mat = [['gvein' if mask[y, x] and vein[y, x] and rr[y, x] < .9 else 'gorg' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .75 + .3, 0, 1) * mask, mask, {'gvein': 'gorg'})

# ---------------- ALHEIRA (rodela grelhada, recheio de pão e carne) ----------------
def alheira(seed, D=20):
    rng = np.random.default_rng(seed + 2200)
    ys, xs, c, _ = grid(D, D)
    r = np.hypot(xs - c, ys - c) / (D / 2 - .4)
    mask = r <= 1
    n = noise(D, D, 2, rng)
    height = np.clip(1 - r ** 2, 0, 1) ** .5 * 1.3 + (n - .5) * 1.1            # miolo esfarelado
    bits = rng.random((D, D)) > .9
    mat = [['alhskin' if r[y, x] > .86 or (bits[y, x] and r[y, x] < .75) else 'alh' for x in range(D)] for y in range(D)]
    return render(mat, np.clip(shade(height, mask) * .8 + .22, 0, 1) * mask, mask, {'alh': 'alhskin'})

def gorgonzola_crumbs(seed):
    """migalhas de gorgonzola: o ralado normal, com parte das migalhas em azul"""
    img = grated('gorg', seed, 'flake', n_bits=40)
    rng = np.random.default_rng(seed + 2300); px = img.load(); blue = R['gvein']
    for y in range(img.height):
        for x in range(img.width):
            c = px[x, y]
            if c[3] and c[:3] != R['gorg'][0] and rng.random() < .45:
                px[x, y] = blue[1 + int(rng.random() * 3)] + (255,)
    return img

SETS = [
    ('Espargos', asparagus, ('asp', 'flake', 40)),
    ('Camarão', shrimp, ('shrimp', 'chunk', 9)),
    ('Figo', fig, ('fig', 'cube', 11)),
    ('Milho', corn, None),
    ('Frango', chicken, ('chick', 'cube', 12)),
    ('Salame', salami, ('salami', 'cube', 11)),
    ('Gorgonzola', gorgonzola, gorgonzola_crumbs),
    ('Alheira', alheira, ('alh', 'cube', 11)),
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
        key = name.lower().replace('ã', 'a')
        arr = [fn(s) for s in (1, 2, 3)]
        g = (gr(60 + i) if callable(gr) else grated(gr[0], 60 + i, gr[1], n_bits=gr[2])) if gr else None
        for j, im in enumerate(arr): im.save(f'{OUT}{key}_{j + 1}.png')
        if g: g.save(f'{OUT}{key}_picado.png')
        y = 36 + i * ROW
        dr.text((20, y + 4), name, fill=(240, 220, 180), font=f)
        x = 150
        for im in arr + ([g] if g else []):
            if im is g: x = 760
            m = drop(im).resize(((im.width + 2) * K, (im.height + 2) * K), Image.NEAREST)
            bg = Image.new('RGB', (190, ROW - 12), (196, 52, 28))
            bg.paste(m, ((190 - m.width) // 2, (ROW - 12 - m.height) // 2), m)
            sheet.paste(bg, (x, y)); x += 200
        if not g:
            dr.text((770, y + 60), 'já é miúdo\n(não se pica)', fill=(200, 180, 150), font=fs)
    sheet.save(OUT + 'preview_ingredientes5.png')
    print('ok', sheet.size)
