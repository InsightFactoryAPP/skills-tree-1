# Post-P2.2 Graph Relationship Integrity Audit

**Date:** 2026-09-19
**Baseline:** `main` at `264c467e3c0826503d0c63b19db81edf3153ce33`
**Scope:** Typed universal graph semantic integrity after Capability↔Adapter linkage symmetry

## Finding

The universal graph is schema-valid and endpoint-valid, but endpoint typing alone does not prove that a relationship expresses a fact already declared by the canonical registry.

The current graph contained this relationship:

`adapter/code-reviewer-mcp -supported_by_evidence-> compatibility/code-reviewer-mcp-model-context-protocol`

The relationship vocabulary is valid, and both endpoints exist, but `supported_by_evidence` semantically requires an evidence target. The compatibility fact already declares the same evidence in its own `evidence` collection. The graph edge was therefore a semantic mismatch rather than a missing entity or compatibility claim.

## Evidence reviewed

- `meta/universal-graph.schema.json` governs graph shape, endpoint types, relationship vocabulary, and provenance.
- `registry/runtime.py` previously checked graph endpoint identity and self-loops but did not validate relationship semantics against source entity references.
- `registry/universal_registry.json` is the canonical source for goal/capability/skill/implementation/adapter/compatibility/evidence relationships.
- `graph/universal_graph.json` is the current typed graph artifact consumed by `UniversalRegistry`.
- `docs/architecture/UNIVERSAL_REGISTRY_AUDIT.md` defines the typed relationship vocabulary and platform-agnostic entity boundaries.

## Selected vertical slice

Implement only graph relationship semantic integrity:

1. Runtime: validate currently used graph relationships against their canonical source-entity references during registry initialization.
2. Preserve schema validation, endpoint identity validation, self-loop rejection, deterministic ordering, and provenance checks.
3. Correct the existing malformed compatibility/evidence graph edge without adding an entity or compatibility claim.
4. Add real regression tests for invalid relationship targets and undeclared source references.
5. Keep MCP classified as a Protocol.
6. Do not invent a numbered P2.3 roadmap item.

## Relationship rules enforced by this slice

- `goal -> capability` via `requires_capability` must appear in the goal's `capabilities` list.
- `capability -> skill` via `enables_skill` must appear in the capability's `skills` list.
- `skill -> implementation` via `realized_by` must appear in the skill's `implementations` list.
- `implementation -> adapter` via `exposed_through` must reference an Adapter whose `implementation` points back to the Implementation.
- `adapter -> platform/framework/model/protocol/runtime` via `adapted_to` must appear in the Adapter's `targets` list.
- `implementation/adapter/compatibility -> evidence` via `supported_by_evidence` must appear in the source entity's `evidence` list.

Unknown relationship types remain schema-governed rather than receiving undocumented semantic rules in this slice.

## Quality gate

The slice is intentionally limited to runtime enforcement, one corrected graph artifact, focused regression coverage, and audit documentation. No provider/platform/framework/model entity is introduced, no undocumented compatibility claim is made, and no MCP classification is changed.
