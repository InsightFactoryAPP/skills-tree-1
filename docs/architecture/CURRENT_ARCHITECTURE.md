# Current Architecture

This document describes the implementation observed at the 2026-09-17 audit baseline. It is not a target-state design.

## Runtime layers

```text
Data
  meta/GOAL_TAXONOMY.md
  meta/skill-schema.json
  meta/frameworks.md
  data/SKILLS_GRAPH.json
  benchmarks/INDEX.json

Core implementation
  tools/architect.py
    GoalTaxonomyParser / RuntimeGoalTaxonomyParser
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

## Current universal-registry position

The repository is currently skill-centric. A JSON Schema exists for skill frontmatter, a Markdown goal taxonomy contains goal → capability → skill mappings, and `meta/frameworks.md` provides a curated framework/platform/model reference. These are useful existing sources, but Capability, Implementation, Platform, Framework, Model, Tool, and Adapter are not yet first-class registry entities.

The new `meta/universal-registry.schema.json` defines the intended cross-entity vocabulary without changing existing runtime contracts. It is the first compatibility boundary for incremental migration.

## Recommendation execution

1. Taxonomy resolves a goal string to a goal ID.
2. Taxonomy returns mapped skills.
3. RecommendationEngine splits skills by priority.
4. SkillsGraph supplies node metadata and dependency/learning-path information.
5. SkillScorer computes recommendation components.
6. EvidenceDeriver derives benchmark/goal/dependency/framework evidence.
7. ExplanationEngine derives explanation text from score components and evidence.
8. RecommendationEngine aggregates confidence and returns the recommendation payload.
9. API applies the ranking calibration boundary and converts the result to Pydantic summaries.

## Blueprint execution

BlueprintGenerator consumes the recommendation result and taxonomy. Architecture selection is still primarily driven by goal-category mappings, with risk patterns matched against required skill IDs. Blueprint output contains runtime-generated identity/timing fields and therefore is not yet a fully deterministic universal architecture artifact.

## Existing hardening completed before the universal-registry migration

- Recommendation and blueprint tests exercise real behavior rather than synthetic placeholders.
- Runtime taxonomy compatibility is covered by the shared runtime parser.
- API ranking/calibration ordering drift was corrected at the API boundary.
- Graph generation validates the regenerated canonical dataset.
- Graph UI data is synchronized from `data/SKILLS_GRAPH.json` by the graph build workflow.
- Workflow permissions and security checks were hardened.

## Remaining architectural gaps

- The core intelligence implementation remains concentrated in `tools/architect.py`.
- Capability is represented inside the goal taxonomy rather than as a first-class registry entity.
- Implementation, Tool, Platform, Framework, and Model identities are not consistently separated.
- Adapter contracts for platform/framework integration do not yet exist as a universal machine-readable layer.
- Provenance is derived for recommendations but is not yet a cross-entity registry contract.
- The graph remains predominantly skill-centric and needs typed cross-entity relationships.
- `meta/ARCHITECTURE_OUTPUT_SCHEMA.md` is currently empty and must be replaced by a versioned output contract in a later P1 slice.
- `meta/frameworks.md` is a curated reference with a documented April 2026 freshness boundary; it is not yet a versioned registry.
- The existing package metadata still describes the product primarily as an Architect recommendation engine; this is a packaging/positioning gap rather than a runtime correctness issue.

## Migration constraint

Do not bulk-migrate the existing skill corpus or introduce platform-specific duplicate skills until the universal entity contract, typed graph relationships, provenance rules, and compatibility semantics have behavioral coverage.
