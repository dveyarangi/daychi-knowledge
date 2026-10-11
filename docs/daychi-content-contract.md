# Daychi content import · v1

Producer: `daychi-knowledge`. Consumer and wire-model authority: Daychi backend.
No payload envelope, endpoint, material ID, revision or authentication change.

| Package | Existing owner operation | Client model |
|---|---|---|
| Source-bound summaries | POST `/api/admin/wiki/content` | `daychi_contracts.content.Batch` |
| Reviewed themes / glossary pilot | POST `/api/admin/wiki/semantic-content` | `daychi_contracts.semantics.SemanticBatch` |

The glossary remains a separately gated pilot; moving its preparation tools does
not enable its server feature or publish its pages. Server deployment / flags must
be verified before any authorized import. The content API remains in Daychi.

Existing login/logout, owner session, Origin and CSRF protection are retained.
Import commands validate locally by default; `--apply --password-file` is restricted
to the coordinator after review and explicit batch publication authorization.

Keep stable resource/concept IDs, expected titles, source revisions, transcript and
subtitles hashes, exact quote text/timecodes, batch ID and `source_checked_draft`.
Same-batch replay is idempotent. Changed content requires the next revision and a
new batch. The server checks the current catalog/source state, conflicts and exact
evidence; passing producer validation alone does not establish import acceptance.
Material IDs used by bookmarks/URLs must not be regenerated during migration.

`contracts/content-v1.schema.json` and `contracts/semantics-v1.schema.json`
describe the payloads. `daychi_contracts/` preserves the existing Pydantic validators,
including independent review and exact semantic evidence references. It contains
no server, catalog, storage or credentials. `contracts/source.json` identifies the
model snapshot. Run `python scripts/sync_daychi_contracts.py --daychi /path/to/daychi`
to verify it against the executable definitions. Refresh a
snapshot only after an agreed compatible change, preserving the validators and updating both schemas. Semantic verification requires a Daychi
checkout containing that pilot; main without it verifies only the available content
contract and reports the absent pilot. Use `--require-semantics` when reviewing it.

Synthetic regression tests cover source binding, quarantine, exact evidence,
independent review, protected proofs and unchanged package generation.

## Full-source article experiment · 2026-10-09

The separate [editorial pilot](wiki-article-pilot-protocol.md) prepares private
articles, concept patches and full-source evidence jointly. It does not replace
this active protocol or authorize imports by itself. See the
[compatible extension proposal](daychi-article-contract-proposal.md); its structured
article/evidence format is not supported by content/semantics v1. After separate
owner authorization, three short article texts were published as prose-only v1
summary projections at revision 2. Existing points and identities were preserved.
The [publication record](wiki-updates/2026-10-09-article-pilot.md) distinguishes this
active-contract update from the proposed extension.
The owner subsequently rejected the article format; see the
[diagnosis and acceptance requirements](wiki-updates/2026-10-09-article-format-review.md).
Legacy summary export is not a structured article publication path.


## Coexisting structured articles · 2026-10-11

The [article contract](daychi-article-contract.md) adds its own strict owner batch,
source-pinned claims/evidence, inline mention ranges and reviewed direct article
paths. It preserves content/semantics v1. `daychi_contracts/articles.py` and
`contracts/articles-v1.schema.json` mirror the provider executable definitions;
`tests/fixtures/article-batch-v1.json` is the shared synthetic case.
