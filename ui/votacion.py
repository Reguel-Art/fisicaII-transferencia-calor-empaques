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

    def revelar(self, si: bool = True):
        with self._lock:
            self.ronda.revelada = si

    def foto(self) -> Ronda:
        """Copia del estado actual (para leer sin el candado)."""
        with self._lock:
            r = self.ronda
            return Ronda(r.id, r.pregunta, list(r.opciones), dict(r.votos), set(r.votantes),
                         r.revelada)


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
        filas.append(
            f'<div class="tp-voto"><div class="tp-voto-nom"><span>{html.escape(o)}</span>'
            f'<b>{n} · {pct:.0f}%</b></div>'
            f'<div class="tp-voto-barra"><i style="width:{pct:.1f}%;background:{c}"></i></div></div>')
    return "".join(filas) + f'<div class="tp-voto-total">{total} voto(s)</div>'
