"""Estado compartido entre páginas y cálculo del análisis completo.

Todo lo que el usuario elige (datos, umbral, tiempo de entrega, costos,
preferencia) vive en st.session_state, de modo que las cuatro páginas
muestran el mismo análisis. Los cálculos usan exclusivamente core/.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

import editor
from core import analisis, costos, datos, decision, fisica

RAIZ = Path(__file__).resolve().parents[1]
CSV_DEFECTO = RAIZ / "data" / "Grupo_3_Datos_Termicos_Web.csv"

ss = st.session_state

COLUMNAS_COSTOS = ["material", "precio", "usos", "limpieza", "otros", "control"]


@st.cache_data(show_spinner=False)
def cargar_ejemplo() -> pd.DataFrame:
    return datos.cargar_csv(CSV_DEFECTO)


def _precios_de(df: pd.DataFrame) -> dict[str, float]:
    return {e: datos.params_empaque(df, e).costo_empaque_pen for e in datos.lista_empaques(df)}


def usos_defecto(emp: str) -> int:
    e = emp.lower()
    if "bolsa" in e:
        return 60
    if "eps" in e or "aislante" in e or "tecnopor" in e:
        return 10
    return 1


# --------------------------------------------------------------------------- #
# Inicialización y origen de datos
# --------------------------------------------------------------------------- #
def inicializar():
    if "df_actual" not in ss:
        ej = cargar_ejemplo()
        fijar_base(ej, CSV_DEFECTO.name, "Ejemplo", CSV_DEFECTO.name)
    ss.setdefault("cfg_umbral", 18.0)   # bebidas a 12,5 °C en el ensayo real
    ss.setdefault("cfg_t", 20)
    ss.setdefault("eco_pedidos", 100)
    ss.setdefault("eco_empaques", 1)
    ss.setdefault("eco_max", 0.0)
    ss.setdefault("eco_fuente", "Precios cotizados por el grupo en el mercado local")
    ss.setdefault("eco_peso", 40)   # 40 % conservación / 60 % costo: criterio del informe
    ss.setdefault("eco_ver", 0)
    ss.setdefault("ver_desv", True)
    ss.setdefault("ver_modelo", False)


def fijar_base(df: pd.DataFrame, nombre: str, modo: str, ident: str):
    """Datos de partida (ejemplo o CSV subido). También sirven de base al editor."""
    ss.df_base, ss.ident_base, ss.precios_partida = df, ident, _precios_de(df)
    ss.nombre_base = nombre
    # Datos nuevos: la tabla de costos se rehace con sus precios y el editor
    # vuelve a partir de estos datos.
    ss.pop("eco_tabla_ult", None)
    ss.pop("ed_ident", None)
    fijar_actual(df, nombre, modo)


def fijar_actual(df: pd.DataFrame, nombre: str, modo: str):
    ss.df_actual, ss.fuente_nombre, ss.fuente_modo = df, nombre, modo


def estado_datos(df: pd.DataFrame) -> str:
    """'Simulado' | 'Validado' | 'Sin declarar'."""
    if "tipo_dato" not in df.columns:
        return "Sin declarar"
    tipos = " ".join(df["tipo_dato"].astype(str).unique()).lower()
    return "Simulado" if "simula" in tipos else "Validado"


def t_tope(df: pd.DataFrame) -> int:
    """Mayor tiempo de entrega evaluable: múltiplo de 5 ≤ última lectura (máx. 60).

    Si los datos no llegan a 5 min se usa la última lectura (redondeada hacia abajo).
    """
    t_max = float(df["tiempo_min"].max())
    tope = 5 * math.floor(t_max / 5)
    return int(min(60, tope if tope >= 5 else math.floor(t_max)))


# --------------------------------------------------------------------------- #
# Tabla de costos (Evaluación económica)
# --------------------------------------------------------------------------- #
def tabla_costos() -> pd.DataFrame:
    """Última tabla de costos, sincronizada con los empaques de los datos actuales."""
    df = ss.df_actual
    empaques = datos.lista_empaques(df)
    t = ss.get("eco_tabla_ult")
    if t is None or t["material"].tolist() != empaques:
        previa = t.set_index("material") if t is not None else pd.DataFrame()
        ctrl = analisis._detectar_control(df, empaques)
        filas = []
        for e in empaques:
            origen = editor.nombre_original(e)
            # Misma fila si el empaque existía, o si fue renombrado en el editor
            # (comparten el nombre de partida): se conservan sus costos editados.
            previo = e if e in previa.index else next(
                (m for m in previa.index
                 if m not in empaques and editor.nombre_original(m) == origen), None)
            if previo is not None:
                filas.append({"material": e, **previa.loc[previo].to_dict()})
                continue
            precio = ss.precios_partida.get(origen, ss.precios_partida.get(e, 0.0))
            filas.append(dict(material=e, precio=float(precio), usos=usos_defecto(e),
                              limpieza=0.0, otros=0.0, control=(e == ctrl)))
        t = pd.DataFrame(filas, columns=COLUMNAS_COSTOS)
        ss.eco_tabla_ult = ss.eco_tabla_base = t
        ss.eco_ver += 1
    return ss.eco_tabla_ult


# --------------------------------------------------------------------------- #
# Análisis completo
# --------------------------------------------------------------------------- #
@dataclass
class Resultado:
    df: pd.DataFrame
    res: pd.DataFrame          # una fila por empaque, con todo lo calculado
    umbral: float
    t: int
    control: str | None
    reco: pd.Series | None     # alternativa recomendada (None si no hay viables)
    n_viables: int
    n_alternativas: int
    peso: float                # 0–1, peso de la conservación


def _evaluar_en_tiempo(df, res, t, control) -> pd.DataFrame:
    ag = datos.agregar(df)
    t_amb = datos.temperatura_ambiente(df)
    T_ctrl = (datos.temperatura_en_tiempo(ag, control, t)
              if control and decision.cubre_tiempo(df, control, t) else None)
    filas = []
    for _, r in res.iterrows():
        p = datos.params_empaque(df, r["empaque"])
        cubre = decision.cubre_tiempo(df, r["empaque"], t)
        # Sin lecturas hasta t no se extrapola: magnitudes en t quedan vacías.
        T_t = datos.temperatura_en_tiempo(ag, r["empaque"], t) if cubre else np.nan
        dT = T_t - r["t0_C"]
        razon = (t_amb - T_t) / (t_amb - r["t0_C"]) if t_amb != r["t0_C"] else np.nan
        r_cond = r["r_cond_KW"]
        filas.append(dict(
            T_t=round(T_t, 2), dT_t=round(dT, 2),
            Q_t=round(fisica.calor_sensible(p.masa_agua_kg, p.calor_especifico_j_kgk, dT), 1),
            k_ef_t=(-math.log(razon) / t if t > 0 and razon > 0 else np.nan),
            qdot_t=((t_amb - T_t) / r_cond if pd.notna(r_cond) and r_cond else np.nan),
            T_ctrl_t=(round(T_ctrl, 2) if T_ctrl is not None else None),
            cubre_tiempo=cubre,
        ))
    return pd.concat([res.reset_index(drop=True), pd.DataFrame(filas)], axis=1)


def calcular() -> Resultado:
    df = ss.df_actual
    umbral = float(ss.cfg_umbral)
    tope = t_tope(df)
    t = int(min(max(5, ss.cfg_t), tope)) if tope >= 10 else tope   # igual que el slider
    tab = tabla_costos().set_index("material")
    controles = tab.index[tab["control"].fillna(False).astype(bool)].tolist()
    control = controles[0] if controles else None

    df_calc = df.copy()
    df_calc["costo_empaque_pen"] = df_calc["empaque"].map(tab["precio"]).fillna(0.0)
    # Celda de usos vacía → supuesto por defecto del material (no 1, que encarecería
    # en silencio un reutilizable).
    usos = {e: max(1, int(u)) if pd.notna(u) else usos_defecto(e)
            for e, u in tab["usos"].items()}
    res = analisis.analizar(df_calc, usos_por_empaque=usos, umbral_override=umbral,
                            control=control)
    res = _evaluar_en_tiempo(df_calc, res, t, control)
    res["orden"] = range(len(res))

    # Costos completos (precio/usos + limpieza + otros) e indicadores derivados.
    res["limpieza"] = res["empaque"].map(tab["limpieza"]).fillna(0.0)
    res["otros"] = res["empaque"].map(tab["otros"]).fillna(0.0)
    res["costo_uso"] = [
        decision.costo_uso_total(r.costo_empaque, r.usos, r.limpieza, r.otros)
        for r in res.itertuples()
    ]
    res["costo_total"] = res["costo_uso"] * int(ss.eco_empaques) * int(ss.eco_pedidos)
    res["spc_t"] = [
        costos.soles_por_grado_evitado(c, T, Tc) if Tc is not None and pd.notna(Tc) else float("inf")
        for c, T, Tc in zip(res["costo_uso"], res["T_t"], res["T_ctrl_t"])
    ]
    res["es_control"] = res["empaque"] == control
    # El control no «evita» grados y sin costo no hay S/ por °C: se muestran vacíos.
    res.loc[res["es_control"] | (res["costo_uso"] <= 0), "spc_t"] = float("inf")
    res["cumple_lecturas"] = [
        decision.cumple_en_cada_lectura(df, e, umbral, t) for e in res["empaque"]
    ]

    peso = float(ss.eco_peso) / 100.0
    ev = decision.evaluar(
        res[["empaque", "es_control", "costo_empaque", "costo_uso", "dT_t", "cumple_lecturas",
             "cubre_tiempo"]]
        .rename(columns={"costo_empaque": "precio", "dT_t": "delta_T"}),
        peso_conservacion=peso, max_costo_uso=float(ss.eco_max),
    )
    res = res.merge(ev[["empaque", "puesto", "viable", "motivo", "puntaje"]], on="empaque")
    res = res.sort_values("puesto").reset_index(drop=True)

    viables = res[res["viable"]]
    return Resultado(
        df=df, res=res, umbral=umbral, t=t, control=control,
        reco=viables.iloc[0] if not viables.empty else None,
        n_viables=len(viables), n_alternativas=int((~res["es_control"]).sum()),
        peso=peso,
    )
