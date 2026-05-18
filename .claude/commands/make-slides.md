Create slides only when the user specifically needs slide output.

Prefer `research/presentation/index.html` as the primary presentation artifact when it exists.
Use the HTML presentation as the source for condensation unless the user asks to build slides directly from research files.

Step 0:
If `research/slides/templates/style-guide.md` does not exist, note that no style guide is available and proceed with general design principles.

Step 1:
Use the `slide-deck-builder` subagent.

Tell it:
- The intended audience (from the user's message, or ask if not specified)
- The presentation length (from the user's message, or default to 15 minutes)
- Any specific sections or experiments to include

The deck must:
- Use Marp format (`marp: true` front matter)
- Condense the already-reviewed HTML presentation if available
- Follow `research/slides/templates/style-guide.md` if it exists
- Read actual results from `research/experiments/results/` and `research/experiments/registry.md`
- Not fabricate figures, metrics, or citations

Generate:
- `research/slides/latest-deck.md`
- `research/slides/deck-outline.md`
- `research/slides/latest-deck.pdf` (if Marp CLI is available)

Step 2:
Use the `slide-consistency-reviewer` subagent.

Check whether the content matches:
- research/state.md
- research/hypotheses.md
- research/experiments/registry.md
- research/experiments/results/
- research/literature/paper-cards/

Step 3:
Use the `slide-style-reviewer` subagent.

Check whether the Marp deck follows:
- research/slides/templates/style-guide.md
- General Marp presentation design principles

Step 4:
Return only:
- generated files
- content consistency verdict (PASS / NEEDS_MINOR_FIXES / NEEDS_MAJOR_FIXES)
- style compliance verdict (PASS / NEEDS_MINOR_FIXES / NEEDS_MAJOR_FIXES)
- critical content issues (if any)
- critical style issues (if any)
- TODOs (missing figures, unverified claims)
- whether the deck is safe to present
- what was condensed from the HTML presentation
