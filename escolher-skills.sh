#!/bin/zsh
# Janela de escolha da família de skills (passo 0 de cada skill da família).
#   zsh escolher-skills.sh
# No macOS abre um popup nativo com as sete skills e a situação de cada uma, e imprime
# as escolhidas separadas por vírgula (ex.: "bdd-antes,conversao-android"), ou CANCELADO.
# Fora do macOS imprime SEM-POPUP e sai com 3: a skill então pergunta pela janela do Claude.
AQUI="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.claude/skills"
FAMILIA=(roteiro-de-teste bdd-antes conversao-preparar conversao-fidelidade conversao-paridade conversao-android conversao-ios)
typeset -A FAZ
FAZ=(
  roteiro-de-teste      "checklists de teste em HTML que salvam (base das de conversão)"
  bdd-antes             "BDD antes do código: features, steps, runner e o HTML ligado ao roteiro"
  conversao-preparar    "começar uma conversão iPhone ⇄ Android, nos dois sentidos"
  conversao-fidelidade  "igualar uma tela ao app de referência, pixel por pixel"
  conversao-paridade    "robô compara o app inteiro nos dois celulares"
  conversao-android     "alvo Android: letra grande, teclado, voltar, Play Store"
  conversao-ios         "alvo iPhone: letra grande, ilha, teclado, gesto de voltar, App Store"
)

situacao() {
  local s=$1
  [[ -d "$AQUI/skills/$s" ]] || { echo "ainda não criada"; return; }
  [[ -d "$DEST/$s" ]] || { echo "falta"; return; }
  diff -rq --exclude backups "$AQUI/skills/$s" "$DEST/$s" >/dev/null 2>&1 && echo "instalada" || echo "desatualizada"
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
  set r to choose from list $lista with title "Família de skills" with prompt "Marque as skills que você quer neste projeto (⌘ + clique para marcar várias). A /roteiro-de-teste é a base: entra primeiro se você escolher uma de conversão." with multiple selections allowed and empty selection allowed OK button name "Continuar" cancel button name "Cancelar"
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
