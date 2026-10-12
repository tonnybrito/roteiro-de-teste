# Roteiro de teste

Uma *skill* para o [Claude Code](https://claude.com/claude-code) que transforma "o que o produto faz e o que mudou" num **roteiro de teste manual em HTML**: uma página aberta no navegador, onde cada item é testado à mão, marcado e **salvo dentro do próprio arquivo**.

Feita para quem é, ao mesmo tempo, quem programa e quem testa — e quer que nada chegue ao revisor sem ter sido conferido antes.

## O que ela faz

- **Lê o projeto**: as regras (`CLAUDE.md`, `README`, especificações), o histórico do git e, se houver, o sistema de tarefas. Descobre em quais plataformas o produto roda (iOS, Android, Web) e o que mudou desde a última vez.
- **Monta um roteiro por produto**, um único arquivo `teste<Produto>.html`, com cartões: cada cartão é uma coisa que uma pessoa consegue conferir à mão, com os passos e o que conta como "passou".
- **Cresce por rodadas.** Cada vez que roda, acrescenta uma rodada nova com os cartões novos e traz de volta, sozinha, o que falhou, o que ficou sem teste, o que o código mudou e o que está ligado a algo que mudou. O que já foi marcado nunca se perde.
- **Duas colunas por cartão: QA e Auditor.** Um cartão só fica verde quando o QA aprovou **e** o Auditor aprovou.
- **Salva no próprio arquivo.** As marcações ficam guardadas dentro do HTML (com cópia de segurança antes de cada mudança), então o arquivo pode ser guardado, enviado ou reaberto depois.
- **Português e inglês**, tema claro e escuro, filtro por plataforma, rodada e variação ("Estou jogando…"), anotações e capturas de tela do que o QA viu.

## Os sub-agentes de QA e Auditor

A pasta `pacote/agentes/` traz dois agentes do Claude Code:

- **`independent-qa`** — verifica a entrega contra os critérios de aceite, roda todas as checagens do repositório e tenta quebrar o que foi feito. Só lê: nunca corrige.
- **`independent-auditor`** — confere **como** o trabalho foi feito, pelas regras do próprio projeto: ordem dos commits, branch, testes junto do código, documentação atualizada, nenhuma assinatura de IA. Só lê também.

Na primeira vez, a skill confere se eles estão em `~/.claude/agents/` e, com a sua permissão, instala. Depois de instalar, reinicie o Claude Code uma vez (os agentes carregam quando a sessão começa).

Eles leem o projeto, os testes e o git. Para lerem também um sistema de tarefas (Linear, Jira…), acrescente as ferramentas dele na linha `tools:` de cada agente.

## Instalar

1. Copie esta pasta para `~/.claude/skills/roteiro-de-teste`.
2. Abra um projeto no Claude Code e digite `/roteiro-de-teste`.
3. Na primeira vez, a skill propõe instalar a ferramenta de salvar em `~/Ferramentas/html-salvavel/`, o app **"Abrir HTML Salvável"** para o Dock (macOS) e os dois agentes — sempre perguntando antes.

O passo a passo ilustrado está em [`COMO-USAR.html`](COMO-USAR.html).

## Como se usa o roteiro

1. Abra o app **"Abrir HTML Salvável"** (ou o atalho `abrir-html-salvavel.command`) e escolha a pasta do projeto.
2. Escolha o arquivo, a plataforma e a rodada.
3. Toque em **"Para testar nesta rodada"** para ver só o que falta testar.
4. Marque cada cartão (✅ Passou / ❌ Falhou / Não testado), escreva uma nota se precisar e salve.

Aberto direto pelo navegador (`file://`), o roteiro funciona só para leitura; para salvar, abra pelo app ou pelo atalho.

## O que tem aqui

| Pasta / arquivo | Para que serve |
|---|---|
| `SKILL.md` | As instruções que o Claude segue |
| `COMO-USAR.html` | Guia ilustrado de instalação e uso |
| `ferramentas/roteiro.py` | O único jeito de criar e atualizar um roteiro (`novo`, `config`, `molde`, `ler`) |
| `pacote/` | A ferramenta de salvar (`servidor.py`), o atalho, o app do Dock e os agentes |
| `pacote/referencia/roteiro-modelo.html` | O modelo de onde todo roteiro nasce, com um exemplo fictício |

## Requisitos

- Claude Code.
- macOS para o app do Dock e o atalho `.command` (o roteiro em si abre em qualquer navegador).
- Python 3.
