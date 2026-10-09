"""Validate or import a private reviewed glossary/topic batch through the owner API."""
import argparse
import http.cookiejar
import json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import HTTPCookieProcessor, Request, build_opener

from daychi_contracts.semantics import SemanticBatch
from scripts.wiki_workflow import Workflow, write_private


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch',type=Path,required=True)
    parser.add_argument('--origin',default='https://daychee-api-production.up.railway.app')
    parser.add_argument('--password-file',type=Path)
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--workflow-db',type=Path)
    parser.add_argument('--assignment')
    parser.add_argument('--receipt',type=Path)
    args=parser.parse_args();batch=SemanticBatch.model_validate_json(args.batch.read_text())
    print(f'Validated {len(batch.pages)} pages / {sum(len(p.links) for p in batch.pages)} semantic relations')
    if not args.apply:return
    origin=args.origin.rstrip('/');parts=urlsplit(origin)
    if parts.scheme!='https' or not parts.netloc or parts.path or parts.query or parts.fragment or parts.username:
        parser.error('origin must be an HTTPS origin without credentials/path')
    if args.password_file is None:parser.error('--apply requires the existing owner password file')
    if not (args.workflow_db and args.assignment and args.receipt):
        parser.error('--apply requires --workflow-db, --assignment and --receipt; see docs/collaboration-workflow.md')
    workflow=Workflow(args.workflow_db)
    try:workflow.check_import(args.assignment,batch.model_dump(),'semantic',origin)
    finally:workflow.close()
    opener=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()));csrf=''
    def call(method,path,body=None):
        headers={'Origin':origin,'Content-Type':'application/json'}
        if csrf:headers['X-CSRF-Token']=csrf
        data=None if body is None else json.dumps(body,ensure_ascii=False).encode()
        with opener.open(Request(origin+path,data=data,headers=headers,method=method),timeout=60) as response:
            return json.load(response)
    login=call('POST','/api/admin/login',{'password':args.password_file.read_text().strip()});csrf=login['csrf']
    try:
        workflow=Workflow(args.workflow_db)
        try:workflow.begin_import(args.assignment,batch.model_dump(),'semantic',origin)
        finally:workflow.close()
        imported=call('POST','/api/admin/wiki/semantic-content',batch.model_dump())
        write_private(args.receipt,{'assignment_id':args.assignment,'batch_id':batch.batch_id,'origin':origin,
                                   'import':imported,'state':'server_write_confirmed_replay_pending'})
        replay=call('POST','/api/admin/wiki/semantic-content',batch.model_dump())
        assert imported['pages']==len(batch.pages) and replay['already_imported']
        receipt={'assignment_id':args.assignment,'batch_id':batch.batch_id,'origin':origin,
                 'import':imported,'replay':replay,'stored':call('GET','/api/admin/wiki/semantic-content')}
        write_private(args.receipt,receipt)
        workflow=Workflow(args.workflow_db)
        try:workflow.imported(args.assignment,receipt)
        finally:workflow.close()
        print(json.dumps({'receipt':str(args.receipt),'pages':imported['pages'],'already_imported':replay['already_imported']}))
    finally:call('POST','/api/admin/logout')


if __name__=='__main__':main()
