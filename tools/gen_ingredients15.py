#!/usr/bin/env python3
"""Pizza Magna: décimo quinto lote em pixel detalhado, de outras culturas. Tofu, char siu
(China), edamame, frango teriyaki (Japão), catupiry, calabresa (Brasil), mexilhões (Espanha),
brie (França), frango tikka e grão-de-bico (Índia). Mesmo método de gen_ingredients.py
(ver tools/CLAUDE.md).

Rodam: mexilhão (bico da concha) e cunha de brie com 4 posições; vagem de edamame com 2
(simétrica de ponta a ponta). Com ang=0 saem deitados, com a frente para a direita.
O catupiry espalha-se e o grão-de-bico já é miúdo: nenhum dos dois se pica.
Uso: python3 tools/gen_ingredients15.py <pasta>"""
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
    'tofu': hexs(['#a89a76', '#ccc09c', '#e4dabc', '#f2ecd6', '#fcf9ee']),
    'tofufried': hexs(['#8a5a1e', '#b07c30', '#d4a04c']),
    'charsiu': hexs(['#4a0a0e', '#7a1416', '#a82420', '#cc4434', '#e8745a']),
    'charmeat': hexs(['#b0706a', '#cc8e86', '#e2aca2', '#f2c8bc']),
    'edapod': hexs(['#1e4214', '#2e5e1e', '#44802c', '#62a03e', '#8ec260']),
    'teri': hexs(['#1e0c06', '#3a1a0c', '#5a2c14', '#7e4422', '#a86636']),
    'sesame': hexs(['#c8b488', '#e6d6b0', '#fbf2dc']),
    'catu': hexs(['#c4b898', '#ddd4b8', '#eee8d6', '#f9f6ec', '#fffefa']),
    'calab': hexs(['#5a0e10', '#8a1c1c', '#b8322c', '#d85448', '#f07c6a']),
    'calabfat': hexs(['#d8b0a4', '#eccac0', '#fae4dc']),
    'musshell': hexs(['#08080e', '#14141e', '#22223a', '#34345a', '#565a86']),
    'musmeat': hexs(['#a44a14', '#cc6a24', '#ea8c3c', '#f8b064', '#ffd294']),
    'brie': hexs(['#b89a52', '#d4b872', '#e8d294', '#f6e8bc']),
    'brierind': hexs(['#b4aea0', '#d4cfc4', '#ebe8e0', '#fbfaf6']),
    'tikka': hexs(['#5a1606', '#8a2a0e', '#b8441c', '#dc6a32', '#f4985a']),
    'grao': hexs(['#a4844a', '#c8a666', '#e0c288', '#f0daa8', '#fcf0d0']),
})

def box3q(W, H, x0, y0, w, h, d, top=235, front=150, side=70):
    """caixa em 3/4 (topo, frente, lado direito) como mapa de luz, para cubos"""
    lt = Image.new('L', (W, H), 0); dl = ImageDraw.Draw(lt)
    dl.polygon([(x0, y0 + d), (x0 + w, y0 + d), (x0 + w + d, y0), (x0 + d, y0)], fill=top)
    dl.rectangle([x0, y0 + d, x0 + w - 1, y0 + d + h - 1], fill=front)
    dl.polygon([(x0 + w, y0 + d), (x0 + w + d, y0), (x0 + w + d, y0 + h - 1), (x0 + w, y0 + d + h - 1)], fill=side)
    return np.array(lt) / 255.0

