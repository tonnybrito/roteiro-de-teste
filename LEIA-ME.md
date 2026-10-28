**🇧🇷 Português** · [🇺🇸 English](#in-english)

# Pacote de conversão iPhone ⇄ Android

Sete skills do Claude Code: cinco guardam um jeito testado de converter um app entre iPhone e Android, **nos dois sentidos** (iPhone → Android ou Android → iPhone); a `/roteiro-de-teste` e a `/bdd-antes` servem para qualquer projeto.
Abra o **GUIA.html** (dois cliques) para ver o que cada uma faz, com imagens. O botão EN no topo mostra o guia em inglês.

| Skill | Para quê |
|---|---|
| `/roteiro-de-teste` | a base das de conversão: roteiros de teste em HTML que salvam no próprio arquivo |
| `/bdd-antes` | BDD antes do código, em qualquer projeto: página com abas, cenários, testes e resultados |
| `/conversao-preparar` | 1 · escolhe o sentido, fixa o app de referência e monta o projeto novo a partir dele |
| `/conversao-fidelidade` | 2 · deixa uma tela por vez igual à referência, medindo no print |
| `/conversao-paridade` | 3 · robô nos dois aparelhos, lado a lado com % e Diff, página de achados |
| `/conversao-android` | 4 · alvo Android: letra grande, tela baixa, teclado, voltar, Play Store |
| `/conversao-ios` | 4 · alvo iPhone: letra grande, ilha e entalhe, teclado, gesto de voltar, App Store |

## Instalar
- Pedindo ao Claude qualquer uma delas: ela abre a janela de escolha (a `/roteiro-de-teste` entra primeiro quando há uma de conversão).
- Ou no Terminal: `zsh ~/Ferramentas/conversao-ios-android/instalar.sh` (menu: 1 só a roteiro-de-teste · 2 escolher · 3 todas).
- Depois: arraste **Abrir HTML Salvável** de `~/Applications` para a Dock e reinicie o Claude Code.

## O que tem aqui
- `skills/` — as sete skills.
- `escolher-skills.sh` — o popup do macOS da janela de escolha (fora do Mac, a skill usa a janela do Claude).
- `skills/_comum-instalacao.md` — o passo 0 que todas repetem: a janela de escolha da família.
- `instalar.sh` — o instalador; guarda cópia de segurança antes de trocar uma skill.
- `GUIA.html` — o guia ilustrado, em português e inglês.

Precisa de `python3` e do ImageMagick (`brew install imagemagick`). Nada vai para a internet.

---

<a id="in-english"></a>

# iPhone ⇄ Android conversion package

Seven Claude Code skills: five keep a tested way to convert an app between iPhone and Android, **either way** (iPhone → Android or Android → iPhone); `/roteiro-de-teste` and `/bdd-antes` work for any project.
Open **GUIA.html** (double-click) to see what each one does, with pictures. The EN button at the top shows the guide in English.

| Skill | What for |
|---|---|
| `/roteiro-de-teste` ("test checklist") | the base of the conversion skills: HTML test checklists that save into the file itself |
| `/bdd-antes` ("BDD first") | BDD before code, in any project: a tabbed page, scenarios, tests and results |
| `/conversao-preparar` | 1 · picks the direction, pins the reference app and sets up the new project from it |
| `/conversao-fidelidade` | 2 · makes one screen at a time match the reference, measuring on the screenshot |
| `/conversao-paridade` | 3 · a robot on both phones, side by side with % and Diff, a findings page |
| `/conversao-android` | 4 · Android target: large font, short screens, keyboard, back, Play Store |
| `/conversao-ios` | 4 · iPhone target: large text, island and notch, keyboard, swipe-back, App Store |

## Install
- Ask Claude for any of them: it opens the choice window (`/roteiro-de-teste` comes first whenever a conversion skill is chosen).
- Or in Terminal: `zsh ~/Ferramentas/conversao-ios-android/instalar.sh` (menu: 1 only roteiro-de-teste · 2 choose · 3 all).
- Then: drag **Abrir HTML Salvável** ("Open Saveable HTML") from `~/Applications` to the Dock and restart Claude Code.

## What is here
- `skills/` — the seven skills.
- `escolher-skills.sh` — the macOS popup of the choice window (off a Mac, the skill uses Claude's own window).
- `skills/_comum-instalacao.md` — the step 0 they all repeat: the family's choice window.
- `instalar.sh` — the installer; keeps a backup copy before replacing a skill.
- `GUIA.html` — the illustrated guide, in Portuguese and English.

Needs `python3` and ImageMagick (`brew install imagemagick`). Nothing goes to the internet.
