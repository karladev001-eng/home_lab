Set up a new research project repository.

Usage:
  /new-research <project-name>
  /new-research <project-name> --from <path>   (load from existing files or directory)
  /new-research <project-name> --resume <path> (continue an existing research project)

Arguments: $ARGUMENTS = project name and optional flags

---

## Step 1 — Determine project name

Get the project name from $ARGUMENTS (the part before any flag).
If no name is given, ask the user.

---

## Step 2 — Choose startup mode

Ask the user which mode to use:

> How do you want to start?
> 1. **Scratch** — create empty templates and start fresh
> 2. **From files** — load an existing spec, proposal, notes, or draft to pre-fill the research files
> 3. **Resume** — copy an existing research project directory and continue from where it left off

If `--from <path>` is in $ARGUMENTS, use mode 2 with that path.
If `--resume <path>` is in $ARGUMENTS, use mode 3 with that path.
Otherwise, ask the user to choose.

---

## Step 3 — Collect mode-specific input

### Mode 1: Scratch
Ask the user:
- Research title (optional, can be filled in later)
- Research field (optional)
- Main research question (optional)

Proceed to Step 4.

### Mode 2: From files
Ask the user:
> Please provide one or more of the following (file paths or URLs):
> - Research proposal or grant application
> - Paper draft or outline
> - Research notes or memo
> - Existing research/state.md or similar

Read each provided file. Extract:
- Research title
- Main research question
- Motivation / problem statement
- Proposed method or approach
- Any hypotheses mentioned
- Any references cited
- Current stage of the research

Use this information to pre-fill the research template files in Step 5.
Mark anything unclear or not found as `(to be filled)`.

Proceed to Step 4.

### Mode 3: Resume
Ask the user for the path to the existing research project directory.
Read and inspect:
- `research/state.md`
- `research/questions.md`
- `research/hypotheses.md`
- `research/decisions.md`
- `research/next-actions.md`
- `research/literature/`
- `research/experiments/registry.md`
- `research/slides/`

