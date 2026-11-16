"""Análisis económico de los empaques térmicos.

Indicadores:
  - costo_por_uso = precio / número de usos
  - soles por °C evitado: cuánto cuesta (por uso) cada grado centígrado que
    el empaque "ahorra" respecto al control, en una ventana de tiempo dada.
  - sensibilidad de usos: cómo cambia el costo por uso al variar el número
    de usos (el documento señala que el supuesto de 60 usos decide el ranking).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class IndicadorCosto:
    empaque: str
    precio: float          # S/ (precio de compra del empaque)
    usos: int              # número de usos estimados
    costo_por_uso: float   # S/ por uso
    delta_evitado: float   # °C evitados respecto al control (en la ventana)
    soles_por_C: float     # S/ por °C evitado (inf si no evita nada)


def costo_por_uso(precio: float, usos: int) -> float:
    """Costo por uso = precio / usos. usos debe ser >= 1."""
    if usos < 1:
        raise ValueError("El número de usos debe ser al menos 1.")
    return precio / usos


def soles_por_grado_evitado(
    costo_uso: float,
    temp_empaque: float,
    temp_control: float,
) -> float:
    """S/ por °C evitado respecto al control, en un instante dado.

    'Grados evitados' = cuánto MENOS se calentó la bebida en este empaque
    frente al control (temp_control - temp_empaque). Si el empaque no mejora
    al control (<= 0 grados evitados) devuelve infinito.
    """
    delta_evitado = temp_control - temp_empaque
    if delta_evitado <= 0:
        return float("inf")
    return costo_uso / delta_evitado


def indicador_completo(
    empaque: str,
    precio: float,
    usos: int,
    temp_empaque: float,
    temp_control: float,
) -> IndicadorCosto:
    """Construye el indicador de costo completo para un empaque."""
    cu = costo_por_uso(precio, usos)
    delta = temp_control - temp_empaque
    spc = soles_por_grado_evitado(cu, temp_empaque, temp_control)
    return IndicadorCosto(
        empaque=empaque,
        precio=precio,
        usos=usos,
        costo_por_uso=cu,
        delta_evitado=delta,
        soles_por_C=spc,
    )


def sensibilidad_usos(
    precio: float,
    lista_usos: list[int],
) -> dict[int, float]:
    """Costo por uso para distintos números de usos.

    Devuelve {usos: costo_por_uso}. Pensado para el análisis de sensibilidad
    recomendado en la revisión (ej. 10, 30, 60 usos).
    """
    return {u: costo_por_uso(precio, u) for u in lista_usos}


def usos_de_equilibrio(
    precio_reutilizable: float,
    costo_uso_desechable: float,
) -> float:
    """Número de usos a partir del cual un empaque reutilizable es más barato
    por uso que una opción desechable de costo fijo por uso.

        precio_reutilizable / usos <= costo_uso_desechable
        =>  usos >= precio_reutilizable / costo_uso_desechable
    """
    if costo_uso_desechable <= 0:
        raise ValueError("El costo por uso del desechable debe ser positivo.")
    return precio_reutilizable / costo_uso_desechable
