"""EcoWatt — Dashboard Principal."""
import streamlit as st
import random
from ecowatt.utils.session import init_session_state
from ecowatt.utils.logging import track_event
from ecowatt.services.energy_calculator import calculate_total_household_consumption
from ecowatt.services.cost_calculator import calculate_cost
from ecowatt.services.preset_service import load_facts
from ecowatt.components.cards import render_metric_card, render_cost_card, render_did_you_know, render_warning_badge
from ecowatt.components.charts import plot_household_distribution_donut, plot_cost_evolution_timeline

st.set_page_config(
    page_title="EcoWatt — Economia Inteligente de Energia",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()
track_event("page_view", page="dashboard")

# Sidebar: Configuração global rápida
with st.sidebar:
    st.markdown("### ⚙️ Configurações Globais")
    st.number_input(
        "Tarifa Elétrica (R$/kWh):",
        min_value=0.10,
        max_value=3.00,
        step=0.05,
        format="%.2f",
        key="tariff",
        help="Valor médio cobrado pela concessionária por cada kWh consumido. No Brasil varia entre R$ 0,70 e R$ 1,20.",
    )
    st.caption("Tarifa editável aplicada em todas as páginas da ferramenta.")
    st.divider()
    st.markdown("### 💡 Dica Rápida")
    facts = load_facts()
    if facts:
        fact = facts[0]
        st.info(f"**{fact['title']}**\n\n{fact['fact']}")

# Main Header / Hero
st.markdown(
    """
    <div style="background: linear-gradient(135deg, #064e3b 0%, #0f172a 100%); padding: 30px; border-radius: 16px; margin-bottom: 25px; border: 1px solid rgba(16, 185, 129, 0.3);">
        <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
            <span style="font-size: 3rem;">⚡</span>
            <div>
                <h1 style="color: #f8fafc; margin: 0; font-size: 2.4rem; font-weight: 800;">EcoWatt</h1>
                <p style="color: #34d399; margin: 0; font-size: 1.1rem; font-weight: 600;">Economia de Energia Elétrica & Consumo Consciente</p>
            </div>
        </div>
        <p style="color: #cbd5e1; font-size: 1.05rem; max-width: 850px; line-height: 1.5; margin: 0;">
            Descubra de forma prática e visual: <strong>quanto seus aparelhos consomem</strong>,
            <strong>quanto isso custa na sua conta</strong> e <strong>como pequenas mudanças de hábito geram grande economia</strong>.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Resumo Residencial Atual
household_data = calculate_total_household_consumption(st.session_state.appliances)
total_monthly_kwh = household_data["total_monthly_kwh"]
total_daily_kwh = round(total_monthly_kwh / 30.0, 1)
total_annual_kwh = household_data["total_annual_kwh"]

total_monthly_cost = calculate_cost(total_monthly_kwh, st.session_state.tariff)
total_daily_cost = round(total_monthly_cost / 30.0, 2)
total_annual_cost = calculate_cost(total_annual_kwh, st.session_state.tariff)

# Potential Savings Scenario (~20% conservador)
pot_savings_kwh = round(total_monthly_kwh * 0.20, 1)
pot_savings_cost_month = round(total_monthly_cost * 0.20, 2)
pot_savings_cost_day = round(pot_savings_cost_month / 30.0, 2)
pot_savings_cost_year = round(total_annual_cost * 0.20, 2)

col1, col2, col3 = st.columns(3)
with col1:
    render_metric_card(
        label="Consumo Total da Casa",
        value=f"{total_monthly_kwh:.1f} kWh",
        subtext=f"Diário: {total_daily_kwh:.1f} kWh • Anual: {total_annual_kwh:.0f} kWh",
        border_color="#38bdf8",
    )
with col2:
    render_cost_card(
        label="Custo Estimado da Conta",
        monthly_cost=total_monthly_cost,
        daily_cost=total_daily_cost,
        annual_cost=total_annual_cost,
        highlight="monthly",
        border_color="#10b981",
        extra_subtext=f"Tarifa: R$ {st.session_state.tariff:.2f} / kWh",
    )
with col3:
    render_cost_card(
        label="Potencial de Economia (20%)",
        monthly_cost=pot_savings_cost_month,
        daily_cost=pot_savings_cost_day,
        annual_cost=pot_savings_cost_year,
        highlight="monthly",
        border_color="#a855f7",
        extra_subtext=f"Redução de ~{pot_savings_kwh:.1f} kWh/mês com hábitos conscientes",
    )

render_warning_badge("Os valores apresentados são estimativas calculadas com base nas potências nominais e tempos médios de uso.")

# Visualização Gráfica
col_chart1, col_chart2 = st.columns([1, 1])

with col_chart1:
    if household_data["items"]:
        st.plotly_chart(
            plot_household_distribution_donut(household_data["items"]),
            use_container_width=True,
        )
    else:
        st.info("Nenhum aparelho cadastrado no momento.")

with col_chart2:
    daily_c = round(total_monthly_cost / 30.0, 2)
    st.plotly_chart(
        plot_cost_evolution_timeline(daily_c, total_monthly_cost, total_annual_cost),
        use_container_width=True,
    )

# Guia de Navegação Rápida
st.markdown("### 🚀 O que você deseja explorar hoje?")
nav_col1, nav_col2, nav_col3 = st.columns(3)

with nav_col1:
    with st.container(border=True):
        st.markdown(
            """
            <div style="min-height: 110px;">
                <h4 style="margin: 0 0 8px 0; color: #f8fafc;">⚡ Calculadora de Aparelhos</h4>
                <p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.4; margin: 0;">
                    Calcule o consumo exato de qualquer aparelho elétrico informando potência e tempo de uso.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/1_⚡_Calculadora.py", label="Explorar Calculadora →", use_container_width=True)

with nav_col2:
    with st.container(border=True):
        st.markdown(
            """
            <div style="min-height: 110px;">
                <h4 style="margin: 0 0 8px 0; color: #f8fafc;">🔄 Comparador de Aparelhos</h4>
                <p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.4; margin: 0;">
                    Coloque dois produtos lado a lado e veja a diferença de consumo e economia na fatura anual.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/2_🔄_Comparador.py", label="Explorar Comparador →", use_container_width=True)

with nav_col3:
    with st.container(border=True):
        st.markdown(
            """
            <div style="min-height: 110px;">
                <h4 style="margin: 0 0 8px 0; color: #f8fafc;">🏠 Simulador Minha Casa</h4>
                <p style="color: #94a3b8; font-size: 0.9rem; line-height: 1.4; margin: 0;">
                    Monte o inventário da sua casa, identifique os vilões de energia e valide com sua fatura real.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.page_link("pages/3_🏠_Minha_Casa.py", label="Explorar Minha Casa →", use_container_width=True)

# Fato educativo randômico no rodapé
if facts:
    random_fact = random.choice(facts)
    render_did_you_know(random_fact["title"], random_fact["fact"])
