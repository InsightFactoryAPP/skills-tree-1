"""Behavioral tests for the real BlueprintGenerator."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.architect import BlueprintGenerator, RecommendationEngine, SkillsGraph
from tools.taxonomy_runtime import RuntimeGoalTaxonomyParser

TAXONOMY_PATH = ROOT / "meta" / "GOAL_TAXONOMY.md"
GRAPH_PATH = ROOT / "data" / "SKILLS_GRAPH.json"
BM_INDEX_PATH = ROOT / "benchmarks" / "INDEX.json"


@pytest.fixture(scope="module")
def stack():
    taxonomy = RuntimeGoalTaxonomyParser(str(TAXONOMY_PATH))
    graph = SkillsGraph(str(GRAPH_PATH))
    benchmark_path = str(BM_INDEX_PATH) if BM_INDEX_PATH.exists() else None
    engine = RecommendationEngine(graph, taxonomy, benchmark_path)
    generator = BlueprintGenerator()
    return engine, generator, taxonomy


def _stable_blueprint(bp):
    """Remove intentionally dynamic identity/timestamp fields for comparison."""
    stable = dict(bp)
    stable.pop("id", None)
    stable.pop("generated_at", None)
    return stable


@pytest.mark.parametrize(
    ("goal", "goal_id", "architecture"),
    [
        ("Coding Agent", "G01", "Single-Agent"),
        ("Browser Agent", "G03", "Single-Agent"),
        ("RAG Assistant", "G04", "RAG"),
        ("Knowledge Management", "G05", "Knowledge-Graph"),
        ("Workflow Automation", "G06", "Workflow"),
        ("Multi-Agent Systems", "G08", "Multi-Agent"),
        ("Data Analysis", "G10", "Data-Pipeline"),
        ("Evaluation Systems", "G11", "Evaluation"),
    ],
)
def test_real_blueprint_generation(stack, goal, goal_id, architecture):
    engine, generator, taxonomy = stack
    recommendation = engine.recommend(goal)

    assert "error" not in recommendation
    blueprint = generator.generate(goal, recommendation, taxonomy)

    assert blueprint["goal_id"] == goal_id
    assert blueprint["architecture_type"] == architecture
    assert blueprint["required_skills"] or blueprint["optional_skills"]
    assert blueprint["learning_path"]
    assert isinstance(blueprint["risks"], list)
    json.dumps(blueprint)


def test_blueprint_is_deterministic_except_identity_fields(stack):
    engine, generator, taxonomy = stack
    recommendation = engine.recommend("RAG Assistant")

    first = generator.generate("RAG Assistant", recommendation, taxonomy)
    second = generator.generate("RAG Assistant", recommendation, taxonomy)

    assert _stable_blueprint(first) == _stable_blueprint(second)


def test_blueprint_required_skills_trace_back_to_recommendation(stack):
    engine, generator, taxonomy = stack
    recommendation = engine.recommend("Coding Agent")
    blueprint = generator.generate("Coding Agent", recommendation, taxonomy)

    expected_ids = [s["id"] for s in recommendation["required_skills"]]
    actual_ids = [s["id"] for s in blueprint["required_skills"]]

    assert actual_ids == expected_ids
    assert all("score_breakdown" in skill for skill in blueprint["required_skills"])
    assert all("evidence" in skill for skill in blueprint["required_skills"])


def test_blueprint_skill_ranks_are_contiguous(stack):
    engine, generator, taxonomy = stack
    recommendation = engine.recommend("Browser Agent")
    blueprint = generator.generate("Browser Agent", recommendation, taxonomy)

    ranks = [skill["rank"] for skill in blueprint["required_skills"]]
    assert ranks == list(range(1, len(ranks) + 1))


def test_blueprint_unknown_goal_does_not_fabricate_output(stack):
    engine, generator, taxonomy = stack
    recommendation = engine.recommend("not-a-real-goal")

    assert "error" in recommendation
    with pytest.raises(KeyError):
        generator.generate("not-a-real-goal", recommendation, taxonomy)


def test_blueprint_schema_projection_is_json_serializable(stack):
    engine, generator, taxonomy = stack
    recommendation = engine.recommend("Multi-Agent Systems")
    blueprint = generator.generate("Multi-Agent Systems", recommendation, taxonomy)

    projection = {
        "goal_id": blueprint["goal_id"],
        "architecture_type": blueprint["architecture_type"],
        "required_skills": blueprint["required_skills"],
        "optional_skills": blueprint["optional_skills"],
        "learning_path": blueprint["learning_path"],
        "risks": blueprint["risks"],
    }
    encoded = json.dumps(projection, sort_keys=True)
    assert json.loads(encoded) == projection
