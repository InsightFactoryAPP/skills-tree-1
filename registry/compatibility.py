"""Deterministic typed runtime access to validated compatibility facts."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, TypedDict

from jsonschema import Draft202012Validator


class CompatibilityTarget(TypedDict):
    """Normative runtime target shape for a compatibility record."""

    type: str
    id: str


class CompatibilityRecord(TypedDict):
    """Normative runtime shape for a registered Compatibility record."""

    id: str
    version: str
    name: str
    subject: str
    target: CompatibilityTarget
    status: str
    evidence: list[str]
    constraints: list[str]
    limitations: list[str]
    provenance: dict[str, Any]


class CompatibilityRuntime:
    """Read-only typed access to validated compatibility facts."""

    def __init__(self, registry_data: dict[str, Any], schema: dict[str, Any]) -> None:
        self._data = registry_data
        records = self._data.get("entities", {}).get("compatibilities")
        if not isinstance(records, list):
            raise ValueError("Registry must contain a compatibilities collection")
        validator = Draft202012Validator(schema)
        evidence = {
            item["id"]: item
            for item in self._data["entities"].get("evidence", [])
        }
        entities = {
            item["id"]: entity_type.rstrip("s")
            for entity_type, items in self._data["entities"].items()
            for item in items
        }
        for record in records:
            validator.validate({"contract_version": "1.0", "compatibility": record})
            if record["subject"] not in entities:
                raise ValueError(f"Unknown compatibility subject: {record['subject']}")
            target = record["target"]
            if target["id"] not in entities:
                raise ValueError(f"Unknown compatibility target: {target['id']}")
            if entities[target["id"]] != target["type"]:
                raise ValueError(
                    f"Compatibility target type mismatch: {target['id']} "
                    f"declared as {target['type']} but registry entity is {entities[target['id']]}"
                )
            unsupported = [
                evidence_id
                for evidence_id in record["evidence"]
                if record["id"] not in evidence.get(evidence_id, {}).get("supports", [])
            ]
            if unsupported:
                raise ValueError(
                    f"Compatibility evidence does not support {record['id']}: "
                    + ", ".join(sorted(unsupported))
                )

    def resolve_compatibility(self, compatibility_id: str) -> CompatibilityRecord:
        """Return one validated Compatibility record by canonical ID."""
        matches = [
            item
            for item in self._data["entities"]["compatibilities"]
            if item["id"] == compatibility_id
        ]
        if not matches:
            raise KeyError(f"Unknown compatibility: {compatibility_id}")
        return deepcopy(matches[0])

    def compatibility_for(
        self,
        subject_id: str,
        target_type: str | None = None,
        target_id: str | None = None,
    ) -> list[CompatibilityRecord]:
        """Return compatibility facts for an entity in deterministic order."""
        records = [
            item
            for item in self._data["entities"]["compatibilities"]
            if item["subject"] == subject_id
        ]
        if target_type is not None:
            records = [item for item in records if item["target"]["type"] == target_type]
        if target_id is not None:
            records = [item for item in records if item["target"]["id"] == target_id]
        return deepcopy(sorted(records, key=lambda item: item["id"]))
