#!/usr/bin/env python3
"""Findings page: one tab per cycle, one card per finding, with the side-by-side image (embedded).
usage: achados_html.py <findings.json>... --out <file.html>"""
import json, sys, os, base64, subprocess, html
S = os.environ.get('QA_WORK', os.path.abspath('qa-work'))
args = sys.argv[1:]; out = args[args.index('--out') + 1]; files = [a for a in args[:args.index('--out')]]
F = []
for f in files: F += json.load(open(f))
IMG = {
 'F-HW-01':'18-ad1-tee-time-trainer','F-HW-02':'08-save-confirm','F-HW-03':S+'/qa/hw03-par.jpg','F-HW-04':'10-review','F-HW-05':'17-credits',
 'F-HW-06':'04-players','F-HW-07':'14-cap1-a-scanner','F-HW-08':'06b-need-assets-popup','F-HW-09':'14-cap1-c-card','F-HW-10':'02-home',
 'F-HW-11':'05-team','F-HW-12':'08-save-confirm','F-XM-01':'06b-need-assets-popup','F-XM-02':'06-assets-intro','F-XM-03':'05-team',
 'F-XM-04':'13-hub-ready','F-XM-05':'14-cap9-e-hub','F-XM-06':'14-cap1-a-scanner','F-XM-07':'03-safety','F-XM-08':'08-save-confirm',
 'F-XM-09':'07b-game-assets-portrait','F-XM-10':'17-credits','F-XM-11':'18-ad1-tee-time-trainer','F-XM-12':'00-carousel',
 'F-XM-13':'14-cap9-c-card','F-XM-14':'14-cap1-a-scanner'}
IMG.update(json.load(open(S + '/qa/img-extra.json')) if os.path.exists(S + '/qa/img-extra.json') else {})
MAPA = json.load(open(S + '/ios26/mapa.json')) if os.path.exists(S + '/ios26/mapa.json') and os.environ.get('V26') else []
V26 = {}
for m in MAPA:
    for a in m['achados']: V26.setdefault(a, []).append(m)
def v26_html(f):
    ms = V26.get(f['id'])
    if not ms: return ''
    items = ''.join(f'<li><b>{html.escape(m["mudanca"])}</b><br><span>{html.escape(m["efeito"])}</span></li>' for m in ms)
    return f'<div class="v26"><h4>🆕 O que mudou no iOS 1.6.26</h4><ul>{items}</ul><p class="v26hint">Para conversarmos amanhã · nada foi alterado no código</p></div>'
def img(f):
    k = IMG.get(f['id']) or f.get('img')
    if not k: return ''
    p = k if k.startswith('/') else f"{S}/{os.environ.get('QA_DIR','qa')}/{f['ciclo']}/lado-a-lado-{k}.jpg"
    if not os.path.exists(p): return ''
    b = subprocess.run(['magick', p, '-resize', '1400x>', '-quality', '72', 'jpg:-'], capture_output=True).stdout
    return 'data:image/jpeg;base64,' + base64.b64encode(b).decode()
def depois_html(f):
    p = f.get('depois')
    if not p or not os.path.exists(p): return ''
    b = subprocess.run(['magick', p, '-resize', '1400x>', '-quality', '75', 'jpg:-'], capture_output=True).stdout
    src = 'data:image/jpeg;base64,' + base64.b64encode(b).decode()
    return f'<h4 class="after">✅ Depois da correção</h4><a class="shot" href="{src}" target="_blank"><img src="{src}" alt="depois" loading="lazy"></a><p class="hint">{html.escape(f.get("depois_legenda",""))}</p>'
