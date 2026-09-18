"""Service for loading educational presets and validating against real energy bills."""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from ecowatt.models.appliance import Appliance
from ecowatt.services.cost_calculator import calculate_cost


def load_presets(json_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Loads all educational household presets from JSON."""
    if json_path is None:
        json_path = Path(__file__).parent.parent / "data" / "presets.json"

    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_preset_by_id(preset_id: str, json_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    """Retrieves a specific preset by ID."""
    presets = load_presets(json_path)
    for p in presets:
        if p["id"] == preset_id:
            return p
    return None


def convert_preset_to_appliances(preset_dict: Dict[str, Any]) -> List[Appliance]:
    """Converts a preset's appliance dictionaries into Appliance domain models."""
    appliances = []
    for item in preset_dict.get("appliances", []):
        appliances.append(
            Appliance(
                id=item["id"],
                name=item["name"],
                power_watts=float(item["power_watts"]),
                hours_per_day=float(item["hours_per_day"]),
                days_per_month=float(item.get("days_per_month", 30.0)),
                category=item.get("category", "Geral"),
            )
        )
    return appliances


def load_default_appliances(json_path: Optional[Path] = None) -> List[Appliance]:
    """Loads default catalog of standard appliances from appliances.json."""
    if json_path is None:
        json_path = Path(__file__).parent.parent / "data" / "appliances.json"

    with open(json_path, "r", encoding="utf-8") as f:
        raw_items = json.load(f)

    return [
        Appliance(
            id=item["id"],
            name=item["name"],
            power_watts=float(item["power_watts"]),
            hours_per_day=float(item["default_hours_per_day"]),
            days_per_month=float(item.get("default_days_per_month", 30.0)),
            category=item.get("category", "Geral"),
            description=item.get("description"),
        )
        for item in raw_items
    ]


def load_facts(json_path: Optional[Path] = None) -> List[Dict[str, str]]:
    """Loads educational Did you know? facts."""
    if json_path is None:
        json_path = Path(__file__).parent.parent / "data" / "facts.json"

    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_against_real_bill(
    simulated_monthly_kwh: float,
    real_bill_reais: float,
    tariff: float,
) -> Dict[str, Any]:
    """Compares simulated household consumption against an actual electricity bill.

    Returns differences, inferred real kWh, and educational explanations.
    """
    if simulated_monthly_kwh < 0 or real_bill_reais < 0 or tariff <= 0:
        raise ValueError("Valores de consumo, fatura e tarifa devem ser positivos.")

    inferred_real_kwh = round(real_bill_reais / tariff, 1)
    simulated_cost = calculate_cost(simulated_monthly_kwh, tariff)

    diff_kwh = round(inferred_real_kwh - simulated_monthly_kwh, 1)
    diff_cost = round(real_bill_reais - simulated_cost, 2)

    if abs(diff_kwh) <= 15:
        verdict = "EXACT"
        explanation = (
            "Sua simulação está muito próxima da sua fatura real! Isso indica que seus principais aparelhos "
            "e tempos de uso foram bem estimados."
        )
    elif diff_kwh > 0:
        verdict = "REAL_HIGHER"
        explanation = (
            f"Sua fatura real registrou aproximadamente {diff_kwh} kWh (R$ {diff_cost}) a mais que a simulação. "
            "Possíveis motivos: consumo em stand-by (aparelhos na tomada), chuveiros operando na potência máxima no inverno, "
            "geladeira com borracha gasta ou aparelhos que não foram adicionados à lista."
        )
    else:
        verdict = "SIMULATED_HIGHER"
        abs_kwh = abs(diff_kwh)
        abs_cost = abs(diff_cost)
        explanation = (
            f"A simulação resultou em {abs_kwh} kWh (R$ {abs_cost}) a mais que a fatura real. "
            "Isso geralmente acontece quando superestimamos as horas diárias de uso de televisores, "
            "ventiladores ou computadores."
        )

    return {
        "simulated_monthly_kwh": simulated_monthly_kwh,
        "simulated_cost": simulated_cost,
        "real_bill_reais": real_bill_reais,
        "inferred_real_kwh": inferred_real_kwh,
        "diff_kwh": diff_kwh,
        "diff_cost": diff_cost,
        "verdict": verdict,
        "explanation": explanation,
    }
