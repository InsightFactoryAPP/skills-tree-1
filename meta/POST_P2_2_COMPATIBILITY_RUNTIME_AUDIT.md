# Post-P2.2 Compatibility Runtime Access Audit

**Date:** 2026-09-19
**Baseline:** `main` at `632b00f470960136a2fbfd174788ce0dfd30296a`

## Finding

The universal registry already contains a normative compatibility model and schema, and `UniversalRegistry.compatibility_for()` exposes compatibility facts as untyped dictionaries. The runtime validates Implementation, Adapter, and universal-graph contracts, but compatibility records do not yet have a dedicated typed runtime boundary with schema, endpoint, and reverse-evidence validation.

That leaves a provenance-bearing eligibility input dependent on raw registry layout and permits compatibility contract drift to escape the runtime boundary.

## Selected vertical slice

- Add typed `CompatibilityRecord` and target shapes.
- Validate existing compatibility records against `meta/compatibility-model.schema.json`.
- Validate compatibility subject and target IDs against existing registry entities.
- Validate reverse Evidence support for every referenced Evidence record.
- Add deterministic `resolve_compatibility()` and filtered `compatibility_for()` access.
- Preserve read-only snapshot semantics.
- Add focused behavioral regression tests.
- Do not add compatibility records, ecosystem claims, provider/platform/framework/model claims, or MCP classifications.

## Boundary

This slice exposes and validates the existing compatibility fact. It does not change compatibility semantics or promote compatibility into ranking. Compatibility remains applicability/eligibility data and MCP remains a Protocol.

## Quality gate

Completion requires focused regression tests, existing test-suite validity, schema/runtime validation, deterministic ordering, package/build validation, security checks, provenance/evidence integrity, documentation consistency, no unrelated changes, and required CI green on the exact PR head.
