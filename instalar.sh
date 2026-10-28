#!/bin/zsh
# Instala as skills da família (roteiro-de-teste, bdd-antes e as de conversão iPhone ⇄ Android, nos dois sentidos) em ~/.claude/skills.
# A /roteiro-de-teste é a base das de conversão: entra SEMPRE primeiro quando uma delas é escolhida.
# A /bdd-antes funciona sozinha: escolhida sozinha, entra sem a /roteiro-de-teste.
#   zsh instalar.sh                                  menu: 1 só a roteiro-de-teste · 2 escolher · 3 todas
#   zsh instalar.sh --todas                          sem menu, instala todas as que o pacote tem
#   zsh instalar.sh --skills conversao-preparar,...  sem menu, só as citadas (+ roteiro-de-teste se houver uma de conversão)
#   --atalhos sim|nao                                com a roteiro-de-teste: o botão do HTML editável no Dock e na Mesa
#                                                    (sem a opção, pergunta; sem terminal para perguntar, não cria)
# Antes de trocar uma skill que já existe e é diferente, guarda uma cópia em ~/Ferramentas/html-salvavel/backups/.
# No fim, abre o GUIA.html no navegador, na aba da skill instalada, mostrando só o que está instalado.
set -e
AQUI="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.claude/skills"
BK="$HOME/Ferramentas/html-salvavel/backups/skills-$(date +%Y%m%d-%H%M%S)"
CONVERSAO=(conversao-preparar conversao-fidelidade conversao-paridade conversao-android conversao-ios)
FAMILIA=(bdd-antes $CONVERSAO)
typeset -a ESCOLHA
existe() { [[ -d "$AQUI/skills/$1" ]]; }

MODO="" LISTA="" ATALHOS=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --todas) MODO=todas ;;
    --skills) MODO=lista; LISTA="$2"; shift ;;
    --atalhos) ATALHOS="$2"; shift ;;
    *) echo "uso: zsh instalar.sh [--todas | --skills a,b] [--atalhos sim|nao]"; exit 1 ;;
  esac
  shift
done

case "$MODO" in
  todas) for s in $FAMILIA; do existe $s && ESCOLHA+=($s); done; ESCOLHA+=(roteiro-de-teste) ;;
  lista) ESCOLHA=(${(s:,:)LISTA}) ;;
  "")
    echo "Família de skills: /roteiro-de-teste, /bdd-antes e as de conversão iPhone ⇄ Android"
    echo "A /roteiro-de-teste é a base das de conversão e entra primeiro quando uma delas é escolhida."
    echo "  1) só a /roteiro-de-teste"
    echo "  2) escolher"
    echo "  3) todas"
    read "op?Escolha 1, 2 ou 3: "
    case "$op" in
      1) ESCOLHA=(roteiro-de-teste) ;;
      2) for s in $FAMILIA; do
           if existe $s; then read "r?Instalar /$s? (s/n) "; [[ "$r" == [sS]* ]] && ESCOLHA+=($s)
           else echo "  /$s: ainda não criada"; fi
         done ;;
      3) for s in $FAMILIA; do existe $s && ESCOLHA+=($s); done; ESCOLHA+=(roteiro-de-teste) ;;
      *) echo "Opção inválida: nada foi instalado."; exit 1 ;;
    esac ;;
esac

for s in $ESCOLHA; do
  existe $s || { echo "Skill desconhecida ou ainda não criada: $s (nada foi instalado)"; exit 1; }
