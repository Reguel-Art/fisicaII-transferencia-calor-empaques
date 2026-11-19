"""Gráficos Plotly con la estética clara de TermoPack."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from core import datos
from ui.estilo import AZUL, BORDE, NARANJA, NARANJA_OSC, TENUE, TEXTO

# Colores de serie con contraste ≥ 3:1 sobre blanco (WCAG 1.4.11): el naranja de la
# serie es una versión más profunda del naranja de marca.
GRIS_CTRL = "#868C93"
# Validada con la guía de visualización (validate_palette.js): banda de luminosidad,
# croma y separación para daltonismo (ΔE ≥ 18.7 entre vecinos). El gris del control
# es intencional: es la referencia y va siempre con línea discontinua.
PALETA = ["#D2691E", "#2E9FB5", "#3B5BC4", "#8E6CC2", "#D2667A", "#5E9E4A"]


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


def _cruce(x: np.ndarray, y: np.ndarray, umbral: float) -> float | None:
    """Primer instante en que la curva supera el umbral (interpolación lineal)."""
    for k in range(1, len(x)):
        if y[k - 1] <= umbral < y[k]:
            return float(x[k - 1] + (umbral - y[k - 1]) * (x[k] - x[k - 1]) / (y[k] - y[k - 1]))
    return None


def curvas(df: pd.DataFrame, control: str | None, umbral: float, t_entrega: int,
           modo: str = "Temperatura", bandas: bool = True, reco: str | None = None,
           res: pd.DataFrame | None = None, modelo: bool = False) -> go.Figure:
    """Evolución de la temperatura (o de ΔT = T − T₀) por empaque.

    - Zonas: por debajo del límite (azul muy suave) y por encima (naranja muy suave).
    - Un rombo marca el minuto en que cada empaque cruza el límite.
    - Etiqueta directa con el valor final al extremo de cada curva.
    - La alternativa recomendada se dibuja más gruesa; el control, gris y discontinuo.
    - Opcional: la curva del modelo de Newton ajustado, T(t) = Tₐ + (T₀ − Tₐ)·e^(−k·t).
    """
    ag = datos.agregar(df)
    empaques = datos.lista_empaques(df)
    col = colores(empaques, control)
    variacion = modo != "Temperatura"
    t_fin = float(ag["tiempo_min"].max())
    t_amb = datos.temperatura_ambiente(df)
    fig = go.Figure()

    y_todos = (ag["temp_media"] - ag.groupby("empaque")["temp_media"].transform("first")
               if variacion else ag["temp_media"])
    y_lo = float((y_todos - ag["temp_std"]).min())
    y_hi = float((y_todos + ag["temp_std"]).max())
    if not variacion:
        y_lo, y_hi = min(y_lo, umbral), max(y_hi, umbral)
    pad = (y_hi - y_lo) * 0.08
    y0, y1 = y_lo - pad, y_hi + pad

    # Zonas respecto del límite (solo en temperatura).
    if not variacion:
        fig.add_hrect(y0=y0, y1=umbral, fillcolor=AZUL, opacity=0.045, line_width=0, layer="below")
        fig.add_hrect(y0=umbral, y1=y1, fillcolor=NARANJA, opacity=0.06, line_width=0, layer="below")
        fig.add_annotation(xref="paper", x=0.005, y=umbral, yanchor="bottom", xanchor="left",
                           text=f"<b>Límite · {umbral:.1f} °C</b>", showarrow=False,
                           font=dict(color=NARANJA_OSC, size=11))
        fig.add_annotation(xref="paper", x=0.005, y=y1, yanchor="top", xanchor="left",
                           text="Sobre el límite", showarrow=False, font=dict(color=TENUE, size=10))
        fig.add_annotation(xref="paper", x=0.005, y=y0, yanchor="bottom", xanchor="left",
                           text="Dentro del límite", showarrow=False, font=dict(color=TENUE, size=10))

    finales = []
    for emp in empaques:
        sub = ag[ag["empaque"] == emp].sort_values("tiempo_min")
        x = sub["tiempo_min"].to_numpy(float)
        base = float(sub["temp_media"].iloc[0]) if variacion else 0.0
        y = sub["temp_media"].to_numpy(float) - base
        sd = sub["temp_std"].to_numpy(float)
        c = col[emp]
        es_ctrl, destacado = emp == control, emp == reco
        if bandas:
            fig.add_trace(go.Scatter(x=x, y=y + sd, mode="lines", line=dict(width=0, shape="spline"),
                                     showlegend=False, hoverinfo="skip", legendgroup=emp))
            fig.add_trace(go.Scatter(x=x, y=y - sd, mode="lines", line=dict(width=0, shape="spline"),
                                     fill="tonexty", fillcolor=_rgba(c, 0.13), showlegend=False,
                                     hoverinfo="skip", legendgroup=emp))
        if modelo and res is not None and not variacion:
            r = res.set_index("empaque")
            if emp in r.index and pd.notna(r.loc[emp, "k_fit_min"]):
                tt = np.linspace(0, t_fin, 121)
                T0 = float(r.loc[emp, "t0_C"])
                ym = t_amb + (T0 - t_amb) * np.exp(-float(r.loc[emp, "k_fit_min"]) * tt)
                fig.add_trace(go.Scatter(x=tt, y=ym, mode="lines", legendgroup=emp,
                                         line=dict(color=c, width=1.4, dash="dot"),
                                         opacity=0.85, showlegend=False, hoverinfo="skip"))
        nombre = emp + (" · recomendado" if destacado else "")
        fig.add_trace(go.Scatter(
            x=x, y=y, name=nombre, legendgroup=emp, mode="lines+markers",
            line=dict(color=c, width=3.2 if destacado else 2.2, shape="spline", smoothing=0.6,
                      dash="dash" if es_ctrl else "solid"),
            marker=dict(size=9 if destacado else 8, color="#fff", line=dict(color=c, width=2)),
            customdata=np.stack([sd, sub["temp_media"].to_numpy(float)], axis=1),
            hovertemplate=(f"{emp}: <b>%{{y:.2f}} °C</b> ± %{{customdata[0]:.2f}}<extra></extra>"
                           if not variacion else
                           f"{emp}: <b>+%{{y:.2f}} °C</b> (T = %{{customdata[1]:.2f}} °C)<extra></extra>"),
        ))
        finales.append((y[-1], c, emp))

        # Minuto en que cruza el límite.
        if not variacion:
            tc = _cruce(x, y, umbral)
            if tc is not None:
                fig.add_trace(go.Scatter(
                    x=[tc], y=[umbral], mode="markers", legendgroup=emp, showlegend=False,
                    marker=dict(symbol="diamond", size=11, color=c, line=dict(color="#fff", width=2)),
                    hovertemplate=f"{emp} supera {umbral:.1f} °C a los <b>{tc:.0f} min</b><extra></extra>"))

    # Etiquetas directas con el valor final; se separan si quedan muy juntas.
    finales.sort()
    min_sep = (y1 - y0) * 0.055
    ult = -1e9
    for yv, c, emp in finales:
        ypos = max(yv, ult + min_sep)
        ult = ypos
        fig.add_annotation(x=t_fin, y=ypos, xanchor="left", xshift=7, showarrow=False,
                           text=f"<b>{'+' if variacion else ''}{yv:.1f}°</b>",
                           font=dict(color=TEXTO, size=11), bgcolor="rgba(255,255,255,0.9)",
                           bordercolor=c, borderwidth=1.5, borderpad=2)

    if t_entrega < t_fin:
        fig.add_vline(x=t_entrega, line_dash="dot", line_color="#9AA6BE",
                      annotation_text=f"Entrega · {t_entrega} min", annotation_position="top",
                      annotation_font=dict(size=11, color=TENUE))

    _base(fig, 470, hovermode="x unified",
          xaxis_title="Tiempo (min)",
          yaxis_title="Variación ΔT (°C)" if variacion else "Temperatura del agua (°C)")
    fig.update_layout(margin=dict(t=24, b=40, l=6, r=56),
                      legend=dict(orientation="h", y=-0.16, x=0, yanchor="top", font=dict(size=11)),
                      hoverlabel=dict(bgcolor="#fff", bordercolor=BORDE, font_size=12))
    fig.update_xaxes(dtick=10, range=[-1, t_fin + 1], showspikes=True,
                     spikemode="across", spikethickness=1, spikedash="dot", spikecolor="#9AA6BE")
    fig.update_yaxes(range=[y0, y1])
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
        text=[f"S/ {v:.2f}" for v in r["costo_uso"]], textposition="auto", cliponaxis=False,
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
                      annotation_text=f"Límite {umbral:.1f} °C", annotation_position="bottom right",
                      annotation_font=dict(color=NARANJA_OSC, size=11))
    for ax_, ay_, xa, ya, txt in [(x0, y0, "left", "bottom", "Barato y frío ✓"),
                                  (x1, y1, "right", "top", "Caro y se calienta")]:
        fig.add_annotation(x=ax_, y=ay_, text=txt, showarrow=False, xanchor=xa, yanchor=ya,
                           font=dict(size=11, color=AZUL if "✓" in txt else "#9A3B2B"))
    for _, row in r.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["costo_uso"]], y=[row["T_t"]], mode="markers+text",
            text=[row["empaque"]], cliponaxis=False,
            textposition="top right" if row["costo_uso"] <= mx else "top left",
            marker=dict(size=16, color=col[row["empaque"]], line=dict(width=2, color="#fff")),
            showlegend=False,
            hovertemplate=(f"<b>{row['empaque']}</b><br>S/ %{{x:.3f}} por uso"
                           f"<br>T = %{{y:.2f}} °C<extra></extra>"),
        ))
    _base(fig, 340, xaxis_title="Costo por uso (S/)", yaxis_title=f"T a los {t} min (°C)")
    fig.update_layout(margin=dict(t=30, b=40, l=10, r=48))   # aire para los nombres largos
    fig.update_xaxes(range=[x0, x1])
    fig.update_yaxes(range=[y0, y1])
    return fig
