import copy
from concurrent.futures import ThreadPoolExecutor
import json
import time

import pytest

from scripts.wiki_workflow import Workflow, batch_payload, file_hash
from scripts.wiki_workflow_snapshot import add_intake, make_snapshot

ORIGIN = 'https://example.test'
RID = 'yt:abcdefghijk'


def item(target='m:one', revision=1, state='available'):
    return {'id': f'summary:{target}:r{revision}', 'target': target, 'kind': 'summary',
            'revision': revision, 'state': state, 'scope': [RID], 'source_fingerprint': 'fixed'}


def snapshot(registry, tasks=None):
    return {'protocol_version': 1, 'live_complete': True, 'origin': ORIGIN,
            'checked_at': time.time(), 'registry_path': str(registry),
            'registry_sha256': file_hash(registry), 'tasks': tasks or [item()]}


@pytest.fixture
def ready(tmp_path):
    registry = tmp_path / 'registry'; registry.write_text('synthetic')
    db = tmp_path / 'workflow.sqlite3'
    w = Workflow(db); w.initialize('owner'); w.sync(snapshot(registry), 'coordinator')
    yield w, registry, db
    w.close()


def packet(w):
    return w.claim([item()['id']], 'editor', 'reviewer', 'synthetic-batch', 'coordinator')['assignment_id']


def result(path):
    batch = {'batch_id': 'synthetic-batch', 'records': [{'resource_id': 'abcdefghijk',
        'expected_title': 'Synthetic lesson', 'revision': 1,
        'summary': 'A synthetic source-bound summary of the lesson for workflow validation.',
        'points': [{'text': 'Exact synthetic quote', 'start_seconds': i, 'end_seconds': i + 1} for i in (0, 2, 4)],
        'transcript_sha256': 'a' * 64, 'subtitles_sha256': 'b' * 64, 'status': 'source_checked_draft'}]}
    path.write_text(json.dumps(batch))
    return batch_payload(path, 'summary')


def reviewed(w, path):
    identifier = packet(w)
    batch = result(path)
    result_hash = w.submit(identifier, path, 'editor')
    report = {'assignment_id': identifier, 'result_sha256': result_hash, 'decision': 'pass',
              'scope': [RID], 'full_source_read': True, 'evidence': [{'path': 'private/full-review.json', 'sha256': 'c' * 64}]}
    w.review(identifier, report, 'reviewer')
    return identifier, batch, report


def test_two_coordinator_connections_cannot_double_claim(ready):
    w, _, db = ready
    def claim(n):
        other = Workflow(db)
        try:
            other.claim([item()['id']], 'editor', 'reviewer', f'batch-{n}', 'coordinator')
            return True
        except ValueError:
            return False
        finally: other.close()
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sum(pool.map(claim, (1, 2))) == 1
    assert w.c.execute('SELECT count(*) FROM assignments').fetchone()[0] == 1


def test_other_revision_and_source_alias_cannot_duplicate_active_target(ready):
    w, registry, _ = ready
    w.sync(snapshot(registry, [item(), item(revision=2)]), 'coordinator')
    packet(w)
    with pytest.raises(ValueError, match='another revision'):
        w.claim([item(revision=2)['id']], 'editor2', 'reviewer2', 'another', 'coordinator')


def test_same_source_under_another_target_cannot_be_claimed_twice(ready):
    w, registry, _ = ready
    w.sync(snapshot(registry, [item(), item(target='m:alias')]), 'coordinator')
    packet(w)
    with pytest.raises(ValueError, match='Source already reserved'):
        w.claim([item(target='m:alias')['id']], 'editor2', 'reviewer2', 'alias', 'coordinator')


def test_published_stale_changed_and_independent_claim_guards(ready):
    w, registry, _ = ready
    with pytest.raises(ValueError, match='Independent'):
        w.claim([item()['id']], 'same', 'same', 'one', 'coordinator')
    stale = snapshot(registry); stale['checked_at'] -= 90000
    with pytest.raises(ValueError, match='Stale'): w.sync(stale, 'coordinator')
    w.sync(snapshot(registry, [item(state='published_existing')]), 'coordinator')
    with pytest.raises(ValueError, match='unavailable'): packet(w)
    registry.write_text('manual edit')
    with pytest.raises(ValueError, match='Registry changed'): packet(w)


def test_sync_preserves_assignment_and_blocks_changed_source(ready):
    w, registry, _ = ready
    identifier = packet(w)
    changed = item(); changed['source_fingerprint'] = 'new'
    w.sync(snapshot(registry, [changed]), 'coordinator')
    row = w.c.execute('SELECT * FROM tasks').fetchone()
    assert row['state'] == 'blocked' and row['assignment'] == identifier
    with pytest.raises(ValueError, match='unavailable'): packet(w)
    w.release(identifier, 'owner', 'review source change')
    w.sync(snapshot(registry, [changed]), 'coordinator')
    assert w.c.execute('SELECT state FROM tasks').fetchone()[0] == 'available'


def test_scope_and_revision_are_bound_to_assignment(ready, tmp_path):
    w, _, _ = ready
    identifier = packet(w); path = tmp_path / 'batch.json'; batch = result(path)
    batch['records'][0]['resource_id'] = 'zyxwvutsrqp'; path.write_text(json.dumps(batch))
    with pytest.raises(ValueError, match='outside assigned scope'): w.submit(identifier, path, 'editor')
    batch['records'][0]['resource_id'] = 'abcdefghijk'; batch['records'][0]['revision'] = 2
    path.write_text(json.dumps(batch))
    with pytest.raises(ValueError, match='Revision'): w.submit(identifier, path, 'editor')


