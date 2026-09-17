# ADR-001: Runtime Taxonomy Compatibility Adapter

## Status

Accepted for the production-hardening branch.

## Problem

The authoritative taxonomy stores detailed Level-4 skill mappings under `#### Gxx.y` sections. The existing parser primarily recognizes table-based `###` mapping sections. Parent goals therefore do not reliably consume the detailed sub-goal skill definitions.

## Decision

Introduce `tools.taxonomy_runtime.RuntimeGoalTaxonomyParser` as a small compatibility-preserving adapter. It subclasses the existing parser, parses numbered Level-4 skill lists, and deterministically aggregates sub-goal mappings for parent goals with duplicate skill IDs removed in stable order.

API dependency construction uses the adapter. The original parser remains intact so existing imports and historical tooling are not broken during the migration.

## Why not rewrite the parser now?

The parser is coupled to the current monolithic architect module and several consumers import it directly. A compatibility adapter allows the behavioral safety net to be established before domain extraction.

## Validation

The hardening branch adds real engine tests for canonical goals, sub-goals, parent aggregation, scoring/evidence, determinism, and the API contract.

## Follow-up

After the safety net is green, consolidate taxonomy parsing into a dedicated domain component and remove the adapter only when all consumers have migrated and regression coverage proves equivalent behavior.
