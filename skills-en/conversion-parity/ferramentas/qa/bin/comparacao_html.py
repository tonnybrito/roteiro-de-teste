#!/usr/bin/env python3
"""Interactive comparison page (side by side, curtain, blink, diff + regions) from diff_par.py outputs.
usage: comparacao_html.py <out.html> <embed:0|1> <pairs.json>
pairs.json: [{"id":"p1","prefix":"/path/p1","title":"...","la":"...","lb":"...","src":"..."}]"""
import json, sys, base64, subprocess, os
out, embed, pairs = sys.argv[1], sys.argv[2] == '1', json.load(open(sys.argv[3]))
def src(path):
    if not embed: return os.path.relpath(path, os.path.dirname(os.path.abspath(out)))
    jpg = subprocess.run(['magick', path, '-quality', '78', 'jpg:-'], capture_output=True).stdout
    return 'data:image/jpeg;base64,' + base64.b64encode(jpg).decode()
def badge(v):
    return f'<span class="badge {"ok" if v>=95 else ("warn" if v>=85 else "bad")}">{v:.1f}%</span>'
cards = []
for p in pairs:
    j = json.load(open(p['prefix'] + '.json')); pre = p['prefix']
    A, B, D = src(pre + '-A.png'), src(pre + '-Bal.png'), src(pre + '-diff.png')
    worst = {(c['r'], c['c']) for c in sorted(j['cells'], key=lambda x: x['score'])[:3]}
    grid = ''.join(f'<div class="cell {"worst" if (c["r"],c["c"]) in worst else ""} {"lo" if c["score"]<85 else ("mid" if c["score"]<95 else "hi")}"><span>{c["score"]:.0f}%</span></div>' for c in j['cells'])
    la, lb = p['la'], p['lb']
    cards.append(f'''<section class="card" id="{p['id']}"><header><div><h2>{p['title']}</h2><p class="src">{p.get('src','')}</p></div>
<div class="scores"><div><small>Nota bruta</small>{badge(j["raw"])}</div><div><small>Depois de alinhar</small>{badge(j["aligned"])}</div><div><small>Deslocamento</small><span class="badge neutral">{j["dy"]:+d}px</span></div></div></header>
<nav class="tabs"><button class="on" data-v="side">Lado a lado</button><button data-v="curtain">Cortina</button><button data-v="blink">Piscar</button><button data-v="diff">Diff + regiões</button></nav>
<div class="view side on"><figure><img src="{A}"><figcaption>{la}</figcaption></figure><figure><img src="{B}"><figcaption>{lb}</figcaption></figure></div>
<div class="view curtain"><div class="stage"><img src="{A}"><div class="top" style="--x:50%"><img src="{B}"></div><div class="bar" style="--x:50%"></div></div><input type="range" min="0" max="100" value="50" class="slider"><p class="hint">Arraste: à esquerda {la}, à direita {lb}</p></div>
<div class="view blink"><div class="stage"><img src="{A}"><img class="b" src="{B}"></div><label class="row"><input type="checkbox" class="auto" checked> piscar sozinho</label><input type="range" min="0" max="100" value="50" class="op"><p class="hint">Ou use a barra para misturar os dois (transparência)</p></div>
<div class="view diff"><div class="stage"><img src="{D}"><div class="grid" style="grid-template-columns:repeat({j["cols"]},1fr)">{grid}</div></div><label class="row"><input type="checkbox" class="showgrid" checked> mostrar a nota de cada região</label>
<p class="legend"><i class="m"></i> mais claro no {la} &nbsp; <i class="c"></i> mais claro no {lb} &nbsp; <i class="w"></i> as 3 piores regiões</p></div></section>''')
CSS = open(os.path.join(os.path.dirname(__file__), 'comparacao.css')).read()
JS = open(os.path.join(os.path.dirname(__file__), 'comparacao.js')).read()
html = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Comparação de telas</title><style>{CSS}</style></head><body><div class="wrap">
<h1>Comparação de telas</h1><p class="lead">Notas por cor, alinhamento automático, cortina, piscar e diff com nota por região.</p>{''.join(cards)}
<div class="note"><b>Como ler as notas.</b> Verde ≥ 95% · amarelo 85–95% · vermelho &lt; 85%. A <b>nota bruta</b> compara pixel a pixel; a <b>nota depois de alinhar</b> desconta o deslocamento de altura. Relógio, bateria e a barra de 3 botões são cortados antes da conta. Telas com vídeo ou animação podem ter nota baixa mesmo corretas.</div></div><script>{JS}</script></body></html>'''
open(out, 'w').write(html); print(out, os.path.getsize(out))
