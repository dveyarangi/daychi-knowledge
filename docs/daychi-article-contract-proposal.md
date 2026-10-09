# Daychi full-source articles · compatible extension proposal

Status: proposal from the 2026-10-09 private knowledge pilot. No server/reader
implementation, schema refresh or feature activation occurred. The three article
texts were subsequently published through the active v1 summary contract after
owner authorization, without truncation; this does not implement the extension.
Owner feedback rejected that prose-only reader result. The proposed extension
and its reader acceptance below are required to deliver the agreed article shape.
The [active v1 contract](daychi-content-contract.md) remains unchanged and Daychi
remains provider and executable-model authority. Knowledge only prepares drafts.

## Why a separate extension

Content v1 provides a summary (maximum 3000 characters) and published points;
it has no article body. Semantic v1 has bounded claims/links addressing those
published points. Full-source pilot evidence is neither a new published point
nor a valid semantic-v1 point_index. Truncating an article into summary or sending
extra fields to a strict v1 model would misrepresent the reviewed result.

The trial's full claim prose happens to fit v1 at 2864/2568/2998 characters. Its
[legacy summary export](wiki-article-pilot-protocol.md#legacy-summary-export-used-in-the-trial)
preserves all 29 reviewed paragraphs' texts and nine existing quote points but
omits section/paragraph layout. Full-source evidence, glossary and semantic paths
remain private proposals. Preserving prose is not preserving an article. This
export must not be used as a substitute for structured article publication.
The [format review](wiki-updates/2026-10-09-article-format-review.md) also identifies
missing inline mention placement in the private preparation format.

Propose a coexisting optional article/semantic extension with its own negotiated
version. Keep current endpoints, resource/material/concept IDs, revisions,
authentication, access controls and default client responses. Old clients continue
to receive v1 summary/points and ordinary graph; capable clients explicitly opt
into the new body/evidence layer. Reuse provider-owned authentication, owner
session, Origin/CSRF and authorized-reader access. The private editorial JSON is
not the proposed wire DTO and exposes audit paths/hashes absent from reader DTOs.

## Shape to agree with Daychi

| Object | Proposed semantics |
|---|---|
| Article | Stable material/resource identity; independent article revision; expected catalog title and source/content revision; introduction; ordered sections and claim IDs; reviewed draft status |
| Claim | Stable identity, reader text and exact evidence references; no unsupported normative definition or implicit medical validation |
| Inline mention | Exact displayed text and placement within a claim paragraph, resolved canonical concept/link identity; reviewed in context, not guessed by keyword matching |
| Evidence | Stable source/revision identity, exact quote, bounded timestamps and source digest in owner package; reader receives allowed quote/time navigation only |
| Concept | Stable canonical ID/type, checked aliases, contextual claims and all retained/new source links; proposals require canonical reconciliation before assignment |
| Material→concept link | Stable identity, explains/practices/discusses, rationale, reviewed evidence; same link drives article mention, graph and backlink |
| Related-material path | Derived projection through two valid edges; reason and path references; no stored direct claim or inferred series order |
| Owner audit | Batch ID, immutable dependencies, final output/review hashes and reviewer proof; never reader filesystem paths or credentials |

Use a bounded paragraph/section object format rather than arbitrary HTML or
untrusted executable markup. Exact request envelope, operation path, size limits,
evidence limits, revision allocation and reader capability selector remain
**unsettled**, owned by Daychi and coordinated before implementation. Do not use
invented endpoint names as established APIs. The editorial size guide is not a
wire byte limit.

## Minimum observable reader result

The agreed output needs a short introduction, ordered concrete section headings,
separate meaningful paragraphs and restrained emphasis on concepts in context.
Concept mentions must be clickable within those paragraphs and open the canonical
concept page. A standalone glossary list may supplement, but cannot replace,
those mentions. A bounded inline representation must preserve the exact paragraph
text when combined; its precise encoding remains a provider design decision.

Related materials must be direct article links with a concrete reason through
reviewed common concepts. Preserve the target material ID and supporting link IDs;
do not resolve an article target to the graph or invent series chronology. Keep
graph exploration as a separate action using the same reviewed identities. The
pilot supports one pair of related articles in both directions; its third article
has no supported path. Missing supported paths and added unsupported paths both
fail acceptance. Canonical concept reconciliation is still outstanding.

Conformance must cover the whole published body/link DTO and real reader route:
heading/paragraph order, contextual link location and destination, related article
destination/reason, compact source/time links, coherent revisions, back/return,
authorized access and legacy fallback. Exact v1 DTO equality proves only v1
delivery. A UI styling deployment alone does not implement these capabilities.

## Common behavior and migration checks to agree

- Validate the whole extension batch before writing. Conflict on source/catalog
  revision, alias identity or expected existing page revision rejects the update;
  no partial graph/body publication. Reconcile concept patches into whole pages
  preserving prior links and require full merged-page review.
- Exact same accepted batch returns the same receipt; unchanged content and
  dependencies do not increment revisions or move “recently updated”. A changed
  body, evidence, source dependency or rationale needs a new reviewed revision.
- Changed/rebound/deleted source invalidates dependent article claims, concept
  claims and links; reader, graph, backlinks and related paths must agree on which
  reviewed revision is visible. The currently accepted semantic-v1 whole-page
  hiding behavior continues for v1; per-claim hiding is an unresolved extension
  decision, not assumed here.
- Anonymous and unauthorized responses preserve existing private-content rules,
  including quotes, graph edges, backlinks and derived paths. No audit fields in
  reader DTO; opt-in cannot broaden access.
- Old native/web clients pass unchanged v1 conformance. New reader handles missing
  extension data using the existing summary; network failure preserves coherent
  last-good state rather than mixed body/graph versions. Do not imply missing
  extension means an empty source or accepted article.

Before implementation: agree an immutable provider-authored shape and common
conformance cases with Daychi. For introduction/migration of an actual coexisting
version, open the Workshop migration-coordination issue under `project:workshop`
and follow [contract evolution](https://github.com/dveyarangi/xuanxue-workshop/blob/HEAD/docs/agent-contract.md#contract-evolution).
This proposal alone neither introduces a wire version nor requests a migration.
Only retire v1 after all known consumers confirm transition. No Cabinet API or
ownership migration is part of this extension.
