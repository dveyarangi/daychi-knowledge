"""Read the private XLSX without rewriting it and reconcile with live Daychi DTOs.

No owner credentials are used. Public DTOs prove publication presence/revision,
not private evidence or exact unsanitized payloads. Those require publication QA.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import time
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
import zipfile

from scripts.wiki_corpus_index import classify
from scripts.wiki_workflow import digest, file_hash, require, write_private

NS = {'x': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
HEADERS = ['ID источника', 'Материал', 'Тип', 'Публикация', 'Группа учёта',
           'Доступ', 'Готовый текст', 'Нужен ASR', 'Длительность, мин', 'Статус',
           'Ответственный', 'Проверяющий', 'Проверка', 'Следующий шаг', 'Партия', 'Импорт']


def registry_id(index_id):
    prefix, value = index_id.split(':', 1)
    return {'youtube': 'yt', 'youtube_playlist': 'playlist', 'drive_folder': 'folder',
            'other': 'link'}.get(prefix, prefix) + ':' + value


def registry_rows(path):
    """Read cached values only. Never recalculate, save or strip native features."""
    with zipfile.ZipFile(path) as z:
        strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            strings = [''.join(t.itertext()) for t in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('x:si', NS)]
        book = ET.fromstring(z.read('xl/workbook.xml'))
        sheet = next(s for s in book.findall('x:sheets/x:sheet', NS) if s.attrib['name'] == 'Материалы')
        rel_id = sheet.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
        rels = ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        target = next(r.attrib['Target'] for r in rels if r.attrib['Id'] == rel_id)
        name = target.lstrip('/') if target.startswith('/') else 'xl/' + target
        parsed = []
        headers_checked = False
        for row in ET.fromstring(z.read(name)).findall('x:sheetData/x:row', NS):
            values = [''] * 26
            for cell in row.findall('x:c', NS):
                letters = ''.join(c for c in cell.attrib['r'] if c.isalpha())
                col = 0
                for c in letters: col = col * 26 + ord(c) - 64
                if col > 26: continue
                value = cell.findtext('x:v', default='', namespaces=NS)
                if cell.attrib.get('t') == 's': value = strings[int(value)] if value else ''
                elif cell.attrib.get('t') == 'inlineStr': value = ''.join(cell.find('x:is', NS).itertext())
                values[col - 1] = value
            if int(row.attrib['r']) == 5:
                require(values[:16] == HEADERS, 'Registry columns changed; update adapter, do not guess')
                headers_checked = True
            elif int(row.attrib['r']) >= 6 and values[0]: parsed.append(values)
        require(headers_checked and parsed, 'Missing registry header/data')
        require(len({r[0] for r in parsed}) == len(parsed), 'Duplicate stable resource IDs in registry')
        return parsed


def production(origin, token_file=None):
    parts = urlsplit(origin)
    require(parts.scheme == 'https' and parts.netloc and not (parts.path or parts.query or parts.fragment or parts.username), 'HTTPS origin required')
    prefix = '/api/wiki' if token_file else '/api/public/wiki'
    headers = {'Accept': 'application/json'}
    if token_file: headers['Authorization'] = 'Bearer ' + Path(token_file).read_text().strip()
    def get(path):
        with urlopen(Request(origin + prefix + path, headers=headers), timeout=45) as response:
            return json.load(response)
    before = get('/graph')
    ids = sorted(n['id'] for n in before['nodes'] if n['type'] == 'material')
    require(len(set(ids)) == len(ids) and ids, 'Invalid production catalogue')
    with ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(lambda i: get('/materials/' + quote(i, safe='')), ids))
    after = get('/graph')
    require(digest(before) == digest(after), 'Catalogue changed during collection; repeat snapshot')
    require(sorted(r['id'] for r in rows) == ids, 'Incomplete production read')
    return rows, {'origin': origin, 'dto_visibility': 'private' if token_file else 'public_sanitized',
                  'catalogue_sha256': digest(before), 'catalogue_materials': len(ids)}


def make_snapshot(registry, rows, live_rows, metadata, checked_at):
    """Conservative intake: pending sources are preparation tasks, never guessed drafts."""
    bindings = {}
    published = {}
    for material in live_rows:
        for link in material.get('links', []):
            item = classify(link['url'])
            if item: bindings.setdefault(registry_id(item[1]), set()).add(material['id'])
        if material.get('annotation'): published[material['id']] = material['annotation']
    imported_sources = {'yt:' + a['resource_id'] for a in published.values()}
    tasks = []
    counts = {'registry_rows': len(rows), 'registry_imported': sum(bool(r[15]) for r in rows),
              'production_summaries': len(published), 'production_excerpts': sum(len(a['points']) for a in published.values()),
              'independent_review_pending': 0, 'registry_server_disagreements': 0}
    targets = {}
    for r in rows:
        for target in bindings.get(r[0], []): targets.setdefault(target, []).append(r[0])
    for r in rows:
        rid = r[0]
        bound = bindings.get(rid, set())
        target = next(iter(bound)) if len(bound) == 1 else 'source:' + rid
        ann = published.get(target)
        server_has_source = rid in imported_sources
        disagreement = bool(r[15]) != server_has_source
        counts['registry_server_disagreements'] += disagreement
        reviewed = r[12] == 'pass'
        kind = 'review' if server_has_source and not reviewed else 'summary' if server_has_source else 'prepare'
        revision = ann['revision'] if ann and server_has_source else 1
        state = 'published_existing' if server_has_source and reviewed else 'available'
        reasons = []
        if disagreement: reasons.append('registry_production_disagree')
        if len(bound) > 1: reasons.append('ambiguous_catalogue_binding')
        if ann and not server_has_source: reasons.append('target_has_another_source')
        if r[10] or r[11] or r[14]:
            if not server_has_source: reasons.append('legacy_assignment_requires_reconciliation')
        if r[9] == 'Контейнер': reasons.append('container_not_a_material')
        if r[12] == 'blocked' or r[5] == 'Недоступно': reasons.append('source_blocked')
        # The seven TXT/SRT rows still require identity/evidence intake; no auto promotion.
        if server_has_source and not reviewed: counts['independent_review_pending'] += 1
        if kind == 'prepare': target = 'source:' + rid
        if reasons: state = 'blocked'
        task = {'target': target, 'kind': kind, 'revision': revision, 'scope': [rid],
                'resource_ids': [rid], 'state': state, 'blocked_reasons': reasons,
                'catalogue_targets': sorted(bound),
                'source_fingerprint': digest(r[:17] + r[24:26]),
                'next_step': r[13] or ('independent_full_source_review' if kind == 'review' else 'verify_access_text_and_catalogue_binding')}
        task['id'] = f'{kind}:{target}:r{revision}'
        tasks.append(task)
    # No ambiguous duplicate target can enter an assignable queue.
    seen = {}
    for task in tasks:
        seen.setdefault(task['id'], []).append(task)
    unique = []
    for group in seen.values():
        task = group[0]
        if len(group) > 1:
            task['state'] = 'blocked'
            task['blocked_reasons'].append('multiple_sources_for_target')
            task['scope'] = sorted({s for g in group for s in g['scope']})
            task['resource_ids'] = task['scope']
            task['source_fingerprint'] = digest([g['source_fingerprint'] for g in group])
        unique.append(task)
    return {'protocol_version': 1, 'checked_at': checked_at, 'live_complete': True,
            'registry_path': str(Path(registry).resolve()), 'registry_sha256': file_hash(registry),
            **metadata, 'counts': counts, 'tasks': sorted(unique, key=lambda t: t['id'])}


def add_intake(snapshot, intake):
    """Coordinator promotes a proven preparation result; no inferred source readiness."""
    tasks = {t['id']: t for t in snapshot['tasks']}
    for item in intake['summaries']:
        source = tasks[item['source_task_id']]
        require(source['kind'] == 'prepare' and source['state'] == 'available', 'Source is blocked/published/ambiguous')
        require(source['source_fingerprint'] == item['source_fingerprint'], 'Intake belongs to an older source')
        require(source['catalogue_targets'] == [item['target']], 'One verified current catalogue target required')
        require(item.get('ready_evidence') and item.get('full_text_available') is True, 'Full text, hashes and intake evidence required')
        require(item['revision'] == 1, 'Corrections require explicit revision reconciliation, not initial intake')
        task = {**source, 'target': item['target'], 'kind': 'summary', 'revision': 1,
                'next_step': 'editorial_and_independent_full_source_review', 'intake_sha256': digest(item)}
        task['id'] = f"summary:{task['target']}:r1"
        require(task['id'] not in tasks, 'Target already has a summary task; reconcile aliases first')
        tasks[task['id']] = task
        # The same preparation should not be offered again while its summary is ready.
        source['state'] = 'blocked'; source['blocked_reasons'] = ['promoted_to_summary']
    snapshot['tasks'] = sorted(tasks.values(), key=lambda t: t['id'])
    return snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registry', type=Path, required=True)
    parser.add_argument('--origin', default='https://daychee-api-production.up.railway.app')
    parser.add_argument('--token-file', type=Path, help='Existing reader token; never included in output')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--intake', type=Path, help='Private coordinator-approved readiness proof for initial summaries')
    args = parser.parse_args()
    before = file_hash(args.registry)
    rows = registry_rows(args.registry)
    started = time.time()
    live, metadata = production(args.origin.rstrip('/'), args.token_file)
    require(file_hash(args.registry) == before, 'Registry changed during collection; repeat read-only snapshot')
    snapshot = make_snapshot(args.registry, rows, live, metadata, started)
    if args.intake: snapshot = add_intake(snapshot, json.loads(args.intake.read_text()))
    write_private(args.output, snapshot)
    print(json.dumps(snapshot['counts'], ensure_ascii=False))


if __name__ == '__main__':
    main()
