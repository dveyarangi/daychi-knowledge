import json
from pathlib import Path
import pytest
from scripts.wiki_article_pilot import sha, validate, revision_digest, content_revision_digest, article_text_v1


def write(root, name, value):
    p = root / name
    p.write_text(json.dumps(value, ensure_ascii=False))
    return p


@pytest.fixture
def pilot(tmp_path):
    p = tmp_path
    (p/'source.txt').write_text('Synthetic complete source.\nSynthetic excluded ending.')
    (p/'source.ru.srt').write_text('1\n00:00:01,000 --> 00:00:02,000\nSynthetic complete source.\n')
    write(p,'source.info.json',{'synthetic':True})
    seg=[{'text':'Synthetic complete source.','start_seconds':1,'end_seconds':2},
         {'text':'Synthetic excluded ending.','start_seconds':3,'end_seconds':4}]
    write(p,'segments.json',seg);write(p,'quarantine.json',{'forbidden':[1]})
    files={n:{'path':str(p/n),'sha256':sha(p/n)} for n in ['source.txt','source.ru.srt','source.info.json','segments.json']}
    source={'resource_id':'synthetic-A','material_id':'synthetic-material','source_revision':1,
            'files':files,'segment_count':2,'forbidden_segment_indexes':[1],
            'quarantine_origin':str(p/'quarantine.json'),'quarantine_origin_sha256':sha(p/'quarantine.json')}
    write(p,'source-manifest.json',[source])
    write(p,'existing.json',{'pages':[{'concept_id':'synthetic-concept','kind':'topic','revision':1}]})
    assignment={'assignment_id':'synthetic-assignment','editor':'synthetic-editor','reviewer':'synthetic-reviewer',
                'pilot_sources':[{'resource_id':'synthetic-A','txt_sha256':sha(p/'source.txt'),
                'srt_sha256':sha(p/'source.ru.srt'),'info_sha256':sha(p/'source.info.json'),
                'segments_sha256':sha(p/'segments.json'),'forbidden_segment_indexes':[1]}]}
    write(p,'assignment.json',assignment)
    evidence={'evidence_id':'synthetic-evidence','resource_id':'synthetic-A','source_revision':1,
              'segment_indexes':[0],'start_seconds':1,'end_seconds':2,
              'quote':seg[0]['text'],'segments_sha256':sha(p/'segments.json')}
    concept={'concept_id':'synthetic-concept','kind':'topic','decision':'supplement','base_revision':1,
             'scope':'contextual_patch_only','merge_requires_full_existing_page_review':True,
             'aliases':[],'evidence_ids':['synthetic-evidence']}
    link={'link_id':'synthetic-link','concept_id':'synthetic-concept','resource_id':'synthetic-A',
          'material_id':'synthetic-material','relation':'explains','rationale':'Synthetic explanation.',
          'evidence_ids':['synthetic-evidence']}
    article={'resource_id':'synthetic-A','material_id':'synthetic-material','article_id':'article:synthetic-A',
             'claims':[{'claim_id':'synthetic-claim','text':'Synthetic article claim.',
                        'evidence_ids':['synthetic-evidence']}],'introduction_claim_ids':['synthetic-claim'],
             'sections':[],'concept_mentions':[{'concept_id':'synthetic-concept','link_id':'synthetic-link'}],
             'related_materials':[]}
    write(p,'editorial.json',{'format':'daychi-editorial-article-pilot/0.1','wire_contract':False,
          'assignment_id':assignment['assignment_id'],'editor':assignment['editor'],
          'sources_manifest_sha256':sha(p/'source-manifest.json'),
          'existing_concepts_reference':{'path':str(p/'existing.json'),'sha256':sha(p/'existing.json')},
          'articles':[article],'evidence':[evidence],'concept_proposals':[concept],'links':[link]})
    (p/'synthetic.md').write_text('Synthetic readable article.')
    write(p,'render-manifest.json',{'synthetic.md':sha(p/'synthetic.md')})
    records=[{'resource_id':'synthetic-A','files':files,'read_segment_indexes':[0,1]}]
    common={'assignment_id':assignment['assignment_id'],'full_source_read':True,
            'sources_manifest_sha256':sha(p/'source-manifest.json'),'records':records}
    write(p,'source-reading-proof.json',{**common,'editor':assignment['editor'],'editorial_sha256':sha(p/'editorial.json')})
    write(p,'source-review-proof.json',{**common,'reviewer':assignment['reviewer'],'result_sha256':sha(p/'editorial.json')})
    write(p,'review.json',{'assignment_id':assignment['assignment_id'],'result_sha256':sha(p/'editorial.json'),
          'decision':'pass','reviewer':assignment['reviewer'],'full_source_read':True,
          'render_manifest_sha256':sha(p/'render-manifest.json'),
          'source_review_proof_sha256':sha(p/'source-review-proof.json'),
          'claims':[{'claim_id':'synthetic-claim','decision':'pass'}],
          'concepts':[{'concept_id':'synthetic-concept','decision':'pass'}],
          'links':[{'link_id':'synthetic-link','decision':'pass'}],'related_materials':[]})
    return p


