# HTML salvável

Deixa um HTML aberto no navegador gravar dados **dentro do próprio arquivo** (botão Salvar).
Funciona em qualquer navegador. Só neste Mac; nada vai para a internet.

## Instalar (Mac novo ou de outra pessoa)
A cópia-mestre deste pacote mora dentro da skill: `~/.claude/skills/test-checklist/pacote/`.
Copiar a pasta da skill para o outro Mac já leva tudo; o `/test-checklist` instala o resto (passo 2) pedindo antes.
1. No Terminal, `python3 --version`. Se não houver, o macOS oferece instalar; aceite.
2. Copie o conteúdo de `pacote/` para `~/Ferramentas/html-salvavel/`.
3. Se o atalho perdeu a permissão na cópia: `chmod +x ~/Ferramentas/html-salvavel/*.command`.
4. Na primeira vez, abra o atalho com botão direito › Abrir › Abrir, para o macOS liberar.

## Peças
- `servidor.py` — o mini-servidor, um só para todos os projetos. Uso: `python3 servidor.py <pasta> [arquivo.html]`.
- `abrir-html-salvavel.command` — o atalho. Copie para a pasta do HTML; dois cliques liga o servidor e abre o navegador.
  Com `ARQUIVO=""` abre uma lista dos HTMLs salváveis da pasta; preencha para abrir um direto.
- `app/` — o app **Abrir HTML Salvável** para o Dock (roteiro, ícone e `instalar-app.sh`, que monta o app em `~/Applications`).
  Ele mostra a lista dos últimos projetos abertos (ou deixa escolher outra pasta) e liga o servidor lá (via `abrir-pasta.sh`). Um app serve para todos os projetos.
- `modelo.html` — ponto de partida de um HTML salvável novo.
- `referencia/roteiro-modelo.html` — o molde que o `/test-checklist` usa: um HTML por produto, com Plataforma, Rodada,
  "Estou jogando" (variações), português/inglês e claro/escuro. Tem dois blocos: `roteiro-config` (os cards, reescrito a cada
  rodada pelo `ferramentas/roteiro.py` da skill) e `dados-salvos` (as marcações, só o botão Salvar escreve).
- `backups/` — cópia do HTML antes de cada gravação (as 30 últimas de cada arquivo).

## O combinado (o que um HTML precisa ter)
1. Exatamente um bloco `<script type="application/json" id="dados-salvos">{}</script>`. É a "gaveta" que o servidor reescreve.
2. Ao carregar, ler esse bloco. O que está nele tem prioridade sobre o localStorage.
3. Para salvar: `POST /__salvavel/salvar?arquivo=<nome.html>` com cabeçalho `X-Salvavel: 1` e um objeto JSON
   (incluir `salvoEm`). O servidor substitui a gaveta inteira por esse objeto.
4. Para saber se pode salvar: `GET /__salvavel/status` responde `{"ok": true}`. Aberto por `file://`, a página é só leitura.

## Segurança
Escuta só em 127.0.0.1, recusa outros hosts, exige o cabeçalho `X-Salvavel` (bloqueia gravações vindas de outros sites)
e só grava em `.html` da própria pasta que tenham a gaveta.

## Exemplos em uso
- o próprio `referencia/roteiro-modelo.html`, com um app fictício (Trilha dos Bichos)