TABS = ([('ios26', '🆕 iOS 1.6.26')] if MAPA else []) + [('halloween', '🎃 Halloween'), ('xmas', '🎄 Natal'), ('easter', '🐣 Páscoa'), ('july4', '🎆 4 de Julho')]
SEV = lambda s: 'major' if s.startswith('major') or s.startswith('blocker') else ('minor' if s.startswith('minor') else 'cos')
e = html.escape
secs, nav = [], []
for tid, tname in TABS:
    if tid == 'ios26':
        cards = []
        for i, m in enumerate(MAPA, 1):
            k = (m['telas'] or [''])[0]
            cyc = 'july4' if 'july4' in m['ciclos'] else ('halloween' if m['ciclos'] in (['halloween'], ['todos']) or 'todos' in m['ciclos'] else m['ciclos'][0])
            fake = {'id': f'V26-{i:02d}', 'ciclo': cyc, 'img': k}
            src = img(fake)
            link = ', '.join(m['achados']) or 'nenhum achado — diferença nova ou iOS agora igual ao Android'
            cards.append(f'''<article class="card minor"><header><span class="hid"><span class="id">V26-{i:02d}</span><span class="new26">🆕 iOS 1.6.26</span></span><span class="sev">{html.escape(', '.join(m['ciclos']))}</span></header>
<h3>{html.escape(m['mudanca'])}</h3><p class="meta">Telas <code>{html.escape(', '.join(m['telas']))}</code> · achados ligados: {html.escape(link)}</p>
{f'<a class="shot" href="{src}" target="_blank"><img src="{src}" loading="lazy"></a><p class="hint">Figma · iOS 1.6.26 · Android · Diff</p>' if src else ''}
<h4>Efeito</h4><p>{html.escape(m['efeito'])}</p><h4>Android hoje</h4><p>{html.escape(m.get('android_hoje') or '—')}</p><p class="cause">iOS: {html.escape(str(m.get('ios_ref','')))} · commits {html.escape(', '.join(m['commits']))}</p>
<p class="status">⏳ Para conversarmos amanhã</p></article>''')
        nav.append(f'<button data-t="{tid}">{tname} <span>{len(MAPA)}</span></button>')
        secs.append(f'<section id="{tid}" class="tab">{"".join(cards)}</section>'); continue
    items = [f for f in F if f['ciclo'] == tid]
    nav.append(f'<button data-t="{tid}">{tname} <span>{len(items)}</span></button>')
    if not items:
        secs.append(f'<section id="{tid}" class="tab"><p class="empty">⏳ O QA deste ciclo ainda está rodando.</p></section>'); continue
    cards = []
    for f in items:
        src = img(f)
        ev = ''.join(f'<li>{e(x)}</li>' for x in f['evidencia'])
        cards.append(f'''<article class="card {SEV(f['gravidade'])}"><header><span class="hid"><span class="id">{e(f['id'])}</span>{'<span class="all">🔁 vale para os 4 ciclos</span>' if f.get('todos') else ''}{'<span class="new26">🆕 iOS 1.6.26 mudou</span>' if f['id'] in V26 else ''}</span><span class="sev">{e(f['gravidade'])}</span></header>
<h3>{e(f['titulo'])}</h3><p class="meta">Ciclo: <b>{e(f.get('ciclo_nome',''))}</b> · Tela <code>{e(f['tela'])}</code> · comparado com {e(f['comparado'])}</p>
{f'<a class="shot" href="{src}" target="_blank"><img src="{src}" alt="lado a lado" loading="lazy"></a><p class="hint">{os.environ.get('IMG_LABEL','Figma · iOS · Android · Diff')} — toque para ampliar</p>' if src else ''}
{depois_html(f)}{v26_html(f)}<div class="grid2"><div><h4>O que o QA viu (Android)</h4><p>{e(f['visto'])}</p></div><div><h4>Esperado</h4><p>{e(f['esperado'])}</p></div></div>
<h4>Evidências</h4><ul>{ev}</ul>{f'<h4>Causa provável</h4><p class="cause">{e(f["causa"])}</p>' if f.get('causa') else ''}
<p class="status{' done' if f.get('decisao') else ''}">{e(f.get('decisao') or '⏳ Aguardando decisão do dev')}</p></article>''')
    secs.append(f'<section id="{tid}" class="tab">{"".join(cards)}</section>')
