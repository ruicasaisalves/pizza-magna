#!/usr/bin/env python3
"""Pizza Magna: junta os sprites de gen_ingredients*.py num atlas para o jogo.

Gera `assets/ingredients.js` com um PNG em data URI (assim o jogo continua a abrir
diretamente do disco, sem servidor, e o canvas não fica "sujo" para getImageData)
e um mapa de frames:  ATLAS = {src, frames: {chave: [x, y, w, h]}}.

Chaves:
  <id>_0..2       ingrediente inteiro/fatiado (3 variantes), com sombra
  <id>_r0..7      ingrediente que roda (ROTATE): uma só peça em 8 orientações de 22,5°,
                  desenhada de raiz em cada ângulo (rodar os píxeis estragava o desenho)
  <id>_g0..2      ralado/picado (3 variantes), com sombra; o mel não tem
  sauce_<id>      disco de molho, 170 px
  crust_<id>      bordo da massa (anel), 170 px
  marble          bancada de mármore 320x200
  bowl            taça de cerâmica para a bancada

Uso: python3 tools/build_atlas.py [pasta_de_prévia]
"""
import base64, io, os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv = sys.argv[:]
sys.argv = sys.argv[:1] + [os.path.join(HERE, '..', 'preview')]     # os geradores leem a pasta de saída de argv
import gen_ingredients as G
import gen_ingredients2 as G2
import gen_ingredients3 as G3
import gen_ingredients4 as G4
sys.argv = _argv
from gen_ingredients import R, hexs, noise, shade, render, drop

PIZZA = 170          # diâmetro da pizza no ecrã lógico 320x200
ROOT = os.path.join(HERE, '..')

# id do jogo -> (inteiro(seed), (rampa, tipo, n_bits) do ralado ou None)
INGS = {
    'mozzarella':   (G.mozz,        ('mozz', 'shred', 40)),
    'queijo_serra': (G4.serra,      ('serra', 'flake', 40)),
    'fiambre':      (G2.ham,        ('ham', 'cube', 12)),
    'pepperoni':    (G2.pepperoni,  ('pep', 'cube', 11)),
    'chourico':     (G2.chourico,   ('chour', 'cube', 11)),
    'presunto':     (G3.presunto,   ('pros', 'chunk', 9)),
    'bacon':        (G.bacon,       ('meat', 'cube', 11)),
    'atum':         (G2.tuna,       ('tuna', 'chunk', 9)),
    'bacalhau':     (G4.cod,        ('cod', 'chunk', 9)),
    'cogumelos':    (G2.mushroom,   ('gill', 'flake', 40)),
    'azeitonas':    (G3.olive,      ('olive', 'flake', 40)),
    'cebola':       (G3.onion,      ('onion', 'flake', 44)),
    'pimento':      (G3.pepper,     ('pepper', 'flake', 40)),
    'tomate':       (G.tomato,      ('flesh', 'cube', 11)),
    'rucula':       (G4.rocket,     ('rocket', 'flake', 44)),
    'manjericao':   (G3.basil,      ('basil', 'flake', 46)),
    'piripiri':     (G4.chili,      ('chili', 'flake', 40)),
    'ananas':       (G3.pineapple,  ('pine', 'cube', 11)),
    'mel':          (G4.honey,      None),
    'ovo':          (G4.egg,        ('eggw', 'chunk', 9)),
}
# uma só forma, em 8 ângulos (0°..157,5°); a tira é simétrica a 180°
ROTATE = {'bacon': lambda a: G.bacon(1, W=36, H=36, ang=a)}
DOUGHS = {'fina': 'Fina', 'napo': 'Napolitana', 'alta': 'Alta'}
SAUCES = {'tomate': 'Tomate', 'natas': 'Natas', 'pesto': 'Pesto', 'sem': 'Sem molho'}


def bases():
    """Molho e bordo em separado: 4 discos + 3 anéis em vez de 12 bases inteiras."""
    out = {}
    D = PIZZA
    c = (D - 1) / 2
    ys, xs = np.mgrid[0:D, 0:D]
    r = np.hypot(xs - c, ys - c) / (D / 2 - .5)
    thin = min(G4.DOUGH.values())
    for k, name in SAUCES.items():
        a = np.array(G4.base(D, 'Fina', name, seed=7 + len(k)))
        a[r > 1 - thin + .02, 3] = 0
        out['sauce_' + k] = Image.fromarray(a)
    for k, name in DOUGHS.items():
        a = np.array(G4.base(D, name, 'Tomate', seed=3 + len(k)))
        a[r <= 1 - G4.DOUGH[name], 3] = 0
        out['crust_' + k] = Image.fromarray(a)
    return out


