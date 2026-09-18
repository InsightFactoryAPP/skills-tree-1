"""Regression tests for typed Implementation runtime access."""

import json
from pathlib import Path

import pytest

from registry.runtime import UniversalRegistry

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registry" / "universal_registry.json"


def test_resolve_implementation_returns_normative_record() -> None:
    registry = UniversalRegistry(REGISTRY_PATH)
    implementation = registry.resolve_implementation("implementation/code-reviewer-system")
    assert implementation["id"] == "implementation/code-reviewer-system"
    assert implementation["skill"] == "05-code/code-review"
    assert implementation["type"] == "composite"
    assert implementation["interface"] == "python-module"
    assert implementation["status"] == "candidate"


def test_implementations_for_skill_are_deterministic() -> None:
    registry = UniversalRegistry(REGISTRY_PATH)
    implementations = registry.implementations_for_skill("05-code/code-review")
    assert [item["id"] for item in implementations] == ["implementation/code-reviewer-system"]


def test_unknown_implementation_and_skill_are_rejected() -> None:
    registry = UniversalRegistry(REGISTRY_PATH)
    with pytest.raises(KeyError, match="Unknown implementation"):
        registry.resolve_implementation("implementation/missing")
    with pytest.raises(KeyError, match="Unknown skill"):
        registry.implementations_for_skill("05-code/missing")


def test_registry_initialization_validates_implementation_contract(tmp_path: Path) -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    registry["entities"]["implementations"][0].pop("interface")
    registry_path = tmp_path / "registry" / "universal_registry.json"
    registry_path.parent.mkdir()
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    contract = ROOT / "meta" / "implementation-contract.schema.json"
    contract_target = tmp_path / "meta" / "implementation-contract.schema.json"
    contract_target.parent.mkdir()
    contract_target.write_text(contract.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(Exception):
        UniversalRegistry(registry_path)


def test_verified_implementation_requires_evidence_and_traceable_provenance(tmp_path: Path) -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    implementation = registry["entities"]["implementations"][0]
    implementation["status"] = "verified"
    implementation["evidence"] = []
    registry_path = tmp_path / "registry" / "universal_registry.json"
    registry_path.parent.mkdir()
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    contract = ROOT / "meta" / "implementation-contract.schema.json"
    contract_target = tmp_path / "meta" / "implementation-contract.schema.json"
    contract_target.parent.mkdir()
    contract_target.write_text(contract.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(Exception, match="evidence"):
        UniversalRegistry(registry_path)


def test_verified_implementation_evidence_must_support_record(tmp_path: Path) -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    implementation = registry["entities"]["implementations"][0]
    implementation["status"] = "verified"
    evidence = registry["entities"]["evidence"][0]
    evidence["supports"] = []
    registry_path = tmp_path / "registry" / "universal_registry.json"
    registry_path.parent.mkdir()
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    contract = ROOT / "meta" / "implementation-contract.schema.json"
    contract_target = tmp_path / "meta" / "implementation-contract.schema.json"
    contract_target.parent.mkdir()
    contract_target.write_text(contract.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(ValueError, match="does not support implementation"):
        UniversalRegistry(registry_path)


def test_verified_implementation_with_supporting_evidence_passes(tmp_path: Path) -> None:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    implementation = registry["entities"]["implementations"][0]
    implementation["status"] = "verified"
    registry_path = tmp_path / "registry" / "universal_registry.json"
    registry_path.parent.mkdir()
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    contract = ROOT / "meta" / "implementation-contract.schema.json"
    contract_target = tmp_path / "meta" / "implementation-contract.schema.json"
    contract_target.parent.mkdir()
    contract_target.write_text(contract.read_text(encoding="utf-8"), encoding="utf-8")
    UniversalRegistry(registry_path)
