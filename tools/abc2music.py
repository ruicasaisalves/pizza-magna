#!/usr/bin/env python3
"""Pizza Magna: converte uma melodia em notação ABC para o formato de music.js.

A melodia vem tal e qual da partitura. O baixo e a harmonia saem das cifras ("C7", "Am"...):
o baixo toca a fundamental no primeiro tempo e a quinta nos outros, e a harmonia segura a terça do acorde.
Suporta o essencial do ABC: notas, acidentes (^ _ =) com armação de clave, oitavas (, '), durações
(2, 3/2, /2, >), pausas (z), ligaduras (-), e ignora ornamentos ({...}, !...!, H), barras e repetições.
As repetições e as voltas (1., 2.) resolvem-se à mão no texto antes de converter.

Uso: from abc2music import convert; convert(abc_corpo, key='F', unit=1, beat=2, bar=6, shift=0)
  unit: passos (colcheias) por unidade L (L:1/8 -> 1, L:1/4 -> 2)
  beat: passos por tempo (3/4 e 4/4 -> 2, 6/8 -> 3); bar: passos por compasso (3/4 -> 6, 4/4 -> 8)
  shift: transposição em meios-tons para a melodia; pickup: passos de anacruse antes do 1.º compasso"""
import re

NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
STEP = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
KEYSIG = {'C': {}, 'Am': {}, 'G': {'F': 1}, 'Em': {'F': 1}, 'D': {'F': 1, 'C': 1}, 'F': {'B': -1}, 'Dm': {'B': -1},
          'Bb': {'B': -1, 'E': -1}}

def name(midi): return NAMES[midi % 12] + str(midi // 12 - 1)

def chord_notes(ch):
    m = re.match(r'([A-G])([#b]?)(m(?!aj)|dim)?(7)?', ch)
    root = STEP[m.group(1)] + {'#': 1, 'b': -1, '': 0}[m.group(2)]
    minor = m.group(3) == 'm'
    return root, root + (3 if minor else 4), root + 7

def convert(body, key='C', unit=1, beat=2, bar=6, shift=0, pickup=0):
    sig = KEYSIG[key]
    body = re.sub(r'%.*', '', body)
    body = re.sub(r'\{[^}]*\}|![^!]*!|\[\d|\|\d|[()H~.]', '', body)       # ornamentos, voltas, ligaduras de expressão
    lead = []                                                              # lead: [midi|None, passos, [[acorde, passos]...]]
    acc = {}; cur = None; tie = False
    tok = re.compile(r'"([^"]*)"|(\^\^|\^|__|_|=)?([A-Ga-gz])([,\']*)(\d*)(/\d*)?|(>)|(-)|(\|)')
    pending_dot = None
    for m in tok.finditer(body):
        ch, a, letter, octs, num, frac, dot, tiem, bline = m.groups()
        if ch is not None:
            if re.match(r'[A-G]', ch): cur = ch
            continue
        if bline: acc = {}; continue
        if tiem: tie = True; continue
        if dot: pending_dot = len(lead) - 1; continue
        d = int(num) if num else 1
        if frac: d = d / (int(frac[1:]) if len(frac) > 1 else 2)
        steps = d * unit
        if letter == 'z': midi = None
        else:
            up = letter.upper()
            base = 60 + STEP[up] + (12 if letter.islower() else 0)
            base += 12 * octs.count("'") - 12 * octs.count(',')
            if a: acc[up + octs + letter] = {'^': 1, '^^': 2, '_': -1, '__': -2, '=': 0}[a]
            alt = acc.get(up + octs + letter, sig.get(up, 0))
            midi = base + alt + shift
        if pending_dot is not None:                                        # a>b: a fica com 3/2, b com 1/2
            lead[pending_dot][1] *= 1.5; lead[pending_dot][2][-1][1] *= 1.5; steps *= .5; pending_dot = None
        if tie and lead and lead[-1][0] == midi: lead[-1][1] += steps; lead[-1][2].append([cur, steps])   # nota ligada: o acorde pode mudar por baixo
        else: lead.append([midi, steps, [[cur, steps]]])
        tie = False
    # para passos
    out_l, out_c = [], []
    for midi, steps, segs in lead:
        n = int(round(steps))
        assert abs(steps - n) < 1e-6 and n > 0, f'duração que não cabe em colcheias: {steps}'
        out_l += [name(midi) if midi is not None else '.'] + ['-' if midi is not None else '.'] * (n - 1)
        for ch, k in segs: out_c += [ch] * int(round(k))
    bass, harm = [], []
    for i, ch in enumerate(out_c):
        if ch is None: bass.append('.'); harm.append('.'); continue
        r, third, fifth = chord_notes(ch)
        if i % beat == 0:
            bass.append(name(36 + r % 12 if (i - pickup) % bar == 0 else 36 + fifth % 12))
        else: bass.append('-')
        if i == 0 or out_c[i - 1] != ch or (i - pickup) % bar == 0: harm.append(name(60 + third % 12))
        else: harm.append('-')
    return ' '.join(out_l), ' '.join(bass), ' '.join(harm)
