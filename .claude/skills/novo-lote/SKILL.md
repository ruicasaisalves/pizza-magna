---
name: novo-lote
description: Adds a batch of new toppings to Pizza Magna (detailed pixel sprites, atlas, game data, translations, weights, combos, docs and test). Use when the user asks for more toppings ("faz mais 6", "acrescenta X e Y", "add 6 more"), or to fix the drawing of an existing topping.
---

# New batch of toppings

Reply to the user in the language they write in (usually Portuguese). Docs, commit messages and code comments are in English.

## 0. Branch

If the working branch's PR has already been merged, restart the branch from `main`:
`git fetch origin main && git checkout -B <branch> origin/main`.

## 1. Read the method

Read `tools/CLAUDE.md`. It has the drawing method, the rotation rules (`ING.rot` 1, 2 or 4), the chopped forms and the atlas keys.

## 2. Choose

- Take toppings from `docs/ingredients.md` (those without ✓★), unless the user names them.
- Vary the categories.
- Decide for each one whether it rotates (1, 2 or 4 positions) and what its chopped form is.

## 3. Draw: `tools/gen_ingredientsN.py`

- Copy the structure of the latest generator (`tools/gen_ingredients16.py` or `15`): the same header, `R.update`, one function per topping, `SETS` and the `__main__` that makes the preview sheet.
- Make the preview and **look at it** with Read before going on. If a piece isn't recognisable at first sight, redraw it. The most common mistakes are:
  - a jagged outline that looks like a leaf;
  - details in the same tone that disappear;
  - a shape that is too small.

## 4. Atlas: `tools/build_atlas.py`

1. `import gen_ingredientsN as GN`, next to the other imports.
2. In `INGS`: `'id': (GN.function, ('ramp', 'kind', n_bits) | function | None)`. Grated cheeses use `('ramp', 'shred', 130, BIG)`.
3. If it rotates, add it to `ROTATE`: `'id': lambda: GN.function(1, ang=0)`, with a comment on the number of positions.
4. Run `python3 tools/build_atlas.py`. This regenerates `assets/ingredients.js`, which is never edited by hand.

## 5. Game: `index.html`

- Use grep to find the blocks; don't read the whole `index.html`.
- **`ING`:** the entry goes in its pack's block.
  - Format: `id:{n:'Name',c:cost,t:[tags],pack:'base'|'local'|'gourmet',rot:N}`. Only set `rot` if it is above 1.
  - **Tags:** `queijo carne peixe vegetal doce picante classico portugues gourmet`.
  - **Packs:** `base` for cheap and common; `local` (Local Market) for Portuguese and fish; `gourmet` (Delicatessen) for expensive and luxury.
  - **Cost per portion:** 0.02 (garlic) to 0.20 (burrata).
- **`GRAMS`:** weight in grams of one whole piece (chopped weighs `GRATED_W`, 70%; a grated cheese in `BIG_SHRED` weighs 150%). The test fails if it is missing.
- **`COMBOS`:** one positive combo per new topping, and one clash per batch.
  - Format: `{id, n, req:[ids or 's:sauce'], q, seg:{estudante,familia,turista,gourmet}}`.
  - Clashes have a negative `q` and a `quote`.
  - Put the positive ones before `{id:'bitoque'` and the clash before `{id:'x_pestoananas'`.
- **`I18N`:** each topping needs `'ing.<id>'`, and each combo `'combo.<id>'`, **in both `en` and `pt`**. Clashes also need `'quote.<id>'` in both languages.

## 6. Docs

- `docs/ingredients.md`: mark the new ones with `✓★`.
- `README.md`: update the number of combos ("95 to discover").

## 7. Test

```bash
node tools/test_ingredients.js id1,id2,id3 <scratchpad>
```

- The test fails (exit 1) if there are:
  - console errors;
  - a missing sprite;
  - `rot` without the `_n` image;
  - translations that differ between en and pt;
  - a combo that asks for a topping that doesn't exist;
  - a topping without a weight;
  - the wrong Rotate button.
- It also places 2 pieces of each topping, rotates those that rotate and lists the active combos.
- Look at `<scratchpad>/bench.png` with Read. If a piece is missing, the spot the test chose was taken or out of bounds; it is not a game bug.
- To confirm a combo, add its toppings to the id list.

## 8. Commit and push

One commit per batch, titled like "6 more toppings: a, b, c, d, e, f". In the body put:
- the generator;
- which ones rotate;
- the packs;
- the new combos and the total.

Push to the working branch. Don't open a PR unless the user asks.

## 9. Reply to the user

- A table with: topping (with a short description of the drawing), chopped form, rotation, where it is bought.
- The new combos and the total.
- What you redrew after looking at the preview.
- Remind them that prices and customer preferences are a first estimate.
