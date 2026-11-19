"""Modelos 3D (Plotly) de la botella de 500 mL dentro de cada empaque.

Cada muestra se dibuja a la MISMA escala (mismos rangos de ejes), así las cuatro
se comparan a simple vista. El agua se colorea con su temperatura en el minuto
elegido (escala común) y unas flechas ilustran el calor que entra desde el
ambiente: su largo es proporcional al flujo Q̇ = U·A·(T_amb − T).
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from ui.estilo import AZUL, NARANJA

# Escala de color del agua: frío (azul) → tibio (ámbar) → caliente (rojo).
# Con un paso por celeste para que la mezcla azul → ámbar no pase por gris.
ESCALA = [(0.0, "#2F6FD6"), (0.35, "#4FB6D8"), (0.62, "#E8B04A"), (1.0, "#D9533D")]
FONDO_ESCENA = "#EEF2F8"
CONTORNO = "#2B3550"

# Rango fijo de la escena: igual en las cuatro muestras.
RX, RY, RZ = (-1.75, 1.75), (-1.75, 1.75), (0.0, 2.7)


# --------------------------------------------------------------------------- #
# Color
# --------------------------------------------------------------------------- #
def _hex(c: str) -> np.ndarray:
    c = c.lstrip("#")
    return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], float)


def color_temperatura(T: float, lo: float, hi: float) -> str:
    """Color de la escala común para la temperatura T (°C)."""
    if T is None or np.isnan(T):
        return "#9AA6BE"
    f = float(np.clip((T - lo) / (hi - lo) if hi > lo else 0.0, 0, 1))
    for (f0, c0), (f1, c1) in zip(ESCALA, ESCALA[1:]):
        if f <= f1:
            u = (f - f0) / (f1 - f0)
            rgb = _hex(c0) * (1 - u) + _hex(c1) * u
            return "#%02X%02X%02X" % tuple(int(round(v)) for v in rgb)
    return ESCALA[-1][1]


def gradiente_css(lo: float, hi: float) -> str:
    return "linear-gradient(90deg, " + ", ".join(f"{c} {f * 100:.0f}%" for f, c in ESCALA) + ")"


# --------------------------------------------------------------------------- #
# Primitivas
# --------------------------------------------------------------------------- #
_LUZ = dict(ambient=0.55, diffuse=0.75, specular=0.18, roughness=0.65, fresnel=0.1)
_POS_LUZ = dict(x=-120, y=-200, z=260)


def _malla(x, y, z, i, j, k, color, opacidad=1.0, nombre="") -> go.Mesh3d:
    return go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, color=color, opacity=opacidad,
                     flatshading=False, lighting=_LUZ, lightposition=_POS_LUZ,
                     hoverinfo="skip", name=nombre, showscale=False)


def cilindro(r: float, z0: float, z1: float, color: str, n: int = 40, r1: float | None = None,
             opacidad: float = 1.0, cx: float = 0.0, cy: float = 0.0) -> go.Mesh3d:
    """Cilindro (o tronco de cono si r1 ≠ r) con tapas, eje vertical."""
    r1 = r if r1 is None else r1
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    xs = np.concatenate([cx + r * np.cos(t), cx + r1 * np.cos(t), [cx, cx]])
    ys = np.concatenate([cy + r * np.sin(t), cy + r1 * np.sin(t), [cy, cy]])
    zs = np.concatenate([np.full(n, z0), np.full(n, z1), [z0, z1]])
    I, J, K = [], [], []
    for a in range(n):
        b = (a + 1) % n
        I += [a, b]; J += [b, n + b]; K += [n + a, n + a]           # lado
        I += [2 * n, 2 * n + 1]; J += [b, n + a]; K += [a, n + b]  # tapas
    return _malla(xs, ys, zs, I, J, K, color, opacidad)


def caja(cx, cy, z0, w, d, h, color, opacidad=1.0, sin_frente=False, sin_tapa=True) -> go.Mesh3d:
    """Caja de caras planas; sin_frente quita la cara de adelante (y = cy − d/2)."""
    x0, x1, y0, y1, z1 = cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2, z0 + h
    v = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                  [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]])
    caras = {"abajo": [(0, 1, 2), (0, 2, 3)], "atras": [(3, 2, 6), (3, 6, 7)],
             "izq": [(0, 3, 7), (0, 7, 4)], "der": [(1, 2, 6), (1, 6, 5)],
             "frente": [(0, 1, 5), (0, 5, 4)], "arriba": [(4, 5, 6), (4, 6, 7)]}
    usar = [c for c in caras if not (sin_frente and c == "frente") and not (sin_tapa and c == "arriba")]
    tri = [t for c in usar for t in caras[c]]
    i, j, k = zip(*tri)
    return _malla(v[:, 0], v[:, 1], v[:, 2], i, j, k, color, opacidad)


def aristas(cx, cy, z0, w, d, h, color=CONTORNO, ancho=3, sin_frente=False) -> go.Scatter3d:
    """Contorno de la caja (aspecto de ilustración)."""
    x0, x1, y0, y1, z1 = cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2, z0 + h
    seg = [((x0, y1, z0), (x1, y1, z0)), ((x0, y1, z0), (x0, y1, z1)), ((x1, y1, z0), (x1, y1, z1)),
           ((x0, y1, z1), (x1, y1, z1)), ((x0, y0, z0), (x0, y1, z0)), ((x1, y0, z0), (x1, y1, z0)),
           ((x0, y0, z1), (x0, y1, z1)), ((x1, y0, z1), (x1, y1, z1)), ((x0, y0, z0), (x1, y0, z0)),
           ((x0, y0, z0), (x0, y0, z1)), ((x1, y0, z0), (x1, y0, z1))]
    if not sin_frente:
        seg.append(((x0, y0, z1), (x1, y0, z1)))
    xs, ys, zs = [], [], []
    for a, b in seg:
        xs += [a[0], b[0], None]; ys += [a[1], b[1], None]; zs += [a[2], b[2], None]
    return go.Scatter3d(x=xs, y=ys, z=zs, mode="lines", line=dict(color=color, width=ancho),
                        hoverinfo="skip", showlegend=False)


# --------------------------------------------------------------------------- #
# Botella y empaques
# --------------------------------------------------------------------------- #
def botella(color_agua: str, z0: float = 0.12) -> list:
    """Botella de 500 mL: cuerpo con agua, hombro, cuello y tapa."""
    return [
        cilindro(0.30, z0, z0 + 1.05, color_agua),
        cilindro(0.30, z0 + 1.05, z0 + 1.30, color_agua, r1=0.13),
        cilindro(0.13, z0 + 1.30, z0 + 1.42, "#C9D4E6", opacidad=0.9),
        cilindro(0.15, z0 + 1.42, z0 + 1.56, "#24584A"),
    ]


def tipo_empaque(nombre: str, es_control: bool) -> str:
    n = nombre.lower()
    if es_control or "sin empaque" in n or "control" in n:
        return "ninguno"
    if "bolsa" in n:
        return "bolsa"
    if "eps" in n or "tecnopor" in n or "aislante" in n or "poliestireno" in n:
        return "eps"
    if "cart" in n or "caja" in n:
        return "carton"
    return "generico"


def empaque(tipo: str, corte: bool) -> list:
    """Trazos del empaque. En corte se quita la cara de adelante para ver la botella."""
    if tipo == "ninguno":
        return []
    if tipo == "carton":
        w, d, h, col = 1.15, 1.0, 1.75, "#B07A45"
        return [caja(0, 0, 0.1, w, d, h, col, opacidad=1.0, sin_frente=corte, sin_tapa=corte),
                aristas(0, 0, 0.1, w, d, h, "#6E4A26", 3, sin_frente=corte)]
    if tipo == "bolsa":
        w, d, h, col = 1.2, 0.95, 1.65, "#A7AEB6"
        tr = [caja(0, 0, 0.1, w, d, h, col, opacidad=0.85 if corte else 1.0,
                   sin_frente=corte, sin_tapa=True),
              aristas(0, 0, 0.1, w, d, h, CONTORNO, 4, sin_frente=corte)]
        # Asa: semicírculo sobre la bolsa.
        t = np.linspace(0, np.pi, 30)
        tr.append(go.Scatter3d(x=0.38 * np.cos(t), y=np.zeros_like(t), z=1.75 + 0.42 * np.sin(t),
                               mode="lines", line=dict(color=CONTORNO, width=7),
                               hoverinfo="skip", showlegend=False))
        return tr
    if tipo == "eps":
        w, d, h, col = 1.3, 1.15, 1.8, "#ECE8DC"
        tr = [caja(0, 0, 0.1, w, d, h, col, sin_frente=corte, sin_tapa=corte),
              aristas(0, 0, 0.1, w, d, h, "#A9A493", 3, sin_frente=corte)]
        if corte:   # pared gruesa: se ve el espesor del tecnopor en el corte
            tr.append(caja(0, -d / 2 + 0.09, 0.1, w, 0.18, 0.12, col))
        return tr
    w, d, h = 1.15, 1.0, 1.7
    return [caja(0, 0, 0.1, w, d, h, "#C8CFDB", sin_frente=corte, sin_tapa=corte),
            aristas(0, 0, 0.1, w, d, h, CONTORNO, 3, sin_frente=corte)]


def flechas(escala: float, z: float = 0.75) -> list:
    """Flechas ilustrativas del calor que entra (desde ambos lados)."""
    if escala <= 0:
        return []
    largo = 0.25 + 0.35 * escala
    tr = []
    for s in (-1, 1):
        x_ini, x_fin = s * 1.65, s * (1.65 - largo)
        tr.append(go.Scatter3d(x=[x_ini, x_fin], y=[0, 0], z=[z, z], mode="lines",
                               line=dict(color=NARANJA, width=6), hoverinfo="skip",
                               showlegend=False))
        tr.append(go.Cone(x=[x_fin], y=[0], z=[z], u=[-s * 0.2], v=[0], w=[0],
                          sizemode="absolute", sizeref=0.22, anchor="tail",
                          colorscale=[[0, NARANJA], [1, NARANJA]], showscale=False,
                          hoverinfo="skip"))
    return tr


def figura_muestra(nombre: str, es_control: bool, T: float, lo: float, hi: float,
                   corte: bool, ver_flujo: bool, flujo_rel: float, zoom: float,
                   revision: int) -> go.Figure:
    """Escena 3D de una muestra a escala común."""
    tipo = tipo_empaque(nombre, es_control)
    trazos = [cilindro(1.25, 0.0, 0.1, "#D3DBE8")]                    # base
    trazos += botella(color_temperatura(T, lo, hi))
    trazos += empaque(tipo, corte)
    if ver_flujo:
        trazos += flechas(flujo_rel)

    fig = go.Figure(trazos)
    d = 1.55 / max(zoom, 0.3)
    fig.update_layout(
        height=290, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
        # uirevision conserva el giro del usuario entre actualizaciones (minuto, corte).
        uirevision=f"lab-{revision}-{zoom}",
        scene=dict(
            xaxis=dict(visible=False, range=list(RX)), yaxis=dict(visible=False, range=list(RY)),
            zaxis=dict(visible=False, range=list(RZ)),
            aspectmode="manual", aspectratio=dict(x=1, y=1, z=0.78),
            bgcolor=FONDO_ESCENA, dragmode="turntable",
            camera=dict(eye=dict(x=0.0, y=-d, z=0.32 * d),
                        center=dict(x=0, y=0, z=-0.08)),
        ),
    )
    return fig


__all__ = ["color_temperatura", "gradiente_css", "figura_muestra", "tipo_empaque", "AZUL"]
