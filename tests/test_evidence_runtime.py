"""Regression tests for typed Evidence runtime access."""

from pathlib import Path

import pytest

from registry.evidence import EvidenceRuntime
from registry.runtime import UniversalRegistry


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registry" / "universal_registry.json"


def test_resolve_evidence_returns_normative_record() -> None:
    registry = UniversalRegistry(REGISTRY_PATH)
    runtime = EvidenceRuntime(registry.data)

    evidence = runtime.resolve_evidence("evidence/code-reviewer-runtime")

    assert evidence["id"] == "evidence/code-reviewer-runtime"
    assert evidence["type"] == "repository"
    assert "implementation/code-reviewer-system" in evidence["supports"]


def test_evidence_for_entity_is_deterministic() -> None:
    registry = UniversalRegistry(REGISTRY_PATH)
    runtime = EvidenceRuntime(registry.data)

    evidence = runtime.evidence_for_entity("implementation/code-reviewer-system")

    assert [item["id"] for item in evidence] == [
        "evidence/code-reviewer-runtime",
        "evidence/code-reviewer-system-source",
    ]


def test_unknown_evidence_is_rejected() -> None:
    registry = UniversalRegistry(REGISTRY_PATH)
    runtime = EvidenceRuntime(registry.data)

    with pytest.raises(KeyError, match="Unknown evidence"):
        runtime.resolve_evidence("evidence/missing")


def test_evidence_for_unknown_entity_returns_empty_list() -> None:
    registry = UniversalRegistry(REGISTRY_PATH)
    runtime = EvidenceRuntime(registry.data)

    assert runtime.evidence_for_entity("implementation/missing") == []


def test_runtime_returns_independent_evidence_snapshots() -> None:
    registry = UniversalRegistry(REGISTRY_PATH)
    runtime = EvidenceRuntime(registry.data)

    evidence = runtime.resolve_evidence("evidence/code-reviewer-runtime")
    evidence["supports"].clear()

    assert runtime.resolve_evidence("evidence/code-reviewer-runtime")["supports"]
