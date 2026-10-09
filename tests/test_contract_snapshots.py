import json
from pathlib import Path

from daychi_contracts.content import Batch
from daychi_contracts.semantics import SemanticBatch

ROOT = Path(__file__).resolve().parents[1]


def test_versioned_schema_snapshots_match_executable_models():
    for name, model in [('content', Batch), ('semantics', SemanticBatch)]:
        assert json.loads((ROOT/'contracts'/f'{name}-v1.schema.json').read_text()) == model.model_json_schema()


def test_pipeline_does_not_depend_on_product_server():
    import ast
    for path in (ROOT/'scripts').glob('*.py'):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or '').startswith('practice_api'), path.name
            elif isinstance(node, ast.Import):
                assert not any(name.name.startswith('practice_api') for name in node.names), path.name
