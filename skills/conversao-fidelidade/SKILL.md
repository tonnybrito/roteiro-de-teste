---
name: conversao-fidelidade
description: Make one screen of the target app match its original in the reference app, pixel by pixel, in either direction (Android matching the iPhone, or the iPhone matching Android) - side-by-side screenshots, measure colours, sizes, spacing, font metrics and line breaks from the reference pixels (never guess), turn each measure into a pure layout rule with a test written first, re-capture, score the proximity and show before/after for approval before moving on. Part of the iPhone ⇄ Android conversion package; needs roteiro-de-teste. Triggers include "/conversao-fidelidade", "deixa essa tela igual ao iPhone", "deixa essa tela igual ao Android", "a tela X está diferente", "mede no print de referência", "corrige o achado F-…".
---

# /conversao-fidelidade — 2 · Pixel fidelity

**One screen at a time.** The person sees the reference and the target side by side, approves, and only then the next screen starts. Measures come from the **reference** app's pixels; nothing is eyeballed. Read the direction first: the `Conversion:` block in the target's `CLAUDE.md` (written by `/conversao-preparar`). If it is missing, ask which app is the reference.

## 0. The skill family (first, every time)

This skill belongs to a **family** kept in `~/Ferramentas/conversao-ios-android/` (guide in `GUIA.html` there):
- `roteiro-de-teste`: the saveable HTML checklists. The base of the conversion skills.
- `bdd-antes`: BDD before code (Gherkin features, steps, runner and the linked BDD page). It works **with or without** `roteiro-de-teste`; when both are in a project, the checklist links to the BDD.
- `conversao-preparar`, `conversao-fidelidade` and `conversao-paridade`: the conversion between iPhone and Android, **both ways** (iPhone → Android or Android → iPhone; `conversao-preparar` records which app is the reference). `conversao-android` and `conversao-ios`: what only the target platform has. Each works alone; all need `roteiro-de-teste`.

1. Check each of the seven: present in `~/.claude/skills/`, and the same as the package copy (`diff -rq ~/.claude/skills/<name> ~/Ferramentas/conversao-ios-android/skills/<name>`). A skill missing from the package's `skills/` is "ainda não criada".
2. **Always open the choice window**, even when everything is installed. Before it, say that `/roteiro-de-teste` is the base: it is installed first whenever a conversion skill is chosen, and cannot be left out then. Never install without the answer.
   - **On macOS: a native popup.** Run `zsh ~/Ferramentas/conversao-ios-android/escolher-skills.sh` with the Bash timeout at 600000 (the person may take a while). It shows the seven skills, each with its state and what it does, and prints the chosen names separated by commas, or `CANCELADO`, or nothing when none was marked. Tell the person the popup is open on the screen.
   - **Elsewhere** (the script prints `SEM-POPUP` and exits 3), use the Claude window instead: **one** AskUserQuestion holding three questions, all `multiSelect: true` (a question holds at most four options): header "BDD" with `/bdd-antes` plus "Nenhuma"; header "Conversão" with `/conversao-preparar`, `/conversao-fidelidade`, `/conversao-paridade` plus "Nenhuma"; header "Plataforma" with `/conversao-android`, `/conversao-ios` plus "Nenhuma". Each option's description says what the skill does and its state.
   - States: **instalada**, **falta**, **desatualizada** or **ainda não criada**. A chosen skill that is "ainda não criada" cannot be installed: say so.
3. Install only what was chosen and is missing or outdated: `zsh ~/Ferramentas/conversao-ios-android/instalar.sh --skills <comma-separated names>`. It puts `roteiro-de-teste` first when a conversion skill is chosen, installs `bdd-antes` alone when only it is chosen, skips what is up to date, refuses a skill the package does not have, and backs up anything it replaces. A chosen skill that is installed and up to date needs nothing: say so.
4. Then, when this skill uses checklists, run `roteiro-de-teste` step 1 ("Prepare the saving"): the saving tool, the Dock app "Abrir HTML Salvável" and the QA/Auditor agents, each asked first.
5. New skills and agents load only in a new session: if something was installed, ask the person to restart Claude Code, and stop here.

