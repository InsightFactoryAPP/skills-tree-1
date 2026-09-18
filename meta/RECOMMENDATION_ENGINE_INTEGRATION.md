# P1.11 Recommendation Engine Integration

P1.11 integrates the universal-registry eligibility boundary with the existing `RecommendationEngine` without replacing its discovery, scoring, calibration, evidence, or learning-path logic.

## Execution pipeline

`Goal → legacy discovery/ranking → registry eligibility → eligible candidate set`

The registry layer is additive. Skills that are not yet represented in the universal registry continue through the legacy pipeline unchanged. Registered candidates are evaluated by `EligibilityEngine` before ranking results are accepted.

## Target-aware compatibility

When a typed target is supplied, compatibility is resolved through the registered relationship:

`Skill → Implementation → Adapter → Target`

This is important because compatibility facts are currently attached to adapters. The integration does not invent direct Skill → Platform/Framework/Protocol compatibility facts.

A `conditional` compatibility result remains selectable and is exposed in the machine-readable eligibility result. `ineligible` candidates are removed before the final ranked result is returned. Eligibility is never converted into a ranking score.

## Preservation guarantees

- The existing `tools.architect.RecommendationEngine` remains the ranking authority.
- Unregistered legacy skills are not filtered by the universal registry.
- Registry eligibility is read-only and deterministic.
- Rank numbers are made contiguous after an ineligible registered candidate is removed.
- MCP remains a Protocol entity; no platform/framework claim is introduced.
- Existing API dependency injection now uses the integrated engine and the canonical registry runtime.
