"""Pruebas de la votación en vivo (ui/votacion.py) y del ganador del simulador."""

import sys
import warnings
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
warnings.filterwarnings("ignore")

from paginas.simulador import _ganador  # noqa: E402
from ui.votacion import Urna, veredicto_html  # noqa: E402

OPC = ["EPS", "Bolsa", "Cartón"]


def test_un_voto_por_persona():
    u = Urna()
    u.nueva("¿Quién gana?", OPC)
    assert u.votar("a", "EPS") and not u.votar("a", "Bolsa")
    assert u.votar("b", "Bolsa")
    assert u.foto().votos == {"EPS": 1, "Bolsa": 1, "Cartón": 0}


def test_limpiar_borra_todo_y_avanza_la_ronda():
    u = Urna()
    u.nueva("¿Quién gana?", OPC)
    u.votar("a", "EPS")
    id_antes = u.foto().id
    u.limpiar()
    r = u.foto()
    assert r.opciones == [] and r.votos == {} and r.votantes == set()
    assert r.id == id_antes + 1 and not r.revelada and r.ganador == ""
    assert not u.votar("b", "EPS")          # sin ronda abierta no se puede votar


def test_veredicto_acierta_y_falla():
    u = Urna()
    u.nueva("¿Quién gana?", OPC)
    u.fijar_ganador("EPS", "Llega a 8.4 °C")
    for v, o in [("a", "EPS"), ("b", "EPS"), ("c", "Bolsa")]:
        u.votar(v, o)
    assert "acertó" in veredicto_html(u.foto())
    u.nueva("¿Quién gana?", OPC)
    u.fijar_ganador("EPS")
    u.votar("a", "Cartón")
    html = veredicto_html(u.foto())
    assert "eligió Cartón" in html and "nadie acertó" in html


def test_ganador_prefiere_el_que_nunca_pasa_el_limite():
    res = pd.DataFrame([
        dict(empaque="EPS", es_control=False, minuto_limite=None, t_entrega_c=8.0),
        dict(empaque="Bolsa", es_control=False, minuto_limite=40.0, t_entrega_c=9.0),
        dict(empaque="Control", es_control=True, minuto_limite=None, t_entrega_c=7.0),
    ])
    g = _ganador(res, "Puno", 10.0, 30)
    assert g["nombre"] == "EPS" and "nunca pasa" in g["detalle"]


def test_ganador_por_minuto_y_desempate_por_temperatura():
    res = pd.DataFrame([
        dict(empaque="Cartón", es_control=False, minuto_limite=12.0, t_entrega_c=14.0),
        dict(empaque="Bolsa", es_control=False, minuto_limite=30.0, t_entrega_c=11.0),
        dict(empaque="EPS", es_control=False, minuto_limite=30.0, t_entrega_c=10.5),
    ])
    assert _ganador(res, "Piura", 10.0, 60)["nombre"] == "EPS"


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
