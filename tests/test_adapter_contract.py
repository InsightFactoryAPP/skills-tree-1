import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "meta" / "adapter-contract.schema.json"


def load_schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def structural_example():
    return {
        "contract_version": "1.0",
        "adapter": {
            "id": "adapter/example-mcp",
            "version": "1.0",
            "name": "Example protocol adapter",
            "implementation": "implementation/example",
            "targets": [
                {"type": "protocol", "id": "protocol/example"}
            ],
            "input_mapping": [
                {
                    "source": "input.query",
                    "target": "request.query",
                    "transform": "identity"
                }
            ],
            "output_mapping": [
                {
                    "source": "response.results",
                    "target": "output.results"
                }
            ],
            "auth_requirements": ["target authentication when required"],
            "runtime_requirements": ["target runtime"],
            "constraints": ["example constraint"],
            "limitations": ["example limitation"],
            "provenance": {
                "source_type": "repository",
                "source": "tests/test_adapter_contract.py",
                "confidence": 0.5,
                "methodology": "structural schema example"
            },
            "evidence": ["tests/test_adapter_contract.py"],
            "status": "candidate"
        }
    }


def test_schema_is_valid_draft_2020_12():
    schema = load_schema()
    Draft202012Validator.check_schema(schema)


def test_structural_example_is_valid():
    validator = Draft202012Validator(load_schema())
    errors = list(validator.iter_errors(structural_example()))
    assert errors == []


def test_invalid_status_is_rejected():
    instance = structural_example()
    instance["adapter"]["status"] = "supported"
    validator = Draft202012Validator(load_schema())
    with pytest.raises(AssertionError):
        assert list(validator.iter_errors(instance)) == []


def test_unknown_adapter_field_is_rejected():
    instance = structural_example()
    instance["adapter"]["unexpected"] = True
    validator = Draft202012Validator(load_schema())
    with pytest.raises(AssertionError):
        assert list(validator.iter_errors(instance)) == []


def test_target_type_is_explicit():
    instance = structural_example()
    instance["adapter"]["targets"][0]["type"] = "provider"
    validator = Draft202012Validator(load_schema())
    with pytest.raises(AssertionError):
        assert list(validator.iter_errors(instance)) == []


def test_target_requires_id():
    instance = structural_example()
    del instance["adapter"]["targets"][0]["id"]
    validator = Draft202012Validator(load_schema())
    with pytest.raises(AssertionError):
        assert list(validator.iter_errors(instance)) == []
