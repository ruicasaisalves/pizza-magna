---
name: novo-lote
description: Acrescenta um lote de ingredientes novos ao Pizza Magna (sprites em pixel detalhado, atlas, dados do jogo, traduções, combos, documentação e teste). Usar quando o utilizador pede mais ingredientes ("faz mais 6", "acrescenta X e Y"), ou para corrigir o desenho de um ingrediente que já existe.
---

# Novo lote de ingredientes

Responde ao utilizador em português. Os comentários no código seguem a língua do ficheiro: português nos geradores, inglês no `index.html`.

## 0. Ramo

Se o PR do ramo de trabalho já foi fundido, recomeça o ramo a partir do `main`:
`git fetch origin main && git checkout -B <ramo> origin/main`.

## 1. Ler o método

Lê `tools/CLAUDE.md`. Tem o método de desenho, as regras de rodar (`ING.rot` 1, 2 ou 4) e do picado, e as chaves do atlas.

## 2. Escolher

- Tira os ingredientes da lista de `docs/ingredientes.md` (os que não têm ✓★), salvo se o utilizador os nomear.
- Varia as categorias e dá prioridade aos que abrem combos planeados (secção "Ideias").
- Decide, para cada um, se roda (1, 2 ou 4 posições) e qual é a forma picada.

## 3. Desenhar: `tools/gen_ingredientsN.py`

- Copia a estrutura de `tools/gen_ingredients9.py`: o mesmo cabeçalho, `R.update`, uma função por ingrediente, `SETS` e o `__main__`, que faz a folha de prévia.
- Gera a prévia e **olha para ela** com Read antes de continuar. Se uma peça não se reconhece à primeira vista, refaz o desenho. Os erros mais comuns são:
  - um contorno recortado que parece folha;
  - pormenores que ficam com o mesmo tom e desaparecem;
  - uma forma pequena demais.

## 4. Atlas: `tools/build_atlas.py`

1. `import gen_ingredientsN as GN`, ao lado dos outros imports.
2. Em `INGS`: `'id': (GN.funcao, ('rampa', 'tipo', n_bits) | funcao | None)`.
3. Se roda, acrescenta-o a `ROTATE`: `'id': lambda: GN.funcao(1, ang=0)`, com um comentário sobre o número de posições.
4. Corre `python3 tools/build_atlas.py`. Isto regenera `assets/ingredients.js`, que nunca se edita à mão.

## 5. Jogo: `index.html`

- Usa grep para encontrar os blocos; não leias o `index.html` inteiro.
- **`ING`:** a entrada vai no bloco do seu pack.
  - Formato: `id:{n:'Nome',c:custo,t:[tags],pack:'base'|'local'|'gourmet',rot:N}`. Só se põe `rot` se for maior do que 1.
  - **Tags:** `queijo carne peixe vegetal doce picante classico portugues gourmet`.
  - **Packs:** `base` para o barato e comum; `local` (Mercado Local) para o português e para peixe; `gourmet` (Delicatessen) para o caro e de luxo.
  - **Custo por porção:** 0,02 (alho) a 0,20 (burrata).
- **`GRAMS`:** o peso em gramas de uma peça inteira (o picado pesa `GRATED_W`, 70%). O teste falha se faltar.
- **`COMBOS`:** um combo positivo por ingrediente novo, e um choque por lote.
  - Formato: `{id, n, req:[ids ou 's:molho'], q, seg:{estudante,familia,turista,gourmet}}`.
  - Os choques têm `q` negativo e `quote`.
  - Põe os positivos antes de `{id:'bitoque'` e o choque antes de `{id:'x_pestoananas'`.
- **`I18N`:** cada ingrediente precisa de `'ing.<id>'`, e cada combo de `'combo.<id>'`, **em `en` e em `pt`**. Os choques precisam também de `'quote.<id>'` nas duas línguas.

## 6. Documentação

- `docs/ingredientes.md`: marca os novos com `✓★` e tira das "Ideias" os combos que passaram a existir.
- `README.md`: atualiza o número de combos em "(há N por descobrir)".

## 7. Testar

```bash
node tools/test_ingredients.js id1,id2,id3 <scratchpad>
```

- O teste falha (exit 1) se houver:
  - erros na consola;
  - um sprite em falta;
  - `rot` sem a imagem `_n`;
  - traduções desiguais entre en e pt;
  - um combo que pede um ingrediente inexistente;
  - o botão Rodar errado.
- Também põe 2 peças de cada ingrediente, roda as que rodam e lista os combos ativos.
- Olha para `<scratchpad>/bancada.png` com Read. Se faltar alguma peça, é porque o sítio onde o teste a pôs está ocupado ou fora da área permitida; não é um erro do jogo.
- Para confirmar um combo, junta os seus ingredientes à lista de ids.

## 8. Commit e push

Faz um commit por lote, com um título como "Mais 6 ingredientes: a, b, c, d, e, f". No corpo, põe:
- o gerador;
- os que rodam;
- os packs;
- os combos novos e o total.

Faz push para o ramo de trabalho. Não abras PR sem o utilizador pedir.

## 9. Resposta ao utilizador

- Uma tabela com: ingrediente (com uma descrição curta do desenho), picado, roda, onde se compra.
- Os combos novos e o total.
- O que refizeste depois de ver a prévia.
- Lembra que os preços e as preferências dos clientes são uma primeira estimativa.
