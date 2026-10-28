[🇧🇷 Português](README.md) · **🇺🇸 English**

# Test checklist and skill family

A set of [Claude Code](https://claude.com/claude-code) *skills*, made by **Tonny Brito**, for people who are both the developer and the tester, and want nothing to reach the reviewer without being checked first.

A *skill* is an instruction manual that Claude follows when you type its name, for example `/test-checklist`. The skills in this repository work together, as a family:

| Skill | What for | Needs |
|---|---|---|
| `/test-checklist` | **The base.** Builds a manual test checklist in HTML that you mark in the browser and that saves inside the file itself. | — |
| `/bdd-first` | BDD before code: Given / When / Then scenarios, Gherkin files, step definitions, the runner and a tabbed HTML page, linked to the checklist. | nothing (works alone) |
| `/conversion-prepare` | 1 · starts a conversion between iPhone and Android, **either way**: asks which app is the reference and records it in the project. | `/test-checklist` |
| `/conversion-fidelity` | 2 · makes one screen at a time match the reference, measuring on the screenshot. | `/test-checklist` |
| `/conversion-parity` | 3 · a robot walks the app on both phones and compares screen by screen, with a score and a Diff. | `/test-checklist` |
| `/conversion-android` | 4 · Android target: large font, short screens, keyboard, back button, Play Store build. | `/test-checklist` |
| `/conversion-ios` | 4 · iPhone target: large text (*Dynamic Type*), island and notch, keyboard, swipe-back, App Store build. | `/test-checklist` |

The examples use **Animal Trail**, a made-up app (a Forest, Ocean, Savanna and Snow trail, with an owl as the guide). Every image in the guide is a fictional illustration.

The skills talk to you in your language; their own texts and the generated pages are in Portuguese and English.

**Two editions.** This page describes the **English edition**: the same seven skills with English command names (`/test-checklist`, `/bdd-first`, `/conversion-prepare`…), in `skills-en/`, installed with `instalar-en.sh`. The Portuguese edition (`/roteiro-de-teste`, `/bdd-antes`, `/conversao-preparar`…) lives in `skills/` and is installed with `instalar.sh`. They do exactly the same: install only one. `skills-en/` is generated from `skills/` by `gerar-edicao-en.py`; never edit it by hand.

## Install

1. Download the repository into the folder the skills expect:

   ```bash
   git clone https://github.com/tonnybrito/roteiro-de-teste ~/Ferramentas/conversao-ios-android
   ```

2. Install the skills you want:

   ```bash
   zsh ~/Ferramentas/conversao-ios-android/instalar-en.sh            # menu: 1 only test-checklist · 2 choose · 3 all
   zsh ~/Ferramentas/conversao-ios-android/instalar-en.sh --skills bdd-first,conversion-android
   ```

   - Choosing any conversion skill installs `/test-checklist` first.
   - `/bdd-first` chosen alone is installed alone.
   - Before replacing a skill that already exists, the installer keeps a copy in `~/Ferramentas/html-salvavel/backups/`.

3. Restart Claude Code. New skills and agents only show up in a new session.

### The choice window (step 0 of every skill)

Every skill in the family starts with **step 0**: it shows the seven skills, each with its state (*installed*, *missing*, *outdated*) and what it does, and asks which ones you want in that project.

- **On macOS** it opens a **system popup** (`escolher-skills-en.sh`). To pick several, use ⌘ + click.
- **On Linux or Windows** the macOS popup does not exist. There the skill asks through **Claude's own choice window**, which works on any system.

Nothing is installed without your answer.

### The first time

`/test-checklist` asks **what you would like to be called** and keeps the name in `~/Ferramentas/html-salvavel/nome.txt` (to change it later, just ask). Then it offers to install, always asking first:

- the saving tool, in `~/Ferramentas/html-salvavel/`;
- the **"Abrir HTML Salvável"** app for the Dock (macOS);
- the **independent-qa** and **independent-auditor** agents.

## `/test-checklist`: the checklist that saves

- **Reads the project**: its rules (`CLAUDE.md`, `README`, specs), the git history and, if there is one, the task tracker (optional, read-only). It finds out which platforms the product runs on (iOS, Android, Web) and what changed since last time.
- **One checklist per product**, in a single `teste<Product>.html` file, made of cards. Each card is one thing a person can check by hand, with the steps and what counts as "passed".
- **Grows round by round.** Each run adds a new round and brings back, by itself, what failed, what was not tested, what the code changed and what is linked to something that changed. What was already marked is never lost.
- **Two columns per card, QA and Auditor.** A card turns green only when both approve.
- **Screen comparison** (iPhone × Android, Figma × Android, before × after), with a score, Curtain, Blink and Diff (`ferramentas/comparar.py`, needs ImageMagick).
- **Linked to the BDD.** If the project has a `BDD/` folder, the checklist gets a "📘 See this project's BDD" button and, on each card, links to the scenarios it covers.
- **Saves inside the file**, with a backup before every change. Portuguese and English, light and dark theme.

### How to use it

1. Open the **"Abrir HTML Salvável"** app (or the `abrir-html-salvavel.command` shortcut) and choose the project folder.
2. Choose the file, the platform and the round.
3. Mark each card (✅ Passed / ❌ Failed / Not tested), write a note if needed, and save.

Opened straight from the browser (`file://`), the checklist is read-only. To save, open it through the app or the shortcut.

### The QA and Auditor agents

- **`independent-qa`**: checks the delivery against the acceptance criteria, runs every check the repository has, and tries to break what was built. Read-only, never fixes.
- **`independent-auditor`**: checks **how** the work was done, by the project's own rules: commit order, branch, tests alongside code, updated docs, no AI signature. Read-only too.

They read the project, its tests and git. To let them read a task tracker too, add its tools to the `tools:` line of each agent.

## `/bdd-first`: BDD before code

Before writing or changing code, the skill describes **everything you can do** in the product, every command and every click, as **Given / When / Then** scenarios, in plain language.

1. **Understands the idea of the project** and which language it is (or will be) written in.
2. **Picks the BDD tool** for that language: `pytest-bdd` for Python, Cucumber.js or playwright-bdd for JavaScript/TypeScript, Cucumber-JVM for Java/Kotlin, and the best fit for others, explaining why.
3. **Installs everything** in the project's `BDD/` folder, without touching its dependencies:
   - the Gherkin files (`.feature`), always in English (only the HTML page is bilingual);
   - the step definitions, the code that ties each sentence to a real action;
   - the runner and its configuration;
   - an HTML page with one tab per screen, a menu to jump between tabs, interlinked buttons and a link checker, in Portuguese and English, light and dark theme, showing next to each scenario whether its test passed.

Each scenario's code (e.g. `L-03`) is the same in the `.feature`, in the HTML and in the test checklist.

## The iPhone ⇄ Android conversion skills

They work **both ways**: iPhone → Android or Android → iPhone. The **reference** app (the "oracle") says how everything must be; the **target** is the app being built. `/conversion-prepare` asks the direction once and the others read the answer. At the end, `/conversion-android` (Android target) or `/conversion-ios` (iPhone target) cover what only that platform has. Open **[`GUIA.html`](GUIA.html)** (double-click) to see, with pictures, what each one does, when to use it and the step by step (Portuguese and English: use the EN button at the top).

## What's in here

| Folder / file | What it is for |
|---|---|
| `skills-en/test-checklist/` | The base. `SKILL.md` (the instructions), `COMO-USAR.html` (illustrated guide), `ferramentas/` (`roteiro.py`, `comparar.py`) and `pacote/` (the saving tool, the shortcut, the Dock app, the agents and the checklist model with the fictional example) |
| `skills-en/bdd-first/` | The BDD skill |
| `skills-en/conversion-*/` | The five conversion skills |
| `skills-en/_comum-instalacao.md` | The step 0 every skill repeats: the family's choice window |
| `instalar-en.sh` | The installer |
| `escolher-skills-en.sh` | The macOS popup for step 0 |
| `GUIA.html` | The family's illustrated guide |
| `LEIA-ME.md` | Short summary of the package |

## Requirements

- Claude Code.
- Python 3.
- macOS for the popup, the Dock app and the `.command` shortcut. The checklist itself opens in any browser.
- ImageMagick for screen comparisons (`brew install imagemagick`).
- For the conversion skills: Xcode, Android Studio and, for `/conversion-parity`, [Maestro](https://maestro.mobile.dev).

Nothing goes to the internet: the saving tool runs only on your computer (`127.0.0.1`).

## Author

Tonny Brito.
