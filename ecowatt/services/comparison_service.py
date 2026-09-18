"""Service for comparing two appliances or scenarios."""
from typing import Dict, Any
from ecowatt.models.appliance import Appliance
from ecowatt.services.energy_calculator import calculate_monthly_kwh, calculate_annual_kwh
from ecowatt.services.cost_calculator import calculate_cost


def compare_appliances(appliance_a: Appliance, appliance_b: Appliance, tariff: float) -> Dict[str, Any]:
    """Compares two appliances and returns absolute and relative differences."""
    kwh_a_monthly = calculate_monthly_kwh(appliance_a.power_watts, appliance_a.hours_per_day, appliance_a.days_per_month)
    kwh_b_monthly = calculate_monthly_kwh(appliance_b.power_watts, appliance_b.hours_per_day, appliance_b.days_per_month)

    cost_a_monthly = calculate_cost(kwh_a_monthly, tariff)
    cost_b_monthly = calculate_cost(kwh_b_monthly, tariff)

    kwh_a_annual = calculate_annual_kwh(kwh_a_monthly)
    kwh_b_annual = calculate_annual_kwh(kwh_b_monthly)

    cost_a_annual = calculate_cost(kwh_a_annual, tariff)
    cost_b_annual = calculate_cost(kwh_b_annual, tariff)

    diff_kwh_monthly = round(abs(kwh_a_monthly - kwh_b_monthly), 4)
    diff_cost_monthly = round(abs(cost_a_monthly - cost_b_monthly), 2)
    diff_kwh_annual = round(abs(kwh_a_annual - kwh_b_annual), 4)
    diff_cost_annual = round(abs(cost_a_annual - cost_b_annual), 2)

    # Determine lower consumption
    if kwh_a_monthly < kwh_b_monthly:
        winner = "A"
        summary = f"O aparelho '{appliance_a.name}' apresenta menor consumo ({diff_kwh_monthly} kWh/mês a menos que '{appliance_b.name}')."
    elif kwh_b_monthly < kwh_a_monthly:
        winner = "B"
        summary = f"O aparelho '{appliance_b.name}' apresenta menor consumo ({diff_kwh_monthly} kWh/mês a menos que '{appliance_a.name}')."
    else:
        winner = "EQUAL"
        summary = "Ambos os aparelhos apresentam o mesmo consumo elétrico mensal para os parâmetros informados."

    return {
        "appliance_a": {
            "name": appliance_a.name,
            "power_watts": appliance_a.power_watts,
            "hours_per_day": appliance_a.hours_per_day,
            "days_per_month": appliance_a.days_per_month,
            "monthly_kwh": kwh_a_monthly,
            "annual_kwh": kwh_a_annual,
            "monthly_cost": cost_a_monthly,
            "annual_cost": cost_a_annual,
        },
        "appliance_b": {
            "name": appliance_b.name,
            "power_watts": appliance_b.power_watts,
            "hours_per_day": appliance_b.hours_per_day,
            "days_per_month": appliance_b.days_per_month,
            "monthly_kwh": kwh_b_monthly,
            "annual_kwh": kwh_b_annual,
            "monthly_cost": cost_b_monthly,
            "annual_cost": cost_b_annual,
        },
        "winner": winner,
        "diff_kwh_monthly": diff_kwh_monthly,
        "diff_cost_monthly": diff_cost_monthly,
        "diff_kwh_annual": diff_kwh_annual,
        "diff_cost_annual": diff_cost_annual,
        "summary": summary,
    }
