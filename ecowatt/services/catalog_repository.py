"""Remote catalog loaders with local JSON fallback for offline presentations."""
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

from ecowatt.models.appliance import Appliance
from ecowatt.models.pc_component import PCComponent
from ecowatt.services.preset_service import load_default_appliances, load_facts, load_presets
from ecowatt.services.analytics_service import is_supabase_configured
from ecowatt.utils.features import feature_enabled

PC_CATEGORY_KEYS = {
    "cpu": "cpus",
    "gpu": "gpus",
    "motherboard": "motherboards",
    "ram": "rams",
    "storage": "storages",
    "monitor": "monitors",
    "peripherals": "peripherals",
}


def _pc_category_key(category: str) -> str:
    normalized = category.strip().casefold()
    return PC_CATEGORY_KEYS.get(normalized, normalized)


def _secret(name: str) -> Optional[str]:
    environment_value = os.getenv(name)
    if environment_value:
        return environment_value.strip()
    try:
        value = st.secrets.get(name)
    except Exception:
        return None
    return str(value).strip() if value else None


def _fetch_table(table: str, filters: Optional[Dict[str, str]] = None) -> Optional[List[Dict[str, Any]]]:
    url = _secret("SUPABASE_URL")
    key = _secret("SUPABASE_ANON_KEY") or _secret("SUPABASE_KEY") or _secret("SUPABASE_SERVICE_ROLE_KEY")
    _set_source("Supabase: consultando")
    if not url or not key:
        st.session_state.catalog_source_reason = "SUPABASE_URL ou chave ausente"
        return None
    query = {"select": "*", **(filters or {})}
    request_url = f"{url.rstrip('/')}/rest/v1/{table}?{urllib.parse.urlencode(query)}"
    request = urllib.request.Request(
        request_url,
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            if not 200 <= response.status < 300:
                st.session_state.catalog_source_reason = f"HTTP {response.status} em {table}"
                return None
            payload = json.loads(response.read().decode("utf-8"))
            return payload if isinstance(payload, list) else None
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
        st.session_state.catalog_source_reason = f"falha em {table}: {type(exc).__name__}"
        return None


def _set_source(source: str) -> None:
    st.session_state.catalog_source = source


def _mark_local_fallback() -> None:
    _set_source("JSON local (fallback)")
    if not is_supabase_configured():
        st.session_state.catalog_source_reason = "Supabase nao configurado"


def load_official_appliances() -> List[Appliance]:
    """Prefer published Supabase appliances and retain the existing JSON contract."""
    if feature_enabled("catalog_remote", True) and is_supabase_configured():
        records = _fetch_table("official_appliances", {"status": "eq.published"})
        if records is not None:
            _set_source("Supabase")
            return [
                Appliance(
                    id=str(item["id"]),
                    name=item["name"],
                    power_watts=float(item["power_watts"]),
                    hours_per_day=float(item["default_hours_per_day"]),
                    days_per_month=float(item.get("default_days_per_month", 30)),
                    category=item.get("category", "Geral"),
                    description=item.get("description"),
                )
                for item in records
            ]
    _mark_local_fallback()
    return load_default_appliances()


def load_official_pc_components() -> Dict[str, List[PCComponent]]:
    """Prefer published Supabase PC components and fall back to the JSON catalog."""
    if feature_enabled("catalog_remote", True) and is_supabase_configured():
        records = _fetch_table("official_pc_components", {"status": "eq.published"})
        if records is not None:
            _set_source("Supabase")
            catalog: Dict[str, List[PCComponent]] = {}
            for item in records:
                component = PCComponent(
                    id=str(item["id"]),
                    name=item["name"],
                    category=item["category"],
                    tdp_watts=float(item["tdp_watts"]),
                    idle_watts=float(item["idle_watts"]),
                    typical_load_watts=float(item["typical_load_watts"]),
                    gaming_load_watts=float(item["gaming_load_watts"]),
                    description=item.get("description"),
                )
                catalog.setdefault(_pc_category_key(component.category), []).append(component)
            return catalog
    from ecowatt.services.pc_energy_service import load_default_pc_components

    _mark_local_fallback()
    return load_default_pc_components()


def load_official_facts() -> List[Dict[str, str]]:
    if feature_enabled("catalog_remote", True) and is_supabase_configured():
        records = _fetch_table("official_facts", {"status": "eq.published"})
        if records is not None:
            _set_source("Supabase")
            return [{"id": str(item["id"]), "title": item["title"], "fact": item["body"]} for item in records]
    _mark_local_fallback()
    return load_facts()


def load_official_presets() -> List[Dict[str, Any]]:
    if feature_enabled("catalog_remote", True) and is_supabase_configured():
        records = _fetch_table("official_presets", {"status": "eq.published"})
        if records is not None:
            items = _fetch_table("official_preset_items")
            if items is None:
                _mark_local_fallback()
                return load_presets()
            items_by_preset: Dict[str, List[Dict[str, Any]]] = {}
            for item in items:
                items_by_preset.setdefault(str(item["preset_id"]), []).append({
                    "id": item["id"],
                    "name": item["name"],
                    "category": item.get("category", "Geral"),
                    "power_watts": float(item["power_watts"]),
                    "hours_per_day": float(item["hours_per_day"]),
                    "days_per_month": float(item.get("days_per_month", 30)),
                })
            for preset in records:
                preset["appliances"] = items_by_preset.get(str(preset["id"]), [])
            _set_source("Supabase")
            return records
    _mark_local_fallback()
    return load_presets()
