#!/usr/bin/env python3
"""Pizza Magna: packs the sprites from gen_ingredients*.py into an atlas for the game.

Writes `assets/ingredients.js` with a PNG as a data URI (so the game still opens
straight from disk, with no server, and the canvas isn't "tainted" for getImageData)
and a frame map:  ATLAS = {src, frames: {key: [x, y, w, h]}}.

Keys:
  <id>_0..2       whole/sliced topping (3 variants), with shadow
  <id>_n          rotating topping (ROTATE): a single piece, no shadow. The game turns it
                  in quarter turns (without losing pixels) and adds the shadow afterwards
  <id>_g0..2      grated/chopped (3 variants), with shadow; honey, sweetcorn, pine nuts, Nutella, olive oil, balsamic, mayonnaise, potato sticks and sour cream have none
  sauce_<id>      sauce disc, 170 px
  crust_<id>      dough crust (ring), 170 px
  marble          320x200 marble bench
  bowl            ceramic bowl for the bench

Usage: python3 tools/build_atlas.py [preview_folder]
"""
import base64, io, os, sys
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
_argv = sys.argv[:]
sys.argv = sys.argv[:1] + [os.path.join(HERE, '..', 'preview')]     # the generators read the output folder from argv
import gen_ingredients as G
import gen_ingredients2 as G2
import gen_ingredients3 as G3
import gen_ingredients20 as G20
import gen_ingredients21 as G21
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
import gen_ingredients16 as G16
import gen_ingredients17 as G17
import gen_ingredients18 as G18
import gen_ingredients19 as G19
import gen_bases as GB
sys.argv = _argv
from gen_ingredients import R, hexs, noise, shade, render, drop

PIZZA = 170          # pizza diameter on the 320x200 logical screen
ROOT = os.path.join(HERE, '..')

# game id -> (whole(seed), grated: (ramp, kind, n_bits[, size]), function(seed) or None)
# grated cheeses: a bigger, looser handful (60x56), so 10 to 12 cover the pizza
BIG = {'W': 60, 'H': 56}

