# Full-source articles, glossary and graph · editorial pilot 0.1

This protocol is a **private preparation experiment**, authorized on 2026-10-09.
It does not replace the published summary process or content/semantics v1.
The [coordinator workflow](collaboration-workflow.md) still owns reservations,
independent review and the single final acceptor. On 2026-10-09 the owner then
authorized publication of the three reviewed article texts. Their lossless v1
projection is published; glossary/graph proposals remain private. Private outputs
stay outside Git. See the [publication record](wiki-updates/2026-10-09-article-pilot.md).

## Assignment and inputs

Use a fresh reconciled queue, preserving XLSX manual assignments and SQLite
locks. Reserve preparation work in the existing coordinator ledger before
editing. Mark this research subtype nonpublication; do not label it a ready
summary/semantic import or promote published summaries into available work.
The three-source trial used one `prepare` assignment and explicitly reserved
its three sources and four existing concept proposal targets. This use of prepare
is for a private report, not ordinary ASR readiness intake. A new concept name/ID
is only a proposal until the coordinator reconciles canonical IDs and current
aliases and reserves it. Historical unpublished semantic pages are reference
material, not proof of current reader state.

Pin material/resource ID, catalog binding, source/content revision, provenance,
language, full TXT/SRT/segment/info hashes and quarantine origin/hash. Reject
ambiguous binding, changed source or active competing reservation. No new ASR is
needed when the existing checked text is fit for this preparation. Reading is
text review; do not claim listening, gesture verification or teacher approval.

## One source, three coordinated outputs

1. Read the complete source before consulting its old summary. Read timecoded
   normalized segments, verify equivalence with the complete TXT and preserve
   SRT/provenance hashes. Restore any tool-output truncation before declaring full
   reading. A prior summary is a comparison baseline, never the extraction input.
2. Map meaningful explanation, question, example, comparison, correction and
   conclusion windows. Keep context around qualifications and apparent conflicts.
   Remove repetitions and administrative remarks from the article. Whole-source
   reading includes quarantined text for context; evidence must exclude it.
3. Identify the actual claim and its scope. A contextual explanation stays
   contextual. Do not reconstruct demonstrations from “this way”, infer medical
   efficacy, add uncertain terminology, or universalize the teacher's examples.
4. Reconcile candidates with canonical concepts and checked aliases: reuse,
   supplement, separate sense, new contextual page, or defer. Similar spelling
   does not prove identity. One substantive source can support a contextual draft;
   more sources expand it without flattening disagreements. No page quota.
5. Write a 2–4 sentence introduction and usually 3–6 concrete sections. The
   300–700 word range is guidance, not a minimum. Give each claim paragraph exact
   evidence IDs pointing to contiguous source segments, quote bytes, both
   timestamps, source revision and hashes. A paragraph can contain several
   propositions; paragraph counts must not be advertised as atomic accuracy.
6. Propose material→concept `explains`, `practices` or `discusses` links with
   semantic rationale and evidence. Article mentions, graph edges and backlinks
   refer to the same IDs and link objects. Similarity/search only propose candidates.
7. Select useful related-material paths through two reviewed edges to the same
   concept, with a specific explanation/comparison reason. Usually 2–4 when
   supported; zero or one is valid. Render them as derived paths, never new direct
   facts or chronology. “Next lesson” requires independently established series
   order. A shared category alone is insufficient.
8. Another reviewer reads the complete sources and checks final article bytes,
   every claim paragraph (all its propositions), glossary patch, link rationale,
   derived path, exclusions and omissions. Decision is pass/needs_changes/blocked.
   Bind review to the editorial hash, readable-artifact manifest and source proof.
   Editing any reviewed content requires a new review. The designated owner then
   makes final acceptance; review pass alone never permits an import.

For supplements, preserve the entire previous concept page and its links.
The pilot returns a patch proposal, not a replacement payload. A later merged
page needs independent review of all retained and added claims/links against
all full sources; current aliases and revisions must be reconciled then.

## Local format and checks

