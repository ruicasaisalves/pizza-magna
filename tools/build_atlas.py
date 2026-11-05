#!/usr/bin/env python3
"""Pizza Magna: junta os sprites de gen_ingredients*.py num atlas para o jogo.

Gera `assets/ingredients.js` com um PNG em data URI (assim o jogo continua a abrir
diretamente do disco, sem servidor, e o canvas não fica "sujo" para getImageData)
e um mapa de frames:  ATLAS = {src, frames: {chave: [x, y, w, h]}}.

Chaves:
  <id>_0..2       ingrediente inteiro/fatiado (3 variantes), com sombra
  <id>_n          ingrediente que roda (ROTATE): uma só peça, sem sombra. O jogo roda-a
                  em quartos de volta (sem perder píxeis) e junta a sombra depois
  <id>_g0..2      ralado/picado (3 variantes), com sombra; o mel, o milho, os pinhões, a Nutella, o azeite, o balsâmico, a maionese, a batata palha e as natas azedas não têm
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
import gen_ingredients5 as G5
import gen_ingredients6 as G6
import gen_ingredients7 as G7
import gen_ingredients8 as G8
import gen_ingredients9 as G9
import gen_ingredients10 as G10
import gen_ingredients11 as G11
import gen_ingredients12 as G12
import gen_ingredients13 as G13
import gen_ingredients14 as G14
import gen_ingredients15 as G15
import gen_bases as GB
sys.argv = _argv
from gen_ingredients import R, hexs, noise, shade, render, drop

PIZZA = 170          # diâmetro da pizza no ecrã lógico 320x200
ROOT = os.path.join(HERE, '..')

# id do jogo -> (inteiro(seed), ralado: (rampa, tipo, n_bits), função(seed) ou None)
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
    'espargos':     (G5.asparagus,  ('asp', 'flake', 40)),
    'camarao':      (G5.shrimp,     ('shrimp', 'chunk', 9)),
    'figo':         (G5.fig,        ('fig', 'cube', 11)),
    'milho':        (G5.corn,       None),
    'frango':       (G5.chicken,    ('chick', 'cube', 12)),
    'salame':       (G5.salami,     ('salami', 'cube', 11)),
    'gorgonzola':   (G5.gorgonzola, G5.gorgonzola_crumbs),
    'alheira':      (G5.alheira,    ('alh', 'cube', 11)),
    'espinafres':   (G6.spinach,    ('spin', 'flake', 44)),
    'tomate_cherry': (G6.cherry,    ('cherry', 'cube', 11)),
    'jalapenos':    (G6.jalapeno,   ('jal', 'flake', 40)),
    'anchovas':     (G6.anchovy,    ('anch', 'chunk', 9)),
    'ricotta':      (G6.ricotta,    ('ricotta', 'flake', 40)),
    'pera':         (G6.pear,       ('pear', 'cube', 11)),
    'cabra':        (G7.goat,       ('goat', 'flake', 40)),
    'alho':         (G7.garlic,     ('garlic', 'flake', 36)),
    'grelos':       (G7.grelos,     ('grelo', 'flake', 44)),
    'sardinha':     (G7.sardine,    ('sardback', 'chunk', 9)),
    'salmao':       (G7.salmon,     ('salmon', 'chunk', 9)),
    'polvo':        (G7.octopus,    ('octo', 'cube', 11)),
    'burrata':      (G8.burrata,    ('burcream', 'shred', 40)),
    'lulas':        (G8.squid,      ('squid', 'chunk', 9)),
    'beringela':    (G8.aubergine,  ('aub', 'flake', 40)),
    'morcela':      (G8.morcela,    ('morc', 'cube', 11)),
    'nozes':        (G8.walnut,     ('walnut', 'dice', 22)),
    'batata':       (G8.potato,     ('pot', 'flake', 40)),
    'parmesao':     (G9.parmesan,   ('parm', 'shred', 40)),
    'alcachofra':   (G9.artichoke,  ('artheart', 'flake', 40)),
    'curgete':      (G9.zucchini,   ('zuc', 'flake', 40)),
    'salsicha':     (G9.sausage,    ('sals', 'cube', 11)),
    'padron':       (G9.padron,     ('padron', 'flake', 40)),
    'pinhoes':      (G9.pinenuts,   None),
    'nutella':      (G10.nutella,   None),
    'banana':       (G10.banana,    ('banana', 'cube', 11)),
    'feta':         (G10.feta,      ('feta', 'flake', 40)),
    'farinheira':   (G10.farinheira, ('farin', 'cube', 11)),
    'ameijoas':     (G10.clam,      ('clammeat', 'chunk', 9)),
    'oregaos':      (G10.oregano,   G10.oregano_flakes),
    'prosciutto':   (G11.prosciutto, ('prosc', 'chunk', 9)),
    'azeite':       (G11.olive_oil, None),
    'balsamico':    (G11.balsamic,  None),
    'maionese':     (G11.mayonnaise, None),
    'cheddar':      (G11.cheddar,   ('ched', 'shred', 40)),
    'coentros':     (G11.coriander, ('coent', 'flake', 44)),
    'provolone':    (G12.provolone, ('prov', 'shred', 40)),
    'carne_picada': (G12.minced_beef, ('beef', 'cube', 12)),
    'cebola_roxa':  (G12.red_onion, ('redon', 'flake', 44)),
    'alecrim':      (G12.rosemary,  ('rosem', 'flake', 44)),
    'maca':         (G12.apple,     ('apple', 'cube', 11)),
    'batata_palha': (G12.straw_potato, None),
    'sao_jorge':    (G13.sao_jorge, ('sj', 'shred', 40)),
    'leitao':       (G13.leitao,    ('pork', 'cube', 12)),
    'couve_galega': (G13.couve,     ('kale', 'shred', 40)),
    'salsa':        (G13.parsley,   ('parsley', 'flake', 44)),
    'chocolate':    (G13.chocolate, ('choc', 'shred', 40)),
    'natas_azedas': (G13.sour_cream, None),
    'emmental':     (G14.emmental,  ('emm', 'shred', 40)),
    'flamengo':     (G14.flamengo,  ('flam', 'shred', 40)),
    'kebab':        (G14.kebab,     ('kebab', 'cube', 12)),
    'tomilho':      (G14.thyme,     ('thyme', 'flake', 44)),
    'pimenta':      (G14.peppercorns, ('pepcorn', 'flake', 50)),
    'marmelada':    (G14.marmelada, ('quince', 'cube', 11)),
    'trufa':        (G14.truffle,   ('truf', 'flake', 44)),
    'tofu':         (G15.tofu,      ('tofu', 'flake', 40)),
    'char_siu':     (G15.char_siu,  ('charsiu', 'cube', 12)),
    'edamame':      (G15.edamame,   ('edapod', 'dice', 22)),
    'frango_teriyaki': (G15.teriyaki, ('teri', 'cube', 12)),
    'catupiry':     (G15.catupiry,  None),
    'calabresa':    (G15.calabresa, ('calab', 'cube', 11)),
    'mejillones':   (G15.mussel,    ('musmeat', 'chunk', 9)),
    'brie':         (G15.brie,      ('brie', 'shred', 40)),
    'frango_tikka': (G15.tikka,     ('tikka', 'cube', 12)),
    'grao':         (G15.chickpeas, None),
}
# peças que rodam: uma só imagem, deitada (as posições contam-se no jogo, em ING.rot)
ROTATE = {
    'bacon': lambda: G.bacon(1, ang=0),            # 2 posições: deitado, de pé
    'espargos': lambda: G5.asparagus(2, ang=0),    # 4: a cabeça aponta para um lado
    'camarao': lambda: G5.shrimp(1, ang=0),        # 4
    'figo': lambda: G5.fig(2, ang=0),              # 4: o pé aponta para um lado
    'anchovas': lambda: G6.anchovy(1, ang=0),      # 4: a cauda aponta para um lado
    'pera': lambda: G6.pear(1, ang=0),             # 4: o pé aponta para um lado
    'sardinha': lambda: G7.sardine(1, ang=0),      # 4: a cauda aponta para um lado
    'polvo': lambda: G7.octopus(1, ang=0),         # 4: o tentáculo enrola para um lado
    'alcachofra': lambda: G9.artichoke(1, ang=0),  # 4: as folhas abrem para um lado
    'padron': lambda: G9.padron(1, ang=0),         # 4: o pé fica de um lado
    'ameijoas': lambda: G10.clam(1, ang=0),        # 4: a dobradiça da concha fica de um lado
    'oregaos': lambda: G10.oregano(1, ang=0),      # 4: o raminho tem pé e ponta
    'coentros': lambda: G11.coriander(1, ang=0),   # 4: o pé fica de um lado
    'alecrim': lambda: G12.rosemary(1, ang=0),     # 4: o raminho tem pé e ponta
    'maca': lambda: G12.apple(1, ang=0),           # 4: casca curva de um lado, corte do caroço do outro
    'sao_jorge': lambda: G13.sao_jorge(1, ang=0),  # 4: a cunha aponta para um lado
    'leitao': lambda: G13.leitao(1, ang=0),        # 4: o courato fica de um lado
    'salsa': lambda: G13.parsley(1, ang=0),        # 4: o pé fica de um lado
    'tomilho': lambda: G14.thyme(1, ang=0),        # 4: o raminho tem pé e ponta
    'edamame': lambda: G15.edamame(1, ang=0),      # 2: a vagem é igual de ponta a ponta
    'mejillones': lambda: G15.mussel(1, ang=0),    # 4: o bico da concha fica de um lado
    'brie': lambda: G15.brie(1, ang=0),            # 4: a cunha aponta para um lado
}
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
    for k in GB.DOUGHS:                                       # massas novas (gen_bases.py)
        out['crust_' + k] = GB.crust(D, k, seed=len(k))
    for k in GB.SAUCES:                                       # molhos novos
        out['sauce_' + k] = GB.sauce(D, k, seed=len(k))
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
            out[f'{k}_n'] = ROTATE[k]()
        else:
            for j, s in enumerate((1, 2, 3)):
                out[f'{k}_{j}'] = drop(fn(s))
        if gr:
            for j in range(3):
                sd = 40 + j * 17 + len(k)
                out[f'{k}_g{j}'] = drop(gr(sd) if callable(gr) else G2.grated(gr[0], sd, gr[1], n_bits=gr[2]))
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
