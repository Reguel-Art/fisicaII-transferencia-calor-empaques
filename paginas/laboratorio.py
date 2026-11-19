"""Página «Laboratorio 3D»: las cuatro muestras en 3D, minuto a minuto."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd
import streamlit as st

from core import datos
from ui import estado, lab3d
from ui.controles import PAGINAS
from ui.estilo import barra_superior, e, encabezado, titulo_tarjeta

ss = st.session_state
POR_FILA = 4


def _tabla_minuto(R, t: int) -> pd.DataFrame:
    """Temperatura media, lecturas y flujo de calor de cada empaque en el minuto t."""
    df = R.df
    ag = datos.agregar(df)
    t_amb = datos.temperatura_ambiente(df)
    res = R.res.set_index("empaque")
    filas = []
    for emp in datos.lista_empaques(df):
        sub = ag[ag["empaque"] == emp]
        t_max = float(sub["tiempo_min"].max())
        cubre = t <= t_max
        T = datos.temperatura_en_tiempo(ag, emp, t) if cubre else np.nan
        n = int(df[(df["empaque"] == emp) & (df["tiempo_min"] == t)]["repeticion"].nunique())
        ua = res.loc[emp, "ua_fit_WK"] if emp in res.index else np.nan
        qdot = ua * (t_amb - T) if pd.notna(ua) and pd.notna(T) else np.nan
        filas.append(dict(
            empaque=emp, T=T, n=n, t_amb=t_amb, qdot=qdot,
            es_control=bool(res.loc[emp, "es_control"]) if emp in res.index else False,
            costo_uso=float(res.loc[emp, "costo_uso"]) if emp in res.index else 0.0,
        ))
    return pd.DataFrame(filas)


def _escala(df: pd.DataFrame) -> tuple[float, float]:
    """Escala común de color: de la lectura más fría a la más caliente (en °C enteros)."""
    lo = math.floor(float(df["temp_C"].min()))
    hi = math.ceil(float(df["temp_C"].max()))
    return float(lo), float(max(hi, lo + 1))


def _tarjeta_muestra(fila, i: int, lo: float, hi: float, corte: bool, ver_flujo: bool,
                     flujo_max: float, t: int):
    color = lab3d.color_temperatura(fila["T"], lo, hi)
    flujo_rel = (fila["qdot"] / flujo_max) if flujo_max and pd.notna(fila["qdot"]) else 0.0
    with st.container(key=f"cardlab_{i}"):
        fig = lab3d.figura_muestra(fila["empaque"], fila["es_control"], fila["T"], lo, hi,
                                   corte, ver_flujo, flujo_rel, ss.lab_zoom, ss.lab_rev)
        st.plotly_chart(fig, width="stretch", key=f"lab3d_{i}", theme=None,
                        config={"displayModeBar": False, "displaylogo": False},
                        alt=f"Modelo 3D: botella de agua en {fila['empaque']}, "
                            f"a {fila['T']:.2f} °C en el minuto {t}")
        temp = "—" if pd.isna(fila["T"]) else f"{fila['T']:.2f}"
        if fila["es_control"]:
            costo = "Sin costo · referencia"
        elif fila["costo_uso"] > 0:
            costo = f"S/ {fila['costo_uso']:.2f} por uso"
        else:
            costo = "Costo sin registrar"
        flujo = ("—" if pd.isna(fila["qdot"]) else f"{fila['qdot']:.2f} W")
        st.markdown(
            f'<div class="tp-lab-nom"><span style="background:{color}"></span>{e(fila["empaque"])}</div>'
            f'<div class="tp-lab-temp">{temp}<small> °C</small></div>'
            f'<div class="tp-lab-sub">Media de lecturas · n = {fila["n"]} · minuto {t}</div>'
            f'<div class="tp-lab-pie"><b>{e(costo)}</b>'
            f'<span>Ambiente · {fila["t_amb"]:.2f} °C</span>'
            f'<span>Calor hacia el agua · {flujo}</span></div>',
            unsafe_allow_html=True)


def _muestras(R):
    """Tarjeta principal. Es un fragmento: sus controles no recargan toda la página."""
    df = R.df
    t_max = int(df["tiempo_min"].max())
    paso = 5 if t_max >= 10 else 1

    # Reproducción: cada ejecución automática del fragmento avanza un paso.
    if ss.get("lab_play"):
        if ss.get("lab_inicio"):          # primer cuadro: arrancar desde 0 si ya estaba al final
            ss.lab_inicio = False
            if ss.lab_t >= t_max:
                ss.lab_t = 0
        elif ss.lab_t >= t_max:
            ss.lab_play = False
            st.rerun(scope="app")         # detiene la actualización automática
        else:
            ss.lab_t = min(t_max, ss.lab_t + paso)

    with st.container(key="card_lab"):
        a, b = st.columns([2, 1.2], vertical_alignment="center")
        with a:
            titulo_tarjeta("Las cuatro muestras" if len(datos.lista_empaques(df)) == 4
                           else "Las muestras",
                           "El informe usa 500 mL de agua por botella. Arrastra para girar "
                           "cada muestra; todas están a la misma escala.")
        with b, st.container(horizontal=True, horizontal_alignment="right",
                             vertical_alignment="center"):
            st.segmented_control("Vista", ["En corte", "Completo"], key="lab_vista",
                                 required=True, persist_state="session",
                                 label_visibility="collapsed")
            if st.button("", icon=":material/remove:", key="lab_menos", help="Alejar"):
                ss.lab_zoom = max(0.6, round(ss.lab_zoom - 0.15, 2))
            if st.button("", icon=":material/add:", key="lab_mas", help="Acercar"):
                ss.lab_zoom = min(1.8, round(ss.lab_zoom + 0.15, 2))
            if st.button("", icon=":material/refresh:", key="lab_reset",
                         help="Volver a la vista inicial"):
                ss.lab_zoom, ss.lab_rev = 1.0, ss.lab_rev + 1

        c1, c2, c3 = st.columns([4, 1, 1], vertical_alignment="bottom")
        with c1:
            st.slider("Minuto del ensayo", 0, t_max, step=paso, key="lab_t",
                      format="%d min")
        # Reproducir/pausar cambian la frecuencia del fragmento: hace falta recargar la página.
        with c2:
            if ss.get("lab_play"):
                if st.button("Pausar", icon=":material/pause:", key="lab_pausa", width="stretch"):
                    ss.lab_play = False
                    st.rerun(scope="app")
            elif st.button("Reproducir", icon=":material/play_arrow:", key="lab_rep",
                           width="stretch", type="primary"):
                ss.lab_play, ss.lab_inicio = True, True
                st.rerun(scope="app")
        with c3:
            st.button("Minuto 0", icon=":material/first_page:", key="lab_cero", width="stretch",
                      on_click=lambda: ss.update(lab_t=0, lab_play=False))

        t = int(ss.lab_t)
        tabla = _tabla_minuto(R, t)
        lo, hi = _escala(df)
        corte = ss.lab_vista == "En corte"
        flujo_max = float(tabla["qdot"].max(skipna=True)) if tabla["qdot"].notna().any() else 0.0

        tabla = pd.concat([tabla[~tabla["es_control"]], tabla[tabla["es_control"]]])
        filas = list(tabla.itertuples(index=False))
        for ini in range(0, len(filas), POR_FILA):
            with st.container(key=f"fila_lab_{ini}"):
                cols = st.columns(POR_FILA)
            for j, fila in enumerate(filas[ini:ini + POR_FILA]):
                with cols[j]:
                    _tarjeta_muestra(fila._asdict(), ini + j, lo, hi, corte, ss.lab_ver_flujo,
                                     flujo_max, t)

        izq, der = st.columns([1.3, 1], vertical_alignment="center")
        with izq:
            st.markdown(
                f'<div class="tp-escala"><div class="tp-escala-tit"><b>Temperatura del agua</b>'
                f'<span>Escala común · °C</span></div>'
                f'<div class="tp-escala-barra" style="background:{lab3d.gradiente_css(lo, hi)}"></div>'
                f'<div class="tp-escala-num"><span>{lo:g} °C</span><span>{(lo + hi) / 2:g} °C</span>'
                f'<span>{hi:g} °C</span></div></div>', unsafe_allow_html=True)
        with der, st.container(horizontal_alignment="right"):
            st.checkbox("Mostrar flujo de calor", key="lab_ver_flujo", persist_state="session",
                        help="Flechas ilustrativas del sentido del intercambio; su largo es "
                             "proporcional a Q̇ = U·A·(T ambiente − T agua).")
            st.caption("Flechas ilustrativas del sentido del intercambio.")


def render():
    R = estado.calcular()
    df = R.df
    ss.setdefault("lab_t", 0)
    ss.setdefault("lab_zoom", 1.0)
    ss.setdefault("lab_rev", 0)
    ss.setdefault("lab_vista", "En corte")
    ss.setdefault("lab_ver_flujo", True)
    if ss.lab_t > int(df["tiempo_min"].max()):
        ss.lab_t = 0

    barra_superior("Laboratorio 3D")
    with st.container(key="fila_cab"):
        izq, der = st.columns([3, 1.25], vertical_alignment="bottom")
    with izq:
        encabezado("Laboratorio térmico 3D",
                   "Explora cómo cambia la temperatura del agua durante los "
                   f"{int(df['tiempo_min'].max())} minutos del ensayo.")
    with der, st.container(horizontal=True, horizontal_alignment="right"):
        with st.popover("Exportar", icon=":material/download:"):
            ag = datos.agregar(df)
            ancha = ag.pivot(index="tiempo_min", columns="empaque", values="temp_media").round(2)
            st.download_button("Temperatura por minuto (CSV)", ancha.to_csv(),
                               "temperatura_por_minuto.csv", "text/csv", width="stretch")
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

    # Mientras se reproduce, solo este fragmento se vuelve a ejecutar (cada 0,9 s).
    st.fragment(_muestras, run_every=0.9 if ss.get("lab_play") else None)(R)
