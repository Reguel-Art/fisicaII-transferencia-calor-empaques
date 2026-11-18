"""Página «Evaluación económica»: costos por material y preferencia de decisión."""

from __future__ import annotations

import streamlit as st

from ui import estado, graficos, tablas
from ui.estilo import barra_superior, e, encabezado, titulo_tarjeta

ss = st.session_state


def _tabla_costos_editable():
    estado.tabla_costos()                     # sincroniza con los empaques actuales
    clave = f"eco_tabla_{ss.eco_ver}"
    if clave not in ss:                       # al volver a la página: partir de lo último
        ss.eco_tabla_base = ss.eco_tabla_ult
    editada = st.data_editor(
        ss.eco_tabla_base, key=clave, hide_index=True, width="stretch", num_rows="fixed",
        column_config={
            # Material fijo a la izquierda y columnas angostas: en celular se ve el
            # nombre mientras se desliza la tabla hacia los demás costos.
            "material": st.column_config.TextColumn("Material", disabled=True, pinned=True),
            "precio": st.column_config.NumberColumn("Precio S/", min_value=0.0, step=0.1,
                                                    format="%.2f", width="small"),
            "usos": st.column_config.NumberColumn("Usos", min_value=1, step=1, format="%d",
                                                  width="small"),
            "limpieza": st.column_config.NumberColumn("Limp. S/", min_value=0.0, step=0.05,
                                                      format="%.2f", width="small",
                                                      help="Costo de limpieza por uso"),
            "otros": st.column_config.NumberColumn("Otros S/", min_value=0.0, step=0.05,
                                                   format="%.2f", width="small",
                                                   help="Otros costos por uso"),
            "control": st.column_config.CheckboxColumn("Control", width="small",
                                                       help="Referencia sin empaque (se excluye)"),
        },
    )
    ss.eco_tabla_ult = editada
    st.markdown('<div class="tp-solo-movil">Desliza la tabla hacia la derecha para ver usos, '
                'limpieza, otros costos y el control.</div>', unsafe_allow_html=True)
    if int(editada["control"].fillna(False).astype(bool).sum()) > 1:
        st.warning("Marca un solo control; se usará el primero de la lista.")


def render():
    barra_superior("Evaluación económica")
    encabezado("Conservar también es decidir",
               "Encuentra el equilibrio entre desempeño térmico y costo por entrega.")
    with st.container(key="banner_eco"):
        st.markdown('<div class="tp-banner">🪙 <b>Una decisión que también cuida tus costos</b>'
                    "Los precios iniciales son supuestos didácticos. Reemplázalos con "
                    "cotizaciones y usos verificables.</div>", unsafe_allow_html=True)
    st.write("")

    with st.container(key="fila_eco"):
        izq, der = st.columns([2.7, 1])
    with izq, st.container(key="card_costos"):
        a, b = st.columns([5, 1])
        with a:
            titulo_tarjeta("Costos por material",
                           "Costo por uso = precio ÷ usos + limpieza + otros costos.")
        b.markdown('<div style="text-align:right"><span class="tp-chip">PEN · S/</span></div>',
                   unsafe_allow_html=True)
        _tabla_costos_editable()
        c1, c2, c3 = st.columns(3)
        c1.number_input("Pedidos a evaluar", min_value=1, step=10, key="eco_pedidos",
                        persist_state="session")
        c2.number_input("Empaques por pedido", min_value=1, step=1, key="eco_empaques",
                        persist_state="session")
        c3.number_input("Máximo por uso (S/)", min_value=0.0, step=0.1, format="%.2f",
                        key="eco_max", persist_state="session",
                        help="0 = sin límite de costo")
        st.text_input("Fuente o referencia de precios", key="eco_fuente",
                      persist_state="session")

    with der, st.container(key="card_pref"):
        titulo_tarjeta("¿Qué es más importante?", "Ajusta las prioridades de tu decisión.")
        w = int(ss.eco_peso)
        st.markdown(
            f'<div class="tp-pesos"><div><div>🌡️</div><div class="n">{w}<small>%</small></div>'
            f'<div class="l">Conservación</div></div><div><div>🪙</div>'
            f'<div class="n costo">{100 - w}<small>%</small></div><div class="l">Costo</div></div></div>',
            unsafe_allow_html=True)
        st.slider("Peso de la conservación", 0, 100, step=5, key="eco_peso",
                  persist_state="session", label_visibility="collapsed")
        st.markdown('<div class="tp-extremos"><span>Priorizar costo</span>'
                    '<span>Priorizar temperatura</span></div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="tp-nota"><b>✓ Primero, el requisito térmico.</b>Solo se puntúan los '
            'empaques que cumplen el límite en todas las lecturas y tienen costo registrado. '
            'El control se excluye.</div>', unsafe_allow_html=True)
        st.caption("60/40 es una preferencia inicial editable, no un resultado de investigación. "
                   "Menor cambio térmico y menor costo reciben mayor puntuación.")
        if st.button("Analizar alternativas", icon=":material/play_arrow:", type="primary",
                     width="stretch"):
            ss.eco_analizado = True

    if not ss.get("eco_analizado"):
        st.write("")
        st.info("Ajusta los costos y tu preferencia, y pulsa **Analizar alternativas** "
                "para ver el ranking.")
        return

    R = estado.calcular()
    res = R.res
    st.write("")
    with st.container(key="card_rank"):
        titulo_tarjeta("Ranking de alternativas",
                       f"Límite {R.umbral:.1f} °C hasta los {R.t} min · "
                       f"{R.n_viables} de {R.n_alternativas} viables")
        cols = {"puesto": "Puesto", "empaque": "Empaque", "motivo": "Estado",
                "T_t": f"T a {R.t} min (°C)", "costo_uso": "S/ por uso",
                "costo_total": f"Total {ss.eco_pedidos} pedidos (S/)",
                "spc_t": "S/ por °C evitado", "puntaje": "Puntaje"}
        vista, cfg = tablas.para_mostrar(res[list(cols)].rename(columns=cols),
                                         texto=("Puesto", "Empaque", "Estado", "Puntaje"))
        cfg["Puntaje"] = st.column_config.ProgressColumn(
            "Puntaje", min_value=0, max_value=100, format="%.0f")
        st.dataframe(vista, hide_index=True, width="stretch", column_config=cfg,
                     height=tablas.alto(len(vista)))
        if R.reco is not None:
            st.markdown(
                f'<div class="tp-nota"><b>Recomendación: {e(R.reco["empaque"])}</b>'
                f'Para {ss.eco_pedidos} pedidos con {ss.eco_empaques} empaque(s) por pedido el '
                f'costo estimado es S/ {R.reco["costo_total"]:.2f}. Fuente de precios: '
                f'{e(ss.eco_fuente)}.</div>', unsafe_allow_html=True)
        else:
            st.warning("Ninguna alternativa cumple el límite en todas las lecturas con costo "
                       "registrado. Revisa el límite, el tiempo de entrega o el costo máximo.")
    st.write("")
    izq, der = st.columns(2)
    with izq, st.container(key="card_cuad"):
        titulo_tarjeta("Costo vs. temperatura", "Abajo a la izquierda: barato y frío")
        if (~res["es_control"]).any():
            st.plotly_chart(graficos.cuadrantes(res, R.control, R.umbral, R.t),
                            width="stretch", config={"displaylogo": False, "displayModeBar": False})
    with der, st.container(key="card_barras"):
        titulo_tarjeta("Costo por uso por material", "Incluye limpieza y otros costos")
        st.plotly_chart(graficos.costo_barras(res, R.control), width="stretch",
                        config={"displaylogo": False, "displayModeBar": False})
