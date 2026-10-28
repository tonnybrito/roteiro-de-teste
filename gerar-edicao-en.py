#!/usr/bin/env python3
"""Builds the English edition of the skill family from the Portuguese one.

  python3 gerar-edicao-en.py

The Portuguese skills in skills/ are the master. This script regenerates, from them:
  skills-en/              the same seven skills, with English command names
  instalar-en.sh          the installer of the English edition
  escolher-skills-en.sh   the macOS choice popup of the English edition
Never edit those by hand: change the Portuguese master and run this again.
Only the command names, the package paths that point to them and the installer
texts change; the instructions inside the skills are already in English.
"""
import re
import shutil
from pathlib import Path

AQUI = Path(__file__).resolve().parent
NOMES = {
    "roteiro-de-teste": "test-checklist",
    "bdd-antes": "bdd-first",
    "conversao-preparar": "conversion-prepare",
    "conversao-fidelidade": "conversion-fidelity",
    "conversao-paridade": "conversion-parity",
    "conversao-android": "conversion-android",
    "conversao-ios": "conversion-ios",
}
# A name is replaced only as a whole word: "conversao-ios" must not touch "conversao-ios-android".
NOME_RE = re.compile(r"(?<![\w-])(" + "|".join(sorted(map(re.escape, NOMES), key=len, reverse=True)) + r")(?![\w-])")
TEXTO = {".md", ".py", ".sh", ".html", ".js", ".css", ".yaml", ".yml", ".applescript", ".command", ".txt", ".json", ".svg"}


def traduz(texto):
    texto = texto.replace("conversao-ios-android/skills/", "conversao-ios-android/skills-en/")
    texto = texto.replace("escolher-skills.sh", "escolher-skills-en.sh").replace("instalar.sh", "instalar-en.sh")
    return NOME_RE.sub(lambda m: NOMES[m.group(1)], texto)


