"""Página «Fundamento físico»: modelo, fórmulas evaluadas y resultados."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core import datos
from ui import estado, tablas
from ui.controles import configurar_experimento
from ui.estilo import barra_superior, encabezado, titulo_tarjeta

ss = st.session_state


def _tarjetas(R):
    res, df, t = R.res, R.df, R.t
    empaques = res["empaque"].tolist()
    alt = res[~res["es_control"] & res["T_t"].notna()]
    defecto = alt.loc[alt["T_t"].idxmin(), "empaque"] if not alt.empty else empaques[0]
    if ss.get("fis_emp") not in empaques:
        ss.fis_emp = defecto
    emp = st.segmented_control("Empaque", empaques, key="fis_emp", required=True,
                               persist_state="session", width="stretch",
                               label_visibility="collapsed")
    r = res[res["empaque"] == emp].iloc[0]
    p = datos.params_empaque(df, emp)
    t_amb = datos.temperatura_ambiente(df)

    with st.container(key="fila_form"):
        c1, c2, c3 = st.columns(3)
    with c1, st.container(key="card_f1"):
        titulo_tarjeta("Calor sensible absorbido", "Energía que ganó el agua")
        st.latex(r"Q = m\,c\,\Delta T")
        st.latex(rf"Q = {p.masa_agua_kg:.2f}\cdot{p.calor_especifico_j_kgk:.0f}"
                 rf"\cdot({r['T_t']:.2f}-{r['t0_C']:.2f})")
        st.markdown(f'<span class="tp-chip">Q = {r["Q_t"] / 1000:.2f} kJ a los {t} min</span>',
                    unsafe_allow_html=True)
    with c2, st.container(key="card_f2"):
        titulo_tarjeta("Constante de calentamiento", "Qué tan rápido se calienta")
        st.latex(r"k_{\text{ef}} = -\frac{1}{t}\ln\frac{T_a - T(t)}{T_a - T_0}")
        if pd.notna(r["k_ef_t"]):
            st.latex(rf"k_{{\text{{ef}}}} = -\tfrac{{1}}{{{t}}}"
                     rf"\ln\tfrac{{{t_amb:.2f}-{r['T_t']:.2f}}}{{{t_amb:.2f}-{r['t0_C']:.2f}}}")
            st.markdown(f'<span class="tp-chip">k_ef = {r["k_ef_t"]:.5f} min⁻¹</span>',
                        unsafe_allow_html=True)
        if pd.notna(r["k_fit_min"]):
            st.caption(f"Ajuste con toda la curva: k = {r['k_fit_min']:.5f} min⁻¹ "
                       f"(R² = {r['r2']:.4f}) · U·A = k·m·c = {r['ua_fit_WK']:.3f} W/K")
    with c3, st.container(key="card_f3"):
        titulo_tarjeta("Resistencia térmica", "Oposición de la pared al paso del calor")
        st.latex(r"R = \frac{L}{k\,A} \qquad \dot{Q} = \frac{T_a - T(t)}{R}")
        if pd.notna(r["r_cond_KW"]):
            st.latex(rf"R = \tfrac{{{p.espesor_pared_mm / 1000:.3f}}}"
                     rf"{{{p.conductividad_k_wmk:.3f}\cdot{p.area_superficial_m2:.2f}}}"
                     rf"= {r['r_cond_KW']:.3f}\ \text{{K/W}}")
            st.markdown(f'<span class="tp-chip">Q̇ = {r["qdot_t"]:.2f} W a los {t} min</span>',
                        unsafe_allow_html=True)
        else:
            st.caption("Sin pared aislante (espesor 0): la ley de conducción no aplica.")


def render():
    R = estado.calcular()
    barra_superior("Fundamento físico")
    encabezado("Fundamento físico",
               "Las leyes que convierten lecturas de temperatura en una decisión.")
    st.write("")

    with st.container(key="card_modelo"):
        a, b = st.columns([2, 1])
        with a:
            titulo_tarjeta("Modelo de calentamiento",
                           "Ley de enfriamiento de Newton para una bebida fría en un ambiente cálido")
        with b, st.container(horizontal=True, horizontal_alignment="right"):
            configurar_experimento()
        c1, c2 = st.columns([1.1, 1])
        with c1:
            # Dos ecuaciones separadas: juntas no caben en un celular.
            st.latex(r"T(t) = T_a + (T_0 - T_a)\,e^{-k t}")
            st.latex(r"U\!\cdot\!A = k\,m\,c")
            st.markdown(
                "La bebida gana calor del ambiente por **conducción** a través de las paredes, "
                "**convección** del aire y el líquido, y **radiación**. Un buen empaque reduce "
                "la conductancia global **U·A**: la constante **k** es menor y la bebida tarda "
                "más en llegar al límite.")
        with c2:
            st.markdown(
                f"- **Límite evaluado:** {R.umbral:.1f} °C\n"
                f"- **Tiempo de entrega:** {R.t} min\n"
                f"- **Temperatura ambiente media:** {datos.temperatura_ambiente(R.df):.1f} °C\n"
                f"- **Lecturas:** {len(R.df)} · {R.df['repeticion'].nunique()} repeticiones")

    st.write("")
    st.markdown(f'<div class="tp-ceja-sec">FÓRMULAS APLICADAS A LOS {R.t} MIN</div>',
                unsafe_allow_html=True)
    _tarjetas(R)

    st.write("")
    with st.container(key="card_fis_tabla"):
        titulo_tarjeta("Resultados físicos por empaque")
        cols = {"empaque": "Empaque", "T_t": f"T a {R.t} min (°C)", "dT_t": "ΔT (°C)",
                "Q_t": "Q (J)", "k_ef_t": "k_ef (1/min)", "k_fit_min": "k ajustada (1/min)",
                "r2": "R²", "ua_fit_WK": "U·A ajustado (W/K)", "r_cond_KW": "R cond. (K/W)",
                "ua_cond_WK": "U·A cond. (W/K)", "qdot_t": "Q̇ (W)",
                "t_umbral_min": "t hasta límite (min)"}
        precisas = {"R²": 4, "U·A ajustado (W/K)": 4, "U·A cond. (W/K)": 4, "R cond. (K/W)": 3}
        vista, cfg = tablas.para_mostrar(R.res[list(cols)].rename(columns=cols),
                                         decimales=precisas)
        st.dataframe(vista, hide_index=True, width="stretch", column_config=cfg,
                     height=tablas.alto(len(vista)))
        st.markdown(
            '<div class="tp-nota"><b>U·A ajustado vs. U·A conductivo</b>El ajustado (desde el '
            'calentamiento real, k·m·c) suele ser mayor que el conductivo (solo la pared, '
            '1/R = k·A/L) porque también incluye convección y la propia botella: U no equivale '
            'a la conductividad k del material.</div>', unsafe_allow_html=True)
