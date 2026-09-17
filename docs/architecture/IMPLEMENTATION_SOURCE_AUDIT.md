# P1.1 — Implementation Source Audit

**Date:** 2026-09-17  
**Branch:** `p1/implementation-source-audit-20260917`  
**Purpose:** Establish the canonical source map for concrete skill implementations before creating new registry implementation entities.

## Audit result

The repository contains several classes of implementation-like source material, but they are not yet represented as a universal `Implementation` registry collection. The correct next move is therefore source mapping and contract design, not bulk migration.

## Canonical source map

| Source | Current role | Universal interpretation | Trust / action |
|---|---|---|---|
| `skills/**` | Canonical skill Markdown and frontmatter | **Skill** source; implementation details may be embedded in skill content | Preserve as canonical skill source; extract implementation references only when evidence is explicit |
| `meta/frameworks.md` | Curated frameworks, platforms, protocols, browser systems, and foundation models | **Reference source** for Framework / Platform / Model / Protocol candidates | High-value discovery source, but not canonical registry data yet |
| `mcp/` | Working MCP server implementation | **Implementation + Adapter candidate** | Audit actual runtime/tool behavior before registration |
| `examples/mcp-server/` | Example MCP server integration | **Implementation example / Adapter candidate** | Treat as example evidence unless runtime validation proves production applicability |
| `meta/MCP_SERVER_SPEC.md` | MCP server design specification | **Architecture/specification evidence** | Use as design provenance; do not treat prose as proof of runtime behavior |
| `meta/MCP_QUICKSTART.md` | MCP usage/onboarding documentation | **Integration documentation** | Supporting source only |
| `meta/MCP_REAL_WORLD_VALIDATION.md` | MCP validation record | **Evidence** | Candidate evidence source; validate freshness and methodology before promotion |
| `meta/MCP_ECOSYSTEM_STRATEGY.md` | Ecosystem strategy | **Strategic context** | Not implementation evidence by itself |
| `docs/cli.md` | CLI interface documentation | **Platform/interface evidence** | Useful for adapter/interface mapping; verify commands against code |
| `docs/api/**` | Published API artifacts | **Interface/runtime artifacts** | Use as generated/public artifacts; canonical source remains implementation code and registry source |
| `registry/universal_registry.json` | Current universal registry dataset | **Canonical registry data** | Already authoritative for currently registered entities |
| `registry/runtime.py` | Deterministic read-only registry runtime | **Registry runtime** | Canonical runtime behavior; not an implementation catalogue |
| `meta/universal-registry.schema.json` | Universal entity/relationship contract | **Canonical ontology contract** | Authoritative contract for future registry entities |
| `data/SKILLS_GRAPH.json` | Canonical skill graph | **Graph source** | Preserve as graph source; extend with typed universal entities only through validated evolution |
| `docs/architecture/CURRENT_ARCHITECTURE.md` | Current architecture description | **Architecture evidence** | Authoritative for current-state interpretation, subject to verified runtime behavior |
| `docs/architecture/TARGET_ARCHITECTURE.md` | Target architecture | **Architecture intent** | Guides evolution; not evidence that target components exist |

## Findings

### 1. Implementation is currently implicit

The repository has real executable systems, especially the MCP server and existing CLI/API/runtime components, but the universal registry currently does not contain implementation records. This is intentional and correct for the current migration stage.

### 2. `meta/frameworks.md` is heterogeneous

The file combines agent frameworks, computer-use/browser systems, interoperability standards, and foundation models. It is useful discovery material, but it should not be copied directly into a single entity type. The future compiler should classify each entry into Framework, Platform, Model, or another explicitly defined ontology entity.

### 3. MCP is an integration surface, not the ontology

Existing MCP server files are concrete executable assets. MCP should therefore be represented as a protocol/platform integration and adapter surface where appropriate. The canonical skill definition must remain independent of MCP.

### 4. Documentation must not be promoted to implementation evidence automatically

Specifications, quickstarts, strategies, and examples describe intended or demonstrated behavior. They become implementation evidence only when linked to verifiable executable code and, where required, real validation results.

### 5. Provenance must be retained during migration

Every future implementation/adapter entity should retain the source path(s) from which its facts were derived. Generated registry artifacts must remain traceable back to those sources.

## Candidate first vertical slice

The audit identifies the existing **Web Search** canonical skill as a suitable candidate for the first implementation migration because the universal model explicitly requires concrete implementations to attach to canonical skills rather than creating provider-specific duplicate skills. The actual provider implementation candidates must still be discovered from repository code or explicit verified metadata before registration.

The current registry already demonstrates the canonical chain:

`goal/research-and-analysis → capability/web-retrieval → 11-web/web-search`

This makes Web Search a natural test subject for the next implementation contract, but this audit does **not** claim that a concrete Web Search provider implementation has been verified in the repository.

## P1.1 acceptance criteria

- [x] Existing implementation-like source classes identified.
- [x] Existing framework/platform/model source identified.
- [x] Existing MCP implementation sources identified.
- [x] Source-of-truth boundaries documented.
- [x] Migration/duplication risks documented.
- [x] Canonical first vertical-slice candidate identified without inventing an implementation.
- [ ] Implementation schema/contract defined — **P1.4**.
- [ ] Concrete implementation entities added — **P1.6**.
- [ ] Adapter entities added — **P1.7**.

## Evidence references

- `meta/DEVELOPMENT_KNOWLEDGE.md` — governing development model and roadmap.
- `meta/universal-registry.schema.json` — universal registry contract.
- `registry/universal_registry.json` — current registered goals/capabilities/skills.
- `registry/runtime.py` — deterministic runtime behavior.
- `meta/frameworks.md` — current curated framework/platform/model reference.
- `mcp/` and `examples/mcp-server/` — concrete MCP implementation assets.
- `meta/MCP_SERVER_SPEC.md`, `meta/MCP_QUICKSTART.md`, `meta/MCP_REAL_WORLD_VALIDATION.md`, `meta/MCP_ECOSYSTEM_STRATEGY.md` — MCP specification/documentation/evidence sources.

## Next task

Proceed to **P1.2 — Adapter Source Audit**. Do not create universal Implementation records until P1.2 and P1.3 have established the complete surrounding source map and P1.4 has frozen the implementation contract.
