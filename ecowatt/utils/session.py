"""Session state initialization and state management utilities."""
import json
import base64
from typing import Any

import streamlit as st
from ecowatt.services.preset_service import convert_preset_to_appliances
from ecowatt.services.catalog_repository import load_official_appliances, load_official_presets
from ecowatt.utils.logging import create_user_id, track_event

IDENTITY_COOKIE = "ecowatt_identity"
IDENTITY_COOKIE_MAX_AGE = 60 * 60 * 24 * 30


def _identity_from_cookie(raw_value: object) -> dict[str, str] | None:
    if not isinstance(raw_value, str):
        return None
    try:
        identity = json.loads(raw_value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    required_fields = {"user_id", "user_name", "class_group", "role", "age_group", "gender"}
    if not isinstance(identity, dict) or not required_fields.issubset(identity):
        return None
    if not all(isinstance(identity[field], str) and identity[field].strip() for field in required_fields):
        return None
    return {field: identity[field].strip() for field in required_fields}


def _identity_from_query_params() -> dict[str, str] | None:
    encoded = st.query_params.get("participant")
    if not encoded:
        return None
    try:
        raw_value = base64.urlsafe_b64decode(encoded.encode("ascii")).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return None
    return _identity_from_cookie(raw_value)


def _save_identity_to_query_params(identity: dict[str, str]) -> None:
    payload = json.dumps(identity, ensure_ascii=True, separators=(",", ":")).encode("utf-8")
    st.query_params["participant"] = base64.urlsafe_b64encode(payload).decode("ascii")


def _save_identity(controller: Any, identity: dict[str, str]) -> None:
    controller.set(
        IDENTITY_COOKIE,
        json.dumps(identity, ensure_ascii=True),
        max_age=IDENTITY_COOKIE_MAX_AGE,
    )


def _restore_identity(controller: Any) -> bool:
    """Restore from the initial HTTP cookie before consulting the async component."""
    identity = _identity_from_query_params()
    if identity is None:
        try:
            raw_cookie = st.context.cookies.get(IDENTITY_COOKIE)
        except (AttributeError, RuntimeError):
            raw_cookie = None
        identity = _identity_from_cookie(raw_cookie)
    if identity is None:
        identity = _identity_from_cookie(controller.get(IDENTITY_COOKIE))
    if identity is None:
        return False
    for field, value in identity.items():
        st.session_state[field] = value
    st.session_state.identity_restored_from_cookie = True
    return True


def init_session_state():
    """Initializes standard state variables in st.session_state if not present."""
    from streamlit_cookies_controller import CookieController

    cookie_controller = CookieController(key="ecowatt_identity_controller")
    if "user_id" not in st.session_state:
        if not _restore_identity(cookie_controller):
            st.markdown(
                """
                <style>
                div[data-testid="stForm"] {
                    max-width: 600px;
                    margin: 0 auto;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
            role_left, role_center, role_right = st.columns([1.5, 2, 1.5])
            with role_center:
                role = st.selectbox(
                    "Perfil:",
                    ["Aluno", "Professor", "Responsável", "Convidado"],
                    key="role_input",
                )
            if role != "Aluno":
                st.session_state.pop("class_group_input", None)
            with st.form("user_identification"):
                st.markdown("### Identificação da sessão")
                st.caption("Responda para registrar sua participação na feira de ciências.")
                user_name = st.text_input("Nome:", key="user_name_input")
                age_group = st.selectbox(
                    "Faixa etária:",
                    ["Até 10", "11–14", "15–17", "18–24", "25–39", "40+", "Prefiro não responder"],
                    key="age_group_input",
                )
                gender = st.selectbox(
                    "Gênero:",
                    ["Mulher", "Homem", "Não binário", "Outro", "Prefiro não responder"],
                    key="gender_input",
                )
                if role == "Aluno":
                    class_group = st.text_input("Turma:", key="class_group_input")
                else:
                    class_group = "N/A"
                submitted = st.form_submit_button("Entrar", type="primary", use_container_width=True)

            if not submitted:
                st.stop()
            if not user_name.strip() or not class_group.strip():
                st.error("Preencha o nome e a turma para continuar.")
                st.stop()

            st.session_state.user_id = create_user_id(user_name, class_group)
            st.session_state.class_group = class_group.strip()
            st.session_state.user_name = user_name.strip()
            st.session_state.role = role
            st.session_state.age_group = age_group
            st.session_state.gender = gender
            _save_identity(cookie_controller, {
                "user_id": st.session_state.user_id,
                "user_name": st.session_state.user_name,
                "class_group": st.session_state.class_group,
                "role": st.session_state.role,
                "age_group": st.session_state.age_group,
                "gender": st.session_state.gender,
            })
            _save_identity_to_query_params({
                "user_id": st.session_state.user_id,
                "user_name": st.session_state.user_name,
                "class_group": st.session_state.class_group,
                "role": st.session_state.role,
                "age_group": st.session_state.age_group,
                "gender": st.session_state.gender,
            })
            track_event("user_identified", role=role, age_group=age_group, gender=gender)
            st.rerun()

    is_new_session = "analytics_session_started" not in st.session_state
    if is_new_session:
        st.session_state.analytics_session_started = True

    if "tariff" not in st.session_state:
        st.session_state.tariff = 0.85  # Tarifa média em R$/kWh

    if "family_name" not in st.session_state:
        st.session_state.family_name = "Família Silva"

    if "personal_presets" not in st.session_state:
        st.session_state.personal_presets = []

    if "personal_pc_components" not in st.session_state:
        st.session_state.personal_pc_components = {}

    if "rooms" not in st.session_state:
        st.session_state.rooms = ["Sala", "Quarto", "Cozinha", "Banheiro", "Lavanderia", "Escritório"]

    if "appliances" not in st.session_state:
        # Começar com preset típico como padrão inicial
        presets = load_official_presets()
        if presets:
            st.session_state.appliances = convert_preset_to_appliances(presets[0])
            st.session_state.active_preset_name = presets[0]["name"]
        else:
            st.session_state.appliances = load_official_appliances()[:4]
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

    if is_new_session:
        track_event("session_started")

    catalog_source = st.session_state.get("catalog_source", "JSON local (fallback)")
    is_online = catalog_source == "Supabase"
    connection_label = "Online - Supabase" if is_online else "Offline - JSON local"
    connection_color = "#16a34a" if is_online else "#dc2626"
    st.sidebar.markdown(
        f"<div title='{connection_label}' style='display:flex; align-items:center; gap:8px;'>"
        f"<span style='display:inline-block; width:10px; height:10px; border-radius:50%; background:{connection_color}; "
        f"box-shadow:0 0 0 2px rgba(0,0,0,0.08);'></span>"
        f"<strong>{st.session_state.user_name}</strong></div>",
        unsafe_allow_html=True,
    )
    st.sidebar.caption(f"Perfil: {st.session_state.role}")

    # if st.sidebar.button("Esquecer identificação", key="forget_identity"):
    #     cookie_controller.remove(IDENTITY_COOKIE)
    #     st.query_params.pop("participant", None)
    #     for field in ("user_id", "user_name", "class_group", "role", "age_group", "gender"):
    #         st.session_state.pop(field, None)
    #     st.rerun()

    # _render_feedback_form()


def _render_feedback_form() -> None:
    """Render the optional end-of-visit survey in the shared sidebar."""
    st.sidebar.markdown(
        """
        <style>
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
            order: 2;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
            order: 1;
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] > div {
            gap: 0.45rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if st.session_state.get("feedback_submitted", False):
        st.sidebar.success("Avaliação registrada. Obrigado!")
        return

    with st.sidebar.expander("⭐ Avaliar experiência", expanded=False):
        st.caption("Preencha quando terminar de explorar o aplicativo.")
        with st.form("experience_feedback"):
            rating = st.select_slider(
                "Como você avalia a experiência?",
                options=[1, 2, 3, 4, 5],
                format_func=lambda value: "⭐" * value,
            )
            knew_kwh = st.radio(
                "Você já sabia o que era kWh antes de usar o aplicativo?",
                ["Sim", "Não", "Não tenho certeza"],
            )
            helped_bill = st.radio(
                "O aplicativo ajudou você a entender sua conta de energia?",
                ["Sim", "Mais ou menos", "Não", "Não se aplica"],
            )
            main_interest = st.selectbox(
                "Qual área você achou mais interessante?",
                ["Calculadora", "Minha Casa", "PC Builder", "Comparador", "Eficiência", "Modo Apresentação"],
            )
            learned = st.text_area(
                "O que você aprendeu? (opcional)",
                max_chars=300,
            )
            submitted = st.form_submit_button("Enviar avaliação", type="primary", use_container_width=True)

        if submitted:
            track_event(
                "experience_feedback_submitted",
                rating=rating,
                knew_kwh=knew_kwh,
                helped_bill=helped_bill,
                main_interest=main_interest,
                learned=learned.strip() or None,
            )
            st.session_state.feedback_submitted = True
            st.rerun()


def reset_to_preset(preset_id: str):
    """Loads a specific preset into session state."""
    presets = load_presets()
    for p in presets:
        if p["id"] == preset_id:
            st.session_state.appliances = convert_preset_to_appliances(p)
            st.session_state.tariff = float(p.get("tariff", 0.85))
            st.session_state.active_preset_name = p["name"]
            break
