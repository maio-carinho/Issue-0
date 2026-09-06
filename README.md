# Issue #0

Uma retrospectiva de quadrinhos lidos, no estilo Spotify Wrapped — feita a partir do histórico de leitura do [League of Comic Geeks](https://leagueofcomicgeeks.com).

O projeto navega até o seu histórico de leitura, coleta os dados de cada edição lida (criadores, personagens, editora, série, data), guarda tudo num banco local, e a partir disso calcula estatísticas como roteirista/artista favorito, maior sequência de leitura, editora mais lida — com a possibilidade de filtrar por ano, mês, trimestre, semestre ou um intervalo de datas específico.

## Funcionalidades

- **Coleta automatizada** do histórico de leitura via [Playwright](https://playwright.dev/), incluindo dados de cada edição (criadores, personagens, páginas, editora) e de cada série (gênero, era).
- **Banco de dados local** (SQLite via SQLAlchemy) — a coleta é incremental, então rodar de novo só busca o que ainda não foi salvo.
- **Análises com filtro de período**: ano inteiro, mês específico, trimestre, semestre, últimos N dias, ou um intervalo de datas customizado.
- **Métricas calculadas**: roteirista, artista, colorista e criador (geral) mais lidos; personagem mais lido; editora mais lida; maior sequência de leitura consecutiva; maior "ressaca literária" (maior intervalo sem ler nada); mês com mais edições lidas; total de edições e páginas lidas no período.
- **Interface de linha de comando** para rodar a coleta e gerar as análises.
- 🚧 **Frontend web** (FastAPI + Jinja2) — incompleto, sem previsão de conclusão.

## Arquitetura

```
retrospectiva/
├── banco/        # persistência (modelos SQLAlchemy, sessão, repositório)
├── scraping/     # coleta (Playwright para navegação, BeautifulSoup para parsing)
├── analise/      # cálculo das métricas e filtro de período
├── web/          # frontend (incompleto)
└── cli.py        # ponto de entrada da linha de comando
```

O projeto separa claramente coleta, persistência e análise em camadas independentes — nenhuma delas sabe como a outra funciona por dentro, só o que ela oferece. Alguns padrões de projeto usados ao longo do caminho: **Repository** (acesso ao banco centralizado, tanto pro lado de escrita quanto de leitura), **Value Object** (o filtro de período é um objeto imutável com construtores nomeados, tipo `Periodo.ano(2025)` ou `Periodo.ultimos_dias(30)`), e **lazy loading** (as métricas só consultam o banco quando alguém realmente pede por elas).

## Tecnologias

Python · SQLAlchemy · BeautifulSoup4 · Playwright · pandas · FastAPI · Jinja2

## Como rodar

```bash
pip install -r requisitos.txt
playwright install chromium   # baixa o navegador que o Playwright controla

# roda a coleta (a primeira vez pede login manual na janela que abre)
python -m retrospectiva.cli coletar
python -m retrospectiva.cli coletar --limite 200
python -m retrospectiva.cli coletar --margem 500

# gera a retrospectiva em determinados períodos
python -m retrospectiva.cli analisar
python -m retrospectiva.cli analisar --ano 2026
python -m retrospectiva.cli analisar --mes 5
python -m retrospectiva.cli analisar --trimestre 10
python -m retrospectiva.cli analisar --semestre 7 # tri e semestre começam a analise partindo do mês N
python -m retrospectiva.cli analisar --dias 30 # N últimos dias
python -m retrospectiva.cli analisar --inicio 2025-01-01 --fim 2025-06-30
```

Pra coletas de teste (ex.: numa conta com histórico muito grande), a coleta aceita limitar tanto quantas edições novas processar (`--limite`) quanto até onde rolar a página do histórico (`--margem`) — útil pra não esperar (ou sobrecarregar o site) processando tudo de uma vez.

## Status

Funcional e em uso pessoal — scraper, banco e análises via CLI estão prontos. O frontend web (pensado pra eventualmente gerar a retrospectiva como uma imagem, estilo cápsula do tempo mensal) ficou pela metade; o design (fontes, cores, layout dos botões de período) está encaminhado, mas a geração da imagem final em si não foi implementada.