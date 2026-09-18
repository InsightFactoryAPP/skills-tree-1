from pathlib import Path

from registry.recommendation import RegistryRecommendationEngine
from registry.runtime import UniversalRegistry
from tools.architect import GoalTaxonomyParser, SkillsGraph

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = UniversalRegistry(ROOT / "registry" / "universal_registry.json")
ENGINE = RegistryRecommendationEngine(
    SkillsGraph(str(ROOT / "data" / "SKILLS_GRAPH.json")),
    GoalTaxonomyParser(str(ROOT / "meta" / "GOAL_TAXONOMY.md")),
    str(ROOT / "benchmarks" / "INDEX.json"),
    registry=REGISTRY,
)


def test_recommendation_exposes_registry_eligibility_without_changing_legacy_candidates():
    result = ENGINE.recommend("Coding Agent")
    assert "error" not in result
    assert result["required_skills"]
    assert result["eligibility"]["candidates"] == [
        {
            "id": "05-code/code-review",
            "status": "eligible",
            "reasons": [],
        }
    ]


def test_target_compatibility_uses_registered_adapter_evidence():
    result = ENGINE.recommend(
        "Coding Agent",
        target={"type": "protocol", "id": "protocol/model-context-protocol"},
    )
    assert "error" not in result
    assert result["eligibility"]["candidates"] == [
        {
            "id": "adapter/code-reviewer-mcp",
            "status": "conditional",
            "reasons": [
                {
                    "code": "compatibility_conditional",
                    "message": "Compatibility is conditional for adapter/code-reviewer-mcp and protocol/protocol/model-context-protocol",
                }
            ],
        }
    ]
    assert any(skill["id"] == "05-code/code-review" for skill in result["required_skills"])


def test_target_incompatible_registered_adapter_is_filtered_before_ranking():
    data = REGISTRY.data
    original = data["entities"]["compatibilities"][0]["status"]
    data["entities"]["compatibilities"][0]["status"] = "incompatible"
    try:
        result = ENGINE.recommend(
            "Coding Agent",
            target={"type": "protocol", "id": "protocol/model-context-protocol"},
        )
        assert all(skill["id"] != "05-code/code-review" for skill in result["required_skills"])
        assert result["eligibility"]["candidates"][0]["status"] == "ineligible"
    finally:
        data["entities"]["compatibilities"][0]["status"] = original
