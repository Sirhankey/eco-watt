"""Structured event logging for Streamlit Cloud logs."""
import json
import hashlib
import logging
import sys
import uuid
from datetime import datetime, timezone
from typing import Any

import streamlit as st
from ecowatt.services.analytics_service import save_event


LOGGER_NAME = "ecowatt.events"


def _get_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


def _get_session_id() -> str:
    if "analytics_session_id" not in st.session_state:
        st.session_state.analytics_session_id = str(uuid.uuid4())
    return st.session_state.analytics_session_id


def create_user_id(name: str, class_group: str) -> str:
    """Create a stable pseudonymous identifier from the session identity."""
    identity = f"{name.strip().casefold()}|{class_group.strip().casefold()}"
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]


def track_event(event_name: str, **details: Any) -> None:
    """Write a JSON event to the hosting platform's application logs."""
    event = {
        "event": event_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "session_id": _get_session_id(),
        "user_id": st.session_state.get("user_id"),
        "class_group": st.session_state.get("class_group"),
        **details,
    }
    _get_logger().info(json.dumps(event, ensure_ascii=True, default=str))
    save_event(event)


def track_event_on_change(state_key: str, event_name: str, **details: Any) -> None:
    """Log an event only when its input signature changes during a session."""
    signature = json.dumps(details, sort_keys=True, ensure_ascii=True, default=str)
    if st.session_state.get(state_key) != signature:
        st.session_state[state_key] = signature
        track_event(event_name, **details)
