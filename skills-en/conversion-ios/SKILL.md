---
name: conversion-ios
description: When the iPhone is the target of a conversion (Android → iPhone), check and fix what the Android version never covers on iOS - Dynamic Type (default, middle, accessibility sizes), small and large iPhones, the Dynamic Island, notch and home indicator, the keyboard covering fields, the swipe-back gesture, light/dark, and the App Store build (Release, privacy manifest, permission texts, TestFlight) - labelling every change as a fix (correção) or an improvement over Android (melhoria), each with its own commit and a proposal back to Android. Mirror of conversion-android. Part of the iPhone ⇄ Android conversion package; needs test-checklist. Triggers include "/conversion-ios", "testa com letra grande no iPhone", "no iPhone ficou cortado", "a ilha cobre o título", "o teclado cobre o campo no iPhone", "o gesto de voltar perde o jogo", "prepara para a App Store".
---

# /conversion-ios — 4 · Beyond Android

For conversions whose **target is the iPhone** (Android → iPhone). A port can match the Android app pixel for pixel and still break on real iPhones. This skill sweeps those cases, one at a time with the person, and keeps a clear line between **correção** (the iPhone broke something Android does right) and **melhoria** (the iPhone goes beyond Android). It mirrors `/conversion-android`; its rules are starting points, refined by the first real project that uses them, so every number below is measured on the project, never copied.

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

## 1. Dynamic Type sweep

- Capture every screen at the default size, at a middle size and at the largest accessibility size: `xcrun simctl ui <device> content_size large`, `extra-extra-large` and `accessibility-extra-extra-extra-large`; put the three side by side for the person. Reset to `large` after.
- Text must use text styles or `@ScaledMetric` so it follows the setting at all; a fixed `.font(.system(size:))` does not grow. Decide per kind of text, with an XCTest on each rule:
  - **Titles and display text**: cap the growth (`.dynamicTypeSize(...DynamicTypeSize.xxxLarge)`) and **never break inside a word** (`.minimumScaleFactor` with `.lineLimit`, or a rule that shrinks until every word fits).
  - **Buttons side by side** keep the same size: one label shrinks to one line, both keep the height of the full-size line.
  - **Tables of values** become rows, labels top-aligned; `ViewThatFits` or a stacked layout at accessibility sizes.
  - **Content pushed below the fold** scrolls (`ScrollView`), with a visible hint that there is more.

## 2. Screens, safe areas and keyboard

- Run on the smallest supported iPhone (iPhone SE, 375 × 667 pt, home button, no island) and the largest (Pro Max), plus the reference size used by `/conversion-fidelity`.
- Safe areas: nothing important under the **Dynamic Island** / notch or the **home indicator**; backgrounds may bleed (`.ignoresSafeArea()` on the background only, never on content). Android status and navigation bars are not the same size: measure, never copy dp offsets.
- Things that overlap there but not on the Android reference get a **measured** rule with an XCTest.
- Keyboard: fields stay visible as it rises (`ScrollViewReader` + `@FocusState`, `.scrollDismissesKeyboard`, `.safeAreaInset(edge: .bottom)` for bars); a field that appears scrolls into view on its own.
- **Swipe back** (edge gesture) and the back button must do what Android's system back does: if Android shows an exit dialog or protects progress, the iPhone must too (`.navigationBarBackButtonHidden` plus an explicit control, or `interactiveDismissDisabled` on sheets). Never lose progress to a swipe.
- Light and dark appearance, if the Android app supports both.

## 3. The App Store build

- Build the **Release** configuration at least once (optimised, no debug hooks; a "QA" scheme with the hooks if the robot needs them) and run the robot on it.
- Check what review asks for: every permission the app requests has its usage text in `Info.plist` (camera, photos, location…), the privacy manifest `PrivacyInfo.xcprivacy` lists data and required-reason APIs, App Tracking Transparency if ads track, icons and launch screen complete.
- Remote services kept off on purpose leave a loud alert in the Release build and in the docs, and a store checklist: TestFlight internal testing on a few real iPhones, the remote service decision, the App Store review notes.

## 4. Correção or melhoria

- Ask the person which one it is when it is not obvious; Android doing the same wrong thing makes it a **melhoria**.
- One commit each: `area: fix …` or `area: improvement - …`, saying Android does/doesn't do it.
- Record it in the findings page tabs **🔧 Correções** / **✨ Melhorias** with before × after, and mark the melhorias as "proposta para levar ao Android".
