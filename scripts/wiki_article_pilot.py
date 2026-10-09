"""Validate private editorial pilot evidence. This is NOT a Daychi wire importer.

Structural validation cannot establish meaning, full reading or acceptance.
Independent review is required separately and must bind the final bytes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(items, key):
    values = [x[key] for x in items]
    require(len(set(values)) == len(values), f'Duplicate {key}')
    return {x[key]: x for x in items}


def article_text_v1(article):
    """Legacy summary export preserving claim prose, not article structure.

    This does not allocate a revision, accept a draft or authorize an import.
    It drops headings, paragraph boundaries, concept mentions and related paths;
    a successful export is not acceptance of a structured article publication.
    Longer articles require the negotiated article contract, never truncation.
    """
    claims = unique(article['claims'], 'claim_id')
    order = article['introduction_claim_ids'] + [cid for section in article['sections']
                                                for cid in section['claim_ids']]
    require(order and len(order) == len(set(order)) and set(order) == set(claims),
            'Unplaced/repeated claims')
    require(all(isinstance(claims[cid]['text'], str) and claims[cid]['text'].strip()
                for cid in order), 'Empty claim text')
    text = ' '.join(claims[cid]['text'] for cid in order)
    require(len(text) <= 3000, 'Article exceeds content-v1 summary limit; do not truncate')
    return text


def revision_digest(value):
    """Canonical semantic bytes: repeated identical processing has the same digest.