total = len(F); nmaj = sum(1 for f in F if SEV(f['gravidade']) == 'major')
page = f'''<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Achados do QA · R3</title><style>
:root{{--bg:#0f1115;--card:#181b22;--ink:#e9ecf2;--mut:#9aa3b2;--line:#2a2f3a;--acc:#7c9cff}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,system-ui,sans-serif}}
.top{{background:linear-gradient(135deg,#3b2a8a,#6a4bd8);padding:22px 16px}}.wrap{{max-width:1000px;margin:auto}}h1{{margin:0;font-size:22px}}.top p{{margin:6px 0 0;opacity:.85}}
.chips{{display:flex;gap:8px;flex-wrap:wrap;margin-top:12px}}.chip{{background:#0005;border-radius:999px;padding:4px 12px;font-size:13px}}
nav{{position:sticky;top:0;background:#0f1115ee;backdrop-filter:blur(6px);border-bottom:1px solid var(--line);z-index:5}}nav .wrap{{display:flex;gap:6px;overflow-x:auto;padding:10px 16px}}
nav button{{font:inherit;white-space:nowrap;background:#232836;color:var(--ink);border:1px solid var(--line);border-radius:10px;padding:7px 12px;cursor:pointer}}nav button.on{{background:var(--acc);color:#0b0d12;border-color:var(--acc)}}nav button span{{opacity:.7;font-size:12px}}
main{{padding:16px}}.tab{{display:none}}.tab.on{{display:block}}.empty{{color:var(--mut);text-align:center;padding:40px}}
.card{{background:var(--card);border:1px solid var(--line);border-left:5px solid #888;border-radius:14px;padding:14px 16px;margin:0 0 16px}}.card.major{{border-left-color:#e5484d}}.card.minor{{border-left-color:#e6b422}}.card.cos{{border-left-color:#6b7280}}
.card header{{display:flex;justify-content:space-between;gap:8px}}.id{{font-weight:800;color:#c7d2ff}}.hid{{display:flex;gap:8px;align-items:center;flex-wrap:wrap}}.new26{{font-size:12px;font-weight:800;padding:3px 10px;border-radius:999px;background:#a855f7;color:#fff}}.v26{{border:1px solid #a855f7;background:#a855f71a;border-radius:12px;padding:10px 14px;margin:10px 0}}.v26 h4{{color:#d8b4fe;margin-top:0}}.v26 li{{margin:6px 0}}.v26 span{{color:#cbd5e1;font-size:14px}}.v26hint{{color:#d8b4fe;font-size:12px;margin:6px 0 0}}.all{{font-size:12px;font-weight:800;padding:3px 10px;border-radius:999px;background:#ffd400;color:#1a1400}}.sev{{font-size:12px;padding:2px 10px;border-radius:999px;background:#232836;color:var(--mut)}}.major .sev{{background:#3f1416;color:#ff8f93}}.minor .sev{{background:#3d3210;color:#f3d06a}}
h3{{margin:6px 0 2px;font-size:17px}}.meta{{color:var(--mut);font-size:13px;margin:0 0 10px}}code{{background:#232836;padding:1px 6px;border-radius:6px}}
.shot img{{width:100%;border-radius:10px;border:1px solid var(--line);display:block}}.hint{{color:var(--mut);font-size:12px;margin:4px 0 10px;text-align:center}}
h4{{margin:10px 0 4px;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--mut)}}.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}.grid2 p{{margin:0}}
ul{{margin:0;padding-left:18px}}.cause{{font-family:ui-monospace,Menlo,monospace;font-size:13px;color:#cbd5e1}}.status{{margin:12px 0 0;font-size:13px;color:#f3d06a}}.status.done{{color:#6fe3a0}}h4.after{{color:#6fe3a0}}
@media (max-width:640px){{.grid2{{grid-template-columns:1fr}}h1{{font-size:19px}}}}
</style></head><body>
<div class="top"><div class="wrap"><h1>Achados do QA · Rodada 3 (celular × celular)</h1><p>{os.environ.get('SUBTITLE','iPhone 17 (iOS 1.6.21) × Pixel 9 Pro XL (Android 16).')} Comparação com o Figma onde existe tela.</p>
<div class="chips"><span class="chip">{total} achados</span><span class="chip">{nmaj} major</span><span class="chip">Testes do Android: {os.environ.get("TESTS","103/103")} ✅</span><span class="chip">"Download" fica "Save" (decidido)</span></div></div></div>
<nav><div class="wrap">{"".join(nav)}</div></nav><main><div class="wrap">{"".join(secs)}</div></main>
<script>
const bs=[...document.querySelectorAll('nav button')];const show=t=>{{bs.forEach(b=>b.classList.toggle('on',b.dataset.t===t));document.querySelectorAll('.tab').forEach(s=>s.classList.toggle('on',s.id===t));try{{localStorage.setItem('achadosTab',t)}}catch(e){{}}}};
bs.forEach(b=>b.onclick=()=>show(b.dataset.t));let t0='halloween';try{{t0=localStorage.getItem('achadosTab')||t0}}catch(e){{}};show(t0);
document.querySelectorAll('.shot').forEach(a=>a.onclick=ev=>{{ev.preventDefault();const w=window.open();if(w){{w.document.write('<body style="margin:0;background:#000"><img src="'+a.href+'" style="width:100%">');}}}});
</script></body></html>'''
open(out, 'w').write(page); print(out, os.path.getsize(out))
