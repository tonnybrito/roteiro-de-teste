#!/bin/zsh
# Usado pelo app "Abrir HTML Salvável": liga o servidor na pasta recebida e abre a lista dos HTMLs no navegador.
for PY in /opt/homebrew/bin/python3 /usr/local/bin/python3 /usr/bin/python3; do
  [ -x "$PY" ] && break
done
exec "$PY" "$HOME/Ferramentas/html-salvavel/servidor.py" "$1"
