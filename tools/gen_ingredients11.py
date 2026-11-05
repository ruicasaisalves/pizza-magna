#!/usr/bin/env python3
"""Pizza Magna: décimo primeiro lote em pixel detalhado. Prosciutto, azeite, balsâmico,
maionese, cheddar e coentros, com a forma picada pela regra de docs/ingredientes.md.
Mesmo método de gen_ingredients.py (ver tools/CLAUDE.md).

Azeite e balsâmico são fios e gotas (como o mel); a maionese espalha-se (como a Nutella).
Nenhum dos três se pica. Os coentros têm frente (pé e folha) e aceitam `ang`.
Uso: python3 tools/gen_ingredients11.py <pasta>"""
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
    'prosc': hexs(['#8a3a44', '#b45a62', '#d47c80', '#eca2a2', '#fcc8c4']),
    'proscfat': hexs(['#d8c4bc', '#eedcd4', '#fbf2ee', '#ffffff']),
    'oil': hexs(['#5e5a0c', '#8e8818', '#bcb030', '#e2d660', '#fff6aa']),
    'balsa': hexs(['#120808', '#2a1010', '#441a16', '#6a2e22', '#b07a5c']),
    'mayo': hexs(['#c4b062', '#dccc86', '#eee2aa', '#f9f2d2', '#fffdf2']),
    'ched': hexs(['#a04a08', '#c86812', '#e88a22', '#f6aa44', '#ffd07e']),
    'coent': hexs(['#0e3a14', '#1a5a1e', '#2c7e2a', '#4aa23e', '#7cc664']),
    'coentstem': hexs(['#2e5a1e', '#4a8030', '#70a84c']),
})

# ---------------- PROSCIUTTO (fatia fina e drapeada, rosada, com faixa de gordura) ----------------
def prosciutto(seed, W=30, H=24):
    """diferente do presunto: mais fino e largo, rosa-claro e quase translúcido, dobrado em pregas,
    com uma faixa de gordura branca contínua num dos lados (o presunto é vermelho-escuro com veios)"""
    rng = np.random.default_rng(seed + 5400)
    u, v = axes(W, H, (rng.random() - .5) * 1.0)
    ph = rng.random() * 6.28
    vv = v - 1.6 * np.sin(u * .28 + ph)
    half = 7.2 + .9 * np.sin(u * .45 + ph * 2)
    n = noise(H, W, 3, rng)
    mask = (np.abs(u) / 13) ** 4 + (np.abs(vv) / (half + (n - .5) * .6)) ** 4 <= 1       # retângulo de cantos redondos
    folds = np.sin(u * .42 + vv * .18 + ph) * .7 + np.sin(u * .9 + ph * 3) * .15   # pregas largas e suaves
    height = folds + np.clip(1 - (vv / half) ** 2, 0, 1) * .8
    fat = vv > half - 2.4 + (n - .5) * 1.2                     # faixa de gordura num dos lados
    mat = [['proscfat' if mask[y, x] and fat[y, x] else 'prosc' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .75 + .3, 0, 1) * mask, mask, {'proscfat': 'prosc'})

# ---------------- fios e gotas (azeite, balsâmico) ----------------
def drizzle(ramp, seed, base, W=30, H=24, thick=1, drops=3, drop_r=(1.4, 2.2)):
    """fio que serpenteia pela pizza, com sombra por baixo e brilho por cima, e algumas gotas"""
    rng = np.random.default_rng(seed + base)
    rp = R[ramp]
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); px = img.load()
    x, y, a = 2.5, H / 2 + (rng.random() - .5) * 6, (rng.random() - .5) * 1.2
    pts = []
    while 1 < x < W - 2 and len(pts) < 160:
        a += (rng.random() - .5) * .5 - (y - H / 2) * .012       # vira devagar, sem fugir da caixa
        x += np.cos(a) * .35 + .25; y += np.sin(a) * .5
        pts.append((x, y))
    for (x, y) in pts:
        X, Y = int(round(x)), int(round(y))
        for dy in range(-thick, thick + 2):
            if 0 <= X < W and 0 <= Y + dy < H:
                k = 0 if dy > thick - 1 else (len(rp) - 2 if dy == -thick else 2)    # sombra em baixo, brilho em cima
                px[X, Y + dy] = rp[k] + (255,)
    for (x, y) in pts[::23]:                                    # pontos de brilho ao longo do fio
        X, Y = int(round(x)), int(round(y)) - thick
        if 0 <= X < W and 0 <= Y < H: px[X, Y] = rp[-1] + (255,)
    for _ in range(drops):                                      # gotas soltas
        cx, cy = rng.uniform(4, W - 4), rng.uniform(4, H - 4)
        r = rng.uniform(*drop_r)
        for yy in range(int(cy - r - 1), int(cy + r + 2)):
            for xx in range(int(cx - r - 1), int(cx + r + 2)):
                if not (0 <= xx < W and 0 <= yy < H): continue
                d = np.hypot(xx - cx, yy - cy) / r
                if d > 1: continue
                lit = .55 - (xx - cx + yy - cy) / r * .3
                px[xx, yy] = rp[int(np.clip(round(lit * (len(rp) - 1)), 0, len(rp) - 1))] + (255,)
                if d > .75 and (xx - cx + yy - cy) > 0: px[xx, yy] = rp[0] + (255,)
        X, Y = int(cx - r * .4), int(cy - r * .4)
        if 0 <= X < W and 0 <= Y < H: px[X, Y] = rp[-1] + (255,)
    return img