def bowl(W=58, H=40):
    """Taça de cerâmica vista a 3/4: aro claro, interior em sombra, faixa azul."""
    R.update({
        'glaze': hexs(['#8f8676', '#b7ae9c', '#d8d0bf', '#eee8db', '#fbf8f1']),
        'inside': hexs(['#a69d8c', '#c4bcaa', '#dcd5c6', '#ece6da']),
        'stripe': hexs(['#1d3c6a', '#2c5894', '#4478b8', '#6c9ad2']),
    })
    ys, xs = np.mgrid[0:H, 0:W]
    cx = (W - 1) / 2
    top_cy, rx, ry = 13.5, W / 2 - .6, 12.5
    out_e = ((xs - cx) / rx) ** 2 + ((ys - top_cy) / ry) ** 2
    body = (np.abs(xs - cx) <= rx * np.sqrt(np.clip(1 - ((ys - top_cy - 6) / (H - top_cy - 6)) ** 2, 0, 1))) & (ys >= top_cy)
    mask = (out_e <= 1) | body
    in_e = ((xs - cx) / (rx - 4)) ** 2 + ((ys - top_cy) / (ry - 3.5)) ** 2
    height = np.zeros((H, W))
    mat = [['glaze'] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if not mask[y, x]: continue
            if in_e[y, x] <= 1:
                mat[y][x] = 'inside'
                height[y, x] = -np.sqrt(max(0, 1 - in_e[y, x])) * 3      # côncavo: luz ao contrário
            elif out_e[y, x] <= 1:
                height[y, x] = 1.2
            else:
                t = (x - cx) / rx
                height[y, x] = np.sqrt(max(0, 1 - t * t)) * 3
                if 25 <= y <= 28: mat[y][x] = 'stripe'
    light = np.clip(shade(height, mask) * .9 + .2, 0, 1) * mask
    return render(mat, light, mask, {'inside': 'glaze', 'stripe': 'stripe'})


def sprites():
    out = {}
    for k, (fn, gr) in INGS.items():
        if k in ROTATE:
            for j in range(8):
                out[f'{k}_r{j}'] = drop(ROTATE[k](j * np.pi / 8))
        else:
            for j, s in enumerate((1, 2, 3)):
                out[f'{k}_{j}'] = drop(fn(s))
        if gr:
            ramp, kind, n = gr
            for j in range(3):
                out[f'{k}_g{j}'] = drop(G2.grated(ramp, 40 + j * 17 + len(k), kind, n_bits=n))
    out.update(bases())
    out['marble'] = G.marble(320, 200, np.random.default_rng(5)).convert('RGBA')
    out['bowl'] = bowl()
    return out


def pack(imgs, width=512):
    """Empacotamento simples em prateleiras, das imagens mais altas para as mais baixas."""
    order = sorted(imgs, key=lambda k: (-imgs[k].height, -imgs[k].width))
    x = y = shelf = 0
    frames = {}
    for k in order:
        w, h = imgs[k].size
        if x + w > width: x, y, shelf = 0, y + shelf + 1, 0
        frames[k] = [x, y, w, h]
        x += w + 1; shelf = max(shelf, h)
    sheet = Image.new('RGBA', (width, y + shelf), (0, 0, 0, 0))
    for k, (x, y, w, h) in frames.items(): sheet.paste(imgs[k], (x, y))
    return sheet, frames


if __name__ == '__main__':
    imgs = sprites()
    sheet, frames = pack(imgs)
    buf = io.BytesIO(); sheet.save(buf, 'PNG', optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    os.makedirs(os.path.join(ROOT, 'assets'), exist_ok=True)
    fr = ',\n'.join(f'  {k}:[{",".join(map(str, v))}]' for k, v in sorted(frames.items()))
    js = ('/* Gerado por tools/build_atlas.py a partir de tools/gen_ingredients*.py. Não editar à mão. */\n'
          f'const ATLAS={{pizza:{PIZZA},frames:{{\n{fr}\n}},\nsrc:"data:image/png;base64,{b64}"}};\n')
    with open(os.path.join(ROOT, 'assets', 'ingredients.js'), 'w') as f: f.write(js)
    if len(_argv) > 1:
        os.makedirs(_argv[1], exist_ok=True); sheet.save(os.path.join(_argv[1], 'atlas.png'))
    print('ok', sheet.size, len(frames), 'frames', len(js) // 1024, 'KB')
