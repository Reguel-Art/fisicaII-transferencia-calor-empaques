"""Identidad visual «TermoPack» y piezas de interfaz reutilizables."""

from __future__ import annotations

import base64
import html
from pathlib import Path

import streamlit as st

AZUL = "#1D428A"
AZUL_OSC = "#142F66"
AZUL_SUAVE = "#EAF0FA"
FONDO = "#F5F7FB"
BORDE = "#E2E7F0"
TEXTO = "#18233F"
TENUE = "#5F6B85"
NARANJA = "#F28C35"
NARANJA_OSC = "#9C4F0F"   # naranja para texto: ≥ 5.3:1 sobre blanco y sobre #FEF2E7

_LOGO = Path(__file__).resolve().parents[1] / "assets" / "logo_ucsur.png"
LOGO_B64 = base64.b64encode(_LOGO.read_bytes()).decode() if _LOGO.exists() else ""

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

html, body, .stApp, p, li, label, input, textarea, button, td, th, h1, h2, h3, h4, h5, h6,
.stMarkdown, [data-testid="stMarkdownContainer"] {{
  font-family: 'Manrope', system-ui, sans-serif;
}}
.stApp {{ background: {FONDO}; color: {TEXTO}; }}
[data-testid="stHeader"] {{ background: transparent; height: 0; }}
/* La barra de Streamlit se mantiene (allí vive el botón para abrir el menú lateral),
   pero se ocultan sus acciones de desarrollo (Deploy, menú ⋮). */
