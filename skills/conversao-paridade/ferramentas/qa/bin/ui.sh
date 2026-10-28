#!/bin/zsh
# dump visible ids/texts/descs on Android device $1
a(){ ~/Library/Android/sdk/platform-tools/adb -s $1 "${@:2}"; }
a $1 shell uiautomator dump /sdcard/u.xml >/dev/null 2>&1
a $1 shell cat /sdcard/u.xml | python3 -c "
import sys,re
x=sys.stdin.read()
for m in re.finditer(r'<node [^>]*>',x):
  n=m.group(0)
  g=lambda k: (re.search(k+'=\"([^\"]*)\"',n) or [None,''])[1]
  if 'systemui' in g('resource-id') or g('package')!='com.exemplo.trilhadosbichos': continue
  t,i,d=g('text'),g('resource-id'),g('content-desc')
  if t or i or d: print(f'{i:35} | {t[:40]:40} | {d[:30]:30} | {g(\"bounds\")}')
"
