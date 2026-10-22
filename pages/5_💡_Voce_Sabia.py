"""Página de curiosidades e dicas educativas sobre energia, alimentada por official_facts."""
import html
import random
import re

import streamlit as st

from ecowatt.components.cards import render_header, render_did_you_know
from ecowatt.services.catalog_repository import load_official_facts
from ecowatt.utils.logging import track_event
from ecowatt.utils.session import init_session_state

st.set_page_config(page_title="Você Sabia? — EcoWatt", page_icon="💡", layout="wide")
init_session_state()
track_event("page_view", page="facts")

render_header(
    title="Você Sabia?",
    subtitle="Curiosidades e dicas para entender melhor o consumo de energia.",
    icon="💡",
)


def _id_sort_key(fact):
    match = re.search(r"(\d+)$", fact["id"])
    return (int(match.group(1)) if match else 10**9, fact["id"])


facts = sorted(load_official_facts(), key=_id_sort_key)
if not facts:
    st.info("Nenhum fato disponível no momento.")
    st.stop()

if "facts_index" not in st.session_state:
    st.session_state.facts_index = random.randrange(len(facts))
current = st.session_state.facts_index % len(facts)

col_prev, col_random, col_next, _ = st.columns([1, 1, 1, 5])
if col_prev.button("◀ Anterior", use_container_width=True):
    st.session_state.facts_index = (current - 1) % len(facts)
    st.rerun()
if col_random.button("🎲 Aleatório", use_container_width=True):
    st.session_state.facts_index = random.randrange(len(facts))
    st.rerun()
if col_next.button("Próximo ▶", use_container_width=True):
    st.session_state.facts_index = (current + 1) % len(facts)
    st.rerun()

featured = facts[current]
render_did_you_know(html.escape(featured["title"]), html.escape(featured["fact"]))
st.caption(f"Fato {current + 1} de {len(facts)}")

st.markdown("### 📚 Todos os fatos")
query = st.text_input("Buscar", placeholder="Ex.: geladeira, LED, kWh").strip().casefold()
matches = [f for f in facts if query in f"{f['title']} {f['fact']}".casefold()]
if not matches:
    st.caption("Nenhum fato encontrado para essa busca.")
for fact in matches:
    with st.expander(fact["title"]):
        st.write(fact["fact"])
