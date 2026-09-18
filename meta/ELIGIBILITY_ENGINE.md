# Eligibility Engine

**Status:** Canonical pre-ranking eligibility contract
**Version:** 1.0

## Purpose

Eligibility answers whether a candidate can proceed to recommendation ranking under the supplied execution target. It is a filter, not a score.

The pipeline remains:

`Discovery → Eligibility → Constraint Filtering → Ranking → Calibration → Explanation`

Eligibility is deterministic and returns an explicit status plus machine-readable reasons.

## Candidate model

A candidate is a registry entity ID. Current execution candidates are canonical skills, implementations, or adapters.

An implementation-backed candidate must reference a real registered implementation. An adapter candidate must also satisfy the requested target through an evidence-backed compatibility fact.

## Compatibility gate

When a target is supplied:

- `compatible` → eligible
- `conditional` → conditional
- `incompatible` → ineligible
- `deprecated` → ineligible
- missing compatibility evidence → ineligible

No compatibility status is converted into a ranking score.

## Determinism

Candidates are returned in input order and all reason lists are stable. The engine does not mutate the registry or recommendation engine.

P1.9 is intentionally a small registry-backed vertical slice. Broader prerequisite evaluation will be added only when authoritative prerequisite data is available.
