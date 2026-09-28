"""Personal household snapshots and consent-aware comparisons."""
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Iterable, Optional
from uuid import uuid4

from ecowatt.models.appliance import Appliance
from ecowatt.services.energy_calculator import calculate_total_household_consumption


def save_personal_preset(
    name: str,
    appliances: Iterable[Appliance],
    tariff: float,
    participant_id: str,
    comparison_consent: bool = False,
    visibility: str = "private",
    pseudonymous_label: Optional[str] = None,
) -> dict[str, Any]:
    clean_name = name.strip()
    if not clean_name or len(clean_name) > 120:
        raise ValueError("O nome do preset deve ter entre 1 e 120 caracteres.")
    if tariff <= 0:
        raise ValueError("A tarifa deve ser maior que zero.")
    if visibility not in {"private", "event"}:
        raise ValueError("Visibilidade de preset invalida.")
    if visibility == "event" and not comparison_consent:
        raise ValueError("A visibilidade do evento exige consentimento para comparacao.")

    appliance_list = list(appliances)
    result = calculate_total_household_consumption(appliance_list)
    return {
        "id": str(uuid4()),
        "participant_id": participant_id,
        "name": clean_name,
        "tariff": float(tariff),
        "monthly_kwh": float(result["total_monthly_kwh"]),
        "visibility": visibility,
        "comparison_consent": comparison_consent,
        "pseudonymous_label": pseudonymous_label.strip() if pseudonymous_label else None,
        "created_at": datetime.now(timezone.utc),
        "items": [deepcopy(asdict(appliance)) for appliance in appliance_list],
    }


def apply_personal_preset(preset: dict[str, Any]) -> list[Appliance]:
    if preset.get("visibility") not in {"private", "event"}:
        raise ValueError("Preset pessoal invalido.")
    return [Appliance(**deepcopy(item)) for item in preset.get("items", [])]


def compare_authorized_presets(presets: Iterable[dict[str, Any]], event_enabled: bool = True) -> dict[str, Optional[dict[str, Any]]]:
    if not event_enabled:
        return {"lowest": None, "highest": None}
    authorized = [
        preset for preset in presets
        if preset.get("visibility") == "event"
        and preset.get("comparison_consent") is True
        and preset.get("pseudonymous_label")
    ]
    if not authorized:
        return {"lowest": None, "highest": None}
    lowest = min(authorized, key=lambda preset: float(preset["monthly_kwh"]))
    highest = max(authorized, key=lambda preset: float(preset["monthly_kwh"]))
    return {
        "lowest": {"label": lowest["pseudonymous_label"], "monthly_kwh": lowest["monthly_kwh"]},
        "highest": {"label": highest["pseudonymous_label"], "monthly_kwh": highest["monthly_kwh"]},
    }
