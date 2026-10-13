---
name: roteiro-de-teste
description: Analyze the current project, decide what must be tested by hand on each platform it runs on (iOS, Android, Web), and build or update ONE saveable HTML test checklist per product: platform and round selectors, a variants filter ("Estou jogando"), three columns per card (QA Passou/Falhou · Auditor Passou/Falhou · Não testado) per platform and round, notes, what the QA saw with screenshots, pt/en and light/dark toggles, and a Save button that writes into the file. Later runs add a new round without touching saved marks. Triggers include "/roteiro-de-teste", "monta o roteiro de teste", "o que eu preciso testar?", "cria o HTML de teste", "nova rodada de testes", "quero testar esse projeto na mão".
---

# /roteiro-de-teste

The owner's own tool, also shared with a partner. It turns "what this product does and what changed" into a checklist that is opened in the browser, tested by hand and marked, with each mark saved **inside the HTML file**. Talk to the person in their language. Call them by the name they chose, saved in `~/Ferramentas/html-salvavel/nome.txt` (step 1 asks for it). Until there is one, use their login name: the part of the terminal prompt before the `@` (the output of `whoami`); if it cannot be read, call them "Dev-Tester". If their CLAUDE.md says how to work with them (language, tutor style, one thing at a time, asking before every action), follow it.

**One file per product, growing round by round.** A product with 60 sessions is tested from session 1. Each run of this skill adds a **round** (rodada) with the new cards and sends back for retest whatever failed before. Nothing that was saved is ever lost.

## The pieces

- `pacote/` is the saving tool (master copy): `servidor.py`, `abrir-html-salvavel.command` and `LEIA-ME.md`. Read `pacote/LEIA-ME.md`, because it is the saving contract. The tool **runs** from `~/Ferramentas/html-salvavel/`, an installed copy that is never edited by hand; `backups/` lives there.
- `pacote/referencia/roteiro-modelo.html` is **the model** every checklist is made from. Its page and JS are fixed. A checklist differs from it only in two JSON blocks:
  - `roteiro-config` holds the cards, tabs, platforms, rounds and variants. **Claude writes it** and rewrites it each round.
  - `dados-salvos` holds the marks (`marcas[card][platform][round] = {result, audit, note}`: `result` is the QA column (`pass`/`fail`/`skip`), `audit` the Auditor column (`pass`/`fail`, only allowed once `result` is `pass`), and one shared note) and the device used on each platform. **Only the Save button writes it. Claude never edits it.**
- `ferramentas/roteiro.py` is the only way to write a checklist:
  - `novo <file.html> <config.json> [qa-marks.json]` creates the checklist from the model. It refuses if the file already exists.
  - `config <file.html> <config.json>` replaces only `roteiro-config`, after a backup to `~/Ferramentas/html-salvavel/backups/`. It refuses if the saved marks would change.
  - `molde <file.html>` swaps the page for the current model, keeping the file's config and marks byte for byte (backup first). Use it, after asking, when a checklist was built with an older model.
  - `ler <file.html>` prints the config and the saved marks.
  
  It also rejects a config that repeats a card id, or whose cards point to a tab, platform, round or variant that does not exist.
- `pacote/app/` holds the **"Abrir HTML Salvável" app** for the Dock: its AppleScript, its icon (`AppIcon.icns`, drawn from `icone.svg`) and `instalar-app.sh`, which builds it into `~/Applications`. The app lists the last projects opened (up to 8, in `~/Ferramentas/html-salvavel/ultimos-projetos.txt`) plus "Outra pasta…", checks the folder has a saveable HTML, and starts the server there through `pacote/abrir-pasta.sh`. One app serves every project, so the per-folder `.command` becomes optional.
- `pacote/agentes/` holds copies of the two independent agents, `independent-qa.md` and `independent-auditor.md`, so a new machine gets them too (step 1).

## 1. Prepare the saving (ask first)

