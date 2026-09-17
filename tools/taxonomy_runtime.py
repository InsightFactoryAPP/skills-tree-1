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
