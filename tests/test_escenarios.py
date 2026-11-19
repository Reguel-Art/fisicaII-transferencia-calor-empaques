"""Pruebas del simulador por ciudad (core/escenarios.py)."""

import math
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import escenarios as esc  # noqa: E402

K_EPS = 0.00411   # 1/min, ajuste del informe


def test_reproduce_el_ensayo():
    # Con el mismo ambiente del ensayo (≈ 27 °C) se recupera T60 ≈ 9.8 °C del EPS.
    t60 = float(esc.temperatura(60, K_EPS, 26.97, 5.0))
    assert abs(t60 - 9.83) < 0.1


def test_mas_calor_en_ciudad_calida():
    frio = esc.resumen(K_EPS, 15.0, 5.0, 10.0, 60)
    calido = esc.resumen(K_EPS, 32.0, 5.0, 10.0, 60)
    assert calido["t_entrega_c"] > frio["t_entrega_c"]
    assert calido["q_kj"] > frio["q_kj"] > 0


def test_minuto_limite_formula():
    t = esc.minuto_limite(K_EPS, 26.97, 5.0, 10.0)
    assert abs(t - (-math.log((26.97 - 10) / (26.97 - 5)) / K_EPS)) < 1e-9
    assert abs(float(esc.temperatura(t, K_EPS, 26.97, 5.0)) - 10.0) < 1e-9


def test_ambiente_bajo_el_limite_nunca_lo_alcanza():
    assert esc.minuto_limite(K_EPS, 9.0, 5.0, 10.0) is None
    r = esc.resumen(K_EPS, 9.0, 5.0, 10.0, 600)
    assert r["cumple"] and r["minuto_limite"] is None


def test_ambiente_mas_frio_que_la_bebida_la_enfria():
    r = esc.resumen(K_EPS, 2.0, 5.0, 10.0, 60)
    assert r["t_entrega_c"] < 5.0 and r["q_kj"] < 0


def test_viento_acelera_el_calentamiento():
    quieto = esc.resumen(K_EPS, 30.0, 5.0, 10.0, 60, factor_viento=1.0)
    moto = esc.resumen(K_EPS, 30.0, 5.0, 10.0, 60, factor_viento=1.8)
    assert moto["t_entrega_c"] > quieto["t_entrega_c"]
    assert moto["minuto_limite"] < quieto["minuto_limite"]
    try:
        esc.k_efectiva(K_EPS, 0.5)
        assert False, "debía rechazar factores < 1"
    except ValueError:
        pass


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
    print(f"\n{fallos} test(s) fallaron." if fallos else "\nTodos los tests pasaron.")
    sys.exit(1 if fallos else 0)
