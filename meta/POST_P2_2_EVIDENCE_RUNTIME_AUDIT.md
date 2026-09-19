# Post-P2.2 Evidence Runtime Access Audit

**Date:** 2026-09-19
**Baseline:** `main` at `5c8a75ee6346a2ec8d85ab4214c6ebd556e6829b`

## Finding

The universal registry already treats Evidence as a first-class entity and the runtime validates Evidence references used by Implementation, Adapter, and compatibility records. Typed runtime access exists for Implementation and Adapter records, but consumers still need to traverse raw registry data to resolve Evidence or enumerate the Evidence supporting an entity.

That is a read-boundary gap: evidence is part of the normative provenance and traceability model, so consumers should not need to depend on the registry's internal JSON layout.

## Selected vertical slice

- Add a typed `EvidenceRecord` runtime shape matching the current registry Evidence structure.
- Add deterministic `resolve_evidence(evidence_id)` access.
- Add deterministic `evidence_for_entity(entity_id)` access.
- Reject unknown Evidence IDs explicitly.
- Preserve read-only snapshot semantics.
- Add focused behavioral regression tests.
- Do not add Evidence records, provenance claims, compatibility facts, provider/platform/framework/model claims, or MCP classifications.

## Boundary

This slice exposes existing, already-validated Evidence. It does not change Evidence validation rules, invent provenance, or promote any registry claim.

## Quality gate

Completion requires focused regression tests, existing test-suite validity, schema/runtime validation, deterministic ordering, package/build validation, security checks, documentation consistency, and required CI green on the exact PR head.
