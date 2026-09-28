"""Feature flags used to enable or roll back event functionality."""
import os

import streamlit as st


def feature_enabled(name: str, default: bool = False) -> bool:
    key = f"ECOWATT_FEATURE_{name.upper()}"
    value = os.getenv(key)
    if value is None:
        try:
            value = st.secrets.get(key)
        except Exception:
            value = None
    if value is None:
        return default
    return str(value).strip().casefold() in {"1", "true", "yes", "on"}