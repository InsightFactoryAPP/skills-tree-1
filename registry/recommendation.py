"""Universal-registry eligibility integration for the legacy recommender."""

from __future__ import annotations

from typing import Any

from registry.eligibility import EligibilityEngine
from registry.runtime import UniversalRegistry
from tools.architect import RecommendationEngine


class RegistryRecommendationEngine(RecommendationEngine):
    """Run registry eligibility before the existing ranking pipeline.

    The legacy recommendation algorithm remains authoritative for discovery,
    scoring, calibration inputs, and learning-path construction. Registry
    eligibility is an additive pre-ranking gate for candidates that are already
    represented in the universal registry. Unregistered legacy skills are left
    untouched so the existing corpus behavior is preserved.
    """

    def __init__(
        self,
        graph: Any,
        taxonomy: Any,
        benchmark_index_path: str | None = None,
        registry: UniversalRegistry | None = None,
    ) -> None:
        super().__init__(graph, taxonomy, benchmark_index_path)
        self.registry = registry
        self.eligibility = EligibilityEngine(registry) if registry is not None else None

    def recommend(
        self,
        goal_query: str,
        target: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        result = super().recommend(goal_query)
        if "error" in result or self.eligibility is None:
            return result

        candidate_ids = [
            skill["id"]
            for skill in result.get("required_skills", []) + result.get("optional_skills", [])
            if skill.get("id") in self._registered_skill_ids()
        ]
        eligibility = self.eligibility.evaluate(candidate_ids, target=target)
        result["eligibility"] = eligibility

        ineligible = {
            item["id"]
            for item in eligibility["candidates"]
            if item["status"] == "ineligible"
        }
        if not ineligible:
            return result

        result["required_skills"] = [
            skill for skill in result.get("required_skills", []) if skill["id"] not in ineligible
        ]
        result["optional_skills"] = [
            skill for skill in result.get("optional_skills", []) if skill["id"] not in ineligible
        ]

        # Preserve the legacy score ordering while making ranks contiguous after
        # an eligibility gate removes a candidate.
        for rank, skill in enumerate(result["required_skills"], start=1):
            skill["rank"] = rank
        for rank, skill in enumerate(result["optional_skills"], start=len(result["required_skills"]) + 1):
            skill["rank"] = rank
        return result

    def _registered_skill_ids(self) -> set[str]:
        return {skill["id"] for skill in self.registry.data["entities"].get("skills", [])}
