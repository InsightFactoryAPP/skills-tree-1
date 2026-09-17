# Current Architecture

This document describes the implementation observed at the 2026-09-17 audit baseline. It is not a target-state design.

## Runtime layers

```text
Data
  meta/GOAL_TAXONOMY.md
  data/SKILLS_GRAPH.json
  benchmarks/INDEX.json

Core implementation
  tools/architect.py
    GoalTaxonomyParser
    SkillsGraph
    EvidenceDeriver
    ExplanationEngine
    SkillScorer
    RecommendationEngine
    BlueprintGenerator
  tools/ranking_calibrator.py

Transport
  api/main.py
  api/routes/*
  api/models.py
  mcp/tools.py
  cli/main.py
```

## Recommendation execution

1. Taxonomy resolves a goal string to a goal ID.
2. Taxonomy returns mapped skills.
3. RecommendationEngine splits skills by priority.
4. SkillsGraph supplies node metadata and dependency/learning-path information.
5. SkillScorer computes priority, centrality, framework, and learning-time components.
6. EvidenceDeriver derives benchmark/goal/dependency/framework evidence.
7. ExplanationEngine derives explanation text from the score components and evidence.
8. RecommendationEngine aggregates confidence and returns the recommendation payload.
9. API applies RankingCalibrator as a second ranking stage and converts the result to Pydantic summaries.

## Blueprint execution

BlueprintGenerator consumes the recommendation result and taxonomy. Architecture selection currently uses a goal-category mapping table. Risk patterns are matched against required skill IDs. Blueprint identity and timestamp are generated at runtime.

## Integration coupling

The CLI and MCP layers currently use FastAPI TestClient for in-process integration. The API dependency module imports core classes directly from `tools.architect.py` and caches process-level instances.

## Current risks

- The main intelligence module is a monolith.
- Goal taxonomy parsing does not fully cover the detailed Level-4 sub-goal format without the runtime adapter introduced in the hardening branch.
- Calibration is separate from the core score and can currently produce ranking/score drift at the API boundary.
- Experience is validated at the API boundary but is not an input to RecommendationEngine.
- Version metadata is fragmented and not returned as a recommendation provenance bundle.
- Blueprint generation is not deterministic in identity/timestamp fields.