def copia_skills():
    destino = AQUI / "skills-en"
    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir()
    for origem in sorted((AQUI / "skills").iterdir()):
        alvo = destino / (NOMES.get(origem.name, origem.name))
        if origem.is_dir():
            shutil.copytree(origem, alvo, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
        else:
            shutil.copy2(origem, alvo)
    for f in destino.rglob("*"):
        if f.is_file() and f.suffix in TEXTO:
            antes = f.read_text(encoding="utf-8")
            depois = traduz(antes)
            if depois != antes:
                f.write_text(depois, encoding="utf-8")
    # The package's instructions (instalar-app.sh, instalar.sh) are run by path; keep them executable.
    for f in destino.rglob("*.sh"):
        f.chmod(0o755)
    for f in destino.rglob("*.command"):
        f.chmod(0o755)


ESCOLHER_TEXTOS = [
    ("# Janela de escolha da família de skills (passo 0 de cada skill da família).", "# Choice window of the skill family (step 0 of every skill in the family). English edition."),
    ("checklists de teste em HTML que salvam (base das de conversão)", "HTML test checklists that save (base of the conversion skills)"),
    ("BDD antes do código: features, steps, runner e o HTML ligado ao roteiro", "BDD before code: features, steps, runner and the page linked to the checklist"),
    ("começar uma conversão iPhone ⇄ Android, nos dois sentidos", "start an iPhone ⇄ Android conversion, either way"),
    ("igualar uma tela ao app de referência, pixel por pixel", "make one screen match the reference app, pixel by pixel"),
    ("robô compara o app inteiro nos dois celulares", "a robot compares the whole app on both phones"),
    ("alvo Android: letra grande, teclado, voltar, Play Store", "Android target: large font, keyboard, back, Play Store"),
    ("alvo iPhone: letra grande, ilha, teclado, gesto de voltar, App Store", "iPhone target: large text, island, keyboard, swipe-back, App Store"),
    ('echo "ainda não criada"', 'echo "not created yet"'),
    ('echo "falta"', 'echo "missing"'),
    ('echo "instalada" || echo "desatualizada"', 'echo "installed" || echo "outdated"'),
    ('with title "Família de skills"', 'with title "Skill family"'),
    ('with prompt "Marque as skills que você quer neste projeto (⌘ + clique para marcar várias). A /test-checklist é a base: entra primeiro se você escolher uma de conversão."',
     'with prompt "Tick the skills you want in this project (⌘ + click to tick several). /test-checklist is the base: it comes first if you pick a conversion skill."'),
    ('OK button name "Continuar" cancel button name "Cancelar"', 'OK button name "Continue" cancel button name "Cancel"'),
    ("# No macOS abre um popup nativo com as sete skills e a situação de cada uma, e imprime\n# as escolhidas separadas por vírgula (ex.: \"bdd-first,conversion-android\"), ou CANCELADO.\n# Fora do macOS imprime SEM-POPUP e sai com 3: a skill então pergunta pela janela do Claude.",
     "# On macOS it opens a native popup with the seven skills and the state of each, and prints\n# the chosen ones separated by commas (e.g. \"bdd-first,conversion-android\"), or CANCELADO.\n# Off macOS it prints SEM-POPUP and exits 3: the skill then asks through Claude's own window."),
]
INSTALAR_TEXTOS = [
    ("# Instala as skills da família (test-checklist, bdd-first e as de conversão iPhone ⇄ Android, nos dois sentidos) em ~/.claude/skills.\n# A /test-checklist é a base das de conversão: entra SEMPRE primeiro quando uma delas é escolhida.\n# A /bdd-first funciona sozinha: escolhida sozinha, entra sem a /test-checklist.",
     "# Installs the family's skills (test-checklist, bdd-first and the iPhone ⇄ Android conversion skills, either way) into ~/.claude/skills. English edition.\n# /test-checklist is the base of the conversion skills: it ALWAYS comes first when one of them is chosen.\n# /bdd-first works alone: chosen alone, it is installed without /test-checklist."),
    ("menu: 1 só a test-checklist · 2 escolher · 3 todas", "menu: 1 only test-checklist · 2 choose · 3 all"),
    ("sem menu, instala todas as que o pacote tem", "no menu, installs every skill the package has"),
    ("sem menu, só as citadas (+ test-checklist se houver uma de conversão)", "no menu, only those named (+ test-checklist if a conversion skill is named)"),
    ("#   --atalhos sim|nao                                com a test-checklist: o botão do HTML editável no Dock e na Mesa\n#                                                    (sem a opção, pergunta; sem terminal para perguntar, não cria)",
     "#   --atalhos yes|no                                 with test-checklist: the editable-HTML button in the Dock and on the Desktop\n#                                                    (without it, asks; with no terminal to ask, does not create them)"),
    ("# Antes de trocar uma skill que já existe e é diferente, guarda uma cópia em ~/Ferramentas/html-salvavel/backups/.\n# No fim, abre o GUIA.html no navegador, na aba da skill instalada, mostrando só o que está instalado.",
     "# Before replacing an existing skill that differs, keeps a copy in ~/Ferramentas/html-salvavel/backups/.\n# At the end, opens GUIA.html in the browser, on the installed skill's tab, showing what is installed."),
    ('echo "uso: zsh instalar-en.sh [--todas | --skills a,b] [--atalhos sim|nao]"', 'echo "usage: zsh instalar-en.sh [--todas | --skills a,b] [--atalhos yes|no]"'),
    ('echo "Família de skills: /test-checklist, /bdd-first e as de conversão iPhone ⇄ Android"', 'echo "Skill family: /test-checklist, /bdd-first and the iPhone ⇄ Android conversion skills"'),
    ('echo "A /test-checklist é a base das de conversão e entra primeiro quando uma delas é escolhida."', 'echo "/test-checklist is the base of the conversion skills and comes first when one of them is chosen."'),
    ('echo "  1) só a /test-checklist"', 'echo "  1) only /test-checklist"'),
    ('echo "  2) escolher"', 'echo "  2) choose"'),
    ('echo "  3) todas"', 'echo "  3) all"'),
    ('read "op?Escolha 1, 2 ou 3: "', 'read "op?Pick 1, 2 or 3: "'),
    ('read "r?Instalar /$s? (s/n) "; [[ "$r" == [sS]* ]]', 'read "r?Install /$s? (y/n) "; [[ "$r" == [yY]* ]]'),
    ('echo "  /$s: ainda não criada"', 'echo "  /$s: not created yet"'),
    ('echo "Opção inválida: nada foi instalado."', 'echo "Invalid option: nothing was installed."'),
    ('echo "Skill desconhecida ou ainda não criada: $s (nada foi instalado)"', 'echo "Unknown skill or not created yet: $s (nothing was installed)"'),
    ("# A /test-checklist entra primeiro quando há alguma de conversão escolhida.", "# /test-checklist comes first when any conversion skill is chosen."),
    ('echo "Nada escolhido: nada foi instalado."', 'echo "Nothing chosen: nothing was installed."'),
    ('echo "= /$nome já está atualizada"', 'echo "= /$nome is already up to date"'),
    ('echo "  cópia de segurança da versão antiga: $BK/$nome"', 'echo "  backup of the old version: $BK/$nome"'),
    ('echo "+ /$nome instalada"', 'echo "+ /$nome installed"'),
    ('# O botão do HTML editável: a ferramenta que salva, o app "Abrir HTML Salvável" e o atalho dele no Dock e na Mesa.', '# The editable-HTML button: the saving tool, the "Abrir HTML Salvável" app and its shortcut in the Dock and on the Desktop.'),
    ('echo "A /test-checklist abre os HTMLs editáveis por um botão: o app \\"Abrir HTML Salvável\\"."', 'echo "/test-checklist opens the editable HTML pages through a button: the \\"Abrir HTML Salvável\\" app (Open Saveable HTML)."'),
    ('read "r?Colocar esse botão no Dock e na Mesa (Desktop)? (s/n) "\n      [[ "$r" == [sS]* ]] && ATALHOS=sim || ATALHOS=nao', 'read "r?Put that button in the Dock and on the Desktop? (y/n) "\n      [[ "$r" == [yY]* ]] && ATALHOS=sim || ATALHOS=nao'),
    ('echo "+ app \\"Abrir HTML Salvável\\" em ~/Applications"', 'echo "+ \\"Abrir HTML Salvável\\" app in ~/Applications"'),
    ('echo "+ botão no Dock"', 'echo "+ button in the Dock"'),
    ('echo "= o botão já está no Dock"', 'echo "= the button is already in the Dock"'),
    ('"$HOME/Desktop/Guia das skills.html"', '"$HOME/Desktop/Skills guide.html"'),
    ('echo "+ na Mesa: \\"Abrir HTML Salvável\\" e \\"Guia das skills\\""', 'echo "+ on the Desktop: \\"Abrir HTML Salvável\\" and \\"Skills guide\\""'),
    ("# O que existe de fato (de uma instalação de agora ou de antes), para o guia mostrar.", "# What really exists (from this install or an earlier one), for the guide to show."),
    ("# O guia mostra o que está instalado: o instalador escreve instaladas.js ao lado do GUIA.html.", "# The guide shows what is installed: the installer writes instaladas.js next to GUIA.html."),
    ('// Escrito pelo instalador em $(date "+%Y-%m-%d %H:%M"). Não editar: rode o instalador de novo.', '// Written by the installer on $(date "+%Y-%m-%d %H:%M"). Do not edit: run the installer again.'),
    ('echo "! Falta o agente $a:', 'echo "! Missing the agent $a:'),
    ('echo "Pronto. Reinicie o Claude Code para as skills novas aparecerem."', 'echo "Done. Restart Claude Code for the new skills to show up."'),
    ('echo "Abrindo o guia das skills no navegador: $AQUI/GUIA.html"', 'echo "Opening the skills guide in the browser: $AQUI/GUIA.html"'),
    ('[[ "$ATALHOS" == (sim|yes) ]]', '[[ "$ATALHOS" == (sim|yes) ]]'),
]


def script(nome_pt, nome_en, textos):
    t = traduz((AQUI / nome_pt).read_text(encoding="utf-8"))
    t = t.replace('"$AQUI/skills/', '"$AQUI/skills-en/')
    for a, b in textos:
        if a not in t:
            raise SystemExit(f"{nome_en}: text not found, update gerar-edicao-en.py: {a[:70]}")
        t = t.replace(a, b)
    if nome_en == "instalar-en.sh":
        t = re.sub(r"^TODAS=\(.*\)$", "TODAS=(roteiro-de-teste bdd-antes conversao-preparar conversao-fidelidade conversao-paridade conversao-android conversao-ios test-checklist bdd-first $CONVERSAO)", t, count=1, flags=re.M)
    # Guard: the English edition never installs next to the Portuguese one.
    if nome_en == "instalar-en.sh":
        guarda = ('\nfor s in roteiro-de-teste bdd-antes conversao-preparar conversao-fidelidade conversao-paridade conversao-android conversao-ios; do\n'
                  '  [[ -d "$DEST/$s" ]] && echo "! The Portuguese edition is installed (/$s). Both editions do the same thing: keep only one (remove ~/.claude/skills/$s to switch)."\n'
                  'done\n')
        t = t.replace('mkdir -p "$DEST"\n', 'mkdir -p "$DEST"' + guarda, 1)
    alvo = AQUI / nome_en
    alvo.write_text(t, encoding="utf-8")
    alvo.chmod(0o755)


copia_skills()
script("escolher-skills.sh", "escolher-skills-en.sh", ESCOLHER_TEXTOS)
script("instalar.sh", "instalar-en.sh", INSTALAR_TEXTOS)
print("ok: skills-en/ (" + ", ".join(NOMES.values()) + "), instalar-en.sh, escolher-skills-en.sh")
