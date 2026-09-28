import pytest

from ecowatt.models.catalog import CatalogAppliance, CatalogPCComponent
from ecowatt.services.catalog_validation import find_duplicate, normalize_name, validate_submission_payload


def test_normalize_name_ignores_case_accents_spacing_and_punctuation():
    assert normalize_name("  Lâmpada-LED!! ") == "lampada led"


def test_catalog_models_reject_invalid_numeric_and_markup_values():
    with pytest.raises(ValueError):
        CatalogAppliance("a", "Chuveiro", "Banheiro", -1, 1)
    with pytest.raises(ValueError):
        CatalogPCComponent("c", "GPU", "gpus", 100, 10, 20, 30, "<script>")


def test_duplicate_key_detects_equivalent_appliance():
    existing = {"name": "Lâmpada LED", "category": "Sala", "power_watts": 10, "hours_per_day": 5, "days_per_month": 30}
    candidate = {"name": " lampada-led ", "category": "Sala", "power_watts": 10, "hours_per_day": 5, "days_per_month": 30}
    assert find_duplicate([existing], candidate, "appliance") == existing


def test_submission_payload_validates_supported_kind():
    payload = validate_submission_payload("appliance", {"name": "Ventilador", "category": "Sala", "power_watts": 80, "hours_per_day": 4, "days_per_month": 30})
    assert payload["name"] == "Ventilador"
    with pytest.raises(ValueError):
        validate_submission_payload("appliance", {"name": "<b>ruim</b>", "category": "Sala", "power_watts": 80, "hours_per_day": 4, "days_per_month": 30})
