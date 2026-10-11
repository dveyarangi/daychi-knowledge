import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from daychi_contracts.articles import ArticleBatch
from scripts.wiki_article_validate import validate
from scripts.wiki_workflow import batch_scope, file_hash
from tests.test_wiki_workflow import ready, snapshot


def fixture():
    return json.loads((Path(__file__).parent / 'fixtures/article-batch-v1.json').read_text())


def test_common_provider_packet_and_unicode_span():
    batch = ArticleBatch(**fixture())
    paragraph = batch.articles[0].claims[1]; mention = paragraph.mentions[0]
    assert paragraph.text[mention.start:mention.end] == 'понятие'
    wrong = fixture(); wrong['articles'][0]['claims'][1]['mentions'][0]['link_id'] = 'l1'
    with pytest.raises(ValidationError): ArticleBatch(**wrong)


def test_article_workflow_binds_complete_sources_concepts_and_each_revision(ready, tmp_path):
    workflow, registry, _ = ready
    data = fixture(); data['batch_id'] = 'workflow-articles'
    scope = batch_scope(data, 'article')
    revisions = {'yt:' + a['resource_id']: a['revision'] for a in data['articles']}
    revisions.update({'concept:' + c['id']: c['revision'] for c in data['concepts']})
    task = {'id': 'article:fixture:r1', 'target': 'fixture', 'kind': 'article', 'revision': 1,
            'object_revisions': revisions, 'state': 'available', 'scope': scope, 'source_fingerprint': 'synthetic'}
    workflow.sync(snapshot(registry, [task]), 'coordinator')
    packet = workflow.claim([task['id']], 'editor', 'reviewer', data['batch_id'], 'coordinator')
    path = tmp_path / 'article-batch.json'; path.write_text(json.dumps(data))
    changed = copy.deepcopy(data); changed['concepts'][0]['revision'] = 2; path.write_text(json.dumps(changed))
    with pytest.raises(ValueError, match='Revision'): workflow.submit(packet['assignment_id'], path, 'editor')
    path.write_text(json.dumps(data)); accepted_hash = workflow.submit(packet['assignment_id'], path, 'editor')
    review = {'assignment_id': packet['assignment_id'], 'result_sha256': accepted_hash, 'decision': 'pass',
              'full_source_read': True, 'scope': scope, 'evidence': [{'path': 'synthetic-proof', 'sha256': 'c' * 64}]}
    workflow.review(packet['assignment_id'], review, 'reviewer')
    workflow.accept(packet['assignment_id'], 'owner', 'explicit synthetic acceptance')
    with pytest.raises(ValueError, match='authorization'):
        workflow.check_import(packet['assignment_id'], ArticleBatch(**data).model_dump(), 'article', 'https://example.test')
    workflow.authorize_publication(packet['assignment_id'], 'owner', 'explicit synthetic permission')
    workflow.check_import(packet['assignment_id'], ArticleBatch(**data).model_dump(), 'article', 'https://example.test')


def editorial_fixture(root):
    data = ArticleBatch(**fixture()).model_dump(); data.pop('review')
    manifest = []
    for i, source in enumerate(data['sources']):
        folder = root / source['resource_id']; folder.mkdir()
        quote = data['evidence'][i]
        ss = [{k: quote[k] for k in ('text', 'start_seconds', 'end_seconds')}]
        files = {}
        for name, body in [('source.txt', quote['text']), ('source.ru.srt', 'synthetic subtitles'), ('segments.json', json.dumps(ss))]:
            p = folder / name; p.write_text(body); files[name] = {'path': str(p), 'sha256': file_hash(p)}
        source['transcript_sha256'] = files['source.txt']['sha256']; source['subtitles_sha256'] = files['source.ru.srt']['sha256']
        manifest.append({k: source[k] for k in ('resource_id', 'material_id', 'expected_title', 'content_revision')} |
                        {'files': files, 'segment_count': 1, 'forbidden_segment_indexes': []})
    def write(name, value): (root / name).write_text(json.dumps(value))
    write('article-document.json', data); write('source-manifest.json', manifest)
    write('assignment.json', {'assignment_id': 'synthetic', 'editor': 'editor', 'reviewer': 'reviewer',
                            'tasks': [{'scope': batch_scope(data, 'article')}]})
    write('evidence-provenance.json', [{'id': e['id'], 'resource_id': e['resource_id'],
                                      'segment_indexes': [0], 'text_join': 'newline'} for e in data['evidence']])
    write('source-reading-proof.json', {'assignment_id': 'synthetic', 'editor': 'editor', 'full_source_read': True,
         'article_document_sha256': file_hash(root / 'article-document.json'),
         'sources_manifest_sha256': file_hash(root / 'source-manifest.json'),
         'records': [{'resource_id': s['resource_id'], 'files': s['files'], 'read_segment_indexes': [0]} for s in manifest]})


def test_exact_full_source_evidence_and_stale_reading_failures(tmp_path):
    editorial_fixture(tmp_path)
    assert validate(tmp_path)['evidence'] == 2
    source = json.loads((tmp_path / 'source-manifest.json').read_text())[0]
    Path(source['files']['source.txt']['path']).write_text('changed transcript')
    with pytest.raises(ValueError, match='Source changed'): validate(tmp_path)


def test_quarantine_is_checked_even_when_all_hashes_match(tmp_path):
    editorial_fixture(tmp_path)
    path = tmp_path / 'source-manifest.json'; data = json.loads(path.read_text()); data[0]['forbidden_segment_indexes'] = [0]
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match='Quarantined'): validate(tmp_path)


def test_redacted_snapshot_cannot_guess_protected_source_bindings(tmp_path):
    from scripts.wiki_workflow_snapshot import make_snapshot
    registry = tmp_path/'registry'; registry.write_text('synthetic')
    with pytest.raises(ValueError, match='Public recording protection'):
        make_snapshot(registry, [], [{'id':'material','links':[], 'annotation':{'revision':1,'points':[]}}], {}, 0)


def test_owner_snapshot_keeps_credentials_out_of_result_and_closes_session(tmp_path, monkeypatch):
    import io
    from scripts import wiki_workflow_snapshot as snapshots
    secret = tmp_path/'owner'; secret.write_text('synthetic-password')
    materials = [{'id':'material','links':[], 'annotation':{'resource_id':'abcdefghijk','revision':1}}]
    calls = []
    class Opener:
        def open(self, request, timeout):
            calls.append(request)
            value = {'csrf':'synthetic-csrf'} if request.full_url.endswith('/login') else {'materials':materials}
            return io.BytesIO(json.dumps(value).encode())
    monkeypatch.setattr(snapshots, 'build_opener', lambda *args: Opener())
    rows, metadata = snapshots.production('https://example.test', owner_password_file=secret)
    assert rows == materials and metadata['dto_visibility'] == 'owner_inventory'
    assert 'synthetic-password' not in json.dumps(metadata)
    assert calls[-1].full_url.endswith('/logout') and calls[-1].get_header('X-csrf-token') == 'synthetic-csrf'
    assert [r.get_method() for r in calls] == ['POST','GET','GET','POST']
