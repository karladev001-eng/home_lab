Sync the current research session back to persistent research files.

Use the main conversation context and relevant files to update:

- research/state.md (if the research direction or hypothesis changed)
- research/session-brief.md (always update with today's progress)
- research/decisions.md (append dated entries for any decisions made)
- research/next-actions.md (replace with current next actions)
- research/experiments/registry.md (if experiments changed)
- research/presentation/ (if presentation-related decisions changed)
- research/slides/ (if slide-related decisions changed)

If the project is inside a git repository, also do lightweight version control for the session:

- Check `git status --short`
- Stage only files relevant to the current research session
- Create a commit when there are meaningful changes
- If a remote named `origin` exists, report whether the work was pushed or is ready to push

Do not create empty commits.
Do not stage unrelated large outputs unless the user explicitly wants them versioned.
Prefer versioning research state, code, configs, registries, and presentation artifacts.

Capture:
- what changed today
- new decisions made (with rationale)
- new evidence found
- failed attempts (these are useful — record them)
- unresolved questions
- next actions

Format for dated entries in decisions.md:
```markdown
## YYYY-MM-DD
### Decision
...
### Reason
...
### Alternatives considered
...
### Consequences
...
```

Do not overwrite important prior context.
Append dated entries where appropriate.
Do not truncate next-actions.md — replace it with the current state.

Return:
- files updated (with a one-line description of what changed)
- new decisions recorded
- next actions saved
- git commit created or skipped (with reason)
- git push status (pushed / skipped / no remote)
- any information that could not be captured (missing context)
