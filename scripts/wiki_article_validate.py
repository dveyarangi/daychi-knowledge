"""Validate a private structured editorial document against full pinned sources.

This verifies exact evidence and review bindings, not semantic truth by itself.
Production publication additionally needs coordinator acceptance and permission.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

from daychi_contracts.articles import ArticleDocument
from scripts.wiki_workflow import batch_scope, file_hash, require


def read(path):
    return json.loads(Path(path).read_text())


def validate_reading(proof, manifest, *, identity, manifest_hash, document_hash):
    require(proof.get('full_source_read') is True and proof.get('sources_manifest_sha256') == manifest_hash,
            'Complete source reading bound to the current manifest is required')
    require(proof.get('editor', proof.get('reviewer')) == identity, 'Reading identity differs')
    require(proof.get('article_document_sha256', proof.get('result_sha256')) == document_hash,
            'Reading proof belongs to different editorial bytes')
    records = proof['records']
    require(len(records) == len(manifest) and {r['resource_id'] for r in records} == set(manifest),
            'Reading source coverage differs')
    for record in records:
        source = manifest[record['resource_id']]
        require(record['files'] == source['files'] and
                record['read_segment_indexes'] == list(range(source['segment_count'])), 'Incomplete source reading coverage')
        if record.get('prior_proof'):
            require(file_hash(record['prior_proof']) == record['prior_proof_sha256'], 'Prior reading proof changed')
            previous = read(record['prior_proof'])
            require(previous.get('full_source_read') is True and previous.get('editor', previous.get('reviewer')) == identity,
                    'Prior complete reading must belong to the same reader')
            require(any(r['resource_id'] == record['resource_id'] and r['files'] == source['files'] and
                        r['read_segment_indexes'] == record['read_segment_indexes'] for r in previous['records']),
                    'Reused reading refers to different source bytes')


def validate(root, review_path=None):
    root = Path(root)
    document_path = root / 'article-document.json'
    document = ArticleDocument.model_validate_json(document_path.read_text()).model_dump()
    document_hash = file_hash(document_path)
    assignment = read(root / 'assignment.json')
    scope = sorted(s for t in assignment['tasks'] for s in t['scope'])
    require(batch_scope(document, 'article') == scope, 'Editorial work is outside its coordinator reservation')
    manifest_path = root / 'source-manifest.json'
    sources = read(manifest_path)
    require(len({s['resource_id'] for s in sources}) == len(sources), 'Duplicate manifest source')
    manifest = {s['resource_id']: s for s in sources}
    require(set(manifest) == {s['resource_id'] for s in document['sources']}, 'Source pin coverage differs')
    segments = {}
    for pin in document['sources']:
        source = manifest[pin['resource_id']]
        for key in ('resource_id', 'material_id', 'expected_title', 'content_revision'):
            require(pin[key] == source[key], 'Source catalogue pin differs')
        for name, file in source['files'].items():
            require(file_hash(file['path']) == file['sha256'], f'Source changed: {pin["resource_id"]}/{name}')
        require(pin['transcript_sha256'] == source['files']['source.txt']['sha256'] and
                pin['subtitles_sha256'] == source['files']['source.ru.srt']['sha256'], 'Wire source hashes differ')
        text = Path(source['files']['source.txt']['path']).read_text()
        ss = read(source['files']['segments.json']['path'])
        require(len(ss) == source['segment_count'] and text.split() == ' '.join(s['text'] for s in ss).split(),
                'Full TXT and segment source differ')
        segments[pin['resource_id']] = ss
    provenance = read(root / 'evidence-provenance.json')
    require(len({e['id'] for e in provenance}) == len(provenance), 'Duplicate evidence provenance')
    by_id = {e['id']: e for e in provenance}
    require(set(by_id) == {e['id'] for e in document['evidence']}, 'Evidence provenance coverage differs')
    for evidence in document['evidence']:
        proof = by_id[evidence['id']]; rid = evidence['resource_id']; indexes = proof['segment_indexes']
        require(proof['resource_id'] == rid and indexes and indexes == list(range(indexes[0], indexes[-1] + 1)) and
                0 <= indexes[0] <= indexes[-1] < len(segments[rid]), 'Invalid contiguous evidence window')
        require(not set(indexes).intersection(manifest[rid]['forbidden_segment_indexes']), 'Quarantined evidence')
        selected = [segments[rid][i] for i in indexes]
        require(min(s['start_seconds'] for s in selected) == evidence['start_seconds'] and
                max(s['end_seconds'] for s in selected) == evidence['end_seconds'], 'Evidence timecodes differ')
        require(proof['text_join'] in ('newline', 'whitespace'), 'Unknown quote normalization')
        if proof['text_join'] == 'newline':
            require(evidence['text'] == '\n'.join(s['text'] for s in selected), 'Evidence text differs')
        else:
            require(evidence['text'].split() == ' '.join(s['text'] for s in selected).split(), 'Evidence text differs')
    reading = read(root / 'source-reading-proof.json')
    require(reading['assignment_id'] == assignment['assignment_id'], 'Editor assignment differs')
    validate_reading(reading, manifest, identity=assignment['editor'],
                     manifest_hash=file_hash(manifest_path), document_hash=document_hash)
    if review_path:
        review_path = Path(review_path); review = read(review_path)
        require(review['assignment_id'] == assignment['assignment_id'] and
                review['result_sha256'] == document_hash and review['decision'] == 'pass' and
                review['reviewer'] == assignment['reviewer'] and assignment['reviewer'] != assignment['editor'] and
                set(review['scope']) == set(scope), 'Missing independent review of final editorial bytes')
        proof_path = review_path.parent / 'source-review-proof.json'
        require(file_hash(proof_path) == review['source_review_proof_sha256'], 'Reviewer reading proof changed')
        validate_reading(read(proof_path), manifest, identity=assignment['reviewer'],
                         manifest_hash=file_hash(manifest_path), document_hash=document_hash)
        for evidence in review['evidence']:
            require(file_hash(evidence['path']) == evidence['sha256'], 'Review evidence changed')
        claims = [c for a in document['articles'] for c in a['claims']] + [c for p in document['concepts'] for c in p['claims']]
        require(Counter((c['id'], tuple(c['evidence_ids'])) for c in claims) ==
                Counter((c['claim_id'], tuple(c['evidence_ids'])) for c in review['claims']) and
                all(c['decision'] == 'pass' for c in review['claims']), 'Incomplete individual claim review')
        for key, values, identity in [('concepts', document['concepts'], 'concept_id'), ('links', document['links'], 'link_id')]:
            require(Counter(v['id'] for v in values) == Counter(v[identity] for v in review[key]) and
                    all(v['decision'] == 'pass' for v in review[key]), f'Incomplete {key} review')
        links = {l['id']: l for l in document['links']}
        spans = Counter((c['id'], c['text'][m['start']:m['end']], links[m['link_id']]['concept_id'])
                        for a in document['articles'] for c in a['claims'] for m in c['mentions'])
        require(spans == Counter((m['claim_id'], m['text'], m['concept_id']) for m in review['inline_mentions']) and
                all(m['decision'] == 'pass' for m in review['inline_mentions']), 'Incomplete inline placement review')
        paths = Counter((a['resource_id'], r['material_id'], r['via_concept_id'], tuple(r['supporting_link_ids']))
                        for a in document['articles'] for r in a['related'])
        require(paths == Counter((r['resource_id'], r['target_material_id'], r['via_concept_id'], tuple(r['supporting_link_ids']))
                                 for r in review['related_materials']) and
                all(r['decision'] == 'pass' for r in review['related_materials']), 'Incomplete related path review')
    return {'article_document_sha256': document_hash, 'sources': len(sources), 'articles': len(document['articles']),
            'concepts': len(document['concepts']), 'evidence': len(document['evidence']),
            'independent_review_checked': bool(review_path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--review', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(validate(args.root, args.review), ensure_ascii=False))
    except (ValueError, KeyError, OSError) as error:
        parser.exit(2, f'Blocked: {error}\n')


if __name__ == '__main__':
    main()
