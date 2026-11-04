#!/usr/bin/env python3
"""Esboço: 3 ingredientes em pixel detalhado (mozzarella, tomate, bacon).
Cada pixel: material + luz (normal de um campo de altura, luz de cima-esquerda),
quantizado numa rampa curta com dithering ordenado 4x4 (Bayer). Contorno seletivo
(o tom mais escuro da própria rampa, não preto)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import os, sys
OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'preview')) + '/'
os.makedirs(OUT, exist_ok=True)
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16 - .47
L = np.array([-.55, -.65, .52]); L /= np.linalg.norm(L)

def hexs(r): return [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5)) for h in r]

R = {
    'flesh': hexs(['#6a120b', '#951d13', '#c22d1d', '#e2462f', '#f77356', '#ffab8a']),
    'jelly': hexs(['#a64f16', '#d47b24', '#f2a83e', '#ffd36e', '#fff0b4']),
    'core': hexs(['#a8341f', '#d9573c', '#f38866', '#ffbea0']),
    'skin': hexs(['#4a0b06', '#7a160d', '#a8241a', '#d9452e']),
    'mozz': hexs(['#a8875a', '#cfb486', '#e8d6ac', '#f6ead0', '#fffaee', '#ffffff']),
    'brown': hexs(['#9a6a34', '#c48c4c', '#dfac68', '#f0cc8e']),
    'meat': hexs(['#4e130b', '#771f14', '#a03322', '#c44c34', '#e27050']),
    'fat': hexs(['#93684a', '#c49470', '#e5bf9c', '#f8e2c8', '#fff4e4']),
    'crisp': hexs(['#3e1a0c', '#6a2e14', '#934420']),
}

def noise(h, w, cell, rng):
    g = rng.random((h // cell + 3, w // cell + 3))
    ys, xs = np.mgrid[0:h, 0:w] / cell
    y0, x0 = ys.astype(int), xs.astype(int); fy, fx = ys - y0, xs - x0
    fy, fx = fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx)
    a, b, c, d = g[y0, x0], g[y0, x0 + 1], g[y0 + 1, x0], g[y0 + 1, x0 + 1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy

def shade(height, mask):
    gy, gx = np.gradient(height)
    n = np.dstack([-gx * 2.2, -gy * 2.2, np.ones_like(height)])
    n /= np.linalg.norm(n, axis=2, keepdims=True)
    lit = (n @ L)
    return np.clip((lit - .25) / .75, 0, 1) * mask

def quant(val, ramp, y, x, bias=0.0):
    k = len(ramp)
    v = np.clip(val * (k - 1) + BAYER[y % 4, x % 4] * .9 + bias, 0, k - 1)
    return ramp[int(round(v))]

def render(mat, light, mask, outline_ramp):
    h, w = mask.shape
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0)); px = img.load()
    for y in range(h):
        for x in range(w):
            if not mask[y, x]: continue
            m = mat[y][x]
            px[x, y] = quant(light[y, x], R[m], y, x) + (255,)
    # contorno seletivo: píxeis da borda passam ao tom escuro da sua rampa
    for y in range(h):
        for x in range(w):
            if not mask[y, x]: continue
            edge = any(not (0 <= y + dy < h and 0 <= x + dx < w and mask[y + dy, x + dx])
                       for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if edge:
                ramp = R[outline_ramp.get(mat[y][x], mat[y][x])]
                lit = light[y, x]
                px[x, y] = ramp[0 if lit < .55 else 1] + (255,)
    return img

# ---------------- TOMATE (rodela) ----------------
def tomato(seed, D=26):
    rng = np.random.default_rng(seed)
    c = (D - 1) / 2
    ys, xs = np.mgrid[0:D, 0:D]
    dx, dy = xs - c, ys - c
    r = np.hypot(dx, dy) / (D / 2 - .3)
    ang = np.arctan2(dy, dx)
    wob = 1 + .035 * np.sin(ang * 3 + seed) + .02 * np.sin(ang * 5 + seed * 2)
    rr = r / wob
    mask = rr <= 1
    rot = rng.random() * 6.28
    n = noise(D, D, 4, rng)
    height = np.sqrt(np.clip(1 - rr ** 2, 0, 1)) * 3.2
    mat = [['flesh'] * D for _ in range(D)]
    lobes = 5 if seed % 2 else 4
    for y in range(D):
        for x in range(D):
            if not mask[y, x]: continue
            q = rr[y, x]
            if q > .86: mat[y][x] = 'skin'; continue
            if q < .2: mat[y][x] = 'core'; continue
            # lóbulos de sementes
            a = (ang[y, x] - rot) % (2 * np.pi / lobes) - np.pi / lobes
            rad, tang = (q - .52) / .24, a / (np.pi / lobes * .62)
            if rad * rad + tang * tang < 1 + (n[y, x] - .5) * .5:
                mat[y][x] = 'jelly'; height[y, x] -= .8
            elif abs(a) < .09 and q < .86:   # septos (parede entre lóbulos)
                mat[y][x] = 'core'
    light = shade(height, mask)
    img = render(mat, light, mask, {'jelly': 'flesh', 'core': 'flesh'})
    # sementes: 2-3 por lóbulo, 1-2 px, claras com ponto escuro
    px = img.load()
    for k in range(lobes):
        a0 = rot + (k + .5) * 2 * np.pi / lobes
        for s in range(3):
            t = (s - 1) * .32
            rad = .5 + (s % 2) * .1
            x = int(round(c + np.cos(a0 + t * .7) * rad * D / 2))
            y = int(round(c + np.sin(a0 + t * .7) * rad * D / 2))
            if 0 <= x < D and 0 <= y < D and mask[y, x]:
                px[x, y] = (255, 246, 196, 255)
                if x + 1 < D and mask[y, x + 1]: px[x + 1, y] = (214, 160, 70, 255)
    # brilho especular (molhado)
    for (x, y) in [(int(c - 5), int(c - 7)), (int(c - 4), int(c - 7)), (int(c - 6), int(c - 6))]:
        if mask[y, x]: px[x, y] = (255, 214, 196, 255)
    return img

# ---------------- MOZZARELLA (pedaço derretido) ----------------
def mozz(seed, W=30, H=26):
    rng = np.random.default_rng(seed + 100)
    ys, xs = np.mgrid[0:H, 0:W]
    cx, cy = (W - 1) / 2, (H - 1) / 2
    dx, dy = (xs - cx) / (W / 2 - 1.2), (ys - cy) / (H / 2 - 1.2)
    ang = np.arctan2(dy, dx); r = np.hypot(dx, dy)
    a, b, c3 = rng.random(3) * 6.28
    edge = 1 + .14 * np.sin(ang * 3 + a) + .09 * np.sin(ang * 5 + b) + .05 * np.sin(ang * 9 + c3)
    rr = r / edge
    n = noise(H, W, 5, rng); n2 = noise(H, W, 2, rng)
    mask = rr <= 1
    # escorre: uma "língua" de queijo para um lado
    la = rng.random() * 6.28
    tongue = (np.cos(ang - la) > .93) & (r < 1.22)
    mask |= tongue
    height = np.clip(1 - rr ** 2, 0, 1) ** .45 * 2.6 + (n - .5) * .9 + (n2 - .5) * .25
    mat = [['mozz'] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if mask[y, x] and height[y, x] > 2.3 and n2[y, x] > .74:
                mat[y][x] = 'brown'          # pintas tostadas no topo
    light = np.clip(shade(height, mask) * .8 + .28, 0, 1) * mask
    img = render(mat, light, mask, {'brown': 'mozz'})
    px = img.load()
    # bolhas: anel claro com centro um tom abaixo
    for _ in range(3):
        x, y = int(cx + (rng.random() - .5) * W * .45), int(cy + (rng.random() - .5) * H * .45)
        if mask[y, x]:
            px[x, y] = R['mozz'][2] + (255,)
            if mask[y - 1, x - 1]: px[x - 1, y - 1] = R['mozz'][5] + (255,)
    return img

# ---------------- BACON (tira ondulada) ----------------
def bacon(seed, W=34, H=24):
    rng = np.random.default_rng(seed + 200)
    ang = (rng.random() - .5) * .9
    ca, sa = np.cos(ang), np.sin(ang)
    ys, xs = np.mgrid[0:H, 0:W]
    u = (xs - (W - 1) / 2) * ca + (ys - (H - 1) / 2) * sa       # ao longo da tira
    v = -(xs - (W - 1) / 2) * sa + (ys - (H - 1) / 2) * ca      # através
    ph = rng.random() * 6.28
    wave = 1.1 * np.sin(u * .3 + ph)                          # tira ondulada
    vv = v - wave
    half = 5.6 + .4 * np.sin(u * .9 + ph * 2)
    L2 = 15.0 - (np.abs(np.sin(v * 1.1 + ph)) * 1.4)            # pontas recortadas
    mask = (np.abs(vv) <= half) & (np.abs(u) <= L2)
    t = (vv / half + 1) / 2                                      # 0..1 através
    n = noise(H, W, 3, rng)
    height = 2.2 * np.cos(u * .42 + ph) * np.sign(np.sin(u * .42 + ph) + 1e-6) * 0 \
        + 1.3 * np.sin(u * .55 + ph) + (n - .5) * .5 + np.clip(1 - (2 * t - 1) ** 2, 0, 1) * 1.6
    mat = [['fat'] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if not mask[y, x]: continue
            tv = t[y, x] + (n[y, x] - .5) * .14
            if .2 < tv < .52 or .64 < tv < .9: mat[y][x] = 'meat'   # faixas de carne
            if abs(u[y, x]) > L2[y, x] - 1.6 and mat[y][x] == 'meat': mat[y][x] = 'crisp'
    light = shade(height, mask)
    return render(mat, light, mask, {'fat': 'meat', 'crisp': 'crisp'})

# ---------------- montagem da prévia ----------------
def drop(img):
    """sombra de 1 px para baixo-direita, como objeto pousado"""
    w, h = img.size
    out = Image.new('RGBA', (w + 2, h + 2), (0, 0, 0, 0))
    a = img.split()[3]
    sh = Image.new('RGBA', img.size, (60, 10, 4, 110)); sh.putalpha(a.point(lambda v: 110 if v else 0))
    out.alpha_composite(sh, (2, 2)); out.alpha_composite(img, (0, 0))
    return out

def pizza_base(D, rng):
    img = Image.new('RGBA', (D, D), (0, 0, 0, 0)); px = img.load()
    c = (D - 1) / 2
    crust = hexs(['#7a4214', '#a8642a', '#cf8a42', '#e9ad62', '#f8cf8e'])
    sauce = hexs(['#7e1a0e', '#a42514', '#c4341c', '#d84a28'])
    n = noise(D, D, 6, rng); n2 = noise(D, D, 2, rng)
    for y in range(D):
        for x in range(D):
            dx, dy = x - c, y - c; r = np.hypot(dx, dy) / (D / 2 - .5)
            if r > 1: continue
            if r > .86:   # bordo: um anel em relevo, luz de cima-esquerda
                t = (r - .86) / .14
                lit = (np.sqrt(max(0, 1 - (2 * t - 1) ** 2)) * .6 + (-dx - dy) / D * .7 + .25 + (n[y, x] - .5) * .5)
                col = quant(np.clip(lit, 0, 1), crust, y, x)
                if n2[y, x] > .93: col = crust[1]
            else:
                lit = .45 + (-dx - dy) / D * .25 + (n[y, x] - .5) * .55
                col = quant(np.clip(lit, 0, 1), sauce, y, x)
            px[x, y] = col + (255,)
    return img

def marble(w, h, rng):
    img = Image.new('RGB', (w, h)); px = img.load()
    ramp = hexs(['#9a958c', '#b9b4aa', '#d2cec4', '#e6e2d9', '#f3f0ea'])
    n = noise(h, w, 18, rng); n2 = noise(h, w, 5, rng)
    for y in range(h):
        for x in range(w):
            vein = abs(np.sin((x * .5 + y * .9) / 14 + n[y, x] * 4))
            v = .74 + (n2[y, x] - .5) * .3 - (vein < .05) * .22 - (vein < .02) * .14
            px[x, y] = quant(np.clip(v, 0, 1), ramp, y, x)
    return img

if __name__ == '__main__':
    rng = np.random.default_rng(5)
    toms = [tomato(s) for s in (1, 2, 3)]
    mozs = [mozz(s) for s in (1, 2, 3)]
    bacs = [bacon(s) for s in (1, 2, 3)]
    for name, arr in (('tomate', toms), ('mozzarella', mozs), ('bacon', bacs)):
        for i, im in enumerate(arr): im.save(f'{OUT}{name}_{i + 1}.png')

    # cena: pizza de 170 px sobre mármore, à escala de um ecrã 320x200
    SW, SH = 320, 200
    scene = marble(SW, SH, rng).convert('RGBA')
    pz = pizza_base(170, rng)
    pieces = []
    for i in range(7): pieces.append(mozs[i % 3])
    for i in range(6): pieces.append(toms[i % 3])
    for i in range(5): pieces.append(bacs[i % 3])
    layer = Image.new('RGBA', (170, 170), (0, 0, 0, 0))
    spots = []
    prng = np.random.default_rng(11)
    order = list(range(len(pieces))); prng.shuffle(order)
    for k in order:
        p = pieces[k]
        for _ in range(200):
            a, r = prng.random() * 6.28, np.sqrt(prng.random()) * 55
            x, y = 85 + np.cos(a) * r, 85 + np.sin(a) * r
            if all(np.hypot(x - sx, y - sy) > 19 for sx, sy in spots): break
        spots.append((x, y))
        layer.alpha_composite(drop(p), (int(x - p.width / 2), int(y - p.height / 2)))
    pz.alpha_composite(layer)
    sh = Image.new('RGBA', (176, 176), (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
    d.ellipse((4, 6, 174, 176), fill=(40, 30, 20, 90))
    scene.alpha_composite(sh, (70, 12)); scene.alpha_composite(pz, (72, 12))

    # folha final: cada ingrediente ×8 numa caixa, depois as 9 variantes ×4, depois a cena ×3
    K, KS = 8, 3
    W = SW * KS + 40
    sheet = Image.new('RGB', (W, 2000), (27, 20, 16))
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 20)
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    dr = ImageDraw.Draw(sheet)
    BOX = 300
    for gi, (name, arr) in enumerate((('Mozzarella', mozs), ('Tomate', toms), ('Bacon', bacs))):
        x = 20 + gi * (BOX + 20)
        dr.text((x, 12), name + '  (×8)', fill=(240, 220, 180), font=f)
        big = arr[0].resize((arr[0].width * K, arr[0].height * K), Image.NEAREST)
        bg = Image.new('RGB', (BOX, 240), (196, 52, 28))
        bg.paste(big, ((BOX - big.width) // 2, (240 - big.height) // 2), big)
        sheet.paste(bg, (x, 42))
    yv = 42 + 240 + 16
    dr.text((20, yv), 'Variantes (×3), para a pizza não ter peças repetidas', fill=(240, 220, 180), font=fs)
    x = 20
    for arr in (mozs, toms, bacs):
        for im in arr:
            m = im.resize((im.width * 3, im.height * 3), Image.NEAREST)
            bg = Image.new('RGB', (m.width + 8, 112), (196, 52, 28))
            bg.paste(m, (4, (112 - m.height) // 2), m)
            sheet.paste(bg, (x, yv + 24)); x += bg.width + 6
    y0 = yv + 24 + 112 + 24
    dr.text((20, y0), 'Na pizza, à escala do jogo (ecrã 320×200, ampliado ×3)', fill=(240, 220, 180), font=fs)
    sheet.paste(scene.convert('RGB').resize((SW * KS, SH * KS), Image.NEAREST), (20, y0 + 26))
    sheet = sheet.crop((0, 0, W, y0 + 26 + SH * KS + 20))
    sheet.save(OUT + 'preview_ingredientes.png')
    print('ok', sheet.size)
