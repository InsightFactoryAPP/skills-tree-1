import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "meta" / "implementation-contract.schema.json"


def load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def valid_example():
    return {
        "contract_version": "1.0",
        "implementation": {
            "id": "implementation/example-web-search",
            "version": "1.0",
            "name": "Example Web Search Implementation",
            "skill": "11-web/web-search",
            "type": "api",
            "provider": "example-provider",
            "interface": "https",
            "inputs": ["query"],
            "outputs": ["search_results"],
            "requirements": [],
            "constraints": [],
            "limitations": [],
            "provenance": {"source_type": "repository", "source": "docs/example.md"},
            "evidence": [],
            "status": "candidate",
        },
    }


def test_implementation_contract_schema_is_valid():
    schema = load_schema()
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(valid_example())


def test_invalid_status_is_rejected():
    instance = valid_example()
    instance["implementation"]["status"] = "unknown"
    errors = list(Draft202012Validator(load_schema()).iter_errors(instance))
    assert errors


def test_provider_is_optional_but_explicitly_nullable():
    instance = valid_example()
    instance["implementation"]["provider"] = None
    Draft202012Validator(load_schema()).validate(instance)


def test_unknown_implementation_field_is_rejected():
    instance = valid_example()
    instance["implementation"]["unexpected"] = True
    errors = list(Draft202012Validator(load_schema()).iter_errors(instance))
    assert errors
