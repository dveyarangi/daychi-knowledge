# Structured article contract · coexisting version 1

Daychi owns executable models, storage and reader. Knowledge owns editorial
preparation, full-source evidence validation, independent review and the gated
owner importer. [Workshop #9](https://github.com/dveyarangi/xuanxue-workshop/issues/9)
coordinates this compatible addition. Content/semantics v1 and old consumers remain.
Provider implementation: [Daychi PR #9](https://github.com/sleontenko/daychi/pull/9).
Immutable executable [provider revision151cbdf](https://github.com/sleontenko/daychi/tree/151cbdf73560cc94d1019873326d5efab721e1ae)
contains the model, schema and common conformance packet. Deployment and publication are tracked in
[the repair record](wiki-updates/2026-10-11-structured-article-repair.md).

`daychi_contracts/articles.py` mirrors `practice_api/wiki_article_models.py` byte for
byte; `contracts/articles-v1.schema.json` is the generated owner schema. Both
projects carry `tests/fixtures/article-batch-v1.json`. Verify against the provider:

```sh
python -m scripts.sync_daychi_contracts --daychi /path/to/daychi --require-articles
python -m pytest -q
```

The wire format is `daychi-wiki-articles/1`. Source pins bind stable material/resource
IDs, exact catalog title, current content revision, TXT/SRT hashes. Articles keep
independent revisions, introduction and ordered section/paragraph identities.
Mentions are reviewed Unicode code-point ranges referencing a material→concept
link; JavaScript slices `Array.from(text)`. Concept pages are complete reconciled
pages, preserving retained claims, quotes and links. Related targets require two
reviewed source links through the same concept and a concrete reason. A standalone
list of keywords or a graph route does not replace contextual article navigation.

The server atomically checks pins, identities, aliases and revisions. Replay and
unchanged content preserve object dates/history; source/catalog changes hide the
whole coherent bundle from article, concept, graph and backlink projections.
Corrections/removal of retained facts require a separate correction protocol.
The server cannot verify source meaning or exact quotation solely from hashes.

## Coordinator path

1. Reconcile the current registry/live catalog and all source pins. Check provider
   capability and owner article inventory before issuing a publication assignment.
   Reserve all `yt:<resource>` and `concept:<slug>` targets. Task kind `article`
   contains explicit `object_revisions` for every article and concept page; source
   dependencies without a new body remain reserved but do not get an article revision.
2. Prepare `ArticleDocument` privately. Validate every complete TXT/normalized
   segment source, unchanged SRT/info hashes, contiguous quotation window, exact
   text/time bounds and quarantine. Editor reading proof binds assignment, identity,
   complete source coverage and the final document hash. Prior reading may be reused
   only by its original reader after exact source/proof/hash checks, stated explicitly.
3. A different reviewer reads the complete source and reviews each final paragraph,
   whole merged page, link rationale, inline span and related path. The validator
   checks that individual review coverage matches the exact document, not just totals.
4. Build `ArticleBatch` with mandatory independent review identity/proof hashes.
   Submit that final modeled batch to its publication assignment. Independent final
   packaging review binds the modeled batch hash; preparation review alone is insufficient.
5. The one designated owner accepts that exact hash, then explicitly permits its
   publication. The importer has no acceptance authority. Use existing owner session,
   Origin/CSRF and workflow gates; save the first write receipt before replay.
6. Verify exact authorized DTOs, unchanged source/v1 fields, replay, public recording
   protection, actual authenticated reader/graph navigation and registry preservation.
   Keep publication `imported` until every required QA fact is observed and recorded.

```sh
python -m scripts.wiki_article_validate --root "$WIKI_PRIVATE_PACKET" --review "$WIKI_PRIVATE_REVIEW"
python -m scripts.wiki_article_import --batch "$WIKI_RESULT"
python -m scripts.wiki_article_import --batch "$WIKI_RESULT" --apply \
  --password-file "$WIKI_OWNER_PASSWORD_FILE" --workflow-db "$WIKI_WORKFLOW_DB" \
  --assignment "$WIKI_ASSIGNMENT" --receipt "$WIKI_RECEIPT"
```

No source files, registry, coordinator database, proofs, receipts or credentials
belong in Git. Text review is not listening or teacher approval.

## Reader and access contract

Existing authorized `/api/wiki/articles/materials/{id}` and `/concepts/{slug}`
expose ordered paragraphs, evidence times and contextual concept/direct article
navigation. Graph/recent opt in with `articles=1`; disabled/absent objects return404
and use the legacy summary. Other errors show retry and preserve a coherent last-good
article. Public equivalents obey the existing public flag, omit recording IDs and
use SHA256-derived opaque editorial IDs/references; they retain text, time labels,
material IDs and concept slugs. Public timestamps cannot reconstruct a YouTube URL.
Owner audit/source hashes and local paths are omitted from every reader DTO.

Source fidelity and reader acceptance are separate. Verify actual headings, exact
paragraph order, mentions/destinations, two supported related paths, absence of
unsupported recommendations, compact source/time links, contents, Back, graph return,
query/scroll preservation and failure recovery with accepted reference/runtime pairs.

After the 11 October recording protection, public snapshots fail closed when source
IDs are absent. The coordinator may use its existing owner session through private
`--owner-password-file` for the owner-only `/api/admin/wiki/articles/sources`
inventory. Two equal fresh reads establish stable catalog/source state; the session
is closed afterward. Credentials never enter snapshots or participant assignments.
This does not add a reader token, invite or broader public access.
