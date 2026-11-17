"""Página «Datos del experimento»: elegir, subir o editar las mediciones."""

from __future__ import annotations

import pandas as pd
import streamlit as st

import editor
from core import datos
from ui import estado
from ui.estilo import barra_superior, e, encabezado, titulo_tarjeta

ss = st.session_state
MODOS = ["Ejemplo del Grupo 3", "Subir CSV", "Editar en la app"]
_MODO_DE_FUENTE = {"Ejemplo": MODOS[0], "CSV": MODOS[1], "Editor": MODOS[2]}


def _resumen(df: pd.DataFrame) -> pd.DataFrame:
    filas = []
    ag = datos.agregar(df)
    for emp in datos.lista_empaques(df):
        sub = df[df["empaque"] == emp]
        a = ag[ag["empaque"] == emp].sort_values("tiempo_min")
        filas.append({
            "Empaque": emp,
            "Lecturas": len(sub),
            "Repeticiones": sub["repeticion"].nunique(),
            "Instantes": f'{a["tiempo_min"].min():g}–{a["tiempo_min"].max():g} min ({len(a)})',
            "T inicial (°C)": round(a["temp_media"].iloc[0], 2),
            "T final (°C)": round(a["temp_media"].iloc[-1], 2),
            "T ambiente (°C)": (round(sub["temp_amb_C"].mean(), 2)
                                if "temp_amb_C" in sub else None),
        })
    return pd.DataFrame(filas)


def render():
    barra_superior("Datos del experimento")
    encabezado("Datos del experimento",
               "Usa el escenario de ejemplo, sube tu CSV o escribe tus mediciones aquí mismo.")
    st.write("")

    if "src_modo" not in ss:
        ss.src_modo = _MODO_DE_FUENTE.get(ss.fuente_modo, MODOS[0])

    with st.container(key="card_origen"):
        titulo_tarjeta("Origen de los datos",
                       "Todo el análisis (las cuatro secciones) usa los datos elegidos aquí.")
        modo = st.segmented_control("Origen", MODOS, key="src_modo", required=True,
                                    persist_state="session", label_visibility="collapsed")

        if modo == MODOS[0]:
            if ss.fuente_modo != "Ejemplo":
                ej = estado.cargar_ejemplo()
                estado.fijar_base(ej, estado.CSV_DEFECTO.name, "Ejemplo", estado.CSV_DEFECTO.name)
            st.caption("Escenario simulado del informe EC3: 4 empaques × 3 repeticiones × "
                       "13 instantes (0–60 min).")

        elif modo == MODOS[1]:
            c1, c2 = st.columns([3, 1], vertical_alignment="bottom")
            subido = c1.file_uploader("Archivo CSV de mediciones", type=["csv"],
                                      help="Mismo formato que la plantilla.")
            c2.download_button("Descargar plantilla", estado.CSV_DEFECTO.read_bytes(),
                               "plantilla_empaques.csv", "text/csv",
                               icon=":material/download:", width="stretch")
            if subido is not None:
                ident = f"{subido.name}:{subido.size}"
                # También se recarga si los datos en uso son una versión editada.
                if ss.get("ident_base") != ident or ss.fuente_modo != "CSV":
                    try:
                        df = datos.cargar_csv(subido)
                    except datos.ErrorDatos as err:
                        st.error(f"Error en el archivo: {err}")
                        st.stop()
                    estado.fijar_base(df, subido.name, "CSV", ident)
                st.success(f"Cargado: {subido.name} · {len(ss.df_actual)} lecturas.")
            elif ss.fuente_modo == "CSV":
                st.caption(f"En uso: `{ss.fuente_nombre}`. Sube otro archivo para reemplazarlo.")
            else:
                st.caption("Mientras no subas un archivo se siguen usando los datos actuales.")

        else:
            st.caption(f"Se parte de: `{ss.get('nombre_base', ss.fuente_nombre)}`. "
                       "Los cambios se aplican al instante en todas las secciones.")

    if modo == MODOS[2]:
        st.write("")
        with st.container(key="card_editor"):
            df_ed, exportar = editor.render(ss.df_base, ss.ident_base)
            if df_ed is not None:
                estado.fijar_actual(df_ed, f"Editado en la app (desde {ss.nombre_base})", "Editor")
                tab = estado.tabla_costos().set_index("material")
                st.download_button("Descargar estos datos (CSV)",
                                   exportar(tab["precio"].to_dict()),
                                   "mis_datos_empaques.csv", "text/csv",
                                   icon=":material/download:",
                                   help="Guarda tu trabajo; puedes volver a subirlo después.")

    df = ss.df_actual
    st.write("")
    with st.container(key="card_resumen"):
        titulo_tarjeta("Resumen de los datos en uso",
                       f"{ss.fuente_nombre} · {len(df)} lecturas · "
                       f"{estado.estado_datos(df).lower()}")
        st.dataframe(_resumen(df), hide_index=True, width="stretch")
        with st.expander("Ver todas las lecturas"):
            st.dataframe(df, hide_index=True, width="stretch", height=360)
