#!/usr/bin/env python3
"""Pizza Magna — personagens a partir das camadas do pack Heroes99 (comprado,
licença comercial do autor, partilhada com o Titan Royale).

As camadas NÃO são copiadas para este repositório: o script lê-as do clone do
Titan Royale (assets/heroes_layers/<Classe>/) e escreve só as folhas finais em
assets/characters/. Por isso este repositório tem de ficar PRIVADO.

Uso:
    python3 tools/gen_characters.py /caminho/para/titan-royale [--preview saida.png]

Cada personagem: camadas pela ordem do Titan Royale, SEM ARMA; pele trocada
pela rampa de SKINS; roupa recolorida pela luminância para a cor pedida (o
contorno fica). O chef leva um chapéu desenhado aqui, alinhado ao topo do
cabelo em cada frame.

Folha de saída: 2 linhas (parado 6 frames, a andar 8 frames), células de
CW x CH, personagem virada para a direita (o jogo espelha para a esquerda).
"""
import argparse
import os
import sys
from PIL import Image

CELL_W, CELL_H = 100, 40      # grelha da folha original (8x17)
CROP_X0, CW, CH = 20, 40, 40  # janela útil dentro da célula
ANIMS = {"idle": (0, 6), "run": (2, 8)}   # linha da folha original, nº de frames
OUTLINE = (24, 24, 24)
INK = 40

SKINS = {
    "dark": ["3a1d0f", "5b2b14", "8b4e25"],
    "medium": ["60341f", "96593a", "c28a5e"],
    "light": ["885038", "d08860", "f8d098"],
}

# nome -> (classe base, cabelo, pele, roupa de baixo, roupa de cima, chapéu de chef, olhos de)
# cabelo: 1=ruivo escuro 2=verde-água 3=louro 4=azul 5=lilás 6=rosa 7=castanho escuro 8=castanho
CHARACTERS = {
    "cliente_1": ("Barbaro", 8, "light", "#3d8ee0", "#3d8ee0", False, "Bruto"),          # túnica azul (família)
    "cliente_2": ("Necromante", 3, "medium", "#f08a3b", "#f08a3b", False, "Lanceiro"),   # casaco laranja (estudante)
    "chef":      ("Sacerdote", 7, "medium", "#f4f1ea", "#f4f1ea", True, "Tanque_v2"),    # bata branca + chapéu
}

eyes = None

HAT = [
    "..oooooooo..",
    ".oWWWWWWWWo.",
    "oWWWWWWWWWWo",
    "oWWWWWWWWwWo",
    "oWWWWWWWWwWo",
    ".oWWWWWWWwo.",
    ".owwwwwwwwo.",
    ".oWWWWWWWWo.",
    ".oooooooooo.",
]
HAT_COL = {"o": OUTLINE, "W": (248, 246, 240), "w": (214, 206, 192)}


