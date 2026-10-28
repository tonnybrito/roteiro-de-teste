import json, os, sys
# Pasta dos relatórios: 2º argumento, senão qa-relatorios/ na pasta atual.
base = sys.argv[2] if len(sys.argv) > 2 else 'qa-relatorios'
data = json.load(open(sys.argv[1]))
for f in data:
    d = os.path.join(base, f['ciclo']); os.makedirs(d, exist_ok=True)
    nome = f"{f['id']}-{f['slug']}.md"
    ev = '\n'.join('- ' + e for e in f['evidencia'])
    md = f"""# {f['id']} · {f['titulo']}

| Campo | Valor |
|---|---|
| Rodada | R3 (celular × celular) · iPhone 17 × Pixel 9 Pro XL |
| Ciclo | {f['ciclo_nome']} |
| Tela | `{f['tela']}` |
| Gravidade | **{f['gravidade']}** |
| Comparado com | {f['comparado']} |
| Status | ⏳ aguardando decisão do dev |

## O que o QA viu (Android)
{f['visto']}

## O que era esperado
{f['esperado']}

## Evidências
{ev}

## Causa provável
{f.get('causa') or 'Não apontada.'}

## Decisão
- [ ] Corrigir
- [ ] Não corrigir (motivo):
"""
    open(os.path.join(d, nome), 'w').write(md)
print('ok', len(data))
