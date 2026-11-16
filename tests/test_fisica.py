"""Pruebas del módulo de física."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import fisica


def test_calor_sensible():
    # Agua: 0.5 kg, c=4186 J/kgK, calentándose 5 °C.
    q = fisica.calor_sensible(0.5, 4186, 5)
    assert abs(q - 10465) < 1e-6


def test_ajustar_k_recupera_valor_conocido():
    # Generamos datos SIN ruido con k conocido y comprobamos que lo recuperamos.
    k_real = 0.0008          # 1/s
    t_amb, t0 = 25.0, 4.0
    t = np.linspace(0, 3600, 20)          # 0 a 60 min
    T = fisica.temperatura_modelo(t, k_real, t_amb, t0)

    aj = fisica.ajustar_k(t, T, t_amb, t0)
    assert abs(aj.k - k_real) < 1e-6
    assert aj.r2 > 0.9999
    assert aj.n == 20


def test_conductancia_UA():
    # Tecnopor del documento: debe salir ~0.14 W/K con k, m, c típicos.
    k = 0.0008
    ua = fisica.conductancia_UA(k, 0.5, 4186)
    assert abs(ua - 1.6744) < 1e-3


def test_tiempo_a_umbral():
    k = 0.0008
    t_amb, t0, umbral = 25.0, 4.0, 10.0
    t = fisica.tiempo_a_umbral(k, t_amb, t0, umbral)
    # Verificación cruzada: evaluar el modelo en ese tiempo da el umbral.
    T = fisica.temperatura_modelo(np.array([t]), k, t_amb, t0)[0]
    assert abs(T - umbral) < 1e-6


def test_tiempo_a_umbral_inalcanzable():
    # Umbral por encima de la ambiente: nunca se alcanza.
    t = fisica.tiempo_a_umbral(0.0008, 25.0, 4.0, 30.0)
    assert t == float("inf")


def test_resistencia_y_flujo():
    # EPS (tecnopor) k=0.0425 W/mK, L=2cm, A=0.06 m².
    r = fisica.resistencia_conduccion(0.02, 0.0425, 0.06)
    assert abs(r - 7.843) < 1e-2
    q_punto = fisica.flujo_calor_conduccion(21.0, r)   # ΔT=25-4
    assert abs(q_punto - 2.677) < 1e-2


if __name__ == "__main__":
    import traceback

    fallos = 0
    for nombre, fn in sorted(globals().items()):
        if nombre.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"[OK]   {nombre}")
            except Exception:
                fallos += 1
                print(f"[FALLO] {nombre}")
                traceback.print_exc()
    print(f"\n{'Todos los tests pasaron.' if fallos == 0 else f'{fallos} test(s) fallaron.'}")
    sys.exit(1 if fallos else 0)
