"""Regression tests for typed Compatibility runtime access."""

import json
from pathlib import Path

import pytest

from registry.compatibility import CompatibilityRuntime
from registry.runtime import UniversalRegistry


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registry" / "universal_registry.json"
SCHEMA_PATH = ROOT / "meta" / "compatibility-model.schema.json"


def _runtime() -> CompatibilityRuntime:
    registry = UniversalRegistry(REGISTRY_PATH)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return CompatibilityRuntime(registry.data, schema)


def test_resolve_compatibility_returns_normative_record() -> None:
    record = _runtime().resolve_compatibility(
        "compatibility/code-reviewer-mcp-model-context-protocol"
    )

    assert record["subject"] == "adapter/code-reviewer-mcp"
    assert record["target"] == {
        "type": "protocol",
        "id": "protocol/model-context-protocol",
    }
    assert record["status"] == "conditional"


def test_compatibility_for_is_deterministic_and_filterable() -> None:
    runtime = _runtime()

    records = runtime.compatibility_for(
        "adapter/code-reviewer-mcp",
        target_type="protocol",
        target_id="protocol/model-context-protocol",
    )

    assert [item["id"] for item in records] == [
        "compatibility/code-reviewer-mcp-model-context-protocol"
    ]


def test_unknown_compatibility_is_rejected() -> None:
    with pytest.raises(KeyError, match="Unknown compatibility"):
        _runtime().resolve_compatibility("compatibility/unknown")


def test_compatibility_runtime_rejects_unsupported_evidence() -> None:
    registry = UniversalRegistry(REGISTRY_PATH)
    data = registry.data
    data["entities"]["compatibilities"][0]["evidence"] = [
        "evidence/code-reviewer-system-source"
    ]
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    with pytest.raises(ValueError, match="does not support"):
        CompatibilityRuntime(data, schema)


def test_compatibility_runtime_returns_read_only_snapshots() -> None:
    runtime = _runtime()
    first = runtime.resolve_compatibility(
        "compatibility/code-reviewer-mcp-model-context-protocol"
    )
    first["constraints"].append("mutated")

    second = runtime.resolve_compatibility(
        "compatibility/code-reviewer-mcp-model-context-protocol"
    )

    assert "mutated" not in second["constraints"]
