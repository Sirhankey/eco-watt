"""Optional persistence of analytics events in Supabase."""
import json
import urllib.error
import urllib.request
from typing import Any

import streamlit as st


def _get_secret(name: str) -> str | None:
    try:
        value = st.secrets.get(name)
    except Exception:
        return None
    return str(value).strip() if value else None


def is_supabase_configured() -> bool:
    """Return whether both Supabase secrets are available."""
    return bool(_get_secret("SUPABASE_URL") and _get_secret("SUPABASE_SERVICE_ROLE_KEY"))


def save_event(event: dict[str, Any]) -> bool:
    """Persist one event without interrupting the Streamlit user experience."""
    supabase_url = _get_secret("SUPABASE_URL")
    service_role_key = _get_secret("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_role_key:
        return False

    payload = {
        "event": event.get("event"),
        "occurred_at": event.get("timestamp"),
        "session_id": event.get("session_id"),
        "user_id": event.get("user_id"),
        "class_group": event.get("class_group"),
        "role": event.get("role"),
        "age_group": event.get("age_group"),
        "gender": event.get("gender"),
        "details": {
            key: value
            for key, value in event.items()
            if key not in {
                "event",
                "timestamp",
                "session_id",
                "user_id",
                "class_group",
                "role",
                "age_group",
                "gender",
            }
        },
    }
    body = json.dumps(payload, ensure_ascii=True, default=str).encode("utf-8")
    request = urllib.request.Request(
        f"{supabase_url.rstrip('/')}/rest/v1/analytics_events",
        data=body,
        method="POST",
        headers={
            "apikey": service_role_key,
            "Authorization": f"Bearer {service_role_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            return 200 <= response.status < 300
    except (urllib.error.URLError, TimeoutError, OSError):
        return False
