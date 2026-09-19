"""Deterministic typed runtime access to registry Evidence records."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, TypedDict


class EvidenceRecord(TypedDict):
    """Normative runtime shape for a registered Evidence record."""

    id: str
    version: str
    name: str
    type: str
    source: str
    supports: list[str]
    provenance: dict[str, Any]


class EvidenceRuntime:
    """Read-only typed access to validated Evidence records."""

    def __init__(self, registry_data: dict[str, Any]) -> None:
        self._data = registry_data
        evidence = self._data.get("entities", {}).get("evidence")
        if not isinstance(evidence, list):
            raise ValueError("Registry must contain an evidence collection")

    def resolve_evidence(self, evidence_id: str) -> EvidenceRecord:
        """Return one Evidence record by canonical ID."""
        matches = [
            item
            for item in self._data["entities"]["evidence"]
            if item["id"] == evidence_id
        ]
        if not matches:
            raise KeyError(f"Unknown evidence: {evidence_id}")
        return deepcopy(matches[0])

    def evidence_for_entity(self, entity_id: str) -> list[EvidenceRecord]:
        """Return Evidence records supporting an entity in deterministic order."""
        records = [
            item
            for item in self._data["entities"]["evidence"]
            if entity_id in item.get("supports", [])
        ]
        return deepcopy(sorted(records, key=lambda item: item["id"]))