def test_single_acceptor_exact_result_and_separate_publication_authorization(ready, tmp_path):
    w, _, _ = ready
    identifier, batch, report = reviewed(w, tmp_path / 'batch.json')
    with pytest.raises(ValueError, match='designated'): w.accept(identifier, 'reviewer', 'approved')
    w.accept(identifier, 'owner', 'explicit human acceptance')
    with pytest.raises(ValueError, match='authorization'): w.begin_import(identifier, batch, 'summary', ORIGIN)
    w.authorize_publication(identifier, 'owner', 'explicit permission for synthetic batch')
    changed = copy.deepcopy(batch); changed['records'][0]['summary'] += ' Changed.'
    with pytest.raises(ValueError, match='changed'): w.begin_import(identifier, changed, 'summary', ORIGIN)
    with pytest.raises(ValueError, match='origin'): w.begin_import(identifier, batch, 'summary', 'https://another.test')
    w.begin_import(identifier, batch, 'summary', ORIGIN)
    with pytest.raises(ValueError): w.begin_import(identifier, batch, 'summary', ORIGIN)
    with pytest.raises(ValueError, match='server write'): w.release(identifier, 'owner', 'timeout')
    w.imported(identifier, {'count': 1, 'already_imported': False})
    qa = {'assignment_id': identifier, 'batch_id': batch['batch_id'], 'result_sha256': report['result_sha256'],
          'evidence': ['private/production-qa.json']}
    with pytest.raises(ValueError, match='incomplete'): w.verify(identifier, qa, 'coordinator')
    qa.update({k: True for k in ('all_payloads_exact', 'source_fields_unchanged', 'idempotent_replay',
                               'anonymous_access_checked', 'authorized_ui_checked', 'registry_updated')})
    w.verify(identifier, qa, 'coordinator')
    assert w.assignment(identifier)['state'] == 'verified'


def test_review_hash_coverage_and_rework(ready, tmp_path):
    w, _, _ = ready
    identifier = packet(w); path = tmp_path / 'batch.json'; result(path)
    h = w.submit(identifier, path, 'editor')
    report = {'assignment_id': identifier, 'result_sha256': h, 'decision': 'pass',
              'scope': [], 'full_source_read': True, 'evidence': ['private/review.json']}
    with pytest.raises(ValueError, match='reviewer'): w.review(identifier, report, 'editor')
    with pytest.raises(ValueError, match='coverage'): w.review(identifier, report, 'reviewer')
    report['decision'] = 'needs_changes'; w.review(identifier, report, 'reviewer')
    w.submit(identifier, path, 'editor')
    assert w.assignment(identifier)['review_hash'] is None
    with pytest.raises(ValueError, match='Review pass'): w.accept(identifier, 'owner', 'skip review')


def test_interrupted_import_needs_live_reconciliation_and_new_authorization(ready, tmp_path):
    w, _, _ = ready
    identifier, batch, report = reviewed(w, tmp_path / 'batch.json')
    w.accept(identifier, 'owner', 'accept'); w.authorize_publication(identifier, 'owner', 'publish')
    w.begin_import(identifier, batch, 'summary', ORIGIN)
    recovery = {'result_sha256': report['result_sha256'], 'server_write': 'unknown', 'evidence': ['live-check.json']}
    with pytest.raises(ValueError, match='Unknown'): w.reconcile_import(identifier, recovery, 'owner')
    recovery['server_write'] = 'absent'; w.reconcile_import(identifier, recovery, 'owner')
    assert w.assignment(identifier)['state'] == 'accepted'
    with pytest.raises(ValueError, match='authorization'): w.begin_import(identifier, batch, 'summary', ORIGIN)


def test_live_snapshot_distinguishes_legacy_review_and_unprepared_sources(tmp_path):
    registry = tmp_path / 'registry'; registry.write_text('synthetic')
    def row(rid, imported=False, reviewed=False):
        r = [''] * 26; r[0] = rid; r[15] = 'date' if imported else ''; r[12] = 'pass' if reviewed else ''
        return r
    live = [{'id': 'm:one', 'links': [{'url': 'https://youtu.be/abcdefghijk'}],
             'annotation': {'resource_id': 'abcdefghijk', 'revision': 1, 'points': [{}, {}, {}]}}]
    s = make_snapshot(registry, [row(RID, True), row('drive:synthetic')], live, {'origin': ORIGIN}, time.time())
    assert s['counts']['registry_server_disagreements'] == 0
    assert s['counts']['independent_review_pending'] == 1
    assert {t['kind'] for t in s['tasks']} == {'review', 'prepare'}
    assert all(t['state'] == 'available' for t in s['tasks'])


def test_intake_requires_current_source_and_unique_catalogue_target(tmp_path):
    registry = tmp_path / 'registry'; registry.write_text('synthetic')
    r = [''] * 26; r[0] = RID
    live = [{'id': 'm:one', 'links': [{'url': 'https://youtu.be/abcdefghijk'}]}]
    s = make_snapshot(registry, [r], live, {'origin': ORIGIN}, time.time())
    t = s['tasks'][0]
    intake = {'summaries': [{'source_task_id': t['id'], 'source_fingerprint': 'old',
                            'target': 'm:one', 'revision': 1, 'ready_evidence': ['full-text-proof.json'], 'full_text_available': True}]}
    with pytest.raises(ValueError, match='older source'): add_intake(copy.deepcopy(s), intake)
    intake['summaries'][0]['source_fingerprint'] = t['source_fingerprint']
    promoted = add_intake(s, intake)
    assert [(i['kind'], i['state']) for i in promoted['tasks']] == [('prepare', 'blocked'), ('summary', 'available')]
