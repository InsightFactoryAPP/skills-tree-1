"""Compatibility loader for the legacy architect implementation.

The preserved implementation contains Python 3.11-incompatible f-string
expressions. Keep the implementation intact and normalize those syntax
patterns at load time so existing imports retain the same public API.
"""
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
import sys

_SOURCE = Path(__file__).with_name("architect_source.py")


class _CompatibilityLoader(SourceFileLoader):
    def get_data(self, path):
        data = super().get_data(path)
        if Path(path).resolve() != _SOURCE.resolve():
            return data
        text = data.decode("utf-8")
        replacements = {
            'print(f"\\n{\'\\u2500\'*70}\\nREQUIRED SKILLS (sorted by score \\u2193):")':
                'separator = "─" * 70\n    print(f"\\n{separator}\\nREQUIRED SKILLS (sorted by score ↓):")',
            'print(f"\\n{\'\\u2500\'*70}\\nMISMATCH REPORT ({len(mm)} fields differ stored vs derived):")':
                'separator = "─" * 70\n        print(f"\\n{separator}\\nMISMATCH REPORT ({len(mm)} fields differ stored vs derived):")',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text.encode("utf-8")


_loader = _CompatibilityLoader(__name__, str(_SOURCE))
_spec = spec_from_loader(__name__, _loader)
_module = module_from_spec(_spec)
sys.modules[__name__] = _module
_loader.exec_module(_module)
globals().update(_module.__dict__)


# Calibration is part of the recommendation contract, not an API-only
# presentation step. Keeping it here makes Engine/API/MCP ordering identical.
_RecommendationEngine = RecommendationEngine
_original_recommend = _RecommendationEngine.recommend


def _calibrated_recommend(self, goal_query):
    result = _original_recommend(self, goal_query)
    if "error" in result:
        return result

    from tools.ranking_calibrator import RankingCalibrator

    calibrator = RankingCalibrator()
    goal_id = result["goal_id"]
    goal_name = result["goal_name"]

    def apply(skills):
        ranked = calibrator.calibrate(
            [(skill["id"], skill["score"]) for skill in skills],
            goal_id=goal_id,
            goal_text=goal_name,
        )
        by_id = {skill["id"]: skill for skill in skills}
        ordered = []
        for rank, (skill_id, score) in enumerate(ranked, start=1):
            skill = dict(by_id[skill_id])
            skill["score"] = score
            skill["rank"] = rank
            ordered.append(skill)
        return ordered

    required = apply(result["required_skills"])
    optional = apply(result["optional_skills"])
    for rank, skill in enumerate(required + optional, start=1):
        skill["rank"] = rank
    result["required_skills"] = required
    result["optional_skills"] = optional
    result["calibration_applied"] = True
    return result


_RecommendationEngine.recommend = _calibrated_recommend
RecommendationEngine = _RecommendationEngine
