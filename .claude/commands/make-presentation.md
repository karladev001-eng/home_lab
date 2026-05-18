Create or update a lightweight HTML research presentation.

Step 0:
If `research/presentation/templates/style-guide.md` does not exist, note that no style guide is available and proceed with general design principles.

Step 1:
Use the `html-presentation-builder` subagent.

Tell it:
- The intended audience
- The purpose of the page
- Any specific sections or experiments to include

The presentation must:
- Generate lightweight reviewable HTML first
- Follow `research/presentation/templates/style-guide.md` if it exists
- Read actual results from `research/experiments/results/` and `research/experiments/registry.md`
- Not fabricate figures, metrics, or citations

Generate:
- `research/presentation/index.html`
- `research/presentation/styles.css`
- `research/presentation/outline.md`

Step 2:
Use the `html-consistency-reviewer` subagent.

Step 3:
Use the `html-style-reviewer` subagent.

Step 4:
Return only:
- generated files
- content consistency verdict
- style compliance verdict
- critical content issues
- critical style issues
- TODOs
- whether the page is safe to share
- whether slides are recommended as a follow-up export
