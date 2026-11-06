#!/usr/bin/env python3
"""Pizza Magna: décimo lote em pixel detalhado. Nutella, banana, feta, farinheira,
amêijoas e orégãos, com a forma picada pela regra de docs/ingredients.md.
Mesmo método de gen_ingredients.py (ver tools/CLAUDE.md).

As peças com frente (amêijoa com a dobradiça da concha, raminho de orégãos) aceitam `ang`:
com ang=0 saem deitadas, com a frente para a direita, e o jogo roda essa imagem em quartos de volta.
Uso: python3 tools/gen_ingredients10.py <pasta>"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
from gen_ingredients import R, hexs, noise, shade, render
from gen_ingredients2 import grated, grid
from gen_ingredients5 import axes

OUT = (sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'preview')) + '/'
os.makedirs(OUT, exist_ok=True)

R.update({
    'nutella': hexs(['#1e0c06', '#36180a', '#522612', '#6e3a1e', '#9a5e38']),
    'banana': hexs(['#b8a058', '#d8c27a', '#ecdca0', '#f8f0c8', '#fffbe6']),
    'banseed': hexs(['#4a2e14', '#6a4420', '#8a5e30']),
    'feta': hexs(['#a8a69c', '#cac8bc', '#e4e2d8', '#f4f3ee', '#ffffff']),
    'farin': hexs(['#9a6a3a', '#c08a52', '#daa870', '#ecc896', '#f8e2b8']),
    'farinskin': hexs(['#5a2e14', '#7e4420', '#a05e30']),
    'paprika': hexs(['#7a1e0c', '#a4321a', '#c84a28']),
    'clam': hexs(['#4a3a2c', '#6e5a46', '#94806a', '#bca88e', '#e2d4bc']),
    'clammeat': hexs(['#a4683c', '#c88a58', '#e6ae7c', '#f8d0a4']),
    'oreg': hexs(['#1e3214', '#2e4a1c', '#466a2a', '#64883c', '#8eac5a']),
    'orestem': hexs(['#3a3a1a', '#5a5a2a', '#7e7c40']),
})

# ---------------- NUTELLA (colherada espalhada, com o remoinho da colher) ----------------
def nutella(seed, W=24, H=19):
    rng = np.random.default_rng(seed + 4800)
    ys, xs, cx, cy = grid(W, H)
    dx, dy = (xs - cx) / (W / 2 - 1.2), (ys - cy) / (H / 2 - 1.2)
    ang = np.arctan2(dy, dx); a, b = rng.random(2) * 6.28
    r = np.hypot(dx, dy)
    rr = r / (1 + .1 * np.sin(ang * 3 + a) + .06 * np.sin(ang * 5 + b))
    mask = rr <= 1
    swirl = np.sin(ang * 1 + r * 9 + a) * .45                 # remoinho deixado pela colher
    height = np.clip(1 - rr ** 2, 0, 1) ** .5 * 1.6 + swirl * np.clip(1 - rr, 0, 1)
    mat = [['nutella'] * W for _ in range(H)]
    light = np.clip(shade(height, mask) * 1.05 + .08, 0, 1) * mask      # brilhante: contraste forte
    return render(mat, light, mask, {})

# ---------------- BANANA (rodela, com a estrela de sementes no meio) ----------------
def banana(seed, D=16):
    rng = np.random.default_rng(seed + 4900)
    ys, xs, c, _ = grid(D, D)
    sq = 1 + (rng.random() - .5) * .16
    r = np.hypot((xs - c) * sq, (ys - c) / sq) / (D / 2 - .4)
    ang = np.arctan2(ys - c, xs - c) - rng.random() * 2
    mask = r <= 1
    height = np.clip(1 - r ** 2, 0, 1) ** .4 * 1.2
    star = (r < .38) & (np.abs(np.sin(ang * 1.5)) > .82) & (r > .12)     # três raios de sementes
    mat = [['banseed' if star[y, x] else 'banana' for x in range(D)] for y in range(D)]
    light = np.clip(shade(height, mask) * .65 + .35 - np.where(r > .82, .18, 0), 0, 1) * mask   # bordo mais escuro
    return render(mat, light, mask, {'banseed': 'banana'})

# ---------------- FETA (cubo esfarelado, em 3/4: topo claro, frente média, lado escuro) ----------------
def feta(seed, W=17, H=17):
    rng = np.random.default_rng(seed + 5000)
    sz, d = int(rng.integers(10, 12)), 4
    x0, y0 = 1, 1
    lt = Image.new('L', (W, H), 0); dl = ImageDraw.Draw(lt)
    dl.polygon([(x0, y0 + d), (x0 + sz, y0 + d), (x0 + sz + d, y0), (x0 + d, y0)], fill=245)                 # topo
    dl.rectangle([x0, y0 + d, x0 + sz - 1, y0 + d + sz - 1], fill=150)                                       # frente
    dl.polygon([(x0 + sz, y0 + d), (x0 + sz + d, y0), (x0 + sz + d, y0 + sz - 1), (x0 + sz, y0 + d + sz - 1)], fill=70)   # lado
    light = np.array(lt) / 255.0
    mask = light > 0
    bite = rng.random((H, W)) > .8                             # arestas esfareladas
    edge = mask & ~(np.roll(mask, 1, 0) & np.roll(mask, -1, 0) & np.roll(mask, 1, 1) & np.roll(mask, -1, 1))
    mask &= ~(edge & bite)
    light = light + (rng.random((H, W)) - .5) * .16            # textura granulada
    mat = [['feta'] * W for _ in range(H)]
    return render(mat, np.clip(light, 0, 1) * mask, mask, {})

# ---------------- FARINHEIRA (rodela clara com pimentão) ----------------
def farinheira(seed, D=18):
    rng = np.random.default_rng(seed + 5100)
    ys, xs, c, _ = grid(D, D)
    r = np.hypot(xs - c, ys - c) / (D / 2 - .4)
    mask = r <= 1
    n = noise(D, D, 2, rng)
    height = np.clip(1 - r ** 2, 0, 1) ** .5 * 1.3 + (n - .5) * .8      # miolo de farinha, esfarelado
    spec = (rng.random((D, D)) > .88) & (r < .82)
    mat = [['farinskin' if r[y, x] > .86 else 'paprika' if spec[y, x] else 'farin' for x in range(D)] for y in range(D)]
    return render(mat, np.clip(shade(height, mask) * .8 + .24, 0, 1) * mask, mask, {'farin': 'farinskin', 'paprika': 'farinskin'})

# ---------------- AMÊIJOA (meia concha com o miolo; dobradiça à esquerda) ----------------
def clam(seed, ang=None, W=22, H=20):
    rng = np.random.default_rng(seed + 5200)
    a = rng.random() * 6.28 if ang is None else ang
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    u, v = axes(W, H, a)
    # triângulo arredondado: estreito na dobradiça (esquerda), largo e redondo no bordo (direita)
    half = 8.0 * np.sqrt(np.clip(1 - (u / 8.4) ** 2, 0, 1)) * (.82 + .18 * np.clip((u + 8.4) / 16.8, 0, 1))
    shell = (np.abs(v) <= half) & (np.abs(u) <= 8.4)
    umbo = np.hypot((u + 8.6) / 1.8, v / 1.6) <= 1             # bico da dobradiça, curto
    mask = shell | umbo
    meat = np.hypot((u - 1.2) / 4.4, v / 4.0) <= 1
    dist = np.hypot(u + 9.5, v * .95)
    rings = (dist % 2.2) < .8                                  # anéis de crescimento
    ribs = np.abs(np.sin(np.arctan2(v, u + 10) * 18)) < .25    # estrias da dobradiça para fora
    height = np.where(meat, 1.2 + np.sqrt(np.clip(1 - (((u - 1.2) / 4.4) ** 2 + (v / 4.0) ** 2), 0, 1)) * 1.3,
                      np.clip(1 - (v / (half + .01)) ** 2, 0, 1) * .9)
    mat = [['clammeat' if meat[y, x] else 'clam' for x in range(W)] for y in range(H)]
    light = np.clip(shade(height, mask) * .7 + .3 - np.where(~meat & rings, .34, 0) - np.where(~meat & ribs, .1, 0), 0, 1) * mask
    return render(mat, light, mask, {'clammeat': 'clam'})

# ---------------- ORÉGÃOS (raminho; pé à esquerda, ponta à direita) ----------------
def oregano(seed, L=22, ang=None):
    rng = np.random.default_rng(seed + 5300)
    a = (rng.random() - .5) * 1.0 if ang is None else ang
    W, H = L + 4, int(np.ceil(L * abs(np.sin(a)) + 12 * abs(np.cos(a)))) + 4
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    u, v = axes(W, H, a)
    vv = v - .6 * np.sin(u * .2 + seed)
    stem = (np.abs(vv) <= .7) & (u >= -L / 2) & (u <= L / 2 - 2)
    leaves = np.zeros_like(stem); lh = np.zeros_like(u)
    for k, lu in enumerate(np.arange(-L / 2 + 4, L / 2 - 1, 3.4)):
        sz = 1 - (lu + L / 2) / L * .35                       # folhas mais pequenas para a ponta
        for side in (-1, 1):
            pu, pv = u - lu - 1, vv - side * 2.2 * sz
            e = (pu / (2.4 * sz)) ** 2 + (pv / (1.5 * sz)) ** 2
            leaves |= e <= 1; lh = np.maximum(lh, np.sqrt(np.clip(1 - e, 0, 1)) * 1.2)
    tip = np.hypot((u - L / 2 + 1.5) / 2.2, vv / 1.6) <= 1     # rebento da ponta
    leaves |= tip
    mask = stem | leaves
    height = np.maximum(np.where(stem, .6, 0), lh + np.where(tip, 1, 0))
    mat = [['oreg' if leaves[y, x] else 'orestem' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .8 + .24, 0, 1) * mask, mask, {'orestem': 'orestem'})

def oregano_flakes(seed):
    """orégãos secos: migalhas verde-acinzentadas, mais miúdas que as das ervas frescas"""
    return grated('oreg', seed, 'flake', n_bits=50)

SETS = [
    ('Nutella', nutella, None),
    ('Banana', banana, ('banana', 'cube', 11)),
    ('Feta', feta, ('feta', 'flake', 40)),
    ('Farinheira', farinheira, ('farin', 'cube', 11)),
    ('Amêijoas', clam, ('clammeat', 'chunk', 9)),
    ('Orégãos', oregano, oregano_flakes),
]

if __name__ == '__main__':
    from gen_ingredients import drop
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 17)
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    ROW = 150
    sheet = Image.new('RGB', (1000, 40 + ROW * len(SETS)), (27, 20, 16))
    dr = ImageDraw.Draw(sheet)
    dr.text((20, 10), 'Inteiro / fatiado (3 variantes)', fill=(240, 220, 180), font=fs)
    dr.text((760, 10), 'Ralado / picado', fill=(240, 220, 180), font=fs)
    for i, (name, fn, gr) in enumerate(SETS):
        key = name.lower().replace('ê', 'e').replace('ã', 'a').replace('õ', 'o')
        arr = [fn(s) for s in (1, 2, 3)]
        g = (gr(110 + i) if callable(gr) else grated(gr[0], 110 + i, gr[1], n_bits=gr[2])) if gr else None
        for j, im in enumerate(arr): im.save(f'{OUT}{key}_{j + 1}.png')
        if g: g.save(f'{OUT}{key}_picado.png')
        y = 36 + i * ROW
        dr.text((20, y + 4), name, fill=(240, 220, 180), font=f)
        x = 150
        for im in arr + ([g] if g else []):
            if im is g: x = 760
            d = drop(im); K = 6 if (d.width * 6 <= 186 and d.height * 6 <= ROW - 14) else 4
            m = d.resize((d.width * K, d.height * K), Image.NEAREST)
            bg = Image.new('RGB', (190, ROW - 12), (196, 52, 28))
            bg.paste(m, ((190 - m.width) // 2, (ROW - 12 - m.height) // 2), m)
            sheet.paste(bg, (x, y)); x += 200
        if not g:
            dr.text((770, y + 60), 'só se espalha\n(não se pica)', fill=(200, 180, 150), font=fs)
    sheet.save(OUT + 'preview_ingredientes10.png')
    print('ok', sheet.size)
