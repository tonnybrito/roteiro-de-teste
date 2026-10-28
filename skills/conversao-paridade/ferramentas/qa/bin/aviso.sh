#!/bin/zsh
# usage: aviso.sh "mensagem"  — raises the Mac volume only while the alert plays
for i in 1 2 3; do
  osascript -e 'set volume output volume 100'
  afplay /System/Library/Sounds/Glass.aiff; afplay /System/Library/Sounds/Glass.aiff; say -v Luciana "$1"
  osascript -e 'set volume output volume 0'
  sleep 8
done
