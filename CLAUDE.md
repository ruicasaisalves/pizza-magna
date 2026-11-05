# Pizza Magna

Jogo de gestão de pizzarias em pixel art dos anos 90, para browser e telemóvel. É HTML e JS simples, sem build nem dependências: abre-se o `index.html` diretamente do disco.

## Ficheiros
- `index.html`: o jogo todo (cerca de 1200 linhas). **Não o leias inteiro.** Procura a secção pelo marcador com grep e lê só essa:
  - `= LANGUAGE =`: `LANG` e a tabela `I18N` (en/pt)
  - `= DATA =`: `DOUGHS`, `SAUCES`, `ING`, `PACKS`, `COMBOS`, `SEG`, `THEMES` e as constantes de economia
  - `= PIZZA ANALYSIS =`: `analyze()` (qualidade, custo, apelo) e `contestScore()`
  - `= DRAWING`: atlas, `spr()`, peças que rodam (`turned()`), `composePizza()`, `LAYER`
  - `= UI: KITCHEN =` e `-- the pizza bench`: a bancada 320×200, as taças, `addPiece()`, `rotatePiece()`
  - `= UI: DAY =`, `-- simulation`, `-- restaurant room`: o dia, os clientes e a sala em tiles
  - `= UI: SHOP =`, `= UI: CONTEST =`, `= MODALS =`
  - `= RENDER + EVENTS =`: `render()` e as ações dos botões (`ACT`)
- `sprites.js`: sala, mobília e personagens, gerados em código.
- `music.js`: música 8 bits / lo-fi italiana, sintetizada com Web Audio (sem ficheiros de som). Cada música é texto: uma nota por colcheia, `-` prolonga, `.` é silêncio. Melodia, baixo e harmonia têm de ter o mesmo número de passos por parte. A preferência ligada/desligada fica em `localStorage` (`pm-music`), à parte da gravação.
- `assets/ingredients.js`: atlas dos ingredientes. **É gerado** por `tools/build_atlas.py`; nunca se edita à mão. Ver `tools/CLAUDE.md`.
- `docs/ingredientes.md`: a lista de ingredientes (✓★ = já no jogo) e as ideias de combos.
- `docs/packs-de-arte.md`: packs de arte avaliados e a decisão de estilo.

## Regras
- **Idioma:** o jogo é em inglês por omissão e em português quando o browser está em `pt`. Todo o texto visível vem de `I18N`, com a mesma chave em `en` e em `pt`. Até agora estão migrados a cozinha e os nomes de ingredientes, massas, molhos, combos e públicos; o resto ainda está escrito em português no código, e o que se tocar migra-se.
- **Respostas e documentação** em português de Portugal. Comentários no `index.html` em inglês; nos geradores Python, em português.
- **Gravações:** o estado vai para `localStorage` (`massa-mestra-v1`). Campos novos precisam de um valor por omissão, para os jogos já gravados continuarem a abrir.
- Não acrescentes dependências nem passos de build.

## Testar
- Modo de teste: `index.html#sandbox` (ou `window.PM_SANDBOX=true`) abre só a Cozinha e o Menu, com tudo desbloqueado e gravação à parte. É o que está publicado no artefacto "Bancada de Pizzas". No site público (`pizzamagna.xyz` e `*.github.io`, via GitHub Pages a partir do `main`) o jogo abre sempre neste modo: só a bancada está live.
- `node tools/test_ingredients.js [id1,id2] <pasta>`: verifica sprites, traduções e combos, e põe peças na bancada.
- Para outros ecrãs, usa o Playwright: `require('playwright')` funciona sem instalar nada.

## Tarefas com procedimento próprio
- Ingredientes novos ou correções de um sprite: usa a skill `novo-lote`.
- Mexer nos geradores de sprites: lê `tools/CLAUDE.md`.
