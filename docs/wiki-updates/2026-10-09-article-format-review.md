# Article format review · 2026-10-09

Result: **needs_changes for article-format acceptance**. The owner reported that
the three published pages have plain prose, no meaningful paragraph/section
structure or contextual concept links, and graph navigation instead of the
expected article transitions. The import succeeded, but the requested article
experience was not delivered. This is a product assessment, not a new coordinator
state or a replacement for historical source reviews and receipts.

## Where requirements and implementation diverged

The original Daychi handoff required a short introduction, usually 3–6 meaningful
sections, internal concept links in context, compact evidence/time navigation and
useful direct related-article transitions through reviewed concepts. Those
requirements were present in the saved brief; they were not lost from context.
The initial preparation scope excluded server/reader changes and production
imports. The later owner request authorized publication, but the existing summary
format was incorrectly treated as a sufficient way to deliver those articles.

| Stage | Observed result | Gap |
|---|---|---|
| Private editorial articles | 4/4/5 sections; 10/9/10 paragraphs including introductions | Reading structure exists in preparation |
| Private concept mentions | Six concept/link references; Markdown glossary links only in end lists | No reviewed placement of clickable concepts in their paragraphs |
| Legacy publication exporter | `article_text_v1` concatenates every claim text with one space | All section headings and paragraph boundaries disappear |
| Imported content-v1 records | `summary` lengths 2864/2568/2998; zero newlines; retained old quote points | No body, inline mentions, new evidence or related semantic paths |
| Production reader | Escaped summary rendered inside one `<p>` | Cannot restore absent sections or render concept links from that string |
| Production “Связи” | Catalog/series neighbors; section/subtopic cards open graph routes; graph buttons | Not the reviewed article-to-article recommendations |
| Contract work | Separate optional extension proposal, no implementation | Documenting the extension did not add provider or reader support |
| Checks and reviews | Source fidelity, unchanged claim prose, exact v1 DTO/replay/access checks | No end-to-end acceptance of structure, contextual links or destinations |

The independent reviews remain evidence for their stated source/projection scope.
They do not establish that the article-format requirements passed. Authorized
production browser QA was left open after the explicitly permitted QA invitation
reported revoked. Missing browser QA is a separate limitation; the formatting
failure is already visible in the exporter, payload and live public reader code.

## Evidence and limits

- Private packet and original readable files remain under
  `data/wiki-article-pilot/2026-10-09/`, outside Git. Compare `editorial.json`, the
  three Markdown files, `publication-batch.json`, `publication-after.json` and
  `publication-qa.json`. Original source/review hashes were not altered.
- The saved original brief is Daychi
  `docs/handoffs/wiki-2026-10-09/knowledge-pilot.txt`. Its requested reading output
  differs from the allowed initial preparation-only runtime scope.
- Exporter and synthetic checks are
  [wiki_article_pilot.py](../../scripts/wiki_article_pilot.py) and
  [test_wiki_article_pilot.py](../../tests/test_wiki_article_pilot.py). The projection
  test explicitly expects a single space between paragraphs. These tests validate
  the implemented legacy export, not the user's article experience.
- Read-only live check at approximately **2026-10-09 19:28 UTC** fetched `/wiki`
  and its `/wiki-graph-assets/graph.js`. Asset SHA-256:
  `22d7fcde82a0709bf853db9cdc1a2adcd3b5c9757c06f881941e261a13a50a45`.
  It renders summary in one escaped paragraph and routes catalog section/subtopic
  cards to graph. This checks shipped code; it is not a screenshot-based authorized
  browser audit. The local newer UI candidate is separate from this live asset.
- The prepared semantic recommendations contain one supported article pair,
  represented in both directions, and no supported transition for the third
  article. Do not invent extra links to reach a quota.

## Concrete repair handoff

1. **Knowledge preparation:** retain the existing sections/claim paragraphs;
   bind intended concept mentions to exact paragraph text and placement; reconcile
   proposed concepts with canonical pages and aliases. Review the final readable
   articles, contextual links, full concept pages and related reasons independently.
2. **Daychi provider:** agree and implement the compatible optional structured
   body/link/evidence representation. Preserve active v1 and access behavior;
   publish a coherent reviewed article/concept/link revision. The private audit
   packet must not become a reader DTO. Follow the existing boundary coordination
   and publication gates for actual implementation.
3. **Daychi reader:** display the introduction, section headings and separate
   paragraphs, restrained concept emphasis and contextual concept-page links.
   Related entries open the target article with the reviewed reason. Keep graph
   exploration as a separate action. Adding Markdown characters to an escaped
   summary or changing CSS cannot deliver the missing link/body objects.
4. **Acceptance of the same three articles:** compare final rendered pages with
   the intended readable structure; exercise concept and related-article links,
   evidence/time navigation, contents, back/return and private access. Retain
   expected/runtime captures. API equality and source review are necessary checks
   within their scope; they cannot replace this reader acceptance.

The preparer/coordinator's error was substituting prose preservation and wire
compatibility for preservation of the agreed reading output. The algorithm now
makes this distinction explicit. The existing three-text publication is recorded
accurately; a corrected structured publication and runtime implementation remain
outstanding. Complete this repair before expanding the experiment.
