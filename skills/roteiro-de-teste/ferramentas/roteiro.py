#!/usr/bin/env python3
"""Cria e atualiza roteiros de teste sem nunca tocar nas marcações salvas.

  python3 roteiro.py novo   <arquivo.html> <config.json> [marcas-do-qa.json]
                                                         cria a partir do modelo (gaveta vazia ou com as marcas do QA)
  python3 roteiro.py config <arquivo.html> <config.json>   troca só o bloco roteiro-config (faz backup)
  python3 roteiro.py molde  <arquivo.html>                 troca a página pelo molde novo, mantendo config e marcações (faz backup)
  python3 roteiro.py ler    <arquivo.html>                 imprime {"config": ..., "dados": ...}

O bloco dados-salvos (a "gaveta") é de quem testa: só o botão Salvar escreve nele.

BDD (opcional): "bdd": {"arquivo": "BDD/bdd-<projeto>.html"} no config, com o caminho relativo
ao roteiro, e "bdd": ["L-03", ...] em cada card. novo/config conferem que o arquivo existe e
que cada id é um cenário dele (class="cen" id="…").
"""
import json, re, shutil, sys, time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
MODELO = AQUI.parent / 'pacote' / 'referencia' / 'roteiro-modelo.html'
CFG_RE = re.compile(r'(<script type="application/json" id="roteiro-config">)(.*?)(</script>)', re.S)
DADOS_RE = re.compile(r'<script type="application/json" id="dados-salvos">(.*?)</script>', re.S)


def bloco(cfg):
    return json.dumps(cfg, ensure_ascii=False, indent=1).replace('</', '<\\/')


def checa(cfg):
    ids = [c['id'] for c in cfg.get('cards', [])]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        sys.exit(f'ids repetidos: {sorted(dup)}')
    abas = {a['id'] for a in cfg.get('abas', [])}
    plats = {p['id'] for p in cfg.get('plataformas', [])}
    rodadas = {r['id'] for r in cfg.get('rodadas', [])}
    vars_ = {v['id'] for v in (cfg.get('variacoes') or {}).get('itens', [])}
    for r in cfg.get('rodadas', []):
        falta = [i for i in r.get('retestar', []) if i not in ids]
        if falta:
            sys.exit(f"rodada {r['id']}: retestar cita cards que não existem {falta}")
    for c in cfg.get('cards', []):
        erros = []
        if c.get('aba') not in abas: erros.append(f"aba {c.get('aba')}")
        if c.get('desde') and c['desde'] not in rodadas: erros.append(f"desde {c['desde']}")
        erros += [f'plataforma {p}' for p in c.get('plataformas', []) if p not in plats]
        erros += [f'variação {v}' for v in c.get('variacoes', []) if v not in vars_]
        erros += [f"qa.rodada {q.get('rodada')}" for q in c.get('qa', []) if q.get('rodada') not in rodadas]
        erros += [f'ligado {i}' for i in c.get('ligados', []) if i not in ids]
        if c.get('bdd') and not (cfg.get('bdd') or {}).get('arquivo'):
            erros.append('bdd.arquivo no config (o card cita cenários do BDD)')
        for q in c.get('qa', []):
            k = q.get('comparacao')
            if k is None:
                continue
            falta = [x for x in ('a', 'b', 'diff', 'la', 'lb', 'raw', 'aligned', 'dy', 'cells') if x not in k]
            if falta or not isinstance(k.get('cells'), list):
                erros.append(f"qa {q.get('rodada')}: comparacao sem {falta or ['cells como lista']} (gere com comparar.py)")
        if erros:
            sys.exit(f"card {c['id']}: não existe {', '.join(erros)}")


def checa_bdd(cfg, alvo):
    """O BDD citado existe ao lado do roteiro e tem cada cenário que os cards apontam."""
    arq = (cfg.get('bdd') or {}).get('arquivo')
    if not arq:
        return
    bdd = (alvo.resolve().parent / arq)
    if not bdd.is_file():
        sys.exit(f'bdd.arquivo {arq}: não existe {bdd}')
    cenarios = set(re.findall(r'class="cen" id="([^"]+)"', bdd.read_text(encoding='utf-8')))
    falta = [f"{c['id']}→{i}" for c in cfg.get('cards', []) for i in c.get('bdd', []) if i not in cenarios]
    if falta:
        sys.exit(f'cenários que não existem em {arq}: {falta}')


def backup(alvo):
    pasta = Path.home() / 'Ferramentas' / 'html-salvavel' / 'backups'
    pasta.mkdir(parents=True, exist_ok=True)
    copia = pasta / f'{time.strftime("%Y-%m-%d_%H%M%S")}_antes-da-rodada__{alvo.name}'
    n = 2
    while copia.exists():
        copia = pasta / f'{time.strftime("%Y-%m-%d_%H%M%S")}-{n}_antes-da-rodada__{alvo.name}'
        n += 1
    shutil.copy2(alvo, copia)
    return copia


