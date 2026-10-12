#!/bin/zsh
# Monta o app "Abrir HTML Salvável" (com o ícone) em ~/Applications, a partir desta pasta.
# Uso: zsh instalar-app.sh   — depois, arraste o app de ~/Applications para o Dock.
set -e
AQUI="$(cd "$(dirname "$0")" && pwd)"
APP="$HOME/Applications/Abrir HTML Salvável.app"
TMP="$(mktemp -d)/app.app"
mkdir -p "$HOME/Applications"
osacompile -o "$TMP" "$AQUI/AbrirHTMLSalvavel.applescript"
cp "$AQUI/AppIcon.icns" "$TMP/Contents/Resources/applet.icns"
rm -f "$TMP/Contents/Resources/Assets.car"
/usr/libexec/PlistBuddy -c "Delete :CFBundleIconName" "$TMP/Contents/Info.plist" 2>/dev/null || true
if [ -d "$APP" ]; then
  # Mantém o mesmo app (e o lugar dele no Dock): troca só o roteiro e o ícone.
  rm -rf "$APP/Contents/Resources/Scripts"
  cp -R "$TMP/Contents/Resources/Scripts" "$APP/Contents/Resources/"
  cp "$AQUI/AppIcon.icns" "$APP/Contents/Resources/applet.icns"
else
  mv "$TMP" "$APP"
fi
codesign --force --deep -s - "$APP" >/dev/null 2>&1 || true
touch "$APP"
echo "ok: $APP"
