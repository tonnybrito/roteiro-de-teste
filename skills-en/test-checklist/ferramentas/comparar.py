#!/usr/bin/env python3
"""Compara dois prints da mesma tela e devolve o objeto "comparacao" de um card do roteiro.

  python3 comparar.py <A> <B> <pasta-dos-prints> <nome> [opções]

  <A>, <B>            os dois prints (ex.: iPhone e Android, ou Figma e Android)
  <pasta-dos-prints>  a pasta "pastaPrints" do roteiro (as imagens geradas vão para lá)
  <nome>              caminho dentro dela, sem extensão (ex.: rodada3/comparacao/T-22)

  --la "iOS · iPhone 17"     legenda de A           --lb "Android · Pixel"   legenda de B
  --corte-a ios|android|figma|nenhum   tira a barra de status/navegação de A (padrão: ios)
  --corte-b ios|android|figma|nenhum   idem para B (padrão: android)

Grava <nome>-A.jpg, <nome>-B.jpg (B alinhado na vertical) e <nome>-diff.jpg, e imprime o JSON
para colar em qa[].comparacao do card. Notas: "raw" compara como está; "aligned" depois de achar o
melhor deslocamento vertical (dy, até 60 px); "cells" é a nota de cada região (4 x 8), da esquerda
para a direita e de cima para baixo. Telas com vídeo ou animação tiram nota baixa mesmo certas.
Precisa do ImageMagick (comando magick).
"""
import argparse, json, os, subprocess, sys, tempfile
from pathlib import Path

W, H, FUZZ, COLS, ROWS = 360, 780, '12%', 4, 8
CORTE = {'ios': (0.07, 0.03), 'android': (0.05, 0.05), 'figma': (0.07, 0.03), 'nenhum': (0.0, 0.0)}


def run(*a):
    return subprocess.run(list(a), capture_output=True, text=True)


def normaliza(src, corte, dst):
    t, b = CORTE[corte]
    run('magick', src, '-gravity', 'south', '-crop', f'100%x{(1 - t) * 100:.2f}%+0+0', '+repage',
        '-gravity', 'north', '-crop', f'100%x{(1 - t - b) / (1 - t) * 100:.2f}%+0+0', '+repage',
        '-resize', f'{W}x{H}!', dst)


def ae(a, b):
    r = run('magick', 'compare', '-metric', 'AE', '-fuzz', FUZZ, a, b, 'null:')
    return float(r.stderr.split()[0])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('a'); ap.add_argument('b'); ap.add_argument('pasta'); ap.add_argument('nome')
    ap.add_argument('--la', default='A'); ap.add_argument('--lb', default='B')
    ap.add_argument('--corte-a', default='ios', choices=CORTE); ap.add_argument('--corte-b', default='android', choices=CORTE)
    o = ap.parse_args()
    if run('magick', '-version').returncode != 0:
        sys.exit('precisa do ImageMagick (brew install imagemagick)')
    pasta = Path(o.pasta)
    base = pasta / o.nome
    base.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        na, nb = str(t / 'A.png'), str(t / 'B.png')
        normaliza(o.a, o.corte_a, na); normaliza(o.b, o.corte_b, nb)
        raw = 100 * (1 - ae(na, nb) / (W * H))
        best = (raw, 0)
        for dy in range(-60, 61, 4):
            if dy == 0:
                continue
            h = H - abs(dy)
            ca, cb = str(t / 'ca.png'), str(t / 'cb.png')
            run('magick', na, '-crop', f'{W}x{h}+0+{max(0, dy)}', '+repage', ca)
            run('magick', nb, '-crop', f'{W}x{h}+0+{max(0, -dy)}', '+repage', cb)
            s = 100 * (1 - ae(ca, cb) / (W * h))
            if s > best[0]:
                best = (s, dy)
        aligned, dy = best
        nbal = str(t / 'Bal.png')
        if dy:
            run('magick', nb, '-background', 'black', '-gravity', 'north', '-splice' if dy > 0 else '-chop', f'0x{abs(dy)}', '-crop', f'{W}x{H}+0+0', '+repage', nbal)
        else:
            run('cp', nb, nbal)
        # Diff de duas cores: magenta onde A é mais claro, ciano onde B é mais claro, sobre A escurecido
        mask, ga, gb, abri = str(t / 'mask.png'), str(t / 'ga.png'), str(t / 'gb.png'), str(t / 'abri.png')
        run('magick', 'compare', '-fuzz', FUZZ, '-highlight-color', 'white', '-lowlight-color', 'black', '-compose', 'src', na, nbal, mask)
        run('magick', na, '-colorspace', 'gray', ga); run('magick', nbal, '-colorspace', 'gray', gb)
        run('magick', ga, gb, '-compose', 'minus_src', '-composite', '-threshold', '1%', abri)
        diff = str(t / 'diff.png')
        run('magick', na, '-modulate', '45,25', '(', '-size', f'{W}x{H}', 'xc:#00e5ff', mask, '-alpha', 'off', '-compose', 'copy_opacity', '-composite', ')',
            '-compose', 'over', '-composite',
            '(', '-size', f'{W}x{H}', 'xc:#ff2bd6', '(', mask, abri, '-compose', 'multiply', '-composite', ')', '-alpha', 'off', '-compose', 'copy_opacity', '-composite', ')',
            '-compose', 'over', '-composite', diff)
        cw, ch = W // COLS, H // ROWS
        cells = []
        for r in range(ROWS):
            for c in range(COLS):
                m = run('magick', mask, '-crop', f'{cw}x{ch}+{c * cw}+{r * ch}', '+repage', '-format', '%[fx:mean]', 'info:').stdout
                cells.append(round(100 * (1 - float(m or 0)), 1))
        for src, suf in ((na, '-A'), (nbal, '-B'), (diff, '-diff')):
            run('magick', src, '-quality', '82', f'{base}{suf}.jpg')
    rel = Path(o.nome).as_posix()
    print(json.dumps({
        'a': f'{rel}-A.jpg', 'b': f'{rel}-B.jpg', 'diff': f'{rel}-diff.jpg', 'la': o.la, 'lb': o.lb,
        'raw': round(raw, 1), 'aligned': round(aligned, 1), 'dy': dy, 'cols': COLS, 'cells': cells,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
