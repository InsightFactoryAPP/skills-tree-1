# Capability↔Adapter Linkage Audit

**Date:** 2026-09-19
**Baseline:** `main` at `5f615fe4870a97b16d42156426067ce659ac43e9`
**Phase:** Phase 2 — Implementation Ontology

## Finding

`Capability.adapters` currently validates only that each referenced Adapter ID exists. The runtime does not verify that the Adapter realizes an Implementation whose canonical Skill belongs to the Capability.

The audited `capability/code-quality` record is internally consistent: `adapter/code-reviewer-mcp` resolves to `implementation/code-reviewer-system`, which resolves to `05-code/code-review`, and that Skill is declared by the Capability.

## Evidence

- `registry/universal_registry.json` contains the Capability, Adapter, Implementation, and Skill records described above.
- `registry/runtime.py` rejects dangling Capability→Adapter IDs but has no semantic Capability→Adapter→Implementation→Skill check.
- `meta/DEVELOPMENT_KNOWLEDGE.md` requires typed, validated, deterministic relationships and rejection of invalid references.

## Smallest vertical slice

1. Runtime: enforce that every Adapter listed by a Capability resolves through its Implementation to a Skill listed by that Capability.
2. Regression: remove the Skill from the Capability while retaining the Adapter and verify registry initialization rejects the relationship.
3. Preserve all existing registry data, compatibility, graph, evidence, Adapter, and MCP behavior.
4. Do not create a numbered P2.3 item or add ecosystem claims.
