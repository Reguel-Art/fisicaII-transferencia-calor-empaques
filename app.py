"""Herramienta de comparación de empaques térmicos — interfaz web (Streamlit).

Grupo 3 · Física II · Comparación de empaques económicos para bebidas frías.

Ejecutar:
    streamlit run app.py

El motor de cálculo (core/) no se modifica: la interfaz solo
  - sobrescribe el precio de cada empaque con el valor editado en la barra lateral,
  - y evalúa las magnitudes dependientes del tiempo (T, ΔT, Q, k_ef, Q̇, S/ por °C)
    en el tiempo de entrega elegido, usando las mismas funciones de core.
"""

from __future__ import annotations

import io
import math
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core import analisis, costos, datos, fisica

RAIZ = Path(__file__).resolve().parent
CSV_DEFECTO = RAIZ / "data" / "Grupo_3_Datos_Termicos_Web.csv"

# Paleta legible sobre fondo oscuro (control cálido → mejor aislante frío).
COLORES = ["#F25F5C", "#FFB547", "#2EC4B6", "#5DA9F6", "#B794F4", "#F78FB3"]
VERDE = "#3DD68C"

st.set_page_config(
    page_title="Empaques térmicos · Grupo 3",
    page_icon="🧊",
    layout="wide",
)

st.markdown(
    """
    <style>
      .block-container {padding-top: 2.2rem;}
      .kpi-titulo {font-size: .80rem; letter-spacing: .04em; text-transform: uppercase;
                   opacity: .70; margin-bottom: .15rem;}
      .kpi-valor {font-size: 1.30rem; font-weight: 700; line-height: 1.25;
                  margin-bottom: .45rem; min-height: 3.2rem;}
      .kpi-valor small {font-size: .85rem; font-weight: 500; opacity: .75;}
      [data-testid="stSidebar"] [data-testid="stNumberInput"] label p {font-size: .78rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------------------------------- #
# Carga de datos
# --------------------------------------------------------------------------- #
@st.cache_data(show_spinner=False)
def _cargar_defecto() -> pd.DataFrame:
    return datos.cargar_csv(CSV_DEFECTO)


def obtener_datos():
    """Devuelve (df, nombre_fuente) según lo que elija el usuario."""
    st.sidebar.header("1 · Datos")
    subido = st.sidebar.file_uploader(
        "Sube un CSV de mediciones", type=["csv"],
        help="Mismo formato que Grupo_3_Datos_Termicos_Web.csv",
    )
    if subido is not None:
        try:
            df = datos.cargar_csv(subido)
            st.sidebar.success(f"Cargado: {subido.name} ({len(df)} filas)")
            return df, subido.name
        except datos.ErrorDatos as e:
            st.sidebar.error(f"Error en el archivo: {e}")
            st.stop()
    if CSV_DEFECTO.exists():
        st.sidebar.caption("Usando el dataset de ejemplo del Grupo 3.")
        return _cargar_defecto(), CSV_DEFECTO.name
    st.sidebar.warning("Sube un CSV para comenzar.")
    st.stop()


def estado_dataset(df: pd.DataFrame) -> tuple[str, str]:
    """('Simulado' | 'Validado' | 'Sin declarar', color del badge)."""
    if "tipo_dato" not in df.columns:
        return "Sin declarar", "gray"
    tipos = " ".join(df["tipo_dato"].astype(str).unique()).lower()
    if "simula" in tipos:
        return "Simulado", "orange"
    return "Validado", "green"


# --------------------------------------------------------------------------- #
# Controles
# --------------------------------------------------------------------------- #
def _usos_defecto(emp: str) -> int:
    e = emp.lower()
    if "bolsa" in e:
        return 60
    if "eps" in e or "aislante" in e or "tecnopor" in e:
        return 10
    return 1


def panel_controles(df: pd.DataFrame):
    empaques = datos.lista_empaques(df)

    st.sidebar.header("2 · Supuestos de uso")
    st.sidebar.caption("Costo por uso = precio ÷ usos. Todo se recalcula al instante.")
    precios, usos = {}, {}
    for emp in empaques:
        p = datos.params_empaque(df, emp)
        st.sidebar.markdown(f"**{emp}**")
        c1, c2 = st.sidebar.columns(2)
        precios[emp] = c1.number_input(
            "Precio (S/)", min_value=0.0, max_value=10_000.0,
            value=float(p.costo_empaque_pen), step=0.10, format="%.2f",
            key=f"precio_{emp}",
        )
        usos[emp] = c2.number_input(
            "Usos", min_value=1, max_value=1000,
            value=_usos_defecto(emp), step=1, key=f"usos_{emp}",
        )

    st.sidebar.header("3 · Umbral de calidad")
    umbral = st.sidebar.slider(
        "Temperatura objetivo (°C)", min_value=6.0, max_value=16.0,
        value=10.0, step=0.5,
        help="Temperatura máxima aceptable de la bebida al entregarla.",
    )
    t_max_datos = float(df["tiempo_min"].max())
    t_tope = int(min(60, max(5, 5 * math.floor(t_max_datos / 5))))
    t_entrega = st.sidebar.slider(
        "Tiempo de entrega a evaluar (min)", min_value=5, max_value=t_tope,
        value=t_tope, step=5,
        help="Las métricas, la línea vertical del gráfico y las fórmulas "
             "se evalúan en este instante.",
    )
    return precios, usos, umbral, t_entrega


# --------------------------------------------------------------------------- #
# Magnitudes evaluadas en el tiempo de entrega (usa funciones de core)
# --------------------------------------------------------------------------- #
def evaluar_en_tiempo(df: pd.DataFrame, res: pd.DataFrame, t: float) -> pd.DataFrame:
    """Añade a `res` las columnas evaluadas en el instante t (min)."""
    ag = datos.agregar(df)
    t_amb = datos.temperatura_ambiente(df)
    control = analisis._detectar_control(df, datos.lista_empaques(df))
    T_ctrl = datos.temperatura_en_tiempo(ag, control, t) if control else None

    filas = []
    for _, r in res.iterrows():
        emp = r["empaque"]
        p = datos.params_empaque(df, emp)
        T_t = datos.temperatura_en_tiempo(ag, emp, t)
        dT = T_t - r["t0_C"]
        Q = fisica.calor_sensible(p.masa_agua_kg, p.calor_especifico_j_kgk, dT)

        razon = (t_amb - T_t) / (t_amb - r["t0_C"]) if t_amb != r["t0_C"] else np.nan
        k_ef = -math.log(razon) / t if (t > 0 and razon > 0) else np.nan

        r_cond = r["r_cond_KW"]
        qdot_t = (t_amb - T_t) / r_cond if pd.notna(r_cond) and r_cond else np.nan

        spc = (costos.soles_por_grado_evitado(r["costo_por_uso"], T_t, T_ctrl)
               if T_ctrl is not None else float("inf"))
        filas.append(dict(T_t=round(T_t, 2), dT_t=round(dT, 2), Q_t=round(Q, 1),
                          k_ef_t=k_ef, qdot_t=qdot_t,
                          spc_t=(round(spc, 4) if np.isfinite(spc) else spc)))
    return pd.concat([res.reset_index(drop=True), pd.DataFrame(filas)], axis=1)


def ventana_segura(fila: pd.Series, umbral: float) -> float:
    """Minutos que la bebida se mantiene ≤ umbral (modelo ajustado)."""
    if fila["t0_C"] >= umbral:
        return 0.0
    t_u = fila["t_umbral_min"]
    return float("inf") if t_u is None or pd.isna(t_u) else float(t_u)


# --------------------------------------------------------------------------- #
# Tarjetas KPI
# --------------------------------------------------------------------------- #
def tarjeta(col, icono: str, titulo: str, valor: str, badge: str, color: str):
    with col.container(border=True):
        st.markdown(
            f'<div class="kpi-titulo">{icono} {titulo}</div>'
            f'<div class="kpi-valor">{valor}</div>',
            unsafe_allow_html=True,
        )
        st.badge(badge, color=color)


def fila_kpis(df, res, rk, umbral, t):
    c1, c2, c3, c4 = st.columns(4)

    mejor = rk.iloc[0]
    if np.isfinite(mejor["spc_t"]):
        tarjeta(c1, "🏆", "Mejor costo-beneficio", mejor["empaque"],
                f"S/ {mejor['spc_t']:.4f} por °C evitado", "green")
    else:
        tarjeta(c1, "🏆", "Mejor costo-beneficio", "—",
                "Ningún empaque mejora al control", "gray")

    frio = res.loc[res["T_t"].idxmin()]
    tarjeta(c2, "❄️", "Mejor conservación", frio["empaque"],
            f"T = {frio['T_t']:.2f} °C a los {t} min", "blue")

    v = ventana_segura(frio, umbral)
    texto_v = "Sin límite" if not np.isfinite(v) else f"{v:.0f} min"
    cubre = v >= t
    tarjeta(c3, "⏱️", "Ventana térmica segura",
            f"{texto_v} <small>≤ {umbral:.1f} °C · {frio['empaque']}</small>",
            f"{'Cubre' if cubre else 'No cubre'} la entrega de {t} min",
            "green" if cubre else "red")

    estado, color = estado_dataset(df)
    tarjeta(c4, "🌡️", "Temperatura ambiente",
            f"{datos.temperatura_ambiente(df):.1f} °C <small>media del ensayo</small>",
            f"Datos: {estado}", color)


# --------------------------------------------------------------------------- #
# Gráficos
# --------------------------------------------------------------------------- #
def _layout_base(fig: go.Figure, height: int, **kw) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(t=40, b=40, l=10, r=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.08, x=0, bgcolor="rgba(0,0,0,0)"),
        **kw,
    )
    fig.update_xaxes(gridcolor="rgba(160,160,160,0.15)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(160,160,160,0.15)", zeroline=False)
    return fig


def grafico_curvas(df: pd.DataFrame, umbral: float, t_entrega: int) -> go.Figure:
    ag = datos.agregar(df)
    fig = go.Figure()
    y_min, y_max = ag["temp_media"].min(), ag["temp_media"].max()
    t_fin = ag["tiempo_min"].max()

    fig.add_hrect(
        y0=0, y1=umbral, fillcolor=VERDE, opacity=0.08, line_width=0, layer="below",
        annotation_text=f"Zona térmica óptima (≤ {umbral:.1f} °C)",
        annotation_position="inside top left",
        annotation_font=dict(color=VERDE, size=12),
    )
    fig.add_hline(y=umbral, line_dash="dash", line_color=VERDE, opacity=0.7)
    fig.add_vline(x=t_entrega, line_dash="dot", line_color="#C9D1D9", opacity=0.8,
                  annotation_text=f"Entrega · {t_entrega} min",
                  annotation_position="top right",
                  annotation_font=dict(size=11))

    for i, emp in enumerate(datos.lista_empaques(df)):
        sub = ag[ag["empaque"] == emp].sort_values("tiempo_min")
        color = COLORES[i % len(COLORES)]
        fig.add_trace(go.Scatter(
            x=sub["tiempo_min"], y=sub["temp_media"],
            error_y=dict(type="data", array=sub["temp_std"], visible=True,
                         thickness=1, width=3, color=color),
            mode="lines+markers", name=emp,
            line=dict(color=color, width=3, shape="spline", smoothing=0.8),
            marker=dict(size=6),
            hovertemplate="%{y:.2f} °C",
        ))
        ult = sub.iloc[-1]
        fig.add_annotation(
            x=ult["tiempo_min"], y=ult["temp_media"],
            text=f"<b>{ult['temp_media']:.1f} °C</b>", showarrow=False,
            xanchor="left", xshift=8, font=dict(color=color, size=12),
        )

    _layout_base(fig, 500, hovermode="x unified",
                 xaxis_title="Tiempo (min)", yaxis_title="Temperatura del agua (°C)")
    fig.update_layout(margin=dict(r=70))
    fig.update_xaxes(range=[-1, t_fin + 1], dtick=5)
    fig.update_yaxes(range=[max(0, min(y_min, umbral) - 1.5), max(y_max, umbral) + 1.5])
    return fig


def grafico_costo_barras(res: pd.DataFrame) -> go.Figure:
    r = res.sort_values("costo_por_uso")
    idx = {e: i for i, e in enumerate(res["empaque"])}
    fig = go.Figure(go.Bar(
        y=r["empaque"], x=r["costo_por_uso"], orientation="h",
        marker_color=[COLORES[idx[e] % len(COLORES)] for e in r["empaque"]],
        text=[f"S/ {v:.3f}" for v in r["costo_por_uso"]], textposition="outside",
        hovertemplate="%{y}: S/ %{x:.3f} por uso<extra></extra>",
    ))
    _layout_base(fig, 420, title="Costo por uso (precio ÷ usos)",
                 xaxis_title="S/ por uso", yaxis_title="", showlegend=False)
    fig.update_xaxes(range=[0, max(r["costo_por_uso"].max() * 1.3, 0.1)])
    return fig


def grafico_cuadrantes(res: pd.DataFrame, umbral: float, t: int) -> go.Figure:
    x, y = res["costo_por_uso"], res["T_t"]
    mx, my = float(x.mean()), float(y.mean())
    px = max((x.max() - x.min()) * 0.15, 0.05)
    py = max((y.max() - y.min()) * 0.15, 0.5)
    x0, x1 = x.min() - px, x.max() + px
    y0, y1 = y.min() - py, y.max() + 2.2 * py  # aire arriba para las etiquetas

    fig = go.Figure()
    fig.add_shape(type="rect", x0=x0, x1=mx, y0=y0, y1=my, fillcolor=VERDE,
                  opacity=0.10, line_width=0, layer="below")
    fig.add_vline(x=mx, line_dash="dot", line_color="#8B949E",
                  annotation_text=f"costo medio S/ {mx:.2f}",
                  annotation_position="top", annotation_font=dict(size=10))
    fig.add_hline(y=my, line_dash="dot", line_color="#8B949E",
                  annotation_text=f"T media {my:.1f} °C",
                  annotation_position="top right", annotation_font=dict(size=10))
    if y0 < umbral < y.max() + py:
        fig.add_hline(y=umbral, line_dash="dash", line_color=VERDE, opacity=0.6,
                      annotation_text=f"Umbral {umbral:.1f} °C",
                      annotation_position="bottom left",
                      annotation_font=dict(color=VERDE, size=10))

    etiquetas = [
        (x0, y0, "left", "bottom", "✅ Barato y frío", VERDE),
        (x1, y0, "right", "bottom", "Frío pero caro", "#8B949E"),
        (x0, y1, "left", "top", "Barato pero se calienta", "#8B949E"),
        (x1, y1, "right", "top", "❌ Caro y se calienta", "#F25F5C"),
    ]
    for ax_, ay_, xa, ya, txt, col in etiquetas:
        fig.add_annotation(x=ax_, y=ay_, text=txt, showarrow=False, xanchor=xa,
                           yanchor=ya, font=dict(size=11, color=col))

    for i, (_, row) in enumerate(res.iterrows()):
        fig.add_trace(go.Scatter(
            x=[row["costo_por_uso"]], y=[row["T_t"]], mode="markers+text",
            text=[row["empaque"]], textposition="top center",
            marker=dict(size=18, color=COLORES[i % len(COLORES)],
                        line=dict(width=2, color="rgba(255,255,255,0.6)")),
            name=row["empaque"], showlegend=False,
            hovertemplate=(f"<b>{row['empaque']}</b><br>S/ %{{x:.3f}} por uso"
                           f"<br>T = %{{y:.2f}} °C<extra></extra>"),
        ))

    _layout_base(fig, 420, title=f"Cuadrantes: costo por uso vs. T a los {t} min",
                 xaxis_title="Costo por uso (S/)  →  más caro",
                 yaxis_title=f"T a los {t} min (°C)  →  más caliente")
    fig.update_xaxes(range=[x0, x1])
    fig.update_yaxes(range=[y0, y1])
    return fig


# --------------------------------------------------------------------------- #
# Pestaña Física
# --------------------------------------------------------------------------- #
def tarjetas_fisica(df: pd.DataFrame, res: pd.DataFrame, t: int):
    empaques = res["empaque"].tolist()
    emp = st.radio("Empaque", empaques, horizontal=True,
                   index=int(res["T_t"].idxmin()), key="emp_fisica")
    r = res[res["empaque"] == emp].iloc[0]
    p = datos.params_empaque(df, emp)
    t_amb = datos.temperatura_ambiente(df)

    c1, c2, c3 = st.columns(3)
    with c1.container(border=True):
        st.markdown("**🔥 Calor sensible absorbido**")
        st.latex(r"Q = m\,c\,\Delta T")
        st.latex(
            rf"Q = {p.masa_agua_kg:.2f}\cdot{p.calor_especifico_j_kgk:.0f}"
            rf"\cdot({r['T_t']:.2f}-{r['t0_C']:.2f})"
        )
        st.badge(f"Q = {r['Q_t'] / 1000:.2f} kJ a los {t} min", color="orange")

    with c2.container(border=True):
        st.markdown("**📉 Constante de calentamiento efectiva**")
        st.latex(r"k_{\text{ef}} = -\frac{1}{t}\ln\frac{T_a - T(t)}{T_a - T_0}")
        if pd.notna(r["k_ef_t"]):
            st.latex(
                rf"k_{{\text{{ef}}}} = -\tfrac{{1}}{{{t}}}"
                rf"\ln\tfrac{{{t_amb:.2f}-{r['T_t']:.2f}}}{{{t_amb:.2f}-{r['t0_C']:.2f}}}"
            )
            st.badge(f"k_ef = {r['k_ef_t']:.5f} min⁻¹", color="blue")
        else:
            st.caption("No definido: la bebida alcanzó la temperatura ambiente.")
        if pd.notna(r["k_fit_min"]):
            st.caption(f"Ajuste con toda la curva: k = {r['k_fit_min']:.5f} min⁻¹ "
                       f"(R² = {r['r2']:.4f}) · U·A = k·m·c = {r['ua_fit_WK']:.3f} W/K")

    with c3.container(border=True):
        st.markdown("**🧱 Resistencia térmica de la pared**")
        st.latex(r"R = \frac{L}{k\,A} \qquad \dot{Q} = \frac{T_a - T(t)}{R}")
        if pd.notna(r["r_cond_KW"]):
            st.latex(
                rf"R = \tfrac{{{p.espesor_pared_mm / 1000:.3f}}}"
                rf"{{{p.conductividad_k_wmk:.3f}\cdot{p.area_superficial_m2:.2f}}}"
                rf"= {r['r_cond_KW']:.3f}\ \text{{K/W}}"
            )
            st.badge(f"Q̇ = {r['qdot_t']:.2f} W a los {t} min", color="violet")
        else:
            st.caption("Sin pared aislante (espesor 0): la ley de conducción no aplica.")


# --------------------------------------------------------------------------- #
# Tablas / salida
# --------------------------------------------------------------------------- #
def nombres_columnas(t: int) -> dict[str, str]:
    return {
        "puesto": "Puesto", "empaque": "Empaque", "codigo": "Código",
        "t0_C": "T₀ (°C)", "t60_C": "T final (°C)", "delta_T": "ΔT final (°C)",
        "q_absorbido_J": "Q final (J)", "k_fit_min": "k ajustada (1/min)", "r2": "R²",
        "ua_fit_WK": "U·A ajustado (W/K)", "r_cond_KW": "R cond. (K/W)",
        "ua_cond_WK": "U·A cond. (W/K)", "qdot_cond_W": "Q̇ inicial (W)",
        "umbral_C": "Umbral (°C)", "t_umbral_min": "t hasta umbral (min)",
        "costo_empaque": "Precio (S/)", "usos": "Usos",
        "costo_por_uso": "S/ por uso", "soles_por_C_evitado": "S/ por °C evitado (final)",
        "T_t": f"T a {t} min (°C)", "dT_t": f"ΔT a {t} min (°C)",
        "Q_t": f"Q a {t} min (J)", "k_ef_t": f"k_ef a {t} min (1/min)",
        "qdot_t": f"Q̇ a {t} min (W)", "spc_t": f"S/ por °C evitado a {t} min",
    }


def panel_procedencia(df: pd.DataFrame, fuente: str):
    estado, _ = estado_dataset(df)
    with st.expander("ℹ️ Ver estado y procedencia de los datos", expanded=False):
        reps = int(df["repeticion"].nunique())
        tiempos = sorted(df["tiempo_min"].unique())
        st.markdown(
            f"- **Fuente:** `{fuente}` · {len(df)} lecturas\n"
            f"- **Empaques:** {', '.join(datos.lista_empaques(df))}\n"
            f"- **Repeticiones:** {reps} · **Tiempos:** {tiempos[0]:g}–{tiempos[-1]:g} min "
            f"({len(tiempos)} instantes)\n"
            f"- **Estado:** {estado}"
            + (f" (`{', '.join(df['tipo_dato'].astype(str).unique())}`)"
               if "tipo_dato" in df.columns else "")
        )
        if estado == "Simulado":
            st.caption("⚠️ Datos simulados: reemplázalos con mediciones reales "
                       "antes de informar resultados experimentales.")


# --------------------------------------------------------------------------- #
# App
# --------------------------------------------------------------------------- #
def main():
    st.title("🧊 Comparación de empaques térmicos")
    st.caption(
        "Grupo 3 · Física II · Conservación de bebidas frías durante el transporte. "
        "Carga mediciones de temperatura y compara desempeño térmico y costo."
    )

    df, fuente = obtener_datos()
    precios, usos, umbral, t = panel_controles(df)

    # Precio editado en la barra lateral → reemplaza el del CSV (el motor no cambia).
    df_calc = df.copy()
    df_calc["costo_empaque_pen"] = df_calc["empaque"].map(precios)

    res = analisis.analizar(df_calc, usos_por_empaque=usos, umbral_override=umbral)
    res = evaluar_en_tiempo(df_calc, res, t)
    rk = analisis.ranking(res, por="spc_t")
    cols = nombres_columnas(t)

    panel_procedencia(df, fuente)
    fila_kpis(df, res, rk, umbral, t)

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Curvas", "💰 Costos", "🏆 Ranking", "🔬 Física"])

    with tab1:
        st.plotly_chart(grafico_curvas(df, umbral, t), width="stretch")
        st.caption(
            "Media ± desviación estándar entre repeticiones. Franja verde: zona "
            "por debajo del umbral de calidad. Línea punteada vertical: tiempo de entrega."
        )

    with tab2:
        ca, cb = st.columns([2, 3])
        with ca:
            st.plotly_chart(grafico_costo_barras(res), width="stretch")
        with cb:
            st.plotly_chart(grafico_cuadrantes(res, umbral, t), width="stretch")
        st.caption(
            "Las líneas punteadas marcan el promedio de costo y de temperatura. "
            "El cuadrante verde (abajo-izquierda) reúne lo barato y que conserva frío."
        )

    with tab3:
        st.subheader(f"Ranking por S/ por °C evitado a los {t} min")
        vista = ["puesto", "empaque", "T_t", "t_umbral_min", "costo_empaque",
                 "usos", "costo_por_uso", "spc_t"]
        # inf (el control no evita grados) se muestra como celda vacía.
        st.dataframe(rk[vista].replace([np.inf], np.nan).rename(columns=cols),
                     width="stretch", hide_index=True)

        csv_buf = io.StringIO()
        rk.rename(columns=cols).to_csv(csv_buf, index=False)
        st.download_button(
            "⬇️ Descargar ranking completo (CSV)", data=csv_buf.getvalue(),
            file_name=f"ranking_empaques_{t}min.csv", mime="text/csv",
        )

    with tab4:
        st.subheader(f"Fórmulas aplicadas a los {t} min")
        tarjetas_fisica(df_calc, res, t)
        st.markdown("##### Resultados físicos por empaque")
        cols_fis = ["empaque", "T_t", "dT_t", "Q_t", "k_ef_t", "k_fit_min", "r2",
                    "ua_fit_WK", "r_cond_KW", "ua_cond_WK", "qdot_t"]
        st.dataframe(res[cols_fis].rename(columns=cols), width="stretch", hide_index=True)
        st.info(
            "**U·A ajustado vs. U·A conductivo.** El ajustado (desde el calentamiento "
            "real, k·m·c) suele ser mayor que el conductivo (solo pared, 1/R = k·A/L) "
            "porque incluye convección y la propia botella. Es la evidencia numérica "
            "de que **U no equivale a la conductividad k del material**."
        )

    st.divider()
    st.caption(f"Fuente de datos: {fuente}  ·  {len(df)} lecturas  ·  "
               "Núcleo de cálculo verificado con 23 pruebas.")


if __name__ == "__main__":
    main()
