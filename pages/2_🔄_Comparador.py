"""Comparador direto entre dois aparelhos elétricos."""
import streamlit as st
from ecowatt.utils.session import init_session_state
from ecowatt.models.appliance import Appliance
from ecowatt.services.comparison_service import compare_appliances
from ecowatt.components.cards import render_metric_card, render_cost_card, render_header, render_did_you_know, render_warning_badge
from ecowatt.components.charts import plot_comparison_bar_chart

st.set_page_config(page_title="Comparador — EcoWatt", page_icon="🔄", layout="wide")
init_session_state()

render_header(
    title="Comparador de Aparelhos",
    subtitle="Compare dois equipamentos ou hábitos de uso e veja a diferença no consumo e no bolso.",
    icon="🔄",
)

# Exemplos didáticos prontos
presets_comp = {
    "Personalizado": None,
    "💡 Iluminação: LED vs Incandescente": {
        "a": {"name": "Lâmpada LED 9W", "power": 9.0, "hours": 6.0, "days": 30},
        "b": {"name": "Lâmpada Incandescente 60W", "power": 60.0, "hours": 6.0, "days": 30},
    },
    "❄️ Climatização: Ar-Condicionado Inverter vs Ar Antigo": {
        "a": {"name": "Ar-Condicionado Inverter", "power": 650.0, "hours": 8.0, "days": 30},
        "b": {"name": "Ar-Condicionado Convencional Antigo", "power": 1100.0, "hours": 8.0, "days": 30},
    },
    "🚿 Hábito de Banho: Banho Curto (10 min) vs Banho Longo (25 min)": {
        "a": {"name": "Chuveiro (Banho 10 min)", "power": 5500.0, "hours": 0.17, "days": 30},
        "b": {"name": "Chuveiro (Banho 25 min)", "power": 5500.0, "hours": 0.42, "days": 30},
    },
}

def on_preset_change():
    chosen = st.session_state.get("selected_preset_key")
    if chosen and chosen in presets_comp and presets_comp[chosen]:
        cfg = presets_comp[chosen]
        st.session_state.comp_name_a = cfg["a"]["name"]
        st.session_state.comp_pow_a = float(cfg["a"]["power"])
        st.session_state.comp_h_a = float(cfg["a"]["hours"])
        st.session_state.comp_d_a = int(cfg["a"]["days"])

        st.session_state.comp_name_b = cfg["b"]["name"]
        st.session_state.comp_pow_b = float(cfg["b"]["power"])
        st.session_state.comp_h_b = float(cfg["b"]["hours"])
        st.session_state.comp_d_b = int(cfg["b"]["days"])

# Garantir inicialização dos widgets no session_state
if "comp_name_a" not in st.session_state:
    st.session_state.comp_name_a = "Aparelho Eficiente A"
    st.session_state.comp_pow_a = 100.0
    st.session_state.comp_h_a = 4.0
    st.session_state.comp_d_a = 30

if "comp_name_b" not in st.session_state:
    st.session_state.comp_name_b = "Aparelho Tradicional B"
    st.session_state.comp_pow_b = 300.0
    st.session_state.comp_h_b = 4.0
    st.session_state.comp_d_b = 30

selected_preset = st.selectbox(
    "Carregar cenário de comparação pronto:",
    list(presets_comp.keys()),
    key="selected_preset_key",
    on_change=on_preset_change,
)

col_a, col_b = st.columns(2, gap="large")

with col_a:
    st.markdown("### 🅰️ Aparelho A (ou Cenário 1)")
    name_a = st.text_input("Nome do Aparelho A:", key="comp_name_a")
    power_a = st.number_input("Potência (Watts):", min_value=1.0, max_value=25000.0, step=10.0, key="comp_pow_a")
    hours_a = st.slider("Horas por dia:", 0.1, 24.0, step=0.1, key="comp_h_a")
    days_a = st.slider("Dias por mês:", 1, 31, step=1, key="comp_d_a")

with col_b:
    st.markdown("### 🅱️ Aparelho B (ou Cenário 2)")
    name_b = st.text_input("Nome do Aparelho B:", key="comp_name_b")
    power_b = st.number_input("Potência (Watts):", min_value=1.0, max_value=25000.0, step=10.0, key="comp_pow_b")
    hours_b = st.slider("Horas por dia:", 0.1, 24.0, step=0.1, key="comp_h_b")
    days_b = st.slider("Dias por mês:", 1, 31, step=1, key="comp_d_b")

tariff = float(st.session_state.tariff)

# Executar comparação
app_a = Appliance(id="a", name=name_a, power_watts=power_a, hours_per_day=hours_a, days_per_month=days_a)
app_b = Appliance(id="b", name=name_b, power_watts=power_b, hours_per_day=hours_b, days_per_month=days_b)

res = compare_appliances(app_a, app_b, tariff)

st.divider()
st.markdown("### 🎯 Veredito e Diferença de Custos")

st.info(f"💡 **Conclusão:** {res['summary']}")

diff_cost_month = res["diff_cost_monthly"]
diff_cost_day = round(diff_cost_month / 30.0, 2)
diff_cost_year = res["diff_cost_annual"]

v1, v2, v3 = st.columns(3)
with v1:
    render_metric_card(
        label="Diferença de Consumo",
        value=f"{res['diff_kwh_monthly']:.1f} kWh",
        subtext=f"Diário: {res['diff_kwh_monthly']/30.0:.2f} kWh • Anual: {res['diff_kwh_annual']:.1f} kWh",
        border_color="#38bdf8",
    )
with v2:
    render_cost_card(
        label="Economia Financeira",
        monthly_cost=diff_cost_month,
        daily_cost=diff_cost_day,
        annual_cost=diff_cost_year,
        highlight="monthly",
        border_color="#10b981",
        extra_subtext="Dinheiro poupado escolhendo o mais eficiente",
    )
with v3:
    render_metric_card(
        label="Mais Eficiente",
        value=f"{res['appliance_a']['name'] if res['winner'] == 'A' else (res['appliance_b']['name'] if res['winner'] == 'B' else 'Empate')}",
        subtext=f"Economiza até R$ {diff_cost_year:.2f}/ano",
        border_color="#a855f7",
    )

st.plotly_chart(
    plot_comparison_bar_chart(
        res["appliance_a"]["name"],
        res["appliance_a"]["monthly_kwh"],
        res["appliance_b"]["name"],
        res["appliance_b"]["monthly_kwh"],
    ),
    use_container_width=True,
)

render_warning_badge("Atenção: Menor potência nem sempre significa maior eficiência em todos os tipos de tarefas. O tempo total necessário para realizar o trabalho também deve ser levado em conta.")

render_did_you_know(
    "Potência x Eficiência",
    "Um micro-ondas de 1.200 W pode gastar MENOS energia para esquentar um prato de comida do que um forninho elétrico de 600 W, simplesmente porque o micro-ondas realiza a mesma tarefa em 2 minutos, enquanto o forno levaria 20 minutos!",
)
