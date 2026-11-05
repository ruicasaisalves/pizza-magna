# Geradores de sprites

`gen_ingredients.py` a `gen_ingredients9.py` desenham os ingredientes em Python (numpy + PIL). `build_atlas.py` junta-os em `../assets/ingredients.js`.

## Depois de mudar um gerador
1. `python3 tools/gen_ingredientsN.py <scratchpad>/gN` gera a folha de prévia (`preview_ingredientesN.png`). **Olha para ela** com Read.
2. `python3 tools/build_atlas.py` regenera o atlas.
3. `node tools/test_ingredients.js <ids> <scratchpad>`, e olha para `bancada.png`.

A pasta `preview/` está no `.gitignore`; as prévias vão para o scratchpad.

## Método de desenho
- **Escala:** ecrã lógico de 320×200 e pizza de 170 px. As peças medem 15 a 30 px, e as compridas até 40 px.
- **Luz:** o volume é um campo de altura; `shade()` dá a luz, sempre de cima-esquerda.
- **Cor:** cada material tem uma rampa curta em `R`, de 4 ou 5 tons, do escuro ao claro.
- **`render(mat, light, mask, mapa)`:** aplica o dithering ordenado 4×4 e o contorno seletivo. O contorno usa o tom escuro da própria rampa, nunca preto. O `mapa` diz que rampa contorna cada material.
- **Helpers:**
  - `grid` e `axes(W, H, ang)` dão as coordenadas ao longo (u) e através (v) da peça;
  - `erode` faz camadas a partir da borda;
  - `noise` dá textura;
  - `drop` faz a sombra de 2 px, que o `build_atlas.py` aplica.
- **Variantes:** 3 por ingrediente, com seeds 1, 2 e 3. Cada função usa `np.random.default_rng(seed + base)`, com uma base própria. O lote 9 chega a `+4700`; continua a partir daí.

## Rodar (`ING.rot` no jogo)
É sempre a **mesma imagem** rodada em quartos de volta, pelo jogo, sem perder píxeis; a sombra é calculada depois.
- **1:** redondo ou sem frente. Não roda e tem 3 variantes.
- **2:** simétrico, como o bacon (deitado ou de pé).
- **4:** tem frente (cauda, pé, ponta).

A função recebe `ang`. Com `ang=0`, a peça sai deitada com a frente para a direita, e o canvas troca W/H quando `|sin(ang)| > .5`. No atlas, entra em `ROTATE` como `<id>_n`, sem sombra.

## Picado (`grated()` em `gen_ingredients2.py`)
- Ervas, vegetais e queijos → `flake`; queijos que se ralam → `shred`.
- Carnes e enchidos → `cube`.
- Peixe e marisco → `chunk`.
- Frutos secos → `dice`.
- O que já é miúdo, ou só vai em fio → nenhum.
- Para misturar cores, passa uma função `f(seed)` (ver `gorgonzola_crumbs`).

## Chaves no atlas
- `<id>_0..2`: inteiro.
- `<id>_n`: inteiro de uma peça que roda.
- `<id>_g0..2`: picado.
- `sauce_<id>`, `crust_<id>`: molho e bordo, de 170 px.
- `marble`, `bowl`: a bancada e a taça.
