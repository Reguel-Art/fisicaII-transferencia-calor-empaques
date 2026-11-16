"""Herramienta de comparación de empaques térmicos — interfaz web (Streamlit).

Grupo 3 · Física II · Comparación de empaques económicos para bebidas frías.

Ejecutar:
    streamlit run app.py
"""

from __future__ import annotations

import io
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core import analisis, datos

RAIZ = Path(__file__).resolve().parent
CSV_DEFECTO = RAIZ / "Grupo_3_Datos_Termicos_Web.csv"

COLORES = ["#E4572E", "#F3A712", "#4C9F70", "#2E86AB", "#8367C7", "#B33771"]

st.set_page_config(
    page_title="Empaques térmicos · Grupo 3",
    page_icon="🧊",
    layout="wide",
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
        st.sidebar.info("Usando el dataset de ejemplo del Grupo 3.")
        return _cargar_defecto(), CSV_DEFECTO.name
    st.sidebar.warning("Sube un CSV para comenzar.")
    st.stop()


# --------------------------------------------------------------------------- #
# Controles
# --------------------------------------------------------------------------- #
def panel_controles(df: pd.DataFrame):
    empaques = datos.lista_empaques(df)

    st.sidebar.header("2 · Supuestos de uso")
    st.sidebar.caption(
        "Número de usos por empaque. Define el costo por uso (precio ÷ usos)."
    )
    usos = {}
    for emp in empaques:
        p = datos.params_empaque(df, emp)
        # Reutilizables arrancan con un supuesto mayor; desechables en 1.
        defecto = 60 if "bolsa" in emp.lower() else (10 if "eps" in emp.lower() or "aislante" in emp.lower() else 1)
        usos[emp] = st.sidebar.number_input(
            f"{emp}  (S/ {p.costo_empaque_pen:.2f})",
            min_value=1, max_value=1000, value=defecto, step=1, key=f"usos_{emp}",
        )

    st.sidebar.header("3 · Umbral de calidad")
    umbral = st.sidebar.slider(
        "Temperatura objetivo (°C)", min_value=6.0, max_value=16.0,
        value=10.0, step=0.5,
        help="Temperatura máxima aceptable de la bebida.",
    )
    return usos, umbral


# --------------------------------------------------------------------------- #
# Gráficos
# --------------------------------------------------------------------------- #
def grafico_curvas(df: pd.DataFrame, umbral: float) -> go.Figure:
    ag = datos.agregar(df)
    fig = go.Figure()
    for i, emp in enumerate(datos.lista_empaques(df)):
        sub = ag[ag["empaque"] == emp].sort_values("tiempo_min")
        fig.add_trace(
            go.Scatter(
                x=sub["tiempo_min"], y=sub["temp_media"],
                error_y=dict(type="data", array=sub["temp_std"], visible=True, thickness=1),
                mode="lines+markers", name=emp,
                line=dict(color=COLORES[i % len(COLORES)], width=2.5),
                marker=dict(size=6),
            )
        )
    fig.add_hline(
        y=umbral, line_dash="dash", line_color="gray",
        annotation_text=f"Umbral {umbral:.1f} °C", annotation_position="top left",
    )
    fig.update_layout(
        title="Evolución de la temperatura (media ± desviación)",
        xaxis_title="Tiempo (min)", yaxis_title="Temperatura del agua (°C)",
        hovermode="x unified", height=460, legend=dict(orientation="h", y=-0.2),
        margin=dict(t=50, b=40),
    )
    return fig


def grafico_costo_barras(res: pd.DataFrame) -> go.Figure:
    r = res.sort_values("costo_por_uso")
    fig = go.Figure(
        go.Bar(
            x=r["empaque"], y=r["costo_por_uso"],
            marker_color=COLORES[: len(r)],
            text=[f"S/ {v:.3f}" for v in r["costo_por_uso"]],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Costo por uso", xaxis_title="", yaxis_title="S/ por uso",
        height=400, margin=dict(t=50, b=40),
    )
    return fig


def grafico_costo_vs_t60(res: pd.DataFrame, umbral: float) -> go.Figure:
    fig = go.Figure()
    for i, (_, row) in enumerate(res.iterrows()):
        fig.add_trace(
            go.Scatter(
                x=[row["t60_C"]], y=[row["costo_por_uso"]],
                mode="markers+text", text=[row["empaque"]], textposition="top center",
                marker=dict(size=16, color=COLORES[i % len(COLORES)]),
                name=row["empaque"], showlegend=False,
            )
        )
    fig.add_vline(
        x=umbral, line_dash="dash", line_color="gray",
        annotation_text=f"Umbral {umbral:.1f} °C",
    )
    fig.update_layout(
        title="Costo por uso vs. Temperatura a los 60 min",
        xaxis_title="T₆₀ (°C)  —  izquierda = conserva mejor",
        yaxis_title="S/ por uso  —  abajo = más barato",
        height=440, margin=dict(t=50, b=40),
    )
    return fig


# --------------------------------------------------------------------------- #
# Tablas / salida
# --------------------------------------------------------------------------- #
COLS_ES = {
    "puesto": "Puesto", "empaque": "Empaque", "codigo": "Código",
    "t0_C": "T₀ (°C)", "t60_C": "T₆₀ (°C)", "delta_T": "ΔT (°C)",
    "q_absorbido_J": "Q (J)", "k_fit_min": "k (1/min)", "r2": "R²",
    "ua_fit_WK": "U·A ajustado (W/K)", "r_cond_KW": "R cond. (K/W)",
    "ua_cond_WK": "U·A cond. (W/K)", "qdot_cond_W": "Q̇ (W)",
    "umbral_C": "Umbral (°C)", "t_umbral_min": "t a umbral (min)",
    "costo_empaque": "Precio (S/)", "usos": "Usos",
    "costo_por_uso": "S/ por uso", "soles_por_C_evitado": "S/ por °C evitado",
}


def tabla_es(df: pd.DataFrame) -> pd.DataFrame:
    return df.rename(columns=COLS_ES)


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
    usos, umbral = panel_controles(df)

    # Aviso de origen de los datos.
    if "tipo_dato" in df.columns:
        tipos = ", ".join(sorted(df["tipo_dato"].astype(str).unique()))
        if "simula" in tipos.lower():
            st.warning(
                f"⚠️ Datos de origen **simulado** ({tipos}). "
                "Reemplázalos con mediciones reales antes de informar resultados experimentales."
            )

    res = analisis.analizar(df, usos_por_empaque=usos, umbral_override=umbral)

    # --- Métricas destacadas (mejor opción por eficiencia) ---
    rk = analisis.ranking(res, por="soles_por_C_evitado")
    mejor = rk.iloc[0]
    mas_frio = res.loc[res["t60_C"].idxmin()]
    c1, c2, c3 = st.columns(3)
    c1.metric("Mejor costo-beneficio", mejor["empaque"],
              f"S/ {mejor['soles_por_C_evitado']:.4f} por °C evitado")
    c2.metric("Mejor conservación", mas_frio["empaque"],
              f"T₆₀ = {mas_frio['t60_C']:.1f} °C")
    c3.metric("Temperatura ambiente", f"{datos.temperatura_ambiente(df):.1f} °C")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📈 Curvas", "💰 Costos", "🏆 Ranking", "🔬 Física"]
    )

    with tab1:
        st.plotly_chart(grafico_curvas(df, umbral), use_container_width=True)
        st.caption(
            "Barras de error = desviación estándar entre repeticiones. "
            "La línea punteada marca el umbral de calidad seleccionado."
        )

    with tab2:
        ca, cb = st.columns(2)
        with ca:
            st.plotly_chart(grafico_costo_barras(res), use_container_width=True)
        with cb:
            st.plotly_chart(grafico_costo_vs_t60(res, umbral), use_container_width=True)
        st.caption(
            "El cuadrante ideal es **abajo-izquierda**: barato y que conserva frío. "
            "El costo por uso depende del número de usos supuesto (barra lateral)."
        )

    with tab3:
        st.subheader("Ranking por eficiencia costo-beneficio")
        cols = ["puesto", "empaque", "t60_C", "t_umbral_min",
                "costo_por_uso", "soles_por_C_evitado", "usos"]
        st.dataframe(tabla_es(rk[cols]), use_container_width=True, hide_index=True)

        csv_buf = io.StringIO()
        tabla_es(rk).to_csv(csv_buf, index=False)
        st.download_button(
            "⬇️ Descargar ranking completo (CSV)",
            data=csv_buf.getvalue(),
            file_name="ranking_empaques.csv", mime="text/csv",
        )

    with tab4:
        st.subheader("Resultados físicos por empaque")
        cols_fis = ["empaque", "delta_T", "q_absorbido_J", "k_fit_min", "r2",
                    "ua_fit_WK", "r_cond_KW", "ua_cond_WK", "qdot_cond_W"]
        st.dataframe(tabla_es(res[cols_fis]), use_container_width=True, hide_index=True)
        st.info(
            "**U·A ajustado vs. U·A conductivo.** El ajustado (desde el enfriamiento "
            "real, k·m·c) suele ser mayor que el conductivo (solo pared, 1/R=k·A/L) "
            "porque incluye convección y la propia botella. Es la evidencia numérica "
            "de que **U no equivale a la conductividad k del material**."
        )
        st.latex(r"Q = m\,c\,\Delta T \qquad R=\frac{L}{k\,A} \qquad \dot{Q}=\frac{\Delta T}{R} \qquad U\!\cdot\!A = k_{fit}\,m\,c")

    st.divider()
    st.caption(f"Fuente de datos: {fuente}  ·  {len(df)} lecturas  ·  Núcleo de cálculo verificado con 23 pruebas.")


if __name__ == "__main__":
    main()
