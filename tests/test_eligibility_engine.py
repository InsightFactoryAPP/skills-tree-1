import json
from pathlib import Path

from jsonschema import Draft202012Validator

from registry.eligibility import EligibilityEngine
from registry.runtime import UniversalRegistry

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "universal_registry.json"
SCHEMA = ROOT / "meta" / "eligibility-contract.schema.json"


def test_eligibility_contract_schema_is_valid() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)


def test_eligibility_allows_candidate_without_target() -> None:
    engine = EligibilityEngine(UniversalRegistry(REGISTRY))
    result = engine.evaluate(["05-code/code-review"], None)
    assert result["candidates"] == [{
        "id": "05-code/code-review",
        "status": "eligible",
        "reasons": [],
    }]


def test_eligibility_requires_compatibility_for_adapter_target() -> None:
    engine = EligibilityEngine(UniversalRegistry(REGISTRY))
    result = engine.evaluate(
        ["adapter/code-reviewer-mcp"],
        {"type": "protocol", "id": "protocol/model-context-protocol"},
    )
    assert result["candidates"][0]["status"] == "conditional"
    assert result["candidates"][0]["reasons"][0]["code"] == "compatibility_conditional"


def test_eligibility_rejects_missing_compatibility() -> None:
    engine = EligibilityEngine(UniversalRegistry(REGISTRY))
    result = engine.evaluate(
        ["adapter/code-reviewer-mcp"],
        {"type": "runtime", "id": "runtime/missing"},
    )
    assert result["candidates"][0]["status"] == "ineligible"
    assert result["candidates"][0]["reasons"][0]["code"] == "compatibility_missing"


def test_eligibility_is_deterministic() -> None:
    engine = EligibilityEngine(UniversalRegistry(REGISTRY))
    target = {"type": "protocol", "id": "protocol/model-context-protocol"}
    assert engine.evaluate(["adapter/code-reviewer-mcp"], target) == engine.evaluate(
        ["adapter/code-reviewer-mcp"], target
    )
