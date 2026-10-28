**🇧🇷 Português** · [🇺🇸 English](README.en.md)

# Roteiro de teste e família de skills

Um conjunto de *skills* para o [Claude Code](https://claude.com/claude-code), feito por **Tonny Brito**, para quem é, ao mesmo tempo, quem programa e quem testa, e quer que nada chegue ao revisor sem ter sido conferido antes.

Uma *skill* é um manual de instruções que o Claude segue quando você digita o nome dela, por exemplo `/roteiro-de-teste`. As skills deste repositório trabalham juntas, como uma família:

| Skill | Para quê | Precisa de |
|---|---|---|
| `/roteiro-de-teste` | **A base.** Monta um roteiro de teste manual em HTML, que você marca no navegador e que salva dentro do próprio arquivo. | — |
| `/bdd-antes` | BDD antes do código: cenários Dado / Quando / Então, arquivos Gherkin, *step definitions*, o *runner* e uma página HTML com abas, ligada ao roteiro. | nada (funciona sozinha) |
| `/conversao-preparar` | 1 · começa a conversão entre iPhone e Android, **nos dois sentidos**: pergunta qual app é a referência e anota no projeto. | `/roteiro-de-teste` |
| `/conversao-fidelidade` | 2 · deixa uma tela por vez igual à referência, medindo no print. | `/roteiro-de-teste` |
| `/conversao-paridade` | 3 · um robô percorre o app nos dois celulares e compara tela por tela, com nota e Diff. | `/roteiro-de-teste` |
| `/conversao-android` | 4 · alvo Android: letra grande, tela baixa, teclado, botão voltar, versão da Play Store. | `/roteiro-de-teste` |
| `/conversao-ios` | 4 · alvo iPhone: letra grande (*Dynamic Type*), ilha e entalhe, teclado, gesto de voltar, versão da App Store. | `/roteiro-de-teste` |

**Duas edições.** Esta página descreve a **edição em português** (`skills/`, instalada com `instalar.sh`). A **edição em inglês** tem as mesmas sete skills com nomes de comando em inglês (`/test-checklist`, `/bdd-first`, `/conversion-prepare`…), fica em `skills-en/` e é instalada com `instalar-en.sh`. As duas fazem exatamente o mesmo: instale só uma. A `skills-en/` é gerada a partir da `skills/` pelo `gerar-edicao-en.py`; nunca edite à mão.

Os exemplos usam a **Trilha dos Bichos**, um app inventado (uma trilha da Floresta, do Oceano, da Savana e da Neve, com uma coruja de guia). Todas as imagens do guia são ilustrações fictícias.

## Instalar

1. Baixe o repositório para a pasta que as skills esperam:

   ```bash
   git clone https://github.com/tonnybrito/roteiro-de-teste ~/Ferramentas/conversao-ios-android
   ```

2. Instale as skills que quiser:

   ```bash
   zsh ~/Ferramentas/conversao-ios-android/instalar.sh            # menu: 1 só a roteiro-de-teste · 2 escolher · 3 todas
   zsh ~/Ferramentas/conversao-ios-android/instalar.sh --skills bdd-antes,conversao-android
   ```

   - Escolher qualquer skill de conversão instala a `/roteiro-de-teste` primeiro.
   - A `/bdd-antes` escolhida sozinha entra sozinha.
   - Antes de trocar uma skill que já existe, o instalador guarda uma cópia em `~/Ferramentas/html-salvavel/backups/`.

3. Reinicie o Claude Code. Skills e agentes novos só aparecem numa sessão nova.

### Depois de instalar: o que aparece

- **O guia abre sozinho no navegador.** É o `GUIA.html` desta pasta, na aba da skill que você acabou de instalar. Ele mostra quais skills estão instaladas neste Mac: as instaladas têm os links ativos e ligados entre si; as outras aparecem apagadas, com "não instalada". Funciona igual para quem instala só a `/roteiro-de-teste`, só a `/bdd-antes` ou as de conversão. O guia tem um botão **EN** para inglês.
- **O botão do HTML editável** (com a `/roteiro-de-teste`). O instalador pergunta se pode pôr o app **"Abrir HTML Salvável"** no **Dock** e na **Mesa** (Desktop). É ele que abre os roteiros de teste **podendo salvar**: clique, escolha a pasta do projeto, e o navegador abre o roteiro com "💾 Salvando no arquivo" no topo (uma janela do Terminal fica aberta enquanto você testa). O guia mostra esse botão em destaque, com o ícone e o passo a passo.
- **Na Mesa** ficam dois atalhos: **"Abrir HTML Salvável"** e **"Guia das skills"**, para reabrir o guia quando quiser.
- Para criar os atalhos depois: `zsh ~/Ferramentas/conversao-ios-android/instalar.sh --skills roteiro-de-teste --atalhos sim`.

### A janela de escolha (passo 0 de toda skill)

Toda skill da família começa pelo **passo 0**: mostra as sete skills, com a situação de cada uma (*instalada*, *falta*, *desatualizada*) e o que ela faz, e pergunta quais você quer naquele projeto.

- **No macOS** abre um **popup do sistema** (`escolher-skills.sh`). Para marcar várias, use ⌘ + clique.
- **Em Linux ou Windows** o popup do macOS não existe. Ali a skill pergunta pela **janela de escolha do próprio Claude**, que funciona em qualquer sistema.

Nada é instalado sem a sua resposta.

### Na primeira vez

A `/roteiro-de-teste` pergunta **como você gostaria de ser chamado** e guarda o nome em `~/Ferramentas/html-salvavel/nome.txt` (para trocar depois, é só pedir). Depois propõe instalar, sempre perguntando antes:

- a ferramenta de salvar, em `~/Ferramentas/html-salvavel/`;
- o app **"Abrir HTML Salvável"** para o Dock (macOS);
- os agentes **independent-qa** e **independent-auditor**.

## `/roteiro-de-teste`: o roteiro que salva

- **Lê o projeto**: as regras (`CLAUDE.md`, `README`, especificações), o histórico do git e, se houver, o sistema de tarefas (opcional, só leitura). Descobre em quais plataformas o produto roda (iOS, Android, Web) e o que mudou desde a última vez.
- **Um roteiro por produto**, num único arquivo `teste<Produto>.html`, com cartões. Cada cartão é uma coisa que uma pessoa consegue conferir à mão, com os passos e o que conta como "passou".
- **Cresce por rodadas.** Cada vez que roda, acrescenta uma rodada nova e traz de volta, sozinha, o que falhou, o que ficou sem teste, o que o código mudou e o que está ligado a algo que mudou. O que já foi marcado nunca se perde.
- **Duas colunas por cartão, QA e Auditor.** Um cartão só fica verde quando os dois aprovam.
- **Comparação de telas** (iPhone × Android, Figma × Android, antes × depois), com nota, Cortina, Piscar e Diff (`ferramentas/comparar.py`, precisa do ImageMagick).
- **Ligado ao BDD.** Se o projeto tem a pasta `BDD/`, o roteiro ganha o botão "📘 Ver o BDD deste projeto" e, em cada cartão, links para os cenários que ele cobre.
- **Salva no próprio arquivo**, com cópia de segurança antes de cada mudança. Português e inglês, tema claro e escuro.

### Como se usa

1. Abra o app **"Abrir HTML Salvável"** (ou o atalho `abrir-html-salvavel.command`) e escolha a pasta do projeto.
2. Escolha o arquivo, a plataforma e a rodada.
3. Marque cada cartão (✅ Passou / ❌ Falhou / Não testado), escreva uma nota se precisar e salve.

Aberto direto pelo navegador (`file://`), o roteiro só lê. Para salvar, abra pelo app ou pelo atalho.

### Os agentes de QA e Auditor

- **`independent-qa`**: verifica a entrega contra os critérios de aceite, roda todas as checagens do repositório e tenta quebrar o que foi feito. Só lê, nunca corrige.
- **`independent-auditor`**: confere **como** o trabalho foi feito, pelas regras do próprio projeto: ordem dos commits, branch, testes junto do código, documentação atualizada, nenhuma assinatura de IA. Também só lê.

Eles leem o projeto, os testes e o git. Para lerem também um sistema de tarefas, acrescente as ferramentas dele na linha `tools:` de cada agente.

## `/bdd-antes`: BDD antes do código

Antes de escrever ou mudar código, a skill descreve **tudo o que se pode fazer** no produto, cada comando e cada clique, como cenários **Dado / Quando / Então**, em linguagem simples.

1. **Entende a ideia do projeto** e em que linguagem ele é (ou vai ser) escrito.
2. **Escolhe a ferramenta de BDD** pela linguagem: `pytest-bdd` para Python, Cucumber.js ou playwright-bdd para JavaScript/TypeScript, Cucumber-JVM para Java/Kotlin, e a mais adequada para as outras, explicando o porquê.
3. **Instala tudo** na pasta `BDD/` do projeto, sem mexer nas dependências dele:
   - os arquivos Gherkin (`.feature`), sempre em inglês (só a página HTML é bilíngue);
   - as *step definitions*, o código que liga cada frase a uma ação de verdade;
   - o *runner* e a configuração;
   - uma página HTML com uma aba por tela, menu para pular entre abas, botões interligados e verificador de links, em português e inglês, tema claro e escuro, que mostra ao lado de cada cenário se o teste passou.

O código de cada cenário (ex.: `L-03`) é o mesmo no `.feature`, no HTML e no roteiro de teste.

## As skills de conversão iPhone ⇄ Android

Funcionam **nos dois sentidos**: iPhone → Android ou Android → iPhone. O app de **referência** (o "oráculo") diz como tudo deve ficar; o **alvo** é o que está sendo construído. A `/conversao-preparar` pergunta o sentido uma vez e as outras leem essa resposta. No fim, a `/conversao-android` (alvo Android) ou a `/conversao-ios` (alvo iPhone) cuidam do que só existe naquela plataforma. Abra o **[`GUIA.html`](GUIA.html)** (dois cliques) para ver, com imagens, o que cada uma faz, quando usar e o passo a passo.

## O que tem aqui

| Pasta / arquivo | Para que serve |
|---|---|
| `skills/roteiro-de-teste/` | A base. `SKILL.md` (as instruções), `COMO-USAR.html` (guia ilustrado), `ferramentas/` (`roteiro.py`, `comparar.py`) e `pacote/` (a ferramenta de salvar, o atalho, o app do Dock, os agentes e o modelo do roteiro com o exemplo fictício) |
| `skills/bdd-antes/` | A skill de BDD |
| `skills/conversao-*/` | As cinco skills de conversão |
| `skills/_comum-instalacao.md` | O passo 0 que todas repetem: a janela de escolha da família |
| `instalar.sh` | O instalador |
| `escolher-skills.sh` | O popup do macOS do passo 0 |
| `skills-en/`, `instalar-en.sh`, `escolher-skills-en.sh` | A edição em inglês, gerada pelo `gerar-edicao-en.py` |
| `GUIA.html` | O guia ilustrado da família, em português e inglês |
| `LEIA-ME.md` | Resumo curto do pacote |

## Requisitos

- Claude Code.
- Python 3.
- macOS para o popup, o app do Dock e o atalho `.command`. O roteiro em si abre em qualquer navegador.
- ImageMagick para as comparações de tela (`brew install imagemagick`).
- Para as skills de conversão: Xcode, Android Studio e, para a `/conversao-paridade`, o [Maestro](https://maestro.mobile.dev).

Nada vai para a internet: a ferramenta de salvar roda só no seu computador (`127.0.0.1`).

## Autor

Tonny Brito.
