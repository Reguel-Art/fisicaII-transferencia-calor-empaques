"""Modelo físico de enfriamiento/calentamiento de bebidas en empaques térmicos.

Modelo de enfriamiento newtoniano (ley de enfriamiento de Newton):

    T(t) = T_amb + (T0 - T_amb) * exp(-k * t)

De donde, linealizando:

    ln[(T_amb - T) / (T_amb - T0)] = -k * t        (bebida fría calentándose)

La constante k (1/s) se obtiene por regresión lineal. A partir de ella:

    U * A = k * m * c        [W/K]     (conductancia térmica global)

y el calor sensible absorbido entre dos temperaturas:

    Q = m * c * (T_final - T_inicial)    [J]

Convención de signos: trabajamos con bebidas FRÍAS que se calientan, por lo
que T_amb > T. El argumento del logaritmo (T_amb - T)/(T_amb - T0) está en (0, 1].
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class AjusteK:
    """Resultado del ajuste de la constante de calentamiento k."""

    k: float          # constante [1/s]
    r2: float         # bondad del ajuste (coef. de determinación)
    n: int            # número de puntos usados

    @property
    def k_por_min(self) -> float:
        """k expresada en 1/min (útil para interpretación rápida)."""
        return self.k * 60.0


def calor_sensible(masa: float, c: float, delta_T: float) -> float:
    """Calor sensible Q = m·c·ΔT en joules.

    masa en kg, c en J/(kg·K), delta_T en K (o °C, es la misma diferencia).
    """
    return masa * c * delta_T


def ajustar_k(
    tiempo_s: np.ndarray,
    temp_C: np.ndarray,
    t_ambiente: float,
    t_inicial: float | None = None,
) -> AjusteK:
    """Ajusta k por regresión lineal del modelo de enfriamiento newtoniano.

    Parameters
    ----------
    tiempo_s : array de tiempos en SEGUNDOS.
    temp_C   : array de temperaturas medidas en °C (misma longitud que tiempo_s).
    t_ambiente : temperatura ambiente en °C.
    t_inicial  : T0 en °C. Si es None, se usa la primera temperatura medida.

    Returns
    -------
    AjusteK con k en 1/s, R² y número de puntos.
    """
    tiempo_s = np.asarray(tiempo_s, dtype=float)
    temp_C = np.asarray(temp_C, dtype=float)

    if tiempo_s.shape != temp_C.shape:
        raise ValueError("tiempo_s y temp_C deben tener la misma longitud.")
    if tiempo_s.size < 2:
        raise ValueError("Se necesitan al menos 2 puntos para ajustar k.")

    T0 = temp_C[0] if t_inicial is None else t_inicial

    # Argumento del logaritmo: debe ser positivo para todos los puntos.
    razon = (t_ambiente - temp_C) / (t_ambiente - T0)
    if np.any(razon <= 0):
        raise ValueError(
            "Hay temperaturas que igualan o superan la ambiente "
            "(ln no definido). Revisa los datos o T_ambiente."
        )

    y = np.log(razon)            # y = -k * t
    # Regresión lineal y = a*t + b; esperamos b≈0 y pendiente a = -k.
    a, b = np.polyfit(tiempo_s, y, 1)
    k = -a

    # Coeficiente de determinación R².
    y_pred = a * tiempo_s + b
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0

    return AjusteK(k=float(k), r2=float(r2), n=int(tiempo_s.size))


def conductancia_UA(k: float, masa: float, c: float) -> float:
    """Conductancia térmica global U·A = k·m·c en W/K.

    k en 1/s, masa en kg, c en J/(kg·K)  ->  resultado en W/K.
    """
    return k * masa * c


def tiempo_a_umbral(
    k: float,
    t_ambiente: float,
    t_inicial: float,
    t_umbral: float,
) -> float:
    """Tiempo (en segundos) que tarda la bebida en alcanzar t_umbral.

        t = -ln[(T_amb - T_umbral) / (T_amb - T0)] / k

    Devuelve np.inf si el umbral nunca se alcanza con el modelo
    (p. ej. umbral >= ambiente) y lanza error si k <= 0.
    """
    if k <= 0:
        raise ValueError("k debe ser positivo.")
    num = t_ambiente - t_umbral
    den = t_ambiente - t_inicial
    if den <= 0:
        raise ValueError("T_inicial debe ser menor que T_ambiente.")
    if num <= 0:
        # El umbral es mayor o igual que la ambiente: nunca se alcanza.
        return float("inf")
    return float(-np.log(num / den) / k)


def resistencia_conduccion(espesor_m: float, k_material: float, area_m2: float) -> float:
    """Resistencia térmica por conducción R = L / (k·A) en K/W.

    espesor_m (L) en m, k_material en W/(m·K), area_m2 (A) en m².
    """
    return espesor_m / (k_material * area_m2)


def flujo_calor_conduccion(delta_T: float, resistencia: float) -> float:
    """Flujo de calor por conducción Q̇ = ΔT / R en watts."""
    return delta_T / resistencia


def temperatura_modelo(
    tiempo_s: np.ndarray,
    k: float,
    t_ambiente: float,
    t_inicial: float,
) -> np.ndarray:
    """Curva teórica T(t) = T_amb + (T0 - T_amb)·exp(-k·t)."""
    tiempo_s = np.asarray(tiempo_s, dtype=float)
    return t_ambiente + (t_inicial - t_ambiente) * np.exp(-k * tiempo_s)
