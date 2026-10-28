---
name: conversion-android
description: When Android is the target of a conversion, check and fix what the iPhone version never covers on Android - the phone's font size (normal, middle of the slider, maximum), short screens and the 3-button bar, the keyboard covering fields, the system back button, edge-to-edge insets and the minified store build - labelling every change as a fix (correção) or an improvement over the iPhone (melhoria), each with its own commit and a proposal back to iOS. Its mirror for an iPhone target is conversion-ios. Part of the iPhone ⇄ Android conversion package; needs test-checklist. Triggers include "/conversion-android", "testa com letra grande no Android", "no meu celular ficou cortado", "o teclado cobre o campo", "a tela é baixa e o balão cobre", "prepara para a Play Store".
---

# /conversion-android — 4 · Beyond the iPhone

For conversions whose **target is Android** (iPhone → Android). A port can match the iPhone pixel for pixel and still break on real Android phones. This skill sweeps those cases, one at a time with the person, and keeps a clear line between **correção** (Android broke something the iPhone does right) and **melhoria** (Android goes beyond the iPhone). When the target is the iPhone, use `/conversion-ios` instead; this skill can still check an Android **reference** app before it is used as the oracle.

## 0. The skill family (first, every time)

This skill belongs to a **family** kept in `~/Ferramentas/conversao-ios-android/` (guide in `GUIA.html` there):
- `test-checklist`: the saveable HTML checklists. The base of the conversion skills.
- `bdd-first`: BDD before code (Gherkin features, steps, runner and the linked BDD page). It works **with or without** `test-checklist`; when both are in a project, the checklist links to the BDD.
- `conversion-prepare`, `conversion-fidelity` and `conversion-parity`: the conversion between iPhone and Android, **both ways** (iPhone → Android or Android → iPhone; `conversion-prepare` records which app is the reference). `conversion-android` and `conversion-ios`: what only the target platform has. Each works alone; all need `test-checklist`.

1. Check each of the seven: present in `~/.claude/skills/`, and the same as the package copy (`diff -rq ~/.claude/skills/<name> ~/Ferramentas/conversao-ios-android/skills-en/<name>`). A skill missing from the package's `skills/` is "ainda não criada".
2. **Always open the choice window**, even when everything is installed. Before it, say that `/test-checklist` is the base: it is installed first whenever a conversion skill is chosen, and cannot be left out then. Never install without the answer.
   - **On macOS: a native popup.** Run `zsh ~/Ferramentas/conversao-ios-android/escolher-skills-en.sh` with the Bash timeout at 600000 (the person may take a while). It shows the seven skills, each with its state and what it does, and prints the chosen names separated by commas, or `CANCELADO`, or nothing when none was marked. Tell the person the popup is open on the screen.
   - **Elsewhere** (the script prints `SEM-POPUP` and exits 3), use the Claude window instead: **one** AskUserQuestion holding three questions, all `multiSelect: true` (a question holds at most four options): header "BDD" with `/bdd-first` plus "Nenhuma"; header "Conversão" with `/conversion-prepare`, `/conversion-fidelity`, `/conversion-parity` plus "Nenhuma"; header "Plataforma" with `/conversion-android`, `/conversion-ios` plus "Nenhuma". Each option's description says what the skill does and its state.
   - States: **instalada**, **falta**, **desatualizada** or **ainda não criada**. A chosen skill that is "ainda não criada" cannot be installed: say so.
3. If `test-checklist` is among the chosen ones (or already installed), ask one more question: put the "Abrir HTML Salvável" button (the app that opens the editable HTML) in the Dock and on the Desktop? Then install only what was chosen and is missing or outdated: `zsh ~/Ferramentas/conversao-ios-android/instalar-en.sh --skills <comma-separated names> --atalhos sim|nao`. At the end it opens `GUIA.html` in the browser, on the installed skill's tab, showing which skills are installed and highlighting that button; tell the person it opened. It puts `test-checklist` first when a conversion skill is chosen, installs `bdd-first` alone when only it is chosen, skips what is up to date, refuses a skill the package does not have, and backs up anything it replaces. A chosen skill that is installed and up to date needs nothing: say so.
4. Then, when this skill uses checklists, run `test-checklist` step 1 ("Prepare the saving"): the saving tool, the Dock app "Abrir HTML Salvável" and the QA/Auditor agents, each asked first.
5. New skills and agents load only in a new session: if something was installed, ask the person to restart Claude Code, and stop here.

Talk to the person in their language, by the name saved in `~/Ferramentas/html-salvavel/nome.txt` (the `test-checklist` step 1 asks for it; until then, their `whoami` name). If their CLAUDE.md says how to work with them (tutor style, one thing at a time, one question per message, asking before every action), follow it.

## 1. Font size sweep

- Capture every screen at `adb shell settings put system font_scale 1.0`, `1.3` (about the middle of a Samsung slider) and `2.0` (Android's maximum); put the three side by side for the person. Reset to 1.0 after.
- Rules that came out of Trilha dos Bichos (each with JVM tests):
  - **Titles** grow only to 1.35× (iOS stops display fonts at xxxLarge) and **never break inside a word**: shrink until every word fits its line (`TitleText(keepWordsWhole)`).
  - **Buttons side by side** keep the same size: the label grows to 1.35×, the longer one shrinks to one line (down to 0.3×), and the button keeps the height of its full-size line.
  - **Speech bubbles** (iOS pins them) follow the phone font up to 1.5×, taking a larger art of the same bubble when it fits the room the screen gives, and never ending past NEXT or the tail (melhoria).
  - **Tables of values** (a summary card) are rows, not free columns: labels top-aligned, pictures and values sharing a line whatever wraps.
  - **Content pushed below the fold**: a soft jumping chevron (like the bubbles' NEXT) and a dimmed button that scrolls to what it waits for (melhoria).

## 2. Short screens, bars and keyboard

- Emulate the person's phone: e.g. `wm size 1080x2400` + `wm density 450` (≈ 384 × 853 dp), the 3-button navigation bar (`cmd overlay enable com.android.internal.systemui.navbar.threebutton`), and a Small Phone.
- Things that overlap there but not on the iPhone get a **measured** rule (Trilha dos Bichos: the first-scan frame rises just enough to sit 20 dp above the tutorial bubble, never under the top bar). Content always sits above the system bar (edge-to-edge insets).
- Keyboard: `imePadding`, and `BringIntoViewRequester` so the field being typed in stays above the keyboard as it slides up; fields that appear (more players) scroll into view on their own.
- System back on every screen does what the iPhone's back does (or the exit dialog), never loses progress.

## 3. The store build

- The release build is minified (R8) and needs signing: install a release-like build at least once (a "qa" variant: minified like release, with the debug hooks) and run the robot on it.
- Remote services kept off on purpose (Trilha dos Bichos: Firebase) leave a loud alert in the release build and in the docs, and a store checklist: Play pre-launch report on real devices, the remote service decision, internal testing on a few phones.

## 4. Correção or melhoria

- Ask the person which one it is when it is not obvious; the iPhone doing the same wrong thing makes it a **melhoria** (Trilha dos Bichos: the Christmas frame was hidden on iOS too).
- One commit each: `area: fix …` or `area: improvement - …`, saying the iPhone does/doesn't do it.
- Record it in the findings page tabs **🔧 Correções** / **✨ Melhorias** with before × after, and mark the melhorias as "proposta para levar ao iOS".
