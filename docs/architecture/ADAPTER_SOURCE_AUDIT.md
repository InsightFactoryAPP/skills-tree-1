# P1.2 — Adapter Source Audit

**Date:** 2026-09-17  
**Purpose:** Identify existing adapter-like integration boundaries and establish what can and cannot become a universal `Adapter` entity.

## Audit result

The repository already contains concrete integration boundaries, but they are not yet represented as universal Adapter registry records. The audit therefore separates executable adapters from protocols, interfaces, examples, and documentation. No compatibility claim is promoted merely because a framework or protocol is mentioned.

## Source map

| Source | Observed role | Universal interpretation | Evidence boundary | Action |
|---|---|---|---|---|
| `mcp/server.py` | stdio JSON-RPC MCP server boundary | Concrete adapter candidate | Executable server behavior is directly inspectable | Validate protocol/tool contract before registration |
| `mcp/tools.py` | MCP tool dispatch layer calling API routes | Adapter/integration candidate | Code proves delegation to API; it does not prove every external host compatibility claim | Preserve as primary adapter evidence |
| `examples/mcp-server/server.py` | Example MCP server | Example adapter candidate | Example status is weaker than production status | Keep as example evidence until independently validated |
| `examples/mcp-server/README.md` | MCP integration instructions | Integration documentation | Documentation describes intended usage | Do not use alone as compatibility proof |
| `meta/MCP_SERVER_SPEC.md` | MCP server specification | Adapter/protocol design evidence | Specification is normative design context, not runtime proof | Link as provenance |
| `meta/MCP_QUICKSTART.md` | MCP onboarding | Integration documentation | Quickstart demonstrates intended setup | Supporting evidence only |
| `meta/MCP_REAL_WORLD_VALIDATION.md` | MCP validation record | Adapter evidence | Claims require freshness/methodology review | Candidate evidence source |
| `meta/MCP_ECOSYSTEM_STRATEGY.md` | Ecosystem strategy | Strategic context | No direct execution proof | Do not promote to compatibility evidence |
| `api/main.py` | FastAPI HTTP service | Interface/runtime boundary | Code verifies HTTP endpoints; it is not automatically an Adapter | Model separately as API interface |
| `docs/cli.md` | CLI documentation | Interface documentation | Commands must be verified against CLI implementation | Do not classify as Adapter by itself |
| `meta/frameworks.md` | Framework/platform/model catalog | Compatibility context | Curated references do not prove adapter implementation | Use for discovery only |
| `docs/architecture/CURRENT_ARCHITECTURE.md` | Current architecture | Architecture evidence | Describes current state and remaining adapter gap | Keep as architectural provenance |
| `registry/universal_registry.json` | Universal entity dataset | Canonical registry | Adapter collection currently empty | Future Adapter records must enter through registry contract |
| `meta/universal-registry.schema.json` | Universal entity vocabulary | Canonical ontology contract | Schema defines Adapter as a first-class entity | Freeze contract before registration |

## Verified concrete boundary: MCP

The current MCP server implements a minimal JSON-RPC 2.0 stdio boundary supporting `initialize`, `tools/list`, and `tools/call`. Its advertised tools are `recommend_skills`, `generate_blueprint`, `list_goals`, and `list_skills`.

`mcp/tools.py` delegates calls to the existing FastAPI application through `TestClient`, rather than duplicating recommendation or blueprint business logic. This makes the MCP layer a real integration boundary over the existing API stack, while keeping the API itself a separate interface entity.

## Adapter classification rules

An Adapter candidate must satisfy all of the following before registry promotion:

1. It maps a universal Implementation or Skill contract into a specific execution ecosystem.
2. Its input/output mapping is inspectable.
3. Its target Platform, Framework, Protocol, or runtime is explicitly identified.
4. Authentication and runtime requirements are documented when applicable.
5. Compatibility claims are supported by executable evidence, tests, or explicit verified validation.
6. Provenance points to the repository source and any external authoritative source used.
7. It is not merely a framework mention, documentation page, protocol specification, or example.

## Important separation

`API`, `CLI`, `MCP`, `Framework`, `Platform`, and `Model` are not interchangeable concepts.

- API is an interface exposed by the system.
- CLI is a command interface.
- MCP is an interoperability protocol and execution surface.
- Framework is an agent-development framework.
- Platform is an execution/service environment.
- Model is a foundation-model entity.
- Adapter is the explicit mapping layer that makes an implementation usable within a target ecosystem.

Therefore, the repository must not create an Adapter record merely because an implementation has an API or because a framework is listed in `meta/frameworks.md`.

## Current adapter candidates

### Candidate A — Skills Tree MCP server

Status: **AUDIT CANDIDATE — NOT REGISTERED**

Evidence:
- `mcp/server.py`
- `mcp/tools.py`
- `meta/MCP_SERVER_SPEC.md`
- `meta/MCP_REAL_WORLD_VALIDATION.md`

Known boundary:
- stdio JSON-RPC
- MCP tool discovery and invocation
- delegation to existing API routes

Unknown until separately verified:
- complete host-by-host compatibility
- production deployment characteristics
- external authentication requirements
- performance/reliability benchmarks

### Candidate B — Example MCP server

Status: **EXAMPLE ONLY**

The example demonstrates integration shape but should not be promoted to production Adapter status without explicit validation.

## Rejected classifications

The following are intentionally **not** registered as Adapters in P1.2:

- individual framework rows in `meta/frameworks.md`
- generic API routes
- CLI documentation
- MCP strategy documentation
- MCP quickstart documentation
- example documentation without runtime evidence

## P1.2 acceptance criteria

- [x] Adapter-like sources identified.
- [x] Concrete executable integration boundary identified.
- [x] MCP implementation and API delegation inspected.
- [x] Example integrations separated from production evidence.
- [x] Framework/platform/model references separated from Adapter entities.
- [x] Adapter promotion criteria documented.
- [x] Unknown compatibility claims explicitly preserved as unknown.
- [ ] Platform/Framework/Model source audit — **P1.3**.
- [ ] Implementation contract — **P1.4**.
- [ ] Adapter contract — **P1.5**.
- [ ] Concrete Adapter registry records — later vertical slice.

## Next task

Proceed to **P1.3 — Platform/Framework Source Audit**. No Adapter registry records should be added until the surrounding Platform/Framework/Model source map is complete and the Adapter contract is frozen.
