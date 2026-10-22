"""Curated ordering, category normalization and icon lookup for official appliances."""
from pathlib import Path
from typing import List, Optional

from ecowatt.models.appliance import Appliance

ICONS_DIR = Path(__file__).resolve().parents[2] / "assets" / "img" / "appliances"
GENERIC_ICON = "generic"

CURATED_ORDER = [
    "shower", "electric_shower_6800", "air_conditioner", "air_conditioner_12000",
    "fridge", "freezer", "led_tv", "bedroom_tv_32", "microwave", "washing_machine",
    "washing_machine_large", "air_fryer", "iron", "clothes_iron_low", "fan",
    "bedroom_fan_40w", "ceiling_fan", "led_bulb_pack", "led_bulb_single",
    "led_ceiling_light", "incandescent_bulb", "laptop", "desktop_pc", "gaming_console",
    "wifi_router", "phone_charger", "electric_oven", "electric_kettle",
    "electric_coffee_maker", "blender", "toaster", "sandwich_maker", "rice_cooker",
    "electric_pressure_cooker", "electric_grill", "electric_mixer", "electric_juicer",
    "dishwasher", "range_hood", "water_dispenser", "water_filter", "hair_dryer",
    "hair_straightener", "hair_clippers", "electric_toothbrush", "bathroom_exhaust",
    "electric_towel_warmer", "electric_fan_heater", "electric_blanket",
    "portable_air_purifier", "portable_speaker", "printer", "sewing_machine",
    "vacuum_cleaner", "robot_vacuum", "aquarium_filter_light", "garden_lamp",
    "garage_door_motor", "water_pump", "electric_lawn_mower",
]
_RANK = {appliance_id: index for index, appliance_id in enumerate(CURATED_ORDER)}

CATEGORY_ALIASES = {
    "Quarto/Escritório": "Escritório",
    "Quarto/Sala": "Quarto",
    "Sala/Quarto": "Sala",
    "Cozinha/Área de serviço": "Cozinha",
    "Garagem/Área externa": "Área externa",
    "Área de serviço": "Lavanderia",
}

# Variants reuse the SVG of the closest base appliance.
ICON_BY_ID = {
    "air_conditioner_12000": "air_conditioner",
    "bedroom_fan_40w": "fan",
    "ceiling_fan": "fan",
    "bedroom_tv_32": "led_tv",
    "clothes_iron_low": "iron",
    "electric_shower_6800": "shower",
    "washing_machine_large": "washing_machine",
    "led_bulb_single": "led_bulb_pack",
    "led_ceiling_light": "led_bulb_pack",
    "incandescent_bulb": "led_bulb_pack",
    "garden_lamp": "led_bulb_pack",
    "freezer": "fridge",
    "water_dispenser": "fridge",
    "electric_oven": "microwave",
    "electric_grill": "microwave",
    "sandwich_maker": "microwave",
    "hair_straightener": "hair_dryer",
    "hair_clippers": "hair_dryer",
    "robot_vacuum": "vacuum_cleaner",
    "electric_pressure_cooker": "rice_cooker",
}


def normalize_category(category: Optional[str]) -> str:
    value = (category or "Geral").strip()
    return CATEGORY_ALIASES.get(value, value)


def sort_appliances(appliances: List[Appliance]) -> List[Appliance]:
    """Curated ids first in the defined order; unknown ids follow alphabetically."""
    return sorted(
        appliances,
        key=lambda item: (_RANK.get(item.id, len(_RANK)), item.name.casefold()),
    )


PRESET_ORDER = [
    "casa_tipica", "casa_sustentavel", "apartamento_pequeno", "familia_grande",
    "casa_calor", "home_office", "cozinha_completa", "quarto_gamer",
]
_PRESET_RANK = {preset_id: index for index, preset_id in enumerate(PRESET_ORDER)}


def sort_presets(presets: List[dict]) -> List[dict]:
    """Curated presets first (the first one is the default home); unknown ids follow by name."""
    return sorted(
        presets,
        key=lambda item: (_PRESET_RANK.get(str(item["id"]), len(_PRESET_RANK)), str(item.get("name", "")).casefold()),
    )


def appliance_icon_path(appliance_id: str) -> Optional[Path]:
    stem = ICON_BY_ID.get(appliance_id, appliance_id)
    for candidate in (stem, GENERIC_ICON):
        path = ICONS_DIR / f"{candidate}.svg"
        if path.is_file():
            return path
    return None
