import pytest

from ecowatt.models.appliance import Appliance
from ecowatt.services.personal_preset_service import (
    apply_personal_preset,
    compare_authorized_presets,
    save_personal_preset,
)


def appliances():
    return [Appliance("lamp", "Lampada", 10, 5, 30, "Sala")]


def test_personal_preset_snapshots_and_applies_copy():
    preset = save_personal_preset("Casa leve", appliances(), 0.85, "user-1")
    restored = apply_personal_preset(preset)
    assert preset["monthly_kwh"] == 1.5
    assert preset["participant_id"] == "user-1"
    assert restored[0].name == "Lampada"
    preset["items"][0]["name"] = "Alterado"
    assert restored[0].name == "Lampada"


def test_event_comparison_requires_consent_and_handles_tie():
    first = save_personal_preset("A", appliances(), 0.85, "a", True, "event", "Casa A")
    second = save_personal_preset("B", appliances(), 0.85, "b", True, "event", "Casa B")
    ranking = compare_authorized_presets([first, second])
    assert ranking["lowest"]["monthly_kwh"] == ranking["highest"]["monthly_kwh"]
    assert compare_authorized_presets([first], event_enabled=False) == {"lowest": None, "highest": None}


def test_event_visibility_without_consent_is_rejected():
    with pytest.raises(ValueError, match="consentimento"):
        save_personal_preset("Casa", appliances(), 0.85, "user-1", False, "event", "Casa")
