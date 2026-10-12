#!/bin/zsh
# Atalho do HTML salvável: dois cliques liga o servidor nesta pasta e abre o HTML no navegador.
# Para usar em outro projeto, copie este arquivo para a pasta do HTML.
# ARQUIVO vazio abre uma lista com os HTMLs salváveis da pasta; preencha para abrir um direto.
ARQUIVO=""

cd "$(dirname "$0")" || exit 1
for PY in /opt/homebrew/bin/python3 /usr/local/bin/python3 /usr/bin/python3; do
  [ -x "$PY" ] && break
done
exec "$PY" "$HOME/Ferramentas/html-salvavel/servidor.py" "$(pwd)" $ARQUIVO
