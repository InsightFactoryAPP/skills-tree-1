"""Runtime taxonomy adapter.

Preserves GoalTaxonomyParser compatibility while supporting canonical Level-4
mappings and deterministic parent-goal coverage.
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
    _GOAL_BASELINE_MAPPINGS = {
        "G03": [("knowledge-graph-reading", "Critical", 5), ("context-management", "High", 4), ("rag-retrieval", "High", 5)],
        "G04": [("web-search", "Critical", 4), ("web-scraping", "High", 4), ("reasoning-chains", "High", 6)],
        "G05": [("knowledge-graph-reading", "Critical", 5), ("context-management", "High", 4), ("rag-retrieval", "High", 5)],
        "G06": [("planning", "Critical", 5), ("tool-use", "Critical", 6), ("error-recovery", "High", 3)],
        "G07": [("prompt-engineering", "Critical", 4), ("rag-retrieval", "High", 5), ("reasoning-chains", "High", 6)],
        "G08": [("planning", "Critical", 5), ("tool-use", "Critical", 6), ("reasoning-chains", "High", 6)],
        "G09": [("audio-transcription", "Critical", 5), ("reasoning-chains", "High", 6), ("prompt-engineering", "High", 4)],
        "G10": [("structured-output", "Critical", 3), ("reasoning-chains", "High", 6), ("prompt-engineering", "High", 4)],
        "G11": [("code-analysis", "Critical", 8), ("structured-output", "High", 3), ("reasoning-chains", "High", 6)],
        "G12": [("prompt-engineering", "Critical", 4), ("summarization", "High", 4), ("markdown-generation", "High", 2)],
    }

    def __init__(self, taxonomy_path: str):
        super().__init__(taxonomy_path)
        self._parse_level4_subgoals()
        self._ensure_goal_baselines()

    @staticmethod
    def _skill(skill_id: str, priority: str, learn_time_hrs: int) -> Dict:
        return {
            "id": skill_id,
            "name": skill_id.replace("-", " ").replace(":", " ").title(),
            "category": "",
            "priority": priority,
            "learn_time_hrs": learn_time_hrs,
        }

    def _ensure_goal_baselines(self) -> None:
        for goal_id, entries in self._GOAL_BASELINE_MAPPINGS.items():
            if not self._skill_maps.get(goal_id):
                self._skill_maps[goal_id] = [self._skill(*entry) for entry in entries]

    def _parse_level4_subgoals(self) -> None:
        for match in self._SUBGOAL_MAPPING_RE.finditer(self._raw):
            goal_id = match.group(1)
            skills = []
            for skill_match in self._NUMBERED_SKILL_RE.finditer(match.group(2)):
                skills.append(self._skill(skill_match.group(1).strip(), skill_match.group(2).strip(), int(skill_match.group(3))))
            if skills:
                self._skill_maps[goal_id] = skills

    def skills_for(self, goal_id: str) -> List[Dict]:
        exact = self._skill_maps.get(goal_id)
        if exact is not None:
            return list(exact)
        if "." not in goal_id:
            parent_prefix = f"{goal_id}."
            merged: "OrderedDict[str, Dict]" = OrderedDict()
            for subgoal_id in sorted(self._skill_maps):
                if subgoal_id.startswith(parent_prefix):
                    for skill in self._skill_maps[subgoal_id]:
                        merged.setdefault(skill["id"], dict(skill))
            if merged:
                return list(merged.values())
        return super().skills_for(goal_id)


_ORIGINAL_PARSE_SKILL_MAPPINGS = GoalTaxonomyParser._parse_skill_mappings
_ORIGINAL_SKILLS_FOR = GoalTaxonomyParser.skills_for


def _parse_skill_mappings_with_level4(self: GoalTaxonomyParser) -> None:
    _ORIGINAL_PARSE_SKILL_MAPPINGS(self)
    for match in RuntimeGoalTaxonomyParser._SUBGOAL_MAPPING_RE.finditer(self._raw):
        goal_id = match.group(1)
        skills = []
        for skill_match in RuntimeGoalTaxonomyParser._NUMBERED_SKILL_RE.finditer(match.group(2)):
            skills.append(RuntimeGoalTaxonomyParser._skill(skill_match.group(1).strip(), skill_match.group(2).strip(), int(skill_match.group(3))))
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
            if subgoal_id.startswith(parent_prefix):
                for skill in self._skill_maps[subgoal_id]:
                    merged.setdefault(skill["id"], dict(skill))
        if merged:
            return list(merged.values())
        baseline = RuntimeGoalTaxonomyParser._GOAL_BASELINE_MAPPINGS.get(goal_id)
        if baseline:
            return [RuntimeGoalTaxonomyParser._skill(*entry) for entry in baseline]
    return _ORIGINAL_SKILLS_FOR(self, goal_id)


GoalTaxonomyParser._parse_skill_mappings = _parse_skill_mappings_with_level4
GoalTaxonomyParser.skills_for = _skills_for_with_level4

_LEGACY_GOAL_ALIASES = {
    "memory agent": "G03",
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
