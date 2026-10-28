#!/usr/bin/env python3
"""The only tool that writes test results into a BDD page. Works for any stack.

  bdd_html.py resultados <page.html> <cucumber.json> <features-dir>
      Reads a Cucumber JSON report (pytest-bdd --cucumberjson, cucumber-js
      --format json, Cucumber-JVM json plugin, ...), and writes every scenario's
      status, failure message, .feature file/line and Gherkin text into the
      page's <script id="bdd-resultados"> block. Nothing else in the page changes.

  bdd_html.py verificar <page.html> <features-dir>
      Checks the page on its own: every internal link points to an id that
      exists, scenario ids are unique, and every scenario card (except AC-NN
      findings) pairs with a tagged scenario in the .feature files, and back.
      Exit 1 when something is wrong.

Scenario ids are tags like @L-03 (letters, dash, number). A scenario tagged
@manual counts as "check by hand". Standard library only.
"""
import json
import re
import sys
import time
from pathlib import Path

BLOCK = re.compile(r'(<script type="application/json" id="bdd-resultados">)(.*?)(</script>)', re.S)
SCENARIO_ID = re.compile(r"^[A-Z]+-\d+$")
CARD = re.compile(r'<div class="cen" id="([^"]+)"')
HREF = re.compile(r'href="#([^"]+)"')
ANY_ID = re.compile(r'\sid="([^"]+)"')
COMMENT = re.compile(r"<!--.*?-->", re.S)

# Gherkin keywords, English and Portuguese (the two languages /bdd-antes writes).
BACKGROUND = ("Background:", "Contexto:", "Cenário de Fundo:", "Cenario de Fundo:", "Fundo:")
SCENARIO = ("Scenario:", "Scenario Outline:", "Scenario Template:", "Example:",
            "Cenário:", "Cenario:", "Esquema do Cenário:", "Esquema do Cenario:",
            "Delineação do Cenário:", "Delineacao do Cenario:", "Exemplo:")
RULE = ("Rule:", "Regra:")


def ids_of(tag_line):
    return [t.lstrip("@") for t in tag_line.split() if SCENARIO_ID.match(t.lstrip("@"))]


def feature_scenarios(features_dir):
    """Scenario id -> {feature, line, gherkin} read from the .feature files."""
    base = Path(features_dir)
    where, dupes = {}, []
    for f in sorted(base.rglob("*.feature")):
        lines = f.read_text(encoding="utf-8").splitlines()
        stripped = [l.strip() for l in lines]
        background = []
        for i, s in enumerate(stripped):
            if s.startswith(BACKGROUND):
                for nxt in lines[i:]:
                    if not nxt.strip():
                        break
                    background.append(nxt)
                break
        for i, s in enumerate(stripped):
            if not s.startswith(SCENARIO):
                continue
            first = i
            while first > 0 and stripped[first - 1].startswith("@"):
                first -= 1
            last = i + 1
            while last < len(lines) and not stripped[last].startswith(("@",) + SCENARIO + RULE):
                last += 1
            body = lines[first:last]
            while body and not body[-1].strip():
                body.pop()
            text = "\n".join(background + [""] + body) if background else "\n".join(body)
            text = "\n".join(l[2:] if l.startswith("  ") else l for l in text.splitlines())
            rel = f.relative_to(base.parent).as_posix()
            # Some runners leave skipped scenarios out of the report: @manual is read here too.
            manual = any(t.lstrip("@") == "manual" for tl in stripped[first:i] for t in tl.split())
            for tag_line in stripped[first:i]:
                for sid in ids_of(tag_line):
                    if sid in where:
                        dupes.append(sid)
                    where[sid] = {"feature": rel, "line": i + 1, "gherkin": text, "manual": manual}
    return where, dupes


