#!/usr/bin/env python3
"""FastAPI dependency-injection providers."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import sys


def _repo_root() -> Path:
    here = Path(__file__).resolve().parent
    for candidate in [here, here.parent, here.parent.parent]:
        if (candidate / "tools" / "architect.py").exists():
            return candidate
    return here.parent


ROOT = _repo_root()
TAXONOMY_PATH = ROOT / "meta" / "GOAL_TAXONOMY.md"
GRAPH_PATH = ROOT / "data" / "SKILLS_GRAPH.json"
BM_INDEX_PATH = ROOT / "benchmarks" / "INDEX.json"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Load the runtime compatibility module first. It patches the legacy parser's
# Level-4 mapping and alias behavior, so every application surface shares one
# taxonomy implementation rather than maintaining divergent parser semantics.
import tools.taxonomy_runtime as _taxonomy_runtime  # noqa: F401
from tools.architect import GoalTaxonomyParser, SkillsGraph, RecommendationEngine, BlueprintGenerator
from tools.ranking_calibrator import RankingCalibrator


@lru_cache(maxsize=1)
def get_taxonomy() -> GoalTaxonomyParser:
    if not TAXONOMY_PATH.exists():
        raise FileNotFoundError(f"GOAL_TAXONOMY.md not found at {TAXONOMY_PATH}")
    return GoalTaxonomyParser(str(TAXONOMY_PATH))


@lru_cache(maxsize=1)
def get_graph() -> SkillsGraph:
    if not GRAPH_PATH.exists():
        raise FileNotFoundError(f"SKILLS_GRAPH.json not found at {GRAPH_PATH}")
    return SkillsGraph(str(GRAPH_PATH))


@lru_cache(maxsize=1)
def get_engine() -> RecommendationEngine:
    bm_path = str(BM_INDEX_PATH) if BM_INDEX_PATH.exists() else None
    return RecommendationEngine(get_graph(), get_taxonomy(), bm_path)


@lru_cache(maxsize=1)
def get_calibrator() -> RankingCalibrator:
    return RankingCalibrator()


@lru_cache(maxsize=1)
def get_blueprint_generator() -> BlueprintGenerator:
    return BlueprintGenerator()
