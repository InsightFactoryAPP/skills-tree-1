# Skills Tree — Autonomous Engineering Audit

**Audit baseline:** `main` at `7d00d0e034b4ba7edfacc512c2794080f7fb8a62`
**Audit branch:** `agent/production-hardening-20260917`
**Date:** 2026-09-17

## Executive assessment

The repository contains a substantial working recommendation/API/CLI/MCP stack, but the current production boundary is weaker than the project documentation implies. The highest-value issues are correctness and behavioral-test integrity, not a wholesale rewrite.

## Architecture map

```text
Taxonomy (meta/GOAL_TAXONOMY.md)
        |
        v
GoalTaxonomyParser -----> RecommendationEngine <----- SkillsGraph (data/SKILLS_GRAPH.json)
        |                         |
        |                         +---- EvidenceDeriver <----- benchmarks/INDEX.json
        |                         +---- SkillScorer
        |                         +---- ExplanationEngine
        |                         +---- learning-path traversal
        v                         v
     API routes --------------> BlueprintGenerator
        ^                         |
        |                         v
      MCP tools               Blueprint JSON
        ^
        |
      CLI (currently via FastAPI TestClient)
```

## Runtime flow findings

1. `api/dependencies.py` constructs cached taxonomy, graph, recommendation engine, calibrator, and blueprint generator instances.
2. `POST /recommend` calls the real `RecommendationEngine`, then applies a separate calibration pass before building API summaries.
3. `POST /blueprint` calls the recommendation engine and then `BlueprintGenerator`.
4. MCP currently delegates to the API layer through an in-process `TestClient`.
5. CLI also delegates to the API layer through an in-process `TestClient`.

## P0/P1/P2/P3 findings

| ID | Severity | Finding | Evidence | Impact |
|---|---|---|---|---|
| AUD-001 | P1 | Parent-goal resolution does not reliably consume the Level-4 sub-goal skill lists. | Taxonomy stores most detailed mappings under `#### Gxx.y` sections, while `GoalTaxonomyParser._parse_skill_mappings()` primarily scans `###` mapping sections and `skills_for()` only falls back from a sub-goal to its parent. | A canonical goal such as `Coding Agent` can resolve successfully while producing an incomplete/empty skill set. |
| AUD-002 | P1 | Recommendation tests are synthetic rather than behavioral. | `tests/test_recommendations.py` constructs dictionaries/lists directly and never instantiates `RecommendationEngine`. | Core recommendation behavior can regress while the suite remains green. |
| AUD-003 | P1 | Blueprint tests are synthetic rather than behavioral. | `tests/test_blueprints.py` constructs blueprint dictionaries directly and never calls `BlueprintGenerator`. | Blueprint generation regressions can pass CI unnoticed. |
| AUD-004 | P1 | Calibration can reorder skills using positional synthetic base scores when passed skill IDs, while API summaries retain the pre-calibration score. | `RankingCalibrator._normalise_input()` assigns `10.0 - index` to ID-only inputs; `/recommend` calls `calibrate_ids()` and `_to_summary()` reads the original `s["score"]`. | Ranking and displayed score can describe different orderings; calibration is not traceable to the score shown to clients. |
| AUD-005 | P1 | Consistency scenario metadata is stale relative to the current goal taxonomy. | `evaluation/consistency_suite.json` maps Browser Agent to `G02`, Memory Agent to `G03`, and other goals that no longer match the current 12-category taxonomy. | A parity suite can validate the wrong semantic contract. |
| AUD-006 | P1 | Experience level is accepted by the API contract but is not used by `RecommendationEngine.recommend()`. | Request model validates `experience`, but the engine signature only accepts `goal_query`. | User context promised by the public API does not affect recommendation behavior. |
| AUD-007 | P1 | Time-budget filtering is presentation-layer logic and only filters required skills. | `api/routes/recommend.py` filters `required_skills` after calibration and leaves optional skills unchanged. | Budget-constrained output can exceed the stated budget semantically and required/optional behavior is inconsistent. |
| AUD-008 | P2 | Blueprint IDs and timestamps are generated from wall-clock time. | `BlueprintGenerator.generate()` uses `datetime.now()` for both `id` and `generated_at`. | Blueprint content is not fully reproducible even when all inputs are identical. |
| AUD-009 | P2 | Framework evidence is goal-level maximum framework strength, not skill-level framework evidence. | `EvidenceDeriver.derive()` receives `top_fw_stars` and applies it to each skill. | Explanations can imply skill-level framework alignment that is not actually evidenced at skill level. |
| AUD-010 | P2 | CLI and MCP use `FastAPI TestClient` as their application integration mechanism. | `cli/main.py` and `mcp/tools.py` construct in-process `TestClient` instances. | Domain/application logic is coupled to the HTTP transport and harder to test independently. |
| AUD-011 | P2 | API uses wildcard CORS and exposes exception strings through the 404/422/500 error contracts. | `api/main.py` sets `allow_origins=["*"]`, wildcard methods/headers, and serializes `str(exc)` as `detail`. | Production hardening and information-disclosure risk. |
| AUD-012 | P2 | Calibration tables are hardcoded Python dictionaries. | `tools/ranking_calibrator.py` defines global, goal, and keyword adjustment tables in source. | Calibration changes are not independently versioned or traceable as data. |
| AUD-013 | P2 | Core intelligence remains concentrated in `tools/architect.py`. | The module contains parser, graph, evidence, explanation, scoring, recommendation, and blueprint responsibilities. | High coupling and change-risk; extraction should follow a behavioral safety net. |
| AUD-014 | P3 | Repository contains a large number of historical/sprint documents and generated artifacts. | Tree inspection shows extensive `meta/`, `evaluation/`, workflow, and generated-data surfaces. | Documentation/source-of-truth drift is harder to detect. |

