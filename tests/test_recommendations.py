"""Behavioral tests for the real recommendation engine.

These tests intentionally execute the production taxonomy, graph, scoring,
evidence, and explanation pipeline. They do not construct expected
recommendation objects merely to validate their own fields.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.architect import RecommendationEngine, SkillsGraph
from tools.taxonomy_runtime import RuntimeGoalTaxonomyParser

TAXONOMY_PATH = ROOT / "meta" / "GOAL_TAXONOMY.md"
GRAPH_PATH = ROOT / "data" / "SKILLS_GRAPH.json"
BM_INDEX_PATH = ROOT / "benchmarks" / "INDEX.json"


@pytest.fixture(scope="module")
def engine() -> RecommendationEngine:
    taxonomy = RuntimeGoalTaxonomyParser(str(TAXONOMY_PATH))
    graph = SkillsGraph(str(GRAPH_PATH))
    benchmark_path = str(BM_INDEX_PATH) if BM_INDEX_PATH.exists() else None
    return RecommendationEngine(graph, taxonomy, benchmark_path)


@pytest.mark.parametrize(
    ("goal", "expected_goal_id"),
    [
        ("Coding Agent", "G01"),
        ("Research Agent", "G02"),
        ("Browser Agent", "G03"),
        ("RAG Assistant", "G04"),
        ("Knowledge Management", "G05"),
        ("Workflow Automation", "G06"),
        ("Customer Support", "G07"),
        ("Multi-Agent Systems", "G08"),
        ("Voice Agent", "G09"),
        ("Data Analysis", "G10"),
        ("Evaluation Systems", "G11"),
        ("Content Generation", "G12"),
    ],
)
def test_canonical_goals_produce_real_recommendations(engine, goal, expected_goal_id):
    result = engine.recommend(goal)

    assert "error" not in result
    assert result["goal_id"] == expected_goal_id
    assert result["taxonomy_skills"]
    assert result["required_skills"] or result["optional_skills"]

    ids = [s["id"] for s in result["required_skills"] + result["optional_skills"]]
    assert len(ids) == len(set(ids))


def test_subgoal_resolution_uses_detailed_skill_mapping(engine):
    result = engine.recommend("G01.1")

    assert "error" not in result
    assert result["goal_id"] == "G01.1"
    assert {s["id"] for s in result["taxonomy_skills"]} >= {
        "code-generation",
        "prompt-engineering",
        "tool-use",
    }


def test_parent_goal_aggregates_subgoal_mappings(engine):
    result = engine.recommend("G01")
    ids = {s["id"] for s in result["taxonomy_skills"]}

    assert len(ids) >= 5
    assert {"code-generation", "code-analysis", "planning"}.issubset(ids)


def test_recommendation_contains_real_scoring_and_evidence(engine):
    result = engine.recommend("Coding Agent")
    skills = result["required_skills"] + result["optional_skills"]

    assert skills
    for skill in skills:
        assert isinstance(skill["score"], (int, float))
        assert "score_breakdown" in skill
        assert "evidence" in skill
        assert "confidence" in skill
        assert 0.0 <= skill["confidence"] <= 1.0
        assert skill["explanation"]


def test_required_and_optional_sets_follow_taxonomy_priority(engine):
    result = engine.recommend("RAG Assistant")

    assert result["required_skills"]
    assert result["optional_skills"]
    assert all(
        s["id"] in {x["id"] for x in result["taxonomy_skills"]}
        for s in result["required_skills"] + result["optional_skills"]
    )


def test_rank_order_is_deterministic_and_monotonic(engine):
    first = engine.recommend("Browser Agent")
    second = engine.recommend("Browser Agent")

    def projection(result):
        return [
            (s["id"], s["rank"], s["score"], s["confidence"])
            for s in result["required_skills"] + result["optional_skills"]
        ]

    first_projection = projection(first)
    second_projection = projection(second)
    assert first_projection == second_projection

    ranks = [row[1] for row in first_projection]
    assert ranks == list(range(1, len(ranks) + 1))


def test_unknown_goal_fails_cleanly(engine):
    result = engine.recommend("definitely-not-a-real-goal")

    assert "error" in result
    assert "Unknown goal" in result["error"]


def test_learning_path_is_unique_and_json_safe(engine):
    import json

    result = engine.recommend("Coding Agent")
    path = result["learning_path"]

    assert path
    path_ids = [node["id"] for node in path]
    assert len(path_ids) == len(set(path_ids))
    json.dumps(path)


def test_real_api_recommendation_contract():
    from fastapi.testclient import TestClient
    from api.main import app

    response = TestClient(app).post(
        "/recommend",
        json={"goal": "Coding Agent", "experience": "intermediate"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["goal_id"] == "G01"
    assert data["required_skills"]
    assert data["calibration_applied"] is True


def test_api_rejects_unknown_goal():
    from fastapi.testclient import TestClient
    from api.main import app

    response = TestClient(app).post(
        "/recommend",
        json={"goal": "definitely-not-a-real-goal", "experience": "intermediate"},
    )

    assert response.status_code == 404