# ---------------- TOFU (cubo frito: miolo claro, arestas douradas) ----------------
def tofu(seed, W=17, H=17):
    rng = np.random.default_rng(seed + 7900)
    s = int(rng.integers(10, 12))
    light = box3q(W, H, 1, 1, s, s - 1, 4)
    mask = light > 0
    edge = mask & ~(np.roll(mask, 1, 0) & np.roll(mask, -1, 0) & np.roll(mask, 1, 1) & np.roll(mask, -1, 1))
    light = light + (rng.random((H, W)) - .5) * .06           # liso, com poros finos
    mat = [['tofufried' if edge[y, x] else 'tofu' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(light, 0, 1) * mask, mask, {'tofu': 'tofufried'})

# ---------------- CHAR SIU (fatia de porco lacado: bordo vermelho, miolo rosado) ----------------
def char_siu(seed, W=24, H=18):
    rng = np.random.default_rng(seed + 8000)
    u, v = axes(W, H, (rng.random() - .5) * 1.0)
    n = noise(H, W, 3, rng)
    mask = (np.abs(u) / 10) ** 4 + (np.abs(v) / 6.5) ** 4 <= 1 + (n - .5) * .25
    q = np.maximum(np.abs(u) / 10, np.abs(v) / 6.5)
    glaze = q > .76 + (n - .5) * .1                          # crosta lacada à volta
    height = np.clip(1 - q ** 2, 0, 1) * .8 + np.sin(v * 1.8 + n * 3) * .15
    mat = [['charsiu' if glaze[y, x] else 'charmeat' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .8 + .24, 0, 1) * mask, mask, {'charmeat': 'charsiu'})

# ---------------- EDAMAME (vagem com três grãos; simétrica de ponta a ponta) ----------------
def edamame(seed, ang=None, W=24, H=12):
    rng = np.random.default_rng(seed + 8100)
    a = (rng.random() - .5) * 1.0 if ang is None else ang
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    elif ang is None: W, H = 26, 18
    u, v = axes(W, H, a)
    vv = v - .6 * np.sin(u * .25)
    mask = np.zeros(u.shape, bool); height = np.zeros(u.shape)
    for bu in (-6, 0, 6):                                     # três grãos dentro da vagem
        e = ((u - bu) / 3.6) ** 2 + (vv / 3.0) ** 2
        mask |= e <= 1; height = np.maximum(height, np.where(e <= 1, np.sqrt(np.clip(1 - e, 0, 1)) * 1.6, 0))
    neck = (np.abs(u) <= 9.5) & (np.abs(vv) <= 2.0)
    tips = (np.hypot((np.abs(u) - 10) / 1.4, vv / 1.2) <= 1)
    mask |= neck | tips; height = np.maximum(height, np.where(neck | tips, .7, 0))
    mat = [['edapod'] * W for _ in range(H)]
    return render(mat, np.clip(shade(height, mask) * .85 + .22, 0, 1) * mask, mask, {})

# ---------------- FRANGO TERIYAKI (pedaço lacado e brilhante, com sésamo) ----------------
def teriyaki(seed, W=19, H=16):
    rng = np.random.default_rng(seed + 8200)
    ys, xs, cx, cy = grid(W, H)
    dx, dy = (xs - cx) / 7.6, (ys - cy) / 6.2
    ang = np.arctan2(dy, dx); a = rng.random() * 6.28
    rr = np.hypot(dx, dy) / (1 + .12 * np.sin(ang * 3 + a) + .06 * np.sin(ang * 5 + a * 2))
    mask = rr <= 1
    height = np.clip(1 - rr ** 2, 0, 1) ** .5 * 1.8
    img = render([['teri'] * W for _ in range(H)], np.clip(shade(height, mask) * 1.05 + .1, 0, 1) * mask, mask, {})
    px = img.load()
    for _ in range(4):                                        # sementes de sésamo
        x, y = int(cx + (rng.random() - .5) * 9), int(cy + (rng.random() - .5) * 7)
        if mask[y, x] and x + 1 < W and mask[y, x + 1]:
            px[x, y] = R['sesame'][2] + (255,); px[x + 1, y] = R['sesame'][0] + (255,)
    return img

# ---------------- CATUPIRY (rosa de queijo cremoso, saído do saco) ----------------
def catupiry(seed, W=22, H=20):
    rng = np.random.default_rng(seed + 8300)
    ys, xs, cx, cy = grid(W, H)
    dx, dy = (xs - cx) / (W / 2 - 1.5), (ys - cy) / (H / 2 - 1.5)
    ang = np.arctan2(dy, dx); a = rng.random() * 6.28
    r = np.hypot(dx, dy)
    rr = r / (1 + .1 * np.sin(ang * 6 + a))                   # bordo em pétalas, do bico do saco
    mask = rr <= 1
    spiral = np.sin(ang * 1 - r * 11 + a) * .35               # espiral do creme
    height = np.clip(1 - rr ** 2, 0, 1) ** .7 * 1.8 + spiral * np.clip(1 - rr, 0, 1)
    return render([['catu'] * W for _ in range(H)], np.clip(shade(height, mask) * .8 + .26, 0, 1) * mask, mask, {})

# ---------------- CALABRESA (rodela rosada, de bordo curvado para cima) ----------------
def calabresa(seed, D=19):
    rng = np.random.default_rng(seed + 8400)
    ys, xs, c, _ = grid(D, D)
    sq = 1 + (rng.random() - .5) * .2
    r = np.hypot((xs - c) * sq, (ys - c) / sq) / (D / 2 - .4)
    mask = r <= 1
    height = r ** 2 * 1.3                                     # bordo levantado, como copinho
    fat = (rng.random((D, D)) > .9) & (r < .78)
    mat = [['calabfat' if fat[y, x] else 'calab' for x in range(D)] for y in range(D)]
    light = np.clip(shade(height, mask) * .8 + .25 - np.where(r > .88, .25, 0), 0, 1) * mask
    return render(mat, light, mask, {'calabfat': 'calab'})

# ---------------- MEXILHÃO (meia concha negra com o miolo cor de laranja; bico à esquerda) ----------------
def mussel(seed, ang=None, W=24, H=16):
    rng = np.random.default_rng(seed + 8500)
    a = (rng.random() - .5) * 1.0 if ang is None else ang
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    elif ang is None: W, H = 26, 22
    u, v = axes(W, H, a)
    t = np.clip((u + 10.5) / 21, 0, 1)                         # 0 no bico, 1 no bordo largo
    half = 6.6 * np.clip(np.sin(np.pi * np.clip(t, 0, 1) * .92 + .12), 0, 1) ** .7 * np.where(t > .55, np.sqrt(np.clip(1 - ((t - .55) / .45) ** 2, 0, 1)), 1)
    vv = v - (t - .5) * 1.5                                    # concha ligeiramente curva
    shell = (u >= -10.5) & (u <= 10.5) & (np.abs(vv) <= half) & (half > 1.2)
    meat = shell & (np.abs(vv) <= half * .55) & (t > .3) & (t < .82)    # miolo pequeno: a concha negra domina
    rings = ((t * 21) % 3.2) < 1.0
    height = np.where(meat, 1.2 + np.clip(1 - (vv / (half + .01)) ** 2, 0, 1) * .8, np.clip(1 - (vv / (half + .01)) ** 2, 0, 1) * .6)
    mat = [['musmeat' if meat[y, x] else 'musshell' for x in range(W)] for y in range(H)]
    light = np.clip(shade(height, shell) * .8 + .25 - np.where(~meat & rings, .15, 0), 0, 1) * shell
    return render(mat, light, shell, {'musmeat': 'musshell'})

# ---------------- BRIE (cunha: casca branca aveludada por fora, miolo cremoso; ponta à direita) ----------------
def brie(seed, ang=None, W=24, H=20):
    rng = np.random.default_rng(seed + 8600)
    a = (rng.random() - .5) * 1.2 if ang is None else ang
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    u, v = axes(W, H, a)
    t = np.clip((u + 9) / 19, 0, 1)
    half = 7.0 * (1 - t) + .6
    top = (u >= -9) & (u <= 10) & (np.abs(v) <= half)
    side = (u >= -9) & (u <= 10) & (v > half) & (v <= half + 2.2 * (1 - t) + .4)
    mask = top | side
    rind = mask & ((u < -7) | side)                           # casca branca atrás e na face de lado
    ooze = top & (u > -7) & (rng.random(u.shape) > .9)        # miolo a escorrer
    light = np.where(top, .8, .5) + (rng.random(u.shape) - .5) * .1 + np.where(ooze, -.15, 0)
    mat = [['brierind' if rind[y, x] else 'brie' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(light, 0, 1) * mask, mask, {'brie': 'brierind'})

# ---------------- FRANGO TIKKA (cubo marinado, com marcas do tandoor) ----------------
def tikka(seed, W=18, H=16):
    rng = np.random.default_rng(seed + 8700)
    ys, xs, cx, cy = grid(W, H)
    dx, dy = (xs - cx) / 7, (ys - cy) / 6
    q = np.maximum(np.abs(dx), np.abs(dy)) * .7 + np.hypot(dx, dy) * .35   # cubo de cantos redondos
    n = noise(H, W, 2, rng)
    mask = q <= 1 + (n - .5) * .2
    height = np.clip(1 - q ** 2, 0, 1) ** .5 * 1.6 + (n - .5) * .5
    charred = (rng.random((H, W)) > .86) & (q < .9)            # pontos queimados
    light = np.clip(shade(height, mask) * .85 + .2 - np.where(charred, .45, 0), 0, 1) * mask
    return render([['tikka'] * W for _ in range(H)], light, mask, {})

# ---------------- GRÃO-DE-BICO (punhado de grãos redondos, com bico) ----------------
def chickpeas(seed, W=17, H=15):
    rng = np.random.default_rng(seed + 8800)
    ys, xs, cx, cy = grid(W, H)
    mask = np.zeros((H, W), bool); height = np.zeros((H, W))
    spots = [(-4.5, -3), (.5, -3.5), (5, -1.5), (-2, 2), (3, 3), (-6, 3.5)]
    rng.shuffle(spots)
    for ox, oy in spots[:4 + seed % 2]:
        e = ((xs - cx - ox) ** 2 + (ys - cy - oy) ** 2) / 6.5
        m = (e <= 1) & ~mask
        beak = np.hypot(xs - cx - ox - 1.6, ys - cy - oy + 1.6) < .9     # biquinho do grão
        mask |= m; height = np.where(m, np.sqrt(np.clip(1 - e, 0, 1)) * 1.8 + np.where(beak, .5, 0), height)
    return render([['grao'] * W for _ in range(H)], np.clip(shade(height, mask) * .8 + .26, 0, 1) * mask, mask, {})

SETS = [
    ('Tofu', tofu, ('tofu', 'flake', 40)),
    ('Char siu', char_siu, ('charsiu', 'cube', 12)),
    ('Edamame', edamame, ('edapod', 'dice', 22)),
    ('Teriyaki', teriyaki, ('teri', 'cube', 12)),
    ('Catupiry', catupiry, None),
    ('Calabresa', calabresa, ('calab', 'cube', 11)),
    ('Mexilhões', mussel, ('musmeat', 'chunk', 9)),
    ('Brie', brie, ('brie', 'shred', 40)),
    ('Tikka', tikka, ('tikka', 'cube', 12)),
    ('Grão', chickpeas, None),
]

if __name__ == '__main__':
    from gen_ingredients import drop
    f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 17)
    fs = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    ROW = 150
    sheet = Image.new('RGB', (1000, 40 + ROW * len(SETS)), (27, 20, 16))
    dr = ImageDraw.Draw(sheet)
    dr.text((20, 10), 'Inteiro / fatiado (3 variantes; nos que rodam, a 1.ª é a deitada)', fill=(240, 220, 180), font=fs)
    dr.text((760, 10), 'Ralado / picado', fill=(240, 220, 180), font=fs)
    ROT = {'Edamame', 'Mexilhões', 'Brie'}
    for i, (name, fn, gr) in enumerate(SETS):
        key = name.lower().replace(' ', '_').replace('õ', 'o').replace('ã', 'a')
        arr = [fn(1, ang=0) if name in ROT else fn(1), fn(2), fn(3)]
        g = grated(gr[0], 160 + i, gr[1], n_bits=gr[2]) if gr else None
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
            dr.text((770, y + 60), 'não se pica', fill=(200, 180, 150), font=fs)
    sheet.save(OUT + 'preview_ingredientes15.png')
    print('ok', sheet.size)
