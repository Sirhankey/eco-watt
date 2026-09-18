"""PC Energy Builder — Estimador de consumo de hardware de computador e perfis de atividade."""
import uuid
import streamlit as st
import plotly.express as px
from ecowatt.utils.session import init_session_state
from ecowatt.models.appliance import Appliance
from ecowatt.models.pc_component import PCComponent, PCUsageProfile
from ecowatt.services.pc_energy_service import (
    load_default_pc_components,
    calculate_pc_energy,
)
from ecowatt.components.cards import render_metric_card, render_cost_card, render_header, render_did_you_know, render_warning_badge

st.set_page_config(page_title="PC Builder — EcoWatt", page_icon="🖥️", layout="wide")
init_session_state()

render_header(
    title="PC Energy Builder",
    subtitle="Monte sua configuração de computador, configure seu perfil de uso e estime o consumo elétrico real.",
    icon="🖥️",
)

catalog = load_default_pc_components()

tab_builder, tab_compare = st.tabs(["🛠️ Montar e Simular Computador", "🎮 Comparar 2 Setups"])

with tab_builder:
    col_parts, col_usage = st.columns([1, 1], gap="large")

    with col_parts:
        st.markdown("### 🧩 Escolha os Componentes")

        # CPU
        c_cpu_ico, c_cpu_sel = st.columns([1, 4])
        with c_cpu_ico:
            try:
                with open("assets/img/hardware/cpu.svg", "r", encoding="utf-8") as f:
                    st.markdown(f"<div style='width: 50px; height: 50px; margin-top: 15px;'>{f.read()}</div>", unsafe_allow_html=True)
            except Exception:
                st.markdown("🧠")
        with c_cpu_sel:
            cpu_names = [f"{c.name} (TDP {c.tdp_watts}W)" for c in catalog["cpus"]]
            sel_cpu_idx = st.selectbox("Processador (CPU):", range(len(cpu_names)), format_func=lambda i: cpu_names[i])
            selected_cpu = catalog["cpus"][sel_cpu_idx]

        # GPU
        c_gpu_ico, c_gpu_sel = st.columns([1, 4])
        with c_gpu_ico:
            try:
                with open("assets/img/hardware/gpu.svg", "r", encoding="utf-8") as f:
                    st.markdown(f"<div style='width: 50px; height: 50px; margin-top: 15px;'>{f.read()}</div>", unsafe_allow_html=True)
            except Exception:
                st.markdown("🎮")
        with c_gpu_sel:
            gpu_names = [f"{c.name} (TDP {c.tdp_watts}W)" for c in catalog["gpus"]]
            sel_gpu_idx = st.selectbox("Placa de Vídeo (GPU):", range(len(gpu_names)), format_func=lambda i: gpu_names[i])
            selected_gpu = catalog["gpus"][sel_gpu_idx]

        # RAM
        c_ram_ico, c_ram_sel = st.columns([1, 4])
        with c_ram_ico:
            try:
                with open("assets/img/hardware/ram.svg", "r", encoding="utf-8") as f:
                    st.markdown(f"<div style='width: 50px; height: 50px; margin-top: 15px;'>{f.read()}</div>", unsafe_allow_html=True)
            except Exception:
                st.markdown("⚡")
        with c_ram_sel:
            ram_names = [f"{c.name} ({c.tdp_watts}W)" for c in catalog["rams"]]
            sel_ram_idx = st.selectbox("Memória RAM:", range(len(ram_names)), format_func=lambda i: ram_names[i])
            selected_ram = catalog["rams"][sel_ram_idx]

        # Armazenamento
        c_stor_ico, c_stor_sel = st.columns([1, 4])
        with c_stor_ico:
            try:
                with open("assets/img/hardware/storage.svg", "r", encoding="utf-8") as f:
                    st.markdown(f"<div style='width: 50px; height: 50px; margin-top: 15px;'>{f.read()}</div>", unsafe_allow_html=True)
            except Exception:
                st.markdown("💾")
        with c_stor_sel:
            stor_names = [f"{c.name} ({c.tdp_watts}W)" for c in catalog["storages"]]
            sel_stor_idx = st.selectbox("Armazenamento:", range(len(stor_names)), format_func=lambda i: stor_names[i])
            selected_storage = catalog["storages"][sel_stor_idx]

        # Monitor
        c_mon_ico, c_mon_sel = st.columns([1, 4])
        with c_mon_ico:
            try:
                with open("assets/img/hardware/monitor.svg", "r", encoding="utf-8") as f:
                    st.markdown(f"<div style='width: 50px; height: 50px; margin-top: 15px;'>{f.read()}</div>", unsafe_allow_html=True)
            except Exception:
                st.markdown("🖥️")
        with c_mon_sel:
            mon_names = [f"{c.name} ({c.tdp_watts}W)" for c in catalog["monitors"]]
            sel_mon_idx = st.selectbox("Monitor:", range(len(mon_names)), format_func=lambda i: mon_names[i])
            selected_mon = catalog["monitors"][sel_mon_idx]

        # Fixos essenciais
        selected_mb = catalog["motherboards"][0]
        selected_periph = catalog["peripherals"][0]

        components = [selected_cpu, selected_gpu, selected_ram, selected_storage, selected_mon, selected_mb, selected_periph]

        st.markdown("#### ⚡ Eficiência da Fonte (PSU)")
        psu_eff = st.select_slider(
            "Certificação da Fonte de Alimentação:",
            options=[0.75, 0.80, 0.85, 0.90, 0.92],
            value=0.85,
            format_func=lambda x: f"{int(x*100)}% ({'80 Plus Gold' if x>=0.90 else '80 Plus Bronze' if x>=0.85 else 'Padrão 80 Plus' if x>=0.80 else 'Genérica'})",
            help="Fontes mais eficientes puxam menos energia da tomada para entregar a mesma potência aos componentes.",
        )

    with col_usage:
        st.markdown("### ⏱️ Perfil de Utilização Diária")
        st.caption("Distribua as 24 horas do dia entre suas atividades no computador:")

        h_study = st.slider("Estudos / Tarefas Leves / Navegação (horas/dia):", 0.0, 16.0, 2.0, 0.5)
        h_game = st.slider("Jogos Pesados / Renderização 3D (horas/dia):", 0.0, 16.0, 3.0, 0.5)
        h_idle = st.slider("Vídeos / Música / Ocioso ligado (horas/dia):", 0.0, 16.0, 2.0, 0.5)

        active_sum = h_study + h_game + h_idle
        h_standby = max(0.0, 24.0 - active_sum)

        # Totalizador de Horas com badge visual
        col_tot1, col_tot2 = st.columns(2)
        with col_tot1:
            st.metric("Total em Uso Ativo", f"{active_sum:.1f} h/dia", help="Tempo diário que o computador está trabalhando.")
        with col_tot2:
            st.metric("Stand-by / Desligado", f"{h_standby:.1f} h/dia", help="Tempo restante do dia conectado na tomada.")

        if active_sum > 24.0:
            st.error(f"⚠️ A soma das atividades ativas ({active_sum:.1f}h) excede as 24h de um dia! Ajuste os sliders.")

        profile = PCUsageProfile(
            study_office_hours=min(h_study, 24.0),
            gaming_heavy_hours=min(h_game, 24.0),
            light_idle_hours=min(h_idle, 24.0),
            standby_off_hours=h_standby,
        )

        days_pc = st.slider("Dias de uso do computador no mês:", 1, 31, 30, 1)

    # Execução do cálculo
    tariff = float(st.session_state.tariff)
    pc_result = calculate_pc_energy(
        components=components,
        profile=profile,
        days_per_month=days_pc,
        psu_efficiency=psu_eff,
        tariff=tariff,
    )

    st.divider()
    st.markdown("### 📊 Estimativa de Consumo e Impacto Financeiro")

    p1, p2, p3, p4 = st.columns(4)
    with p1:
        render_metric_card("Potência Pico Estimada", f"{pc_result['peak_gaming_wall_watts']:.0f} W", f"TDP Nominal: {pc_result['total_tdp']:.0f} W", border_color="#ec4899")
    with p2:
        render_metric_card("Média Ativa na Tomada", f"{pc_result['average_active_wall_watts']:.0f} W", "Durante o uso real", border_color="#38bdf8")
    with p3:
        render_metric_card(
            "Consumo de Energia",
            f"{pc_result['monthly_kwh']:.1f} kWh",
            f"Diário: {pc_result['daily_kwh']:.2f} kWh • Anual: {pc_result['annual_kwh']:.0f} kWh",
            border_color="#10b981",
        )
    with p4:
        render_cost_card(
            "Custo do Computador",
            monthly_cost=pc_result["monthly_cost"],
            daily_cost=pc_result["daily_cost"],
            annual_cost=pc_result["annual_cost"],
            highlight="monthly",
            border_color="#f59e0b",
            extra_subtext=f"Tarifa: R$ {tariff:.2f}/kWh",
        )

    # Botão de exportação para a residência "Minha Casa"
    st.markdown("#### 🏠 Levar este Computador para 'Minha Casa'")
    c_add_pc1, c_add_pc2 = st.columns([2, 1])
    with c_add_pc1:
        pc_dest_room = st.selectbox(
            "Cômodo onde o PC ficará:",
            options=st.session_state.get("rooms", ["Quarto", "Sala", "Escritório", "Cozinha", "Banheiro", "Lavanderia"]),
            index=0,
            key="pc_dest_room",
        )
    with c_add_pc2:
        st.write("")
        st.write("")
        if st.button("➕ Adicionar PC à Minha Casa", type="primary", width="stretch"):
            avg_w = pc_result["average_active_wall_watts"]
            act_h = max(0.1, float(active_sum))
            pc_item = Appliance(
                id=str(uuid.uuid4())[:8],
                name="Computador PC Builder",
                power_watts=round(avg_w, 1),
                hours_per_day=round(act_h, 1),
                days_per_month=float(days_pc),
                category=pc_dest_room,
                description=f"PC customizado ({active_sum:.1f}h ativo @ {avg_w:.0f}W médio)",
            )
            st.session_state.appliances.append(pc_item)
            st.session_state.quick_add_notification = f"🎉 Computador PC Builder ({round(avg_w)} W, {act_h:.1f}h/dia) adicionado ao cômodo '{pc_dest_room}'!"
            st.success(f"Computador adicionado ao cômodo '{pc_dest_room}' da sua casa com sucesso!")

    # Gráfico de carga por componente em jogos
    st.markdown("#### 🎮 Demanda Máxima por Componente (Tomada em Jogos)")
    breakdown_df = [
        {"Componente": b["name"], "Potência (W)": b["gaming_load_watts"]}
        for b in pc_result["breakdown"]
    ]
    fig_pc = px.bar(
        breakdown_df,
        x="Componente",
        y="Potência (W)",
        color="Potência (W)",
        color_continuous_scale="Reds",
        text="Potência (W)",
    )
    fig_pc.update_traces(texttemplate="%{text:.0f} W", textposition="outside")
    fig_pc.update_layout(margin=dict(l=20, r=20, t=30, b=30), height=320)
    st.plotly_chart(fig_pc, width="stretch")

