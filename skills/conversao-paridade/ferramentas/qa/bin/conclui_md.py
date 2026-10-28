import sys,re
p, status, texto = sys.argv[1], sys.argv[2], sys.argv[3]
s=open(p).read()
s=re.sub(r'\| Status \| .* \|', f'| Status | {status} |', s)
s=s[:s.index('## Decisão')]+'## Decisão\n'+texto+'\n'
open(p,'w').write(s)
