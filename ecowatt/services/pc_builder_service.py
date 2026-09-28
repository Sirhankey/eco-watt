"""Pure helpers for PC setup summaries and comparisons."""
from typing import Any, Iterable

from ecowatt.models.pc_component import PCComponent, PCUsageProfile
from ecowatt.services.pc_energy_service import calculate_pc_energy


def calculate_setup(components: Iterable[PCComponent], profile: PCUsageProfile, days_per_month: float, tariff: float, psu_efficiency: float) -> dict[str, Any]:
    component_list = list(components)
    if not component_list:
        raise ValueError("Selecione pelo menos um componente para calcular.")
    return calculate_pc_energy(component_list, profile, days_per_month, psu_efficiency, tariff)


def compare_setups(first: dict[str, Any], second: dict[str, Any]) -> dict[str, float]:
    """Return absolute deltas, preserving which setup is more economical in the UI."""
    return {
        "peak_power_watts": abs(float(first["peak_gaming_wall_watts"]) - float(second["peak_gaming_wall_watts"])),
        "monthly_kwh": abs(float(first["monthly_kwh"]) - float(second["monthly_kwh"])),
        "monthly_cost": abs(float(first["monthly_cost"]) - float(second["monthly_cost"])),
        "annual_cost": abs(float(first["annual_cost"]) - float(second["annual_cost"])),
    }
