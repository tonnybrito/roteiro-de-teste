#!/usr/bin/env python3
"""Static card image for one pair: A | B(aligned) | Diff with region grid; header with coloured scores.
usage: card_img.py <diff_par outprefix> <labelA> <labelB> <title> <out.jpg>"""
import json, subprocess, sys
p, la, lb, title, out = sys.argv[1:6]
F = '/System/Library/Fonts/Supplemental/Arial.ttf'; FB = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
j = json.load(open(p + '.json')); W, H, C, R = j['w'], j['h'], j['cols'], j['rows']
col = lambda v: '#2fbf71' if v >= 95 else ('#e6b422' if v >= 85 else '#e5484d')
cw, ch = W // C, H // R
worst = sorted(j['cells'], key=lambda x: x['score'])[:3]
draw = []
for c in j['cells']:
    x, y = c['c'] * cw, c['r'] * ch
    draw += ['-fill', 'none', '-stroke', '#ffffff30', '-strokewidth', '1', '-draw', f'rectangle {x},{y} {x+cw-1},{y+ch-1}']
    draw += ['-stroke', 'none', '-fill', '#000000a0', '-draw', f'rectangle {x+cw-44},{y+2} {x+cw-3},{y+20}',
             '-fill', col(c['score']), '-font', FB, '-pointsize', '14', '-annotate', f'+{x+cw-42}+{y+16}', f"{c['score']:.0f}%"]
for c in worst:
    x, y = c['c'] * cw, c['r'] * ch
    draw += ['-fill', 'none', '-stroke', '#ffd400', '-strokewidth', '4', '-draw', f'rectangle {x+2},{y+2} {x+cw-3},{y+ch-3}']
def lab(t, w, color='#e9ecf2', size=18, h=34, bg='#181b22', font=F):
    return ['(', '-size', f'{w}x{h}', f'xc:{bg}', '-font', font, '-pointsize', str(size), '-fill', color, '-gravity', 'center', '-annotate', '+0+0', t, ')']
G = 12; TW = 3 * W + 4 * G
cmd = ['magick', '-background', '#0f1115']
cmd += lab(title, TW, size=24, h=46, bg='#0f1115', font=FB)
cmd += ['('] + lab(f"Nota bruta {j['raw']:.1f}%", TW // 3, col(j['raw']), 20, 40, '#0f1115', FB) + lab(f"Depois de alinhar {j['aligned']:.1f}%", TW // 3, col(j['aligned']), 20, 40, '#0f1115', FB) + lab(f"Deslocamento {j['dy']:+d}px", TW - 2 * (TW // 3), '#9aa3b2', 18, 40, '#0f1115') + ['+append', ')']
row = ['(', '-size', f'{G}x{H+34}', 'xc:#0f1115']
for img, l in ((p + '-A.png', la), (p + '-Bal.png', lb), (p + '-diff.png', 'Diff (caixa amarela = pior região)')):
    extra = draw if img.endswith('-diff.png') else []
    row += ['(', '(', img] + extra + [')'] + lab(l, W, size=14 if 'Diff' in l else 17) + ['-append', ')', '-size', f'{G}x{H+34}', 'xc:#0f1115']
row += ['+append', ')']
cmd += row + ['-append', '-quality', '80', out]
subprocess.run(cmd, check=True)
print(out)
