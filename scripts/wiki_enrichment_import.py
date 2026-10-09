"""Validate/import a private wiki batch through the existing owner session."""
import argparse
import http.cookiejar
import json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import HTTPCookieProcessor, Request, build_opener

from daychi_contracts.content import Batch
from scripts.wiki_workflow import Workflow, write_private


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--batch',type=Path,required=True)
    p.add_argument('--origin',default='https://daychee-api-production.up.railway.app')
    p.add_argument('--password-file',type=Path)
    p.add_argument('--apply',action='store_true',help='Import; otherwise only validate locally')
    p.add_argument('--workflow-db', type=Path)
    p.add_argument('--assignment', help='Coordinator reservation with final acceptance and publication authorization')
    p.add_argument('--receipt', type=Path, help='Private durable import receipt')
    args=p.parse_args()
    batch=Batch.model_validate_json(args.batch.read_text()).model_dump()
    print(f"Validated {len(batch['records'])} source-bound drafts, {sum(len(r['points']) for r in batch['records'])} excerpts")
    if not args.apply:return
    origin=args.origin.rstrip('/');u=urlsplit(origin)
    if u.scheme!='https' or not u.netloc or u.path or u.query or u.fragment or u.username:
        p.error('origin must be an HTTPS origin without credentials/path')
    if args.password_file is None:p.error('--apply requires existing --password-file')
    if not (args.workflow_db and args.assignment and args.receipt):
        p.error('--apply requires --workflow-db, --assignment and --receipt; see docs/collaboration-workflow.md')
    workflow = Workflow(args.workflow_db)
    try: workflow.check_import(args.assignment, batch, 'summary', origin)
    finally: workflow.close()
    opener=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
    csrf=''
    def call(method,path,body=None):
        data=None if body is None else json.dumps(body,ensure_ascii=False).encode()
        headers={'Origin':origin,'Content-Type':'application/json'}
        if csrf:headers['X-CSRF-Token']=csrf
        with opener.open(Request(origin+path,data=data,headers=headers,method=method),timeout=60) as response:
            return json.load(response)
    login=call('POST','/api/admin/login',{'password':args.password_file.read_text().strip()})
    csrf=login['csrf']
    try:
        workflow = Workflow(args.workflow_db)
        try:
            workflow.begin_import(args.assignment, batch, 'summary', origin)
        finally:
            workflow.close()
        imported=call('POST','/api/admin/wiki/content',batch)
        write_private(args.receipt, {'assignment_id': args.assignment, 'batch_id': batch['batch_id'],
                                    'origin': origin, 'import': imported, 'state': 'server_write_confirmed_replay_pending'})
        replay=call('POST','/api/admin/wiki/content',batch)
        assert imported['count']==len(batch['records']) and replay['already_imported']
        receipt={'assignment_id':args.assignment, 'batch_id':batch['batch_id'], 'origin':origin,
                 'import':imported,'replay':replay,'stored':call('GET','/api/admin/wiki/content')}
        write_private(args.receipt, receipt)
        workflow = Workflow(args.workflow_db)
        try: workflow.imported(args.assignment, receipt)
        finally: workflow.close()
        print(json.dumps({'receipt': str(args.receipt), 'count': imported['count'], 'already_imported': replay['already_imported']}))
    finally:
        call('POST','/api/admin/logout')


if __name__=='__main__':main()