Copy all `research/` contents to the new project.
Copy `src/`, `scripts/`, `notebooks/`, `outputs/` if they exist.
Skip `.claude/` from the source (will use home_lab's fresh agents instead).

After copying, run `research-state-loader` to regenerate `research/session-brief.md`.

Proceed to Step 4.

---

## Step 4 — Confirm project location

Default parent directory: same parent as the current home_lab directory.
Show the full path and ask the user to confirm before creating anything.

---

## Step 5 — Create project structure

Create:

```
<project-name>/
├── .claude/
│   ├── agents/          ← copy from home_lab/.claude/agents/ (research, code, slides)
│   └── commands/        ← copy from home_lab/.claude/commands/ (exclude new-research.md and new-app.md)
├── CLAUDE.md
├── research/
│   ├── state.md
│   ├── session-brief.md
│   ├── questions.md
│   ├── hypotheses.md
│   ├── decisions.md
│   ├── next-actions.md
│   ├── literature/
│   │   ├── papers.bib
│   │   ├── paper-cards/
│   │   └── search-reports/
│   ├── experiments/
│   │   ├── registry.md
│   │   ├── results/
│   │   ├── logs/
│   │   └── figures/
│   ├── presentation/
│   │   ├── templates/
│   │   └── assets/
│   └── slides/
│       ├── templates/
│       └── assets/
├── src/
├── scripts/
├── notebooks/
└── outputs/
```

Copy agents and commands:
- Copy `home_lab/.claude/agents/research/`, `home_lab/.claude/agents/code/`, `home_lab/.claude/agents/slides/` → `<project>/.claude/agents/`
- Copy all commands from `home_lab/.claude/commands/` EXCEPT `new-research.md` and `new-app.md`

Copy shared presentation templates:
- Copy `home_lab/templates/research/presentation/base/index.html` → `<project>/research/presentation/index.html`
- Copy `home_lab/templates/research/presentation/base/styles.css` → `<project>/research/presentation/styles.css`
- Copy `home_lab/templates/research/presentation/base/style-guide.md` → `<project>/research/presentation/templates/style-guide.md`
- Copy files from `home_lab/templates/research/presentation/assets/` → `<project>/research/presentation/assets/`

Copy shared slide templates:
- Copy `home_lab/templates/research/slides/marp/theme.css` → `<project>/research/slides/templates/theme.css`
- Copy `home_lab/templates/research/slides/marp/style-guide.md` → `<project>/research/slides/templates/style-guide.md`
- Copy files from `home_lab/templates/research/slides/assets/` → `<project>/research/slides/assets/`
- Copy files from `home_lab/templates/research/slides/sample-slides/` → `<project>/research/slides/templates/sample-slides/`

If a destination file already exists because of resume mode, keep the resumed file and do not overwrite it with the shared template.

---

## Step 6 — Write CLAUDE.md

```markdown
# Role

You are my main research partner inside Claude Code.

Your primary job is to help me think through research questions, hypotheses,
models, experiments, results, and paper narratives.

Do not perform long literature searches, large experiment log analysis,
HTML presentation generation, or slide generation directly in the main session.
Delegate those tasks to specialized subagents.

# Context policy

Keep the main conversation compact.
When using subagents, ask them to return only:
- key findings
- evidence
- uncertainty
- recommended next action
- file paths they created or modified

Do not paste long logs, full papers, full code listings, or raw search results
into the main conversation unless explicitly requested.

# Research files

Use these files as persistent research memory:
- research/state.md
- research/session-brief.md
- research/questions.md
- research/hypotheses.md
- research/decisions.md
- research/next-actions.md
- research/literature/
- research/experiments/
- research/presentation/
- research/slides/

# Session startup

At the beginning of a session, use `/research-start` to load the current state.

# Session sync

When finishing a session, use `/research-sync` to save progress.

# Decision style

Always separate:
- facts from papers
- experimental observations
- assumptions and hypotheses
- your own interpretation

# Slide policy

Create HTML presentation artifacts first when the goal is review, sharing,
or iterative refinement.

Slides must not invent results, figures, citations, or conclusions.
Mark missing evidence as TODO instead of fabricating it.
```

---

## Step 7 — Write research template files

**Mode 1 (scratch):** Write empty templates with placeholder text, and keep the copied shared presentation / slide starter files as the initial visual baseline.

**Mode 2 (from files):** Write templates pre-filled with extracted content.
Wrap each extracted section with its source: `(extracted from: <filename>)`.
Mark missing sections as `(to be filled)`.
Also keep the copied shared presentation / slide starter files, then update them later through `/make-presentation` or `/make-slides`.

**Mode 3 (resume):** Files already copied in Step 3. Do not overwrite.
Only copy shared template files when the corresponding destination file or directory is missing.

Template for `research/state.md` (scratch / from files):
```markdown
# Research State

## Title
<title or "(to be filled)">

## Field
<field or "(to be filled)">

## Main research question
<question or "(to be filled)">

## Motivation
<motivation or "(to be filled)">

## Proposed method / model
<method or "(to be filled)">

## Current hypotheses
<hypotheses or "(to be filled)">

## Evidence so far
(none yet)

## Known limitations
(to be filled)

## Current stage
Planning / Literature review / Implementation / Experimentation / Writing
```

Template for `research/questions.md`, `research/hypotheses.md`, `research/decisions.md`,
`research/next-actions.md`, `research/experiments/registry.md`, `research/literature/papers.bib`:
→ Use the same templates as the scratch mode, pre-filled where data was extracted.

---

## Step 8 — Initialize git

```bash
cd <project-name>
git init
```

Create an initial commit after the starter files are in place:

```bash
git add .
git commit -m "chore: initialize research project"
```

If git user identity is not configured and commit fails, note that clearly in the report.

Write `.gitignore`:
```
__pycache__/
*.pyc
.env
*.egg-info/
dist/
.DS_Store
outputs/*.pkl
outputs/*.pt
outputs/*.bin
```

Ask the user:
> Do you want to create a private GitHub repository for this project? (yes/no)

If yes: `gh repo create <project-name> --private --source=. --push`
If no: skip.
If `gh` is unavailable or not logged in, skip GitHub creation and report that local git was initialized without remote publishing.

---

## Step 9 — Report

Return:
- Full path of the created project
- Mode used (scratch / from files / resume)
- Files created or copied
- Shared templates copied (presentation / slides)
- Git initialized status
- Initial commit status
- GitHub repo URL (if created)
- For mode 2: list of what was extracted and what was not found
- For mode 3: summary of the loaded research state (from session-brief.md)
- Next step: `cd <project-name> && claude` then `/research-start`
