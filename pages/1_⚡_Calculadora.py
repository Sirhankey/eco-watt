"""Calculadora de consumo individual de aparelhos."""
import streamlit as st
from ecowatt.utils.session import init_session_state
from ecowatt.utils.logging import track_event, track_event_on_change
from ecowatt.services.energy_calculator import calculate_daily_kwh, calculate_monthly_kwh, calculate_annual_kwh
from ecowatt.services.cost_calculator import project_costs
from ecowatt.services.preset_service import load_default_appliances
from ecowatt.components.cards import render_metric_card, render_cost_card, render_header, render_did_you_know, render_warning_badge
from ecowatt.components.charts import plot_cost_evolution_timeline

st.set_page_config(page_title="Calculadora — EcoWatt", page_icon="⚡", layout="wide")
init_session_state()
track_event("page_view", page="calculator")

render_header(
    title="Calculadora de Consumo e Custo",
    subtitle="Descubra quanto consome qualquer aparelho e quanto ele custa no final do mês.",
    icon="⚡",
)

# Catálogo rápido para preenchimento com 1 clique
default_apps = load_default_appliances()
app_names = ["(Digitar dados manualmente)"] + [f"{a.name} ({a.power_watts:.0f} W)" for a in default_apps]

selected_template = st.selectbox("Escolher aparelho comum como referência rápida:", app_names)

# Defaults baseados na seleção
def_name = "Chuveiro Elétrico"
def_power = 5500.0
def_hours = 0.5
def_days = 30.0

if selected_template != "(Digitar dados manualmente)":
    idx = app_names.index(selected_template) - 1
    chosen = default_apps[idx]
    def_name = chosen.name
    def_power = float(chosen.power_watts)
    def_hours = float(chosen.hours_per_day)
    def_days = float(chosen.days_per_month)

col_form, col_res = st.columns([1, 1], gap="large")

with col_form:
    st.markdown("### 📝 Dados do Aparelho")
    name = st.text_input("Nome ou Identificação do Aparelho:", value=def_name)

    power = st.number_input(
        "Potência Nominal (Watts):",
        min_value=1.0,
        max_value=25000.0,
        value=def_power,
        step=10.0,
        help="A potência geralmente vem gravada na etiqueta do fabricante ou na carcaça do aparelho.",
    )

    time_unit = st.radio(
        "Unidade do tempo de uso:",
        options=["Minutos", "Horas"],
        horizontal=True,
        index=0 if def_hours < 1.0 else 1,
    )

    if time_unit == "Minutos":
        def_minutes = int(round(def_hours * 60))
        minutes_input = st.number_input(
            "Tempo de uso diário (minutos):",
            min_value=1,
            max_value=1440,
            value=max(1, min(1440, def_minutes)),
            step=5,
            help="Informe o tempo médio de uso em minutos por dia (ex: 15, 30, 45 min).",
        )
        hours = minutes_input / 60.0
        st.caption(f"⏱️ Equivalente a **{hours:.2f} horas/dia** ({minutes_input} min)")
    else:
        hours = st.slider(
            "Tempo de uso diário (Horas por dia):",
            min_value=0.1,
            max_value=24.0,
            value=float(min(24.0, max(0.1, def_hours))),
            step=0.1,
            help="Exemplo: 1.5 horas = 1h30m.",
        )
        minutes_equiv = int(round(hours * 60))
        st.caption(f"⏱️ Equivalente a **{minutes_equiv} minutos/dia**")

    days = st.slider(
        "Frequência de uso no mês (Dias por mês):",
        min_value=1,
        max_value=31,
        value=int(def_days),
        step=1,
    )

    st.number_input(
        "Tarifa Elétrica (R$/kWh):",
        min_value=0.10,
        max_value=3.00,
        step=0.05,
        format="%.2f",
        key="tariff",
    )
    tariff = float(st.session_state.tariff)

# Cálculos
daily_kwh = calculate_daily_kwh(power, hours)
monthly_kwh = calculate_monthly_kwh(power, hours, days)
annual_kwh = calculate_annual_kwh(monthly_kwh)
costs = project_costs(daily_kwh, monthly_kwh, annual_kwh, tariff)
track_event_on_change(
    "calculator_event_signature",
    "calculator_completed",
    appliance_name=name,
    power_watts=power,
    hours_per_day=hours,
    days_per_month=days,
)

with col_res:
    st.markdown("### 📊 Resultado do Cálculo")

    m1, m2 = st.columns(2)
    with m1:
        render_metric_card(
            "Consumo de Energia",
            f"{monthly_kwh:.2f} kWh",
            f"Diário: {daily_kwh:.2f} kWh • Anual: {annual_kwh:.1f} kWh",
            border_color="#38bdf8",
        )
    with m2:
        render_cost_card(
            "Custo na Fatura",
            monthly_cost=costs["monthly_cost"],
            daily_cost=costs["daily_cost"],
            annual_cost=costs["annual_cost"],
            highlight="monthly",
            border_color="#10b981",
            extra_subtext=f"Tarifa: R$ {tariff:.2f}/kWh",
        )

    st.markdown(
        f"<div style='background: rgba(16, 185, 129, 0.1); border-left: 4px solid #10b981; padding: 12px 16px; border-radius: 6px; margin: 15px 0;'>"
        f"💬 <strong>Interpretação:</strong> O aparelho <strong>{name}</strong> ({power:.0f} W), ligado por {hours:.1f}h/dia durante {days} dias no mês, "
        f"representa um custo de aproximadamente <strong>R$ {costs['monthly_cost']:.2f} na sua conta mensal</strong>."
        f"</div>",
        unsafe_allow_html=True,
    )

    st.plotly_chart(
        plot_cost_evolution_timeline(costs["daily_cost"], costs["monthly_cost"], costs["annual_cost"]),
        use_container_width=True,
    )

render_warning_badge("Valores reais podem oscilar de acordo com bandeiras tarifárias, impostos (ICMS/PIS/COFINS) e variações na tensão da rede elétrica.")

render_did_you_know(
    "Como o cálculo é feito?",
    "A fórmula fundamental é: <strong>Consumo (kWh) = (Potência em Watts / 1000) × Horas por dia × Dias no mês</strong>. Em seguida, multiplica-se esse total pelo valor da tarifa (R$/kWh).",
)
