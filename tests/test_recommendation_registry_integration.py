from pathlib import Path

from registry.recommendation import RegistryRecommendationEngine
from registry.runtime import UniversalRegistry
from tools.architect import SkillsGraph
from tools.taxonomy_runtime import RuntimeGoalTaxonomyParser

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = UniversalRegistry(ROOT / "registry" / "universal_registry.json")
ENGINE = RegistryRecommendationEngine(
    SkillsGraph(str(ROOT / "data" / "SKILLS_GRAPH.json")),
    RuntimeGoalTaxonomyParser(str(ROOT / "meta" / "GOAL_TAXONOMY.md")),
    str(ROOT / "benchmarks" / "INDEX.json"),
    registry=REGISTRY,
)


def test_recommendation_exposes_registry_eligibility_without_changing_legacy_candidates():
    result = ENGINE.recommend("Research Agent")
    assert "error" not in result
    assert result["required_skills"]
    assert result["eligibility"]["candidates"] == [
        {
            "id": "11-web/web-search",
            "status": "eligible",
            "reasons": [],
        }
    ]
    assert any(skill["id"] == "web-search" for skill in result["required_skills"])


def test_target_compatibility_uses_registered_adapter_evidence():
    target = {"type": "protocol", "id": "protocol/model-context-protocol"}
    candidate_ids, mapping = ENGINE._eligibility_candidates(["05-code/code-review"], target)
    eligibility = ENGINE.eligibility.evaluate(candidate_ids, target=target)

    assert candidate_ids == ["adapter/code-reviewer-mcp"]
    assert mapping == {"adapter/code-reviewer-mcp": {"05-code/code-review"}}
    assert eligibility["candidates"] == [
        {
            "id": "adapter/code-reviewer-mcp",
            "status": "conditional",
            "reasons": [
                {
                    "code": "compatibility_conditional",
                    "message": "Compatibility is conditional for adapter/code-reviewer-mcp and protocol/model-context-protocol",
                }
            ],
        }
    ]


def test_target_incompatible_registered_candidate_is_filtered_before_final_result():
    result = ENGINE.recommend(
        "Research Agent",
        target={"type": "protocol", "id": "protocol/model-context-protocol"},
    )

    assert all(skill["id"] != "web-search" for skill in result["required_skills"])
    assert result["eligibility"]["candidates"] == [
        {
            "id": "11-web/web-search",
            "status": "ineligible",
            "reasons": [
                {
                    "code": "no_implementation",
                    "message": "Skill has no registered implementation: 11-web/web-search",
                },
                {
                    "code": "compatibility_missing",
                    "message": "No evidence-backed compatibility fact for 11-web/web-search and protocol/model-context-protocol",
                },
            ],
        }
    ]


def test_canonical_skill_id_normalizes_to_registry_id():
    assert ENGINE._normalize_skill_id("11-web/web-search") == "11-web/web-search"
    assert ENGINE._normalize_skill_id("web-search") == "11-web/web-search"
    assert ENGINE._normalize_skill_id("not-registered") is None