def report_results(report):
    """Scenario id -> {status, message} from a Cucumber JSON report."""
    results = {}
    for feature in json.loads(Path(report).read_text(encoding="utf-8")):
        for el in feature.get("elements", []):
            if el.get("type", "scenario") == "background":
                continue
            tags = [t.get("name", "").lstrip("@") for t in el.get("tags", [])]
            steps = el.get("steps", []) + el.get("before", []) + el.get("after", [])
            statuses = [s.get("result", {}).get("status", "") for s in steps]
            message = ""
            if "manual" in tags:
                status = "manual"
            elif "failed" in statuses:
                status = "failed"
                failed = next(s for s in steps if s.get("result", {}).get("status") == "failed")
                message = failed["result"].get("error_message") or ""
                # pytest puts the whole traceback here; its "E   ..." lines are the error itself.
                e_lines = [l[1:].strip() for l in message.splitlines() if l.startswith("E ")]
                message = ("\n".join(e_lines) if e_lines else message)[:300]
            elif statuses and all(s == "passed" for s in statuses):
                status = "passed"
            else:
                status = "not-run"
                message = ", ".join(sorted(set(statuses) - {"passed"})) or "no steps"
            for sid in (t for t in tags if SCENARIO_ID.match(t)):
                prev = results.get(sid)
                # A scenario outline runs once per example: one failure fails the scenario.
                if prev and prev["status"] == "failed":
                    continue
                results[sid] = {"status": status, "message": message}
    return results


def resultados(page, report, features_dir):
    page = Path(page)
    html = page.read_text(encoding="utf-8")
    m = BLOCK.search(html)
    if not m:
        sys.exit(f"{page}: no #bdd-resultados block (was the page made from bdd-modelo.html?)")
    where, _ = feature_scenarios(features_dir)
    runs = report_results(report)
    scenarios = {}
    for sid, loc in where.items():
        manual = loc.pop("manual")
        res = {"status": "manual", "message": ""} if manual else runs.get(sid, {"status": "not-run", "message": "not in the report"})
        scenarios[sid] = {**res, **loc}
    block = json.dumps({"generated": time.strftime("%Y-%m-%dT%H:%M:%S"), "scenarios": scenarios},
                       ensure_ascii=False, indent=1).replace("</", "<\\/")
    page.write_text(BLOCK.sub(lambda x: x.group(1) + block + x.group(3), html, count=1), encoding="utf-8")
    tally = {}
    for s in scenarios.values():
        tally[s["status"]] = tally.get(s["status"], 0) + 1
    print(f"{page.name}: {len(scenarios)} scenarios · " + " · ".join(f"{k} {v}" for k, v in sorted(tally.items())))


def verificar(page, features_dir):
    html = COMMENT.sub("", Path(page).read_text(encoding="utf-8"))
    problems = []
    main = html.split("<main>", 1)[-1].split("</main>", 1)[0]
    ids = ANY_ID.findall(html)
    seen = set()
    for i in ids:
        if i in seen:
            problems.append(f"repeated id: {i}")
        seen.add(i)
    for target in sorted(set(HREF.findall(main)) - seen):
        problems.append(f"link to a missing id: #{target}")
    if 'id="inicio"' not in html:
        problems.append('no first tab with id="inicio"')
    cards = [c for c in CARD.findall(main) if not c.startswith("AC-")]
    where, dupes = feature_scenarios(features_dir)
    problems += [f"scenario id used twice in the .feature files: {d}" for d in dupes]
    only_page = [c for c in cards if c not in where]
    only_feature = [s for s in where if s not in cards]
    if only_page:
        problems.append("only on the page: " + ", ".join(only_page))
    if only_feature:
        problems.append("only in the .feature files: " + ", ".join(only_feature))
    m = BLOCK.search(html)
    try:
        json.loads(m.group(2) or "{}") if m else problems.append("no #bdd-resultados block")
    except ValueError:
        problems.append("#bdd-resultados is not valid JSON")
    links = len(HREF.findall(main))
    print(f"{Path(page).name}: {len(cards)} scenario cards, {len(where)} in the .feature files, {links} links")
    for p in problems:
        print("  ✗ " + p)
    if not problems:
        print("  ✓ links, ids and pairs all ok")
    return 1 if problems else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) == 4 and a[0] == "resultados":
        resultados(a[1], a[2], a[3])
    elif len(a) == 3 and a[0] == "verificar":
        sys.exit(verificar(a[1], a[2]))
    else:
        sys.exit(__doc__)
