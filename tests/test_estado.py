"""Pruebas del estado compartido (ui/estado.py) fuera del servidor de Streamlit.

st.session_state funciona en «modo simple» (sin servidor), así que se puede
probar la lógica de páginas sin abrir la app.
"""

import sys
import warnings
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
warnings.filterwarnings("ignore")

import streamlit as st  # noqa: E402

from ui import estado  # noqa: E402

ss = st.session_state
EPS = "Recipiente Aislante (EPS)"
BOLSA = "Bolsa Térmica Aluminizada"


def _reiniciar():
    for k in list(ss.keys()):
        del ss[k]
    estado.inicializar()


def _fila(R, emp):
    return R.res.set_index("empaque").loc[emp]


def test_escenario_base_recomienda_bolsa():
    # Límite 18 °C a los 20 min: bolsa y EPS cumplen, el cartón no (19,5 °C).
    # Con 40 % conservación / 60 % costo gana la bolsa (S/ 0,67 vs S/ 3,00 por uso).
    _reiniciar()
    R = estado.calcular()
    assert R.reco["empaque"] == BOLSA
    assert (R.n_viables, R.n_alternativas) == (2, 3)
    assert np.isinf(_fila(R, "Control (Sin empaque)")["spc_t"])


def test_sin_lecturas_hasta_entrega_no_se_extrapola():
    _reiniciar()
    df = ss.df_actual
    ss.df_actual = df[~((df["empaque"] == EPS) & (df["tiempo_min"] > 30))]
    ss.cfg_umbral = 8.0
    ss.cfg_t = 60          # entrega después de la última lectura del EPS (30 min)
    R = estado.calcular()
    f = _fila(R, EPS)
    assert not f["viable"]
    assert f["motivo"] == "Sin lecturas hasta el tiempo de entrega"
    assert np.isnan(f["T_t"])


def test_usos_vacio_usa_supuesto_por_defecto():
    _reiniciar()
    t = estado.tabla_costos().copy()
    t.loc[t["material"] == BOLSA, "usos"] = np.nan
    ss.eco_tabla_ult = t
    R = estado.calcular()
    assert abs(_fila(R, BOLSA)["costo_uso"] - 40 / 60) < 1e-9


def test_sin_costo_no_muestra_soles_por_grado():
    _reiniciar()
    t = estado.tabla_costos().copy()
    t.loc[t["material"] == EPS, "precio"] = 0.0
    ss.eco_tabla_ult = t
    f = _fila(estado.calcular(), EPS)
    assert f["motivo"] == "Sin costo registrado"
    assert np.isinf(f["spc_t"])


def test_renombrar_conserva_costos_editados():
    _reiniciar()
    t = estado.tabla_costos().copy()
    t.loc[t["material"] == BOLSA, ["precio", "usos", "limpieza"]] = [30.0, 100, 0.1]
    ss.eco_tabla_ult = t
    # Simula el editor: la bolsa pasa a llamarse «Bolsa reutilizable».
    ss.ed_alias = {e: e for e in t["material"]}
    ss.ed_alias["Bolsa reutilizable"] = BOLSA
    df = ss.df_actual.copy()
    df.loc[df["empaque"] == BOLSA, "empaque"] = "Bolsa reutilizable"
    ss.df_actual = df
    fila = estado.tabla_costos().set_index("material").loc["Bolsa reutilizable"]
    assert (fila["precio"], fila["usos"], fila["limpieza"]) == (30.0, 100, 0.1)


def test_csv_nuevo_con_mismos_empaques_actualiza_precios():
    _reiniciar()
    estado.tabla_costos()
    df = ss.df_actual.copy()
    df["costo_empaque_pen"] = 99.0
    estado.fijar_base(df, "cotizaciones.csv", "CSV", "cotizaciones.csv:1")
    assert (estado.tabla_costos()["precio"] == 99.0).all()


def test_tope_con_datos_cortos():
    _reiniciar()
    df = ss.df_actual
    assert estado.t_tope(df) == 60
    assert estado.t_tope(df[df["tiempo_min"] <= 5]) == 5
    assert estado.t_tope(df[df["tiempo_min"] <= 0]) == 0
    ss.df_actual = df[df["tiempo_min"] <= 5]
    assert estado.calcular().t == 5


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
