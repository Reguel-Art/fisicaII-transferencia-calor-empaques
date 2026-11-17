"""Evaluación de alternativas: requisito térmico + costo + preferencia.

Reglas (las mismas que muestra la pestaña «Evaluación económica»):

1. Costo por uso = precio ÷ usos + limpieza + otros costos (S/ por uso).
2. Una alternativa es VIABLE si:
     - no es el control,
     - tiene costo registrado (costo por uso > 0: precio, limpieza u otros),
     - tiene lecturas que lleguen al tiempo de entrega (no se extrapola),
     - TODAS sus lecturas hasta el tiempo de entrega están ≤ umbral
       («cumple en cada lectura», no solo el promedio). Si la entrega cae entre
       dos lecturas se incluye también la lectura siguiente, y
     - su costo por uso no supera el máximo (0 = sin límite).
3. Entre las viables se calcula un puntaje 0–100:
     puntaje = w·(conservación normalizada) + (1−w)·(costo normalizado)
   donde menor ΔT y menor costo reciben más puntos (normalización min–max
   entre las viables; si solo hay una, recibe 100).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core import costos


def costo_uso_total(precio: float, usos: int, limpieza: float = 0.0, otros: float = 0.0) -> float:
    """S/ por uso = precio/usos + limpieza + otros."""
    return costos.costo_por_uso(precio, usos) + float(limpieza) + float(otros)


def _instante_de_control(df: pd.DataFrame, empaque: str, t_max: float) -> float | None:
    """Primer instante medido ≥ t_max para el empaque (None si sus datos no llegan)."""
    tiempos = df.loc[df["empaque"] == empaque, "tiempo_min"]
    posteriores = tiempos[tiempos >= t_max - 1e-9]
    return float(posteriores.min()) if not posteriores.empty else None


def cubre_tiempo(df: pd.DataFrame, empaque: str, t_max: float) -> bool:
    """True si el empaque tiene lecturas en t_max o después (no hace falta extrapolar)."""
    return _instante_de_control(df, empaque, t_max) is not None


def cumple_en_cada_lectura(df: pd.DataFrame, empaque: str, umbral: float, t_max: float) -> bool:
    """True si todas las lecturas (todas las repeticiones) hasta la entrega están ≤ umbral.

    Se revisan las lecturas con t ≤ t*, donde t* es el primer instante medido ≥ t_max
    (si la entrega cae entre dos lecturas, la siguiente también cuenta). Si los datos
    del empaque no llegan a t_max devuelve False. `df` es el DataFrame validado.
    """
    t_ctrl = _instante_de_control(df, empaque, t_max)
    if t_ctrl is None:
        return False
    sub = df[(df["empaque"] == empaque) & (df["tiempo_min"] <= t_ctrl + 1e-9)]
    if sub.empty:
        return False
    return bool((sub["temp_C"] <= umbral + 1e-9).all())


def _normalizar_inverso(x: pd.Series) -> pd.Series:
    """Menor valor → 1, mayor → 0 (min–max). Constante → 1."""
    lo, hi = x.min(), x.max()
    if not np.isfinite(lo) or not np.isfinite(hi) or hi - lo < 1e-12:
        return pd.Series(1.0, index=x.index)
    return (hi - x) / (hi - lo)


def evaluar(
    tabla: pd.DataFrame,
    peso_conservacion: float,
    max_costo_uso: float = 0.0,
) -> pd.DataFrame:
    """Clasifica las alternativas.

    `tabla` necesita las columnas:
        empaque, es_control (bool), precio, costo_uso, delta_T, cumple_lecturas (bool)
    y opcionalmente cubre_tiempo (bool; por defecto True).

    peso_conservacion en [0, 1]. max_costo_uso = 0 → sin límite.
    Devuelve la tabla con: viable, motivo, puntaje (0–100, NaN si no viable), puesto.
    """
    t = tabla.copy()
    w = float(np.clip(peso_conservacion, 0.0, 1.0))

    if "cubre_tiempo" not in t.columns:
        t["cubre_tiempo"] = True

    motivos = []
    for _, r in t.iterrows():
        costo = r["costo_uso"]
        if r["es_control"]:
            motivos.append("Control (referencia)")
        elif pd.isna(costo) or costo <= 0:
            motivos.append("Sin costo registrado")
        elif not r["cubre_tiempo"]:
            motivos.append("Sin lecturas hasta el tiempo de entrega")
        elif pd.isna(r["delta_T"]):
            motivos.append("Datos insuficientes")
        elif not r["cumple_lecturas"]:
            motivos.append("Supera el límite en alguna lectura")
        elif max_costo_uso > 0 and r["costo_uso"] > max_costo_uso + 1e-12:
            motivos.append("Supera el costo máximo por uso")
        else:
            motivos.append("Cumple temperatura y costo")
    t["motivo"] = motivos
    t["viable"] = t["motivo"] == "Cumple temperatura y costo"

    t["puntaje"] = np.nan
    v = t[t["viable"]]
    if not v.empty:
        cons = _normalizar_inverso(v["delta_T"].astype(float))
        cost = _normalizar_inverso(v["costo_uso"].astype(float))
        t.loc[v.index, "puntaje"] = (100 * (w * cons + (1 - w) * cost)).round(1)

    # Orden: viables por puntaje; luego no viables por ΔT (mejor conservación primero).
    t["_k1"] = (~t["viable"]).astype(int)
    t["_k2"] = -t["puntaje"].fillna(-1)
    t["_k3"] = t["delta_T"].astype(float)
    t = t.sort_values(["_k1", "_k2", "_k3"]).drop(columns=["_k1", "_k2", "_k3"])
    t.insert(0, "puesto", range(1, len(t) + 1))
    return t.reset_index(drop=True)
