"""Deterministic pre-ranking eligibility evaluation."""

from __future__ import annotations

from typing import Any

from registry.runtime import UniversalRegistry


class EligibilityEngine:
    """Evaluate registry candidates before recommendation ranking."""

    def __init__(self, registry: UniversalRegistry) -> None:
        self.registry = registry

    def evaluate(
        self,
        candidate_ids: list[str],
        target: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        results = []
        entities = self.registry.data["entities"]
        by_id = {
            record["id"]: (entity_type, record)
            for entity_type, records in entities.items()
            for record in records
        }

        for candidate_id in candidate_ids:
            entry = by_id.get(candidate_id)
            if entry is None:
                results.append({
                    "id": candidate_id,
                    "status": "ineligible",
                    "reasons": [{
                        "code": "missing_candidate",
                        "message": f"Candidate is not registered: {candidate_id}",
                    }],
                })
                continue

            entity_type, candidate = entry
            reasons = []
            if entity_type == "skills" and not candidate.get("implementations"):
                if target is not None:
                    reasons.append({
                        "code": "no_implementation",
                        "message": f"Skill has no registered implementation: {candidate_id}",
                    })
            if entity_type == "implementations" and candidate.get("status") == "deprecated":
                reasons.append({
                    "code": "compatibility_deprecated",
                    "message": f"Implementation is deprecated: {candidate_id}",
                })

            if target is not None:
                facts = self.registry.compatibility_for(
                    candidate_id,
                    target_type=target["type"],
                    target_id=target["id"],
                )
                if not facts:
                    reasons.append({
                        "code": "compatibility_missing",
                        "message": f"No evidence-backed compatibility fact for {candidate_id} and {target['type']}/{target['id']}",
                    })
                else:
                    status = facts[0]["status"]
                    if status == "conditional":
                        reasons.append({
                            "code": "compatibility_conditional",
                            "message": f"Compatibility is conditional for {candidate_id} and {target['type']}/{target['id']}",
                        })
                    elif status in {"incompatible", "deprecated"}:
                        reasons.append({
                            "code": f"compatibility_{status}",
                            "message": f"Compatibility status is {status} for {candidate_id} and {target['type']}/{target['id']}",
                        })
                    elif status == "unknown":
                        reasons.append({
                            "code": "compatibility_missing",
                            "message": f"Compatibility is not established for {candidate_id} and {target['type']}/{target['id']}",
                        })

            reason_codes = {reason["code"] for reason in reasons}
            if any(code in reason_codes for code in {
                "missing_candidate",
                "no_implementation",
                "compatibility_missing",
                "compatibility_incompatible",
                "compatibility_deprecated",
            }):
                status = "ineligible"
            elif "compatibility_conditional" in reason_codes:
                status = "conditional"
            else:
                status = "eligible"

            results.append({"id": candidate_id, "status": status, "reasons": reasons})

        return {"candidates": results}
