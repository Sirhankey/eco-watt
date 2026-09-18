"""Session state initialization and state management utilities."""
import streamlit as st
from ecowatt.services.preset_service import (
    load_presets,
    convert_preset_to_appliances,
    load_default_appliances,
)


def init_session_state():
    """Initializes standard state variables in st.session_state if not present."""
    if "tariff" not in st.session_state:
        st.session_state.tariff = 0.85  # Tarifa média em R$/kWh

    if "family_name" not in st.session_state:
        st.session_state.family_name = "Família Silva"

    if "rooms" not in st.session_state:
        st.session_state.rooms = ["Sala", "Quarto", "Cozinha", "Banheiro", "Lavanderia", "Escritório"]

    if "appliances" not in st.session_state:
        # Começar com preset típico como padrão inicial
        presets = load_presets()
        if presets:
            st.session_state.appliances = convert_preset_to_appliances(presets[0])
            st.session_state.active_preset_name = presets[0]["name"]
        else:
            st.session_state.appliances = load_default_appliances()[:4]
            st.session_state.active_preset_name = "Personalizado"

    if "calculator_item" not in st.session_state:
        st.session_state.calculator_item = {
            "name": "Chuveiro Elétrico",
            "power_watts": 5500.0,
            "hours_per_day": 0.5,
            "days_per_month": 30.0,
        }

    if "comparison_a" not in st.session_state:
        st.session_state.comparison_a = {
            "name": "Lâmpada LED",
            "power_watts": 10.0,
            "hours_per_day": 6.0,
            "days_per_month": 30.0,
        }

    if "comparison_b" not in st.session_state:
        st.session_state.comparison_b = {
            "name": "Lâmpada Incandescente",
            "power_watts": 60.0,
            "hours_per_day": 6.0,
            "days_per_month": 30.0,
        }


def reset_to_preset(preset_id: str):
    """Loads a specific preset into session state."""
    presets = load_presets()
    for p in presets:
        if p["id"] == preset_id:
            st.session_state.appliances = convert_preset_to_appliances(p)
            st.session_state.tariff = float(p.get("tariff", 0.85))
            st.session_state.active_preset_name = p["name"]
            break
