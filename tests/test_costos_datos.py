"""Pruebas de los módulos de costos y datos."""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import costos, datos, simulacion


# ---------------------------- costos ----------------------------

def test_costo_por_uso():
    assert costos.costo_por_uso(8.0, 60) == 8.0 / 60


def test_costo_por_uso_invalido():
    try:
        costos.costo_por_uso(8.0, 0)
    except ValueError:
        return
    raise AssertionError("Debió lanzar ValueError con usos=0.")


def test_soles_por_grado():
    # Empaque a 12°C, control a 18°C -> 6°C evitados, costo_uso 0.13.
    spc = costos.soles_por_grado_evitado(0.13, 12.0, 18.0)
    assert abs(spc - 0.13 / 6.0) < 1e-9


def test_soles_por_grado_sin_mejora():
    # El empaque no mejora al control -> infinito.
    assert costos.soles_por_grado_evitado(0.13, 18.0, 18.0) == float("inf")


def test_sensibilidad_usos():
    s = costos.sensibilidad_usos(8.0, [10, 30, 60])
    assert s[10] == 0.8 and abs(s[60] - 8 / 60) < 1e-9


def test_usos_de_equilibrio():
    # Reutilizable S/8 vs desechable S/0.30 por uso -> equilibrio ~26.7 usos.
    u = costos.usos_de_equilibrio(8.0, 0.30)
    assert abs(u - 26.6667) < 1e-3


# ---------------------------- datos ----------------------------

def test_validar_detecta_columnas_faltantes():
    df = pd.DataFrame({"empaque": ["a"], "tiempo_min": [0]})
    try:
        datos.validar(df)
    except datos.ErrorDatos as e:
        assert "Faltan columnas" in str(e)
        return
    raise AssertionError("Debió detectar columnas faltantes.")


def test_validar_detecta_tiempo_negativo():
    df = pd.DataFrame(
        {"empaque": ["a"], "repeticion": [1], "tiempo_min": [-5], "temp_C": [4]}
    )
    try:
        datos.validar(df)
    except datos.ErrorDatos as e:
        assert "negativos" in str(e)
        return
    raise AssertionError("Debió detectar tiempo negativo.")


def test_agregar_media_y_std():
    df = simulacion.generar(repeticiones=3, semilla=1)
    df = datos.validar(df)
    ag = datos.agregar(df)
    # Debe haber una fila por (empaque, tiempo) y n=3 repeticiones.
    assert set(ag.columns) >= {"empaque", "tiempo_min", "temp_media", "temp_std", "n"}
    assert (ag["n"] == 3).all()


def test_interpolacion_temperatura():
    df = datos.validar(simulacion.generar(semilla=2))
    ag = datos.agregar(df)
    # A t=0 todos arrancan en ~4°C.
    t0 = datos.temperatura_en_tiempo(ag, "tecnopor", 0)
    assert abs(t0 - 4.0) < 0.5


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
