"""Verify standalone v1 models against Daychi's executable import definitions."""
import argparse
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def definitions(path, names):
    tree = ast.parse(path.read_text())
    found = {node.name: ast.dump(node, include_attributes=False)
             for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in names}
    if set(found) != set(names):
        raise ValueError(f'Missing contract definitions in {path.name}')
    return found


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--daychi', type=Path, required=True)
    parser.add_argument('--require-semantics', action='store_true')
    parser.add_argument('--require-articles', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((ROOT/'contracts/source.json').read_text())
    for kind, source in manifest.items():
        server = args.daychi/source['source_path']
        if kind == 'semantics' and not server.exists() and not args.require_semantics:
            print('SKIP: semantic pilot absent from this Daychi checkout')
            continue
        local = ROOT/'daychi_contracts'/f'{kind}.py'
        if definitions(server, source['names']) != definitions(local, source['names']):
            raise SystemExit(f'FAIL: {kind}-v1 differs from Daychi; coordinate contract changes before updating')
        print(f'PASS: {kind}-v1 executable definitions match Daychi')
    provider = args.daychi/'practice_api/wiki_article_models.py'
    if not provider.exists() and not args.require_articles:
        print('SKIP: article extension absent from this Daychi checkout')
    else:
        if provider.read_bytes() != (ROOT/'daychi_contracts/articles.py').read_bytes():
            raise SystemExit('FAIL: articles-v1 differs from Daychi; coordinate before refreshing')
        if (args.daychi/'docs/contracts/wiki-articles-v1.schema.json').read_bytes() != (ROOT/'contracts/articles-v1.schema.json').read_bytes():
            raise SystemExit('FAIL: articles-v1 schema differs from Daychi')
        if (args.daychi/'tests/fixtures/article-batch-v1.json').read_bytes() != (ROOT/'tests/fixtures/article-batch-v1.json').read_bytes():
            raise SystemExit('FAIL: articles-v1 common conformance fixture differs from Daychi')
        print('PASS: articles-v1 models, schema and common fixture match Daychi')


if __name__ == '__main__':
    main()
