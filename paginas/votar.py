"""Página «Votar»: la abre el público desde el código QR (no aparece en el menú)."""

from __future__ import annotations

import streamlit as st

from ui import votacion
from ui.estilo import e

ss = st.session_state


def render():
    u = votacion.urna()
    yo = votacion.id_votante()
    st.markdown('<div class="tp-ceja">TERMOPACK · VOTACIÓN EN VIVO</div>'
                '<div class="tp-titulo" style="font-size:1.9rem">Tu predicción<i>.</i></div>',
                unsafe_allow_html=True)

    # Se actualiza solo: cuando el presentador abre una ronda nueva aparece aquí.
    @st.fragment(run_every=3)
    def _ronda():
        r = u.foto()
        if not r.opciones:
            st.info("Todavía no hay una votación abierta. Espera a que el presentador la inicie.",
                    icon=":material/hourglass_empty:")
            return
        st.markdown(f"#### {e(r.pregunta)}")
        ya = ss.get("voto_ronda") == r.id or yo in r.votantes
        if ya:
            st.success(f"¡Gracias! Votaste por **{e(ss.get('voto_opcion', '—'))}**.",
                       icon=":material/check_circle:")
        else:
            for i, o in enumerate(r.opciones):
                if st.button(o, key=f"voto_{r.id}_{i}", width="stretch",
                             type="primary" if i == 0 else "secondary"):
                    if u.votar(yo, o):
                        ss.voto_ronda, ss.voto_opcion = r.id, o
                    st.rerun(scope="fragment")
        if r.revelada:
            st.markdown("**Resultados**")
            st.markdown(votacion.barras_html(r, {}), unsafe_allow_html=True)
        else:
            st.caption(f"{sum(r.votos.values())} voto(s) hasta ahora · los resultados se muestran "
                       "en la pantalla del presentador.")

    _ronda()
