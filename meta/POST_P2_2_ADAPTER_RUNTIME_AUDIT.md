# Post-P2.2 Adapter Runtime Access Audit

**Date:** 2026-09-19
**Baseline:** `main` at `3b4ddc44ba10dd3d97433b7095dfd624fd219a95`

## Finding

The registry already contains a normative Adapter contract and runtime validation. However, the read-only runtime facade exposed typed Implementation access but did not expose typed Adapter access. Consumers therefore had to traverse raw registry data to resolve an Adapter or enumerate Adapters for an Implementation.

This is an architectural boundary gap because Adapter is already a first-class ontology entity and graph/compatibility validation depends on its canonical identity.

## Selected vertical slice

- Add a typed `AdapterRecord` runtime shape matching the normative Adapter contract.
- Add deterministic `resolve_adapter(adapter_id)`.
- Add deterministic `adapters_for_implementation(implementation_id)`.
- Reject unknown Adapter and Implementation IDs explicitly.
- Add behavioral regression coverage.
- Do not add or alter Adapter entities, targets, compatibility claims, MCP classification, or evidence.

## Boundary

This slice provides runtime access only. It does not promote Adapter lifecycle status, invent compatibility, or replace the existing validation/graph layer.

## Quality gate

The change is complete only after real regression tests, schema/runtime validation, deterministic ordering, package/build validation, security checks, and required CI are green.