done
# A /roteiro-de-teste entra primeiro quando há alguma de conversão escolhida.
for s in $ESCOLHA; do
  (( ${CONVERSAO[(Ie)$s]} )) && { ESCOLHA=(roteiro-de-teste ${ESCOLHA:#roteiro-de-teste}); break; }
done
[[ ${#ESCOLHA} -gt 0 ]] || { echo "Nada escolhido: nada foi instalado."; exit 0; }

mkdir -p "$DEST"
instala() {
  local nome=$1 origem="$AQUI/skills/$1" alvo="$DEST/$1"
  if [[ -d "$alvo" ]]; then
    if diff -rq "$origem" "$alvo" >/dev/null 2>&1; then echo "= /$nome já está atualizada"; return; fi
    mkdir -p "$BK"; cp -Rp "$alvo" "$BK/$nome"
    echo "  cópia de segurança da versão antiga: $BK/$nome"
    rm -rf "$alvo"
  fi
  cp -Rp "$origem" "$alvo"
  echo "+ /$nome instalada"
}

for s in $ESCOLHA; do instala $s; done

# O botão do HTML editável: a ferramenta que salva, o app "Abrir HTML Salvável" e o atalho dele no Dock e na Mesa.
HS="$HOME/Ferramentas/html-salvavel"
APP="$HOME/Applications/Abrir HTML Salvável.app"
DOCK=nao MESA=nao
if [[ -d "$DEST/roteiro-de-teste" ]]; then
  if [[ -z "$ATALHOS" ]]; then
    if [[ -t 0 ]]; then
      echo
      echo "A /roteiro-de-teste abre os HTMLs editáveis por um botão: o app \"Abrir HTML Salvável\"."
      read "r?Colocar esse botão no Dock e na Mesa (Desktop)? (s/n) "
      [[ "$r" == [sS]* ]] && ATALHOS=sim || ATALHOS=nao
    else
      ATALHOS=nao
    fi
  fi
  if [[ "$ATALHOS" == (sim|yes) ]]; then
    mkdir -p "$HS"
    cp -Rp "$DEST/roteiro-de-teste/pacote/." "$HS/"
    chmod +x "$HS/abrir-html-salvavel.command" "$HS/servidor.py" "$HS/abrir-pasta.sh" 2>/dev/null || true
    zsh "$HS/app/instalar-app.sh" >/dev/null 2>&1 && echo "+ app \"Abrir HTML Salvável\" em ~/Applications"
    if [[ -z "$SEM_DOCK" ]] && command -v defaults >/dev/null; then
      if ! defaults read com.apple.dock persistent-apps 2>/dev/null | grep -q "Abrir%20HTML%20Salv"; then
        URL="file://$(python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1]))' "$APP")/"
        defaults write com.apple.dock persistent-apps -array-add "<dict><key>tile-data</key><dict><key>file-data</key><dict><key>_CFURLString</key><string>$URL</string><key>_CFURLStringType</key><integer>15</integer></dict></dict></dict>"
        killall Dock 2>/dev/null || true
        echo "+ botão no Dock"
      else
        echo "= o botão já está no Dock"
      fi
    fi
    mkdir -p "$HOME/Desktop"
    ln -sfn "$APP" "$HOME/Desktop/Abrir HTML Salvável.app"
    ln -sfn "$AQUI/GUIA.html" "$HOME/Desktop/Guia das skills.html"
    echo "+ na Mesa: \"Abrir HTML Salvável\" e \"Guia das skills\""
  fi
fi
# O que existe de fato (de uma instalação de agora ou de antes), para o guia mostrar.
[[ -e "$HOME/Desktop/Abrir HTML Salvável.app" ]] && MESA=sim
[[ -z "$SEM_DOCK" ]] && defaults read com.apple.dock persistent-apps 2>/dev/null | grep -q "Abrir%20HTML%20Salv" && DOCK=sim

# O guia mostra o que está instalado: o instalador escreve instaladas.js ao lado do GUIA.html.
TODAS=(roteiro-de-teste bdd-antes $CONVERSAO test-checklist bdd-first conversion-prepare conversion-fidelity conversion-parity conversion-android conversion-ios)
typeset -a TEM
for s in $TODAS; do [[ -d "$DEST/$s" ]] && TEM+=("\"$s\""); done
cat > "$AQUI/instaladas.js" <<EOF
// Escrito pelo instalador em $(date "+%Y-%m-%d %H:%M"). Não editar: rode o instalador de novo.
window.INSTALADAS = {"skills": [${(j:, :)TEM}], "abrir": "${ESCOLHA[-1]}", "quando": "$(date +%s)", "dock": "$DOCK", "mesa": "$MESA"};
EOF

for a in independent-qa independent-auditor; do
  if [[ -d "$DEST/roteiro-de-teste" && ! -f "$HOME/.claude/agents/$a.md" ]]; then
    echo "! Falta o agente $a: cp -p \"$AQUI/skills/roteiro-de-teste/pacote/agentes/$a.md\" ~/.claude/agents/"
  fi
done
echo "Pronto. Reinicie o Claude Code para as skills novas aparecerem."
echo "Abrindo o guia das skills no navegador: $AQUI/GUIA.html"
[[ -n "$SEM_ABRIR" ]] || open "$AQUI/GUIA.html" 2>/dev/null || true
