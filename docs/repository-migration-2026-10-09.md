# Knowledge pipeline moved · 2026-10-09

The operator approved separate product and knowledge repositories.
Continue source indexing, transcription, editorial batches, review, registry and
work-plan updates in [daychi-knowledge](https://github.com/sleontenko/daychi-knowledge).
Local checkout: `/Users/mac-mini-server/projects/daychi-knowledge`.
Read that repository's AGENTS.md and README.md before resuming an old assignment.
Keep current stable IDs, batch assignments and manual register edits.

Daychi retains the app, website, wiki UI, server, authorization and runtime/import
endpoints. Existing content v1 JSON imports are retained; no deployment or new
production import is authorized by this repository migration.

Existing pipeline branches preserve historical work. They are not the location
for new pipeline changes. Transfer any unfinished pipeline edits to a dedicated
branch in daychi-knowledge; application/server changes still target Daychi.
Private data never enters either Git repository. On the coordinator's Mac Mini,
old pipeline data paths resolve through compatibility symlinks to the new local
data directory, preserving absolute paths recorded in proofs and assignments.

The initial knowledge snapshot includes current workspace versions as listed in
`migration/source-manifest.json`; Daychi's unrelated uncommitted work is preserved.

## Scope

Transferred: `scripts/wiki_*.py`, archive ingestion, ASR requirements and their
pipeline tests; working editorial protocols, team register instructions, work
plan, content status, batch journals and enrichment QA records.
Runtime/API tests and wiki UI/design QA stay in Daychi. No content imports or
deployments were run. Historical files retain their original factual statements.
Local data directories: wiki-workspace, wiki-pipeline, wiki-enrichment, wiki-audit
and nikita-archive. Runtime access databases, releases, credentials and UI captures
stay in the Daychi workspace. Git tracks neither set of private data.

## Existing chats

«Продолжи пайплайн вики» and «Подготовить контент вики» must resume from this
checkout. The original Daychi checkout also has forwarding instructions and
protocol links for sessions still starting in its old cwd.

## Executed checks

- Knowledge pipeline: 76 tests passed; all argparse CLI help checks passed.
- Daychi migration branch: 110 backend tests passed.
- Import model definitions match the coordinator workspace for both v1 packages.
- Main verifies content-v1; the semantic pilot is absent there and remains separate.
- Relative Markdown links resolve in both prepared repositories.
- Staged repository checks found no recognized private artifacts or credentials.
- App/wiki UI files and deployment configuration are untouched by this migration.
