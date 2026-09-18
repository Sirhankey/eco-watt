"""Pure functions for electricity cost calculations and financial projections."""
from typing import Dict, Any


def calculate_cost(kwh: float, tariff: float) -> float:
    """Calculates financial cost given energy in kWh and tariff in R$/kWh.

    Formula: kwh * tariff
    """
    if kwh < 0:
        raise ValueError("O consumo em kWh não pode ser negativo.")
    if tariff < 0:
        raise ValueError("A tarifa não pode ser negativa.")

    return round(kwh * tariff, 2)


def project_costs(daily_kwh: float, monthly_kwh: float, annual_kwh: float, tariff: float) -> Dict[str, float]:
    """Generates cost projections across standard periods."""
    return {
        "daily_cost": calculate_cost(daily_kwh, tariff),
        "monthly_cost": calculate_cost(monthly_kwh, tariff),
        "annual_cost": calculate_cost(annual_kwh, tariff),
    }


def calculate_savings(current_monthly_kwh: float, new_monthly_kwh: float, tariff: float) -> Dict[str, Any]:
    """Calculates energy and financial savings between two usage scenarios."""
    if current_monthly_kwh < 0 or new_monthly_kwh < 0:
        raise ValueError("Valores de consumo não podem ser negativos.")

    kwh_saved_monthly = round(current_monthly_kwh - new_monthly_kwh, 4)
    cost_saved_monthly = calculate_cost(max(0.0, kwh_saved_monthly), tariff)
    if kwh_saved_monthly < 0:
        cost_saved_monthly = -calculate_cost(abs(kwh_saved_monthly), tariff)

    kwh_saved_annual = round(kwh_saved_monthly * 12.0, 4)
    cost_saved_annual = round(cost_saved_monthly * 12.0, 2)

    pct_reduction = 0.0
    if current_monthly_kwh > 0:
        pct_reduction = round((kwh_saved_monthly / current_monthly_kwh) * 100.0, 2)

    return {
        "kwh_saved_monthly": kwh_saved_monthly,
        "kwh_saved_annual": kwh_saved_annual,
        "cost_saved_monthly": cost_saved_monthly,
        "cost_saved_annual": cost_saved_annual,
        "percentage_reduction": pct_reduction,
    }
