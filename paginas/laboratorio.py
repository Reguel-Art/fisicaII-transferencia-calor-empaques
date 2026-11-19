"""Página «Laboratorio 3D»: las muestras en 3D, minuto a minuto.

La animación corre en el navegador (ui/visor3d.py): Python calcula la temperatura
y el flujo de calor de cada empaque en cada minuto, y el visor solo recolorea el
agua y ajusta las flechas, sin volver a crear los modelos 3D.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import streamlit as st

from core import datos
from ui import estado, lab3d, visor3d
from ui.controles import PAGINAS
from ui.estilo import barra_superior, e, encabezado, titulo_tarjeta

ss = st.session_state


def _escala(df: pd.DataFrame) -> tuple[float, float]:
    """Escala común de color: de la lectura más fría a la más caliente (°C enteros)."""
    lo = math.floor(float(df["temp_C"].min()))
    hi = math.ceil(float(df["temp_C"].max()))
    return float(lo), float(max(hi, lo + 1))


def _num(v) -> float | None:
    return None if v is None or pd.isna(v) else round(float(v), 4)


def _muestras(R, tmax: int) -> tuple[list[dict], float]:
    """Datos por minuto de cada empaque (empaques primero, el control al final)."""
    df = R.df
    ag = datos.agregar(df)
    t_amb = datos.temperatura_ambiente(df)
    res = R.res.set_index("empaque")
    minutos = np.arange(0, tmax + 1)
    salida, qmax = [], 0.0
    for emp in datos.lista_empaques(df):
        sub = ag[ag["empaque"] == emp].sort_values("tiempo_min")
        t_ult = float(sub["tiempo_min"].max())
        # Interpolación lineal entre lecturas; sin extrapolar más allá de la última.
        T = np.interp(minutos, sub["tiempo_min"], sub["temp_media"])
        T = np.where(minutos <= t_ult, T, np.nan)
        reps = df[df["empaque"] == emp].groupby("tiempo_min")["repeticion"].nunique()
        n = [int(reps.get(m, 0)) for m in minutos]
        es_control = bool(res.loc[emp, "es_control"]) if emp in res.index else False
        ua = res.loc[emp, "ua_fit_WK"] if emp in res.index else np.nan
        q = ua * (t_amb - T) if pd.notna(ua) else np.full_like(T, np.nan)
        if np.isfinite(q).any():
            qmax = max(qmax, float(np.nanmax(q)))
        costo_uso = float(res.loc[emp, "costo_uso"]) if emp in res.index else 0.0
        costo = ("Sin costo · referencia" if es_control
                 else f"S/ {costo_uso:.2f} por uso" if costo_uso > 0 else "Costo sin registrar")
        salida.append(dict(
            nombre=emp, es_control=es_control, costo=costo, amb=round(t_amb, 2),
            temps=[_num(v) for v in T], qdot=[_num(v) for v in q], n=n,
            escenas={"corte": lab3d.escena(emp, es_control, corte=True),
                     "completo": lab3d.escena(emp, es_control, corte=False)},
        ))
    salida.sort(key=lambda m: m["es_control"])
    return salida, qmax


def render():
    R = estado.calcular()
    df = R.df
    tmax = int(df["tiempo_min"].max())

    barra_superior("Laboratorio 3D")
    with st.container(key="fila_cab"):
        izq, der = st.columns([3, 1.25], vertical_alignment="bottom")
    with izq:
        encabezado("Laboratorio térmico 3D",
                   f"Explora cómo cambia la temperatura del agua durante los {tmax} minutos "
                   "del ensayo, minuto a minuto.")
    with der, st.container(horizontal=True, horizontal_alignment="right"):
        with st.popover("Exportar", icon=":material/download:"):
            ag = datos.agregar(df)
            ancha = ag.pivot(index="tiempo_min", columns="empaque", values="temp_media").round(2)
            st.download_button("Temperatura por lectura (CSV)", ancha.to_csv(),
                               "temperatura_por_lectura.csv", "text/csv", width="stretch")
        if st.button("Cargar datos", icon=":material/upload:", type="primary"):
            ss.src_modo = "Subir CSV"
            st.switch_page(PAGINAS["datos"])

    estado_d = estado.estado_datos(df)
    with st.container(key="banner_lab", horizontal=True, vertical_alignment="center"):
        etiqueta = "Datos simulados" if estado_d == "Simulado" else "Datos experimentales"
        st.markdown(f'<div class="tp-banner">⚗️ <b>{etiqueta}</b>{e(ss.fuente_nombre)} · '
                    f'{len(df)} registros</div>', unsafe_allow_html=True)
        st.page_link(PAGINAS["datos"], label="Ver datos del experimento →")
    st.write("")

    muestras, qmax = _muestras(R, tmax)
    lo, hi = _escala(df)
    with st.container(key="card_lab"):
        titulo_tarjeta(
            "Las cuatro muestras" if len(muestras) == 4 else "Las muestras",
            "El informe usa 500 mL de agua por botella. Arrastra para girar cada muestra; "
            "todas están a la misma escala. Entre lecturas (cada 5 min) la temperatura se "
            "interpola.")
        st.iframe(visor3d.html_visor(muestras, tmax, lo, hi, qmax), height="content",
                  alt="Laboratorio 3D: botellas de agua dentro de cada empaque, coloreadas "
                      "según su temperatura minuto a minuto")