Talk to the person in their language, by the name saved in `~/Ferramentas/html-salvavel/nome.txt` (the `roteiro-de-teste` step 1 asks for it; until then, their `whoami` name). If their CLAUDE.md says how to work with them (tutor style, one thing at a time, one question per message, asking before every action), follow it.

## 1. Put both screens side by side

- The reference screenshot of the **reference version** (from `/conversao-paridade` captures, the simulator or the emulator) and the target one at the same logical width (Trilha dos Bichos: iPhone 17, 402 pt wide; Android emulator at the same dp width). Note device and OS on both.
- Build the comparison with `roteiro-de-teste/ferramentas/comparar.py A B <prints folder> <name> --la ... --lb ...`, with **A = reference** and **B = target**; show the score and the Diff's worst regions. That is the "before".

## 2. Measure, never guess

- **Colours**: read the pixel on the reference screenshot (`magick img.png -crop 1x1+X+Y txt:`), sampling flat areas, never antialiased edges or glows. Record which screenshot and OS (Trilha dos Bichos measured on iOS 26.2).
- **Sizes and spacing**: convert screenshot pixels to logical units and use the same number on the target. iPhone: pixels ÷ scale (@2x/@3x) = points. Android: pixels ÷ (density ÷ 160) = dp (`adb shell wm density`). 1 pt ↔ 1 dp.
- **Safe areas are not insets.** iPhone safe areas (Dynamic Island, home indicator) and Android system bars differ: measure from the visible top of the content, not the screen edge (Trilha dos Bichos: July's name sat 7% of the *safe area* below a 59 pt island = 13% of the screen).
- **Fonts**: the line height is the font's own metrics (hhea ascent + descent + line gap, per em) plus SwiftUI `.lineSpacing` on iOS, or Compose `lineHeight` / `includeFontPadding` / `LineHeightStyle` on Android; never a guessed multiplier. Where lines break, measure the widest line that fits and the narrowest that breaks on the reference: SwiftUI wraps a few points short of its frame (Trilha dos Bichos: 6 pt, `WRAP_INSET`), Compose wraps at the frame.
- **Line breaks only** (same size, different word on the second line) are accepted when the person says so; if the target already matches Figma, Figma wins.
- **Pop-ups and texts** are an exact replica: same copy, same size, same moment they appear.
- Read the reference layout code too (`file:line`) and cite it in a comment next to the target's rule.

## 3. Rule first, then the screen

- Each measure that is a decision ("the frame rises until it clears the bubble") becomes a **pure function** in a small type with a **test written first**: JVM test in a Kotlin `object` on Android (Trilha dos Bichos: `ScanFrameLift`, `CaptureLayout.trapYOffset`, `CarouselButtonWidth`, `JackBubbleRules`), XCTest on a Swift `enum` with static functions on iOS. Run it red, then green.
- Then use it in the screen. Measure real positions when the answer depends on other elements: `onGloballyPositioned` on Android (first in the modifier chain, so it is the element's own box); `GeometryReader` + a `PreferenceKey` (or `.onGeometryChange`) on iOS.
- Keep the reference in the doc comment (KDoc / `///`): version, file, commit.

## 4. Re-capture and show

- Build, install, capture the same screen in **every theme/cycle** it exists in; run `comparar.py` again (the "after"). Video or animated screens score low even when right; say so.
- Show before × after to the person (a page or an image on the Desktop / their chosen folder) and ask whether it can be approved. Fix divergences directly; move to another screen only after their check.
- Commit one fix per commit (`area: fix …` with the reference version). Update the checklist card and the findings page; a finding with twins in other cycles closes with "vinculado ao …".
- Prints for the checklist: JPG 720 px wide, quality 72, in the round's folder; never delete a print.