def _hex(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lum(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def reskin(img, tone):
    px = img.load()
    cols = sorted({px[x, y][:3] for x in range(img.width) for y in range(img.height)
                   if px[x, y][3] > 0 and px[x, y][:3] != OUTLINE}, key=lum)
    if len(cols) != 3:
        sys.exit(f"pele com {len(cols)} tons (esperava 3) — parei")
    mp = {c: _hex(h) for c, h in zip(cols, SKINS[tone])}
    out = img.copy()
    op = out.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a and (r, g, b) in mp:
                op[x, y] = mp[(r, g, b)] + (a,)
    return out


def colorize(img, target):
    """Roupa na cor `target`: cada tom pela sua luminância, entre uma sombra
    escura e um brilho claro da mesma cor. O contorno (lum < INK) fica."""
    t = _hex(target)
    dark = tuple(round(v * .38) for v in t)
    light = tuple(round(v + (255 - v) * .45) for v in t)
    px = img.load()
    ls = {px[x, y][:3]: lum(px[x, y][:3]) for x in range(img.width) for y in range(img.height) if px[x, y][3]}
    body = [v for v in ls.values() if v >= INK]
    if not body:
        return img
    lo, hi = min(body), max(body)
    out = img.copy()
    op = out.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if not a or ls[(r, g, b)] < INK:
                continue
            k = (ls[(r, g, b)] - lo) / (hi - lo) if hi > lo else 1.0
            # rampa em 3 troços: sombra -> cor -> brilho
            if k < .5:
                c = tuple(round(dark[i] + (t[i] - dark[i]) * k * 2) for i in range(3))
            else:
                c = tuple(round(t[i] + (light[i] - t[i]) * (k - .5) * 2) for i in range(3))
            op[x, y] = c + (a,)
    return out


def compose(layers, cls, hair, skin, bot, top, eye):
    base = Image.new("RGBA", (800, 680), (0, 0, 0, 0))
    hair_only = Image.new("RGBA", (800, 680), (0, 0, 0, 0))
    for n in ("skin", "face", f"hair_bot_c{hair}", "cloth_bot_c1", f"hair_top_c{hair}", "cloth_top_c1"):
        p = os.path.join(layers, cls, n + ".png")
        if not os.path.exists(p):
            continue
        layer = Image.open(p).convert("RGBA")
        if n == "skin":
            layer = reskin(layer, skin)
        if n == "face" and eyes:
            layer = eyes.recolor_face(layer, eye)
        if n.startswith("cloth_bot"):
            layer = colorize(layer, bot)
        if n.startswith("cloth_top"):
            layer = colorize(layer, top)
        if n.startswith("hair"):
            hair_only.alpha_composite(layer)
        base.alpha_composite(layer)
    return base, hair_only


def put_hat(cell, hair_cell):
    bb = hair_cell.getbbox()
    if not bb:
        return cell
    # centro do cabelo nas 3 linhas de cima: o chapéu assenta aí
    px = hair_cell.load()
    xs = [x for y in range(bb[1], min(bb[1] + 4, bb[3])) for x in range(bb[0], bb[2]) if px[x, y][3]]
    cx = round(sum(xs) / len(xs)) if xs else (bb[0] + bb[2]) // 2
    ox, oy = cx - len(HAT[0]) // 2, bb[1] + 4 - len(HAT)
    cp = cell.load()
    for j, row in enumerate(HAT):
        for i, ch in enumerate(row):
            if ch in HAT_COL and 0 <= ox + i < cell.width and 0 <= oy + j < cell.height:
                cp[ox + i, oy + j] = HAT_COL[ch] + (255,)
    return cell


def build(layers, cls, hair, skin, bot, top, hat, eye):
    sheet, hair_layer = compose(layers, cls, hair, skin, bot, top, eye)
    frames = max(n for _, n in ANIMS.values())
    out = Image.new("RGBA", (CW * frames, CH * len(ANIMS)), (0, 0, 0, 0))
    for r, (row, n) in enumerate(ANIMS.values()):
        for f in range(n):
            box = (f * CELL_W + CROP_X0, row * CELL_H, f * CELL_W + CROP_X0 + CW, row * CELL_H + CELL_H)
            cell = sheet.crop(box)
            if hat:
                # espaço por cima para o chapéu: desce a personagem 0 px, o chapéu cabe na célula (topo ~6)
                cell = put_hat(cell, hair_layer.crop(box))
            out.alpha_composite(cell, (f * CW, r * CH))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("titan", help="clone do titan-royale (tem assets/heroes_layers)")
    ap.add_argument("-o", "--out", default=os.path.join(os.path.dirname(__file__), "..", "assets", "characters"))
    ap.add_argument("--preview")
    args = ap.parse_args()
    layers = os.path.join(args.titan, "assets", "heroes_layers")
    global eyes
    sys.path.insert(0, os.path.join(args.titan, "tools"))
    try:
        import eyes as _eyes  # olhos do Titan Royale (precisa de numpy)
        eyes = _eyes
    except ImportError:
        print("aviso: sem tools/eyes.py ou numpy, os olhos ficam os do pack")
    os.makedirs(args.out, exist_ok=True)
    sheets = {}
    for name, spec in CHARACTERS.items():
        im = build(layers, *spec)
        im.save(os.path.join(args.out, name + ".png"))
        sheets[name] = im
    print("escrito", ", ".join(sheets), "em", os.path.abspath(args.out))
    if args.preview:
        k = 5
        g = Image.new("RGBA", (CW * 8 * k, CH * 2 * k * len(sheets)), (76, 48, 28, 255))
        for i, im in enumerate(sheets.values()):
            g.alpha_composite(im.resize((im.width * k, im.height * k), Image.NEAREST), (0, i * CH * 2 * k))
        g.save(args.preview)


if __name__ == "__main__":
    main()
