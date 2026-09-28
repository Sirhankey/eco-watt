"""Session state initialization and state management utilities."""
from datetime import datetime, timezone

import streamlit as st
from streamlit_cookies_controller import CookieController

from ecowatt.services.preset_service import convert_preset_to_appliances
from ecowatt.services.catalog_repository import load_official_appliances, load_official_presets
from ecowatt.services.participant_auth import (
    AuthStorageUnavailable,
    LoginRateLimited,
    ParticipantAuthService,
    UsernameAlreadyTaken,
    normalize_username,
)
from ecowatt.utils.features import feature_enabled
from ecowatt.utils.logging import track_event

IDENTITY_COOKIE = "ecowatt_identity"
AUTH_SESSION_COOKIE = "ecowatt_auth_session"
AUTH_SESSION_MAX_AGE = 60 * 60 * 24 * 30


def _set_authenticated_participant(participant) -> None:
    st.session_state.participant_id = participant.participant_id
    st.session_state.user_id = participant.participant_id
    st.session_state.username = participant.username
    st.session_state.user_name = participant.username
    st.session_state.auth_session_token = participant.session_token
    st.session_state.auth_expires_at = participant.expires_at.isoformat()
    st.session_state.must_change_password = participant.must_change_password


def _auth_cookie_value(controller: CookieController) -> str | None:
    try:
        value = st.context.cookies.get(AUTH_SESSION_COOKIE)
    except (AttributeError, RuntimeError):
        value = None
    return value if isinstance(value, str) and value else controller.get(AUTH_SESSION_COOKIE)


def _remove_auth_cookie(controller: CookieController) -> None:
    if controller.get(AUTH_SESSION_COOKIE) is not None:
        controller.remove(AUTH_SESSION_COOKIE, secure=True, same_site="strict")
    st.session_state.pop("auth_session_token", None)
    st.session_state.pop("auth_expires_at", None)
    st.session_state.pop("participant_id", None)
    st.session_state.pop("user_id", None)
    st.session_state.pop("username", None)
    st.session_state.pop("user_name", None)
    st.session_state.pop("must_change_password", None)


def _render_authentication(controller: CookieController, service: ParticipantAuthService) -> None:
    st.title("EcoWatt")
    st.caption("Entre ou crie sua conta da feira.")
    login_tab, register_tab = st.tabs(["Entrar", "Criar conta"])

    with login_tab:
        with st.form("participant_login"):
            username = st.text_input("Nome de usuário", key="login_username")
            password = st.text_input("Senha", type="password", key="login_password")
            submitted = st.form_submit_button("Entrar", type="primary", use_container_width=True)
        if submitted:
            try:
                participant = service.login(username, password)
                if participant is None:
                    st.error("Nome de usuário ou senha incorretos.")
                else:
                    _set_authenticated_participant(participant)
                    controller.set(
                        AUTH_SESSION_COOKIE,
                        participant.session_token,
                        max_age=AUTH_SESSION_MAX_AGE,
                        path="/",
                        secure=True,
                        same_site="strict",
                    )
                    track_event("participant_logged_in")
                    st.rerun()
            except LoginRateLimited as exc:
                st.warning(str(exc))
            except AuthStorageUnavailable as exc:
                st.error(str(exc))

    with register_tab:
        with st.form("participant_registration"):
            username = st.text_input("Nome de usuário", key="register_username")
            password = st.text_input("Senha (6 a 128 caracteres)", type="password", key="register_password")
            confirmation = st.text_input("Confirmar senha", type="password", key="register_password_confirmation")
            check_name = st.form_submit_button("Verificar nome")
            create_account = st.form_submit_button("Criar conta", type="primary", use_container_width=True)
        if check_name:
            try:
                normalized = normalize_username(username)
                if service.username_available(normalized):
                    st.success("Nome de usuário disponível.")
                else:
                    st.warning("Esse nome de usuário já está em uso.")
            except ValueError as exc:
                st.warning(str(exc))
            except AuthStorageUnavailable as exc:
                st.error(str(exc))
        if create_account:
            if password != confirmation:
                st.error("As senhas não conferem.")
            else:
                try:
                    participant = service.register(username, password)
                    _set_authenticated_participant(participant)
                    controller.set(
                        AUTH_SESSION_COOKIE,
                        participant.session_token,
                        max_age=AUTH_SESSION_MAX_AGE,
                        path="/",
                        secure=True,
                        same_site="strict",
                    )
                    track_event("participant_registered")
                    st.rerun()
                except (ValueError, UsernameAlreadyTaken) as exc:
                    st.error(str(exc))
                except AuthStorageUnavailable as exc:
                    st.error(str(exc))

    st.info("O serviço de contas precisa estar online para criar uma conta ou entrar.")
    st.stop()