- **The person's name.** If `~/Ferramentas/html-salvavel/nome.txt` is missing or empty, ask once, in their language: "Como você gostaria de ser chamado?" (offer their `whoami` name as the default). Save the answer, one line, in that file, and use it from then on. If they say to change it later, rewrite the file.
- If `~/Ferramentas/html-salvavel/` is missing or differs from `pacote/` (`diff -rq`, excluding `backups/`, `nome.txt` and `ultimos-projetos.txt`), propose copying `pacote/` over it with `cp -Rp`, never touching `backups/`, `nome.txt` or `ultimos-projetos.txt`. Then `chmod +x` the `.command` and `servidor.py`. If `python3` is missing, explain the "Instalar" steps in `pacote/LEIA-ME.md`.
- **The Dock app.** If `~/Applications/Abrir HTML Salvável.app` is missing, offer to build it: `zsh ~/Ferramentas/html-salvavel/app/instalar-app.sh`. Then explain: drag it from `~/Applications` to the Dock; the first click explains and asks for the project folder; macOS may ask to let it control Terminal (OK).
- Optionally (the app already covers it), propose copying `abrir-html-salvavel.command` in list mode (`ARQUIVO=""`) into the HTML's folder, usually the project root, with `cp -p`. Remind the person that the first time it needs right-click › Abrir › Abrir, so macOS lets it run.
- Recommend keeping the HTML, the shortcut and the screenshots folder out of git through `.git/info/exclude`.
- **The two independent agents.** Step 5 needs `independent-qa` and `independent-auditor`. This skill carries copies in `pacote/agentes/`. Check `~/.claude/agents/` (and the project's `.claude/agents/`):
  - **missing:** say what each one does and ask before copying it to `~/.claude/agents/` with `cp -p`. Agents load when a session starts, so after installing, ask the person to restart Claude Code before step 5;
  - **present and identical:** nothing to do;
  - **present but different:** show the difference and ask. Never overwrite the person's own version without a yes.
  
  The bundled agents read the project, its tests and git; they do not read a task tracker by themselves. To let them read one, add that tracker's MCP tools to the `tools:` line of each agent.

## 2. First run or new round?

Look for an existing checklist in the project: `grep -l 'id="roteiro-config"' *.html`.
- **None found:** this is the first run, and steps 3–7 build the checklist. Name it `teste<Product>.html` (e.g. `testeTrilhaDosBichos.html`): one per product, never one per platform.
- **Found:** this is a new round. Run `roteiro.py ler` on it first. Its saved marks say what passed, failed or was skipped on each platform. Steps 3–7 then **add to** that config.

## 3. Discover the product

Read these in order and skip whatever does not exist:
1. The project's `CLAUDE.md`, `README`, `spec/` and decision records.
2. The project's task tracker, if it has one and its tools are available (optional). It is read-only here; this skill never writes to it.
3. Git (`git log`, tags, `gh pr list` / `gh pr view`), for what changed since the last round.
4. The code, only to see where a change shows up for the person using the product.

From them, find out:
- **Platforms:** which of iOS, Android and Web the product really ships on. Only those go in `plataformas`.
- **Variants:** versions of the same product that are played or used differently. In the model's fictional example (Trilha dos Bichos) they are Forest and Ocean; a seasonal game would have one per season. Variants feed the "Estou jogando" filter. A variant that arrives later gets `"desde": "R<n>"`.
- **Scope of this round:** the new sessions, features or fixes. If it is unclear, ask **one** question.

## 4. Decide the cards

One card is one thing a person can check by hand, with a clear pass condition.
- **No repeated cards across variants or platforms.** A card valid everywhere is written once. Restrict it only where it truly differs, with `"variacoes": ["hw"]` or `"plataformas": ["android"]`. The same card is marked separately on each platform, so never copy it per platform.
- New cards get `"desde": "<this round>"`. Old cards keep their ids and their `desde`. Never renumber or delete a card that has marks. If it no longer applies, set `"foraDoEscopo": "<why>"`, which removes it from the progress count.
- Card fields:
  - `id`: the issue id when there is one, otherwise `T-01`, `T-02`…;
  - `aba`, `tag`, `corTag` and `titulo`;
  - `passos`: short, concrete steps;
  - `passa`: what counts as passing;
  - optional: `link`/`linkRotulo`, `aviso` and `chips`.
- **Language: always both.** Every text the person reads (titles, steps, pass conditions, tags, notes, tabs, rounds, variants, the header and footer, what the QA saw) is written as `{"pt": "...", "en": "..."}`, never as a plain string. Ask once which language opens first and set `idiomaPadrao` (`"pt"` or `"en"`); the page's PT/EN button switches everything. `roteiro.py` refuses a config with any single-language text and lists what is missing. When updating an older checklist written in one language, translate all of it in the same update.

## 5. The independent QA, per platform, then the Auditor (ask first)

When the product can be run here (emulator, simulator or browser), offer to send the `independent-qa` agent to walk it, **one platform at a time**, with the role and scope the person chooses.
- For each card, it reports: pass, fail or could not test; what it saw; the severity (`blocker`, `major`, `minor` or `cosmetic`); and the names of its screenshots. The screenshots are saved compressed under `images/<checklist name>/`, and that folder goes in `pastaPrints`.
- What it saw goes in the card's `qa` list, for example `{"rodada": "R2", "plataforma": "android", "gravidade": "major", "visto": "...", "prints": ["a.jpg"]}`. A finding that no card covers becomes a new card.
### The approval loop (a card is green only when both approve)

1. **QA tests.** A card the QA fails or could not test **does not go to the Auditor**.
2. **The Auditor reviews only what the QA passed.** For each passed card it checks whether the work behind it followed the project's rules: issue, branch, commits, spec, no AI signature, and the task tracker (if any) matching reality. Give it the linked issue or PR of each card. A passed card with nothing to audit (no issue, PR or commits behind it) is left out, and the hand-over says so. What it saw goes into the same `qa` entry as `"auditor": {"veredito": "pass" | "fail", "visto": "..."}`, shown under what the QA saw. Its verdict itself is the card's **Auditor column** (`audit`). Mark a card with nothing to audit `"semAuditoria": true` (its Auditor column reads "sem auditoria" and the QA pass alone makes it green); a project with no Auditor at all sets `"auditoria": false` in the config.
3. **Rejected by the QA or by the Auditor → the executor fixes it.** The executor is whoever builds the code (the dev, or the dev's coding session following the project's own flow). This skill does not fix code: it hands over the findings and asks before anything goes to the executor.
4. **After the fix, the loop starts again from step 1**: the QA retests, and if it passes, the Auditor reviews again. The fix is a change, so the rules below for changed and linked cards apply.
5. **A card is green only when the QA passed it and the Auditor approved it** (or it is `semAuditoria`). The page derives the card's state from the two columns:
   - QA ✅, Auditor empty → **blue**, "✅ QA aprovou · ⏳ aguardando o Auditor";
   - QA ✅, Auditor ❌ → **red**, "✅ QA aprovou · ❌ Auditor reprovou", and the note holds the Auditor's reason (one note per card: when the QA fails there is no Auditor, and when the Auditor fails the note is its reason);
   - QA ❌ → red, and the Auditor column is greyed out;
   - QA ✅ + Auditor ✅ → **green**.
   Blue and Auditor-rejected cards count as not passed, so they come back in the next round.
6. **Closing.** The product's test can only close when **every** card in scope is green on every platform. Even then, **the dev decides** whether the project is finished; the skill only reports "everything is green" and asks. It never declares the project closed.

### When an approved card comes back

A card approved by the QA and the Auditor is **not retested**, except when:
- **the dev changed it**: list its id in the new round's `"retestar": ["T-01"]`;
- **a card linked to it changed**: a change in A can break B. Cards declare their links with `"ligados": ["T-01"]` (either side is enough; the link works both ways). When A is in `retestar`, every card linked to A comes back too;
- the round is a full regression (`"regressao": true`).

To fill `retestar`, use git: what the commits since the last round touched, mapped to the cards. When writing cards, add `ligados` whenever two cards share a screen, a flow or data. If unsure whether a change touches a card, include it and say why in the plan. The page shows "↻ Alterado: retestar" or "↻ Ligado a T-01" on those cards.

- The QA's and the Auditor's results are marks (`result` and `audit`), so they belong in `dados-salvos`. They can go in only when the file is **created**: pass them as the third argument of `novo`, as `{"marcas": {...}, "env": {...}}`. On an existing file, never write marks; the `qa` entries show what each agent found, and the person marks the two columns by hand.

## 6. Show the plan before building

Send one message, in the person's language, with:
- the platforms, the variants and the new round's name;
- how many cards are new, and how many come back for retest, each with its reason: failed or untested before, rejected by the Auditor, changed by the dev, or linked to a changed card;
- the tabs, with how many cards each;
- one line per new card;
- where the list came from.

**The count comes from the analysis, never from a target.** Wait for approval.

## 7. Build or update

- Write the config JSON in the scratchpad with these keys: `chave` (unique per checklist, it keeps the browser's memory apart), `idiomaPadrao`, `selo`, `titulo`, `tituloAba`, `subtitulo`, `rodape`, `exemplosAparelho`, `plataformas`, `rodadas`, `variacoes`, `abas`, `cards` and `pastaPrints`. Copy the shapes from the example config inside `roteiro-modelo.html`.
- Add the new round at the end of `rodadas`, as `{"id": "R2", "rotulo": {...}, "curto": "R2", "retestar": [...]}`. Add `"regressao": true` when everything must be retested, for example before a release or after a big change.
- The page decides by itself what to test in each round. A card shows up when it is new in that round, when the round is a regression round, when it or a card linked to it is in `retestar`, or when its last result on that platform was not a pass. Earlier passes show faded, as "carried". Nothing needs computing by hand.
- Run `python3 ferramentas/roteiro.py novo|config <file> <config.json>`. Never edit the HTML by hand, and never touch `dados-salvos`.

## 8. Check it before handing over

- Contract: `servidor.html_salvavel(Path(file))` must print `True`. Import it from `pacote/` with `sys.dont_write_bytecode=True`.
- `roteiro.py ler` must show the same number of saved marks as before the update.
- If the model itself changed: extract the last `<script>` and run `node --check` on it.
- When possible, open a **copy** in headless Chrome through `servidor.py`. Switch the platform, round, variant and language; mark a card, save, reload, and see it come back.

## 9. Hand it over

Tell the person:
- the file name and the round;
- how many cards are new and how many come back for retest;
- how to open it: "dois cliques em `abrir-html-salvavel.command`, escolha o arquivo, escolha a plataforma e a rodada";
- how many cards are green on each platform, and, if all are, ask the dev whether the project is finished;
- what the Auditor approved or rejected, and which passed cards it skipped because nothing was behind them;
- what was **not** checked, and why.

Then ask whether to start.

When the person later pastes the "Copiar resultado pro Claude" text, follow the project's own flow for findings. This skill files nothing.
