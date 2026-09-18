"""Simulador do consumo elétrico da residência, inventário, ranking e validação de fatura real."""
import streamlit as st
import uuid
from ecowatt.utils.session import init_session_state, reset_to_preset
from ecowatt.utils.logging import track_event, track_event_on_change
from ecowatt.models.appliance import Appliance
from ecowatt.services.energy_calculator import calculate_total_household_consumption
from ecowatt.services.cost_calculator import calculate_cost
from ecowatt.services.preset_service import (
    load_presets,
    load_default_appliances,
    validate_against_real_bill,
)
from ecowatt.components.cards import render_metric_card, render_cost_card, render_header, render_did_you_know, render_warning_badge
from ecowatt.components.charts import (
    plot_household_distribution_donut,
    plot_appliances_bar_chart,
)

st.set_page_config(page_title="Minha Casa — EcoWatt", page_icon="🏠", layout="wide")
init_session_state()
track_event("page_view", page="home_simulator")

# CSS responsivo para botões de ação e cards no mobile e desktop
st.markdown(
    """
    <style>
    /* Botão compacto de configuração do card */
    [data-testid="stPopoverButton"] {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        color: #94a3b8 !important;
        font-size: 0.95rem !important;
        padding: 4px 8px !important;
        height: 30px !important;
        min-height: 30px !important;
        border-radius: 6px !important;
        transition: all 0.15s ease !important;
        margin-top: 4px !important;
        margin-left: auto !important;
    }

    [data-testid="stPopoverButton"]:hover {
        background: rgba(56, 189, 248, 0.12) !important;
        border-color: #38bdf8 !important;
        color: #38bdf8 !important;
    }

    /* Efeito de hover no container do card */
    div[data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stPopoverButton"]) {
        transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease !important;
        border-radius: 12px !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:has([data-testid="stPopoverButton"]):hover {
        border-color: rgba(56, 189, 248, 0.4) !important;
        box-shadow: 0 4px 16px -2px rgba(0, 0, 0, 0.35) !important;
    }

    /* Regras específicas para telas pequenas / Mobile */
    @media (max-width: 768px) {
        [data-testid="stPopoverButton"] {
            width: 42px !important;
            min-width: 42px !important;
            height: 30px !important;
            min-height: 30px !important;
            padding: 4px 8px !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

render_header(
    title="Simulador de Residência — Minha Casa",
    subtitle="Monte o inventário dos seus aparelhos, identifique os maiores consumidores e compare com sua fatura real.",
    icon="🏠",
)

# 1. Seção de Identificação do Aluno / Família e Presets Didáticos
presets = load_presets()
preset_names = [p["name"] for p in presets]

col_fam, col_preset, col_tariff = st.columns([1.2, 1.4, 0.9])

with col_fam:
    st.markdown("##### 👨‍👩‍👧‍👦 Residência / Família")
    st.session_state.family_name = st.text_input(
        "Nome da Casa / Família:",
        value=st.session_state.get("family_name", "Minha Residência"),
        help="Personalize o nome da residência que o aluno está simulando.",
    )

with col_preset:
    st.markdown("##### ⚡ Cenários Prontos")
    sel_p_name = st.selectbox("Carregar perfil pré-configurado:", ["(Manter atual)"] + preset_names)
    if sel_p_name != "(Manter atual)":
        for p in presets:
            if p["name"] == sel_p_name:
                if st.button(f"📥 Aplicar '{p['name']}'"):
                    reset_to_preset(p["id"])
                    st.session_state.family_name = f"Casa ({p['name'].split('(')[0].strip()})"
                    track_event("home_preset_applied", preset_id=p["id"])
                    st.rerun()

with col_tariff:
    st.markdown("##### ⚙️ Tarifa Elétrica")
    st.number_input(
        "Tarifa (R$/kWh):",
        min_value=0.10,
        max_value=3.00,
        step=0.05,
        format="%.2f",
        key="tariff",
    )

st.divider()

# 2. Gerenciamento do Inventário (Visual com Cards rápidos, Adicionar e Exportar/Importar JSON)
tab_inventory, tab_quick_add, tab_custom_add, tab_rooms, tab_share, tab_validate = st.tabs([
    "📋 Inventário Atual",
    "⚡ Adicionar Rápido (Cards)",
    "➕ Personalizado",
    "🚪 Gerenciar Cômodos",
    "💾 Exportar / Compartilhar JSON",
    "🧾 Validar Fatura Real",
])

catalog = load_default_appliances()

with tab_rooms:
    st.markdown("#### 🚪 Gerenciar Cômodos da Casa")
    st.caption("Crie cômodos personalizados (ex: Quarto do Pedro, Suíte, Varanda Gourmet, Garagem) para organizar seus aparelhos.")
    
    col_new_room, col_btn_room = st.columns([3, 1])
    with col_new_room:
        new_room_name = st.text_input("Nome do novo cômodo:", placeholder="Ex: Quarto dos Filhos, Garagem...", key="input_new_room")
    with col_btn_room:
        st.write("")
        st.write("")
        if st.button("➕ Adicionar Cômodo", type="primary", use_container_width=True):
            clean_name = new_room_name.strip()
            if clean_name and clean_name not in st.session_state.rooms:
                st.session_state.rooms.append(clean_name)
                track_event("room_added", room_count=len(st.session_state.rooms))
                st.success(f"Cômodo '{clean_name}' cadastrado com sucesso!")
                st.rerun()
            elif clean_name in st.session_state.rooms:
                st.warning("Este cômodo já está cadastrado.")

    st.markdown("##### Cômodos Ativos:")
    cols_r = st.columns(4)
    room_to_del = None
    for idx, r in enumerate(st.session_state.rooms):
        with cols_r[idx % 4]:
            with st.container(border=True):
                st.markdown(f"**🚪 {r}**")
                # Contar quantos aparelhos estão nesse cômodo
                apps_in_r = [a for a in st.session_state.appliances if a.category == r]
                st.caption(f"{len(apps_in_r)} aparelho(s)")
                if len(st.session_state.rooms) > 1:
                    if st.button(f"Remover cômodo", key=f"del_room_{idx}"):
                        room_to_del = r
    if room_to_del:
        st.session_state.rooms.remove(room_to_del)
        # Aparelhos órfãos voltam para "Geral"
        for a in st.session_state.appliances:
            if a.category == room_to_del:
                a.category = "Geral"
        if "Geral" not in st.session_state.rooms:
            st.session_state.rooms.append("Geral")
        track_event("room_removed", room_count=len(st.session_state.rooms))
        st.rerun()

with tab_quick_add:
    st.markdown("#### ⚡ Adição Visual com 1 Clique")
    st.caption("Selecione o cômodo de destino e clique no botão para adicionar um aparelho padrão instantaneamente ao inventário:")

    # Feedback de adição persistente
    if "quick_add_notification" in st.session_state and st.session_state.quick_add_notification:
        st.success(st.session_state.quick_add_notification)
        if st.button("✖️ Fechar aviso", key="dismiss_notif"):
            st.session_state.quick_add_notification = None
            st.rerun()

    # Seletor de cômodo para onde os cards rápidos vão
    quick_dest_room = st.selectbox("🚪 Adicionar aparelhos ao cômodo:", options=st.session_state.rooms, index=0, key="quick_dest_room")

    q_cols = st.columns(3)
    for idx, c in enumerate(catalog):
        with q_cols[idx % 3]:
            with st.container(border=True):
                # Imagem SVG do aparelho se existir
                svg_path = f"assets/img/appliances/{c.id}.svg"
                try:
                    with open(svg_path, "r", encoding="utf-8") as f:
                        svg_code = f.read()
                    st.markdown(f"<div style='width: 70px; height: 70px; margin: 0 auto 8px auto;'>{svg_code}</div>", unsafe_allow_html=True)
                except Exception:
                    pass

                st.markdown(f"**{c.name}**")
                st.caption(f"Potência: **{c.power_watts:.0f} W** | Uso: **{c.hours_per_day:.1f}h/dia**")
                if st.button(f"➕ Adicionar ao {quick_dest_room}", key=f"quick_add_{c.id}"):
                    st.session_state.appliances.append(
                        Appliance(
                            id=str(uuid.uuid4())[:8],
                            name=c.name,
                            power_watts=c.power_watts,
                            hours_per_day=c.hours_per_day,
                            days_per_month=c.days_per_month,
                            category=quick_dest_room,
                            description=c.description,
                        )
                    )
                    track_event("appliance_added_quick", appliance_id=c.id)
                    st.session_state.quick_add_notification = f"✅ **{c.name}** adicionado com sucesso ao cômodo **{quick_dest_room}**! Total na casa: {len(st.session_state.appliances)} aparelhos."
                    st.rerun()

with tab_custom_add:
    st.markdown("#### Adicionar Aparelho Personalizado com Ajuste Fino")
    c_name, c_room = st.columns(2)
    with c_name:
        new_name = st.text_input("Nome do Aparelho:", value="Novo Eletrodoméstico")
    with c_room:
        new_cat = st.selectbox("Cômodo / Categoria:", options=st.session_state.rooms)

    c_power, c_hours, c_days = st.columns(3)
    with c_power:
        new_power = st.number_input("Potência (Watts):", min_value=1.0, max_value=25000.0, value=150.0, step=10.0)
    with c_hours:
        new_hours = st.slider("Horas por dia:", 0.1, 24.0, 2.0, 0.1, key="custom_h")
    with c_days:
        new_days = st.slider("Dias por mês:", 1, 31, 30, 1, key="custom_d")

    if st.button("➕ Adicionar à Minha Casa", type="primary"):
        new_app = Appliance(
            id=str(uuid.uuid4())[:8],
            name=new_name,
            power_watts=new_power,
            hours_per_day=new_hours,
            days_per_month=new_days,
            category=new_cat,
        )
        st.session_state.appliances.append(new_app)
        st.session_state.active_preset_name = "Personalizado"
        track_event("appliance_added_custom", power_watts=new_power, hours_per_day=new_hours, days_per_month=new_days)
        st.session_state.quick_add_notification = f"✅ **{new_name}** adicionado com sucesso ao cômodo **{new_cat}**!"
        st.success(f"'{new_name}' adicionado com sucesso ao cômodo '{new_cat}'!")
        st.rerun()

with tab_share:
    st.markdown("#### 💾 Compartilhar ou Guardar Casa em JSON")
    st.caption("Como a aplicação roda em modo local, o aluno pode exportar seu inventário em JSON para entregar ao professor ou carregar o JSON de um colega!")

    import json

    export_data = {
        "family_name": st.session_state.get("family_name", "Minha Casa"),
        "tariff": st.session_state.tariff,
        "rooms": st.session_state.rooms,
        "appliances": [
            {
                "id": a.id,
                "name": a.name,
                "power_watts": a.power_watts,
                "hours_per_day": a.hours_per_day,
                "days_per_month": a.days_per_month,
                "category": a.category,
            }
            for a in st.session_state.appliances
        ],
    }
    json_str = json.dumps(export_data, indent=2, ensure_ascii=False)

    col_exp, col_imp = st.columns(2)
    with col_exp:
        st.markdown("##### 📤 Baixar JSON da Residência")
        st.download_button(
            label="💾 Baixar Arquivo casa_aluno.json",
            data=json_str,
            file_name=f"{st.session_state.get('family_name', 'casa').replace(' ', '_').lower()}.json",
            mime="application/json",
            on_click=lambda: track_event("inventory_exported"),
        )
        st.text_area("Pré-visualização do JSON:", json_str, height=160)

    with col_imp:
        st.markdown("##### 📥 Carregar JSON de Outro Aluno / Arquivo")
        uploaded_json = st.file_uploader("Selecione um arquivo .json de inventário:", type=["json"])
        if uploaded_json is not None:
            try:
                loaded = json.load(uploaded_json)
                if st.button("📥 Importar e Substituir Inventário Atual"):
                    st.session_state.family_name = loaded.get("family_name", "Casa Importada")
                    st.session_state.tariff = float(loaded.get("tariff", 0.85))
                    if "rooms" in loaded and isinstance(loaded["rooms"], list):
                        st.session_state.rooms = loaded["rooms"]
                    st.session_state.appliances = [
                        Appliance(
                            id=item.get("id", str(uuid.uuid4())[:8]),
                            name=item["name"],
                            power_watts=float(item["power_watts"]),
                            hours_per_day=float(item["hours_per_day"]),
                            days_per_month=float(item.get("days_per_month", 30.0)),
                            category=item.get("category", "Geral"),
                        )
                        for item in loaded.get("appliances", [])
                    ]
                    track_event("inventory_imported", appliance_count=len(st.session_state.appliances), room_count=len(st.session_state.rooms))
                    st.session_state.quick_add_notification = "🏠 Inventário residencial e cômodos importados com sucesso!"
                    st.success("Casa importada com sucesso!")
                    st.rerun()
            except Exception as e:
                st.error(f"Erro ao ler arquivo JSON: {e}")

with tab_inventory:
    st.markdown(f"#### 🏠 Residência: {st.session_state.get('family_name', 'Minha Residência')}")
    if not st.session_state.appliances:
        st.warning("Nenhum aparelho na residência. Adicione aparelhos nas abas acima ou carregue um preset.")
    else:
        st.markdown(f"**Total de aparelhos cadastrados:** {len(st.session_state.appliances)}")

        # Paleta didática e harmoniosa de cores e ícones por cômodo
        ROOM_THEMES = {
            "Banheiro": {"color": "#06b6d4", "bg": "rgba(6, 182, 212, 0.12)", "icon": "🚿"},
            "Cozinha": {"color": "#f97316", "bg": "rgba(249, 115, 22, 0.12)", "icon": "🍳"},
            "Sala": {"color": "#8b5cf6", "bg": "rgba(139, 92, 246, 0.12)", "icon": "🛋️"},
            "Quarto": {"color": "#ec4899", "bg": "rgba(236, 72, 153, 0.12)", "icon": "🛏️"},
            "Lavanderia": {"color": "#3b82f6", "bg": "rgba(59, 130, 246, 0.12)", "icon": "🧺"},
            "Escritório": {"color": "#10b981", "bg": "rgba(16, 185, 129, 0.12)", "icon": "💼"},
            "Climatização": {"color": "#0284c7", "bg": "rgba(2, 132, 199, 0.12)", "icon": "❄️"},
            "Iluminação": {"color": "#eab308", "bg": "rgba(234, 179, 8, 0.12)", "icon": "💡"},
            "Tecnologia": {"color": "#a855f7", "bg": "rgba(168, 85, 247, 0.12)", "icon": "🖥️"},
        }

        # Agrupamento e ordenação por cômodo e consumo
        # 1. Filtro opcional
        rooms_in_inventory = sorted(list(set([a.category for a in st.session_state.appliances])))
        sel_filter_room = st.selectbox("🔍 Filtrar visualização por Cômodo:", ["Todos os Cômodos"] + rooms_in_inventory)

        # Modal de confirmação de exclusão
        @st.dialog("⚠️ Confirmar Exclusão")
        def confirm_delete_dialog(appliance_to_delete):
            st.write(f"Tem certeza que deseja remover **{appliance_to_delete.name}** do inventário da casa?")
            st.caption(f"Cômodo: {appliance_to_delete.category} • Potência: {appliance_to_delete.power_watts:.0f} W")
            c_yes, c_no = st.columns(2)
            with c_yes:
                if st.button("🗑️ Sim, excluir", type="primary", use_container_width=True):
                    if appliance_to_delete in st.session_state.appliances:
                        st.session_state.appliances.remove(appliance_to_delete)
                    track_event("appliance_deleted", appliance_count=len(st.session_state.appliances))
                    st.session_state.appliance_to_delete_id = None
                    st.rerun()
            with c_no:
                if st.button("Cancelar", use_container_width=True):
                    st.session_state.appliance_to_delete_id = None
                    st.rerun()

        # Modal/Painel de Edição se houver um item sendo editado
        if "editing_appliance_id" in st.session_state and st.session_state.editing_appliance_id is not None:
            edit_id = st.session_state.editing_appliance_id
            target_app = next((a for a in st.session_state.appliances if a.id == edit_id), None)
            if target_app:
                with st.form("form_edit_appliance"):
                    st.markdown(f"### ✏️ Editando: **{target_app.name}**")
                    st.caption("Você pode ter dois aparelhos iguais (ex: TVs ou Chuveiros) com potências, tempos e cômodos totalmente diferentes!")
                    ed_name = st.text_input("Nome do aparelho:", value=target_app.name)
                    ed_room = st.selectbox("Cômodo:", options=st.session_state.rooms, index=st.session_state.rooms.index(target_app.category) if target_app.category in st.session_state.rooms else 0)
                    c_ed1, c_ed2, c_ed3 = st.columns(3)
                    with c_ed1:
                        ed_power = st.number_input("Potência (Watts):", min_value=1.0, max_value=25000.0, value=float(target_app.power_watts), step=10.0)
                    with c_ed2:
                        ed_hours = st.slider("Horas por dia:", 0.1, 24.0, float(target_app.hours_per_day), 0.1)
                    with c_ed3:
                        ed_days = st.slider("Dias por mês:", 1, 31, int(target_app.days_per_month), 1)

                    c_save, c_cancel = st.columns(2)
                    with c_save:
                        if st.form_submit_button("💾 Salvar Alterações", type="primary", use_container_width=True):
                            target_app.name = ed_name
                            target_app.category = ed_room
                            target_app.power_watts = ed_power
                            target_app.hours_per_day = ed_hours
                            target_app.days_per_month = ed_days
                            track_event("appliance_edited", appliance_count=len(st.session_state.appliances))
                            st.session_state.editing_appliance_id = None
                            st.success(f"Aparelho '{ed_name}' atualizado com sucesso!")
                            st.rerun()
                    with c_cancel:
                        if st.form_submit_button("✖️ Cancelar Edição", use_container_width=True):
                            st.session_state.editing_appliance_id = None
                            st.rerun()
                st.divider()

        # Abrir modal de exclusão se solicitado
        if "appliance_to_delete_id" in st.session_state and st.session_state.appliance_to_delete_id is not None:
            del_target = next((a for a in st.session_state.appliances if a.id == st.session_state.appliance_to_delete_id), None)
            if del_target:
                confirm_delete_dialog(del_target)
            else:
                st.session_state.appliance_to_delete_id = None

        # 2. Agrupar aparelhos por cômodo calculando consumo
        room_consumption = {
            room_name: sum(
                (app.power_watts / 1000.0) * app.hours_per_day * app.days_per_month
                for app in st.session_state.appliances
                if app.category == room_name
            )
            for room_name in rooms_in_inventory
        }
        active_rooms = sorted(
            [r for r in rooms_in_inventory if sel_filter_room == "Todos os Cômodos" or r == sel_filter_room],
            key=lambda room_name: room_consumption[room_name],
            reverse=True,
        )

        to_remove = None

        # CSS responsivo e grid para os cards
        st.markdown(
            """
            <style>
            .appliance-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
                gap: 16px;
                margin-top: 10px;
                margin-bottom: 20px;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

        for room_name in active_rooms:
            # Aparelhos pertencentes a este cômodo com índice original preservado
            room_items = [(idx, a) for idx, a in enumerate(st.session_state.appliances) if a.category == room_name]
            if not room_items:
                continue

            # Calcular consumo mensal de cada um para ordenação
            room_items_with_kwh = []
            for orig_idx, app in room_items:
                kwh = (app.power_watts / 1000.0) * app.hours_per_day * app.days_per_month
                room_items_with_kwh.append((orig_idx, app, kwh))

            # Ordenar do MAIOR consumo para o MENOR
            room_items_with_kwh.sort(key=lambda x: x[2], reverse=True)

            room_total_kwh = sum(x[2] for x in room_items_with_kwh)
            room_total_cost = room_total_kwh * st.session_state.tariff

            theme = ROOM_THEMES.get(room_name, {"color": "#64748b", "bg": "rgba(100, 116, 139, 0.12)", "icon": "🚪"})
            r_color = theme["color"]
            r_bg = theme["bg"]
            r_icon = theme["icon"]

            # Bloco Container do Cômodo com borda colorida e cabeçalho informativo
            st.markdown(
                f"""
                <div style="background: rgba(255, 255, 255, 0.02); border-left: 4px solid {r_color}; border-top: 1px solid rgba(255,255,255,0.08); border-right: 1px solid rgba(255,255,255,0.08); border-bottom: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 12px 16px; margin: 18px 0 12px 0;">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            <span style="font-size: 1.3rem;">{r_icon}</span>
                            <span style="font-size: 1.15rem; font-weight: 700; color: #f8fafc;">{room_name}</span>
                            <span style="background: {r_bg}; color: {r_color}; border: 1px solid {r_color}44; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">
                                {len(room_items_with_kwh)} {'aparelho' if len(room_items_with_kwh) == 1 else 'aparelhos'}
                            </span>
                        </div>
                        <div style="font-size: 0.85rem; color: #cbd5e1; font-weight: 500;">
                            Total: <strong style="color: {r_color}; font-size: 0.95rem;">{room_total_kwh:.1f} kWh/mês</strong> 
                            <span style="color: #64748b;">&bull;</span> 
                            <span style="color: #10b981; font-weight: 600;">R$ {room_total_cost:.2f}/mês</span>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Grid de cards: 2 colunas para excelente visualização em desktop e mobile
            grid_cols = st.columns(2)

            for rank, (orig_idx, app, app_kwh) in enumerate(room_items_with_kwh):
                app_cost = app_kwh * st.session_state.tariff

                # Identificar miniatura SVG se existir
                svg_match = None
                for pot_id in ["shower", "air_conditioner", "fridge", "led_tv", "microwave", "washing_machine", "fan", "led_bulb_pack", "iron", "air_fryer"]:
                    if pot_id in app.name.lower() or app.name.lower().startswith(pot_id[:3]):
                        svg_match = pot_id
                        break
                if "pc" in app.name.lower() or "computador" in app.name.lower():
                    svg_match = "hardware/pc_custom"
                elif "chuveiro" in app.name.lower():
                    svg_match = "shower"
                elif "geladeira" in app.name.lower():
                    svg_match = "fridge"
                elif "ar-" in app.name.lower() or "ar condicionado" in app.name.lower():
                    svg_match = "air_conditioner"
                elif "tv" in app.name.lower():
                    svg_match = "led_tv"
                elif "micro" in app.name.lower():
                    svg_match = "microwave"
                elif "lavar" in app.name.lower():
                    svg_match = "washing_machine"
                elif "ventilador" in app.name.lower():
                    svg_match = "fan"
                elif "lâmpada" in app.name.lower() or "led" in app.name.lower():
                    svg_match = "led_bulb_pack"
                elif "ferro" in app.name.lower():
                    svg_match = "iron"
                elif "fryer" in app.name.lower():
                    svg_match = "air_fryer"

                svg_html = ""
                if svg_match:
                    folder = "hardware" if "hardware" in svg_match else "appliances"
                    sname = svg_match.replace("hardware/", "")
                    try:
                        with open(f"assets/img/{folder}/{sname}.svg", "r", encoding="utf-8") as f:
                            svg_html = f"<div style='width: 32px; height: 32px; display: flex; align-items: center; justify-content: center;'>{f.read()}</div>"
                    except Exception:
                        svg_html = "<span style='font-size: 1.3rem;'>⚡</span>"
                else:
                    svg_html = "<span style='font-size: 1.3rem;'>🔌</span>"

                # Badge de maior consumo do cômodo
                top_badge = ""
                if rank == 0 and len(room_items_with_kwh) > 1:
                    top_badge = "<span style='background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); font-size: 0.7rem; padding: 1px 6px; border-radius: 8px; font-weight: 600;'>🔥 Maior do cômodo</span>"

                col_target = grid_cols[rank % 2]

                with col_target:
                    with st.container(border=True):
                        # Topo do card: ícone e título
                        c_card_info = st.container()

                        with c_card_info:
                            info_html = (
                                f"<div style='display: flex; align-items: center; gap: 12px;'>"
                                f"<div style='background: {r_bg}; border: 1px solid {r_color}33; border-radius: 10px; padding: 6px; display: flex; align-items: center; justify-content: center; min-width: 44px; min-height: 44px; flex-shrink: 0;'>"
                                f"{svg_html}"
                                f"</div>"
                                f"<div style='min-width: 0;'>"
                                f"<div style='display: flex; align-items: center; gap: 6px; flex-wrap: wrap;'>"
                                f"<span style='color: #f8fafc; font-size: 1rem; font-weight: 700; word-break: break-word;'>{app.name}</span>"
                                f"{top_badge}"
                                f"</div>"
                                f"<div style='color: #94a3b8; font-size: 0.8rem; display: flex; align-items: center; gap: 6px; flex-wrap: wrap; margin-top: 3px;'>"
                                f"<span>⚡ <strong style='color: #f1f5f9;'>{app.power_watts:.0f} W</strong></span>"
                                f"<span style='color: #475569;'>&bull;</span>"
                                f"<span>⏱️ {app.hours_per_day:.1f} h/d</span>"
                                f"<span style='color: #475569;'>&bull;</span>"
                                f"<span>📅 {app.days_per_month:.0f} d/m</span>"
                                f"</div>"
                                f"</div>"
                                f"</div>"
                            )
                            st.markdown(info_html, unsafe_allow_html=True)

                        # Base do card: consumo, custo e ações
                        c_card_stats, c_card_actions = st.columns([3.5, 0.8], vertical_alignment="bottom")

                        with c_card_stats:
                            stats_html = (
                                f"<div style='margin-top: 10px;'>"
                                f"<div style='color: #38bdf8; font-weight: 800; font-size: 1.05rem; letter-spacing: -0.02em;'>"
                                f"{app_kwh:.1f} kWh/mês"
                                f"</div>"
                                f"<div style='color: #10b981; font-size: 0.88rem; font-weight: 700; margin-top: 1px;'>"
                                f"R$ {app_cost:.2f}/mês"
                                f"</div>"
                                f"</div>"
                            )
                            st.markdown(stats_html, unsafe_allow_html=True)

                        with c_card_actions:
                            with st.popover("⚙️", key=f"config_{app.id}_{orig_idx}", help=f"Configurar {app.name}"):
                                if st.button("✏️ Editar", key=f"config_edit_{app.id}_{orig_idx}", use_container_width=True):
                                    st.session_state.editing_appliance_id = app.id
                                    st.rerun()
                                if st.button("🗑️ Excluir", key=f"config_delete_{app.id}_{orig_idx}", use_container_width=True):
                                    st.session_state.appliance_to_delete_id = app.id
                                    st.rerun()

with tab_validate:
    st.markdown("#### 🧾 Validador de Conta de Luz Real vs Consumo Estimado")
    st.markdown("Descubra por que o valor da sua conta física pode ser diferente do simulador.")

    hh_calc = calculate_total_household_consumption(st.session_state.appliances)
    sim_kwh = hh_calc["total_monthly_kwh"]

    c_bill_val, c_bill_btn = st.columns([1, 1])
    with c_bill_val:
        real_val = st.number_input(
            "Valor Total da sua Última Fatura de Energia (R$):",
            min_value=10.0,
            max_value=5000.0,
            value=max(20.0, float(calculate_cost(sim_kwh, st.session_state.tariff))),
            step=5.0,
        )

    val_res = validate_against_real_bill(sim_kwh, real_val, st.session_state.tariff)
    track_event_on_change(
        "bill_validation_event_signature",
        "real_bill_validated",
        simulated_monthly_kwh=sim_kwh,
        real_bill_reais=real_val,
        verdict=val_res["verdict"],
    )

    st.markdown(
        f"<div style='background: rgba(14, 165, 233, 0.1); border-left: 4px solid #38bdf8; padding: 15px; border-radius: 8px; margin: 15px 0;'>"
        f"<h4 style='margin-top:0; color:#38bdf8;'>Diagnóstico da Comparação:</h4>"
        f"<p>• <strong>Consumo Simulado:</strong> {val_res['simulated_monthly_kwh']:.1f} kWh (~ R$ {val_res['simulated_cost']:.2f})</p>"
        f"<p>• <strong>Consumo Estimado da Fatura Real:</strong> ~ {val_res['inferred_real_kwh']:.1f} kWh (R$ {val_res['real_bill_reais']:.2f})</p>"
        f"<p>• <strong>Diferença Identificada:</strong> {abs(val_res['diff_kwh']):.1f} kWh (R$ {abs(val_res['diff_cost']):.2f})</p>"
        f"<hr style='border-color: rgba(255,255,255,0.1);'/>"
        f"<p style='color: #f8fafc; font-size: 0.95rem;'>💡 {val_res['explanation']}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.divider()

# 3. Resultados Globais da Residência
household = calculate_total_household_consumption(st.session_state.appliances)
tot_kwh = household["total_monthly_kwh"]
tot_daily_kwh = round(tot_kwh / 30.0, 1)
tot_ann_kwh = household["total_annual_kwh"]

tot_cost = calculate_cost(tot_kwh, st.session_state.tariff)
tot_daily_cost = round(tot_cost / 30.0, 2)
tot_ann_cost = calculate_cost(tot_ann_kwh, st.session_state.tariff)

st.markdown("### 📊 Balanço Geral da Residência")
c1, c2, c3 = st.columns(3)
with c1:
    render_metric_card(
        "Consumo da Casa",
        f"{tot_kwh:.1f} kWh",
        f"Diário: {tot_daily_kwh:.1f} kWh • Anual: {tot_ann_kwh:.0f} kWh",
        border_color="#38bdf8",
    )
with c2:
    render_cost_card(
        "Custo Estimado da Fatura",
        monthly_cost=tot_cost,
        daily_cost=tot_daily_cost,
        annual_cost=tot_ann_cost,
        highlight="monthly",
        border_color="#10b981",
        extra_subtext=f"Tarifa: R$ {st.session_state.tariff:.2f}/kWh",
    )
with c3:
    render_metric_card(
        "Aparelhos Cadastrados",
        f"{len(st.session_state.appliances)} itens",
        f"Maior vilão: {household['items'][0]['name'] if household['items'] else 'Nenhum'}",
        border_color="#f59e0b",
    )

# Ranking e Gráficos
col_rank, col_charts = st.columns([1, 1], gap="large")

with col_rank:
    st.markdown("#### 🏆 Ranking dos 'Vilões' de Consumo")
    if household["items"]:
        medals = ["🥇", "🥈", "🥉", "4º", "5º", "6º", "7º", "8º", "9º", "10º"]
        for idx, item in enumerate(household["items"][:10]):
            medal = medals[idx] if idx < len(medals) else f"{idx+1}º"
            item_cost = calculate_cost(item["monthly_kwh"], st.session_state.tariff)
            st.markdown(
                f"<div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;'>"
                f"<div>"
                f"<span style='font-size: 1.2rem; margin-right: 6px;'>{medal}</span>"
                f"<strong>{item['name']}</strong>"
                f"<div style='font-size: 0.8rem; color: #94a3b8; margin-left: 32px;'>{item['category']}</div>"
                f"</div>"
                f"<div style='text-align: right;'>"
                f"<span style='font-weight: 700; color: #38bdf8;'>{item['monthly_kwh']:.1f} kWh</span>"
                f"<span style='font-size: 0.85rem; color: #cbd5e1;'> ({item['percentage']}%)</span>"
                f"<div style='font-size: 0.8rem; color: #10b981;'>R$ {item_cost:.2f}/mês</div>"
                f"</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        st.info("Nenhum aparelho para exibir ranking.")

with col_charts:
    st.markdown("#### 🥧 Distribuição e Comparativo")
    if household["items"]:
        st.plotly_chart(plot_household_distribution_donut(household["items"]), use_container_width=True)
        st.plotly_chart(plot_appliances_bar_chart(household["items"]), use_container_width=True)

render_warning_badge("O ranking é ordenado pelo consumo total mensal (kWh), que depende tanto da potência do equipamento quanto das horas de funcionamento.")

render_did_you_know(
    "Potência alta vs Uso contínuo",
    "Um ferro de passar (1.500 W) usado por 1 hora na semana gasta muito menos no mês que uma geladeira (150 W) ligada todos os dias. O tempo de uso é tão decisivo quanto a potência!",
)
