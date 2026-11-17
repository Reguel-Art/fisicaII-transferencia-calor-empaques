"""Editor de datos dentro de la app (Streamlit).

Permite ingresar o modificar mediciones sin preparar un CSV a mano:

  1. Tabla de EMPAQUES: una fila por empaque con sus parámetros físicos
     (T ambiente, conductividad, espesor, área, masa, c, umbral) y si es el control.
     Se pueden agregar, renombrar o borrar empaques.
  2. Tabla de TEMPERATURAS: filas = instantes (min); columnas = "Empaque · R1",
     "Empaque · R2", ... Se pueden agregar instantes y dejar celdas vacías.

Las dos tablas se convierten al esquema canónico del CSV y pasan por
core.datos.validar, igual que un archivo subido. El motor de cálculo no cambia.
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd
import streamlit as st

from core import datos

SEP = " · R"   # separador de columnas "Empaque · R1"

PARAM_DEFECTOS = {
    "control": False,
    "temp_ambiente_c": 25.0,
    "conductividad_k_wmk": np.nan,
    "espesor_pared_mm": 0.0,
    "area_superficial_m2": 0.04,
    "masa_agua_kg": 0.5,
    "calor_especifico_j_kgk": 4186.0,
    "umbral_calidad_c": 10.0,
}
ORIGENES = ["Simulado", "Medición real"]

COLUMNAS_CSV = [
    "id_registro", "codigo_empaque", "empaque", "repeticion", "tiempo_min",
    "temp_agua_c", "temp_ambiente_c", "costo_empaque_pen", "conductividad_k_wmk",
    "espesor_pared_mm", "masa_agua_kg", "calor_especifico_j_kgk",
    "area_superficial_m2", "umbral_calidad_c", "tipo_dato",
]


# --------------------------------------------------------------------------- #
# Conversión CSV ⇄ tablas editables
# --------------------------------------------------------------------------- #
def _es_control(df: pd.DataFrame, emp: str) -> bool:
    codigo = datos.params_empaque(df, emp).codigo
    if codigo is not None and str(codigo).upper() == "CTRL":
        return True
    e = emp.lower()
    return "control" in e or "sin empaque" in e


def df_a_editables(df: pd.DataFrame):
    """DataFrame validado → (params, repeticiones, tabla ancha, origen)."""
    empaques = datos.lista_empaques(df)
    filas = []
    for emp in empaques:
        p = datos.params_empaque(df, emp)
        sub = df[df["empaque"] == emp]
        t_amb = (float(sub["temp_amb_C"].mean())
                 if "temp_amb_C" in sub and sub["temp_amb_C"].notna().any() else 25.0)
        filas.append({
            "empaque": emp,
            "control": _es_control(df, emp),
            "temp_ambiente_c": round(t_amb, 2),
            "conductividad_k_wmk": p.conductividad_k_wmk,
            "espesor_pared_mm": p.espesor_pared_mm if p.espesor_pared_mm is not None else 0.0,
            "area_superficial_m2": p.area_superficial_m2 or 0.04,
            "masa_agua_kg": p.masa_agua_kg,
            "calor_especifico_j_kgk": p.calor_especifico_j_kgk,
            "umbral_calidad_c": p.umbral_calidad_c if p.umbral_calidad_c is not None else 10.0,
        })
    params = pd.DataFrame(filas)

    reps = int(df["repeticion"].max())
    ancha = (
        df.assign(col=df["empaque"] + SEP + df["repeticion"].astype(int).astype(str))
        .pivot_table(index="tiempo_min", columns="col", values="temp_C", aggfunc="mean")
    )
    columnas = [f"{e}{SEP}{r}" for e in empaques for r in range(1, reps + 1)]
    ancha = ancha.reindex(columns=columnas).reset_index()
    ancha["tiempo_min"] = ancha["tiempo_min"].astype(float)

    simulado = ("tipo_dato" in df.columns and
                "simula" in " ".join(df["tipo_dato"].astype(str).unique()).lower())
    origen = "Simulado" if simulado else "Medición real"
    return params, reps, ancha, origen


def _codigo(emp: str, control: bool, usados: set[str]) -> str:
    if control:
        base = "CTRL"
    else:
        base = re.sub(r"[^A-Za-z0-9]", "", emp).upper()[:4] or "EMP"
        if base == "CTRL":
            base = "EMP"
    cod, i = base, 2
    while cod in usados:
        cod, i = f"{base}{i}", i + 1
    usados.add(cod)
    return cod


def _valor(fila: pd.Series, col: str):
    v = fila.get(col)
    return PARAM_DEFECTOS[col] if v is None or (isinstance(v, float) and np.isnan(v)) else v


def editables_a_csv(params: pd.DataFrame, ancha: pd.DataFrame, reps: int,
                    origen: str, precios: dict[str, float] | None = None) -> pd.DataFrame:
    """Tablas editables → DataFrame con el esquema del CSV (sin validar)."""
    precios = precios or {}
    tipo = ("Simulacion_Editada_En_App" if origen == "Simulado"
            else "Medicion_Real_Editada_En_App")
    filas, usados, vistos = [], set(), set()
    for orden, (_, pr) in enumerate(params.iterrows()):
        emp = str(pr["empaque"]).strip() if pd.notna(pr["empaque"]) else ""
        if not emp or emp in vistos:
            continue
        vistos.add(emp)
        control = bool(_valor(pr, "control"))
        cod = _codigo(emp, control, usados)
        for r in range(1, reps + 1):
            col = f"{emp}{SEP}{r}"
            if col not in ancha.columns:
                continue
            for t, v in zip(ancha["tiempo_min"], ancha[col]):
                if pd.isna(t) or pd.isna(v):
                    continue
                filas.append({
                    "_orden": orden,
                    "codigo_empaque": cod, "empaque": emp, "repeticion": r,
                    "tiempo_min": float(t), "temp_agua_c": float(v),
                    "temp_ambiente_c": float(_valor(pr, "temp_ambiente_c")),
                    "costo_empaque_pen": float(precios.get(emp, 0.0)),
                    "conductividad_k_wmk": _valor(pr, "conductividad_k_wmk"),
                    "espesor_pared_mm": float(_valor(pr, "espesor_pared_mm")),
                    "masa_agua_kg": float(_valor(pr, "masa_agua_kg")),
                    "calor_especifico_j_kgk": float(_valor(pr, "calor_especifico_j_kgk")),
                    "area_superficial_m2": float(_valor(pr, "area_superficial_m2")),
                    "umbral_calidad_c": float(_valor(pr, "umbral_calidad_c")),
                    "tipo_dato": tipo,
                })
    if not filas:
        return pd.DataFrame(columns=COLUMNAS_CSV)
    out = (pd.DataFrame(filas)
           .sort_values(["_orden", "repeticion", "tiempo_min"], kind="stable")
           .drop(columns="_orden").reset_index(drop=True))
    out.insert(0, "id_registro", range(1, len(out) + 1))
    return out[COLUMNAS_CSV]


# --------------------------------------------------------------------------- #
# Estado de sesión
# --------------------------------------------------------------------------- #
def _inicializar(df: pd.DataFrame, ident: str):
    params, reps, ancha, origen = df_a_editables(df)
    ss = st.session_state
    ss.ed_ident = ident
    ss.ed_params = params
    ss.ed_params_ult = params
    ss.ed_reps = reps
    ss.ed_ancha_base = ancha
    ss.ed_ancha_ult = ancha
    ss.ed_nombres = params["empaque"].tolist()
    ss.ed_alias = {n: n for n in ss.ed_nombres}   # nombre actual → nombre de partida
    ss.ed_origen = origen
    ss.ed_ver = ss.get("ed_ver", 0) + 1     # fuerza nuevas claves de widgets
    ss.ed_ver_p = ss.get("ed_ver_p", 0) + 1


def _sincronizar_columnas(nombres: list, reps: int):
    """Ajusta las columnas de temperatura a los empaques y repeticiones actuales.

    Si un empaque se renombra (misma posición en la tabla), sus columnas se
    renombran y se conservan los valores. Empaques nuevos → columnas vacías.
    """
    ss = st.session_state
    ult = ss.ed_ancha_ult.copy()
    previos = ss.ed_nombres
    if len(previos) == len(nombres):
        renombrar = {}
        for viejo, nuevo in zip(previos, nombres):
            if viejo and nuevo and viejo != nuevo:
                ss.ed_alias[nuevo] = ss.ed_alias.get(viejo, viejo)
                for c in ult.columns:
                    if c.startswith(f"{viejo}{SEP}"):
                        renombrar[c] = f"{nuevo}{c[len(viejo):]}"
        ult = ult.rename(columns=renombrar)
    ss.ed_nombres = list(nombres)

    validos = list(dict.fromkeys(n for n in nombres if n))
    deseadas = [f"{e}{SEP}{r}" for e in validos for r in range(1, reps + 1)]
    if list(ss.ed_ancha_base.columns[1:]) != deseadas:
        nueva = pd.DataFrame({"tiempo_min": ult["tiempo_min"]})
        for c in deseadas:
            nueva[c] = ult[c] if c in ult.columns else np.nan
        ss.ed_ancha_base = nueva
        ss.ed_ancha_ult = nueva
        ss.ed_ver += 1


def nombre_original(emp: str) -> str:
    """Nombre con el que el empaque venía en los datos de partida (para su precio)."""
    return st.session_state.get("ed_alias", {}).get(emp, emp)


# --------------------------------------------------------------------------- #
# Interfaz
# --------------------------------------------------------------------------- #
def render(df_partida: pd.DataFrame, ident: str):
    """Dibuja el editor y devuelve (df_validado | None, func_exportar).

    func_exportar(precios) → bytes del CSV con los datos editados.
    """
    ss = st.session_state
    if ss.get("ed_ident") != ident:
        _inicializar(df_partida, ident)
    # Al volver a esta página Streamlit ya borró el estado de las tablas:
    # se parte de lo último que el usuario editó.
    if f"ed_params_{ss.ed_ver_p}" not in ss:
        ss.ed_params = ss.ed_params_ult
    if f"ed_ancha_{ss.ed_ver}" not in ss:
        ss.ed_ancha_base = ss.ed_ancha_ult

    st.markdown("#### ✏️ Ingresa o modifica tus mediciones")
    st.caption(
        "Edita las celdas directamente. Con **＋** al pie de cada tabla agregas "
        "filas (empaques o instantes); selecciona filas y pulsa 🗑️ para borrarlas. "
        "Los resultados de las demás pestañas se recalculan al instante."
    )

    c1, c2, c3, c4 = st.columns([1.2, 1.2, 1, 1])
    reps = c1.number_input("Repeticiones por empaque", min_value=1, max_value=10,
                           value=int(ss.ed_reps), step=1, key=f"ed_reps_{ss.ed_ver_p}")
    origen = c2.selectbox("Origen de los datos", ORIGENES,
                          index=ORIGENES.index(ss.ed_origen), key=f"ed_origen_{ss.ed_ver_p}",
                          help="Marca «Medición real» solo si son lecturas tomadas por el grupo.")
    c3.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
    if c3.button("↺ Restaurar", help="Vuelve a los datos de partida", width="stretch"):
        _inicializar(df_partida, ident)
        st.rerun()
    c4.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)
    if c4.button("🧹 Vaciar temperaturas", help="Deja la tabla de temperaturas en blanco",
                 width="stretch"):
        base = ss.ed_ancha_ult.copy()
        base.iloc[:, 1:] = np.nan
        ss.ed_ancha_base = ss.ed_ancha_ult = base
        ss.ed_ver += 1
        st.rerun()

    st.markdown("**1 · Empaques y parámetros físicos**")
    params = st.data_editor(
        ss.ed_params, key=f"ed_params_{ss.ed_ver_p}", num_rows="dynamic",
        hide_index=True, width="stretch",
        column_config={
            "empaque": st.column_config.TextColumn("Empaque", required=True),
            "control": st.column_config.CheckboxColumn(
                "¿Control?", help="Referencia sin empaque para «°C evitados»", default=False),
            "temp_ambiente_c": st.column_config.NumberColumn("T ambiente (°C)", format="%.1f", default=25.0),
            "conductividad_k_wmk": st.column_config.NumberColumn(
                "k material (W/m·K)", format="%.3f", min_value=0.0, default=0.04),
            "espesor_pared_mm": st.column_config.NumberColumn(
                "Espesor (mm)", format="%.1f", min_value=0.0, default=0.0),
            "area_superficial_m2": st.column_config.NumberColumn(
                "Área (m²)", format="%.3f", min_value=0.0, default=0.04),
            "masa_agua_kg": st.column_config.NumberColumn("Masa agua (kg)", format="%.2f", min_value=0.0, default=0.5),
            "calor_especifico_j_kgk": st.column_config.NumberColumn(
                "c (J/kg·K)", format="%.0f", min_value=0.0, default=4186.0),
            "umbral_calidad_c": st.column_config.NumberColumn("Umbral (°C)", format="%.1f", default=10.0),
        },
    )
    ss.ed_params_ult = params
    ss.ed_reps, ss.ed_origen = int(reps), origen
    nombres = [str(n).strip() if pd.notna(n) else "" for n in params["empaque"]]
    duplicados = sorted({n for n in nombres if n and nombres.count(n) > 1})
    if duplicados:
        # No se sincronizan columnas con nombres repetidos (mezclaría sus datos).
        st.error(f"Hay empaques con el mismo nombre: {', '.join(duplicados)}. "
                 "Cámbialos para que cada uno sea único; mientras tanto se mantienen "
                 "los últimos datos válidos.")
    else:
        _sincronizar_columnas(nombres, int(reps))

    st.markdown("**2 · Temperatura del agua (°C) por instante y repetición**")
    col_cfg = {"tiempo_min": st.column_config.NumberColumn(
        "Tiempo (min)", min_value=0, step=1, format="%g", required=True)}
    for c in ss.ed_ancha_base.columns[1:]:
        col_cfg[c] = st.column_config.NumberColumn(c, format="%.2f")
    ancha = st.data_editor(
        ss.ed_ancha_base, key=f"ed_ancha_{ss.ed_ver}", num_rows="dynamic",
        hide_index=True, width="stretch", column_config=col_cfg,
    )
    ss.ed_ancha_ult = ancha
    st.caption("Las celdas vacías se ignoran. Precios y usos se ajustan en «Evaluación económica».")

    def exportar(precios: dict[str, float]) -> bytes:
        return editables_a_csv(params, ancha, int(reps), origen, precios).to_csv(
            index=False).encode("utf-8")

    if duplicados:
        return None, exportar
    crudo = editables_a_csv(params, ancha, int(reps), origen)
    if crudo.empty:
        st.info("Ingresa al menos un empaque con temperaturas para ver resultados.")
        return None, exportar
    try:
        df = datos.validar(crudo)
    except datos.ErrorDatos as e:
        st.error(f"Revisa los datos: {e}")
        return None, exportar

    # Avisos útiles antes de analizar.
    pocos = [e for e, g in df.groupby("empaque", sort=False) if g["tiempo_min"].nunique() < 2]
    if pocos:
        st.warning("Necesitan al menos 2 instantes para ajustar k: " + ", ".join(pocos))
    if not any(bool(_valor(r, "control")) for _, r in params.iterrows()):
        st.caption("ℹ️ Ningún empaque está marcado como control: «S/ por °C evitado» "
                   "solo se calcula frente a un control.")
    return df, exportar
