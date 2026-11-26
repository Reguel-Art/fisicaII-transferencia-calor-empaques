"""Controles compartidos entre páginas y registro de páginas."""

from __future__ import annotations

import streamlit as st

from ui import estado

PAGINAS: dict = {}   # lo llena app.py: {"vista": st.Page, "datos": ..., ...}


def configurar_experimento():
    """Popover «Configurar experimento»: límite de temperatura y tiempo de entrega."""
    ss = st.session_state
    tope = estado.t_tope(ss.df_actual)
    # Mantener el valor dentro del rango válido del slider (múltiplo de 5 en [5, tope]).
    if tope >= 10:
        ss.cfg_t = int(min(max(5, 5 * round(ss.cfg_t / 5)), tope))
    else:
        ss.cfg_t = tope
    with st.popover("Configurar experimento", icon=":material/tune:", type="tertiary"):
        st.slider("Límite de temperatura (°C)", min_value=6.0, max_value=24.0, step=0.5,
                  key="cfg_umbral", persist_state="session",
                  help="Temperatura máxima aceptable de la bebida al entregarla.")
        if tope >= 10:
            st.slider("Tiempo de entrega a evaluar (min)", min_value=5, max_value=tope, step=5,
                      key="cfg_t", persist_state="session",
                      help="Las métricas y la viabilidad se evalúan hasta este instante.")
        else:
            st.caption(f"Los datos llegan solo hasta {tope} min: se evalúa en ese instante.")
        st.caption("Una alternativa es viable si **todas** sus lecturas hasta el tiempo de "
                   "entrega quedan por debajo del límite.")
