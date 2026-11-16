"""Generador de datos SIMULADOS para probar la herramienta.

IMPORTANTE: estos datos NO son mediciones reales. Se generan con el modelo de
enfriamiento newtoniano más un ruido gaussiano pequeño, solo para poder
desarrollar y demostrar la herramienta mientras se obtienen datos reales.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from core import fisica

# Empaques de ejemplo: k (1/s), precio (S/), usos estimados.
# k mayor = se calienta más rápido = peor aislamiento.
EMPAQUES_DEMO = {
    "control":    dict(k=0.00130, precio=0.00, usos=1),
    "carton":     dict(k=0.00090, precio=1.50, usos=5),
    "tecnopor":   dict(k=0.00055, precio=2.00, usos=10),
    "bolsa_term": dict(k=0.00040, precio=8.00, usos=60),
}


def generar(
    t_ambiente: float = 25.0,
    t_inicial: float = 4.0,
    tiempos_min: list[int] | None = None,
    repeticiones: int = 3,
    ruido_std: float = 0.3,
    semilla: int = 42,
) -> pd.DataFrame:
    """Genera un DataFrame simulado en el formato de entrada de la herramienta."""
    if tiempos_min is None:
        tiempos_min = [0, 10, 20, 30, 40, 50, 60]

    rng = np.random.default_rng(semilla)
    filas = []
    t_s = np.array(tiempos_min, dtype=float) * 60.0

    for empaque, cfg in EMPAQUES_DEMO.items():
        T_ideal = fisica.temperatura_modelo(t_s, cfg["k"], t_ambiente, t_inicial)
        for rep in range(1, repeticiones + 1):
            ruido = rng.normal(0.0, ruido_std, size=T_ideal.shape)
            ruido[0] = 0.0  # todas las pruebas arrancan en T_inicial
            T = T_ideal + ruido
            for tmin, temp in zip(tiempos_min, T):
                filas.append(
                    dict(
                        empaque=empaque,
                        repeticion=rep,
                        tiempo_min=tmin,
                        temp_C=round(float(temp), 2),
                    )
                )
    return pd.DataFrame(filas)


if __name__ == "__main__":
    from pathlib import Path

    df = generar()
    destino = Path(__file__).resolve().parents[1] / "data" / "ejemplo_simulado.csv"
    df.to_csv(destino, index=False)
    print(f"CSV simulado escrito en: {destino}")
    print(df.head(10).to_string(index=False))
