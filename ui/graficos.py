"""Gráficos Plotly con la estética clara de TermoPack."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from core import datos
from ui.estilo import AZUL, BORDE, NARANJA, NARANJA_OSC, TENUE, TEXTO

# Colores de serie con contraste ≥ 3:1 sobre blanco (WCAG 1.4.11): el naranja de la
# serie es una versión más profunda del naranja de marca.
GRIS_CTRL = "#868C93"
PALETA = ["#D06A16", "#5B8DEF", AZUL, "#8E6CC2", "#D2667A", "#2E8C99"]


def colores(empaques: list[str], control: str | None) -> dict[str, str]:
    out, i = {}, 0
    for e in empaques:
        if e == control:
            out[e] = GRIS_CTRL
        else:
            out[e] = PALETA[i % len(PALETA)]
            i += 1
    return out


def _rgba(hex_color: str, a: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{a})"


def _base(fig: go.Figure, height: int, **kw) -> go.Figure:
    fig.update_layout(
        template="plotly_white", height=height,
        font=dict(family="Manrope, sans-serif", color=TEXTO, size=12),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=30, b=40, l=10, r=20),
        legend=dict(orientation="h", y=-0.18, x=0, font=dict(size=11)),
        hoverlabel=dict(font_family="Manrope"),
        **kw,
    )
    fig.update_xaxes(gridcolor="#EDF0F6", zeroline=False, linecolor=BORDE)
    fig.update_yaxes(gridcolor="#EDF0F6", griddash="dash", zeroline=False)
    return fig


def curvas(df: pd.DataFrame, control: str | None, umbral: float, t_entrega: int,
           modo: str = "Temperatura", bandas: bool = True) -> go.Figure:
    """modo: 'Temperatura' (T media) o 'Variación térmica' (T − T₀)."""
    ag = datos.agregar(df)
    empaques = datos.lista_empaques(df)
    col = colores(empaques, control)
    fig = go.Figure()
    variacion = modo != "Temperatura"
    t_fin = ag["tiempo_min"].max()

    for emp in empaques:
        sub = ag[ag["empaque"] == emp].sort_values("tiempo_min")
        y = sub["temp_media"] - (sub["temp_media"].iloc[0] if variacion else 0)
        c = col[emp]
        if bandas:
            fig.add_trace(go.Scatter(x=sub["tiempo_min"], y=y + sub["temp_std"], mode="lines",
                                     line=dict(width=0, shape="spline"), showlegend=False,
                                     hoverinfo="skip"))
            fig.add_trace(go.Scatter(x=sub["tiempo_min"], y=y - sub["temp_std"], mode="lines",
                                     line=dict(width=0, shape="spline"), fill="tonexty",
                                     fillcolor=_rgba(c, 0.15), showlegend=False, hoverinfo="skip"))
        fig.add_trace(go.Scatter(
            x=sub["tiempo_min"], y=y, name=emp, mode="lines+markers",
            line=dict(color=c, width=2.6, shape="spline", smoothing=0.7,
                      dash="dash" if emp == control else "solid"),
            marker=dict(size=7, color="#fff", line=dict(color=c, width=2)),
            hovertemplate="%{y:.2f} °C",
        ))

    if not variacion:
        fig.add_hline(y=umbral, line_dash="dash", line_color=NARANJA, line_width=1.2,
                      annotation_text=f"Límite · {umbral:.1f} °C",
                      annotation_position="bottom right",
                      annotation_font=dict(color=NARANJA_OSC, size=12),
                      annotation_bgcolor="#FEF2E7")
    if t_entrega < t_fin:
        fig.add_vline(x=t_entrega, line_dash="dot", line_color="#9AA6BE",
                      annotation_text=f"Entrega · {t_entrega} min",
                      annotation_position="top", annotation_font=dict(size=11, color=TENUE))

    _base(fig, 460, hovermode="x unified",
          xaxis_title="Tiempo (min)",
          yaxis_title="Variación ΔT (°C)" if variacion else "Temperatura (°C)")
    fig.update_xaxes(dtick=5, range=[-1, t_fin + 1])
    return fig


def _orden(res: pd.DataFrame) -> list[str]:
    """Empaques en el orden de los datos (para que cada uno conserve su color)."""
    return res.sort_values("orden")["empaque"].tolist() if "orden" in res else res["empaque"].tolist()


def costo_barras(res: pd.DataFrame, control: str | None) -> go.Figure:
    r = res[~res["es_control"]].sort_values("costo_uso")
    col = colores(_orden(res), control)
    fig = go.Figure(go.Bar(
        y=r["empaque"], x=r["costo_uso"], orientation="h",
        marker=dict(color=[col[e] for e in r["empaque"]], cornerradius=6),
        text=[f"S/ {v:.2f}" for v in r["costo_uso"]], textposition="outside",
        hovertemplate="%{y}: S/ %{x:.3f} por uso<extra></extra>",
    ))
    _base(fig, 340, showlegend=False, xaxis_title="S/ por uso")
    fig.update_xaxes(range=[0, max(float(r["costo_uso"].max() or 0) * 1.35, 0.1)])
    return fig


def cuadrantes(res: pd.DataFrame, control: str | None, umbral: float, t: int) -> go.Figure:
    r = res[~res["es_control"] & res["T_t"].notna()]
    col = colores(_orden(res), control)
    if r.empty:
        return _base(go.Figure(), 340, xaxis_title="Costo por uso (S/)")
    x, y = r["costo_uso"], r["T_t"]
    mx, my = float(x.mean()), float(y.mean())
    px = max((x.max() - x.min()) * 0.35, 0.1)
    py = max((y.max() - y.min()) * 0.2, 0.5)
    x0, x1, y0, y1 = x.min() - px, x.max() + px, y.min() - py, y.max() + 2 * py

    fig = go.Figure()
    fig.add_shape(type="rect", x0=x0, x1=mx, y0=y0, y1=my, fillcolor="#E3EBF9",
                  opacity=0.6, line_width=0, layer="below")
    fig.add_vline(x=mx, line_dash="dot", line_color="#B8C2D6")
    fig.add_hline(y=my, line_dash="dot", line_color="#B8C2D6")
    if y0 < umbral < y1:
        fig.add_hline(y=umbral, line_dash="dash", line_color=NARANJA,
                      annotation_text=f"Límite {umbral:.1f} °C", annotation_position="bottom left",
                      annotation_font=dict(color=NARANJA_OSC, size=11))
    for ax_, ay_, xa, ya, txt in [(x0, y0, "left", "bottom", "Barato y frío ✓"),
                                  (x1, y1, "right", "top", "Caro y se calienta")]:
        fig.add_annotation(x=ax_, y=ay_, text=txt, showarrow=False, xanchor=xa, yanchor=ya,
                           font=dict(size=11, color=AZUL if "✓" in txt else "#9A3B2B"))
    for _, row in r.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["costo_uso"]], y=[row["T_t"]], mode="markers+text",
            text=[row["empaque"]], textposition="top center",
            marker=dict(size=16, color=col[row["empaque"]], line=dict(width=2, color="#fff")),
            showlegend=False,
            hovertemplate=(f"<b>{row['empaque']}</b><br>S/ %{{x:.3f}} por uso"
                           f"<br>T = %{{y:.2f}} °C<extra></extra>"),
        ))
    _base(fig, 340, xaxis_title="Costo por uso (S/)", yaxis_title=f"T a los {t} min (°C)")
    fig.update_xaxes(range=[x0, x1])
    fig.update_yaxes(range=[y0, y1])
    return fig
