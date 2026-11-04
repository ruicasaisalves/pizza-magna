# Pizza Magna

Jogo de gestão de pizzarias para browser e telemóvel, em estilo pixel-art dos anos 90.

> Protótipo. O nome do jogo dentro do protótipo ainda é "Massa Mestra".

## Como jogar

Abre `index.html` num browser. Não precisa de instalação nem de servidor.

- **Cozinha:** inventa pizzas com massa, molho e ingredientes. A qualidade depende da quantidade, da distribuição e dos combos (há 16 por descobrir).
- **Menu:** até 5 pizzas, com preços ajustáveis.
- **Abrir:** vê a sala de cima. Os clientes (estudantes, famílias, turistas, gourmets) escolhem entre ti e a Pizza Rápida, a rival.
- **Loja:** fornos, pizzaiolos, decoração, folhetos e fornecedores de ingredientes portugueses.
- **Concurso:** a cada 5 dias há um concurso com tema.

Objetivo: 4 000 € e 3★ para abrir a segunda loja.

## Tecnologia

HTML e JavaScript simples, sem dependências nem build.

- `index.html`: jogo, interface e simulação.
- `sprites.js`: todos os sprites em pixel-art (chão, paredes, mobília, fornos, personagens), gerados em código numa grelha de 16 px e guardados em cache. Para trocar por um pack comprado, basta substituir as funções deste ficheiro mantendo os mesmos nomes.

A sala do restaurante é um mapa de 20×17 tiles. Os clientes e os empregados encontram caminho entre as mesas com pesquisa em largura (BFS). O jogo grava no `localStorage` do browser.

## Idioma

O jogo é em **inglês por omissão** e passa a **português** quando o idioma do browser ou do telemóvel é português (`pt`, `pt-PT`, `pt-BR`). Todos os textos visíveis vêm de uma tabela de traduções, nunca escritos diretamente no código.