def olive_oil(seed):
    """azeite: fio fino e gotas largas, amarelo-esverdeado"""
    img = drizzle('oil', seed, 5500, thick=1, drops=3, drop_r=(1.8, 2.8))
    # um pouco translúcido: o corpo do azeite deixa ver a pizza; os brilhos ficam opacos
    px = img.load(); top = R['oil'][-1]
    for y in range(img.height):
        for x in range(img.width):
            c = px[x, y]
            if c[3] and c[:3] != top: px[x, y] = c[:3] + (175,)
    return img

def balsamic(seed):
    """balsâmico: fio fino e escuro, quase preto, com muitas gotinhas"""
    return drizzle('balsa', seed, 5600, thick=0, drops=6, drop_r=(1.0, 1.7))

# ---------------- MAIONESE (colherada espalhada, como a Nutella) ----------------
def mayonnaise(seed, W=24, H=19):
    rng = np.random.default_rng(seed + 5700)
    ys, xs, cx, cy = grid(W, H)
    dx, dy = (xs - cx) / (W / 2 - 1.2), (ys - cy) / (H / 2 - 1.2)
    ang = np.arctan2(dy, dx); a, b = rng.random(2) * 6.28
    r = np.hypot(dx, dy)
    rr = r / (1 + .1 * np.sin(ang * 3 + a) + .07 * np.sin(ang * 5 + b))
    mask = rr <= 1
    swirl = np.sin(ang + r * 8 + a) * .4
    height = np.clip(1 - rr ** 2, 0, 1) ** .5 * 1.5 + swirl * np.clip(1 - rr, 0, 1)
    mat = [['mayo'] * W for _ in range(H)]
    return render(mat, np.clip(shade(height, mask) * .9 + .2, 0, 1) * mask, mask, {})

# ---------------- CHEDDAR (fatia quadrada a derreter, cor de laranja) ----------------
def cheddar(seed, W=26, H=24):
    rng = np.random.default_rng(seed + 5800)
    u, v = axes(W, H, (rng.random() - .5) * 1.2)
    n = noise(H, W, 3, rng)
    # quadrado de cantos redondos que escorre: bordos ondulados
    q = np.maximum(np.abs(u), np.abs(v)) + np.clip(np.minimum(np.abs(u), np.abs(v)) - 5.5, 0, None) * .5
    mask = q <= 9.4 + (n - .5) * 1.6
    n2 = noise(H, W, 2, rng)
    height = np.clip(1 - (q / 10) ** 2, 0, 1) ** .25 * .9 + (n2 - .5) * .15     # fatia lisa, só desce no bordo
    mat = [['ched'] * W for _ in range(H)]
    img = render(mat, np.clip(shade(height, mask) * .6 + .38, 0, 1) * mask, mask, {})
    px = img.load()
    for _ in range(3):                                          # bolhas de queijo derretido
        x, y = int(W / 2 + (rng.random() - .5) * 9), int(H / 2 + (rng.random() - .5) * 8)
        if mask[y, x] and mask[y - 1, x - 1]:
            px[x, y] = R['ched'][1] + (255,); px[x - 1, y - 1] = R['ched'][4] + (255,)
    return img

# ---------------- COENTROS (raminho de folhas recortadas; pé à esquerda) ----------------
def coriander(seed, ang=None, W=24, H=22):
    rng = np.random.default_rng(seed + 5900)
    a = (rng.random() - .5) * 1.2 if ang is None else ang
    if ang is not None and abs(np.sin(ang)) > .5: W, H = H, W
    u, v = axes(W, H, a)
    stem = (np.abs(v - (u + 11) * .02) <= .7) & (u >= -11) & (u <= 1)
    mask = stem.copy(); height = np.where(stem, .6, 0.)
    # três folíolos redondos e recortados no fim do pé (o do meio maior)
    for (lu, lv, rr) in ((4.5, 0, 5.2), (0, -5.2, 3.9), (0, 5.2, 3.9)):
        d = np.hypot(u - lu, v - lv)
        lob = rr * (1 + .14 * np.sin(np.arctan2(v - lv, u - lu) * 7 + seed))     # bordo serrilhado
        m = d <= lob
        mask |= m; height = np.maximum(height, np.where(m, np.sqrt(np.clip(1 - (d / lob) ** 2, 0, 1)) * 1.3, 0))
    veins = (np.abs(v) < .5) & (u > 0) | (np.abs(np.abs(v) - (u * -1.1)) < .5) & (u < 0) & (u > -4.5)
    mat = [['coentstem' if stem[y, x] or (mask[y, x] and veins[y, x]) else 'coent' for x in range(W)] for y in range(H)]
    return render(mat, np.clip(shade(height, mask) * .8 + .24, 0, 1) * mask, mask, {'coentstem': 'coent'})

SETS = [
    ('Prosciutto', prosciutto, ('prosc', 'chunk', 9)),
    ('Azeite', olive_oil, None),
    ('Balsâmico', balsamic, None),
    ('Maionese', mayonnaise, None),
    ('Cheddar', cheddar, ('ched', 'shred', 40)),
    ('Coentros', coriander, ('coent', 'flake', 44)),
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
        key = name.lower().replace('â', 'a')
        arr = [fn(s) for s in (1, 2, 3)]
        g = grated(gr[0], 120 + i, gr[1], n_bits=gr[2]) if gr else None
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
    sheet.save(OUT + 'preview_ingredientes11.png')
    print('ok', sheet.size)
