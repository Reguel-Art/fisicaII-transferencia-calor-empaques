"""Motor de análisis: integra física y costos por empaque.

A partir del DataFrame validado (esquema web), calcula para cada empaque el
resumen térmico y económico que alimenta las tablas y gráficos de la herramienta.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from core import costos, datos, fisica


@dataclass
class ResumenEmpaque:
    empaque: str
    codigo: str | None
    # --- térmico ---
    t0_C: float                 # temperatura inicial (t=0)
    t60_C: float                # temperatura final (último tiempo)
    delta_T: float              # T_final - T_inicial
    q_absorbido_J: float        # calor sensible Q = m·c·ΔT
    k_fit_min: float            # constante de enfriamiento ajustada [1/min]
    r2: float                   # bondad del ajuste
    ua_fit_WK: float            # U·A desde el ajuste = k·m·c [W/K]
    # --- ley de conducción (si hay k material, espesor, área) ---
    r_cond_KW: float | None     # resistencia conductiva R = L/(k·A) [K/W]
    ua_cond_WK: float | None    # U·A conductivo = 1/R [W/K]
    qdot_cond_W: float | None   # flujo inicial Q̇ = ΔT/R [W]
    # --- umbral ---
    umbral_C: float | None
    t_umbral_min: float | None  # tiempo hasta cruzar el umbral [min]
    # --- económico ---
    costo_empaque: float
    usos: int
    costo_por_uso: float
    soles_por_C_evitado: float  # frente al control


def _serie_media(df: pd.DataFrame, empaque: str) -> tuple[np.ndarray, np.ndarray]:
    sub = (
        df[df["empaque"] == empaque]
        .groupby("tiempo_min")["temp_C"]
        .mean()
        .reset_index()
        .sort_values("tiempo_min")
    )
    return sub["tiempo_min"].to_numpy(float), sub["temp_C"].to_numpy(float)


def analizar(
    df: pd.DataFrame,
    usos_por_empaque: dict[str, int] | None = None,
    umbral_override: float | None = None,
    control: str | None = None,
) -> pd.DataFrame:
    """Calcula el resumen de todos los empaques.

    Parameters
    ----------
    df : DataFrame validado (core.datos.validar).
    usos_por_empaque : usos estimados por empaque (dict empaque->usos). Por
        defecto 1 para todos (se ajusta desde la interfaz / sensibilidad).
    umbral_override : si se da, reemplaza el umbral del CSV para todos.
    control : nombre del empaque de referencia. Si None, se detecta el que
        tenga código 'CTRL' o el que contenga 'control' en el nombre.

    Returns
    -------
    DataFrame con una fila por empaque (columnas = campos de ResumenEmpaque).
    """
    usos_por_empaque = usos_por_empaque or {}
    empaques = datos.lista_empaques(df)
    t_amb = datos.temperatura_ambiente(df)

    control = control or _detectar_control(df, empaques)

    # T60 del control para el indicador S/°C evitado.
    t60_control = None
    if control is not None:
        _, Tc = _serie_media(df, control)
        t60_control = float(Tc[-1])

    filas = []
    for emp in empaques:
        p = datos.params_empaque(df, emp)
        t_min, T = _serie_media(df, emp)
        t0, t60 = float(T[0]), float(T[-1])
        delta = t60 - t0

        q = fisica.calor_sensible(p.masa_agua_kg, p.calor_especifico_j_kgk, delta)

        # Ajuste de k por regresión sobre toda la serie (en segundos).
        k_fit_min, r2, ua_fit = np.nan, np.nan, np.nan
        try:
            aj = fisica.ajustar_k(t_min * 60.0, T, t_amb, t0)
            k_fit_min = aj.k_por_min
            r2 = aj.r2
            ua_fit = fisica.conductancia_UA(aj.k, p.masa_agua_kg, p.calor_especifico_j_kgk)
        except ValueError:
            pass  # p. ej. el control llega casi al ambiente: ln inestable

        # Ley de conducción (requiere k material, espesor y área > 0).
        r_cond = ua_cond = qdot = None
        if (
            p.conductividad_k_wmk
            and p.espesor_pared_mm
            and p.area_superficial_m2
            and p.espesor_pared_mm > 0
        ):
            L = p.espesor_pared_mm / 1000.0  # mm -> m
            r_cond = fisica.resistencia_conduccion(L, p.conductividad_k_wmk, p.area_superficial_m2)
            ua_cond = 1.0 / r_cond
            qdot = fisica.flujo_calor_conduccion(t_amb - t0, r_cond)

        # Umbral.
        umbral = umbral_override if umbral_override is not None else p.umbral_calidad_c
        t_umbral = None
        if umbral is not None and not np.isnan(k_fit_min) and k_fit_min > 0:
            seg = fisica.tiempo_a_umbral(k_fit_min / 60.0, t_amb, t0, umbral)
            t_umbral = seg / 60.0 if np.isfinite(seg) else float("inf")

        # Económico.
        usos = int(usos_por_empaque.get(emp, 1))
        costo_uso = costos.costo_por_uso(p.costo_empaque_pen, usos) if usos >= 1 else 0.0
        spc = float("inf")
        if t60_control is not None:
            spc = costos.soles_por_grado_evitado(costo_uso, t60, t60_control)

        filas.append(
            ResumenEmpaque(
                empaque=emp,
                codigo=p.codigo,
                t0_C=round(t0, 2),
                t60_C=round(t60, 2),
                delta_T=round(delta, 2),
                q_absorbido_J=round(q, 1),
                k_fit_min=round(k_fit_min, 5) if not np.isnan(k_fit_min) else np.nan,
                r2=round(r2, 4) if not np.isnan(r2) else np.nan,
                ua_fit_WK=round(ua_fit, 4) if not np.isnan(ua_fit) else np.nan,
                r_cond_KW=round(r_cond, 3) if r_cond is not None else None,
                ua_cond_WK=round(ua_cond, 4) if ua_cond is not None else None,
                qdot_cond_W=round(qdot, 3) if qdot is not None else None,
                umbral_C=umbral,
                t_umbral_min=(round(t_umbral, 1) if t_umbral not in (None, float("inf")) else t_umbral),
                costo_empaque=p.costo_empaque_pen,
                usos=usos,
                costo_por_uso=round(costo_uso, 4),
                soles_por_C_evitado=(round(spc, 4) if np.isfinite(spc) else spc),
            )
        )

    return pd.DataFrame([asdict(f) for f in filas])


def _detectar_control(df: pd.DataFrame, empaques: list[str]) -> str | None:
    """Detecta el empaque de control (código CTRL o nombre con 'control')."""
    if "codigo_empaque" in df.columns:
        ctrl = df[df["codigo_empaque"].astype(str).str.upper() == "CTRL"]
        if not ctrl.empty:
            return ctrl["empaque"].iloc[0]
    for e in empaques:
        if "control" in e.lower() or "sin empaque" in e.lower():
            return e
    return None


def ranking(resumen: pd.DataFrame, por: str = "soles_por_C_evitado") -> pd.DataFrame:
    """Ordena el resumen para construir la tabla de ranking.

    Por defecto ordena por mejor eficiencia costo-beneficio (S/ por °C evitado,
    menor es mejor). El control (inf) queda al final.
    """
    r = resumen.copy()
    r["_orden"] = pd.to_numeric(r[por], errors="coerce").replace([np.inf], np.nan)
    r = r.sort_values("_orden", na_position="last").drop(columns="_orden")
    r.insert(0, "puesto", range(1, len(r) + 1))
    return r.reset_index(drop=True)
