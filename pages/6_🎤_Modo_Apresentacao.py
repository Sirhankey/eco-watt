"""Modo Apresentação — Demonstração simplificada de 30 segundos para feira de ciências ou sala de aula."""
import streamlit as st
from ecowatt.utils.session import init_session_state
from ecowatt.services.energy_calculator import calculate_monthly_kwh
from ecowatt.services.cost_calculator import calculate_cost
from ecowatt.components.cards import render_metric_card, render_cost_card

st.set_page_config(page_title="Modo Apresentação — EcoWatt", page_icon="🎤", layout="centered")
init_session_state()

# Layout focado e de alto impacto visual para projetores e telas
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 25px;">
        <span style="font-size: 3.5rem;">🎤⚡</span>
        <h1 style="font-size: 2.8rem; font-weight: 900; margin: 0; color: #38bdf8;">EcoWatt Show</h1>
        <p style="font-size: 1.3rem; color: #94a3b8; margin-top: 5px;">
            Demonstração Rápida em 30 Segundos
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

quick_items = {
    "🚿 Chuveiro Elétrico Potente": {"power": 5500.0, "time_min": 15, "icon": "🚿", "hint": "Alta potência concentrada em poucos minutos."},
    "❄️ Ar-Condicionado Quarto": {"power": 900.0, "time_min": 480, "icon": "❄️", "hint": "Potência média, mas ligado a noite inteira (8h)."},
    "🎮 Computador Gamer Completo": {"power": 380.0, "time_min": 240, "icon": "🎮", "hint": "Jogatina de 4 horas com placa de vídeo dedicada."},
    "💡 Lâmpada Incandescente Antiga": {"power": 60.0, "time_min": 360, "icon": "💡", "hint": "6 horas ligada iluminando a sala."},
    "🌱 Lâmpada LED Moderna": {"power": 9.0, "time_min": 360, "icon": "🌱", "hint": "Ilumina o mesmo que a incandescente, mas gasta 85% menos."},
}

selected_demo = st.selectbox("Escolha um aparelho para demonstrar:", list(quick_items.keys()))

item_info = quick_items[selected_demo]

col_in1, col_in2 = st.columns(2)
with col_in1:
    power_w = st.number_input("Potência do Aparelho (Watts):", min_value=1.0, max_value=25000.0, value=item_info["power"], step=50.0)
with col_in2:
    time_min = st.number_input("Tempo de Uso Diário (Minutos):", min_value=1, max_value=1440, value=item_info["time_min"], step=5)

hours_day = time_min / 60.0
monthly_kwh = calculate_monthly_kwh(power_w, hours_day, days_per_month=30)
monthly_cost = calculate_cost(monthly_kwh, st.session_state.tariff)
annual_cost = calculate_cost(monthly_kwh * 12.0, st.session_state.tariff)

daily_cost = round(monthly_cost / 30.0, 2)

st.markdown(f"*{item_info['hint']}*")

st.markdown(
    """
    <div style="text-align: center; font-size: 2rem; margin: 10px 0; color: #10b981;">
        ⬇️
    </div>
    """,
    unsafe_allow_html=True,
)

res1, res2, res3 = st.columns(3)
with res1:
    render_metric_card(
        "Consumo de Energia",
        f"{monthly_kwh:.1f} kWh",
        f"Diário: {monthly_kwh/30.0:.2f} kWh • Anual: {monthly_kwh*12:.0f} kWh",
        border_color="#38bdf8",
    )
with res2:
    render_cost_card(
        "Custo Estimado",
        monthly_cost=monthly_cost,
        daily_cost=daily_cost,
        annual_cost=annual_cost,
        highlight="monthly",
        border_color="#10b981",
        extra_subtext=f"Tarifa: R$ {st.session_state.tariff:.2f}/kWh",
    )
with res3:
    render_metric_card(
        "Tempo de Uso",
        f"{time_min} min/dia",
        f"Equivale a {hours_day:.2f}h por dia",
        border_color="#f59e0b",
    )

st.markdown(
    f"<div style='background: rgba(14, 165, 233, 0.1); border: 2px solid #38bdf8; border-radius: 12px; padding: 20px; text-align: center; margin-top: 20px;'>"
    f"<h3 style='color: #f8fafc; margin: 0 0 10px 0;'>⚡ Frase de Impacto para a Apresentação:</h3>"
    f"<p style='font-size: 1.25rem; color: #38bdf8; font-weight: 700; margin: 0;'>"
    f"Deixar este aparelho ligado por apenas {time_min} minutos por dia custa R$ {monthly_cost:.2f} no mês e R$ {annual_cost:.2f} todos os anos!"
    f"</p>"
    f"</div>",
    unsafe_allow_html=True,
)
