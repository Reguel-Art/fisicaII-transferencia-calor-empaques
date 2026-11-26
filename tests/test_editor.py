"""Pruebas de la conversión del editor de datos (tablas ⇄ CSV)."""

import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import editor  # noqa: E402
from core import analisis, datos  # noqa: E402

CSV = RAIZ / "data" / "Grupo_3_Datos_Termicos_Web.csv"


def _ida_y_vuelta():
    df = datos.cargar_csv(CSV)
    params, reps, ancha, origen = editor.df_a_editables(df)
    precios = {e: datos.params_empaque(df, e).costo_empaque_pen
               for e in datos.lista_empaques(df)}
    crudo = editor.editables_a_csv(params, ancha, reps, origen, precios)
    return df, datos.validar(crudo), params, reps, ancha, origen


def test_tablas_editables():
    _, _, params, reps, ancha, origen = _ida_y_vuelta()
    assert reps == 1
    assert origen == "Medición real"
    assert len(params) == 4
    assert params["control"].tolist() == [True, False, False, False]
    assert ancha.shape == (13, 1 + 4 * 1)        # tiempo + 4 empaques × 1 rep


def test_ida_y_vuelta_conserva_resultados():
    df, df2, *_ = _ida_y_vuelta()
    assert len(df2) == len(df) == 52
    r1 = analisis.analizar(df).set_index("empaque")
    r2 = analisis.analizar(df2).set_index("empaque")
    for col in ["t0_C", "t60_C", "q_absorbido_J", "k_fit_min", "r_cond_KW", "costo_empaque"]:
        a, b = r1[col].astype(float), r2[col].astype(float)
        assert np.allclose(a.fillna(-1), b.fillna(-1), atol=0.02), col


def test_celdas_vacias_y_empaque_nuevo():
    _, _, params, reps, ancha, origen = _ida_y_vuelta()
    ancha = ancha.copy()
    col = "Caja de Cartón · R1"
    ancha.loc[ancha["tiempo_min"] == 60, col] = np.nan     # celda vacía → se ignora
    params = params.copy()
    params.loc[len(params)] = {"empaque": "Bolsa de tela"}  # sin temperaturas aún
    crudo = editor.editables_a_csv(params, ancha, reps, "Medición real")
    df = datos.validar(crudo)
    assert len(df) == 51
    assert "Bolsa de tela" not in datos.lista_empaques(df)
    assert set(df["tipo_dato"]) == {"Medicion_Real_Editada_En_App"}


def test_control_por_casilla():
    _, _, params, reps, ancha, _ = _ida_y_vuelta()
    params = params.copy()
    params["control"] = False
    params.loc[params["empaque"] == "Caja de Cartón", "control"] = True
    crudo = editor.editables_a_csv(params, ancha, reps, "Simulado")
    cods = crudo.groupby("empaque")["codigo_empaque"].first()
    assert cods["Caja de Cartón"] == "CTRL"
    assert cods["Control (Sin empaque)"] != "CTRL"


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
