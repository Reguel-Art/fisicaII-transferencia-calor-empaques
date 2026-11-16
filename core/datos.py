"""Carga, validación y agregación de los datos experimentales.

Esquema CANÓNICO de la herramienta (archivo Grupo_3_Datos_Termicos_Web.csv):

    id_registro, codigo_empaque, empaque, repeticion, tiempo_min,
    temp_agua_c, temp_ambiente_c, delta_t_c, costo_empaque_pen,
    conductividad_k_wmk, espesor_pared_mm, masa_agua_kg,
    calor_especifico_j_kgk, area_superficial_m2, umbral_calidad_c,
    estado_calidad, tipo_dato

Cada empaque trae sus propios parámetros físicos (conductividad, espesor, área,
masa, calor específico) y económicos (costo), lo que permite calcular tanto el
modelo de enfriamiento como la ley de conducción R = L/(k·A).

Para compatibilidad, también se acepta el esquema mínimo:
    empaque, repeticion, tiempo_min, temp_C   (+ opcional temp_ambiente_c)
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

# Columnas mínimas imprescindibles para poder analizar.
COLUMNAS_MINIMAS = ["empaque", "repeticion", "tiempo_min"]

# Posibles nombres para la temperatura del agua (se normaliza a 'temp_C').
ALIAS_TEMP_AGUA = ["temp_agua_c", "temp_agua_C", "temp_C", "temp_c"]
ALIAS_TEMP_AMB = ["temp_ambiente_c", "temp_ambiente_C", "temp_amb_C", "t_ambiente"]


class ErrorDatos(ValueError):
    """Error de validación de los datos de entrada."""


@dataclass
class ParamsEmpaque:
    """Parámetros físicos y económicos de un empaque (constantes en el CSV)."""

    empaque: str
    codigo: str | None
    conductividad_k_wmk: float | None   # k del material [W/(m·K)]
    espesor_pared_mm: float | None      # L [mm]
    area_superficial_m2: float | None   # A [m²]
    masa_agua_kg: float                 # m [kg]
    calor_especifico_j_kgk: float       # c [J/(kg·K)]
    costo_empaque_pen: float            # precio unitario [S/]
    umbral_calidad_c: float | None      # umbral objetivo [°C]


def _primera_columna(df: pd.DataFrame, alias: list[str]) -> str | None:
    for a in alias:
        if a in df.columns:
            return a
    return None


def validar(df: pd.DataFrame) -> pd.DataFrame:
    """Valida el DataFrame y devuelve una copia normalizada.

    Normaliza la temperatura del agua a 'temp_C' y la ambiente a 'temp_amb_C'
    (si existe). Comprueba columnas mínimas, tipos y rangos básicos.
    """
    faltan = [c for c in COLUMNAS_MINIMAS if c not in df.columns]
    if faltan:
        raise ErrorDatos(
            f"Faltan columnas obligatorias: {', '.join(faltan)}. "
            f"Se requieren al menos: {', '.join(COLUMNAS_MINIMAS)} y una de "
            f"temperatura ({', '.join(ALIAS_TEMP_AGUA)})."
        )

    col_agua = _primera_columna(df, ALIAS_TEMP_AGUA)
    if col_agua is None:
        raise ErrorDatos(
            f"No se encontró columna de temperatura del agua. "
            f"Se esperaba una de: {', '.join(ALIAS_TEMP_AGUA)}."
        )

    df = df.copy()
    df["empaque"] = df["empaque"].astype(str).str.strip()
    df = df.rename(columns={col_agua: "temp_C"})

    col_amb = _primera_columna(df, ALIAS_TEMP_AMB)
    if col_amb and col_amb != "temp_amb_C":
        df = df.rename(columns={col_amb: "temp_amb_C"})

    for col in ["repeticion", "tiempo_min", "temp_C"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if "temp_amb_C" in df.columns:
        df["temp_amb_C"] = pd.to_numeric(df["temp_amb_C"], errors="coerce")

    esenciales = ["repeticion", "tiempo_min", "temp_C"]
    nulos = df[esenciales].isna().any(axis=1)
    if nulos.any():
        filas = (df.index[nulos] + 2).tolist()
        raise ErrorDatos(
            f"Hay valores vacíos o no numéricos en las filas (del CSV): {filas}."
        )

    if (df["tiempo_min"] < 0).any():
        raise ErrorDatos("Hay tiempos negativos; el tiempo debe ser >= 0.")
    if df.empty:
        raise ErrorDatos("El archivo no contiene datos.")

    return df


def cargar_csv(ruta_o_buffer) -> pd.DataFrame:
    """Lee un CSV (ruta o buffer) y lo valida.

    Usa utf-8-sig para tolerar el BOM que genera el script del grupo.
    """
    df = pd.read_csv(ruta_o_buffer, encoding="utf-8-sig")
    return validar(df)


def temperatura_ambiente(df: pd.DataFrame, por_defecto: float = 22.0) -> float:
    """Temperatura ambiente representativa (media de la columna si existe)."""
    if "temp_amb_C" in df.columns and df["temp_amb_C"].notna().any():
        return float(df["temp_amb_C"].mean())
    return por_defecto


def params_empaque(df: pd.DataFrame, empaque: str) -> ParamsEmpaque:
    """Extrae los parámetros físicos/económicos de un empaque desde el CSV.

    Toma el primer valor no nulo de cada columna de parámetros (son constantes
    por empaque). Si una columna no existe, deja None / valores por defecto.
    """
    sub = df[df["empaque"] == empaque]
    if sub.empty:
        raise ErrorDatos(f"No hay datos para el empaque '{empaque}'.")

    def primero(col, defecto=None):
        if col in sub.columns and sub[col].notna().any():
            return sub[col].dropna().iloc[0]
        return defecto

    return ParamsEmpaque(
        empaque=empaque,
        codigo=primero("codigo_empaque"),
        conductividad_k_wmk=_float_o_none(primero("conductividad_k_wmk")),
        espesor_pared_mm=_float_o_none(primero("espesor_pared_mm")),
        area_superficial_m2=_float_o_none(primero("area_superficial_m2")),
        masa_agua_kg=float(primero("masa_agua_kg", 0.5)),
        calor_especifico_j_kgk=float(primero("calor_especifico_j_kgk", 4186.0)),
        costo_empaque_pen=float(primero("costo_empaque_pen", 0.0)),
        umbral_calidad_c=_float_o_none(primero("umbral_calidad_c")),
    )


def _float_o_none(v):
    try:
        return None if v is None else float(v)
    except (TypeError, ValueError):
        return None


def agregar(df: pd.DataFrame) -> pd.DataFrame:
    """Promedio y desviación estándar por empaque y tiempo.

    Devuelve: empaque, tiempo_min, temp_media, temp_std, n.
    Desviación muestral (ddof=1); con n=1 queda NaN -> se rellena con 0.
    """
    g = (
        df.groupby(["empaque", "tiempo_min"])["temp_C"]
        .agg(temp_media="mean", temp_std="std", n="count")
        .reset_index()
    )
    g["temp_std"] = g["temp_std"].fillna(0.0)
    return g.sort_values(["empaque", "tiempo_min"]).reset_index(drop=True)


def temperatura_en_tiempo(
    agregado: pd.DataFrame, empaque: str, tiempo_min: float
) -> float:
    """Temperatura media de un empaque en un tiempo dado (interpola si hace falta)."""
    import numpy as np

    sub = agregado[agregado["empaque"] == empaque].sort_values("tiempo_min")
    if sub.empty:
        raise ErrorDatos(f"No hay datos para el empaque '{empaque}'.")
    return float(np.interp(tiempo_min, sub["tiempo_min"], sub["temp_media"]))


def lista_empaques(df: pd.DataFrame) -> list[str]:
    """Lista de empaques en orden de aparición (conserva el orden del CSV)."""
    return list(dict.fromkeys(df["empaque"].tolist()))
