"""Service for calculating PC hardware energy consumption based on realistic workload profiles."""
import json
from pathlib import Path
from typing import List, Dict, Any
from ecowatt.models.pc_component import PCComponent, PCUsageProfile
from ecowatt.services.cost_calculator import calculate_cost


def load_default_pc_components(json_path: Path = None) -> Dict[str, List[PCComponent]]:
    """Loads default PC components catalog from JSON."""
    if json_path is None:
        json_path = Path(__file__).parent.parent / "data" / "pc_components.json"

    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    catalog = {}
    for cat_name, items in raw.items():
        catalog[cat_name] = [
            PCComponent(
                id=item["id"],
                name=item["name"],
                category=item["category"],
                tdp_watts=item["tdp_watts"],
                idle_watts=item["idle_watts"],
                typical_load_watts=item["typical_load_watts"],
                gaming_load_watts=item["gaming_load_watts"],
            )
            for item in items
        ]
    return catalog


def calculate_pc_energy(
    components: List[PCComponent],
    profile: PCUsageProfile,
    days_per_month: float = 30.0,
    psu_efficiency: float = 0.85,
    tariff: float = 0.85,
) -> Dict[str, Any]:
    """Calculates PC power demand and energy consumption weighted by activity hours.

    Parameters:
    - components: List of selected components (CPU, GPU, RAM, Storage, etc.)
    - profile: Hours per day spent in study, gaming, light use and standby.
    - days_per_month: Days per month the PC is used (default 30).
    - psu_efficiency: Power Supply Unit efficiency factor (e.g. 0.85 for 80 Plus Bronze/Gold).
    - tariff: Electricity tariff in R$/kWh.
    """
    if psu_efficiency <= 0 or psu_efficiency > 1.0:
        raise ValueError("A eficiência da fonte deve estar entre 0.1 e 1.0.")
    if days_per_month < 0 or days_per_month > 31:
        raise ValueError("Os dias de uso no mês devem estar entre 0 e 31.")

    # Sum component draws under each operational mode
    total_tdp = sum(c.tdp_watts for c in components)
    total_idle_raw = sum(c.idle_watts for c in components)
    total_study_raw = sum(c.typical_load_watts for c in components)
    total_gaming_raw = sum(c.gaming_load_watts for c in components)

    # Standby base draw (motherboard/USB powered when PC is soft-off) ~ 3-5W
    standby_raw = 4.0 if profile.standby_off_hours > 0 else 0.0

    # Apply PSU efficiency (wall draw = component draw / psu_efficiency)
    # Note: Monitores normalmente possuem fonte própria, mas na simplificação didática agrupamos com eficiência da tomada
    wall_idle = total_idle_raw / psu_efficiency
    wall_study = total_study_raw / psu_efficiency
    wall_gaming = total_gaming_raw / psu_efficiency
    wall_standby = standby_raw  # Standby is very low direct 5VSB

    # Daily Wh = (Watts * hours)
    daily_wh = (
        (wall_study * profile.study_office_hours)
        + (wall_gaming * profile.gaming_heavy_hours)
        + (wall_idle * profile.light_idle_hours)
        + (wall_standby * profile.standby_off_hours)
    )

    daily_kwh = round(daily_wh / 1000.0, 4)
    monthly_kwh = round(daily_kwh * days_per_month, 4)
    annual_kwh = round(monthly_kwh * 12.0, 4)

    # Weighted average active power
    active_hours = profile.total_active_hours
    avg_active_power = (
        ((wall_study * profile.study_office_hours)
        + (wall_gaming * profile.gaming_heavy_hours)
        + (wall_idle * profile.light_idle_hours)) / active_hours
        if active_hours > 0 else 0.0
    )

    monthly_cost = calculate_cost(monthly_kwh, tariff)
    annual_cost = calculate_cost(annual_kwh, tariff)

    # Component breakdown for gaming peak
    breakdown = [
        {
            "name": c.name,
            "category": c.category,
            "gaming_load_watts": round(c.gaming_load_watts / psu_efficiency, 1),
            "typical_load_watts": round(c.typical_load_watts / psu_efficiency, 1),
        }
        for c in components
    ]

    return {
        "total_tdp": round(total_tdp, 1),
        "peak_gaming_wall_watts": round(wall_gaming, 1),
        "average_active_wall_watts": round(avg_active_power, 1),
        "daily_kwh": daily_kwh,
        "monthly_kwh": monthly_kwh,
        "annual_kwh": annual_kwh,
        "daily_cost": calculate_cost(daily_kwh, tariff),
        "monthly_cost": monthly_cost,
        "annual_cost": annual_cost,
        "breakdown": breakdown,
    }