`daychi-editorial-article-pilot/0.1` explicitly has `wire_contract: false`.
Private packet: assignment, source manifest, editorial JSON, readable articles,
glossary, comparison, render manifest, editor reading proof, independent review
and reviewer reading proof. JSON keeps articles/sections/claim IDs, shared exact
evidence, concept proposals, material-concept links and derived related paths.
It is not `Batch` or `SemanticBatch` and must never be sent to their endpoints.

```sh
.venv/bin/python -m scripts.wiki_article_pilot --root "$PRIVATE_PILOT_ROOT"
.venv/bin/python -m scripts.wiki_article_pilot --root "$PRIVATE_PILOT_ROOT" --require-review
.venv/bin/python -m pytest -q
.venv/bin/python scripts/check_repository.py
```

The validator checks immutable dependencies, exact evidence/timing/quarantine,
reserved source identity, existing concept reference, article placement, shared
link IDs, supported paths and final review coverage. It cannot verify meaning or
prove human/agent reading. Synthetic tests deliberately reject stale sources,
changed reviewed articles, modified readable files, missing evidence, self/partial
review, quarantine use, duplicate concepts and unsupported paths.

## Publishing a short article through the active contract

For this three-source trial all reviewed claim texts fit content-v1's 3000-character
summary bound: 2864, 2568 and 2998 characters. `article_text_v1` orders introduction
and section claim IDs, requires every claim exactly once, joins their unchanged
texts with one space and fails on overflow. It never truncates or paraphrases.
The current reader receives one prose body. Section headings and paragraph layout
remain in the private structured artifact until the article extension is agreed.

This is a separate `summary` publication assignment, explicitly reconciled against
live revision 1 and reserved as revision 2. Preserve title/resource/material IDs,
source hashes, status and previously published points. Independently review the
final modeled batch hash, projection order, baseline DTO and retained quote
windows. A previous complete-source read may be reused by the same reviewer only
after fresh file/proof/hash identity checks, with that reuse stated explicitly.
Owner acceptance and publication authorization are recorded for the exact batch.

Use the existing gated importer, save its receipt and verify exact authorized DTO,
unchanged catalog fields, anonymous redaction, replay and recent-update behavior.
Merge the facts into the existing registry without replacing assignments or source
periods. Record browser QA separately. A successful import and API checks do not
become `verified` while required authorized UI checks remain open.

The 62 full-source evidence windows, concept patches and new graph links do not
become v1 published points or semantic payloads through this projection. Longer
articles need the negotiated extension. An identical rerun reuses the same batch
and revision; allocate another revision only for a real content/dependency change.

## Incremental processing

Keep material/concept IDs and claim/evidence IDs stable for unchanged content.
Revisions change for actual content/dependency changes, not processing dates,
checkout paths, a new assignment or a repeated identical run. The local revision
fingerprint excludes those audit fields, while including source hashes and
quarantine. Production revision allocation stays with the owning provider.

Track source-revision/hash→evidence→claims/links→articles/concepts and derived
paths. On source change or quarantine correction, invalidate dependent review,
then regenerate and review affected assertions and rationale. Do not silently
retarget old offsets. Deletion/rebinding must remove stale navigation as well.
Changing a rendered article invalidates its review, even when JSON was untouched.
Persist both editorial and readable-file hashes. Future serializers should
produce the readable body deterministically from the same claim objects.

## Trial measurement and next scope

Measure final reviewed paragraphs/total paragraphs, accepted rationale/total
links, useful unique related pairs separately from directed paths, existing/new/
deferred concepts, possible duplicate senses, and end-to-end wall time. Record
reading/review overlaps: concurrent agent time is not additive elapsed time.
Do not replace unavailable tokens/cost/accuracy with estimates.

Next scope: six already checked sources, two for each tested source style,
including one repeated concept and one conflicting sense. Reserve actual sources
from a fresh queue. Recheck canonical IDs/aliases; test one source revision change
and one identical rerun; retain all disagreement and omission evidence. Measure
reader usefulness with owner feedback before scaling. This is a proposal, not a
new assignment or permission to publish.
