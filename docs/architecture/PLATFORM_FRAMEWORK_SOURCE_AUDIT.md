# Platform / Framework / Model Source Audit

Repository-backed classification and provenance audit for Platform, Framework, Model, Protocol, and Runtime/Ecosystem sources. No registry population is performed here.

## Findings

`meta/frameworks.md` is a heterogeneous discovery source, not a canonical entity registry. It contains framework, computer-use/browser, protocol, and model sections and is dated April 2026, so freshness must be considered for imported records.

`docs/PROJECT_GOAL.md` is the canonical project-intent source. `meta/PLATFORM_ASCENSION_FINAL.md`, `meta/OS_MASTER_PLAN.md`, and `meta/AGENT_ARCHITECT_VISION.md` provide strategic or architectural context, not compatibility proof. `intelligence/ontology/capability_ontology.json` contains structured framework/model requirements, but those references must resolve to typed canonical entities before graph edges are created.

`mcp/server.py` and `mcp/tools.py` provide executable evidence for this repository's MCP integration boundary. MCP remains a Protocol, separate from the implementation and any future Adapter. `api/main.py` and CLI documentation are interfaces, not automatically Platforms or Frameworks.

## Source map

| Source | Candidate types | Role | Evidence quality | Migration risk |
|---|---|---|---|---|
| `meta/frameworks.md` | Framework, Platform, Model, Protocol | Curated reference | Heterogeneous reference | High |
| `docs/PROJECT_GOAL.md` | Platform, Framework, Model, Adapter | Canonical intent | Normative | Low |
| `meta/PLATFORM_ASCENSION_FINAL.md` | Platform, Framework, Model, Runtime | Strategy | Strategic/reference | Medium |
| `meta/OS_MASTER_PLAN.md` | Framework, Model, ecosystem | Planning | Historical/strategic | Medium |
| `meta/AGENT_ARCHITECT_VISION.md` | Model, Platform, Runtime | Requirements | Architectural intent | Medium |
| `intelligence/ontology/capability_ontology.json` | Framework, Model | Structured requirements | Requirement reference | Medium |
| `mcp/server.py` / `mcp/tools.py` | Protocol, integration/runtime | Executable boundary | Repository implementation evidence | Low for boundary; insufficient for broad host compatibility |
| `meta/MCP_REAL_WORLD_VALIDATION.md` | Protocol/ecosystem | Validation candidate | Evidence requiring freshness/methodology review | Medium |
| `meta/universal-registry.schema.json` | Platform, Framework, Model, Adapter | Ontology contract | Normative schema | Low |
| `registry/universal_registry.json` | Platform, Framework, Model | Registry state | Canonical current data | Low; collections intentionally empty |

## Classification rules

A Framework record requires evidence of a software framework/SDK role. A Platform record requires evidence of an execution, hosting, managed-agent, model-service, or deployment role. A Model record requires an identifiable model family/version or service identifier. A Protocol requires an interoperability specification. Runtime/Ecosystem must not be invented merely to absorb ambiguous references.

## Compatibility boundary

Presence in `meta/frameworks.md` does not establish Skill support, Framework support, Platform support, Model/Framework compatibility, Adapter existence, production readiness, or benchmark/reliability results. Those claims require executable evidence, authoritative documentation, benchmark evidence, or another explicitly classified evidence source.

## Migration risks

Primary risks are duplicate identities, confusing providers with models, confusing platforms with frameworks, treating model families and versions as one entity, importing stale references, inferring compatibility from prose, and conflating protocol support with framework support.

## Initial migration strategy

Do not import the entire reference file. First select one framework, one platform/execution environment, one model, and MCP as a separate Protocol, each with traceable provenance. Add compatibility edges only after evidence validation.

## Graph constraints

```text
Skill --IMPLEMENTED_BY--> Implementation
Implementation --ADAPTED_BY--> Adapter
Adapter --TARGETS--> Framework
Adapter --TARGETS--> Platform
Implementation --REQUIRES--> Runtime/Tool/Model
Framework --RUNS_ON--> Platform
Model --SUPPORTED_BY--> Platform
```

Only relationship types from the universal registry vocabulary may be used.

## Decision

No Platform, Framework, Model, Protocol, or Runtime records are created by this audit. The evidence boundary is intentionally preserved.

## Acceptance criteria

- [x] Major sources reviewed.
- [x] Heterogeneous source categories classified.
- [x] Canonical versus contextual sources distinguished.
- [x] Provenance and evidence boundaries documented.
- [x] No unverified registry records created.
- [x] Migration risks documented.

## Next

P1.4 — Implementation Contract.