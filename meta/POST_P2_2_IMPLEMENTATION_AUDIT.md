# Post-P2.2 Implementation Ontology Architecture Audit

**Date:** 2026-09-18
**Baseline:** `main` at `31cabe75eae7f26d73a7504ad3b83043d6fe79af`
**Scope:** Implementation Ontology after P2.2

## Audit conclusion

P2.2 correctly establishes typed runtime access, deterministic Implementation lookup, Skill-to-Implementation lookup, and schema validation. The remaining high-value contract gap is lifecycle enforcement: the normative Implementation Contract defines `verified` as a state whose claims have passed evidence and validation gates, but the machine-readable contract previously allowed a `verified` record with an empty evidence list, and the runtime did not verify that referenced evidence actually supports the Implementation.

The current production registry record is `candidate`, so this gap does not alter existing registry behavior. It is nevertheless a correctness boundary because a future record could otherwise be marked `verified` without the minimum evidence relationship required by the governing contract.

## Evidence reviewed

- `meta/IMPLEMENTATION_CONTRACT.md` defines `verified` as a state requiring applicable evidence/validation gates and states that evidence supports behavior, compatibility, quality, reliability, or operational-status claims.
- `meta/implementation-contract.schema.json` validates lifecycle values but previously imposed no minimum evidence requirement for `verified` and did not require a traceable provenance source in that state.
- `registry/universal_registry.json` contains one real Implementation, `implementation/code-reviewer-system`, currently `candidate`, with two evidence records that explicitly support it.
- `registry/runtime.py` validates schema shape and reference integrity, but previously did not enforce lifecycle-specific evidence gates.
- `tests/test_registry_implementation_runtime.py` covered schema rejection and deterministic lookup, but had no regression test for invalid `verified` lifecycle state.

## Rejected candidates

- Skill/Implementation bidirectional linkage is a real consistency refinement, but the current runtime's canonical Implementation lookup is based on the Implementation's explicit `skill` field and the existing registry fixture is symmetric. It is lower-value than preventing an invalid `verified` trust state.
- TypedDict `Literal` refinements are static typing improvements, not a missing runtime invariant.
- Read-only facade immutability and contract-version derivation are maintainability refinements, not currently evidenced correctness blockers.

## Selected vertical slice

Implement the smallest lifecycle trust boundary:

1. Schema: when `status` is `verified`, require at least one evidence identifier and a traceable `provenance.source`.
2. Runtime: for `verified` records, require each referenced evidence record to list the Implementation in its `supports` collection.
3. Behavioral tests: verify rejection of empty evidence, rejection of unsupported evidence, and acceptance of the existing evidence-backed record when promoted to `verified` in an isolated test fixture.
4. Documentation/state: record the audit result and active vertical slice without inventing a numbered P2.3 roadmap item.

This does not introduce providers, implementations, platforms, frameworks, models, adapters, compatibility claims, or changes to MCP classification.
