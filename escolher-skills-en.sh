#!/bin/zsh
# Choice window of the skill family (step 0 of every skill in the family). English edition.
#   zsh escolher-skills-en.sh
# On macOS it opens a native popup with the seven skills and the state of each, and prints
# the chosen ones separated by commas (e.g. "bdd-first,conversion-android"), or CANCELADO.
# Off macOS it prints SEM-POPUP and exits 3: the skill then asks through Claude's own window.
AQUI="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.claude/skills"
FAMILIA=(test-checklist bdd-first conversion-prepare conversion-fidelity conversion-parity conversion-android conversion-ios)
typeset -A FAZ
FAZ=(
  test-checklist      "HTML test checklists that save (base of the conversion skills)"
  bdd-first             "BDD before code: features, steps, runner and the page linked to the checklist"
  conversion-prepare    "start an iPhone ⇄ Android conversion, either way"
  conversion-fidelity  "make one screen match the reference app, pixel by pixel"
  conversion-parity    "a robot compares the whole app on both phones"
  conversion-android     "Android target: large font, keyboard, back, Play Store"
  conversion-ios         "iPhone target: large text, island, keyboard, swipe-back, App Store"
)

situacao() {
  local s=$1
  [[ -d "$AQUI/skills-en/$s" ]] || { echo "not created yet"; return; }
  [[ -d "$DEST/$s" ]] || { echo "missing"; return; }
  diff -rq --exclude backups "$AQUI/skills-en/$s" "$DEST/$s" >/dev/null 2>&1 && echo "installed" || echo "outdated"
}

if [[ "$(uname)" != Darwin ]] || ! command -v osascript >/dev/null; then
  for s in $FAMILIA; do echo "$s: $(situacao $s)" >&2; done
  echo SEM-POPUP; exit 3
fi

itens=()
for s in $FAMILIA; do itens+=("/$s  ·  $(situacao $s)  ·  ${FAZ[$s]}"); done

# Lista AppleScript: {"a", "b", ...}, com aspas escapadas.
lista="{$(for i in $itens; do printf '"%s",' "${i//\"/\\\"}"; done | sed 's/,$//')}"

escolha=$(osascript <<EOF
with timeout of 1800 seconds
tell application "System Events"
  activate
  set r to choose from list $lista with title "Skill family" with prompt "Tick the skills you want in this project (⌘ + click to tick several). /test-checklist is the base: it comes first if you pick a conversion skill." with multiple selections allowed and empty selection allowed OK button name "Continue" cancel button name "Cancel"
end tell
end timeout
if r is false then return "CANCELADO"
set AppleScript's text item delimiters to "|"
return r as text
EOF
)

# Sem resposta do popup (erro do AppleScript): a skill cai para a janela do Claude.
[[ $? -eq 0 ]] || { echo SEM-POPUP; exit 3; }
[[ "$escolha" == CANCELADO ]] && { echo CANCELADO; exit 0; }
nomes=()
for i in ${(s:|:)escolha}; do nomes+=("${${i%%  ·  *}#/}"); done
echo "${(j:,:)nomes}"
