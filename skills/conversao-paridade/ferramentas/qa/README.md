# QA tools (round R3, 15/10/2026)

Tools used to capture both apps screen by screen and compare them. Working files go to `$QA_WORK`
(default `./qa-work`, git-ignored).

## Capture (Maestro)
- `maestro/run-cycles.sh <device> <label> <appId> <cycles…>` plays carousel → setup → save signs → 9 captures →
  ending → Hunt Complete → credits/ads → carousel, saving screenshots to `maestro/shots/<label>/`.
  iOS appId `com.exemplo.trilhadosbichos.ios` (Debug build), Android `com.exemplo.trilhadosbichos`.
  `PLAY_J4="PLAY 4TH OF JULY TRAIL"` for iOS 1.6.26+ and the current Android.
- Only one Maestro run at a time (port 7001). Before a run: close other apps on the device, mute the Mac for
  the iOS simulator, `adb shell settings put secure show_ime_with_hard_keyboard 0` on the emulator.
- On the Pixel 9 Pro XL, July's screenshots exceed Maestro's 4 MB limit at native resolution: run with
  `wm size 1008x2244` + `wm density 360` (same dp layout), then `wm size reset` / `wm density reset`.

## Compare
- `bin/lado_a_lado.py <shots> <iosLabel> <androidLabel> <figmaDir> <out> [cycle]` — one image per screen
  (Figma | iOS | Android | Diff) and `proximidade.json` (iOS × Android %).
- `bin/diff_par.py A kind B kind prefix` — one pair: raw/aligned %, region grid, two-colour diff.
- `bin/card_img.py`, `bin/comparacao_html.py` — static card image / interactive comparison page.

## Findings
- `bin/gera_md.py findings.json` — one Markdown report per finding in `qa-relatorios/<round>/<cycle>/`.
- `bin/conclui_md.py report.md "<status>" "<decision text>"` — records a decision.
- `bin/achados_html.py <findings.json…> --out <page.html>` — the findings page (tabs per cycle).
  Env: `QA_DIR` (composites dir under `$QA_WORK`), `V26=1` (iOS-change marks from `$QA_WORK/ios26/mapa.json`).

## Misc
- `bin/ui.sh <adb device>` — dumps visible ids/texts/bounds on Android.
- `bin/aviso.sh "<mensagem>"` — loud alert + spoken pt-BR message (raises the volume only while speaking).
