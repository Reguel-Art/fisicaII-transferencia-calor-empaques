"""Visor 3D animado del Laboratorio (HTML + plotly.js dentro de un iframe).

Por qué no st.plotly_chart: al animar, Streamlit vuelve a montar cada gráfico en
cada paso y cada gráfico 3D abre un contexto WebGL nuevo. El navegador admite
unos 16; al superarlos borra los más antiguos y los modelos desaparecen.

Aquí cada escena se crea UNA vez y JavaScript solo actualiza el color del agua,
las flechas y los textos con Plotly.restyle, minuto a minuto, sin recargar nada.
Los datos (temperatura por minuto, flujo de calor) se calculan en Python.
"""

from __future__ import annotations

import json

from plotly.utils import PlotlyJSONEncoder

from ui.estilo import AZUL, AZUL_SUAVE, BORDE, FONDO, NARANJA, TENUE, TEXTO
from ui.lab3d import ESCALA

PLOTLY_VERSION = "4.1.1"   # la misma que trae el paquete plotly de Python
CDNS = [
    f"https://cdn.jsdelivr.net/npm/plotly.js-dist-min@{PLOTLY_VERSION}/plotly.min.js",
    f"https://unpkg.com/plotly.js-dist-min@{PLOTLY_VERSION}/plotly.min.js",
]

