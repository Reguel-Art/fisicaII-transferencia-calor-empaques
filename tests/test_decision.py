"""Pruebas de la evaluación de alternativas (core/decision.py)."""

import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import datos, decision  # noqa: E402

CSV = RAIZ / "data" / "Grupo_3_Datos_Termicos_Web.csv"


def _tabla(**cambios):
    base = pd.DataFrame([
        dict(empaque="Control", es_control=True, precio=0.0, costo_uso=0.0, delta_T=13.3, cumple_lecturas=False),
        dict(empaque="Cartón", es_control=False, precio=1.8, costo_uso=1.8, delta_T=9.9, cumple_lecturas=False),
        dict(empaque="Bolsa", es_control=False, precio=25.0, costo_uso=0.42, delta_T=6.9, cumple_lecturas=True),
        dict(empaque="EPS", es_control=False, precio=6.5, costo_uso=0.65, delta_T=4.8, cumple_lecturas=True),
    ])
    for k, v in cambios.items():
        base[k] = v
    return base


def test_costo_uso_total():
    assert abs(decision.costo_uso_total(25, 60, 0.1, 0.05) - (25 / 60 + 0.15)) < 1e-12


def test_cumple_en_cada_lectura_con_datos_del_informe():
    df = datos.cargar_csv(CSV)
    # EPS: la repetición 2 llega exactamente a 10,0 °C al minuto 60.
    assert decision.cumple_en_cada_lectura(df, "Recipiente Aislante (EPS)", 10.0, 60)
    assert not decision.cumple_en_cada_lectura(df, "Recipiente Aislante (EPS)", 9.9, 60)
    # La bolsa supera 10 °C antes del minuto 60, pero no a los 30.
    assert not decision.cumple_en_cada_lectura(df, "Bolsa Térmica Aluminizada", 10.0, 60)
    assert decision.cumple_en_cada_lectura(df, "Bolsa Térmica Aluminizada", 10.0, 30)


def test_viabilidad_y_motivos():
    r = decision.evaluar(_tabla(), peso_conservacion=0.6).set_index("empaque")
    assert r.loc["Control", "motivo"] == "Control (referencia)"
    assert r.loc["Cartón", "motivo"] == "Supera el límite en alguna lectura"
    assert r.loc["Bolsa", "viable"] and r.loc["EPS", "viable"]


def test_peso_cambia_la_recomendacion():
    solo_temp = decision.evaluar(_tabla(), peso_conservacion=1.0)
    solo_costo = decision.evaluar(_tabla(), peso_conservacion=0.0)
    assert solo_temp.iloc[0]["empaque"] == "EPS"      # menor ΔT
    assert solo_costo.iloc[0]["empaque"] == "Bolsa"   # menor costo por uso
    assert solo_temp.iloc[0]["puntaje"] == 100.0


def test_costo_maximo_excluye():
    r = decision.evaluar(_tabla(), peso_conservacion=1.0, max_costo_uso=0.5).set_index("empaque")
    assert not r.loc["EPS", "viable"]
    assert r.loc["EPS", "motivo"] == "Supera el costo máximo por uso"
    assert r.loc["Bolsa", "puntaje"] == 100.0       # única viable


def test_sin_viables_ordena_por_conservacion():
    r = decision.evaluar(_tabla(cumple_lecturas=False), peso_conservacion=0.6)
    assert not r["viable"].any()
    assert r.iloc[0]["empaque"] == "EPS"


def test_no_aprueba_si_los_datos_no_llegan_a_la_entrega():
    df = datos.cargar_csv(CSV)
    eps = "Recipiente Aislante (EPS)"
    corto = df[~((df["empaque"] == eps) & (df["tiempo_min"] > 30))]
    assert not decision.cubre_tiempo(corto, eps, 60)
    assert not decision.cumple_en_cada_lectura(corto, eps, 8.0, 60)
    assert decision.cubre_tiempo(corto, eps, 30)


def test_entrega_entre_lecturas_incluye_la_siguiente():
    df = datos.cargar_csv(CSV)
    cada10 = df[df["tiempo_min"] % 10 == 0]
    bolsa = "Bolsa Térmica Aluminizada"
    # A los 45 min la bolsa (interpolada) ya supera 10 °C: la lectura de 50 min cuenta.
    assert not decision.cumple_en_cada_lectura(cada10, bolsa, 10.0, 45)
    assert decision.cumple_en_cada_lectura(cada10, bolsa, 10.0, 30)


def test_costo_registrado_por_costo_de_uso_y_nan():
    t = _tabla()
    t.loc[t["empaque"] == "Bolsa", ["precio", "costo_uso"]] = [0.0, 0.30]   # solo limpieza
    t.loc[t["empaque"] == "EPS", ["precio", "costo_uso"]] = [float("nan"), float("nan")]
    r = decision.evaluar(t, peso_conservacion=0.6).set_index("empaque")
    assert r.loc["Bolsa", "viable"]
    assert r.loc["EPS", "motivo"] == "Sin costo registrado"


def test_motivo_sin_lecturas_hasta_entrega():
    t = _tabla()
    t["cubre_tiempo"] = [True, True, True, False]
    r = decision.evaluar(t, peso_conservacion=0.6).set_index("empaque")
    assert r.loc["EPS", "motivo"] == "Sin lecturas hasta el tiempo de entrega"
    assert r.loc["Bolsa", "puntaje"] == 100.0


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
