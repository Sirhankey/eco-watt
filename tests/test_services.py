"""Unit tests for energy calculations, cost projections, PC builder, and presets."""
import pytest
from ecowatt.models.appliance import Appliance
from ecowatt.models.pc_component import PCComponent, PCUsageProfile
from ecowatt.services.energy_calculator import (
    calculate_daily_kwh,
    calculate_monthly_kwh,
    calculate_annual_kwh,
    calculate_appliance_consumption,
    calculate_total_household_consumption,
)
from ecowatt.services.cost_calculator import (
    calculate_cost,
    project_costs,
    calculate_savings,
)
from ecowatt.services.comparison_service import compare_appliances
from ecowatt.services.pc_energy_service import calculate_pc_energy, load_default_pc_components
from ecowatt.services.preset_service import (
    load_presets,
    convert_preset_to_appliances,
    load_default_appliances,
    load_facts,
    validate_against_real_bill,
)


# --- Tests for Appliance model and Energy Calculator ---

def test_calculate_daily_kwh():
    # 1000 W for 2 hours = 2 kWh
    assert calculate_daily_kwh(1000, 2) == 2.0
    # 5500 W for 0.5 hours = 2.75 kWh
    assert calculate_daily_kwh(5500, 0.5) == 2.75
    # 0 W
    assert calculate_daily_kwh(0, 5) == 0.0


def test_calculate_monthly_kwh():
    # 1000 W * 2h * 30 days = 60 kWh
    assert calculate_monthly_kwh(1000, 2, 30) == 60.0
    # 100 W * 5h * 30 days = 15 kWh
    assert calculate_monthly_kwh(100, 5, 30) == 15.0


def test_calculate_annual_kwh():
    # 60 kWh/month * 12 months = 720 kWh
    assert calculate_annual_kwh(60) == 720.0


def test_energy_calculator_invalid_inputs():
    with pytest.raises(ValueError):
        calculate_daily_kwh(-100, 2)
    with pytest.raises(ValueError):
        calculate_daily_kwh(500, -1)
    with pytest.raises(ValueError):
        calculate_daily_kwh(500, 25)
    with pytest.raises(ValueError):
        calculate_monthly_kwh(500, 2, 35)


def test_appliance_model_validation():
    with pytest.raises(ValueError):
        Appliance(id="test", name="Inválido", power_watts=-10, hours_per_day=2)
    with pytest.raises(ValueError):
        Appliance(id="test", name="Inválido", power_watts=100, hours_per_day=25)


def test_household_aggregation():
    appliances = [
        Appliance(id="1", name="Chuveiro", power_watts=5000, hours_per_day=1, days_per_month=30, category="Banheiro"),
        Appliance(id="2", name="Geladeira", power_watts=100, hours_per_day=10, days_per_month=30, category="Cozinha"),
    ]
    # Chuveiro: 5 kW * 1h * 30 = 150 kWh
    # Geladeira: 0.1 kW * 10h * 30 = 30 kWh
    # Total: 180 kWh
    res = calculate_total_household_consumption(appliances)
    assert res["total_monthly_kwh"] == 180.0
    assert res["total_annual_kwh"] == 2160.0
    assert len(res["items"]) == 2
    assert res["items"][0]["name"] == "Chuveiro"
    assert res["items"][0]["percentage"] == pytest.approx(83.33, 0.1)


# --- Tests for Cost Calculator ---

def test_calculate_cost():
    # 100 kWh at R$ 0.85/kWh = R$ 85.00
    assert calculate_cost(100, 0.85) == 85.0
    with pytest.raises(ValueError):
        calculate_cost(-10, 0.85)
    with pytest.raises(ValueError):
        calculate_cost(100, -0.5)


def test_project_costs():
    proj = project_costs(daily_kwh=2.0, monthly_kwh=60.0, annual_kwh=720.0, tariff=0.80)
    assert proj["daily_cost"] == 1.60
    assert proj["monthly_cost"] == 48.00
    assert proj["annual_cost"] == 576.00


def test_calculate_savings():
    savings = calculate_savings(current_monthly_kwh=100.0, new_monthly_kwh=70.0, tariff=0.80)
    assert savings["kwh_saved_monthly"] == 30.0
    assert savings["cost_saved_monthly"] == 24.0
    assert savings["cost_saved_annual"] == 288.0
    assert savings["percentage_reduction"] == 30.0


# --- Tests for Comparison Service ---

def test_compare_appliances():
    app_a = Appliance(id="a", name="LED", power_watts=10, hours_per_day=5, days_per_month=30)
    app_b = Appliance(id="b", name="Incandescente", power_watts=60, hours_per_day=5, days_per_month=30)

    res = compare_appliances(app_a, app_b, tariff=0.85)
    assert res["winner"] == "A"
    assert res["diff_kwh_monthly"] == pytest.approx(7.5, 0.01)
    assert res["diff_cost_monthly"] == pytest.approx(6.38, 0.01)


# --- Tests for PC Energy Service ---

def test_pc_energy_calculation():
    components = [
        PCComponent(id="cpu", name="CPU", category="CPU", tdp_watts=65, idle_watts=20, typical_load_watts=50, gaming_load_watts=70),
        PCComponent(id="gpu", name="GPU", category="GPU", tdp_watts=160, idle_watts=10, typical_load_watts=40, gaming_load_watts=150),
    ]
    profile = PCUsageProfile(study_office_hours=2, gaming_heavy_hours=2, light_idle_hours=2, standby_off_hours=18)
    res = calculate_pc_energy(components, profile, days_per_month=30, psu_efficiency=0.85, tariff=0.85)

    assert res["total_tdp"] == 225.0
    assert res["monthly_kwh"] > 0
    assert res["daily_cost"] == pytest.approx(res["daily_kwh"] * 0.85, 0.01)
    assert res["monthly_cost"] > 0
    assert len(res["breakdown"]) == 2


def test_pc_catalog_load():
    catalog = load_default_pc_components()
    assert "cpus" in catalog
    assert "gpus" in catalog
    assert len(catalog["cpus"]) >= 3


# --- Tests for Preset and Bill Validation ---

def test_presets_loading():
    presets = load_presets()
    assert len(presets) >= 3
    appliances = convert_preset_to_appliances(presets[0])
    assert len(appliances) > 0


def test_bill_validation():
    # Simulated 150 kWh, real bill R$ 127.50 at R$ 0.85/kWh = exactly 150 kWh
    res = validate_against_real_bill(simulated_monthly_kwh=150.0, real_bill_reais=127.50, tariff=0.85)
    assert res["verdict"] == "EXACT"

    # Higher bill
    res_high = validate_against_real_bill(simulated_monthly_kwh=100.0, real_bill_reais=170.00, tariff=0.85)
    assert res_high["verdict"] == "REAL_HIGHER"


def test_facts_loading():
    facts = load_facts()
    assert len(facts) >= 5
