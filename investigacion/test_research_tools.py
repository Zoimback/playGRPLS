from pathlib import Path

from investigacion.common import keyword_hits, load_json, model_inventory, redact


def test_inventory_discovers_models_and_data_shape():
    response = load_json(Path(__file__).parent / "fixtures" / "backbone_minimo.json")

    inventory = model_inventory(response)

    assert len(inventory) == 2
    assert inventory[0]["data_keys"] == ["population", "production", "resources"]


def test_keyword_hits_reports_research_candidates():
    response = {"backbone": {"models": [], "collections": [{"model_class_name": "FarmTowns", "data": []}]}}

    assert keyword_hits(response, ("farm",)) == [{"section": "collections", "index": 0, "matches": ["farm"], "class_name": "FarmTowns"}]


def test_redact_removes_sensitive_values_recursively():
    value = redact({"csrfToken": "secret", "nested": [{"password": "hidden"}], "safe": 1})

    assert value == {"csrfToken": "[REDACTED]", "nested": [{"password": "[REDACTED]"}], "safe": 1}