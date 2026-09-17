# Skills Tree — Project Goal

## Mission

Skills Tree is a platform-agnostic, machine-readable source of truth for the capabilities, skills, patterns, tools, implementations, dependencies, evidence, and architectural knowledge required to build AI agents.

The long-term goal is to become a universal skills and capability registry that can serve agents and agent-building platforms across vendors, models, frameworks, runtimes, and deployment environments.

## North Star

**Any agent, on any platform, should be able to discover what it needs, understand the dependencies and constraints, select compatible skills, and compose them into a validated agent architecture using Skills Tree.**

## Scope

Skills Tree must represent knowledge at four connected levels:

1. **Capability** — what an agent can do.
2. **Skill** — a reusable, platform-independent method or competency that enables a capability.
3. **Implementation** — a concrete realization of a skill using a model, API, library, tool, runtime, or service.
4. **Platform / Framework Adapter** — the mapping required to use the capability or skill within a specific agent ecosystem.

The knowledge graph must connect these with goals, prerequisites, dependencies, evidence, benchmarks, constraints, compatibility, versions, and quality signals.

## Platform Principle

The canonical skill definition must remain platform-agnostic.

OpenAI, Anthropic, Google, MCP, LangChain, LangGraph, CrewAI, AutoGen, LlamaIndex, Semantic Kernel, browser/computer-use runtimes, coding agents, local models, cloud platforms, and future ecosystems are integrations around the universal model — not separate competing skill taxonomies.

## Core Pipeline

```text
Goal
  ↓
Goal Resolution
  ↓
Capability Identification
  ↓
Skill Discovery
  ↓
Eligibility & Constraints
  ↓
Prerequisite / Dependency Graph
  ↓
Evidence & Benchmark Analysis
  ↓
Deterministic Scoring
  ↓
Platform / Framework Compatibility
  ↓
Skill Composition
  ↓
Learning / Execution Path
  ↓
Architecture Inference
  ↓
Validated Agent Blueprint
```

## Engineering Requirements

- Preserve the existing repository; evolve incrementally and do not rewrite from scratch.
- Prefer canonical, structured, machine-readable data over duplicated platform-specific definitions.
- Keep recommendation, eligibility, ranking, calibration, explanation, and presentation logically separate.
- Make deterministic behavior a hard requirement wherever reproducibility is expected.
- Every important claim should have provenance or evidence when practical.
- Every graph relationship must be validated.
- Platform compatibility must be explicit rather than inferred from naming alone.
- Tests must exercise real behavior; never add synthetic tests merely to obtain green CI.
- Never weaken tests or validation rules to make CI pass.
- Security, supply-chain integrity, data integrity, and reproducibility are first-class requirements.
- New platforms and frameworks must be additive integrations, not reasons to fork the canonical taxonomy.

## Success Definition

The project succeeds when an external agent or platform can provide a goal such as:

> Build an autonomous research agent that searches the web, reads documents, verifies evidence, reasons over sources, and produces a cited report.

and Skills Tree can deterministically expose:

- the required capabilities;
- the relevant skills;
- prerequisites and dependencies;
- evidence and benchmarks;
- compatible implementations;
- supported platforms and frameworks;
- constraints and known failure modes;
- an explainable recommendation;
- and a validated architecture / implementation blueprint.

The same knowledge must remain reusable when the target model, platform, framework, toolchain, or deployment environment changes.

## Strategic Position

Skills Tree is not intended to be merely a large collection of markdown files.

It is intended to become the **Universal Agent Skills & Capability Registry**: an open, versioned, evidence-backed knowledge layer that lets different AI agent ecosystems share a common vocabulary for capabilities and skills without requiring them to share the same runtime.
