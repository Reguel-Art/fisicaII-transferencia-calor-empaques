"""Votación en vivo del público durante la exposición.

Los votos se guardan en memoria del servidor (st.cache_resource), así que los ven
todas las personas conectadas a la misma app: el presentador en el proyector y el
público desde su celular (página /votar, a la que lleva el código QR).
Se pierden al reiniciar la app; es lo esperado para una demo en vivo.
"""

from __future__ import annotations

import html
import threading
import uuid
from dataclasses import dataclass, field
from urllib.parse import urlsplit

import segno
import streamlit as st


@dataclass
class Ronda:
    id: int = 0
    pregunta: str = ""
    opciones: list[str] = field(default_factory=list)
    votos: dict[str, int] = field(default_factory=dict)
    votantes: set[str] = field(default_factory=set)
    revelada: bool = False
    ganador: str = ""          # resultado real del simulador para esta ronda
    detalle: str = ""          # frase corta con el porqué (temperatura, minutos)


class Urna:
    """Estado compartido entre sesiones, protegido con un candado."""

    def __init__(self):
        self._lock = threading.Lock()
        self.ronda = Ronda()

    def nueva(self, pregunta: str, opciones: list[str]):
        with self._lock:
            self.ronda = Ronda(id=self.ronda.id + 1, pregunta=pregunta, opciones=list(opciones),
                               votos={o: 0 for o in opciones})

    def votar(self, votante: str, opcion: str) -> bool:
        """Registra un voto por persona y ronda. Devuelve False si ya había votado."""
        with self._lock:
            r = self.ronda
            if opcion not in r.votos or votante in r.votantes:
                return False
            r.votos[opcion] += 1
            r.votantes.add(votante)
            return True

    def limpiar(self):
        """Borra la ronda y sus votos. El id sigue creciendo para que ningún celular
        crea que ya votó en la ronda siguiente."""
        with self._lock:
            self.ronda = Ronda(id=self.ronda.id + 1)

    def fijar_ganador(self, nombre: str, detalle: str = ""):
        """El presentador informa el resultado real del escenario actual."""
        with self._lock:
            self.ronda.ganador, self.ronda.detalle = nombre, detalle

    def revelar(self, si: bool = True):
        with self._lock:
            self.ronda.revelada = si

    def foto(self) -> Ronda:
        """Copia del estado actual (para leer sin el candado)."""
        with self._lock:
            r = self.ronda
            return Ronda(r.id, r.pregunta, list(r.opciones), dict(r.votos), set(r.votantes),
                         r.revelada, r.ganador, r.detalle)


@st.cache_resource
def urna() -> Urna:
    return Urna()


def id_votante() -> str:
    """Identificador anónimo de esta sesión del navegador."""
    ss = st.session_state
    if "votante" not in ss:
        ss.votante = uuid.uuid4().hex
    return ss.votante


def url_base() -> str:
    """Origen de la app tal como la abrió el presentador (p. ej. http://192.168.1.33:8501)."""
    try:
        partes = urlsplit(st.context.url)
        return f"{partes.scheme}://{partes.netloc}"
    except Exception:
        return ""


def es_local(url: str) -> bool:
    host = urlsplit(url).hostname or ""
    return host in ("localhost", "127.0.0.1", "::1", "")


def qr_svg(url: str, escala: int = 5) -> str:
    """Código QR (SVG en línea) que lleva a `url`."""
    return segno.make(url, error="m").svg_inline(scale=escala, dark="#142F66", light="#FFFFFF")


def barras_html(r: Ronda, colores: dict[str, str]) -> str:
    """Resultados como barras horizontales en HTML (sin gráficos pesados)."""
    total = sum(r.votos.values())
    filas = []
    for o in r.opciones:
        n = r.votos.get(o, 0)
        pct = 100 * n / total if total else 0
        c = colores.get(o, "#5F6B85")
        trofeo = " 🏆" if r.ganador and o == r.ganador else ""
        filas.append(
            f'<div class="tp-voto"><div class="tp-voto-nom"><span>{html.escape(o)}{trofeo}</span>'
            f'<b>{n} · {pct:.0f}%</b></div>'
            f'<div class="tp-voto-barra"><i style="width:{pct:.1f}%;background:{c}"></i></div></div>')
    return "".join(filas) + f'<div class="tp-voto-total">{total} voto(s)</div>'


def veredicto_html(r: Ronda) -> str:
    """Compara el ganador real con la opción más votada por el público."""
    if not r.ganador:
        return ""
    total = sum(r.votos.values())
    gan = html.escape(r.ganador)
    det = f'<span>{html.escape(r.detalle)}</span>' if r.detalle else ""
    if total == 0:
        publico = "Todavía no hay votos."
    else:
        top = max(r.votos.values())
        mas_votadas = [o for o, n in r.votos.items() if n == top]
        pct = 100 * r.votos.get(r.ganador, 0) / total
        if r.ganador in mas_votadas and len(mas_votadas) == 1:
            publico = f"¡El público acertó! El {pct:.0f}% eligió el ganador."
        elif r.ganador in mas_votadas:
            publico = f"Empate en la votación; el {pct:.0f}% eligió el ganador."
        else:
            elegida = html.escape(mas_votadas[0])
            publico = (f"El público eligió {elegida}; nadie acertó." if pct == 0
                       else f"El público eligió {elegida}; solo el {pct:.0f}% acertó.")
    return (f'<div class="tp-ganador"><div class="tp-ganador-tit">🏆 Ganador real: <b>{gan}</b></div>'
            f'{det}<div class="tp-ganador-pub">{publico}</div></div>')
