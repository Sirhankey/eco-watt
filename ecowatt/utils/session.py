"""Session state initialization and state management utilities."""
import streamlit as st
from ecowatt.services.preset_service import (
    load_presets,
    convert_preset_to_appliances,
    load_default_appliances,
)
from ecowatt.utils.logging import create_user_id, track_event


def init_session_state():
    """Initializes standard state variables in st.session_state if not present."""
    if "user_id" not in st.session_state:
        with st.form("user_identification"):
            st.markdown("### Identificação da sessão")
            st.caption("Responda para registrar sua participação na feira de ciências.")
            user_name = st.text_input("Nome:", key="user_name_input")
            role = st.selectbox(
                "Perfil:",
                ["Aluno", "Professor", "Responsável", "Convidado"],
                key="role_input",
            )
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
        track_event("user_identified", role=role, age_group=age_group, gender=gender)

    is_new_session = "analytics_session_started" not in st.session_state
    if is_new_session:
        st.session_state.analytics_session_started = True

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

    if is_new_session:
        track_event("session_started")

    _render_feedback_form()


def _render_feedback_form() -> None:
    """Render the optional end-of-visit survey in the shared sidebar."""
    if st.session_state.get("feedback_submitted", False):
        st.sidebar.success("Avaliação registrada. Obrigado!")
        return

    with st.sidebar.expander("⭐ Avaliar experiência", expanded=False):
        st.caption("Preencha quando terminar de explorar o aplicativo.")
        with st.form("experience_feedback"):
            rating = st.radio(
                "Como você avalia a experiência?",
                ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"],
                horizontal=True,
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
                rating=rating.count("⭐"),
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
