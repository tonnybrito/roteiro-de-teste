#!/usr/bin/env python3
"""Compare two screenshots of the same screen. Writes normalized A/B, a two-colour diff overlay and a JSON with
raw score, aligned score (best vertical shift), and a per-cell grid score.
usage: diff_par.py <A> <kindA> <B> <kindB> <outprefix>   (kind: ios|android|figma)"""
import json, subprocess, sys, os
A, ka, B, kb, out = sys.argv[1:6]
W, H, FUZZ, COLS, ROWS = 360, 780, '12%', 4, 8
CROP = {'ios': (0.07, 0.03), 'android': (0.05, 0.05), 'figma': (0.07, 0.03)}
def run(*a, **k): return subprocess.run(list(a), capture_output=True, text=True, **k)
def norm(src, kind, dst):
    t, b = CROP[kind]
    run('magick', src, '-gravity', 'south', '-crop', f'100%x{(1-t)*100:.2f}%+0+0', '+repage',
        '-gravity', 'north', '-crop', f'100%x{(1-t-b)/(1-t)*100:.2f}%+0+0', '+repage', '-resize', f'{W}x{H}!', dst)
def ae(a, b, geom=None):
    args = ['magick', 'compare', '-metric', 'AE', '-fuzz', FUZZ]
    r = run(*args, a, b, 'null:')
    return float(r.stderr.split()[0])
na, nb = out + '-A.png', out + '-B.png'
norm(A, ka, na); norm(B, kb, nb)
raw = 100 * (1 - ae(na, nb) / (W * H))
# alignment: shift B vertically, compare the overlapping band
best = (raw, 0)
for dy in range(-60, 61, 4):
    if dy == 0: continue
    h = H - abs(dy)
    ca, cb = out + '-ca.png', out + '-cb.png'
    run('magick', na, '-crop', f'{W}x{h}+0+{max(0, dy)}', '+repage', ca)
    run('magick', nb, '-crop', f'{W}x{h}+0+{max(0, -dy)}', '+repage', cb)
    s = 100 * (1 - ae(ca, cb) / (W * h))
    if s > best[0]: best = (s, dy)
aligned, dy = best
# aligned B for the visuals
nbal = out + '-Bal.png'
if dy:
    run('magick', nb, '-background', 'black', '-gravity', 'north', '-splice' if dy > 0 else '-chop', f'0x{abs(dy)}', '-crop', f'{W}x{H}+0+0', '+repage', nbal)
else:
    run('cp', nb, nbal)
# two-colour diff: where they differ, magenta if A is brighter, cyan if B is brighter; base = A dimmed
mask = out + '-mask.png'
run('magick', 'compare', '-fuzz', FUZZ, '-highlight-color', 'white', '-lowlight-color', 'black', '-compose', 'src', na, nbal, mask)
ga, gb = out + '-ga.png', out + '-gb.png'
run('magick', na, '-colorspace', 'gray', ga); run('magick', nbal, '-colorspace', 'gray', gb)
abri = out + '-abri.png'
run('magick', ga, gb, '-compose', 'minus_src', '-composite', '-threshold', '1%', abri)  # A brighter
over = out + '-diff.png'
run('magick', na, '-modulate', '45,25', '(', '-size', f'{W}x{H}', 'xc:#00e5ff', mask, '-alpha', 'off', '-compose', 'copy_opacity', '-composite', ')',
    '-compose', 'over', '-composite',
    '(', '-size', f'{W}x{H}', 'xc:#ff2bd6', '(', mask, abri, '-compose', 'multiply', '-composite', ')', '-alpha', 'off', '-compose', 'copy_opacity', '-composite', ')',
    '-compose', 'over', '-composite', over)
# per-cell scores on the mask
cw, ch = W // COLS, H // ROWS
cells = []
for r in range(ROWS):
    for c in range(COLS):
        m = run('magick', mask, '-crop', f'{cw}x{ch}+{c*cw}+{r*ch}', '+repage', '-format', '%[fx:mean]', 'info:').stdout
        cells.append({'r': r, 'c': c, 'score': round(100 * (1 - float(m or 0)), 1)})
for f in (out + '-ca.png', out + '-cb.png', ga, gb, abri): 
    if os.path.exists(f): os.remove(f)
json.dump({'raw': round(raw, 1), 'aligned': round(aligned, 1), 'dy': dy, 'w': W, 'h': H, 'cols': COLS, 'rows': ROWS, 'cells': cells}, open(out + '.json', 'w'))
print(out, round(raw, 1), round(aligned, 1), dy)