def _require_password_change(service: ParticipantAuthService, controller: CookieController) -> None:
    st.title("Atualize sua senha")
    st.caption("Sua senha temporária precisa ser trocada antes de continuar.")
    with st.form("participant_password_change"):
        password = st.text_input("Nova senha (6 a 128 caracteres)", type="password")
        confirmation = st.text_input("Confirmar nova senha", type="password")
        submitted = st.form_submit_button("Salvar nova senha", type="primary", use_container_width=True)
    if submitted:
        if password != confirmation:
            st.error("As senhas não conferem.")
        else:
            try:
                service.change_password(st.session_state.participant_id, password)
                st.session_state.must_change_password = False
                st.rerun()
            except (ValueError, AuthStorageUnavailable) as exc:
                st.error(str(exc))
    st.stop()


def init_session_state():
    """Initializes standard state variables in st.session_state if not present."""
    if not feature_enabled("participant_auth", True):
        st.error("O acesso autenticado está temporariamente desativado.")
        st.stop()

    cookie_controller = CookieController(key="ecowatt_auth_controller")
    service = st.session_state.get("participant_auth_service")
    if service is None:
        service = ParticipantAuthService()
        st.session_state.participant_auth_service = service

    if "participant" in st.query_params:
        st.query_params.pop("participant", None)
    if controller_identity := cookie_controller.get(IDENTITY_COOKIE):
        cookie_controller.remove(IDENTITY_COOKIE, secure=True, same_site="strict")

    token = st.session_state.get("auth_session_token") or _auth_cookie_value(cookie_controller)
    if token:
        try:
            participant = service.restore(token)
        except AuthStorageUnavailable as exc:
            st.error(str(exc))
            st.stop()
        if participant:
            _set_authenticated_participant(participant)
        else:
            _remove_auth_cookie(cookie_controller)

    if "participant_id" not in st.session_state:
        for field in ("user_id", "user_name", "class_group", "role", "age_group", "gender"):
            st.session_state.pop(field, None)
        _render_authentication(cookie_controller, service)

    try:
        expires_at = datetime.fromisoformat(st.session_state.auth_expires_at)
    except (KeyError, TypeError, ValueError):
        expires_at = datetime.min.replace(tzinfo=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        _remove_auth_cookie(cookie_controller)
        _render_authentication(cookie_controller, service)

    if st.session_state.get("must_change_password"):
        _require_password_change(service, cookie_controller)

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
        f"<strong>{st.session_state.username}</strong></div>",
        unsafe_allow_html=True,
    )
    st.sidebar.caption("Participante")
    if st.sidebar.button("Sair", key="participant_logout"):
        try:
            service.logout(st.session_state.auth_session_token)
        except AuthStorageUnavailable as exc:
            st.sidebar.error(str(exc))
        else:
            _remove_auth_cookie(cookie_controller)
            st.rerun()

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
    presets = load_official_presets()
    for p in presets:
        if p["id"] == preset_id:
            st.session_state.appliances = convert_preset_to_appliances(p)
            st.session_state.tariff = float(p.get("tariff", 0.85))
            st.session_state.active_preset_name = p["name"]
            break
