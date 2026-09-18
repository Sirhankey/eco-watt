"""Página educativa de eficiência energética, conceitos de física e leitura de etiquetas."""
import streamlit as st
from ecowatt.utils.logging import track_event
from ecowatt.utils.session import init_session_state
from ecowatt.components.cards import render_header, render_did_you_know, render_warning_badge

st.set_page_config(page_title="Eficiência Energética — EcoWatt", page_icon="🏷️", layout="wide")
init_session_state()
track_event("page_view", page="efficiency")

render_header(
    title="Entenda a Eficiência Energética",
    subtitle="Aprenda a diferença entre potência e consumo, como ler a etiqueta nacional e como economizar.",
    icon="🏷️",
)

st.markdown(
    "<div style='background: rgba(16, 185, 129, 0.08); border-left: 4px solid #10b981; padding: 20px; border-radius: 10px; margin-bottom: 25px;'>"
    "<h3 style='color: #34d399; margin-top: 0;'>O que é Eficiência Energética?</h3>"
    "<p style='font-size: 1.05rem; line-height: 1.6; color: #cbd5e1; margin-bottom: 0;'>"
    "Eficiência energética é a capacidade de realizar a <strong>mesma quantidade de trabalho útil</strong> "
    "(como iluminar uma sala, resfriar um quarto ou lavar roupas) consumindo a <strong>menor quantidade possível de eletricidade</strong>. "
    "Dois aparelhos podem ter potências iguais ou diferentes, mas aquele que entrega o resultado gastando menos kWh é o mais eficiente."
    "</p>"
    "</div>",
    unsafe_allow_html=True,
)

# 4 Cards Fundamentais
st.markdown("### 📚 Os 4 Conceitos Fundamentais da Energia")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        "<div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 10px; padding: 16px; height: 100%;'>"
        "<div style='font-size: 1.5rem; margin-bottom: 6px;'>💡</div>"
        "<h4 style='color: #38bdf8; margin: 0 0 8px 0;'>Potência (W)</h4>"
        "<p style='font-size: 0.9rem; color: #94a3b8; line-height: 1.4;'>"
        "É a taxa de demanda instantânea de energia quando o aparelho está funcionando. É a 'força' ou capacidade de puxar carga da tomada."
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        "<div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 10px; padding: 16px; height: 100%;'>"
        "<div style='font-size: 1.5rem; margin-bottom: 6px;'>⚡</div>"
        "<h4 style='color: #10b981; margin: 0 0 8px 0;'>Consumo (kWh)</h4>"
        "<p style='font-size: 0.9rem; color: #94a3b8; line-height: 1.4;'>"
        "É a energia total gasta ao longo do tempo. Resulta da multiplicação da potência pelas horas e dias que o aparelho permaneceu ligado."
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        "<div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(245, 158, 11, 0.3); border-radius: 10px; padding: 16px; height: 100%;'>"
        "<div style='font-size: 1.5rem; margin-bottom: 6px;'>💰</div>"
        "<h4 style='color: #f59e0b; margin: 0 0 8px 0;'>Custo (R$)</h4>"
        "<p style='font-size: 0.9rem; color: #94a3b8; line-height: 1.4;'>"
        "É o valor financeiro em reais cobrado pela concessionária, obtido pela multiplicação do consumo em kWh pelo preço da tarifa."
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )

with c4:
    st.markdown(
        "<div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(168, 85, 247, 0.3); border-radius: 10px; padding: 16px; height: 100%;'>"
        "<div style='font-size: 1.5rem; margin-bottom: 6px;'>🌱</div>"
        "<h4 style='color: #a855f7; margin: 0 0 8px 0;'>Eficiência</h4>"
        "<p style='font-size: 0.9rem; color: #94a3b8; line-height: 1.4;'>"
        "É a relação entre o benefício entregue (luz, frio, calor, processamento) e a quantidade de energia gasta no processo."
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )

st.divider()

# Escala visual de eficiência didática
st.markdown("### 🏷️ Como Interpretar as Etiquetas de Eficiência (Selo Procel / Inmetro)")

st.markdown(
    """
    <div style="max-width: 600px; margin: 15px 0;">
        <div style="background: #16a34a; color: white; padding: 10px 16px; border-radius: 6px; margin-bottom: 6px; font-weight: 700; width: 100%;">
            A +++ / A → Máxima Eficiência (Menor Consumo de Energia)
        </div>
        <div style="background: #65a30d; color: white; padding: 10px 16px; border-radius: 6px; margin-bottom: 6px; font-weight: 700; width: 90%;">
            B → Alta Eficiência
        </div>
        <div style="background: #eab308; color: black; padding: 10px 16px; border-radius: 6px; margin-bottom: 6px; font-weight: 700; width: 80%;">
            C → Média Eficiência
        </div>
        <div style="background: #f97316; color: white; padding: 10px 16px; border-radius: 6px; margin-bottom: 6px; font-weight: 700; width: 70%;">
            D → Baixa Eficiência
        </div>
        <div style="background: #dc2626; color: white; padding: 10px 16px; border-radius: 6px; margin-bottom: 6px; font-weight: 700; width: 60%;">
            E → Consumo Elevado (Menor Eficiência)
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

render_warning_badge(
    "A classificação e os critérios da etiqueta podem variar de acordo com a categoria do produto e as regras técnicas aplicáveis por cada país e órgão regulador."
)

st.divider()

# Dicas práticas para a escola e residência
st.markdown("### 💡 5 Hábitos Simples que Reduzem a Conta de Luz")

dicas = [
    ("🚿 Banhos conscientes", "Reduzir o tempo de banho de 15 para 8 minutos poupa até 50% da energia consumida pelo aparelho mais potente da casa."),
    ("❄️ Cuidados com a Geladeira", "Não forre as prateleiras com plásticos, não guarde alimentos fervendo e verifique se a borracha da porta fecha bem."),
    ("💡 Iluminação inteligente", "Aproveite a luz natural do dia e utilize sempre lâmpadas LED, apagando as luzes ao sair de cômodos vazios."),
    ("🔌 Elimine o Consumo Fantasma", "Aparelhos com luzes indicadoras e relógios (micro-ondas, TV, carregadores conectados) consomem energia mesmo desligados. Use réguas com interruptor."),
    ("🖥️ Gerenciamento de Energia no Computador", "Configure o computador para suspender a tela após 10 minutos de inatividade em vez de deixá-la ligada o dia todo."),
]

for icone_titulo, desc in dicas:
    st.markdown(f"**{icone_titulo}**: {desc}")

render_did_you_know(
    "Por que lâmpadas antigas esquentavam tanto?",
    "As lâmpadas incandescentes tradicionais convertiam cerca de 90% da eletricidade em CALOR e apenas 10% em luz visível. Por isso esquentavam tanto e gastavam tanta energia! O LED moderno quase não dissipa calor e foca a energia na emissão de luz.",
)
