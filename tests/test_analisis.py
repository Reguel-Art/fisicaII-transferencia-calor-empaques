"""Pruebas del motor de análisis sobre el CSV real del Grupo 3."""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from core import analisis, datos

CSV = RAIZ / "data" / "Grupo_3_Datos_Termicos_Web.csv"


def _resumen():
    df = datos.cargar_csv(CSV)
    return df, analisis.analizar(df)


def test_carga_y_estructura():
    df = datos.cargar_csv(CSV)
    assert len(df) == 52            # 4 configuraciones × 13 lecturas
    assert datos.lista_empaques(df) == [
        "Control (Sin empaque)",
        "Caja de Cartón",
        "Bolsa Térmica Aluminizada",
        "Recipiente Aislante (EPS)",
    ]
    # Ensayo real del grupo: ambiente constante de 24,0 °C
    assert abs(datos.temperatura_ambiente(df) - 24.0) < 1e-9


def test_params_empaque_eps():
    df = datos.cargar_csv(CSV)
    p = datos.params_empaque(df, "Recipiente Aislante (EPS)")
    assert p.codigo == "EPS"
    assert p.conductividad_k_wmk == 0.038
    assert p.espesor_pared_mm == 15.0
    assert p.area_superficial_m2 == 0.04
    assert p.masa_agua_kg == 0.6     # botella de 600 mL
    assert p.calor_especifico_j_kgk == 4186


def test_resumen_termico_eps():
    _, res = _resumen()
    eps = res[res["empaque"] == "Recipiente Aislante (EPS)"].iloc[0]
    # Valores de la Tabla 8 de la parte experimental (tecnopor/EPS).
    assert eps["t0_C"] == 12.5
    assert eps["t60_C"] == 20.9
    assert eps["delta_T"] == 8.4
    # Q = 0.6 * 4186 * (20.9 - 12.5) = 21097.4 J  (informe: 21,10 kJ)
    assert abs(eps["q_absorbido_J"] - 21097.4) < 1.0
    assert eps["r2"] > 0.99          # ajuste muy bueno


def test_ley_conduccion_eps():
    # R = L/(k·A) = 0.015 / (0.038 * 0.04) = 9.868 K/W
    _, res = _resumen()
    eps = res[res["empaque"] == "Recipiente Aislante (EPS)"].iloc[0]
    assert abs(eps["r_cond_KW"] - 9.868) < 0.01
    assert abs(eps["ua_cond_WK"] - 0.1013) < 1e-3
    # Q̇ inicial = (24.0 - 12.5)/9.868 = 1.165 W
    assert abs(eps["qdot_cond_W"] - 1.165) < 0.01


def test_control_calienta_mas_rapido():
    _, res = _resumen()
    ctrl = res[res["empaque"] == "Control (Sin empaque)"].iloc[0]
    eps = res[res["empaque"] == "Recipiente Aislante (EPS)"].iloc[0]
    # El control debe tener mayor k (se calienta más rápido) y mayor T60.
    assert ctrl["k_fit_min"] > eps["k_fit_min"]
    assert ctrl["t60_C"] > eps["t60_C"]


def test_tiempo_umbral_ordenado():
    _, res = _resumen()
    r = res.set_index("empaque")["t_umbral_min"]
    # Mejor aislante tarda más en cruzar 10 °C.
    assert r["Control (Sin empaque)"] < r["Caja de Cartón"]
    assert r["Caja de Cartón"] < r["Bolsa Térmica Aluminizada"]
    assert r["Bolsa Térmica Aluminizada"] < r["Recipiente Aislante (EPS)"]


def test_ranking_bolsa_gana_en_eficiencia():
    df = datos.cargar_csv(CSV)
    res = analisis.analizar(
        df, usos_por_empaque={"Bolsa Térmica Aluminizada": 60}
    )
    rk = analisis.ranking(res, por="soles_por_C_evitado")
    # El control queda último (inf); la bolsa primera con 60 usos.
    assert rk.iloc[-1]["empaque"] == "Control (Sin empaque)"
    assert rk.iloc[0]["empaque"] == "Bolsa Térmica Aluminizada"


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