def modify(root,name,fn):
    value=json.loads((root/name).read_text());fn(value);write(root,name,value)


def test_valid_private_pilot_and_repeat_digest(pilot):
    first=validate(pilot,True);second=validate(pilot,True)
    assert first==second and first['wire_contract'] is False
    assert revision_digest({'b':2,'a':1})==revision_digest({'a':1,'b':2})
    assert revision_digest({'claims':['a','b']})!=revision_digest({'claims':['b','a']})


@pytest.mark.parametrize('change,match',[
    (lambda d:d.update(assignment_id='unreserved'),'Assignment differs'),
    (lambda d:d['evidence'][0].update(quote='Invented quote'),'Quote differs'),
    (lambda d:d['evidence'][0].update(start_seconds=0),'Timecodes differ'),
    (lambda d:d['evidence'][0].update(source_revision=2),'Stale evidence'),
    (lambda d:d['evidence'][0].update(segment_indexes=[1]),'Quarantined evidence'),
    (lambda d:d['articles'][0]['claims'][0].update(evidence_ids=[]),'Missing/duplicate evidence'),
    (lambda d:d['concept_proposals'][0].update(decision='new_page',base_revision=None),'Duplicate new concept'),
    (lambda d:d['articles'][0]['related_materials'].append({'target_resource_id':'synthetic-B',
      'via_concept_id':'synthetic-concept','supporting_link_ids':['synthetic-link'],
      'reason':'Unverified path','derived_path':True}),'Unsupported related path'),
])
def test_invalid_editorial(pilot,change,match):
    modify(pilot,'editorial.json',change)
    with pytest.raises(ValueError,match=match):validate(pilot)


def test_source_change_invalidates_dependencies(pilot):
    (pilot/'source.txt').write_text('Changed source.')
    with pytest.raises(ValueError,match='Source changed'):validate(pilot,True)


def test_article_change_requires_new_review(pilot):
    modify(pilot,'editorial.json',lambda d:d['articles'][0]['claims'][0].update(text='Changed article.'))
    modify(pilot,'source-reading-proof.json',lambda d:d.update(editorial_sha256=sha(pilot/'editorial.json')))
    with pytest.raises(ValueError,match='Missing independent final pass'):validate(pilot,True)


def test_readable_change_invalidates_review(pilot):
    (pilot/'synthetic.md').write_text('Changed readable article.')
    with pytest.raises(ValueError,match='Readable artifact changed'):validate(pilot,True)


def test_partial_or_self_review_is_rejected(pilot):
    modify(pilot,'review.json',lambda d:d['claims'].clear())
    with pytest.raises(ValueError,match='Incomplete claim review'):validate(pilot,True)
    modify(pilot,'review.json',lambda d:d.update(reviewer='synthetic-editor'))
    with pytest.raises(ValueError,match='Missing independent final pass'):validate(pilot,True)


def test_false_full_reading_coverage_is_rejected(pilot):
    modify(pilot,'source-reading-proof.json',lambda d:d['records'][0].update(read_segment_indexes=[0]))
    with pytest.raises(ValueError,match='Incomplete editor reading coverage'):validate(pilot)


def test_revision_ignores_assignment_paths_but_not_source_changes(pilot):
    doc=json.loads((pilot/'editorial.json').read_text())
    sources={s['resource_id']:s for s in json.loads((pilot/'source-manifest.json').read_text())}
    before=content_revision_digest(doc,sources)
    doc['assignment_id']='later-assignment';doc['editor']='another-editor'
    doc['processed_at']='later';doc['existing_concepts_reference']['path']='/another/checkout'
    for source in sources.values():
        for file in source['files'].values():file['path']='/another/checkout'
    assert content_revision_digest(doc,sources)==before
    sources['synthetic-A']['files']['source.txt']['sha256']='different-source'
    assert content_revision_digest(doc,sources)!=before


def projection_article():
    return {'claims':[{'claim_id':'second','text':'Second exact paragraph.'},
                      {'claim_id':'intro','text':'First exact paragraph.'}],
            'introduction_claim_ids':['intro'],
            'sections':[{'heading':'Private structural heading','claim_ids':['second']}]}


def test_v1_projection_preserves_every_claim_in_reading_order():
    article=projection_article()
    assert article_text_v1(article)=='First exact paragraph. Second exact paragraph.'
    assert article['claims'][0]['text']=='Second exact paragraph.'


@pytest.mark.parametrize('change,match',[
    (lambda a:a['sections'][0].update(claim_ids=[]),'Unplaced/repeated'),
    (lambda a:a['sections'][0].update(claim_ids=['second','intro']),'Unplaced/repeated'),
    (lambda a:a['claims'][0].update(text=' '),'Empty claim'),
    (lambda a:a['claims'][0].update(text='x'*3000),'do not truncate'),
])
def test_v1_projection_rejects_lossy_or_invalid_body(change,match):
    article=projection_article();change(article)
    with pytest.raises(ValueError,match=match):article_text_v1(article)
