"""Página «Vista general»: resumen, curvas y recomendación."""

from __future__ import annotations

import numpy as np
import streamlit as st

from core import datos
from ui import estado, graficos
from ui.controles import PAGINAS, configurar_experimento
from ui.estilo import barra_superior, e, encabezado, kpi, titulo_tarjeta

ss = st.session_state


def _promedios_anchos(df):
    ag = datos.agregar(df)
    tabla = ag.pivot(index="tiempo_min", columns="empaque", values="temp_media")
    return tabla[datos.lista_empaques(df)].round(2).reset_index().rename(
        columns={"tiempo_min": "Tiempo (min)"})


def _tabla_resultados(R):
    cols = {"puesto": "Puesto", "empaque": "Empaque", "motivo": "Estado",
            "T_t": f"T a {R.t} min (°C)", "dT_t": "ΔT (°C)", "costo_uso": "S/ por uso",
            "costo_total": "Costo total (S/)", "spc_t": "S/ por °C evitado",
            "puntaje": "Puntaje", "k_fit_min": "k (1/min)", "r2": "R²",
            "q_absorbido_J": "Q final (J)", "t_umbral_min": "t hasta límite (min)"}
    return R.res[list(cols)].replace([np.inf], np.nan).rename(columns=cols)


def render():
    R = estado.calcular()
    df = R.df
    barra_superior("Vista general")

    with st.container(key="fila_cab"):
        izq, der = st.columns([3, 1.25], vertical_alignment="bottom")
    with izq:
        encabezado("Análisis de empaques",
                   "La temperatura importa. Elige el empaque que mejor la conserva.")
    with der:
        with st.container(horizontal=True, horizontal_alignment="right"):
            with st.popover("Exportar", icon=":material/download:"):
                st.download_button("Resultados (CSV)", _tabla_resultados(R).to_csv(index=False),
                                   "resultados_empaques.csv", "text/csv", width="stretch")
                st.download_button("Promedios por instante (CSV)",
                                   _promedios_anchos(df).to_csv(index=False),
                                   "promedios_empaques.csv", "text/csv", width="stretch")
                st.download_button("Datos cargados (CSV)", df.to_csv(index=False),
                                   "datos_empaques.csv", "text/csv", width="stretch")
            if st.button("Cargar datos", icon=":material/upload:", type="primary"):
                ss.src_modo = "Subir CSV"
                st.switch_page(PAGINAS["datos"])

    # Aviso de procedencia de los datos.
    estado_d = estado.estado_datos(df)
    with st.container(key="banner_vg", horizontal=True, vertical_alignment="center"):
        if estado_d == "Simulado":
            st.markdown('<div class="tp-banner">⚗️ <b>Explora con datos simulados</b>'
                        "Un escenario de ejemplo. Carga tus mediciones para obtener resultados "
                        "propios.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="tp-banner">✅ <b>Datos {e(estado_d.lower())}</b>'
                        f"Fuente: {e(ss.fuente_nombre)} · {len(df)} lecturas.</div>",
                        unsafe_allow_html=True)
        st.page_link(PAGINAS["datos"], label="Ver datos →")

    st.write("")
    a, b = st.columns([3, 1], vertical_alignment="center")
    a.markdown('<div class="tp-ceja-sec">RESUMEN DEL EXPERIMENTO</div>', unsafe_allow_html=True)
    with b, st.container(horizontal=True, horizontal_alignment="right"):
        configurar_experimento()

    # ---------- KPIs ----------
    alt = R.res[~R.res["es_control"] & R.res["T_t"].notna()]
    mejor = alt.loc[alt["T_t"].idxmin()] if not alt.empty else None
    with st.container(key="fila_kpis"):
        k1, k2, k3, k4 = st.columns(4)
    with k1:
        if mejor is not None:
            kpi("📦", "Mejor conservación",
                f'<span class="tp-kpi-nombre">{e(mejor["empaque"])}</span>',
                "Menor variación térmica absoluta", ok=True, clave="cardsel_k1")
        else:
            kpi("📦", "Mejor conservación", "—",
                f"Sin lecturas de empaques hasta los {R.t} min", clave="cardsel_k1")
    with k2:
        if mejor is not None:
            kpi("🌡️", "Variación más baja", f'{mejor["dT_t"]:.2f}<small> °C</small>',
                f'De {mejor["t0_C"]:.1f} a {mejor["T_t"]:.2f} °C en {R.t} min', clave="card_k2")
        else:
            kpi("🌡️", "Variación más baja", "—", "Sin datos en ese instante", clave="card_k2")
    with k3:
        if R.reco is not None:
            kpi("🪙", "Costo de la recomendación",
                f'<small>S/</small> {R.reco["costo_uso"]:.2f}',
                "Costo por uso · precios declarados", clave="card_k3")
        else:
            kpi("🪙", "Costo de la recomendación", "—",
                "Sin alternativa viable", clave="card_k3")
    with k4:
        kpi("🛡️", "Alternativas viables",
            f'{R.n_viables}<small> / {R.n_alternativas}</small>',
            "Cumplen temperatura y costo", clave="card_k4")

    st.write("")
    with st.container(key="fila_graf"):
        g, rc = st.columns([2.75, 1])
    with g, st.container(key="card_graf"):
        c1, c2 = st.columns([4, 1])
        with c1:
            titulo_tarjeta("Evolución de la temperatura",
                           "Promedio por instante · bandas de variabilidad entre repeticiones")
        with c2, st.container(horizontal=True, horizontal_alignment="right"):
            st.download_button("", _promedios_anchos(df).to_csv(index=False),
                               "promedios_empaques.csv", "text/csv",
                               icon=":material/download:", type="tertiary",
                               help="Descargar promedios (CSV)")
        c1, c2 = st.columns([3, 1], vertical_alignment="center")
        with c1:
            modo = st.segmented_control(
                "Vista", ["Temperatura", "Variación térmica", "Promedios"],
                default="Temperatura", required=True, key="graf_modo",
                persist_state="session", label_visibility="collapsed")
        with c2, st.container(horizontal=True, horizontal_alignment="right"):
            st.checkbox("Desviación estándar", key="ver_desv", persist_state="session")
        if modo == "Promedios":
            st.dataframe(_promedios_anchos(df), hide_index=True, width="stretch", height=430)
        else:
            st.plotly_chart(
                graficos.curvas(df, R.control, R.umbral, R.t, modo=modo, bandas=ss.ver_desv),
                width="stretch", config={"displaylogo": False})

    with rc, st.container(key="reco"):
        st.markdown('<div class="tp-ceja-sec" style="letter-spacing:.14em">RECOMENDACIÓN DEL '
                    'ANÁLISIS</div>', unsafe_allow_html=True)
        if R.reco is not None:
            r = R.reco
            intro = ("La única alternativa viable en este escenario."
                     if R.n_viables == 1 else
                     f"La mejor de {R.n_viables} alternativas viables con tu preferencia "
                     f"{round(R.peso * 100)} % conservación / {round((1 - R.peso) * 100)} % costo.")
            st.markdown(
                f'<div class="tp-reco-nom">{e(r["empaque"])}</div>'
                f'<div class="tp-reco-txt">{e(intro)} Termina en {r["T_t"]:.2f} °C a los '
                f'{R.t} min y cuesta S/ {r["costo_uso"]:.2f} por uso.</div>'
                f'<span class="tp-chip">✓ Cumple ≤ {R.umbral:.1f} °C en cada lectura</span>',
                unsafe_allow_html=True)
        else:
            st.markdown(
                f'<div class="tp-reco-nom">Sin alternativa viable</div>'
                f'<div class="tp-reco-txt">Ningún empaque con costo registrado mantiene todas sus '
                f'lecturas ≤ {R.umbral:.1f} °C hasta los {R.t} min.'
                + (f' El que mejor conserva es <b>{e(mejor["empaque"])}</b> '
                   f'({mejor["T_t"]:.2f} °C).' if mejor is not None else '')
                + '</div>'
                f'<span class="tp-chip no">Revisa el límite, el tiempo o el costo máximo</span>',
                unsafe_allow_html=True)
        st.divider()
        st.page_link(PAGINAS["economia"], label="Explorar la evaluación  →")

    st.write("")
    with st.container(key="card_tabla"):
        titulo_tarjeta("Comparativo de alternativas",
                       f"Evaluado a los {R.t} min con límite de {R.umbral:.1f} °C")
        vista = _tabla_resultados(R).iloc[:, :9]
        st.dataframe(vista, hide_index=True, width="stretch", column_config={
            c: st.column_config.NumberColumn(format="%.2f")
            for c in vista.columns if c not in ("Puesto", "Empaque", "Estado")})
