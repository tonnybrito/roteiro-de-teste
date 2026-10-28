---
name: conversion-prepare
description: Start or refresh a conversion between iPhone and Android, in either direction (SwiftUI app to Kotlin/Jetpack Compose, or Compose to SwiftUI) - choose the direction, pin the reference app (the behavioural oracle) and its version, inventory screens, strings, assets, videos and fonts, set up converters (never hand-edit generated resources), map SwiftUI and Compose patterns, write the house rules, and open round 1 of the test checklist. First skill of the conversion package; installs the package (test-checklist first) on first use. Triggers include "/conversion-prepare", "vamos converter esse app para Android", "vamos converter esse app para iPhone", "prepara a conversão", "saiu versão nova do iOS", "saiu versão nova do Android", "espelhar a versão nova".
---

# /conversion-prepare — 1 · Prepare the conversion

A conversion has a **reference** app (the *oracle*: every flow, rule and string comes from it) and a **target** app (the one being built). It goes either way: iPhone → Android or Android → iPhone. This skill decides the direction once, records it, and builds the ground the other skills walk on. The iPhone → Android direction came out of the Trilha dos Bichos port (iOS `trilhadosbichos-ios` → `trilhadosbichos-android`), and its examples cite it; the Android → iPhone direction uses the same steps read from the other side.

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

## 1. Choose the direction and pin the oracle

- Ask the direction: **iPhone → Android** (the iOS app is the reference) or **Android → iPhone** (the Android app is the reference). One question, then wait.
- Find the reference project (ask for the path) and **which version** is the reference (iOS: tag, commit or the version in `Info.plist`; Android: tag, commit or `versionName` in `build.gradle(.kts)`).
- Write both down in the target project's `CLAUDE.md`, in one block every conversion skill reads first:
  `Conversion: <iPhone → Android | Android → iPhone>. Reference (oracle): <platform> app at <path>, version <x.y.z>. Target: <platform>.`
- Ask what is **out of scope** (e.g. Trilha dos Bichos: credits/ads differ by decision) and record it.
- If a certification matrix or Figma exists, link them. **Figma wins on line breaks** only where the target already matches Figma; otherwise the reference wins.
- When the reference ships a new version mid-way: tag a checkpoint (`git tag checkpoint-antes-<reference>-<ver>`), list every change since the last reference (one row per change: screens, effect on the target, linked findings), mirror it part by part with one commit each, and re-capture both apps.

## 2. Inventory the reference

List, from the **reference** project (in the scratchpad, then show a summary):

| | Reference is iOS | Reference is Android |
|---|---|---|
| **Screens** and the order between them | every navigated `View`; `NavigationStack` / `.navigationDestination` / `.sheet` | every `NavHost` destination and dialog; the nav graph |
| **Strings** | `.xcstrings` / `Localizable.strings`, per theme or cycle prefix | `res/values*/strings.xml`, per locale and prefix |
| **Assets** | `.xcassets` image sets (variants per theme), fonts | `res/drawable*` / `mipmap*` (densities), `res/font` |
| **Videos** | bundle videos, and whether they need alpha | `res/raw` / assets videos, and whether they need alpha |
| **Behaviour** | rules and controllers with XCTest tests | rules and controllers with JVM tests |

Behaviour tests on the reference become tests on the target (XCTest ⇄ JVM), written first.

## 3. Converters, never hand edits

Generated resources are regenerated, never edited. One script per kind, run in the conversion's direction:
- strings: `.xcstrings` → `res/values/strings.xml` (Trilha dos Bichos: `tools/convert_strings.py`), or `strings.xml` → `.xcstrings`; keys prefixed by cycle/theme, read through one accessor (Android `theme.text(key)`, iOS a `String(localized:)` wrapper);
- images and fonts: one import script and **one naming rule** (Trilha dos Bichos: `tools/import_assets.py`, `AssetNames.resourceName`; themed lookup through `theme.assetName(base)`). Android → iOS goes from the densities to `@1x/@2x/@3x` image sets (prefer vectors as PDF/SVG). **Never strip suffixes by hand** (one past bug came from stripping only two);
- videos: one script (Trilha dos Bichos: `tools/convert_videos.sh`), alpha videos kept transparent on both sides (HEVC with alpha on iOS).
Propose these scripts before writing them; run them once and diff the output.

## 4. SwiftUI ⇄ Compose map

Agree the translations and put the table in the target's `docs/architecture.md`. Read it left to right for iPhone → Android, right to left for Android → iPhone:

| SwiftUI | Compose |
|---|---|
| `NavigationStack` / `.navigationDestination` | one `NavHost`, navigation wired only there |
| `.sheet(item:)` | nullable state `var item by remember { mutableStateOf<T?>(null) }` (never a boolean plus an optional) |
| `ZStack` / `VStack` / `HStack` / `Spacer()` | `Box` / `Column` / `Row` / `Spacer(Modifier.weight(1f))` |
| `GeometryReader` | `BoxWithConstraints` |
| `.padding(.top, -30)` | a `layout {}` that also gives back the room (an `offset` only moves the picture) |
| `@State` / `@Observable` (or `@Published` + `ObservableObject`) | `remember` / `StateFlow` in a controller read through a `CompositionLocal` |
| `.environment(...)` | `CompositionLocalProvider` |
| SwiftData / Core Data | Room, the source of truth; remote sync mirrors into it |
| `AVPlayer` | Media3 (`AlphaVideoView` for alpha videos) |
| `.accessibilityIdentifier("x")` | `Modifier.testTag("x")` (same names, so robot flows port) |
| `.onAppear` / `.task` | `LaunchedEffect` / `DisposableEffect`, never side effects in composition |
| `@FocusState` | `FocusRequester` |
| `.onPreferenceChange` / `GeometryReader` reading a frame | `onGloballyPositioned` |

Read the **reference implementation**, not just the call site: Trilha dos Bichos passed `bubbleWidthRatio` that iOS's `GuideDialog` never read; applying it on Android broke line breaks. The same trap exists the other way: a Compose parameter with a default the code never overrides.

## 5. House rules (write them in the target's CLAUDE.md)

- Behaviour is shared across themes; a theme changes only presentation (an exhaustive `when` / `switch` over the theme type, never `if (theme == "xmas")` for behaviour).
- TDD for logic: rules, validators, controllers and **layout rules** are pure functions with tests written first (JVM tests on Android, XCTest on iOS).
- Feature branches; build and tests pass before every handoff; one commit per fix or improvement, saying which reference version/commit it mirrors.
- Prints are never deleted (obsolete ones renamed `-REMOVIDO`); one folder per round and device.

## 6. Open round 1 and hand off

- With `/test-checklist`, create the product's checklist: one card per screen or flow to compare with the reference (tabs follow the app's sections).
- Show the plan (screens in order), then hand off: screen-by-screen fidelity → `/conversion-fidelity`; whole-app comparison runs → `/conversion-parity`; what only the target platform has → `/conversion-android` (target Android) or `/conversion-ios` (target iPhone).