with tab_compare:
    st.markdown("### 🎮 Comparar 2 Setups")
    st.caption("Monte cada configuração e atribua seus componentes ao Setup A ou ao Setup B.")

    def render_setup_selector(prefix, title, icon):
        st.markdown(f"#### {icon} {title}")

        selected_components = []
        selector_fields = [
            ("cpus", "Processador (CPU)"),
            ("gpus", "Placa de Vídeo (GPU)"),
            ("rams", "Memória RAM"),
            ("storages", "Armazenamento"),
            ("monitors", "Monitor"),
        ]
        for category, label in selector_fields:
            options = catalog[category]
            selected_index = st.selectbox(
                label,
                range(len(options)),
                format_func=lambda index, items=options: f"{items[index].name} ({items[index].tdp_watts:.0f} W)",
                key=f"{prefix}_{category}",
            )
            selected_components.append(options[selected_index])

        selected_components.extend([catalog["motherboards"][0], catalog["peripherals"][0]])
        return selected_components

    setup_col_a, setup_col_b = st.columns(2)
    with setup_col_a:
        setup_a_comps = render_setup_selector("setup_a", "Setup A", "💻")
    with setup_col_b:
        setup_b_comps = render_setup_selector("setup_b", "Setup B", "🚀")

    prof_gamer = PCUsageProfile(study_office_hours=2, gaming_heavy_hours=4, light_idle_hours=2, standby_off_hours=16)

    res_a = calculate_pc_energy(setup_a_comps, prof_gamer, days_per_month=30, psu_efficiency=0.85, tariff=tariff)
    res_b = calculate_pc_energy(setup_b_comps, prof_gamer, days_per_month=30, psu_efficiency=0.85, tariff=tariff)

    diff_kwh = res_b["annual_kwh"] - res_a["annual_kwh"]
    diff_money = res_b["annual_cost"] - res_a["annual_cost"]

    cb1, cb2 = st.columns(2)
    with cb1:
        st.markdown("#### 💻 Setup A: PC Escritório / Estudos")
        st.write("• CPU Básica com Gráficos Integrados")
        st.write("• Monitor 24'' Full HD")
        render_cost_card(
            label="Custo Setup A",
            monthly_cost=res_a["monthly_cost"],
            daily_cost=res_a["daily_cost"],
            annual_cost=res_a["annual_cost"],
            highlight="monthly",
            border_color="#38bdf8",
            extra_subtext=f"Consumo: {res_a['monthly_kwh']:.1f} kWh/mês",
        )

    with cb2:
        st.markdown("#### 🚀 Setup B: PC Gamer Entusiasta")
        st.write("• CPU Alta Performance + GPU Dedicada Topo")
        st.write("• Monitor 27'' QHD 144Hz")
        render_cost_card(
            label="Custo Setup B",
            monthly_cost=res_b["monthly_cost"],
            daily_cost=res_b["daily_cost"],
            annual_cost=res_b["annual_cost"],
            highlight="monthly",
            border_color="#ec4899",
            extra_subtext=f"Consumo: {res_b['monthly_kwh']:.1f} kWh/mês",
        )

    st.markdown(
        f"""
        <div style="background: rgba(245, 158, 11, 0.1); border-left: 4px solid #f59e0b; padding: 15px; border-radius: 8px; margin-top: 15px;">
            💡 <strong>Diferença de Consumo Anual:</strong><br>
            A configuração Gamer B consome aproximadamente <strong>{diff_kwh:.1f} kWh a mais por ano</strong> do que o Setup A,
            o que representa um impacto de <strong>R$ {diff_money:.2f} a mais por ano na conta de luz</strong>.
        </div>
        """,
        unsafe_allow_html=True,
    )

render_warning_badge("A potência real na tomada foi calculada considerando o perfil ponderado de uso e a eficiência da fonte (80 Plus), não sendo uma soma estática de TDP máximo.")

render_did_you_know(
    "A Importância da Fonte de Alimentação (80 Plus)",
    "Uma fonte com selo 80 Plus Gold dissipa muito menos calor do que uma fonte de baixa qualidade genérica. Em um PC que fica muitas horas ligado para jogos pesados, a economia de energia na tomada pode pagar o custo de uma fonte de melhor qualidade ao longo do ano!",
)