INGS = {
    'mozzarella':   (G.mozz,        G18.mozz_layer),             # grated: a thick white layer (60x56, like BIG)
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
    'pimento':      (G21.pepper_ring, ('pepperg', 'flake', 40)),   # a sliced ring (batch 21 replaced the arc)
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
    'burrata':      (G8.burrata,    ('burcream', 'shred', 130, BIG)),
    'lulas':        (G8.squid,      ('squid', 'chunk', 9)),
    'beringela':    (G8.aubergine,  ('aub', 'flake', 40)),
    'morcela':      (G8.morcela,    ('morc', 'cube', 11)),
    'nozes':        (G8.walnut,     ('walnut', 'dice', 22)),
    'batata':       (G8.potato,     ('pot', 'flake', 40)),
    'parmesao':     (G9.parmesan,   ('parm', 'shred', 130, BIG)),
    'alcachofra':   (G9.artichoke,  ('artheart', 'flake', 40)),
    'curgete':      (G9.zucchini,   ('zuc', 'flake', 40)),
    'salsicha':     (G9.sausage,    ('sals', 'cube', 11)),
    'padron':       (G9.padron,     ('padron', 'flake', 40)),
    'pinhoes':      (G9.pinenuts,   None),
    'nutella':      (G10.nutella,   None),
    'banana':       (G20.banana,    G20.banana_slices),          # whole banana; chopped = the slices
    'feta':         (G10.feta,      ('feta', 'flake', 40)),
    'farinheira':   (G10.farinheira, ('farin', 'cube', 11)),
    'ameijoas':     (G10.clam,      ('clammeat', 'chunk', 9)),
    'oregaos':      (G10.oregano,   G10.oregano_flakes),
    'prosciutto':   (G11.prosciutto, ('prosc', 'chunk', 9)),
    'azeite':       (G11.olive_oil, None),
    'balsamico':    (G11.balsamic,  None),
    'maionese':     (G11.mayonnaise, None),
    'cheddar':      (G11.cheddar,   ('ched', 'shred', 130, BIG)),
    'coentros':     (G11.coriander, ('coent', 'flake', 44)),
    'provolone':    (G12.provolone, ('prov', 'shred', 130, BIG)),
    'carne_picada': (G12.minced_beef, ('beef', 'cube', 12)),
    'cebola_roxa':  (G12.red_onion, ('redon', 'flake', 44)),
    'alecrim':      (G12.rosemary,  ('rosem', 'flake', 44)),
    'maca':         (G12.apple,     ('apple', 'cube', 11)),
    'batata_palha': (G12.straw_potato, None),
    'sao_jorge':    (G13.sao_jorge, ('sj', 'shred', 130, BIG)),
    'leitao':       (G13.leitao,    ('pork', 'cube', 12)),
    'couve_galega': (G13.couve,     ('kale', 'shred', 40)),
    'salsa':        (G13.parsley,   ('parsley', 'flake', 44)),
    'chocolate':    (G13.chocolate, ('choc', 'shred', 40)),
    'natas_azedas': (G13.sour_cream, None),
    'emmental':     (G14.emmental,  ('emm', 'shred', 130, BIG)),
    'flamengo':     (G18.flamengo_slice, ('flam', 'shred', 130, BIG)),   # whole: one big supermarket slice
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
    'brie':         (G15.brie,      ('brie', 'shred', 130, BIG)),
    'frango_tikka': (G15.tikka,     ('tikka', 'cube', 12)),
    'grao':         (G15.chickpeas, None),
    'frankfurt':    (G16.frankfurt, G16.slices),
    'vaca':         (G17.beef,      G17.beef_cubes),
    'lagosta':      (G17.lobster,   G17.lobster_chunks),
    'ribs':         (G17.rib,       G17.rib_cubes),
    'amora':        (G19.blackberry, G19.blackberry_halves),
    'mirtilo':      (G19.blueberry, G19.blueberry_halves),
    'framboesa':    (G19.raspberry, G19.raspberry_halves),
    'coxa':         (G20.drumstick, G20.drumstick_chunk),
    'cenoura':      (G21.carrot_whole, G21.carrot_slice),
    'cereja':       (G21.cherry,    G21.cherry_halves),
    'bife_osso':    (G21.bone_steak, G21.bone_steak_slice),
}
# chopped forms that lie flat (melted cheese): no drop shadow, so handfuls side by side make one even surface
NO_DROP = {'mozzarella'}
# rotating pieces: a single image, lying down (the positions are counted in the game, in ING.rot)
ROTATE = {
    'bacon': lambda: G.bacon(1, ang=0),            # 2 positions: lying, standing
    'espargos': lambda: G5.asparagus(2, ang=0),    # 4: the head points one way
    'camarao': lambda: G5.shrimp(1, ang=0),        # 4
    'figo': lambda: G5.fig(2, ang=0),              # 4: the stem points one way
    'anchovas': lambda: G6.anchovy(1, ang=0),      # 4: the tail points one way
    'pera': lambda: G6.pear(1, ang=0),             # 4: the stem points one way
    'sardinha': lambda: G7.sardine(1, ang=0),      # 4: the tail points one way
    'polvo': lambda: G7.octopus(1, ang=0),         # 4: the tentacle curls one way
    'alcachofra': lambda: G9.artichoke(1, ang=0),  # 4: the leaves open one way
    'padron': lambda: G9.padron(1, ang=0),         # 4: the stem is on one side
    'ameijoas': lambda: G10.clam(1, ang=0),        # 4: the shell hinge is on one side
    'oregaos': lambda: G10.oregano(1, ang=0),      # 4: the sprig has a stem and a tip
    'coentros': lambda: G11.coriander(1, ang=0),   # 4: the stem is on one side
    'alecrim': lambda: G12.rosemary(1, ang=0),     # 4: the sprig has a stem and a tip
    'maca': lambda: G12.apple(1, ang=0),           # 4: curved skin on one side, core cut on the other
    'sao_jorge': lambda: G13.sao_jorge(1, ang=0),  # 4: the wedge points one way
    'leitao': lambda: G13.leitao(1, ang=0),        # 4: the crackling is on one side
    'salsa': lambda: G13.parsley(1, ang=0),        # 4: the stem is on one side
    'tomilho': lambda: G14.thyme(1, ang=0),        # 4: the sprig has a stem and a tip
    'edamame': lambda: G15.edamame(1, ang=0),      # 2: the pod is the same end to end
    'mejillones': lambda: G15.mussel(1, ang=0),    # 4: the shell's beak is on one side
    'brie': lambda: G15.brie(1, ang=0),            # 4: the wedge points one way
    'frankfurt': lambda: G16.frankfurt(1, ang=0),  # 2: the same end to end
    'lagosta': lambda: G17.lobster(1, ang=0),      # 4: claws one way, tail the other
    'ribs': lambda: G17.rib(1, ang=0),             # 4: the bone sticks out at one end
    'coxa': lambda: G20.drumstick(1, ang=0),       # 4: the bone sticks out at one end
    'banana': lambda: G20.banana(1, ang=0),        # 4: a smile, a frown, or on its side
    'cenoura': lambda: G21.carrot_whole(1, ang=0), # 4: thick at one end, a point at the other
    'cereja': lambda: G21.cherry(1, ang=0),        # 4: the stem points one way
}
DOUGHS = {'fina': 'Fina', 'napo': 'Napolitana', 'alta': 'Alta'}
SAUCES = {'tomate': 'Tomate', 'natas': 'Natas', 'pesto': 'Pesto', 'sem': 'Sem molho'}


def bases():
    """Sauce and crust kept apart: discs + rings instead of every dough x sauce base."""
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
    for k in GB.DOUGHS:                                       # new doughs (gen_bases.py)
        out['crust_' + k] = GB.crust(D, k, seed=len(k))
    for k in GB.SAUCES:                                       # new sauces
        out['sauce_' + k] = GB.sauce(D, k, seed=len(k))
    return out


def bowl(W=58, H=40):
    """Ceramic bowl seen in 3/4: light rim, shaded inside, blue band."""
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
                height[y, x] = -np.sqrt(max(0, 1 - in_e[y, x])) * 3      # concave: light reversed
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
                im = gr(sd) if callable(gr) else G2.grated(gr[0], sd, gr[1], n_bits=gr[2], **(gr[3] if len(gr) > 3 else {}))
                out[f'{k}_g{j}'] = im if k in NO_DROP else drop(im)
    out.update(bases())
    out['marble'] = G.marble(320, 200, np.random.default_rng(5)).convert('RGBA')
    out['bowl'] = bowl()
    return out


def pack(imgs, width=512):
    """Simple shelf packing, from the tallest images to the shortest."""
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
    js = ('/* Generated by tools/build_atlas.py from tools/gen_ingredients*.py. Do not edit by hand. */\n'
          f'const ATLAS={{pizza:{PIZZA},frames:{{\n{fr}\n}},\nsrc:"data:image/png;base64,{b64}"}};\n')
    with open(os.path.join(ROOT, 'assets', 'ingredients.js'), 'w') as f: f.write(js)
    if len(_argv) > 1:
        os.makedirs(_argv[1], exist_ok=True); sheet.save(os.path.join(_argv[1], 'atlas.png'))
    print('ok', sheet.size, len(frames), 'frames', len(js) // 1024, 'KB')
