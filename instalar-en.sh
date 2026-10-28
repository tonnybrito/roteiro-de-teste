#!/bin/zsh
# Installs the family's skills (test-checklist, bdd-first and the iPhone ⇄ Android conversion skills, either way) into ~/.claude/skills.
# /test-checklist is the base of the conversion skills: it ALWAYS comes first when one of them is chosen. English edition.
# A /bdd-first funciona sozinha: escolhida sozinha, entra sem a /test-checklist.
#   zsh instalar-en.sh                                  menu: 1 only test-checklist · 2 choose · 3 all
#   zsh instalar-en.sh --todas                          sem menu, instala todas as que o pacote tem
#   zsh instalar-en.sh --skills conversion-prepare,...  no menu, only those named (+ test-checklist if a conversion skill is named)
# Before replacing an existing skill that differs, keeps a copy in ~/Ferramentas/html-salvavel/backups/.
set -e
AQUI="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.claude/skills"
BK="$HOME/Ferramentas/html-salvavel/backups/skills-$(date +%Y%m%d-%H%M%S)"
CONVERSAO=(conversion-prepare conversion-fidelity conversion-parity conversion-android conversion-ios)
FAMILIA=(bdd-first $CONVERSAO)
typeset -a ESCOLHA
existe() { [[ -d "$AQUI/skills-en/$1" ]]; }

case "$1" in
  --todas) for s in $FAMILIA; do existe $s && ESCOLHA+=($s); done; ESCOLHA+=(test-checklist) ;;
  --skills) ESCOLHA=(${(s:,:)2}) ;;
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
  *) echo "usage: zsh instalar-en.sh [--todas | --skills a,b]"; exit 1 ;;
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

# What /test-checklist needs outside the skills: only a warning; the skill itself asks before installing
[[ -d "$HOME/Ferramentas/html-salvavel" ]] || echo "! Missing the tool that saves into the HTML: ask Claude for \"/test-checklist\" (step 1) or copy skills-en/test-checklist/pacote to ~/Ferramentas/html-salvavel"
[[ -d "$HOME/Applications/Abrir HTML Salvável.app" ]] || echo "! Missing the Dock app: zsh ~/Ferramentas/html-salvavel/app/instalar-app.sh"
for a in independent-qa independent-auditor; do
  [[ -f "$HOME/.claude/agents/$a.md" ]] || echo "! Missing the agent $a: cp -p \"$AQUI/skills-en/test-checklist/pacote/agentes/$a.md\" ~/.claude/agents/"
done
echo "Done. Restart Claude Code for the new skills to show up."
