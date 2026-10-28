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
    ('echo "Família de skills: /test-checklist, /bdd-first e as de conversão iPhone ⇄ Android"', 'echo "Skill family: /test-checklist, /bdd-first and the iPhone ⇄ Android conversion skills"'),
    ('echo "A /test-checklist é a base das de conversão e entra primeiro quando uma delas é escolhida."', 'echo "/test-checklist is the base of the conversion skills and comes first when one of them is chosen."'),
    ('echo "  1) só a /test-checklist"', 'echo "  1) only /test-checklist"'),
    ('echo "  2) escolher"', 'echo "  2) choose"'),
    ('echo "  3) todas"', 'echo "  3) all"'),
    ('read "op?Escolha 1, 2 ou 3: "', 'read "op?Pick 1, 2 or 3: "'),
    ('read "r?Instalar /$s? (s/n) "; [[ "$r" == [sS]* ]]', 'read "r?Install /$s? (y/n) "; [[ "$r" == [yY]* ]]'),
    ('echo "  /$s: ainda não criada"', 'echo "  /$s: not created yet"'),
    ('echo "Opção inválida: nada foi instalado."', 'echo "Invalid option: nothing was installed."'),
    ('echo "uso: zsh instalar-en.sh [--todas | --skills a,b]"', 'echo "usage: zsh instalar-en.sh [--todas | --skills a,b]"'),
    ('echo "Skill desconhecida ou ainda não criada: $s (nada foi instalado)"', 'echo "Unknown skill or not created yet: $s (nothing was installed)"'),
    ('echo "Nada escolhido: nada foi instalado."', 'echo "Nothing chosen: nothing was installed."'),
    ('echo "= /$nome já está atualizada"', 'echo "= /$nome is already up to date"'),
    ('echo "  cópia de segurança da versão antiga: $BK/$nome"', 'echo "  backup of the old version: $BK/$nome"'),
    ('echo "+ /$nome instalada"', 'echo "+ /$nome installed"'),
    ('echo "Pronto. Reinicie o Claude Code para as skills novas aparecerem."', 'echo "Done. Restart Claude Code for the new skills to show up."'),
    ("# Instala as skills da família (test-checklist, bdd-first e as de conversão iPhone ⇄ Android, nos dois sentidos) em ~/.claude/skills.\n# A /test-checklist é a base das de conversão: entra SEMPRE primeiro quando uma delas é escolhida.",
     "# Installs the family's skills (test-checklist, bdd-first and the iPhone ⇄ Android conversion skills, either way) into ~/.claude/skills.\n# /test-checklist is the base of the conversion skills: it ALWAYS comes first when one of them is chosen. English edition."),
    ("menu: 1 só a test-checklist · 2 escolher · 3 todas", "menu: 1 only test-checklist · 2 choose · 3 all"),
    ("sem menu, só as citadas (+ test-checklist se houver uma de conversão)", "no menu, only those named (+ test-checklist if a conversion skill is named)"),
    ("# Antes de trocar uma skill que já existe e é diferente, guarda uma cópia em ~/Ferramentas/html-salvavel/backups/.", "# Before replacing an existing skill that differs, keeps a copy in ~/Ferramentas/html-salvavel/backups/."),
    ("# A /test-checklist entra primeiro quando há alguma de conversão escolhida.", "# /test-checklist comes first when any conversion skill is chosen."),
    ("# O que a /test-checklist precisa fora das skills: só avisa; a própria skill pergunta antes de instalar", "# What /test-checklist needs outside the skills: only a warning; the skill itself asks before installing"),
    ('echo "! Falta a ferramenta que salva no HTML: peça ao Claude \\"/test-checklist\\" (passo 1) ou copie skills/test-checklist/pacote para ~/Ferramentas/html-salvavel"',
     'echo "! Missing the tool that saves into the HTML: ask Claude for \\"/test-checklist\\" (step 1) or copy skills-en/test-checklist/pacote to ~/Ferramentas/html-salvavel"'),
    ('echo "! Falta o app da Dock: zsh ~/Ferramentas/html-salvavel/app/instalar-app.sh"', 'echo "! Missing the Dock app: zsh ~/Ferramentas/html-salvavel/app/instalar-app.sh"'),
    ('echo "! Falta o agente $a:', 'echo "! Missing the agent $a:'),
]


def script(nome_pt, nome_en, textos):
    t = traduz((AQUI / nome_pt).read_text(encoding="utf-8"))
    t = t.replace('"$AQUI/skills/', '"$AQUI/skills-en/')
    for a, b in textos:
        if a not in t:
            raise SystemExit(f"{nome_en}: text not found, update gerar-edicao-en.py: {a[:70]}")
        t = t.replace(a, b)
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
