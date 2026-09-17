#!/usr/bin/env python3
"""
RankingCalibrator — Sprint C-08

Calibrates the Skills Tree architect recommendation ranking using
empirical signal from evaluation/results.json (Sprint C-07).

Three calibration layers (applied in order):
  1. Global penalties — demote chronically over-recommended skills
  2. Global boosts    — promote chronically under-recommended skills
  3. Goal-specific    — cluster-level adjustments (G01, G03, G07, G10, G11)
  4. Keyword layer    — goal-text keyword detection for fine-grained sub-goal tuning

Usage:
    from tools.ranking_calibrator import RankingCalibrator
    cal = RankingCalibrator()
    ranked_skills = cal.calibrate(ranked_skills, goal_id="G10", goal_text="Analytics Agent")
"""

from __future__ import annotations
from typing import Dict, List, Tuple, Optional

GLOBAL_PENALTIES: Dict[str, float] = {
    "skill:llm-orchestration": -0.16,
    "skill:context-management": -0.08,
    "skill:api-integration": -0.06,
    "skill:function-calling": -0.06,
    "skill:web-scraping": -0.10,
}

GLOBAL_BOOSTS: Dict[str, float] = {
    "skill:prompt-engineering": +0.18,
    "skill:rag-retrieval": +0.14,
    "skill:browser-automation": +0.10,
    "skill:embedding-generation": +0.10,
    "skill:workflow-automation": +0.06,
}

GOAL_ADJUSTMENTS: Dict[str, Dict[str, float]] = {
    "G01": {"skill:llm-orchestration": -0.18},
    "G03": {
        "skill:llm-orchestration": -0.15,
        "skill:api-integration": -0.12,
        "skill:function-calling": -0.08,
        "skill:rag-retrieval": +0.10,
        "skill:prompt-engineering": +0.10,
    },
    "G07": {
        "skill:browser-automation": +0.20,
        "skill:web-scraping": +0.12,
        "skill:llm-orchestration": -0.10,
        "skill:context-management": -0.08,
    },
    "G10": {
        "skill:rag-retrieval": +0.25,
        "skill:prompt-engineering": +0.20,
        "skill:context-management": +0.10,
        "skill:embedding-generation": +0.10,
        "skill:data-extraction": -0.03,
        "skill:web-scraping": -0.08,
    },
    "G11": {
        "skill:web-scraping": -0.20,
        "skill:browser-automation": -0.10,
        "skill:prompt-engineering": +0.15,
        "skill:code-generation": +0.12,
        "skill:llm-orchestration": +0.08,
    },
}

KEYWORD_ADJUSTMENTS: Dict[str, Dict[str, float]] = {
    "memory": {"skill:context-management": +0.30, "skill:embedding-generation": +0.15,
               "skill:web-scraping": -0.30, "skill:data-extraction": -0.20},
    "assistant": {"skill:context-management": +0.20, "skill:rag-retrieval": +0.15},
    "analytics": {"skill:prompt-engineering": +0.25, "skill:context-management": +0.20,
                   "skill:rag-retrieval": +0.20, "skill:web-scraping": -0.20},
    "report": {"skill:prompt-engineering": +0.25, "skill:context-management": +0.20,
               "skill:rag-retrieval": +0.20, "skill:web-scraping": -0.20},
    "financial": {"skill:prompt-engineering": +0.20, "skill:rag-retrieval": +0.25,
                  "skill:context-management": +0.20, "skill:web-scraping": -0.25},
    "etl": {"skill:data-extraction": +0.10, "skill:workflow-automation": +0.15,
            "skill:rag-retrieval": -0.10, "skill:embedding-generation": -0.05},
    "security": {"skill:browser-automation": +0.35, "skill:web-scraping": +0.20,
                 "skill:api-integration": -0.30, "skill:context-management": -0.20,
                 "skill:llm-orchestration": -0.25},
    "audit": {"skill:browser-automation": +0.35, "skill:web-scraping": +0.20,
              "skill:api-integration": -0.30, "skill:context-management": -0.20},
    "social": {"skill:prompt-engineering": +0.20, "skill:api-integration": +0.20,
               "skill:browser-automation": -0.05, "skill:context-management": -0.15},
    "collection": {"skill:api-integration": +0.20, "skill:browser-automation": -0.10},
    "aggregator": {"skill:embedding-generation": +0.25, "skill:context-management": +0.20,
                   "skill:browser-automation": -0.15},
    "content creation": {"skill:rag-retrieval": +0.30, "skill:embedding-generation": +0.20,
                          "skill:function-calling": -0.20, "skill:error-recovery": -0.15},
    "sales": {"skill:rag-retrieval": +0.30, "skill:context-management": +0.20,
              "skill:code-generation": -0.25, "skill:error-recovery": -0.10},
    "slack": {"skill:function-calling": +0.10, "skill:workflow-automation": -0.25,
              "skill:llm-orchestration": -0.20},
    "fine-tun": {"skill:data-extraction": +0.15, "skill:embedding-generation": +0.15,
                 "skill:api-integration": -0.20, "skill:context-management": -0.10},
    "pipeline": {"skill:data-extraction": +0.10, "skill:workflow-automation": +0.15},
}


