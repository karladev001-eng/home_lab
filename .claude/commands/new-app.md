Start a new app generation project.

Usage:
  /new-app <project-name>
  /new-app <project-name> --from <path>   (load from existing spec/requirements doc)
  /new-app <project-name> --resume <path> (resume a project that was already started)

Arguments: $ARGUMENTS = project name and optional flags

Project name must be lowercase kebab-case (letters, numbers, hyphens only).

---

## Step 1 — Determine project name

Get the project name from $ARGUMENTS (the part before any flag).
If no name is given, ask the user.

---

## Step 2 — Choose startup mode

Ask the user which mode to use:

> How do you want to start?
> 1. **Scratch** — describe your app idea and start fresh
> 2. **From spec** — load an existing requirements doc, design spec, or notes to use as Phase 1 input
> 3. **Resume** — continue a project that was already started (has pipeline_state.yaml)

If `--from <path>` is in $ARGUMENTS, use mode 2 with that path.
If `--resume <path>` is in $ARGUMENTS, use mode 3 with that path.
Otherwise, ask the user to choose.

---

## Step 3 — Collect mode-specific input

### Mode 1: Scratch
Collect from the user:
- **App idea**: What do you want to build? (natural language description)
- **Platforms**: Select one or more:
  - `web` — React/Vue web application
  - `mobile` — iOS/Android mobile app (React Native / Flutter)
  - `desktop` — Desktop app (Electron / Tauri)
  - `api` — Backend API only

Proceed to Step 4.

### Mode 2: From spec
Ask the user for one or more file paths:
> Please provide file paths to any of the following:
> - Requirements document or spec sheet
> - Design document or wireframes description
> - Existing idea_analysis.json or requirements_spec.md from a previous run
> - Meeting notes or feature list
> - Any other document describing what the app should do

Read each provided file. Extract:
- App purpose and target users
- Feature list and use cases
- Platform targets (web / mobile / desktop / api)
- Non-functional requirements (performance, security, scale)
- Any technical constraints or preferences mentioned
- Any UI/UX notes

Use this as the pre-filled input to the orchestrator instead of the user's verbal description.
Tell the orchestrator:

```
PROJECT_NAME: <project-name>
PLATFORMS: <extracted or confirmed platforms>
IDEA: <synthesized description from the spec documents>
SPEC_FILES: <list of files read>
```

Also ask the user to confirm or correct the extracted platforms before proceeding.

Proceed to Step 4.

### Mode 3: Resume
Ask the user for the path to the existing project workspace.
Read `_orchestrator/pipeline_state.yaml` to determine:
- Which phase was completed last
- Which phases remain
- Any unresolved issues

Report the current state to the user:
> Project: <name>
> Last completed phase: <phase>
> Status: <status>
> Next step: <what the orchestrator should do next>

Ask the user to confirm before resuming.

Do NOT recreate the workspace directory structure — just copy the `.claude/` agents if they are missing.
Launch the orchestrator with the current pipeline state:

```
PROJECT_NAME: <project-name>
RESUME: true
PIPELINE_STATE: <path to pipeline_state.yaml>
```

Skip Steps 4–8 and go directly to Step 9.

---

## Step 4 — Confirm project location

Default: `~/projects/<project-name>/`
Show the full path and ask the user to confirm before creating anything.

---

## Step 5 — Check prerequisites

```bash
gh auth status 2>/dev/null && echo "gh: OK" || echo "gh: not logged in"
node --version 2>/dev/null || echo "node: not found"
pnpm --version 2>/dev/null || echo "pnpm: not found"
```

Warn the user about missing tools but proceed unless the user says to stop.

---

## Step 6 — Create workspace

```bash
mkdir -p ~/projects/<project-name>/{global,_orchestrator}
mkdir -p ~/projects/<project-name>/global/user_feedback
```

Copy agents:
- Copy `home_lab/.claude/agents/app-dev/` → `~/projects/<project-name>/.claude/agents/`
- Do NOT copy `new-app.md` or `new-research.md` commands

Write `CLAUDE.md`:

```markdown
# アプリ自動生成システム

マルチエージェントオーケストレーションによるアプリ自動生成システム。

## 使い方

ユーザーがアプリのアイデアを話したら、まず以下の情報を収集し、`orchestrator` エージェントを起動する。

収集する情報:
1. **プロジェクト名** — 英数字とハイフンのみ
2. **アプリのアイデア** — 何を作りたいかの自然言語説明
3. **対象プラットフォーム** — `web` / `mobile` / `desktop` / `api`（複数選択可）

## 前提条件

- `gh` CLI がログイン済みであること（GitHub連携のため）
- `~/design_library/` にデザイン参考画像・テーマを事前配置しておくと品質が向上する
```

---

## Step 7 — Write global files

Write `global/project_config.yaml`:
```yaml
project_name: <project-name>
platforms: [<selected platforms>]
created_at: <YYYY-MM-DD>
startup_mode: scratch | from_spec | resume
```

Write `global/user_idea.md`:
- **Mode 1**: The app idea as described by the user.
- **Mode 2**: The synthesized description extracted from the spec files.
  Add a `## Source files` section listing the files read.

---

## Step 8 — Initialize git and GitHub

```bash
cd ~/projects/<project-name>
git init
gh repo create <project-name> --private --source=. --push
```

If `gh` is not logged in, skip GitHub and note it.

---

## Step 9 — Launch orchestrator

Invoke the `orchestrator` subagent:

**Mode 1 / Mode 2:**
```
PROJECT_NAME: <project-name>
PLATFORMS: <platforms>
IDEA: <app idea or synthesized spec>
```

**Mode 3 (resume):**
```
PROJECT_NAME: <project-name>
RESUME: true
PIPELINE_STATE: <path>
```

---

## Step 10 — Report

Return:
- Project location
- GitHub repo URL (if created)
- Mode used (scratch / from spec / resume)
- For mode 2: what was extracted from the spec and what was not found
- For mode 3: the phase being resumed and what comes next
- Platforms being built
- That the orchestrator has started and will pause at the next approval gate