def bilingue(cfg):
    """Todo texto que a pessoa lê precisa ter as duas línguas: {"pt": ..., "en": ...}."""
    faltas = []
    def olha(onde, v):
        if v is None or v == '':
            return
        if not (isinstance(v, dict) and str(v.get('pt', '')).strip() and str(v.get('en', '')).strip()):
            faltas.append(onde)
    for k in ('selo', 'titulo', 'tituloAba', 'subtitulo', 'rodape'):
        olha(k, cfg.get(k))
    for r in cfg.get('rodadas', []):
        olha(f"rodada {r.get('id')}", r.get('rotulo'))
    var = cfg.get('variacoes') or {}
    for k in ('rotulo', 'todos', 'todosRotulo'):
        olha(f'variacoes.{k}', var.get(k))
    for v in var.get('itens', []):
        olha(f"variação {v.get('id')}", v.get('rotulo'))
    for a in cfg.get('abas', []):
        for k in ('titulo', 'selo', 'sub'):
            olha(f"aba {a.get('id')}.{k}", a.get(k))
    for c in cfg.get('cards', []):
        cid = c.get('id')
        for k in ('titulo', 'passa', 'tag', 'aviso', 'foraDoEscopo', 'linkRotulo'):
            olha(f'{cid}.{k}', c.get(k))
        for i, x in enumerate(c.get('passos', []), 1):
            olha(f'{cid}.passos[{i}]', x)
        for i, x in enumerate(c.get('chips', []), 1):
            olha(f'{cid}.chips[{i}]', x)
        for q in c.get('qa', []):
            olha(f"{cid}.qa[{q.get('rodada')}].visto", q.get('visto'))
            olha(f"{cid}.qa[{q.get('rodada')}].auditor", (q.get('auditor') or {}).get('visto'))
    if faltas:
        mostra = ', '.join(faltas[:15]) + (f' … (+{len(faltas) - 15})' if len(faltas) > 15 else '')
        sys.exit(f'{len(faltas)} texto(s) sem as duas línguas {{"pt", "en"}}: {mostra}')


def ler_cfg(caminho):
    cfg = json.loads(Path(caminho).read_text(encoding='utf-8'))
    checa(cfg)
    bilingue(cfg)
    return cfg


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    cmd, alvo = sys.argv[1], Path(sys.argv[2])
    if cmd == 'ler':
        html = alvo.read_text(encoding='utf-8')
        cfg = json.loads(CFG_RE.search(html).group(2).replace('<\\/', '</'))
        dados = json.loads(DADOS_RE.search(html).group(1) or '{}')
        print(json.dumps({'config': cfg, 'dados': dados}, ensure_ascii=False, indent=1))
        return
    if cmd == 'molde':
        velho = alvo.read_text(encoding='utf-8')
        cfg_txt, dados_txt = CFG_RE.search(velho).group(2), DADOS_RE.search(velho).group(0)
        copia = backup(alvo)
        html = CFG_RE.sub(lambda m: m.group(1) + cfg_txt + m.group(3), MODELO.read_text(encoding='utf-8'), count=1)
        html = DADOS_RE.sub(lambda m: dados_txt, html, count=1)
        if DADOS_RE.search(html).group(0) != dados_txt or CFG_RE.search(html).group(2) != cfg_txt:
            sys.exit('config ou marcações mudariam: nada foi gravado')
        alvo.write_text(html, encoding='utf-8')
        print('backup', copia); print('ok', alvo, 'página atualizada; cards e marcações iguais')
        return
    cfg = ler_cfg(sys.argv[3])
    checa_bdd(cfg, alvo)
    if cmd == 'novo':
        if alvo.exists():
            sys.exit(f'{alvo} já existe: use "config" para atualizar, nunca "novo"')
        html = MODELO.read_text(encoding='utf-8')
        dados = Path(sys.argv[4]).read_text(encoding='utf-8') if len(sys.argv) > 4 else '{}'
        dados = json.loads(dados)
        if dados.get('marcas'):
            dados.setdefault('versao', 2)
            dados.setdefault('salvoEm', time.strftime('%Y-%m-%dT%H:%M:%S'))
        dados = json.dumps(dados, ensure_ascii=False).replace('</', '<\\/')
        html = DADOS_RE.sub(lambda m: f'<script type="application/json" id="dados-salvos">{dados}</script>', html, count=1)
    elif cmd == 'config':
        html = alvo.read_text(encoding='utf-8')
        print('backup', backup(alvo))
    else:
        sys.exit(__doc__)
    antes = DADOS_RE.search(html).group(0)
    novo = CFG_RE.sub(lambda m: m.group(1) + bloco(cfg) + m.group(3), html, count=1)
    if DADOS_RE.search(novo).group(0) != antes or len(DADOS_RE.findall(novo)) != 1:
        sys.exit('a gaveta dados-salvos mudaria: nada foi gravado')
    alvo.write_text(novo, encoding='utf-8')
    print('ok', alvo, f"({len(cfg.get('cards', []))} cards, {len(cfg.get('rodadas', []))} rodadas)")


if __name__ == '__main__':
    main()
