"""Página «Simulador por ciudad»: ¿cómo le iría a cada empaque en otro departamento?

Pensada para la exposición en vivo:
  1. Alguien del público propone un departamento (o se toca en el mapa).
  2. La app predice, con el modelo de Newton y la k medida de cada empaque, la
     temperatura de la bebida, el calor que absorbe y el minuto en que pasa el límite.
  3. Opcional: antes de revelar, el público vota desde su celular (código QR).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core import escenarios as esc
from ui import estado, graficos, lab3d, tablas, visor3d, votacion
from ui.estilo import AZUL, TENUE, TEXTO, barra_superior, e, encabezado, titulo_tarjeta

ss = st.session_state
RAIZ = Path(__file__).resolve().parents[1]
CSV_CIUDADES = RAIZ / "data" / "ciudades_peru.csv"
MASA_KG, C_AGUA = 0.6, 4186.0   # botella de 600 mL del ensayo
ESCALA_LO, ESCALA_HI = 0.0, 35.0     # escala de color fija: compara ciudades entre sí


@st.cache_data(show_spinner=False)
def ciudades() -> pd.DataFrame:
    return pd.read_csv(CSV_CIUDADES, encoding="utf-8")


def _etiqueta(fila) -> str:
    return f"{fila['departamento']} · {fila['capital']} ({fila['tmax_verano_c']:.1f} °C)"


def _al_cambiar_ciudad():
    """Al elegir otra ciudad, el deslizador toma su temperatura de referencia."""
    cs = ciudades().set_index("departamento")
    if ss.sim_ciudad in cs.index:
        ss.sim_ta = float(round(cs.loc[ss.sim_ciudad, "tmax_verano_c"], 1))


def _empaques(R) -> pd.DataFrame:
    """k de cada empaque (ajustada con las mediciones) y su costo por uso."""
    r = R.res[["empaque", "k_fit_min", "es_control", "costo_uso", "orden"]].copy()
    r = r[r["k_fit_min"].notna() & (r["k_fit_min"] > 0)]
    return pd.concat([r[~r["es_control"]], r[r["es_control"]]]).reset_index(drop=True)


def _escenario(emp: pd.DataFrame, ta: float, t0: float, lim: float, t_ent: int,
               factor: float) -> pd.DataFrame:
    filas = []
    for _, r in emp.iterrows():
        x = esc.resumen(r["k_fit_min"], ta, t0, lim, t_ent, factor, MASA_KG, C_AGUA)
        filas.append({**r.to_dict(), **x})
    return pd.DataFrame(filas)


# --------------------------------------------------------------------------- #
# Mapa
# --------------------------------------------------------------------------- #
def _mapa(cs: pd.DataFrame, k: float, t0: float, lim: float, factor: float, t_ent: int,
          elegida: str, nombre_emp: str) -> go.Figure:
    kk = esc.k_efectiva(k, factor)
    mins = []
    for ta in cs["tmax_verano_c"]:
        m = esc.minuto_limite(kk, ta, t0, lim)
        mins.append(np.nan if m is None else m)
    mins = np.array(mins, float)
    # Escala útil para la decisión: hasta el doble del tiempo de entrega (mín. 60 min);
    # las ciudades más frías quedan en el color de «sobra tiempo».
    tope = float(max(60, 2 * t_ent))
    color = np.where(np.isnan(mins), tope, np.minimum(mins, tope))
    texto = [("nunca lo pasa" if np.isnan(m) else f"{m:.0f} min") for m in mins]
    sel = (cs["departamento"] == elegida).to_numpy()

    fig = go.Figure(go.Scattergeo(
        lat=cs["lat"], lon=cs["lon"], mode="markers",
        customdata=np.stack([cs["departamento"], cs["capital"], cs["tmax_verano_c"], texto], axis=1),
        marker=dict(size=np.where(sel, 20, 12), color=color, cmin=0, cmax=tope,
                    colorscale=[[0, "#D9533D"], [0.5, "#E8B04A"], [1, "#2F6FD6"]],
                    line=dict(color=np.where(sel, TEXTO, "#FFFFFF").tolist(), width=np.where(sel, 3, 1.2)),
                    # Barra horizontal debajo: deja todo el ancho al mapa (clave en celular).
                    colorbar=dict(title=dict(text=f"Minutos bajo {lim:.0f} °C", side="top",
                                             font=dict(size=11)),
                                  orientation="h", x=0.5, xanchor="center", y=-0.02,
                                  yanchor="top", len=0.9, thickness=10, tickfont=dict(size=10),
                                  tickvals=[0, t_ent, tope],
                                  ticktext=["0", f"{t_ent} (entrega)", f"≥ {tope:.0f}"])),
        # Al tocar una ciudad, las demás no se atenúan.
        selected=dict(marker=dict(opacity=1)), unselected=dict(marker=dict(opacity=1)),
        hovertemplate=("<b>%{customdata[0]}</b> · %{customdata[1]}<br>"
                       "Máx. del mes más cálido: %{customdata[2]:.1f} °C<br>"
                       f"{nombre_emp}: " + "%{customdata[3]}<extra></extra>"),
    ))
    fig.update_geos(
        fitbounds="locations", projection_type="mercator", resolution=50,
        showcountries=True, countrycolor="#B8C2D6", showcoastlines=True, coastlinecolor="#B8C2D6",
        showland=True, landcolor="#F2F4F8", showocean=True, oceancolor="#E6EEF8",
        showlakes=True, lakecolor="#E6EEF8", bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(height=500, margin=dict(l=0, r=0, t=0, b=70), paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Manrope, sans-serif", color=TEXTO), clickmode="event+select")
    return fig


# --------------------------------------------------------------------------- #
# Votación
# --------------------------------------------------------------------------- #
def _ganador(res: pd.DataFrame, ciudad: str, lim: float, t_ent: int) -> dict | None:
    """Empaque que mantiene la bebida bajo el límite por más tiempo (sin el control).

    Gana quien pasa el límite más tarde (o nunca); si empatan, el que llega más frío.
    """
    alt = res[~res["es_control"]]
    if alt.empty:
        return None
    # «Nunca pasa el límite» llega como None o NaN (pandas): cuenta como infinito.
    clave = alt.apply(lambda r: (-(float("inf") if pd.isna(r["minuto_limite"])
                                   else r["minuto_limite"]), r["t_entrega_c"]), axis=1)
    g = alt.loc[clave.sort_values().index[0]]
    m = g["minuto_limite"]
    cuando = (f"nunca pasa {lim:.1f} °C" if pd.isna(m)
              else "ya sale por encima del límite" if m == 0
              else f"pasa {lim:.1f} °C recién al minuto {m:.0f}")
    return {"nombre": g["empaque"],
            "titulo": f"Ganador en {ciudad}: {g['empaque']}",
            "detalle": f"Llega a {g['t_entrega_c']:.1f} °C a los {t_ent} min y {cuando}."}


def _bloque_votacion(opciones: list[str], ciudad: str, colores: dict[str, str],
                     ganador: dict | None):
    u = votacion.urna()
    # El resultado real se asocia a la ronda de esta ciudad (para revelarlo luego).
    r0 = u.foto()
    if ganador and r0.opciones and f"En {ciudad}," in r0.pregunta and r0.ganador != ganador["nombre"]:
        u.fijar_ganador(ganador["nombre"], ganador["detalle"])
    base = st.text_input(
        "Dirección de la app para el público", value=votacion.url_base(), key="sim_url",
        persist_state="session",
        help="La que abren los celulares. En la misma red WiFi usa la «Network URL» que "
             "muestra Streamlit al iniciar (p. ej. http://192.168.1.33:8501).")
    url = base.rstrip("/") + "/votar"
    c1, c2 = st.columns([1, 1.4], vertical_alignment="top")
    with c1:
        st.markdown(f'<div class="tp-qr">{votacion.qr_svg(url)}</div>', unsafe_allow_html=True)
        st.caption(f"Escanea para votar · `{url}`")
        if votacion.es_local(url):
            st.warning("Esta dirección solo funciona en esta computadora. Abre la app con la "
                       "dirección de red para que el código sirva en los celulares.")
    with c2:
        pregunta = f"En {ciudad}, ¿qué empaque mantiene la bebida bajo el límite por más tiempo?"
        a, b, c = st.columns(3)
        if a.button("Nueva votación", icon=":material/how_to_vote:", type="primary",
                    width="stretch", help="Empieza una ronda con la ciudad elegida"):
            u.nueva(pregunta, opciones)
            if ganador:
                u.fijar_ganador(ganador["nombre"], ganador["detalle"])
        r = u.foto()
        if b.button("Ocultar resultados" if r.revelada else "Mostrar resultados",
                    icon=":material/visibility:", width="stretch", disabled=not r.opciones):
            u.revelar(not r.revelada)
            st.rerun()   # para que el botón muestre su nuevo texto
        if c.button("Limpiar votación", icon=":material/delete_sweep:", width="stretch",
                    disabled=not r.opciones,
                    help="Borra la ronda y todos sus votos; los celulares vuelven a esperar"):
            u.limpiar()
            st.toast("Votación limpiada", icon=":material/delete_sweep:")
            st.rerun()

        @st.fragment(run_every=2)
        def _en_vivo():
            r = u.foto()
            if not r.opciones:
                st.caption("Pulsa «Nueva votación» para abrir la ronda.")
                return
            st.markdown(f"**Ronda {r.id}:** {e(r.pregunta)}")
            if r.revelada:
                st.markdown(votacion.barras_html(r, colores), unsafe_allow_html=True)
                st.markdown(votacion.veredicto_html(r), unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="tp-voto-total">{sum(r.votos.values())} voto(s) '
                            f'recibidos · resultados ocultos</div>', unsafe_allow_html=True)

        _en_vivo()


# --------------------------------------------------------------------------- #
# Página
# --------------------------------------------------------------------------- #
def render():
    R = estado.calcular()
    cs = ciudades()
    emp = _empaques(R)
    if emp.empty:
        st.warning("No hay empaques con una constante de calentamiento k válida en los datos.")
        return
    col = graficos.colores(R.res.sort_values("orden")["empaque"].tolist(), R.control)

    ss.setdefault("sim_ciudad", "Piura" if "Piura" in set(cs["departamento"]) else cs["departamento"].iloc[0])
    if "sim_ta" not in ss:
        _al_cambiar_ciudad()
    ss.setdefault("sim_t0", 5.0)
    ss.setdefault("sim_lim", float(R.umbral))
    ss.setdefault("sim_t", 30)
    ss.setdefault("sim_viento", list(esc.FACTORES_VIENTO)[0])

    # Ciudad elegida tocando el mapa (antes de dibujar el selector).
    if ss.get("sim_pendiente"):
        ss.sim_ciudad = ss.pop("sim_pendiente")
        _al_cambiar_ciudad()

    barra_superior("Simulador por ciudad")
    encabezado("¿Y si el delivery fuera en tu ciudad?",
               "Elige un departamento: el modelo de Newton, con la k medida de cada empaque, "
               "predice cómo llega la bebida.")
    st.write("")

    # ---------- Escenario + mapa ----------
    with st.container(key="fila_sim"):
        izq, der = st.columns([1, 1.25])
    with izq, st.container(key="card_sim_esc"):
        titulo_tarjeta("Escenario", "Ajusta lo que diga el público; todo se recalcula al instante.")
        etiquetas = {r["departamento"]: _etiqueta(r) for _, r in cs.iterrows()}
        st.selectbox("Departamento", list(etiquetas), key="sim_ciudad", persist_state="session",
                     on_change=_al_cambiar_ciudad, format_func=etiquetas.get)
        st.slider("Temperatura ambiente (°C)", 0.0, 45.0, step=0.5, key="sim_ta",
                  persist_state="session",
                  help="Toma la máxima media del mes más cálido de la ciudad (normales climáticas); "
                       "puedes cambiarla a mano.")
        a, b = st.columns(2)
        a.slider("Bebida al salir (°C)", 0.0, 15.0, step=0.5, key="sim_t0", persist_state="session")
        b.slider("Límite de calidad (°C)", 4.0, 20.0, step=0.5, key="sim_lim", persist_state="session")
        st.slider("Tiempo de entrega (min)", 5, 120, step=5, key="sim_t", persist_state="session",
                  help="Más allá de 60 min es extrapolación del modelo (el ensayo duró 60 min).")
        st.segmented_control("Viento sobre el empaque", list(esc.FACTORES_VIENTO), key="sim_viento",
                             required=True, width="stretch", persist_state="session")
        f = esc.FACTORES_VIENTO[ss.sim_viento]
        st.caption(f"U·A × {f:.1f}. Factores ilustrativos: el viento aumenta la convección "
                   "exterior; no se midieron en el ensayo.")
        fila = cs.set_index("departamento").loc[ss.sim_ciudad]
        st.caption(f"Fuente de la temperatura: {fila['nota']} · [ver fuente]({fila['fuente']})")

    ta, t0, lim, t_ent = float(ss.sim_ta), float(ss.sim_t0), float(ss.sim_lim), int(ss.sim_t)
    res = _escenario(emp, ta, t0, lim, t_ent, f)
    ganador = _ganador(res, ss.sim_ciudad, lim, t_ent)

    with der, st.container(key="card_sim_mapa"):
        nombres = res.loc[~res["es_control"], "empaque"].tolist() or res["empaque"].tolist()
        defecto = R.reco["empaque"] if R.reco is not None and R.reco["empaque"] in nombres else nombres[-1]
        if ss.get("sim_color") not in nombres:
            ss.sim_color = defecto
        titulo_tarjeta("Mapa del Perú",
                       "Minutos que el empaque mantiene la bebida bajo el límite en cada capital "
                       "(máxima media del mes más cálido). Toca una ciudad para elegirla.")
        st.selectbox("Colorear según", nombres, key="sim_color", label_visibility="collapsed",
                     persist_state="session")
        k_col = float(res.set_index("empaque").loc[ss.sim_color, "k_fit_min"])
        ev = st.plotly_chart(_mapa(cs, k_col, t0, lim, f, t_ent, ss.sim_ciudad, ss.sim_color),
                             key="sim_mapa", on_select="rerun", selection_mode="points",
                             config={"displayModeBar": False, "scrollZoom": False}, theme=None,
                             alt="Mapa del Perú con las capitales coloreadas por minutos bajo el límite")
        pts = (ev.selection or {}).get("points", []) if ev else []
        if pts:
            dep = pts[0].get("customdata", [None])[0]
            if dep and dep != ss.sim_ciudad and dep in set(cs["departamento"]):
                # El selector ya se dibujó en esta ejecución: se aplica al reiniciar.
                ss.sim_pendiente = dep
                st.rerun()

    # ---------- Resultados ----------
    st.write("")
    with st.container(key="card_sim_res"):
        titulo_tarjeta(f"Resultado en {ss.sim_ciudad} · {ta:.1f} °C · entrega de {t_ent} min",
                       "Predicción con T(t) = Tₐ + (T₀ − Tₐ)·e^(−k·t) y Q = m·c·ΔT "
                       f"(gaseosa de 600 mL). {ss.sim_viento}.")
        tabla = pd.DataFrame({
            "Empaque": res["empaque"],
            "Llega a (°C)": res["t_entrega_c"].round(2),
            "Calor absorbido (kJ)": res["q_kj"].round(2),
            f"Pasa {lim:.1f} °C en (min)": [
                ("nunca" if pd.isna(m) else "ya parte por encima" if m == 0 else f"{m:.0f}")
                for m in res["minuto_limite"]],
            "¿Llega bajo el límite?": ["✓ Sí" if c else "✗ No" for c in res["cumple"]],
            "S/ por uso": [("referencia" if ctrl else f"{c:.2f}")
                           for c, ctrl in zip(res["costo_uso"], res["es_control"])],
        })
        st.dataframe(tabla, hide_index=True, width="stretch", height=tablas.alto(len(tabla)))
        ok = res[res["cumple"] & ~res["es_control"]]
        if not ok.empty:
            mejor = ok.sort_values("costo_uso").iloc[0]
            st.markdown(f'<div class="tp-nota"><b>En {e(ss.sim_ciudad)}, la opción más barata que '
                        f'llega bajo {lim:.1f} °C es {e(mejor["empaque"])}</b>'
                        f'(S/ {mejor["costo_uso"]:.2f} por uso; llega a {mejor["t_entrega_c"]:.1f} °C).'
                        f'</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="tp-nota"><b>Ningún empaque llega bajo {lim:.1f} °C en '
                        f'{e(ss.sim_ciudad)} con {t_ent} min de entrega.</b>Prueba con un tiempo '
                        f'menor o un empaque más aislante.</div>', unsafe_allow_html=True)

        # Visor 3D con la predicción minuto a minuto.
        minutos = np.arange(0, t_ent + 1)
        muestras, qmax = [], 0.0
        for _, r in res.iterrows():
            T = esc.temperatura(minutos, r["k_min"], ta, t0)
            ua = r["k_min"] / 60.0 * MASA_KG * C_AGUA           # W/K
            q = ua * (ta - T)
            qmax = max(qmax, float(np.max(np.abs(q))))
            costo = ("Sin costo · referencia" if r["es_control"]
                     else f"S/ {r['costo_uso']:.2f} por uso" if r["costo_uso"] > 0 else "Costo sin registrar")
            muestras.append(dict(
                nombre=r["empaque"], es_control=bool(r["es_control"]), costo=costo, amb=round(ta, 2),
                temps=[round(float(v), 4) for v in T], qdot=[round(float(v), 4) for v in q],
                n=[0] * len(minutos),
                escenas={"corte": lab3d.escena(r["empaque"], r["es_control"], corte=True),
                         "completo": lab3d.escena(r["empaque"], r["es_control"], corte=False)}))
        st.iframe(visor3d.html_visor(muestras, t_ent, ESCALA_LO, ESCALA_HI, qmax,
                                     sin_lectura=f"Predicción en {ss.sim_ciudad}",
                                     ganador=ganador),
                  height="content",
                  alt=f"Predicción 3D de las botellas en {ss.sim_ciudad}, minuto a minuto")

    # ---------- Votación ----------
    st.write("")
    with st.container(key="card_sim_voto"):
        titulo_tarjeta("Votación del público",
                       "Antes de revelar el resultado, el público vota desde su celular.")
        _bloque_votacion(res.loc[~res["es_control"], "empaque"].tolist(), ss.sim_ciudad, col,
                         ganador)
