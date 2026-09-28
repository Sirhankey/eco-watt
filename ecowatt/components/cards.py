"""UI cards, metrics, and educational display components."""
import streamlit as st
from typing import Optional


def _palette() -> dict[str, str]:
    """Return readable colors for the active Streamlit theme."""
    try:
        is_dark = st.context.theme.type == "dark"
    except Exception:
        is_dark = False
    if is_dark:
        return {
            "surface": "rgba(255, 255, 255, 0.05)",
            "label": "#cbd5e1",
            "value": "#f8fafc",
            "body": "#cbd5e1",
            "muted": "#cbd5e1",
            "accent": "#7dd3fc",
            "info_background": "rgba(14, 165, 233, 0.08)",
            "info_text": "#bae6fd",
            "warning_background": "rgba(245, 158, 11, 0.1)",
            "warning_text": "#fbbf24",
            "border": "rgba(255, 255, 255, 0.1)",
        }
    return {
        "surface": "#ffffff",
        "label": "#475569",
        "value": "#0f172a",
        "body": "#334155",
        "muted": "#475569",
        "accent": "#0369a1",
        "info_background": "#eff6ff",
        "info_text": "#075985",
        "warning_background": "#fff7ed",
        "warning_text": "#9a3412",
        "border": "#cbd5e1",
    }


def render_metric_card(
    label: str,
    value: str,
    subtext: Optional[str] = None,
    delta: Optional[str] = None,
    delta_color: str = "normal",
    border_color: str = "#22c55e",
):
    """Renders a styled card for KPIs and metrics without markdown indentation issues."""
    palette = _palette()
    delta_html = f"<div style='font-size: 0.85rem; color: #059669; margin-top: 4px;'>{delta}</div>" if delta else ""
    subtext_html = f"<div style='font-size: 0.8rem; color: {palette['muted']}; margin-top: 2px;'>{subtext}</div>" if subtext else ""

    html = (
        f"<div style='background: {palette['surface']}; border: 1px solid {palette['border']}; border-left: 4px solid {border_color}; "
        f"border-radius: 10px; padding: 14px 18px; margin-bottom: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.12);'>"
        f"<div style='font-size: 0.8rem; font-weight: 600; color: {palette['label']}; text-transform: uppercase; letter-spacing: 0.05em;'>{label}</div>"
        f"<div style='font-size: 1.7rem; font-weight: 700; color: {palette['value']}; margin-top: 2px; line-height: 1.2;'>{value}</div>"
        f"{delta_html}"
        f"{subtext_html}"
        f"</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def render_cost_card(
    label: str,
    monthly_cost: float,
    daily_cost: Optional[float] = None,
    annual_cost: Optional[float] = None,
    highlight: str = "monthly",
    border_color: str = "#10b981",
    extra_subtext: Optional[str] = None,
):
    """Renders a standardized financial cost/savings card highlighting one period

    while always displaying daily, monthly, and annual projections in subtext.
    """
    if daily_cost is None:
        daily_cost = monthly_cost / 30.0
    if annual_cost is None:
        annual_cost = monthly_cost * 12.0

    if highlight == "daily":
        main_val = f"R$ {daily_cost:.2f}"
        main_sub = "por dia"
        sec1 = f"Mensal: R$ {monthly_cost:.2f}"
        sec2 = f"Anual: R$ {annual_cost:.2f}"
    elif highlight == "annual":
        main_val = f"R$ {annual_cost:.2f}"
        main_sub = "por ano"
        sec1 = f"Diário: R$ {daily_cost:.2f}"
        sec2 = f"Mensal: R$ {monthly_cost:.2f}"
    else:  # default 'monthly'
        main_val = f"R$ {monthly_cost:.2f}"
        main_sub = "por mês"
        sec1 = f"Diário: R$ {daily_cost:.2f}"
        sec2 = f"Anual: R$ {annual_cost:.2f}"

    palette = _palette()
    extra_html = f"<div style='font-size: 0.75rem; color: {palette['muted']}; margin-top: 3px;'>{extra_subtext}</div>" if extra_subtext else ""

    html = (
        f"<div style='background: {palette['surface']}; border: 1px solid {palette['border']}; border-left: 4px solid {border_color}; "
        f"border-radius: 10px; padding: 14px 18px; margin-bottom: 12px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.12);'>"
        f"<div style='font-size: 0.8rem; font-weight: 600; color: {palette['label']}; text-transform: uppercase; letter-spacing: 0.05em;'>{label}</div>"
        f"<div style='display: flex; align-items: baseline; gap: 6px; margin-top: 2px;'>"
        f"<span style='font-size: 1.7rem; font-weight: 700; color: {palette['value']}; line-height: 1.2;'>{main_val}</span>"
        f"<span style='font-size: 0.85rem; color: {palette['muted']};'>{main_sub}</span>"
        f"</div>"
        f"<div style='font-size: 0.8rem; color: {palette['accent']}; margin-top: 4px; font-weight: 600;'>{sec1} &bull; {sec2}</div>"
        f"{extra_html}"
        f"</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def render_did_you_know(title: str, fact: str):
    """Renders an educational Did You Know tip card."""
    palette = _palette()
    html = (
        f"<div style='background: {palette['info_background']}; border: 1px solid #7dd3fc; "
        f"border-radius: 10px; padding: 14px 18px; margin: 14px 0;'>"
        f"<div style='font-weight: 600; color: {palette['info_text']}; font-size: 0.95rem; margin-bottom: 4px;'>💡 Você sabia? — {title}</div>"
        f"<div style='font-size: 0.9rem; color: {palette['body']}; line-height: 1.4;'>{fact}</div>"
        f"</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def render_warning_badge(message: str):
    """Renders a gentle warning or estimate disclaimer."""
    palette = _palette()
    html = (
        f"<div style='background: {palette['warning_background']}; border-left: 4px solid #d97706; "
        f"border-radius: 6px; padding: 8px 14px; margin: 10px 0; font-size: 0.85rem; color: {palette['warning_text']};'>"
        f"⚠️ <strong>Estimativa didática:</strong> {message}"
        f"</div>"
    )
    st.markdown(html, unsafe_allow_html=True)


def render_header(title: str, subtitle: str, icon: str = "⚡"):
    """Renders standard hero header for views."""
    palette = _palette()
    html = (
        f"<div style='margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid {palette['border']};'>"
        f"<h1 style='font-size: 2.1rem; font-weight: 800; margin-bottom: 4px; display: flex; align-items: center; gap: 8px; color: {palette['value']};'>"
        f"<span>{icon}</span> {title}"
        f"</h1>"
        f"<p style='font-size: 1.05rem; color: {palette['body']}; margin: 0;'>{subtitle}</p>"
        f"</div>"
    )
    st.markdown(html, unsafe_allow_html=True)
