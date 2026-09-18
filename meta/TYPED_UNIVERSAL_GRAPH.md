# Typed Universal Graph

**Status:** P1.10 vertical-slice contract
**Version:** 1.0

The universal graph is the typed relationship layer over registry entities. Each edge declares source ID/type, target ID/type, relationship type, and provenance.

P1.10 is intentionally additive. It does not replace the existing generated skill graph. The new graph covers the audited universal-registry slice and is validated against registry endpoints at runtime.

## Guarantees

- source and target IDs must resolve to registered entities
- declared endpoint types must match registry entity collections
- self-loops are rejected
- relationship types use the universal vocabulary
- returned edges are deterministically ordered
- every edge carries provenance

The graph is authoritative only for the universal-registry slice represented in `graph/universal_graph.json`. The existing `data/SKILLS_GRAPH.json` remains the generated skill-corpus graph.

## Current vertical slice

`Goal → Capability → Skill → Implementation → Adapter → Protocol`

with evidence and compatibility relationships attached to the audited Code Reviewer slice.

Future phases will expand the graph only when source contracts and evidence support the additional entities and relationships.
