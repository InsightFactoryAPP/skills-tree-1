from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class UniversalRegistry:
    """Read-only runtime access to the universal registry."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._data = json.loads(self.path.read_text(encoding="utf-8"))
        self._validate_integrity()

    def resolve_goal(self, goal_id: str) -> dict[str, Any]:
        for goal in self._data["entities"]["goals"]:
            if goal["id"] == goal_id:
                return goal
        raise KeyError(goal_id)

    def skills_for_goal(self, goal_id: str) -> list[str]:
        goal = self.resolve_goal(goal_id)
        skills: list[str] = []
        for capability_id in goal["capabilities"]:
            capability = self._find("capabilities", capability_id)
            skills.extend(capability["skills"])
        return sorted(set(skills))

    def compatibility_for(self, subject_id: str, target_type: str | None = None, target_id: str | None = None) -> list[dict[str, Any]]:
        records = [x for x in self._data["entities"]["compatibilities"] if x["subject"] == subject_id]
        if target_type is not None:
            records = [x for x in records if x["target"]["type"] == target_type]
        if target_id is not None:
            records = [x for x in records if x["target"]["id"] == target_id]
        return sorted(records, key=lambda x: x["id"])

    def graph_edges(self) -> list[dict[str, Any]]:
        """Return validated typed universal-graph edges in deterministic order."""
        graph = getattr(self, "_graph_data", None)
        if graph is None:
            graph_path = self.path.parent.parent / "graph" / "universal_graph.json"
            graph = json.loads(graph_path.read_text(encoding="utf-8"))
        entities = self._data["entities"]
        collection_types = {
            "goals": "goal",
            "capabilities": "capability",
            "skills": "skill",
            "implementations": "implementation",
            "tools": "tool",
            "models": "model",
            "platforms": "platform",
            "frameworks": "framework",
            "protocols": "protocol",
            "runtimes": "runtime",
            "adapters": "adapter",
            "evidence": "evidence",
            "benchmarks": "benchmark",
            "architectures": "architecture",
            "compatibilities": "compatibility",
        }
        by_id = {
            record["id"]: collection_types[entity_type]
            for entity_type, records in entities.items()
            for record in records
        }
        edges = graph.get("edges", [])
        for edge in edges:
            if by_id.get(edge["source"]) != edge["source_type"] or by_id.get(edge["target"]) != edge["target_type"]:
                raise ValueError(f"Invalid typed graph endpoint: {edge['source']} -> {edge['target']}")
            if edge["source"] == edge["target"]:
                raise ValueError(f"Graph self-loop: {edge['source']}")
        return sorted(edges, key=lambda x: (x["source"], x["relationship_type"], x["target"]))

    def _find(self, collection: str, entity_id: str) -> dict[str, Any]:
        for record in self._data["entities"][collection]:
            if record["id"] == entity_id:
                return record
        raise KeyError(entity_id)

    def _validate_integrity(self) -> None:
        entities = self._data.get("entities")
        if not isinstance(entities, dict):
            raise ValueError("Registry must contain an entities object")

        ids: set[str] = set()
        for entity_type, records in entities.items():
            if not isinstance(records, list):
                raise ValueError(f"Entity collection must be a list: {entity_type}")
            for record in records:
                if not isinstance(record, dict):
                    raise ValueError(f"Entity record must be an object: {entity_type}")
                entity_id = record.get("id")
                if not isinstance(entity_id, str) or not entity_id:
                    raise ValueError(f"Entity ID must be a non-empty string: {entity_type}")
                if entity_id in ids:
                    raise ValueError(f"Duplicate entity ID: {entity_id}")
                ids.add(entity_id)
                if not isinstance(record.get("version"), str) or not record["version"]:
                    raise ValueError(f"Entity version must be a non-empty string: {entity_id}")
                if not isinstance(record.get("provenance"), dict):
                    raise ValueError(f"Entity provenance must be an object: {entity_id}")

        for goal in entities.get("goals", []):
            for capability_id in goal.get("capabilities", []):
                self._find("capabilities", capability_id)
        for capability in entities.get("capabilities", []):
            for skill_id in capability.get("skills", []):
                self._find("skills", skill_id)
            for implementation_id in capability.get("implementations", []):
                self._find("implementations", implementation_id)
            for adapter_id in capability.get("adapters", []):
                self._find("adapters", adapter_id)
        for skill in entities.get("skills", []):
            if skill.get("canonical") is not True:
                raise ValueError(f"Universal registry skills must be canonical: {skill['id']}")
            for capability_id in skill.get("capabilities", []):
                self._find("capabilities", capability_id)
            for implementation_id in skill.get("implementations", []):
                self._find("implementations", implementation_id)
        for implementation in entities.get("implementations", []):
            self._find("skills", implementation["skill"])
            for evidence_id in implementation.get("evidence", []):
                self._find("evidence", evidence_id)
        for adapter in entities.get("adapters", []):
            self._find("implementations", adapter["implementation"])
            for target in adapter.get("targets", []):
                collection = target["type"] + "s"
                self._find(collection, target["id"])
            for evidence_id in adapter.get("evidence", []):
                self._find("evidence", evidence_id)
        for compatibility in entities.get("compatibilities", []):
            subject = compatibility["subject"]
            if not any(subject in [r.get("id") for r in entities.get(collection, [])] for collection in ("skills", "implementations", "adapters")):
                raise ValueError(f"Invalid compatibility subject: {subject}")
            target = compatibility["target"]
            self._find(target["type"] + "s", target["id"])
            for evidence_id in compatibility.get("evidence", []):
                self._find("evidence", evidence_id)
