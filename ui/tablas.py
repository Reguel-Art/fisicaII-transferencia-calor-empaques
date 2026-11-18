"""Preparación de tablas para mostrarlas (sin «None» y sin filas cortadas)."""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

ALTO_FILA = 35
ENTEROS = ("Puesto", "Usos")


def _decimales(s: pd.Series) -> int:
    """4 decimales si la columna tiene valores pequeños (p. ej. k en 1/min), si no 2."""
    v = s.dropna()
    return 4 if ((v != 0) & (v.abs() < 0.1)).any() else 2


def para_mostrar(df: pd.DataFrame, texto: tuple[str, ...] = ("Puesto", "Empaque", "Estado"),
                 decimales: dict[str, int] | None = None):
    """Devuelve (tabla, column_config) con «—» en las celdas sin valor.

    st.dataframe muestra los valores faltantes como «None»; las columnas numéricas
    con huecos se pasan a texto ya formateado y alineado a la derecha. Cada columna
    usa un mismo número de decimales en todas sus filas; `decimales` lo fija por
    columna (útil en magnitudes físicas como R² = 0.9994, que con 2 decimales se
    leería 1.00).
    """
    out = df.copy()
    cfg = {}
    for c in out.columns:
        if c in texto:
            continue
        s = pd.to_numeric(out[c], errors="coerce").replace([np.inf, -np.inf], np.nan)
        d = 0 if c in ENTEROS else (decimales or {}).get(c, _decimales(s))
        if s.isna().any():
            out[c] = ["—" if pd.isna(v) else f"{v:.{d}f}" for v in s]
            cfg[c] = st.column_config.TextColumn(c, alignment="right")
        else:
            out[c] = s
            cfg[c] = st.column_config.NumberColumn(c, format=f"%.{d}f")
    return out, cfg


def alto(n_filas: int) -> int:
    """Altura que muestra todas las filas, más espacio para la barra de desplazamiento."""
    return ALTO_FILA * (n_filas + 1) + 3 + 14
