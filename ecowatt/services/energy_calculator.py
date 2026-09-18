"""Pure functions for electrical energy calculations."""
from typing import Sequence
from ecowatt.models.appliance import Appliance


def calculate_daily_kwh(power_watts: float, hours_per_day: float) -> float:
    """Calculates daily electrical consumption in kWh.

    Formula: (power_watts / 1000) * hours_per_day
    """
    if power_watts < 0:
        raise ValueError("A potência em Watts não pode ser negativa.")
    if hours_per_day < 0 or hours_per_day > 24:
        raise ValueError("As horas de uso por dia devem estar entre 0 e 24.")

    return round((power_watts / 1000.0) * hours_per_day, 4)


def calculate_monthly_kwh(power_watts: float, hours_per_day: float, days_per_month: float = 30.0) -> float:
    """Calculates monthly electrical consumption in kWh.

    Formula: (power_watts / 1000) * hours_per_day * days_per_month
    """
    if days_per_month < 0 or days_per_month > 31:
        raise ValueError("Os dias de uso por mês devem estar entre 0 e 31.")

    daily = calculate_daily_kwh(power_watts, hours_per_day)
    return round(daily * days_per_month, 4)


def calculate_annual_kwh(monthly_kwh: float, months_per_year: float = 12.0) -> float:
    """Calculates annual electrical consumption in kWh from monthly kWh."""
    if monthly_kwh < 0:
        raise ValueError("O consumo mensal em kWh não pode ser negativo.")
    if months_per_year <= 0:
        raise ValueError("A quantidade de meses no ano deve ser positiva.")

    return round(monthly_kwh * months_per_year, 4)


def calculate_appliance_consumption(appliance: Appliance) -> dict:
    """Calculates daily, monthly and annual consumption for a single appliance."""
    daily_kwh = calculate_daily_kwh(appliance.power_watts, appliance.hours_per_day)
    monthly_kwh = calculate_monthly_kwh(appliance.power_watts, appliance.hours_per_day, appliance.days_per_month)
    annual_kwh = calculate_annual_kwh(monthly_kwh)

    return {
        "id": appliance.id,
        "name": appliance.name,
        "category": appliance.category,
        "daily_kwh": daily_kwh,
        "monthly_kwh": monthly_kwh,
        "annual_kwh": annual_kwh,
    }


def calculate_total_household_consumption(appliances: Sequence[Appliance]) -> dict:
    """Calculates aggregated household consumption and breakdown."""
    if not appliances:
        return {
            "total_monthly_kwh": 0.0,
            "total_annual_kwh": 0.0,
            "items": [],
            "category_distribution": {},
        }

    items = []
    category_totals = {}
    total_monthly = 0.0

    for app in appliances:
        res = calculate_appliance_consumption(app)
        items.append(res)
        m_kwh = res["monthly_kwh"]
        total_monthly += m_kwh
        category_totals[app.category] = category_totals.get(app.category, 0.0) + m_kwh

    total_monthly = round(total_monthly, 4)
    total_annual = round(calculate_annual_kwh(total_monthly), 4)

    # Sort items by monthly consumption descending (ranking)
    items_sorted = sorted(items, key=lambda x: x["monthly_kwh"], reverse=True)

    # Add percentage of total
    for item in items_sorted:
        pct = (item["monthly_kwh"] / total_monthly * 100.0) if total_monthly > 0 else 0.0
        item["percentage"] = round(pct, 2)

    return {
        "total_monthly_kwh": total_monthly,
        "total_annual_kwh": total_annual,
        "items": items_sorted,
        "category_distribution": {k: round(v, 4) for k, v in category_totals.items()},
    }
