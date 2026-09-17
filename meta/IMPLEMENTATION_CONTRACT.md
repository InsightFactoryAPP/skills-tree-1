# Universal Implementation Contract

## Purpose

An **Implementation** is a concrete realization of a canonical Skill using one or more models, APIs, libraries, tools, runtimes, or services.

Implementation is intentionally separate from Skill, Tool, Platform, Framework, Model, and Adapter.

## Required fields

Every Implementation record must contain:

- `id` — stable unique identifier.
- `version` — registry contract/data version in `major.minor` form.
- `name` — human-readable implementation name.
- `skill` — canonical Skill ID implemented by the record.
- `type` — one of `library`, `api`, `service`, `tool`, `runtime`, `composite`.
- `interface` — actual invocation/integration boundary.
- `inputs` — declared input names or contract elements.
- `outputs` — declared output names or contract elements.
- `requirements` — dependencies and execution prerequisites.
- `constraints` — eligibility or operational constraints.
- `limitations` — known functional boundaries and failure modes.
- `provenance` — traceable source metadata.
- `evidence` — identifiers for supporting evidence.
- `status` — `candidate`, `verified`, `deprecated`, or `experimental`.

`provider` is optional when the provider cannot be established from evidence.

## Semantics

`skill` must resolve to a canonical Skill. An Implementation never creates or modifies the canonical taxonomy.

`version` identifies the registry representation/contract version. A provider's software, API, or model version must not be silently substituted for this field; provider versions belong in requirements or evidence when applicable.

`interface` must describe the actual boundary, such as HTTP API, Python library, SDK, CLI, MCP tool, or local runtime. Documentation-only claims are insufficient to establish executable behavior.

`requirements`, `constraints`, and `limitations` describe concrete facts supported by repository or external evidence. They must not contain guessed dependencies or compatibility claims.

`provenance` establishes where the record was derived from. `evidence` supports claims about behavior, compatibility, quality, reliability, or operational status. A source mention is not evidence of compatibility.

## Lifecycle

```text
candidate → verified → deprecated
      └────────→ experimental
```

`candidate` means a concrete implementation has been identified but applicable validation is incomplete. `verified` means the claims represented by the record have passed applicable validation/evidence gates. `experimental` means it is intentionally usable for exploration while evidence remains incomplete. `deprecated` means it should not be selected for new recommendations unless explicitly requested.

## Separation rules

- Skill = canonical, platform-independent method or competency.
- Implementation = concrete realization of a Skill.
- Tool = executable dependency or interface consumed by an Implementation.
- Model = model entity required or used by an Implementation.
- Platform = execution/hosting environment.
- Framework = software construction/orchestration environment.
- Adapter = mapping of an Implementation into a target ecosystem.

A framework, model, platform, protocol, or documentation reference must never be promoted to Implementation merely because it mentions a capability.

## Validation gate

Before status becomes `verified`, the registry compiler/runtime must be able to establish:

1. the referenced Skill exists and is canonical;
2. referenced entity identifiers resolve;
3. the interface is supported by executable evidence where applicable;
4. inputs and outputs match the observed implementation boundary;
5. requirements, constraints, and limitations are evidence-backed;
6. provenance sources are traceable;
7. evidence supports every compatibility or quality claim;
8. serialization is schema-valid and deterministic.

## Structural example

The following is intentionally non-production data and must not be registered as a real provider:

```json
{
  "id": "implementation/example-web-search",
  "version": "1.0",
  "name": "Example Web Search Implementation",
  "skill": "11-web/web-search",
  "type": "api",
  "provider": "example-provider",
  "interface": "https",
  "inputs": ["query"],
  "outputs": ["search_results"],
  "requirements": [],
  "constraints": [],
  "limitations": [],
  "provenance": {"source_type": "repository", "source": "docs/example.md"},
  "evidence": [],
  "status": "candidate"
}
```

The normative machine-readable contract is `meta/implementation-contract.schema.json`.

## P1.4 acceptance criteria

- The contract is machine-readable and schema-valid.
- Implementation identity and versioning are distinct from provider/model versions.
- Skill linkage is explicit and canonical.
- Inputs, outputs, requirements, constraints, and limitations are explicit.
- Provenance and evidence are first-class.
- Lifecycle states are explicit.
- Implementation remains distinct from Tool, Model, Platform, Framework, and Adapter.
- No real provider is registered by this contract-only step.
