"""TermoPack — comparación de empaques térmicos (Grupo 3 · Física II).

Ejecutar:
    streamlit run app.py

Estructura:
    app.py          punto de entrada: estilo, barra lateral y navegación
    paginas/        Vista general · Datos del experimento · Evaluación económica · Fundamento físico
    ui/             estado compartido, estilos y gráficos
    editor.py       editor de datos dentro de la app
    core/           motor de cálculo (física, costos, decisión) — verificado con pruebas
"""

from __future__ import annotations

import streamlit as st

from paginas import datos_experimento, economia, fisica, laboratorio, vista_general
from ui import controles, estado, estilo

st.set_page_config(page_title="TermoPack · Análisis de empaques", page_icon="📦",
                   layout="wide", initial_sidebar_state="auto")

estilo.aplicar_css()
estado.inicializar()

paginas = {
    "vista": st.Page(vista_general.render, title="Vista general", url_path="vista-general",
                     default=True),
    "lab": st.Page(laboratorio.render, title="Laboratorio 3D", url_path="laboratorio"),
    "datos": st.Page(datos_experimento.render, title="Datos del experimento", url_path="datos"),
    "economia": st.Page(economia.render, title="Evaluación económica", url_path="economia"),
    "fisica": st.Page(fisica.render, title="Fundamento físico", url_path="fisica"),
}
controles.PAGINAS.update(paginas)

actual = st.navigation(list(paginas.values()), position="hidden")
estilo.barra_lateral(paginas, len(st.session_state.df_actual))
actual.run()
