#!/bin/zsh
# Instala as skills da família (roteiro-de-teste, bdd-antes e as de conversão iPhone ⇄ Android, nos dois sentidos) em ~/.claude/skills.
# A /roteiro-de-teste é a base das de conversão: entra SEMPRE primeiro quando uma delas é escolhida.
# A /bdd-antes funciona sozinha: escolhida sozinha, entra sem a /roteiro-de-teste.
#   zsh instalar.sh                                  menu: 1 só a roteiro-de-teste · 2 escolher · 3 todas
#   zsh instalar.sh --todas                          sem menu, instala todas as que o pacote tem
#   zsh instalar.sh --skills conversao-preparar,...  sem menu, só as citadas (+ roteiro-de-teste se houver uma de conversão)
# Antes de trocar uma skill que já existe e é diferente, guarda uma cópia em ~/Ferramentas/html-salvavel/backups/.
set -e
AQUI="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.claude/skills"
BK="$HOME/Ferramentas/html-salvavel/backups/skills-$(date +%Y%m%d-%H%M%S)"
CONVERSAO=(conversao-preparar conversao-fidelidade conversao-paridade conversao-android conversao-ios)
FAMILIA=(bdd-antes $CONVERSAO)
typeset -a ESCOLHA
existe() { [[ -d "$AQUI/skills/$1" ]]; }

case "$1" in
  --todas) for s in $FAMILIA; do existe $s && ESCOLHA+=($s); done; ESCOLHA+=(roteiro-de-teste) ;;
  --skills) ESCOLHA=(${(s:,:)2}) ;;
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
  *) echo "uso: zsh instalar.sh [--todas | --skills a,b]"; exit 1 ;;
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

# O que a /roteiro-de-teste precisa fora das skills: só avisa; a própria skill pergunta antes de instalar
[[ -d "$HOME/Ferramentas/html-salvavel" ]] || echo "! Falta a ferramenta que salva no HTML: peça ao Claude \"/roteiro-de-teste\" (passo 1) ou copie skills/roteiro-de-teste/pacote para ~/Ferramentas/html-salvavel"
[[ -d "$HOME/Applications/Abrir HTML Salvável.app" ]] || echo "! Falta o app da Dock: zsh ~/Ferramentas/html-salvavel/app/instalar-app.sh"
for a in independent-qa independent-auditor; do
  [[ -f "$HOME/.claude/agents/$a.md" ]] || echo "! Falta o agente $a: cp -p \"$AQUI/skills/roteiro-de-teste/pacote/agentes/$a.md\" ~/.claude/agents/"
done
echo "Pronto. Reinicie o Claude Code para as skills novas aparecerem."
