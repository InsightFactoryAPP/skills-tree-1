# Post-P2.2 Capability Runtime Audit — 2026-09-19

## Finding

The registry already contains authoritative Capability records with symmetric links to canonical Skills, Implementations, and Adapters, and `registry/runtime.py` validates those relationships. The runtime exposed Goal and Skill traversal plus typed Implementation and Adapter access, but it had no dedicated typed Capability runtime boundary.

## Minimal vertical slice

Add `CapabilityRuntime` as a read-only runtime boundary over the existing `UniversalRegistry` facade. It provides deterministic Capability-by-ID resolution and deterministic Capability-to-Implementation and Capability-to-Adapter lookup.

## Contract boundary

This slice does not add registry entities, alter existing relationships, or infer new compatibility/provider/platform/framework/model facts. It reuses relationships already validated during registry initialization.

MCP remains classified as a Protocol. Compatibility remains applicability data rather than a ranking score.

## Verification requirements

The slice is complete only after focused regression tests, repository test/build/security checks, deterministic ordering, snapshot isolation, graph/reference integrity, and required CI checks pass.