## Source-of-truth matrix

| Domain | Current authoritative source | Assessment |
|---|---|---|
| Skills | `skills/` | Primary content source |
| Goals | `meta/GOAL_TAXONOMY.md` | Primary taxonomy source; parser coverage needs hardening |
| Graph | `data/SKILLS_GRAPH.json` | Generated artifact; metadata says schema 3.1 |
| Graph generation | `tools/build_graph.py` | Generator source |
| Benchmarks | `benchmarks/INDEX.json` | Runtime evidence source |
| Calibration | `tools/ranking_calibrator.py` | Hardcoded source; should become versioned data |
| API contract | `api/models.py` | Pydantic contract |
| Blueprint contract | API model + generator output | No dedicated strict schema enforcement |
| Package version | `pyproject.toml` | `1.46.0` |

## Versioning observations

- Package version: `1.46.0`.
- Graph schema: `3.1` in `SKILLS_GRAPH.json` metadata.
- Taxonomy document is dated 2026-06-14 and describes itself as complete.
- Architect source comments still reference older graph schema terminology in places.
- Calibration has no runtime-exposed version.
- Recommendation/API response does not expose a traceable taxonomy/graph/benchmark/calibration version bundle.

## CI assessment

The repository has strong build-oriented workflow coverage, including wheel content verification and clean-install smoke tests. The clean-install workflow explicitly runs `pytest tests/` and API/CLI smoke tests. However, workflow presence is not proof of current green status. The latest remote workflow evidence inspected during this audit includes successful scheduled CodeQL runs for the audit baseline; a current full build/test run was not available from the GitHub connector during this audit.

## Security assessment

The workflows inspected use explicit read-only `contents` permissions in the build/verification paths, which is a positive baseline. Remaining concerns are API wildcard CORS, exception detail exposure, dependency/supply-chain policy depth, and ensuring every workflow maintains least privilege.

## Immediate execution plan

### P1 vertical slice

1. Establish real RecommendationEngine behavioral tests.
2. Establish real BlueprintGenerator behavioral tests.
3. Add deterministic/invariant assertions without overfitting floating-point values.
4. Add a regression test for canonical parent-goal skill resolution.
5. Route production taxonomy loading through a compatibility-preserving runtime adapter while the monolith remains intact.
6. Validate the branch through GitHub CI before broader extraction.

### Next P1 slices

- Correct calibration semantics and expose calibrated scores/version.
- Reconcile consistency-suite goal IDs with the authoritative taxonomy.
- Make experience and time constraints real application-level inputs.
- Extract domain/application services incrementally.
- Replace static goal-to-architecture selection with capability/graph-derived inference behind a compatibility fallback.
