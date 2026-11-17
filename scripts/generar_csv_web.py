"""Genera data/Grupo_3_Datos_Termicos_Web.csv con el MISMO escenario del informe.

Reproduce exactamente la simulación de analisis_empaques.py (Anexo C del
informe EC3): misma semilla, mismas constantes de calentamiento y mismas
repeticiones (T0 ≈ 5 °C, T ambiente ≈ 27 °C, lecturas cada 5 min durante 60 min).
Así, los promedios del CSV coinciden con las tablas 7, 8, B1 y B2 del informe.

Precios (S/) iguales a la tabla 9 del informe: cartón 1,80; bolsa térmica 25,00;
tecnopor (EPS) 6,50. Los usos (1, 60, 10) se fijan en la barra lateral de la app.

IMPORTANTE: son datos SIMULADOS, no mediciones. Reemplazar por lecturas reales.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "data" / "Grupo_3_Datos_Termicos_Web.csv"

# --- Escenario idéntico al script del informe (no cambiar sin actualizar el informe) ---
RNG = np.random.default_rng(20261112)
TIEMPOS = np.arange(0, 61, 5)
REPS = [
    {"Tamb": 26.8, "T0": 4.9, "mult": 0.970},
    {"Tamb": 27.1, "T0": 5.1, "mult": 1.018},
    {"Tamb": 27.0, "T0": 5.0, "mult": 1.012},
]

# código, nombre en la app, k del informe [1/min], precio S/, k material W/(m·K), espesor mm
EMPAQUES = [
    ("CTRL", "Control (Sin empaque)",     0.0155, 0.00, 0.026, 0.0),
    ("CART", "Caja de Cartón",            0.0099, 1.80, 0.065, 3.0),
    ("BOLS", "Bolsa Térmica Aluminizada", 0.0062, 25.00, 0.045, 5.0),
    ("EPS",  "Recipiente Aislante (EPS)", 0.0041, 6.50, 0.038, 15.0),
]

MASA_KG = 0.5
C_AGUA = 4186
AREA_M2 = 0.04
UMBRAL_C = 10.0


def serie(rep: dict, k: float) -> list[float]:
    """Misma lógica que generar() del informe (incluye el orden de llamadas al RNG)."""
    temps: list[float] = []
    for t in TIEMPOS:
        if t == 0:
            tm = rep["T0"]
        else:
            tm = rep["Tamb"] - (rep["Tamb"] - rep["T0"]) * math.exp(-k * rep["mult"] * t)
            tm += RNG.normal(0, 0.055)
        tm = round(tm, 1)
        if temps and tm < temps[-1]:
            tm = temps[-1]
        temps.append(tm)
    return temps


def main() -> None:
    # El informe recorre repeticiones (fuera) y empaques (dentro): se respeta ese
    # orden para consumir el RNG igual y obtener las mismas cifras.
    series: dict[tuple[str, int], list[float]] = {}
    for j, rep in enumerate(REPS, 1):
        for cod, _, k, *_ in EMPAQUES:
            series[(cod, j)] = serie(rep, k)

    filas = []
    for cod, nombre, _, precio, k_mat, esp in EMPAQUES:
        for j, rep in enumerate(REPS, 1):
            temps = series[(cod, j)]
            for t, temp in zip(TIEMPOS, temps):
                filas.append({
                    "id_registro": len(filas) + 1,
                    "codigo_empaque": cod,
                    "empaque": nombre,
                    "repeticion": j,
                    "tiempo_min": int(t),
                    "temp_agua_c": temp,
                    "temp_ambiente_c": rep["Tamb"],
                    "delta_t_c": round(temp - temps[0], 1),
                    "costo_empaque_pen": precio,
                    "conductividad_k_wmk": k_mat,
                    "espesor_pared_mm": esp,
                    "masa_agua_kg": MASA_KG,
                    "calor_especifico_j_kgk": C_AGUA,
                    "area_superficial_m2": AREA_M2,
                    "umbral_calidad_c": UMBRAL_C,
                    "estado_calidad": "Optimo" if temp <= UMBRAL_C else "Fuera de Rango",
                    "tipo_dato": "Simulacion_Informe_EC3_No_Experimental",
                })

    with DESTINO.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)
    print(f"{len(filas)} registros escritos en {DESTINO}")


if __name__ == "__main__":
    main()
