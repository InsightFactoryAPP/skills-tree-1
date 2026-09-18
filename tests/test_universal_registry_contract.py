"""Regression tests for the Universal Agent Skills Registry contract."""

import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "meta" / "universal-registry.schema.json"


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def test_universal_registry_schema_is_valid_json_and_versioned() -> None:
    schema = load_schema()

    Draft202012Validator.check_schema(schema)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["properties"]["schema_version"]["const"] == "1.0"
    assert schema["type"] == "object"
    assert schema["required"] == ["schema_version", "entity_types", "relationship_types"]


def test_universal_registry_defines_all_core_entity_types() -> None:
    schema = load_schema()
    entity_types = schema["properties"]["entity_types"]["properties"]
    required = schema["properties"]["entity_types"]["required"]

    expected = {
        "goal",
        "capability",
        "skill",
        "implementation",
        "tool",
        "model",
        "platform",
        "framework",
        "adapter",
        "protocol",
        "runtime",
        "evidence",
        "benchmark",
        "architecture",
        "compatibility",
    }

    assert set(required) == expected
    assert set(entity_types) == expected


def test_universal_registry_skill_is_platform_agnostic() -> None:
    skill = load_schema()["$defs"]["skillDefinition"]

    skill_properties = skill["allOf"][1]["properties"]
    assert skill_properties["canonical"]["const"] is True
    assert skill_properties["capabilities"]["uniqueItems"] is True
    assert skill_properties["implementations"]["uniqueItems"] is True


def test_universal_registry_relationship_vocabulary_is_explicit() -> None:
    schema = load_schema()
    relationships = schema["properties"]["relationship_types"]["items"]["enum"]

    required_relationships = {
        "requires_capability",
        "enables_skill",
        "realized_by",
        "implemented_with",
        "adapted_to",
        "supported_by_model",
        "alternative_to",
        "supported_by_evidence",
        "validated_by_benchmark",
        "constrained_by",
        "composes_with",
        "depends_on",
    }

    assert required_relationships <= set(relationships)
