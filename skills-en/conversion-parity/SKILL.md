---
name: conversion-parity
description: Walk the whole app on the iPhone and on Android with the same robot flows (Maestro), in either conversion direction, capture every screen per cycle/theme and device, build side-by-side images with a proximity score and a Diff against the reference app, and turn every difference into a findings page and checklist cards reviewed one at a time with the person. Also maps what changed when the reference app ships a new version. Part of the iPhone ⇄ Android conversion package; needs test-checklist. Triggers include "/conversion-parity", "roda o robô nos dois", "compara o app inteiro com o iPhone", "compara o app inteiro com o Android", "nova rodada de QA lado a lado", "o que mudou na versão nova".
---

# /conversion-parity — 3 · Parity walk

The robot plays the same path on both phones, so the comparison is fair. The **reference** app is the yardstick and the **target** is what gets findings; read the direction first from the `Conversion:` block in the target's `CLAUDE.md` (written by `/conversion-prepare`), or ask. The person reviews the findings **one card at a time**; nothing is recorded as decided until they confirm it.

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
3. Install only what was chosen and is missing or outdated: `zsh ~/Ferramentas/conversao-ios-android/instalar-en.sh --skills <comma-separated names>`. It puts `test-checklist` first when a conversion skill is chosen, installs `bdd-first` alone when only it is chosen, skips what is up to date, refuses a skill the package does not have, and backs up anything it replaces. A chosen skill that is installed and up to date needs nothing: say so.
4. Then, when this skill uses checklists, run `test-checklist` step 1 ("Prepare the saving"): the saving tool, the Dock app "Abrir HTML Salvável" and the QA/Auditor agents, each asked first.
5. New skills and agents load only in a new session: if something was installed, ask the person to restart Claude Code, and stop here.

Talk to the person in their language, by the name saved in `~/Ferramentas/html-salvavel/nome.txt` (the `test-checklist` step 1 asks for it; until then, their `whoami` name). If their CLAUDE.md says how to work with them (tutor style, one thing at a time, one question per message, asking before every action), follow it.

## 1. Before every capture

- Check the devices: apps open on emulators and simulators, robot processes left running (`pgrep -fl maestro`). Close them and say so.
- Mute: start the emulator with `-no-audio` and mute the Mac while the robot runs; sound back only when calling the person.
- Robot settings on Android: `adb shell settings put secure show_ime_with_hard_keyboard 0` (restore to 1 to show the full keyboard to a person). On the iOS simulator: hardware keyboard off (I/O → Keyboard → Connect Hardware Keyboard) so the soft keyboard shows as on a phone.
- Only **one** Maestro run at a time (port 7001). Large screenshots over Maestro's 4 MB: shrink the screen (`wm size` + `wm density`, same dp) and reset after.

## 2. The robot flows

- Start from `ferramentas/qa/maestro-exemplo/` (Trilha dos Bichos's flows: carousel → setup → captures → ending → credits, split in parts, plus iOS subflows). Ids are the iOS accessibility identifiers = Android `testTag`s, so one flow runs on both; whichever app is the reference, its ids are the names the target copies.
- Parameterise per cycle/theme (`run-cycles.sh <device> <label> <appId> <cycles…>`). Add `scrollUntilVisible` before taps on elements that may be below the fold (large fonts, short screens), but never before fixed bars (they never "appear" by scrolling).
- Debug-only shortcuts help reach one screen fast (Trilha dos Bichos: `--es startGame <cycle> --es debugScreen <screen>` on Android; a launch argument does the same on iOS), but a full run still proves the path.

## 3. Side by side, score, Diff

- `ferramentas/qa/bin/lado_a_lado.py` builds one image per screen (Figma | iOS | Android | Diff) and `proximidade.json`; `test-checklist/ferramentas/comparar.py` gives the checklist card's comparison box (A = reference, B = target).
- Read the score: ≥ 95% green, ≥ 85% amber, below red. Video/animated screens and live camera score low even when right.

## 4. Findings, one at a time

- `ferramentas/qa/bin/achados_html.py` makes the findings page: one tab per cycle, one card per difference (id `F-<CYCLE>-NN`, severity, what the QA saw, expected = what the reference shows, evidence, probable cause with `file:line` in the target), plus tabs for reference-version changes, **Melhorias** and **Correções**.
- Go through the cards **one at a time** with the person. A short reply in the conversation is conversation: ask "posso registrar como decidido?" before writing a decision. When a finding is closed, its twins in other cycles close with "vinculado ao …".
- Fixes go to `/conversion-fidelity`; problems only the target platform has go to `/conversion-android` (target Android) or `/conversion-ios` (target iPhone). Back up the page before each edit; keep a copy where the person keeps their deliverables.

## 5. A new version of the reference

- Pull the new reference version, list every change since the pinned one (commits and screens), and add a tab with one card per change: what changed, effect on the open findings, what the target does today. Mirror it with `/conversion-prepare` §1 (checkpoint tag, part by part) and re-run this walk.

## 6. Prints and rounds

- One folder per round and device (`images/<checklist>/rodadaN-<scope>/<device>/`), nothing loose; checklist prints JPG 720 px, quality 72; the original PNG only in the scratchpad. Never delete prints: rename obsolete ones `-REMOVIDO`.