class RankingCalibrator:
    """Apply calibration weights to a pre-scored skill list."""

    def __init__(
        self,
        global_penalties: Optional[Dict[str, float]] = None,
        global_boosts: Optional[Dict[str, float]] = None,
        goal_adjustments: Optional[Dict[str, Dict[str, float]]] = None,
        keyword_adjustments: Optional[Dict[str, Dict[str, float]]] = None,
    ):
        self._penalties = global_penalties or GLOBAL_PENALTIES
        self._boosts = global_boosts or GLOBAL_BOOSTS
        self._goal_adj = goal_adjustments or GOAL_ADJUSTMENTS
        self._kw_adj = keyword_adjustments or KEYWORD_ADJUSTMENTS

    def calibrate(self, skills: List, goal_id: str = "", goal_text: str = "") -> List[Tuple[str, float]]:
        scored = self._normalise_input(skills)
        calibrated = self._apply_weights(scored, goal_id, goal_text)
        return sorted(calibrated.items(), key=lambda x: (-x[1], x[0]))

    def calibrate_ids(self, skills: List, goal_id: str = "", goal_text: str = "") -> List[str]:
        return [sid for sid, _ in self.calibrate(skills, goal_id, goal_text)]

    def describe_adjustments(self, goal_id: str = "", goal_text: str = "") -> Dict:
        adjustments: Dict[str, float] = {}
        for sid, delta in self._penalties.items():
            adjustments[sid] = adjustments.get(sid, 0.0) + delta * 10
        for sid, delta in self._boosts.items():
            adjustments[sid] = adjustments.get(sid, 0.0) + delta * 10
        for sid, delta in self._goal_adj.get(goal_id, {}).items():
            adjustments[sid] = adjustments.get(sid, 0.0) + delta * 10
        if goal_text:
            goal_lower = goal_text.lower()
            for kw, kw_boosts in self._kw_adj.items():
                if kw in goal_lower:
                    for sid, delta in kw_boosts.items():
                        adjustments[sid] = adjustments.get(sid, 0.0) + delta * 10
        return adjustments

    @staticmethod
    def _normalise_input(skills: List) -> Dict[str, float]:
        """Normalize inputs without giving ID-only callers a positional score advantage."""
        scored: Dict[str, float] = {}
        for item in skills:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                sid, base = item[0], float(item[1])
            else:
                sid, base = str(item), 0.0
            scored[sid] = base
        return scored

    def _apply_weights(self, scores: Dict[str, float], goal_id: str, goal_text: str) -> Dict[str, float]:
        out = dict(scores)
        for sid, delta in self._penalties.items():
            if sid in out:
                out[sid] += delta * 10
        for sid, delta in self._boosts.items():
            if sid in out:
                out[sid] += delta * 10
        for sid, delta in self._goal_adj.get(goal_id, {}).items():
            if sid in out:
                out[sid] += delta * 10
        if goal_text:
            goal_lower = goal_text.lower()
            for kw, kw_boosts in self._kw_adj.items():
                if kw in goal_lower:
                    for sid, delta in kw_boosts.items():
                        if sid in out:
                            out[sid] += delta * 10
        return out
