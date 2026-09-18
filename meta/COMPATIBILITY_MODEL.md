# Compatibility Model

**Status:** Canonical contract for evidence-backed compatibility facts  
**Version:** 1.0

## Purpose

Compatibility answers a different question from ranking:

> Can this subject be used with this target under the recorded conditions?

A compatibility fact is explicit, typed, provenance-backed, and independently queryable. It must not be inferred from a framework name, provider mention, documentation example, or score alone.

## Subject types

Compatibility facts may describe a canonical skill, concrete implementation, or adapter.

## Target types

Targets are execution or integration environments:

- Platform
- Framework
- Model
- Protocol
- Runtime

MCP is represented as a **Protocol**, not as a platform or framework.

## Status semantics

- **compatible** — evidence supports use under the recorded scope.
- **conditional** — use is supported only when stated constraints are satisfied.
- **incompatible** — evidence establishes a conflict or unsupported boundary.
- **unknown** — insufficient evidence to make a compatibility claim.
- **deprecated** — the compatibility fact is no longer current.

No status is a ranking score.

## Evidence gate

Every compatibility fact requires one or more evidence references. Compatibility claims must preserve provenance, constraints, limitations, and verification context.

The first registry fact is intentionally **conditional**: the Code Reviewer MCP adapter maps to the repository's MCP boundary, but this does not establish broad host-by-host MCP compatibility or production deployment.

## Runtime behavior

`UniversalRegistry.compatibility_for(subject_id, target_type=None, target_id=None)` returns matching facts in deterministic ID order.

Eligibility logic will consume these facts in P1.9. It must filter on compatibility before recommendation ranking; compatibility failures must never be hidden inside a ranking score.
