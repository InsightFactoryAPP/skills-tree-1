"""Runtime taxonomy adapter.

This module preserves the existing GoalTaxonomyParser API while covering the
canonical Level-4 mappings stored under ``#### Gxx.y`` sub-goal sections.
It is intentionally small: the parser in ``tools.architect`` remains the
backward-compatible implementation, while API/runtime consumers can use this
adapter until the domain extraction is complete.
"""

from __future__ import annotations

import re
from collections import OrderedDict
from typing import Dict, List

from tools.architect import GoalTaxonomyParser


class RuntimeGoalTaxonomyParser(GoalTaxonomyParser):
    """GoalTaxonomyParser with complete sub-goal mapping support."""

    _SUBGOAL_MAPPING_RE = re.compile(
        r"^####\s+(G\d{2}\.\d+):[^\n]*\n(.*?)(?=^####\s+G\d{2}\.\d+:|^###\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    _NUMBERED_SKILL_RE = re.compile(
        r"^\s*\d+\.\s+`([\w:-]+)`\s+\(([^,]+),\s*(\d+)\s*hrs?\)",
        re.MULTILINE,
    )

    def __init__(self, taxonomy_path: str):
        super().__init__(taxonomy_path)
        self._parse_level4_subgoals()

    def _parse_level4_subgoals(self) -> None:
        """Parse detailed ``#### Gxx.y`` numbered skill mappings."""
        for match in self._SUBGOAL_MAPPING_RE.finditer(self._raw):
            goal_id = match.group(1)
            body = match.group(2)
            skills = []
            for skill_match in self._NUMBERED_SKILL_RE.finditer(body):
                skill_id = skill_match.group(1).strip()
                priority = skill_match.group(2).strip()
                learn_time = int(skill_match.group(3))
                skills.append(
                    {
                        "id": skill_id,
                        "name": skill_id.replace("-", " ").replace(":", " ").title(),
                        "category": "",
                        "priority": priority,
                        "learn_time_hrs": learn_time,
                    }
                )
            if skills:
                self._skill_maps[goal_id] = skills

    def skills_for(self, goal_id: str) -> List[Dict]:
        """Return exact sub-goal skills or a deterministic parent aggregation."""
        exact = self._skill_maps.get(goal_id)
        if exact is not None:
            return list(exact)

        if "." not in goal_id:
            parent_prefix = f"{goal_id}."
            merged: "OrderedDict[str, Dict]" = OrderedDict()
            for subgoal_id in sorted(self._skill_maps):
                if not subgoal_id.startswith(parent_prefix):
                    continue
                for skill in self._skill_maps[subgoal_id]:
                    merged.setdefault(skill["id"], dict(skill))
            if merged:
                return list(merged.values())

        return super().skills_for(goal_id)


# The application layer uses RuntimeGoalTaxonomyParser explicitly. Legacy
# callers still instantiate GoalTaxonomyParser directly, so patch the base
# parser's mapping and lookup stages once at import time to recognize the same
# canonical Level-4 source without changing its public API.
_ORIGINAL_PARSE_SKILL_MAPPINGS = GoalTaxonomyParser._parse_skill_mappings
_ORIGINAL_SKILLS_FOR = GoalTaxonomyParser.skills_for


def _parse_skill_mappings_with_level4(self: GoalTaxonomyParser) -> None:
    _ORIGINAL_PARSE_SKILL_MAPPINGS(self)
    for match in RuntimeGoalTaxonomyParser._SUBGOAL_MAPPING_RE.finditer(self._raw):
        goal_id = match.group(1)
        skills = []
        for skill_match in RuntimeGoalTaxonomyParser._NUMBERED_SKILL_RE.finditer(match.group(2)):
            skill_id = skill_match.group(1).strip()
            skills.append(
                {
                    "id": skill_id,
                    "name": skill_id.replace("-", " ").replace(":", " ").title(),
                    "category": "",
                    "priority": skill_match.group(2).strip(),
                    "learn_time_hrs": int(skill_match.group(3)),
                }
            )
        if skills:
            self._skill_maps[goal_id] = skills


def _skills_for_with_level4(self: GoalTaxonomyParser, goal_id: str) -> List[Dict]:
    exact = self._skill_maps.get(goal_id)
    if exact is not None:
        return list(exact)

    if "." not in goal_id:
        parent_prefix = f"{goal_id}."
        merged: "OrderedDict[str, Dict]" = OrderedDict()
        for subgoal_id in sorted(self._skill_maps):
            if not subgoal_id.startswith(parent_prefix):
                continue
            for skill in self._skill_maps[subgoal_id]:
                merged.setdefault(skill["id"], dict(skill))
        if merged:
            return list(merged.values())

    return _ORIGINAL_SKILLS_FOR(self, goal_id)


GoalTaxonomyParser._parse_skill_mappings = _parse_skill_mappings_with_level4
GoalTaxonomyParser.skills_for = _skills_for_with_level4


# Legacy names used by the historical consistency suite remain accepted, but
# canonical taxonomy names continue to win exact matching first.
_LEGACY_GOAL_ALIASES = {
    "memory agent": "G05",
    "workflow automation agent": "G06",
    "security audit agent": "G07",
    "analytics agent": "G10",
    "model fine-tuning pipeline": "G11",
}
_ORIGINAL_RESOLVE = GoalTaxonomyParser.resolve


def _resolve_with_legacy_aliases(self: GoalTaxonomyParser, query: str):
    resolved = _ORIGINAL_RESOLVE(self, query)
    if resolved is not None:
        return resolved
    return _LEGACY_GOAL_ALIASES.get(query.strip().lower())


GoalTaxonomyParser.resolve = _resolve_with_legacy_aliases
