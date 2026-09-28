import pytest

from ecowatt.models.pc_component import PCComponent, PCUsageProfile
from ecowatt.services.pc_builder_service import calculate_setup, compare_setups


def component(name, gaming):
    return PCComponent(name, name, "GPU", gaming, 10, 20, gaming)


def test_compare_setups_returns_absolute_deltas():
    profile = PCUsageProfile(2, 2, 2, 18)
    first = calculate_setup([component("A", 100)], profile, 30, 0.85, 0.85)
    second = calculate_setup([component("B", 200)], profile, 30, 0.85, 0.85)
    delta = compare_setups(first, second)
    assert delta["monthly_kwh"] > 0
    assert delta["monthly_cost"] == pytest.approx(delta["monthly_kwh"] * 0.85, 0.01)


def test_empty_setup_is_rejected():
    with pytest.raises(ValueError, match="pelo menos um"):
        calculate_setup([], PCUsageProfile(), 30, 0.85, 0.85)
