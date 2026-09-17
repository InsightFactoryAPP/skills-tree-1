#!/usr/bin/env python3
"""POST /recommend — calibrated skill recommendations for a goal."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from api.dependencies import get_engine, get_calibrator
from api.models import RecommendRequest, RecommendResponse, SkillSummary

router = APIRouter(tags=["Recommendations"])


@router.post(
    "/recommend",
    response_model=RecommendResponse,
    summary="Get skill recommendations",
    description=(
        "Resolves the goal against GOAL_TAXONOMY.md, scores skills via the "
        "RecommendationEngine, then re-ranks using RankingCalibrator (C-08). "
        "Skills are split into required (critical/high priority) and optional "
        "(medium/low priority)."
    ),
)
def recommend(body: RecommendRequest) -> RecommendResponse:
    engine = get_engine()
    calibrator = get_calibrator()

    result = engine.recommend(body.goal)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    goal_id = result["goal_id"]
    goal_name = result["goal_name"]

    # Calibrate the real engine scores. Passing IDs alone would cause the
    # calibrator to manufacture positional base scores (10, 9, 8, ...).
    req_ranked = calibrator.calibrate(
        [(s["id"], s["score"]) for s in result["required_skills"]],
        goal_id=goal_id,
        goal_text=goal_name,
    )
    opt_ranked = calibrator.calibrate(
        [(s["id"], s["score"]) for s in result["optional_skills"]],
        goal_id=goal_id,
        goal_text=goal_name,
    )

    req_map = {s["id"]: s for s in result["required_skills"]}
    opt_map = {s["id"]: s for s in result["optional_skills"]}

    def _to_summary(sid: str, rank: int, calibrated_score: float, node_map: dict) -> SkillSummary:
        s = node_map.get(sid, {"id": sid, "name": sid})
        return SkillSummary(
            id=sid,
            name=s.get("name", sid),
            rank=rank,
            score=calibrated_score,
            confidence=s.get("confidence"),
            priority=s.get("priority"),
            learn_time=s.get("learn_time"),
            explanation=s.get("explanation", []),
            evidence=s.get("evidence", {}),
            score_breakdown=s.get("score_breakdown", {}),
            stability=s.get("stability"),
        )

    required_skills = [
        _to_summary(sid, i + 1, score, req_map)
        for i, (sid, score) in enumerate(req_ranked)
    ]
    optional_skills = [
        _to_summary(sid, len(req_ranked) + i + 1, score, opt_map)
        for i, (sid, score) in enumerate(opt_ranked)
    ]

    # Filter required skills to the available time budget. This remains a
    # presentation constraint until constraints are moved into the application layer.
    if body.time_budget_hours is not None:
        taxonomy_map = {s["id"]: s for s in result["taxonomy_skills"]}
        budget = body.time_budget_hours
        spent = 0
        filtered_req = []
        for s in required_skills:
            hrs = taxonomy_map.get(s.id, {}).get("learn_time_hrs", 0)
            if spent + hrs <= budget:
                filtered_req.append(s)
                spent += hrs
        required_skills = filtered_req

    learning_path = [
        n.get("name", n["id"]) if isinstance(n, dict) else str(n)
        for n in result["learning_path"]
    ]

    total_hrs = sum(
        s.get("learn_time_hrs", 0) for s in result.get("taxonomy_skills", [])
    )

    return RecommendResponse(
        goal=goal_name,
        goal_id=goal_id,
        confidence_score=result["confidence_score"],
        required_skills=required_skills,
        optional_skills=optional_skills,
        learning_path=learning_path,
        deployment=result.get("deployment"),
        complexity=result.get("complexity"),
        estimated_learn_hours=total_hrs or None,
        calibration_applied=True,
    )
