"""Interactive Plotly charts for consumption and financial visualization."""
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any


def plot_appliances_bar_chart(items: List[Dict[str, Any]], title: str = "Consumo Mensal por Aparelho (kWh)"):
    """Creates a horizontal or vertical bar chart comparing appliance consumption."""
    if not items:
        fig = go.Figure()
        fig.update_layout(title="Nenhum aparelho adicionado ainda.")
        return fig

    names = [i["name"] for i in items]
    kwhs = [i["monthly_kwh"] for i in items]

    fig = px.bar(
        x=kwhs,
        y=names,
        orientation="h",
        labels={"x": "Consumo Mensal (kWh)", "y": "Aparelho"},
        title=title,
        color=kwhs,
        color_continuous_scale="Viridis",
        text=kwhs,
    )
    fig.update_traces(texttemplate="%{text:.1f} kWh", textposition="outside")
    fig.update_layout(
        showlegend=False,
        yaxis=dict(autorange="reversed"),
        margin=dict(l=20, r=40, t=50, b=30),
        height=max(320, len(items) * 38),
    )
    return fig


def plot_household_distribution_donut(items: List[Dict[str, Any]], title: str = "Distribuição do Consumo da Residência"):
    """Creates a donut pie chart showing proportional consumption by appliance."""
    if not items:
        fig = go.Figure()
        fig.update_layout(title="Nenhum aparelho adicionado.")
        return fig

    names = [i["name"] for i in items]
    values = [i["monthly_kwh"] for i in items]

    fig = px.pie(
        names=names,
        values=values,
        hole=0.45,
        title=title,
        color_discrete_sequence=px.colors.qualitative.Prism,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=380,
    )
    return fig


def plot_cost_evolution_timeline(daily_cost: float, monthly_cost: float, annual_cost: float):
    """Creates a bar chart illustrating cumulative financial cost over time periods."""
    periods = ["1 Dia", "1 Semana (7d)", "1 Mês (30d)", "1 Ano (365d)"]
    weekly_cost = round(daily_cost * 7.0, 2)
    costs = [daily_cost, weekly_cost, monthly_cost, annual_cost]

    fig = px.bar(
        x=periods,
        y=costs,
        labels={"x": "Período", "y": "Custo Estimado (R$)"},
        title="Projeção Acumulada de Custo ao Longo do Tempo",
        color=costs,
        color_continuous_scale="Tealgrn",
        text=costs,
    )
    fig.update_traces(texttemplate="R$ %{text:.2f}", textposition="outside")
    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=30),
        height=340,
    )
    return fig


def plot_comparison_bar_chart(name_a: str, kwh_a: float, name_b: str, kwh_b: float):
    """Creates a clear side-by-side comparison bar chart for two appliances."""
    fig = go.Figure(
        data=[
            go.Bar(
                name=name_a,
                x=[name_a],
                y=[kwh_a],
                text=[f"{kwh_a:.1f} kWh"],
                textposition="auto",
                marker_color="#38bdf8",
            ),
            go.Bar(
                name=name_b,
                x=[name_b],
                y=[kwh_b],
                text=[f"{kwh_b:.1f} kWh"],
                textposition="auto",
                marker_color="#f59e0b",
            ),
        ]
    )
    fig.update_layout(
        title="Comparativo de Consumo Mensal (kWh)",
        yaxis_title="kWh / mês",
        margin=dict(l=20, r=20, t=50, b=30),
        height=320,
        showlegend=False,
    )
    return fig
