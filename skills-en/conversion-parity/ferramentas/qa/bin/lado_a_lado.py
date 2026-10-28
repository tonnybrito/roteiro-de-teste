#!/usr/bin/env python3
"""Builds one side-by-side JPG per screen: rows = 4 cycles, columns = Figma | iOS | Android.
usage: lado_a_lado.py <shots dir> <ios dev> <android dev> <figma dir> <out dir>"""
import os, re, subprocess, sys
shots, ios, andr, figma, out = sys.argv[1:6]
ONLY = sys.argv[6].split(',') if len(sys.argv) > 6 else None
FONT = '/System/Library/Fonts/Supplemental/Arial.ttf'
CYCLES = [('halloween', 'Halloween'), ('xmas', 'Natal'), ('easter', 'Pascoa'), ('july4', '4 de Julho')]
W, H = 240, 520
os.makedirs(out, exist_ok=True)
def keys(dev):
    ks = set()
    for f in os.listdir(os.path.join(shots, dev)):
        m = re.match(r'(halloween|xmas|easter|july4)-(.+)\.png$', f)
        if m: ks.add(m.group(2))
    return ks
def cell(path, text):
    if path and os.path.exists(path):
        return ['(', path, '-resize', f'{W}x{H}', '-background', '#1b1b1b', '-gravity', 'center', '-extent', f'{W}x{H}', ')']
    return ['(', '-size', f'{W}x{H}', 'xc:#2a2a2a', '-font', FONT, '-pointsize', '20', '-fill', '#bbbbbb', '-gravity', 'center', '-annotate', '+0+0', text, ')']
def label(text, w, h=36, size=20):
    return ['(', '-size', f'{w}x{h}', 'xc:#111111', '-font', FONT, '-pointsize', str(size), '-fill', 'white', '-gravity', 'center', '-annotate', '+0+0', text, ')']
def figma_for(cyc, key):
    base = re.sub(r'^(14-cap)\d(-[a-e])-.*$', r'\1\2', key)
    base = re.sub(r'^(14-cap)\d(-[a-e]).*$', r'\1\2', base)
    for k in (key, base):
        p = os.path.join(figma, f'{cyc}-{k}.png')
        if os.path.exists(p): return p
    return None
import tempfile
TMP = tempfile.mkdtemp()
CW, CH = 300, 640
def norm(path, kind, tag):
    """crop what is not the app (status bar, home indicator / Android nav bar) and resize to a common size"""
    top, bot = {'ios': (0.07, 0.03), 'android': (0.05, 0.05), 'figma': (0.07, 0.03)}[kind]
    out = os.path.join(TMP, tag + '.png')
    subprocess.run(['magick', path, '-gravity', 'south', '-crop', f'100%x{int((1-top)*100)}%+0+0', '+repage',
                    '-gravity', 'north', '-crop', f'100%x{int((1-top-bot)/(1-top)*100)}%+0+0', '+repage',
                    '-resize', f'{CW}x{CH}!', out], check=True)
    return out
def similarity(a, b):
    r = subprocess.run(['magick', 'compare', '-metric', 'AE', '-fuzz', '15%', a, b, 'null:'], capture_output=True, text=True)
    try: ae = float(r.stderr.split()[0])
    except Exception: return None
    return max(0.0, 100.0 * (1 - ae / (CW * CH)))
def diff_img(a, b, tag):
    out = os.path.join(TMP, tag + '-diff.png')
    subprocess.run(['magick', 'compare', '-fuzz', '15%', '-highlight-color', '#ff2a2a', '-lowlight-color', '#ffffff30', a, b, out], capture_output=True)
    return out
allkeys = sorted(keys(ios) | keys(andr))
SUMMARY = []
for key in allkeys:
    if re.match(r'14-cap[2-8]-', key):
        continue
    cmd = ['magick']
    cmd += label(key + '   (vermelho no Diff = pixels diferentes entre iOS e Android)', 120 + 4 * W, 44, 22)
    head = ['('] + label('', 120) + label('Figma', W) + label('iOS (' + ios + ')', W) + label('Android (' + andr + ')', W) + label('Diff iOS x Android', W) + ['+append', ')']
    cmd += head
    for cyc, name in [x for x in CYCLES if not ONLY or x[0] in ONLY]:
        row = ['('] + ['(', '-size', f'120x{H}', 'xc:#111111', '-font', FONT, '-pointsize', '20', '-fill', 'white', '-gravity', 'center', '-annotate', '+0+0', name, ')']
        fp, ip, ap = figma_for(cyc, key), os.path.join(shots, ios, f'{cyc}-{key}.png'), os.path.join(shots, andr, f'{cyc}-{key}.png')
        row += cell(fp, 'sem Figma')
        row += cell(ip, 'sem print')
        row += cell(ap, 'sem print')
        txt = []
        if os.path.exists(ip) and os.path.exists(ap):
            ni, na = norm(ip, 'ios', f'{key}-{cyc}-i'), norm(ap, 'android', f'{key}-{cyc}-a')
            sim = similarity(ni, na)
            row += ['(', diff_img(ni, na, f'{key}-{cyc}'), '-resize', f'{W}x{H-90}', '-background', '#1b1b1b', '-gravity', 'center', '-extent', f'{W}x{H-90}']
            txt.append(f'iOS x Android: {sim:.0f}%' if sim is not None else 'iOS x Android: ?')
            if fp:
                s2 = similarity(norm(fp, 'figma', f'{key}-{cyc}-f'), na)
                txt.append(f'Figma x Android: {s2:.0f}% (ref.)' if s2 is not None else '')
            else:
                txt.append('Figma: sem tela')
            row += ['(', '-size', f'{W}x90', 'xc:#111111', '-font', FONT, '-pointsize', '19', '-fill', '#ffe680', '-gravity', 'center', '-annotate', '+0+0', '\n'.join(txt), ')', '-append', ')']
            SUMMARY.append((key, cyc, sim))
        else:
            row += cell(None, 'sem par para comparar')
        row += ['+append', ')']
        cmd += row
    cmd += ['-append', '-quality', '72', os.path.join(out, f'lado-a-lado-{key}.jpg')]
    subprocess.run(cmd, check=True)
import json
json.dump([{'tela': k, 'ciclo': c, 'proximidade_ios_android': None if v is None else round(v, 1)} for k, c, v in SUMMARY], open(os.path.join(out, 'proximidade.json'), 'w'), ensure_ascii=False, indent=1)
print('ok', len(os.listdir(out)))
