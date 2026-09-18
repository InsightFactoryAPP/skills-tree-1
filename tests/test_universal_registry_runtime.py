import json
from pathlib import Path

import pytest

from registry.runtime import UniversalRegistry


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "universal_registry.json"


def test_registry_resolves_goal_to_capability_to_canonical_skills() -> None:
    registry = UniversalRegistry(REGISTRY)

    skills = registry.skills_for_goal("goal/research-and-analysis")

    assert [skill["id"] for skill in skills] == [
        "03-memory/rag",
        "11-web/web-search",
    ]
    assert all(skill["canonical"] is True for skill in skills)


def test_registry_resolution_is_deterministic() -> None:
    registry = UniversalRegistry(REGISTRY)

    first = registry.skills_for_goal("goal/research-and-analysis")
    second = registry.skills_for_goal("goal/research-and-analysis")

    assert first == second


def test_registry_rejects_unknown_goal() -> None:
    registry = UniversalRegistry(REGISTRY)

    with pytest.raises(KeyError, match="Unknown goal"):
        registry.resolve_goal("goal/does-not-exist")


def test_registry_rejects_dangling_references(tmp_path: Path) -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    data["entities"]["goals"][0]["capabilities"].append("capability/missing")
    broken = tmp_path / "broken.json"
    broken.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError, match="Dangling capability reference"):
        UniversalRegistry(broken)


def test_registry_provenance_points_to_existing_repository_sources() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))

    for entity_type in ("goals", "capabilities", "skills"):
        for entity in data["entities"][entity_type]:
            source = entity["provenance"]["source"]
            assert (ROOT / source).is_file(), source


def test_first_implementation_slice_links_to_canonical_skill_and_evidence() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    implementations = {item["id"]: item for item in data["entities"]["implementations"]}
    evidence = {item["id"]: item for item in data["entities"]["evidence"]}
    skills = {item["id"]: item for item in data["entities"]["skills"]}

    implementation = implementations["implementation/code-reviewer-system"]
    assert implementation["skill"] == "05-code/code-review"
    assert skills[implementation["skill"]]["canonical"] is True
    assert implementation["status"] == "candidate"
    assert implementation["provenance"]["source"] == "systems/code-reviewer.md"
    assert implementation["evidence"] == ["evidence/code-reviewer-system-source"]
    assert evidence["evidence/code-reviewer-system-source"]["source"] == "systems/code-reviewer.md"


def test_implementation_source_exists() -> None:
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    implementation = data["entities"]["implementations"][0]
    assert (ROOT / implementation["provenance"]["source"]).is_file()
