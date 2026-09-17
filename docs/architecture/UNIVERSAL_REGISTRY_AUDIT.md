# Universal Agent Skills Registry — Architecture Audit

**Audit date:** 2026-09-17  
**Baseline:** `main` at `0eb0d38b79d57a31a77a70f5b9372cf9e7b09ad7`  
**Mission:** evolve Skills Tree into a platform-agnostic Universal Agent Skills & Capability Registry.

## Executive finding

The repository already contains most of the primitives required for the registry: a skill corpus, JSON Schema for skill frontmatter, a goal taxonomy, a dependency graph, framework/model mappings, benchmarks, recommendation and blueprint engines, API/CLI/MCP surfaces, and CI validation.

The principal architectural gap is not missing content. It is **entity separation and machine-readable interoperability**. The current data model primarily treats the skill as the central entity and attaches framework/model metadata directly to it. The target model requires explicit separation of Capability, Skill, Implementation, Platform, Framework, Model, Tool, Adapter, Evidence, Goal, and Architecture.

No runtime rewrite is justified by this audit. The smallest useful P1 slice is a versioned universal registry contract that can be introduced alongside the existing skill schema and consumed incrementally by future adapters and services.

## Findings

| Area | Current state | Gap | Priority |
|---|---|---|---|
| Skill | `meta/skill-schema.json` defines frontmatter; current files use title/category/level/stability/etc. | Skill identity is still coupled to category paths and optional framework metadata. | P1 |
| Goal | `meta/GOAL_TAXONOMY.md` defines 12 goal categories, 48 sub-goals and capability/skill mappings. | Goal data is Markdown-first rather than a stable machine-readable entity contract. | P1 |
| Capability | Capabilities exist inside the goal taxonomy. | No first-class capability registry/entity contract. | P1 |
| Implementation | Concrete examples/framework references exist in skills. | No first-class implementation entity; implementation and framework are conflated in places. | P1 |
| Platform | Platforms are described across framework/model references. | No first-class platform registry or compatibility contract. | P1 |
| Framework | `meta/frameworks.md` is a curated catalog. | Framework, platform, protocol and model are represented in one human-readable reference rather than a typed registry. | P1 |
| Adapter | Existing runtime taxonomy adapter is a compatibility mechanism. | No universal adapter contract connecting canonical skills to platform implementations. | P1 |
| Model | Models are listed in `meta/frameworks.md` and skill framework sections. | No stable model entity or capability compatibility contract. | P1 |
| Tool | Tool-use skills and integrations exist. | Tool identity is not consistently separated from implementations. | P1 |
| Evidence | Benchmarks and derived evidence exist in the recommendation pipeline. | Provenance is not a universal cross-entity contract. | P1 |
| Graph | `data/SKILLS_GRAPH.json` is canonical and synchronized with the UI dataset. | Graph is predominantly skill-to-skill; cross-entity typed edges are not yet universal. | P1 |
| Recommendation | RecommendationEngine, scorer, calibrator and explanation components exist. | Pipeline still assumes skill-centric inputs and does not yet consume universal compatibility entities. | P1 |
| Blueprint | BlueprintGenerator exists and uses goal-category mappings. | Capability/implementation/platform inference is not yet the primary architecture path. | P1 |
| Output contract | `meta/ARCHITECTURE_OUTPUT_SCHEMA.md` is currently empty. | No machine-readable universal architecture/registry output contract. | P1 |
| Tests | Real recommendation, blueprint, graph and API behavior is covered. | No regression contract for the new universal entity vocabulary. | P1 |
| Framework coverage | `meta/frameworks.md` includes many frameworks, platforms and models. | Coverage is curated and human-readable; compatibility semantics are not typed. | P2 |

## Entity boundaries

The canonical vocabulary for the next phases is:

```text
Goal
  │ requires
  ▼
Capability
  │ enabled-by
  ▼
Skill
  │ realized-by
  ▼
Implementation
  │ exposed-through
  ▼
Tool / Runtime
  │ adapted-to
  ▼
Platform / Framework
  │ uses
  ▼
Model
```

Cross-cutting entities:

```text
Evidence ───────► Goal / Capability / Skill / Implementation / Platform / Model
Benchmark ──────► Skill / Implementation / Model
Architecture ───► Capability / Skill / Implementation / Platform / Tool
Dependency ────► Skill / Implementation / Tool
Constraint ────► Goal / Skill / Implementation / Platform
```

## Existing data preservation

The current skill corpus remains the canonical content source during migration. Existing frontmatter fields remain valid. The universal contract adds normalized references rather than requiring an immediate migration of all skill files.

The existing goal taxonomy remains the source for goal and capability discovery until a structured goal registry is introduced. The existing framework catalog remains the source for initial platform/framework/model mappings until those records become typed registry entities.

The canonical graph remains `data/SKILLS_GRAPH.json`; generated compatibility artifacts must continue to be derived from it.

## Duplication risks

The audit identified four high-risk duplication patterns to prevent during expansion:

1. Platform-specific copies of the same canonical skill.
2. Framework names used as substitutes for platform or implementation identities.
3. Model capability claims embedded directly in skill prose without provenance.
4. Human-readable Markdown mappings becoming an implicit API contract.

The registry contract must make these distinctions explicit before adding large volumes of new platform coverage.

## Missing graph relationships

The current graph should eventually support typed relationships beyond prerequisite/related skill edges:

- `requires_capability`
- `enables_skill`
- `realized_by`
- `implemented_with`
- `exposed_by`
- `adapted_to`
- `supported_by_model`
- `alternative_to`
- `enhances`
- `unlocks`
- `supported_by_evidence`
- `validated_by_benchmark`
- `constrained_by`
- `composes_with`

These must be introduced only after graph schema validation and deterministic generation rules are defined.

## Smallest justified P1 vertical slice

1. Define the universal entity vocabulary and relationship boundaries.
2. Add a machine-readable registry contract without changing existing skill files.
3. Add a real regression test proving the contract contains the required entity types, relationship vocabulary, and platform-agnostic skill rule.
4. Keep the existing recommendation and blueprint runtime unchanged.
5. Use the contract as the compatibility boundary for the next incremental implementation slices.

## Deferred work

The following are deliberately not implemented in this slice:

- bulk migration of existing skills;
- creation of thousands of new skills;
- new platform-specific skill taxonomies;
- replacing the recommendation engine;
- replacing the graph generator;
- semantic embeddings;
- database migration;
- external API versioning.

Those changes require subsequent audited slices with behavioral tests.
