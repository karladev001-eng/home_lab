Start or resume the research session.

Use the `research-state-loader` subagent.

Goal:
- Load the current research state from files.
- Create or update `research/session-brief.md`.
- Return a compact summary so the main Claude session can continue from where the project left off.

The loader should inspect:
- research/state.md
- research/session-brief.md
- research/questions.md
- research/hypotheses.md
- research/decisions.md
- research/next-actions.md
- research/literature/paper-cards/
- research/literature/search-reports/
- research/experiments/registry.md
- research/experiments/results/
- research/presentation/
- research/slides/
- outputs/

Do not paste long file contents.
Do not summarize every paper or every experiment unless needed.
Focus on:
- current research question
- current hypothesis
- proposed method
- latest results
- unresolved issues
- next actions

After the subagent returns, read `research/session-brief.md` and continue as the main research partner.

Return:
1. One-paragraph project status
2. Current focus
3. Top 3 next actions
4. Any blockers
5. Ask the user which direction they want to continue
