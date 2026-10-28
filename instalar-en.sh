#!/bin/zsh
# Installs the family's skills (test-checklist, bdd-first and the iPhone ⇄ Android conversion skills, either way) into ~/.claude/skills. English edition.
# /test-checklist is the base of the conversion skills: it ALWAYS comes first when one of them is chosen.
# /bdd-first works alone: chosen alone, it is installed without /test-checklist.
#   zsh instalar-en.sh                                  menu: 1 only test-checklist · 2 choose · 3 all
#   zsh instalar-en.sh --todas                          no menu, installs every skill the package has
#   zsh instalar-en.sh --skills conversion-prepare,...  no menu, only those named (+ test-checklist if a conversion skill is named)
#   --atalhos yes|no                                 with test-checklist: the editable-HTML button in the Dock and on the Desktop
#                                                    (without it, asks; with no terminal to ask, does not create them)
# Before replacing an existing skill that differs, keeps a copy in ~/Ferramentas/html-salvavel/backups/.
# At the end, opens GUIA.html in the browser, on the installed skill's tab, showing what is installed.
set -e
AQUI="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.claude/skills"
BK="$HOME/Ferramentas/html-salvavel/backups/skills-$(date +%Y%m%d-%H%M%S)"
CONVERSAO=(conversion-prepare conversion-fidelity conversion-parity conversion-android conversion-ios)
FAMILIA=(bdd-first $CONVERSAO)
typeset -a ESCOLHA
existe() { [[ -d "$AQUI/skills-en/$1" ]]; }

MODO="" LISTA="" ATALHOS=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --todas) MODO=todas ;;
    --skills) MODO=lista; LISTA="$2"; shift ;;
    --atalhos) ATALHOS="$2"; shift ;;
    *) echo "usage: zsh instalar-en.sh [--todas | --skills a,b] [--atalhos yes|no]"; exit 1 ;;
  esac
  shift
done

case "$MODO" in
  todas) for s in $FAMILIA; do existe $s && ESCOLHA+=($s); done; ESCOLHA+=(test-checklist) ;;
  lista) ESCOLHA=(${(s:,:)LISTA}) ;;
  "")
    echo "Skill family: /test-checklist, /bdd-first and the iPhone ⇄ Android conversion skills"
    echo "/test-checklist is the base of the conversion skills and comes first when one of them is chosen."
    echo "  1) only /test-checklist"
    echo "  2) choose"
    echo "  3) all"
    read "op?Pick 1, 2 or 3: "
    case "$op" in
      1) ESCOLHA=(test-checklist) ;;
      2) for s in $FAMILIA; do
           if existe $s; then read "r?Install /$s? (y/n) "; [[ "$r" == [yY]* ]] && ESCOLHA+=($s)
           else echo "  /$s: not created yet"; fi
         done ;;
      3) for s in $FAMILIA; do existe $s && ESCOLHA+=($s); done; ESCOLHA+=(test-checklist) ;;
      *) echo "Invalid option: nothing was installed."; exit 1 ;;
    esac ;;
esac

for s in $ESCOLHA; do
  existe $s || { echo "Unknown skill or not created yet: $s (nothing was installed)"; exit 1; }
