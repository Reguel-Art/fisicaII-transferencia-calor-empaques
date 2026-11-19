"""Predicción por escenario: «¿y si el delivery fuera en otra ciudad?».

Con la constante de calentamiento k de cada empaque (ajustada con las mediciones)
se predice la temperatura del agua para OTRA temperatura ambiente con la ley de
enfriamiento de Newton:

    T(t) = Tₐ + (T₀ − Tₐ)·e^(−k·t)

Supuesto (decirlo en la exposición): la conductancia U·A del empaque no cambia
con la temperatura del ambiente; k = U·A / (m·c) se toma de los ensayos.

El viento sobre el empaque (por ejemplo, ir en moto) aumenta la convección
exterior y con ella U·A: se modela multiplicando k por un factor ≥ 1.
"""

from __future__ import annotations

import math

import numpy as np

# Factores ilustrativos de aumento de U·A por viento (NO medidos en el ensayo).
FACTORES_VIENTO = {
    "Quieto (como en el ensayo)": 1.0,
    "Caminando": 1.3,
    "En moto": 1.8,
}


def k_efectiva(k_min: float, factor_viento: float = 1.0) -> float:
    """k con el efecto del viento (1/min)."""
    if factor_viento < 1:
        raise ValueError("El factor de viento debe ser ≥ 1.")
    return float(k_min) * float(factor_viento)


def temperatura(t_min, k_min: float, t_amb: float, t0: float) -> np.ndarray:
    """T(t) = Tₐ + (T₀ − Tₐ)·e^(−k·t) para t en minutos."""
    t = np.asarray(t_min, dtype=float)
    return t_amb + (t0 - t_amb) * np.exp(-float(k_min) * t)


def calor_absorbido_kj(t_final: float, t0: float, masa_kg: float = 0.5,
                       c_j_kgk: float = 4186.0) -> float:
    """Q = m·c·(T_final − T₀) en kJ (negativo si el agua se enfría)."""
    return masa_kg * c_j_kgk * (t_final - t0) / 1000.0


def minuto_limite(k_min: float, t_amb: float, t0: float, limite: float) -> float | None:
    """Minuto en que la bebida alcanza el límite, o None si nunca lo alcanza.

        t = −ln[(Tₐ − T_lím)/(Tₐ − T₀)] / k

    Nunca lo alcanza si el ambiente no supera el límite (Tₐ ≤ T_lím). Si la
    bebida ya parte por encima del límite, el resultado es 0.
    """
    if t0 >= limite:
        return 0.0
    if t_amb <= limite or k_min <= 0:
        return None
    return float(-math.log((t_amb - limite) / (t_amb - t0)) / k_min)


def resumen(k_min: float, t_amb: float, t0: float, limite: float, t_entrega: float,
            factor_viento: float = 1.0, masa_kg: float = 0.5, c_j_kgk: float = 4186.0) -> dict:
    """Resultado de un empaque en el escenario: T de entrega, Q, minuto límite, veredicto."""
    k = k_efectiva(k_min, factor_viento)
    t_fin = float(temperatura(t_entrega, k, t_amb, t0))
    t_lim = minuto_limite(k, t_amb, t0, limite)
    return {
        "k_min": k,
        "t_entrega_c": t_fin,
        "q_kj": calor_absorbido_kj(t_fin, t0, masa_kg, c_j_kgk),
        "minuto_limite": t_lim,
        "cumple": t_fin <= limite + 1e-9,
    }
