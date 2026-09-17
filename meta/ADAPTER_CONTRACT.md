# Universal Adapter Contract

## Purpose

An Adapter is a concrete translation boundary between a registered Implementation and a target execution ecosystem. It maps the implementation's contract into an explicitly identified platform, framework, protocol, or runtime without redefining the underlying Skill or Implementation.

The Adapter contract is deliberately separate from Skill, Implementation, Tool, Model, Platform, Framework, and Protocol records.

## Required fields

- `id`: stable adapter identifier.
- `version`: registry contract representation version, not the target ecosystem's release version.
- `name`: human-readable adapter name.
- `implementation`: canonical Implementation ID being adapted.
- `targets`: one or more explicit target descriptors. Each target has a typed ecosystem class and stable ID.
- `input_mapping`: inspectable mappings from implementation inputs to target-facing inputs.
- `output_mapping`: inspectable mappings from target outputs to implementation outputs.
- `auth_requirements`: authentication or authorization requirements at the boundary.
- `runtime_requirements`: runtime dependencies required for the adapter to operate.
- `constraints`: evidence-backed compatibility or operational constraints.
- `limitations`: known unsupported behavior and boundary limitations.
- `provenance`: traceable origin and verification metadata.
- `evidence`: references supporting the adapter's concrete claims.
- `status`: lifecycle state.

## Target semantics

A target must be explicitly typed as `platform`, `framework`, `protocol`, or `runtime`. A framework mention in documentation is not an adapter. A protocol specification is not an implementation. A platform or model name is not compatibility evidence by itself.

Multiple targets are allowed when the same adapter boundary is demonstrably valid for each target. Each target must remain independently verifiable.

## Mapping semantics

Mappings describe the actual boundary rather than an abstract relationship. `source` identifies the implementation-side field or behavior; `target` identifies the target-side field or behavior; `transform` is optional and records a required conversion.

An empty mapping is structurally valid when the boundary is identity-preserving, but a verified adapter still requires executable evidence that the advertised boundary works.

## Provenance and evidence

Provenance answers where the adapter definition came from and how it was verified. Evidence identifies concrete supporting artifacts. Claims about host compatibility, authentication, runtime behavior, limitations, or transformations must be traceable to evidence.

Documentation alone can establish an intended interface, but executable validation is required before claiming that an adapter is `verified`.

## Lifecycle

- `candidate`: identified from repository or ecosystem evidence but not fully verified.
- `experimental`: executable or partially validated, but stability or coverage is intentionally limited.
- `verified`: contract, target mapping, runtime behavior, and evidence satisfy the validation gate.
- `deprecated`: retained for provenance or migration while no longer recommended for new use.

## Validation gate for `verified`

Before promotion to `verified`, all of the following must hold:

1. The referenced Implementation exists and satisfies the Implementation Contract.
2. Every target resolves to an explicitly typed ecosystem entity.
3. Input and output mappings are inspectable and consistent with the implementation boundary.
4. Authentication and runtime requirements are documented when applicable.
5. Constraints and limitations are evidence-backed.
6. Provenance is traceable to repository, official, implementation, benchmark, production, community, or experimental evidence.
7. Executable tests or verified validation demonstrate the advertised target boundary.
8. The serialized record validates against the machine-readable schema and is deterministic.
9. No unsupported host-by-host compatibility is inferred from a generic framework, protocol, or documentation mention.

## Separation rules

- Skill defines the platform-agnostic capability behavior.
- Implementation realizes the Skill.
- Adapter translates an Implementation into a target ecosystem.
- Tool is an executable capability dependency, not automatically an Adapter.
- Platform identifies an execution environment, not an Adapter.
- Framework identifies an application/development ecosystem, not an Adapter.
- Model identifies an inference model and does not become an Adapter merely because it is supported.
- Protocol identifies an interoperability boundary; an adapter is the concrete translation/use of that boundary.

## Non-goals

This contract does not register providers, claim ecosystem compatibility, populate the universal registry, or alter MCP/API/CLI behavior. Those changes require concrete implementation and evidence work in later vertical slices.