Do not include processing times or reviewer events in a content revision.
Array order remains meaningful (article/section/claim/evidence order).
"""
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode()).hexdigest()


def content_revision_digest(document, sources):
    """Exclude assignment, paths, processing/review timestamps from revisions."""
    dependency_inputs = [{
        'resource_id': rid, 'material_id': source['material_id'],
        'source_revision': source['source_revision'],
        'file_hashes': {name: file['sha256'] for name, file in source['files'].items()},
        'forbidden_segment_indexes': source['forbidden_segment_indexes'],
    } for rid, source in sorted(sources.items())]
    content = {key: document.get(key) for key in
               ('format', 'articles', 'evidence', 'concept_proposals', 'links', 'deferred_candidates')}
    return revision_digest({'content': content, 'dependencies': dependency_inputs})


def validate(root, require_review=False):
    root = Path(root)
    document = json.loads((root / 'editorial.json').read_text())
    assignment = json.loads((root / 'assignment.json').read_text())
    require(document['format'] == 'daychi-editorial-article-pilot/0.1' and
            document['wire_contract'] is False, 'Not the private pilot format')
    require(document['assignment_id'] == assignment['assignment_id'], 'Assignment differs')
    require(document['editor'] == assignment['editor'], 'Editor differs')
    require(document['sources_manifest_sha256'] == sha(root / 'source-manifest.json'), 'Manifest changed')
    sources = unique(json.loads((root / 'source-manifest.json').read_text()), 'resource_id')
    reserved = {s['resource_id']: s for s in assignment['pilot_sources']}
    require(set(sources) == set(reserved), 'Sources outside reserved assignment')
    segments = {}
    for rid, source in sources.items():
        for name, file in source['files'].items():
            require(sha(file['path']) == file['sha256'], f'Source changed: {rid}/{name}')
        require(source['files']['source.txt']['sha256'] == reserved[rid]['txt_sha256'] and
                source['files']['source.ru.srt']['sha256'] == reserved[rid]['srt_sha256'] and
                source['files']['segments.json']['sha256'] == reserved[rid]['segments_sha256'] and
                source['files']['source.info.json']['sha256'] == reserved[rid]['info_sha256'],
                'Source differs from reservation')
        require(sha(source['quarantine_origin']) == source['quarantine_origin_sha256'], 'Quarantine origin changed')
        require(source['forbidden_segment_indexes'] == reserved[rid]['forbidden_segment_indexes'], 'Quarantine differs')
        segments[rid] = json.loads(Path(source['files']['segments.json']['path']).read_text())
        require(len(segments[rid]) == source['segment_count'], 'Segment count differs')
        require(Path(source['files']['source.txt']['path']).read_text().split() ==
                ' '.join(s['text'] for s in segments[rid]).split(), 'TXT/segments differ')
    existing = document['existing_concepts_reference']
    require(sha(existing['path']) == existing['sha256'], 'Existing concepts changed')
    existing_pages = unique(json.loads(Path(existing['path']).read_text())['pages'], 'concept_id')
    evidence = unique(document['evidence'], 'evidence_id')
    for ev in evidence.values():
        rid = ev['resource_id']; require(rid in sources, 'Unknown evidence source')
        indexes = ev['segment_indexes']; source = sources[rid]
        require(indexes and indexes == list(range(indexes[0], indexes[-1] + 1)) and
                0 <= indexes[0] <= indexes[-1] < len(segments[rid]), 'Evidence is not a contiguous valid window')
        require(not set(indexes).intersection(source['forbidden_segment_indexes']), 'Quarantined evidence')
        ss = [segments[rid][i] for i in indexes]
        require(ev['quote'] == '\n'.join(s['text'] for s in ss), 'Quote differs')
        require(ev['start_seconds'] == min(s['start_seconds'] for s in ss) and
                ev['end_seconds'] == max(s['end_seconds'] for s in ss), 'Timecodes differ')
        require(ev['source_revision'] == source['source_revision'] and
                ev['segments_sha256'] == source['files']['segments.json']['sha256'], 'Stale evidence')
    def refs(value, rid=None):
        ids = value['evidence_ids']
        require(ids and len(set(ids)) == len(ids) and all(i in evidence for i in ids), 'Missing/duplicate evidence')
        if rid:
            require(all(evidence[i]['resource_id'] == rid for i in ids), 'Evidence source differs')
    concepts = unique(document['concept_proposals'], 'concept_id')
    for c in concepts.values():
        refs(c)
        require(c['kind'] in ('term', 'topic') and c['scope'] == 'contextual_patch_only', 'Invalid concept scope')
        if c['decision'] == 'new_page':
            require(c['concept_id'] not in existing_pages and c['base_revision'] is None, 'Duplicate new concept')
        else:
            require(c['decision'] in ('reuse', 'supplement') and c['concept_id'] in existing_pages, 'Unreconciled concept')
            previous = existing_pages[c['concept_id']]
            require(c['base_revision'] == previous['revision'] and c['kind'] == previous['kind'] and
                    c['merge_requires_full_existing_page_review'] is True, 'Replacement/revision requires merged-page review')
        # This pilot adds no aliases; their future introduction requires explicit reconciliation.
        require(c['aliases'] == [], 'Pilot aliases not reconciled')
    links = unique(document['links'], 'link_id')
    for link in links.values():
        rid = link['resource_id']; refs(link, rid)
        require(link['concept_id'] in concepts and rid in sources and
                link['material_id'] == sources[rid]['material_id'], 'Broken link identity')
        require(link['relation'] in ('explains', 'practices', 'discusses') and link['rationale'].strip(), 'Unsupported relation')
    articles = unique(document['articles'], 'resource_id')
    require(set(articles) == set(sources), 'Article coverage differs')
    claims_count = 0
    for rid, article in articles.items():
        require(article['material_id'] == sources[rid]['material_id'] and
                article['article_id'] == 'article:' + rid, 'Article identity differs')
        claims = unique(article['claims'], 'claim_id'); claims_count += len(claims)
        placed = article['introduction_claim_ids'] + [i for s in article['sections'] for i in s['claim_ids']]
        require(len(placed) == len(set(placed)) and set(placed) == set(claims), 'Unplaced/repeated claims')
        for claim in claims.values(): refs(claim, rid)
        for mention in article['concept_mentions']:
            link = links[mention['link_id']]
            require(link['resource_id'] == rid and link['concept_id'] == mention['concept_id'], 'Backlink differs')
        for related in article['related_materials']:
            require(related['derived_path'] is True and related['reason'].strip(), 'Derived path presented as fact')
            edges = [links[i] for i in related['supporting_link_ids']]
            require(len(edges) == 2 and related['target_resource_id'] != rid and
                    {e['resource_id'] for e in edges} == {rid, related['target_resource_id']} and
                    all(e['concept_id'] == related['via_concept_id'] for e in edges), 'Unsupported related path')
    render = json.loads((root / 'render-manifest.json').read_text())
    require(all(sha(root / p) == h for p, h in render.items()), 'Readable artifact changed')
    editorial_hash = sha(root / 'editorial.json')
    reading = json.loads((root / 'source-reading-proof.json').read_text())
    require(reading['editorial_sha256'] == editorial_hash and reading['full_source_read'] is True and
            reading['assignment_id'] == assignment['assignment_id'] and reading['editor'] == document['editor'] and
            reading['sources_manifest_sha256'] == sha(root / 'source-manifest.json'), 'Stale editor reading proof')
    require({r['resource_id'] for r in reading['records']} == set(sources), 'Missing editor reading source')
    for r in reading['records']:
        require(r['read_segment_indexes'] == list(range(sources[r['resource_id']]['segment_count'])) and
                r['files'] == sources[r['resource_id']]['files'], 'Incomplete editor reading coverage')
    if require_review:
        review = json.loads((root / 'review.json').read_text())
        require(review['assignment_id'] == assignment['assignment_id'] and
                review['result_sha256'] == editorial_hash and review['decision'] == 'pass' and
                review['reviewer'] == assignment['reviewer'] and review['reviewer'] != document['editor'] and
                review['full_source_read'] is True, 'Missing independent final pass')
        require(review['render_manifest_sha256'] == sha(root / 'render-manifest.json'), 'Review render binding differs')
        require(review['source_review_proof_sha256'] == sha(root / 'source-review-proof.json'), 'Review proof changed')
        proof = json.loads((root / 'source-review-proof.json').read_text())
        require(proof['result_sha256'] == editorial_hash and proof['full_source_read'] is True and
                proof['sources_manifest_sha256'] == sha(root / 'source-manifest.json') and
                proof['assignment_id'] == assignment['assignment_id'] and proof['reviewer'] == assignment['reviewer'],
                'Stale reviewer reading proof')
        require({r['resource_id'] for r in proof['records']} == set(sources), 'Missing reviewer reading source')
        for r in proof['records']:
            require(r['read_segment_indexes'] == list(range(sources[r['resource_id']]['segment_count'])) and
                    r['files'] == sources[r['resource_id']]['files'], 'Incomplete reviewer reading coverage')
        expected = {c['claim_id'] for a in articles.values() for c in a['claims']}
        require(len(review['claims']) == len(expected) and {c['claim_id'] for c in review['claims']} == expected and
                all(c['decision'] == 'pass' for c in review['claims']), 'Incomplete claim review')
        for key, ids, idkey in [('links', set(links), 'link_id'), ('concepts', set(concepts), 'concept_id')]:
            require(len(review[key]) == len(ids) and {x[idkey] for x in review[key]} == ids and
                    all(x['decision'] == 'pass' for x in review[key]), f'Incomplete {key} review')
        paths = {(a['resource_id'], r['target_resource_id'], r['via_concept_id'])
                 for a in articles.values() for r in a['related_materials']}
        require(len(review['related_materials']) == len(paths) and
                {(r['resource_id'], r['target_resource_id'], r['via_concept_id']) for r in review['related_materials']} == paths and
                all(r['decision'] == 'pass' for r in review['related_materials']), 'Incomplete related-path review')
    return {'articles': len(articles), 'claims': claims_count, 'evidence_windows': len(evidence),
            'concept_proposals': len(concepts), 'links': len(links),
            'review_required': require_review, 'editorial_sha256': editorial_hash,
            'revision_digest': content_revision_digest(document, sources), 'wire_contract': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--require-review', action='store_true')
    args = p.parse_args()
    try:
        print(json.dumps(validate(args.root, args.require_review), ensure_ascii=False))
    except (ValueError, KeyError, OSError) as error:
        p.exit(2, f'Blocked: {error}\n')


if __name__ == '__main__':
    main()