[data-testid="stToolbarActions"], [data-testid="stMainMenu"],
[data-testid="stAppDeployButton"] {{ display: none; }}
/* Botón «Menú»: abre la barra lateral cuando está plegada (siempre en celular). */
[data-testid="stExpandSidebarButton"] {{
  position: fixed; top: .7rem; left: .7rem; z-index: 1000;
  display: inline-flex; align-items: center; gap: .3rem;
  background: {AZUL}; color: #fff !important; border-radius: 10px;
  padding: .35rem .7rem .35rem .5rem; box-shadow: 0 2px 8px rgba(20,47,102,.25);
}}
[data-testid="stExpandSidebarButton"] * {{ color: #fff !important; }}
[data-testid="stExpandSidebarButton"]::after {{ content: "Menú"; font-size: .85rem; font-weight: 600; }}
/* Botón para cerrar el menú, visible sobre el fondo azul (en celular el menú se cierra con él). */
[data-testid="stSidebarCollapseButton"] button {{
  display: inline-flex; align-items: center; gap: .25rem; color: #fff !important;
  background: rgba(255,255,255,.10); border-radius: 8px; padding: .2rem .55rem;
}}
[data-testid="stSidebarCollapseButton"] button::after {{ content: "Cerrar"; font-size: .78rem; font-weight: 600; }}
@media (max-width: 768px) {{ [data-testid="stSidebarCollapseButton"] {{ display: block !important; visibility: visible !important; }} }}
.block-container {{ padding: 1.2rem 2.4rem 3rem; max-width: 1500px; }}
/* Con el menú plegado, el botón «Menú» necesita su espacio arriba. */
@media (max-width: 768px) {{ .block-container {{ padding-top: 3.6rem; }} }}

/* ---------- Barra lateral ---------- */
[data-testid="stSidebar"] {{ background: {AZUL_OSC}; border-right: none; }}
[data-testid="stSidebar"] * {{ color: #DCE4F3; }}
[data-testid="stSidebarHeader"] {{ height: 2.6rem; padding: .5rem .8rem 0; }}
[data-testid="stSidebarUserContent"] {{ padding-top: .4rem; }}
[data-testid="stSidebar"] [data-testid="stPageLink"] a {{
  border-radius: 10px; padding: .55rem .8rem; margin: .1rem 0;
}}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {{ background: rgba(255,255,255,.06); }}
[data-testid="stSidebar"] [data-testid="stPageLink"] a[aria-current="page"],
[data-testid="stSidebar"] [data-testid="stPageLink-NavLink"][aria-current="page"] {{
  background: rgba(255,255,255,.10); border: 1px solid rgba(255,255,255,.14);
  box-shadow: inset 3px 0 0 {NARANJA};
}}
[data-testid="stSidebar"] [data-testid="stPageLink"] p {{ font-size: .88rem; font-weight: 500; }}
.tp-logo {{ display:flex; align-items:center; gap:.7rem; margin:.2rem 0 1.4rem; }}
.tp-logo .marca {{ font-size:1.45rem; font-weight:800; color:#fff; letter-spacing:-.02em; line-height:1; }}
.tp-logo .lema {{ font-size:.58rem; letter-spacing:.22em; color:{NARANJA}; margin-top:.25rem; }}
.tp-lab {{ border:1px solid rgba(255,255,255,.14); border-radius:12px; padding:.75rem .85rem;
  display:flex; align-items:center; gap:.7rem; margin-bottom:1.6rem; }}
.tp-lab .ico {{ width:32px; height:32px; border-radius:8px; background:rgba(255,255,255,.08);
  display:flex; align-items:center; justify-content:center; }}
.tp-lab b {{ font-size:.8rem; color:#fff; display:block; }}
.tp-lab small {{ font-size:.68rem; color:#A9B8D6; }}
.tp-lab .punto {{ margin-left:auto; width:7px; height:7px; border-radius:50%; background:{NARANJA}; }}
.tp-seccion {{ font-size:.62rem; letter-spacing:.2em; color:#8FA3CB !important; margin:.2rem 0 .5rem .2rem; }}
.tp-tip {{ border:1px solid rgba(255,255,255,.12); background:rgba(255,255,255,.04);
  border-radius:12px; padding:1rem; margin-top:2.2rem; }}
.tp-tip b {{ color:#fff; font-size:.92rem; display:block; margin:.5rem 0 .6rem; }}
.tp-tip p {{ font-size:.75rem; color:#B5C3DE; margin:0; line-height:1.5; }}
.tp-uni {{ display:flex; gap:.7rem; align-items:center; margin-top:1.4rem; }}
.tp-uni img {{ width:40px; height:40px; border-radius:9px; flex-shrink:0;
  box-shadow: 0 0 0 1px rgba(255,255,255,.18); }}
.tp-uni b {{ font-size:.72rem; color:#fff; display:block; }}
.tp-uni small {{ font-size:.66rem; color:#A9B8D6; }}
.tp-pie {{ font-size:.62rem; letter-spacing:.16em; color:#A9B8D6 !important; text-align:center;
  margin-top:1.4rem; border-top:1px solid rgba(255,255,255,.08); padding-top:.9rem; }}

/* ---------- Barra superior y encabezado ---------- */
.tp-top {{ display:flex; justify-content:space-between; align-items:center;
  border-bottom:1px solid {BORDE}; padding:.2rem 0 .9rem; margin-bottom:1.6rem; }}
.tp-miga {{ font-size:.82rem; color:{TENUE}; }}
.tp-miga b {{ color:{TEXTO}; font-weight:500; }}
.tp-estado {{ display:flex; align-items:center; gap:1rem; font-size:.74rem; color:{AZUL}; }}
.tp-estado .dot {{ width:7px; height:7px; border-radius:50%; background:#3BAA6A; display:inline-block; margin-right:.35rem; }}
.tp-avatar {{ width:32px; height:32px; border-radius:50%; border:1px solid {BORDE}; display:flex;
  align-items:center; justify-content:center; font-size:.72rem; font-weight:700; color:{TEXTO}; background:#fff; }}
.tp-ceja {{ font-size:.64rem; letter-spacing:.18em; color:{AZUL}; font-weight:600; }}
.tp-ceja span {{ color:{TENUE}; margin-left:.9rem; padding-left:.9rem; border-left:1px solid {BORDE};
  font-size:.56rem; }}
.tp-titulo {{ font-size:clamp(1.7rem, 2.6vw, 2.35rem); font-weight:800; letter-spacing:-.035em; color:{TEXTO};
  margin:.35rem 0 .3rem; line-height:1.1; }}
.tp-titulo i {{ color:{NARANJA}; font-style:normal; }}
.tp-sub {{ font-size:.92rem; color:{TENUE}; margin-bottom:.4rem; }}

/* ---------- Tarjetas ---------- */
div[class*="st-key-card"], div[class*="st-key-reco"], div[class*="st-key-banner"] {{
  background:#fff; border:1px solid {BORDE}; border-radius:14px; padding:1.1rem 1.3rem;
}}
div[class*="st-key-reco"] {{ background: linear-gradient(160deg, #EEF3FC 0%, #E3EBF9 100%);
  border-color:#CFDCF2; }}
div[class*="st-key-banner"] {{ background:#FEF5EC; border-color:#F8DEC4; padding:.55rem 1.1rem; }}
div[class*="st-key-cardsel"] {{ border:1.5px solid #F6C08F; }}
.tp-kpi-tit {{ font-size:.8rem; color:{TENUE}; }}
.tp-kpi-nombre {{ font-size:clamp(1.05rem, 1.5vw, 1.35rem); line-height:1.25; display:block;
  overflow-wrap:normal; word-break:normal; hyphens:manual; }}
.tp-kpi-val {{ font-size:clamp(1.5rem, 2vw, 1.9rem); font-weight:700; color:{TEXTO}; letter-spacing:-.02em; margin:.55rem 0 .2rem; }}
.tp-kpi-val small {{ font-size:1rem; color:{TENUE}; font-weight:500; }}
.tp-kpi-sub {{ font-size:.72rem; color:{TENUE}; }}
.tp-kpi-sub.ok {{ color:{AZUL}; }}
.tp-kpi-head {{ display:flex; justify-content:space-between; align-items:flex-start; }}
.tp-ico {{ width:30px; height:30px; border-radius:8px; background:{AZUL_SUAVE}; display:flex;
  align-items:center; justify-content:center; font-size:15px; }}
.tp-card-tit {{ font-size:1.12rem; font-weight:700; color:{TEXTO}; }}
.tp-card-sub {{ font-size:.78rem; color:#4A6296; margin-top:.15rem; }}
.tp-ceja-sec {{ font-size:.66rem; letter-spacing:.16em; color:{TENUE}; font-weight:600; }}
.tp-ceja-sec::before {{ content:'●'; color:{AZUL}; margin-right:.5rem; font-size:.5rem; vertical-align:middle; }}
.tp-banner {{ font-size:.8rem; color:{TENUE}; }}
.tp-banner b {{ color:{TEXTO}; margin-right:.6rem; }}
.tp-chip {{ display:inline-block; font-size:.68rem; padding:.2rem .55rem; border-radius:6px;
  background:#E1E9F8; color:{AZUL}; }}
.tp-chip.no {{ background:#F6E3DF; color:#9A3B2B; }}
.tp-reco-nom {{ font-size:1.85rem; font-weight:800; color:{AZUL_OSC}; letter-spacing:-.02em; margin:.8rem 0 .5rem; }}
.tp-reco-txt {{ font-size:.86rem; color:{AZUL}; line-height:1.6; margin-bottom:.8rem; }}
.tp-pesos {{ display:flex; justify-content:space-around; text-align:center; margin:.6rem 0 .2rem; }}
.tp-pesos .n {{ font-size:2.3rem; font-weight:800; color:{AZUL}; }}
.tp-pesos .n.costo {{ color:{NARANJA_OSC}; }}
.tp-pesos .n small {{ font-size:1rem; }}
.tp-pesos .l {{ font-size:.74rem; color:#5A72A6; }}
.tp-nota {{ background:{AZUL_SUAVE}; border-radius:10px; padding:.8rem .9rem; font-size:.74rem;
  color:{AZUL}; line-height:1.55; }}
.tp-nota b {{ display:block; margin-bottom:.25rem; }}

.tp-ceja {{ border-left:3px solid {NARANJA}; padding-left:.6rem; }}

/* ---------- Distribución adaptable ----------
   Las filas principales se envuelven en contenedores «fila_*». Solo se toca su
   primer nivel de columnas (no las columnas internas de cada tarjeta). */
div[class*="st-key-fila"] > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] {{
  flex-wrap: wrap; }}
@media (max-width: 1350px) {{
  div.st-key-fila_kpis > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
    flex: 1 1 calc(50% - 1rem) !important; min-width: calc(50% - 1rem) !important; }}
  div.st-key-fila_graf > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
  div.st-key-fila_eco > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
  div.st-key-fila_form > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
  div.st-key-fila_cab > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
    flex: 1 1 100% !important; min-width: 100% !important; }}
}}
@media (max-width: 560px) {{
  div.st-key-fila_kpis > [data-testid="stLayoutWrapper"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{
    flex: 1 1 100% !important; min-width: 100% !important; }}
}}

/* ---------- Ajustes de la revisión de diseño ---------- */
/* Textos secundarios de Streamlit (st.caption) con contraste AA sobre blanco. */
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {{ color:{TENUE} !important;
  opacity:1 !important; }}
/* Rótulos en los extremos del deslizador, en una sola línea. */
.tp-extremos {{ display:flex; justify-content:space-between; gap:1rem; font-size:.8rem;
  color:{TENUE}; margin-top:-.4rem; }}
/* «Guía del experimento» no se marca como página actual (ya lo hace Fundamento físico). */
div.st-key-guia [data-testid="stPageLink"] a {{
  background: transparent !important; border-color: transparent !important; box-shadow: none !important; }}
div.st-key-guia [data-testid="stPageLink"] a:hover {{ background: rgba(255,255,255,.06) !important; }}
/* Aviso que solo hace falta en pantallas angostas. */
.tp-solo-movil {{ display:none; font-size:.78rem; color:{TENUE}; margin-top:-.3rem; }}
@media (max-width: 700px) {{ .tp-solo-movil {{ display:block; }} }}
/* Celular: la barra superior en una sola línea. */
@media (max-width: 480px) {{ .tp-estado > span {{ display:none; }} }}

/* ---------- Widgets ---------- */
.stButton button[kind="primary"], .stDownloadButton button[kind="primary"],
[data-testid="stPopover"] button[kind="primary"] {{
  background:{AZUL}; border-color:{AZUL}; color:#fff; border-radius:8px; font-weight:600;
}}
.stButton button, [data-testid="stPopover"] button, .stDownloadButton button {{ border-radius:8px; }}
[data-testid="stDataFrame"], [data-testid="stDataEditor"] {{ border-radius:10px; }}
[data-testid="stTabs"] button p {{ font-size:.85rem; }}
</style>
"""


def aplicar_css():
    st.markdown(CSS, unsafe_allow_html=True)


def e(texto) -> str:
    return html.escape(str(texto))


def barra_superior(miga: str):
    st.markdown(
        f"""<div class="tp-top">
          <div class="tp-miga">Laboratorio &nbsp;/&nbsp; <b>{e(miga)}</b></div>
          <div class="tp-estado"><span><span class="dot"></span>Motor Python activo</span>
            <div class="tp-avatar">G3</div></div>
        </div>""",
        unsafe_allow_html=True,
    )


def encabezado(titulo: str, subtitulo: str, ceja: str = "FÍSICA APLICADA AL DELIVERY",
               experimento: str = "EXPERIMENTO 01"):
    st.markdown(
        f"""<div class="tp-ceja">{e(ceja)}<span>{e(experimento)}</span></div>
        <div class="tp-titulo">{e(titulo)}<i>.</i></div>
        <div class="tp-sub">{e(subtitulo)}</div>""",
        unsafe_allow_html=True,
    )


def kpi(icono: str, titulo: str, valor_html: str, sub: str, ok: bool = False, clave: str = "card"):
    with st.container(key=clave):
        st.markdown(
            f"""<div class="tp-kpi-head"><div class="tp-kpi-tit">{e(titulo)}</div>
                 <div class="tp-ico">{icono}</div></div>
               <div class="tp-kpi-val">{valor_html}</div>
               <div class="tp-kpi-sub{' ok' if ok else ''}">{'✓ ' if ok else ''}{e(sub)}</div>""",
            unsafe_allow_html=True,
        )


def titulo_tarjeta(titulo: str, sub: str = ""):
    st.markdown(
        f'<div class="tp-card-tit">{e(titulo)}</div>'
        + (f'<div class="tp-card-sub">{e(sub)}</div>' if sub else ""),
        unsafe_allow_html=True,
    )


def barra_lateral(paginas: dict, n_lecturas: int):
    sb = st.sidebar
    sb.markdown(
        f"""<div class="tp-logo">
          <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="1.6"
               stroke-linejoin="round"><path d="M12 2 3 7v10l9 5 9-5V7z"/><path d="m3 7 9 5 9-5M12 12v10"/></svg>
          <div><div class="marca">TermoPack</div><div class="lema">CIENCIA QUE CONSERVA</div></div>
        </div>
        <div class="tp-lab"><div class="ico">⚗️</div>
          <div><b>Laboratorio de empaques</b><small>Proyecto académico · EC3</small></div>
          <div class="punto"></div></div>
        <div class="tp-seccion">ESPACIO DE TRABAJO</div>""",
        unsafe_allow_html=True,
    )
    sb.page_link(paginas["vista"], label="Vista general", icon=":material/grid_view:")
    sb.page_link(paginas["datos"], label=f"Datos del experimento · {n_lecturas}",
                 icon=":material/table_chart:")
    sb.page_link(paginas["economia"], label="Evaluación económica", icon=":material/payments:")
    sb.page_link(paginas["fisica"], label="Fundamento físico", icon=":material/science:")
    sb.markdown(
        """<div class="tp-tip"><div>💡</div><b>De la medición a la decisión.</b>
          <p>La física y los datos al servicio de un mejor delivery.</p></div>""",
        unsafe_allow_html=True,
    )
    with sb.container(key="guia"):
        st.page_link(paginas["fisica"], label="Guía del experimento  →")
    sb.markdown(
        f"""<div class="tp-uni"><img src="data:image/png;base64,{LOGO_B64}"
               alt="Logo Universidad Científica del Sur">
          <div><b>Universidad Científica del Sur</b><small>Física II · Grupo 3</small></div></div>
        <div class="tp-pie">INGENIERÍA EMPRESARIAL Y DE SISTEMAS</div>""",
        unsafe_allow_html=True,
    )