_PLANTILLA = r"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  :root { --azul:__AZUL__; --azul-suave:__AZUL_SUAVE__; --borde:__BORDE__; --fondo:__FONDO__;
          --naranja:__NARANJA__; --tenue:__TENUE__; --texto:__TEXTO__; }
  * { box-sizing: border-box; }
  html, body { margin:0; padding:0; background:transparent; color:var(--texto);
               font-family:'Manrope', system-ui, sans-serif; }
  button { font-family:inherit; cursor:pointer; }
  .barra { display:flex; flex-wrap:wrap; gap:.6rem; align-items:center; justify-content:space-between;
           margin-bottom:.8rem; }
  .grupo { display:inline-flex; border:1px solid var(--borde); border-radius:9px; overflow:hidden; }
  .grupo button { border:0; background:#fff; padding:.45rem .85rem; font-size:.85rem; color:var(--texto); }
  .grupo button + button { border-left:1px solid var(--borde); }
  .grupo button[aria-pressed="true"] { background:var(--azul-suave); color:var(--azul); font-weight:600; }
  .icono { border:1px solid var(--borde); background:#fff; border-radius:9px; width:38px; height:36px;
           font-size:1.05rem; color:var(--texto); }
  .tiempo { display:grid; grid-template-columns: 1fr auto auto; gap:.7rem; align-items:end;
            margin-bottom:1rem; }
  .tiempo label { display:block; font-size:.82rem; color:var(--texto); margin-bottom:.25rem; }
  .tiempo label b { color:var(--azul); }
  input[type=range] { width:100%; accent-color:var(--azul); }
  .primario { background:var(--azul); color:#fff; border:0; border-radius:9px; padding:.55rem 1.1rem;
              font-weight:600; font-size:.88rem; min-width:130px; }
  .secundario { background:#fff; color:var(--texto); border:1px solid var(--borde); border-radius:9px;
                padding:.55rem 1rem; font-size:.88rem; }
  .grid { display:grid; grid-template-columns:repeat(4, minmax(0, 1fr)); gap:.8rem; }
  @media (max-width: 1050px) { .grid { grid-template-columns:repeat(2, minmax(0, 1fr)); } }
  @media (max-width: 520px)  { .grid { grid-template-columns:1fr; }
                               .tiempo { grid-template-columns:1fr 1fr; }
                               .tiempo > div:first-child { grid-column:1 / -1; } }
  .tarjeta { border:1px solid var(--borde); border-radius:12px; background:#fff; padding:.55rem .55rem .9rem; }
  .plot { height:260px; border-radius:9px; overflow:hidden; background:#EEF2F8; }
  .nom { display:flex; align-items:center; gap:.45rem; font-weight:700; font-size:.93rem; margin:.6rem .3rem 0; }
  .nom i { width:9px; height:9px; border-radius:50%; flex-shrink:0; background:#9AA6BE; }
  .temp { font-size:1.95rem; font-weight:800; letter-spacing:-.02em; margin:.15rem .3rem 0; line-height:1.15; }
  .temp small { font-size:.92rem; font-weight:500; color:var(--tenue); }
  .sub { font-size:.74rem; color:var(--tenue); margin:0 .3rem .65rem; }
  .pie { border-top:1px solid var(--borde); padding-top:.6rem; margin:0 .3rem; display:flex;
         flex-direction:column; gap:.12rem; font-size:.76rem; color:var(--tenue); }
  .pie b { color:var(--texto); font-size:.82rem; margin-bottom:.12rem; }
  .leyenda { display:flex; flex-wrap:wrap; gap:1rem; justify-content:space-between; align-items:flex-end;
             margin-top:1rem; }
  .escala { width:min(360px, 100%); }
  .escala .tit { display:flex; justify-content:space-between; font-size:.82rem; }
  .escala .tit span { font-size:.72rem; color:var(--tenue); }
  .escala .barra-c { height:8px; border-radius:6px; margin:.45rem 0 .3rem; background:__GRADIENTE__; }
  .escala .num { display:flex; justify-content:space-between; font-size:.72rem; color:var(--tenue); }
  .flujo { text-align:right; font-size:.85rem; }
  .flujo small { display:block; font-size:.72rem; color:var(--tenue); margin-top:.2rem; }
  .flujo input { accent-color:var(--azul); width:16px; height:16px; vertical-align:-3px; margin-right:.35rem; }
  .aviso { padding:1rem; border:1px dashed var(--borde); border-radius:10px; color:var(--tenue);
           font-size:.85rem; display:none; }
  :focus-visible { outline:2px solid var(--azul); outline-offset:2px; }
</style></head>
<body>
  <div class="barra">
    <div class="grupo" role="group" aria-label="Vista del empaque">
      <button id="v-corte" aria-pressed="true">En corte</button>
      <button id="v-completo" aria-pressed="false">Completo</button>
    </div>
    <div style="display:flex; gap:.4rem">
      <button class="icono" id="z-menos" aria-label="Alejar" title="Alejar">−</button>
      <button class="icono" id="z-mas" aria-label="Acercar" title="Acercar">+</button>
      <button class="icono" id="z-reset" aria-label="Volver a la vista inicial" title="Volver a la vista inicial">↺</button>
    </div>
  </div>
  <div class="tiempo">
    <div><label for="minuto">Minuto del ensayo: <b id="lbl-min">0 min</b></label>
      <input type="range" id="minuto" min="0" max="__TMAX__" step="1" value="__T0__"></div>
    <button class="primario" id="play">▶ Reproducir</button>
    <button class="secundario" id="cero">⏮ Minuto 0</button>
  </div>
  <div class="aviso" id="aviso">No se pudo cargar el visor 3D (se necesita conexión a internet para
    descargar plotly.js). Los resultados por minuto siguen disponibles en las demás secciones.</div>
  <div class="grid" id="grid"></div>
  <div class="leyenda">
    <div class="escala"><div class="tit"><b>Temperatura del agua</b><span>Escala común · °C</span></div>
      <div class="barra-c"></div>
      <div class="num"><span>__LO__ °C</span><span>__MID__ °C</span><span>__HI__ °C</span></div></div>
    <label class="flujo"><input type="checkbox" id="flujo" checked>Mostrar flujo de calor
      <small>Flechas ilustrativas del sentido del intercambio; su largo es proporcional a
      Q̇ = U·A·(T ambiente − T agua).</small></label>
  </div>

<script>
const D = __DATOS__;
const CDNS = __CDNS__;
const ESC = D.escala, LO = D.lo, HI = D.hi;
let minuto = D.t0, vista = 'corte', zoom = 1, flujo = true, reloj = null;
const CFG = { displayModeBar: false, responsive: true };

function hex(c) { c = c.replace('#',''); return [0,2,4].map(i => parseInt(c.substr(i,2), 16)); }
function colorT(T) {
  if (T === null || isNaN(T)) return '#9AA6BE';
  let f = (HI > LO) ? (T - LO) / (HI - LO) : 0; f = Math.max(0, Math.min(1, f));
  for (let k = 0; k < ESC.length - 1; k++) {
    const [f0, c0] = ESC[k], [f1, c1] = ESC[k + 1];
    if (f <= f1) { const u = (f - f0) / (f1 - f0), a = hex(c0), b = hex(c1);
      return '#' + a.map((v, i) => Math.round(v * (1 - u) + b[i] * u).toString(16).padStart(2, '0')).join(''); }
  }
  return ESC[ESC.length - 1][1];
}
function fmt(v, d) { return (v === null || isNaN(v)) ? '—' : v.toFixed(d); }

// ---- Tarjetas (texto con textContent: los nombres vienen de los datos) ----
const grid = document.getElementById('grid');
D.muestras.forEach((m, i) => {
  const t = document.createElement('div'); t.className = 'tarjeta';
  t.innerHTML = `<div class="plot" id="p${i}" role="img"></div>
    <div class="nom"><i id="dot${i}"></i><span id="nom${i}"></span></div>
    <div class="temp"><span id="t${i}">—</span><small> °C</small></div>
    <div class="sub" id="s${i}"></div>
    <div class="pie"><b id="c${i}"></b><span id="a${i}"></span><span id="q${i}"></span></div>`;
  grid.appendChild(t);
  document.getElementById('nom' + i).textContent = m.nombre;
  document.getElementById('c' + i).textContent = m.costo;
  document.getElementById('a' + i).textContent = 'Ambiente · ' + m.amb.toFixed(2) + ' °C';
  document.getElementById('p' + i).setAttribute('aria-label', 'Modelo 3D de la botella en ' + m.nombre);
});

// ---- Escenas: se crean una vez; luego solo se actualizan trazos ----
function camara() { return { eye: { x: 0, y: -1.55 / zoom, z: 0.5 / zoom }, center: { x: 0, y: 0, z: -0.08 } }; }
function dibujar() {
  D.muestras.forEach((m, i) => {
    const e = m.escenas[vista];
    const layout = JSON.parse(JSON.stringify(e.layout)); layout.scene.camera = camara();
    Plotly.react('p' + i, JSON.parse(JSON.stringify(e.data)), layout, CFG).then(() => aplicar(i));
  });
}
function aplicar(i) {
  const m = D.muestras[i], e = m.escenas[vista], T = m.temps[minuto], q = m.qdot[minuto];
  const c = colorT(T), div = 'p' + i;
  Plotly.restyle(div, { color: e.agua.map(() => c) }, e.agua);
  const esc = (flujo && q !== null && D.qmax > 0) ? Math.max(0, q / D.qmax) : 0;
  const largo = 0.25 + 0.35 * esc, z = 0.75, vis = esc > 0.02;
  const [l1, c1, l2, c2] = e.flechas, xs = [], xc = [], uc = [];
  [-1, 1].forEach(s => { const x0 = s * 1.65, x1 = s * (1.65 - largo); xs.push([x0, x1]); xc.push([x1]); uc.push([-s * 0.2]); });
  Plotly.restyle(div, { x: xs, visible: [vis, vis] }, [l1, l2]);
  Plotly.restyle(div, { x: xc, u: uc, visible: [vis, vis] }, [c1, c2]);
  document.getElementById('dot' + i).style.background = c;
  document.getElementById('t' + i).textContent = fmt(T, 2);
  const n = m.n[minuto];
  document.getElementById('s' + i).textContent = (T === null) ? 'Sin lecturas en este minuto'
    : (n > 0 ? `Media de lecturas · n = ${n} · minuto ${minuto}`
             : `Interpolado entre lecturas · minuto ${minuto}`);
  document.getElementById('q' + i).textContent = 'Calor hacia el agua · ' + (q === null ? '—' : q.toFixed(2) + ' W');
}
function irA(m) {
  minuto = Math.max(0, Math.min(D.tmax, m));
  document.getElementById('minuto').value = minuto;
  document.getElementById('lbl-min').textContent = minuto + ' min';
  D.muestras.forEach((_, i) => aplicar(i));
}

// ---- Controles ----
function pausar() { clearInterval(reloj); reloj = null; document.getElementById('play').textContent = '▶ Reproducir'; }
document.getElementById('play').onclick = () => {
  if (reloj) { pausar(); return; }
  if (minuto >= D.tmax) irA(0);
  document.getElementById('play').textContent = '⏸ Pausar';
  reloj = setInterval(() => { if (minuto >= D.tmax) { pausar(); return; } irA(minuto + 1); }, D.ms);
};
document.getElementById('cero').onclick = () => { pausar(); irA(0); };
document.getElementById('minuto').oninput = (ev) => { pausar(); irA(parseInt(ev.target.value, 10)); };
document.getElementById('flujo').onchange = (ev) => { flujo = ev.target.checked; D.muestras.forEach((_, i) => aplicar(i)); };
function ponerVista(v) {
  vista = v;
  document.getElementById('v-corte').setAttribute('aria-pressed', v === 'corte');
  document.getElementById('v-completo').setAttribute('aria-pressed', v === 'completo');
  dibujar();
}
document.getElementById('v-corte').onclick = () => ponerVista('corte');
document.getElementById('v-completo').onclick = () => ponerVista('completo');
function ponerZoom(z) { zoom = Math.max(0.6, Math.min(1.8, z));
  D.muestras.forEach((_, i) => Plotly.relayout('p' + i, { 'scene.camera': camara() })); }
document.getElementById('z-menos').onclick = () => ponerZoom(zoom - 0.15);
document.getElementById('z-mas').onclick = () => ponerZoom(zoom + 0.15);
document.getElementById('z-reset').onclick = () => { zoom = 1; ponerZoom(1); };

// ---- Carga de plotly.js (con un CDN de respaldo) ----
function cargar(k) {
  if (k >= CDNS.length) { document.getElementById('aviso').style.display = 'block'; return; }
  const s = document.createElement('script'); s.src = CDNS[k];
  s.onload = () => { dibujar(); irA(minuto); };
  s.onerror = () => cargar(k + 1);
  document.head.appendChild(s);
}
cargar(0);
</script></body></html>"""


def html_visor(muestras: list[dict], tmax: int, lo: float, hi: float, qmax: float,
               t0: int = 0, ms_por_minuto: int = 250) -> str:
    """HTML autocontenido del visor.

    Cada muestra: nombre, costo (texto), amb (°C), temps[min], qdot[min], n[min]
    y escenas {"corte": ..., "completo": ...} (de ui.lab3d.escena).
    """
    datos = {"muestras": muestras, "tmax": int(tmax), "lo": lo, "hi": hi, "qmax": qmax,
             "t0": int(t0), "ms": int(ms_por_minuto), "escala": [[f, c] for f, c in ESCALA]}
    gradiente = "linear-gradient(90deg, " + ", ".join(f"{c} {f * 100:.0f}%" for f, c in ESCALA) + ")"
    reemplazos = {
        "__AZUL__": AZUL, "__AZUL_SUAVE__": AZUL_SUAVE, "__BORDE__": BORDE, "__FONDO__": FONDO,
        "__NARANJA__": NARANJA, "__TENUE__": TENUE, "__TEXTO__": TEXTO, "__GRADIENTE__": gradiente,
        "__TMAX__": str(int(tmax)), "__T0__": str(int(t0)),
        "__LO__": f"{lo:g}", "__MID__": f"{(lo + hi) / 2:g}", "__HI__": f"{hi:g}",
        "__CDNS__": json.dumps(CDNS),
        # «</» escapado para que un nombre con «</script>» no cierre la etiqueta.
        "__DATOS__": json.dumps(datos, cls=PlotlyJSONEncoder, ensure_ascii=False).replace("</", "<\\/"),
    }
    html = _PLANTILLA
    for k, v in reemplazos.items():
        html = html.replace(k, v)
    return html