done
# /test-checklist comes first when any conversion skill is chosen.
for s in $ESCOLHA; do
  (( ${CONVERSAO[(Ie)$s]} )) && { ESCOLHA=(test-checklist ${ESCOLHA:#test-checklist}); break; }
done
[[ ${#ESCOLHA} -gt 0 ]] || { echo "Nothing chosen: nothing was installed."; exit 0; }

mkdir -p "$DEST"
for s in roteiro-de-teste bdd-antes conversao-preparar conversao-fidelidade conversao-paridade conversao-android conversao-ios; do
  [[ -d "$DEST/$s" ]] && echo "! The Portuguese edition is installed (/$s). Both editions do the same thing: keep only one (remove ~/.claude/skills/$s to switch)."
done
instala() {
  local nome=$1 origem="$AQUI/skills-en/$1" alvo="$DEST/$1"
  if [[ -d "$alvo" ]]; then
    if diff -rq "$origem" "$alvo" >/dev/null 2>&1; then echo "= /$nome is already up to date"; return; fi
    mkdir -p "$BK"; cp -Rp "$alvo" "$BK/$nome"
    echo "  backup of the old version: $BK/$nome"
    rm -rf "$alvo"
  fi
  cp -Rp "$origem" "$alvo"
  echo "+ /$nome installed"
}

for s in $ESCOLHA; do instala $s; done

# The editable-HTML button: the saving tool, the "Abrir HTML Salvável" app and its shortcut in the Dock and on the Desktop.
HS="$HOME/Ferramentas/html-salvavel"
APP="$HOME/Applications/Abrir HTML Salvável.app"
DOCK=nao MESA=nao
if [[ -d "$DEST/test-checklist" ]]; then
  if [[ -z "$ATALHOS" ]]; then
    if [[ -t 0 ]]; then
      echo
      echo "/test-checklist opens the editable HTML pages through a button: the \"Abrir HTML Salvável\" app (Open Saveable HTML)."
      read "r?Put that button in the Dock and on the Desktop? (y/n) "
      [[ "$r" == [yY]* ]] && ATALHOS=sim || ATALHOS=nao
    else
      ATALHOS=nao
    fi
  fi
  if [[ "$ATALHOS" == (sim|yes) ]]; then
    mkdir -p "$HS"
    cp -Rp "$DEST/test-checklist/pacote/." "$HS/"
    chmod +x "$HS/abrir-html-salvavel.command" "$HS/servidor.py" "$HS/abrir-pasta.sh" 2>/dev/null || true
    zsh "$HS/app/instalar-app.sh" >/dev/null 2>&1 && echo "+ \"Abrir HTML Salvável\" app in ~/Applications"
    if [[ -z "$SEM_DOCK" ]] && command -v defaults >/dev/null; then
      if ! defaults read com.apple.dock persistent-apps 2>/dev/null | grep -q "Abrir%20HTML%20Salv"; then
        URL="file://$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1]))' "$APP")/"
        defaults write com.apple.dock persistent-apps -array-add "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>$URL</string><key>_CFURLStringType</key><integer>15</integer></dict></dict></dict>"
        killall Dock 2>/dev/null || true
        echo "+ button in the Dock"
      else
        echo "= the button is already in the Dock"
      fi
    fi
    mkdir -p "$HOME/Desktop"
    ln -sfn "$APP" "$HOME/Desktop/Abrir HTML Salvável.app"
    ln -sfn "$AQUI/GUIA.html" "$HOME/Desktop/Skills guide.html"
    echo "+ on the Desktop: \"Abrir HTML Salvável\" and \"Skills guide\""
  fi
fi
# What really exists (from this install or an earlier one), for the guide to show.
[[ -e "$HOME/Desktop/Abrir HTML Salvável.app" ]] && MESA=sim
[[ -z "$SEM_DOCK" ]] && defaults read com.apple.dock persistent-apps 2>/dev/null | grep -q "Abrir%20HTML%20Salv" && DOCK=sim

# The guide shows what is installed: the installer writes instaladas.js next to GUIA.html.
TODAS=(roteiro-de-teste bdd-antes conversao-preparar conversao-fidelidade conversao-paridade conversao-android conversao-ios test-checklist bdd-first $CONVERSAO)
typeset -a TEM
for s in $TODAS; do [[ -d "$DEST/$s" ]] && TEM+=("\"$s\""); done
cat > "$AQUI/instaladas.js" <<EOF
// Written by the installer on $(date "+%Y-%m-%d %H:%M"). Do not edit: run the installer again.
window.INSTALADAS = {"skills": [${(j:, :)TEM}], "abrir": "${ESCOLHA[-1]}", "quando": "$(date +%s)", "dock": "$DOCK", "mesa": "$MESA"};
EOF

for a in independent-qa independent-auditor; do
  if [[ -d "$DEST/test-checklist" && ! -f "$HOME/.claude/agents/$a.md" ]]; then
    echo "! Missing the agent $a: cp -p \"$AQUI/skills-en/test-checklist/pacote/agentes/$a.md\" ~/.claude/agents/"
  fi
done
echo "Done. Restart Claude Code for the new skills to show up."
echo "Opening the skills guide in the browser: $AQUI/GUIA.html"
[[ -n "$SEM_ABRIR" ]] || open "$AQUI/GUIA.html" 2>/dev/null || true
