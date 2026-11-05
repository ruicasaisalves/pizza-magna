# Pizza Magna

Jogo de gestão de pizzarias para browser e telemóvel, em estilo pixel-art dos anos 90.

> Protótipo. O nome do jogo dentro do protótipo ainda é "Massa Mestra".

## Como jogar

Abre `index.html` num browser. Não precisa de instalação nem de servidor.

- **Cozinha:** inventa pizzas numa bancada de mármore (ecrã lógico de 320×200). Cada ingrediente entra inteiro ou ralado/picado: o ralado pesa e custa menos por porção e espalha o sabor. Algumas peças rodam em quartos de volta: é sempre a mesma imagem rodada. Redondas não rodam; simétricas, como o bacon, têm 2 posições (deitado, de pé); peças com frente, como um molho de espargos, têm 4. Roda-se com o botão direito do rato sobre a peça ou com o botão **Rodar** (telemóvel), que roda a última peça posta ou a próxima. A qualidade depende da quantidade, da distribuição e dos combos (há 58 por descobrir).
- **Menu:** até 5 pizzas, com preços ajustáveis.
- **Abrir:** vê a sala de cima. Os clientes (estudantes, famílias, turistas, gourmets) escolhem entre ti e a Pizza Rápida, a rival.
- **Loja:** fornos, pizzaiolos, decoração, folhetos e fornecedores de ingredientes portugueses.
- **Concurso:** a cada 5 dias há um concurso com tema.

Objetivo: 4 000 € e 3★ para abrir a segunda loja.

## Tecnologia

HTML e JavaScript simples, sem dependências nem build.

- `index.html`: jogo, interface e simulação.
- `assets/ingredients.js`: atlas com os ingredientes, massas, molhos, bancada e taça em pixel detalhado. É gerado por `python3 tools/build_atlas.py` a partir de `tools/gen_ingredients*.py`; não se edita à mão.
- `tools/test_ingredients.js`: testa os ingredientes no browser (sprites, traduções, combos, rodar). `node tools/test_ingredients.js id1,id2 <pasta>`.
- `.claude/skills/novo-lote/`: o procedimento para acrescentar um lote de ingredientes, carregado só quando se pede um lote novo.
- `sprites.js`: todos os sprites em pixel-art (chão, paredes, mobília, fornos, personagens), gerados em código numa grelha de 16 px e guardados em cache. Para trocar por um pack comprado, basta substituir as funções deste ficheiro mantendo os mesmos nomes.

A sala do restaurante é um mapa de 20×17 tiles. Os clientes e os empregados encontram caminho entre as mesas com pesquisa em largura (BFS). O jogo grava no `localStorage` do browser.

## Idioma

O jogo é em **inglês por omissão** e passa a **português** quando o idioma do browser ou do telemóvel é português (`pt`, `pt-PT`, `pt-BR`). Todos os textos visíveis vêm de uma tabela de traduções (`I18N` em `index.html`), nunca escritos diretamente no código. Já migrados: a cozinha e os nomes de ingredientes, massas, molhos, combos e públicos. Os outros ecrãs continuam por migrar.
