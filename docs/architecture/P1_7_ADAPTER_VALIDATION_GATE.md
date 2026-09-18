# P1.7 — First Real Adapter Validation Gate

**Date:** 2026-09-18

## Result

No Adapter registry record is promoted in this slice.

The repository has a concrete MCP integration boundary, but the current first registered Implementation is `implementation/code-reviewer-system`. The MCP server does not expose that implementation or its Code Review skill; it exposes recommendation, blueprint, goal-listing, and skill-listing tools. Registering the MCP boundary as an adapter for the Code Reviewer implementation would therefore create an unsupported implementation-to-target mapping.

## Evidence inspected

- `mcp/server.py` — executable stdio JSON-RPC boundary.
- `mcp/tools.py` — MCP tool dispatch to the existing FastAPI API.
- `registry/universal_registry.json` — first Implementation is `implementation/code-reviewer-system`.
- `meta/adapter-contract.schema.json` — Adapter requires an explicit Implementation and typed target.
- `docs/architecture/ADAPTER_SOURCE_AUDIT.md` — MCP is a concrete adapter candidate, but compatibility and mapping must be verified.

## Compatibility decision

The current MCP boundary can be described as an integration surface, but it cannot yet be truthfully registered as an Adapter for `implementation/code-reviewer-system`.

The missing evidence is a concrete target-facing mapping in which the registered Implementation is actually exposed and invocable through that target.

## Required next vertical slice

Build or identify a real target integration for the registered Implementation, then validate:

1. Implementation-side input contract.
2. Target-side input contract.
3. Input transformation.
4. Target invocation.
5. Target output contract.
6. Output transformation.
7. Runtime/authentication requirements.
8. Executable integration tests.
9. Provenance and evidence.

Only after these are demonstrated should an Adapter record be added.

## Safety rule

Do not create a placeholder Adapter, do not register MCP merely because it exists, and do not infer compatibility from documentation or protocol support.
