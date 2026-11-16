# Textos y tablas para el informe (resultados reales de la herramienta)

> Generado a partir de `Grupo_3_Datos_Termicos_Web.csv` (156 lecturas: 4 configuraciones × 3 repeticiones × 13 instantes, 0–60 min).
> Parámetros del escenario: T₀ = 3,0 °C; T ambiente = 22,0 °C; m = 0,50 kg de agua; c = 4186 J/(kg·°C); A = 0,04 m².
> **Origen: SIMULACIÓN. No son mediciones de laboratorio.** Mantener esta aclaración hasta tomar datos reales.

---

## Sección 4 — Presentación de datos (texto para actualizar)

Para ilustrar el procedimiento de análisis se emplearon series con tres repeticiones por configuración. Se simularon 500 mL de agua a 3,0 °C, una temperatura ambiente de 22,0 °C y lecturas cada cinco minutos durante una hora. El procesamiento calcula, para cada empaque, la temperatura media por instante y su desviación estándar entre repeticiones, de modo que las curvas de la Figura 1 pueden presentarse con barras de error. Ninguna cifra de esta sección constituye una medición obtenida por el grupo.

### Tabla 7. Temperatura media del agua por intervalo y configuración (°C)

| Tiempo (min) | Control (sin empaque) | Caja de cartón | Bolsa térmica aluminizada | Recipiente EPS |
|---:|---:|---:|---:|---:|
| 0  | 3,00  | 3,00  | 3,00  | 3,0 |
| 10 | 7,80  | 6,50  | 5,30  | 4,0 |
| 20 | 11,97 | 9,80  | 7,47  | 5,0 |
| 30 | 15,43 | 12,67 | 9,47  | 6,0 |
| 40 | 18,23 | 15,20 | 11,27 | 7,0 |
| 50 | 20,17 | 17,27 | 12,87 | 7,9 |
| 60 | 21,47 | 18,93 | 14,27 | 8,7 |

*Nota. SIMULACIÓN DIDÁCTICA, no datos experimentales. Promedios de tres repeticiones; se muestran cortes cada diez minutos. El CSV adjunto conserva las 156 lecturas (cada 5 min).*

---

## Sección 5.1 — Calor absorbido por el agua (texto + tabla)

Se aplicó el principio de calor sensible, Q = m·c·ΔT, con m = 0,50 kg, c = 4186 J/(kg·°C) y ΔT = T₆₀ − T₀. El resultado representa la energía ganada por el agua y no incluye la almacenada en la botella ni en el empaque. Como ejemplo, para el recipiente de EPS: Q = 0,50 × 4186 × (8,70 − 3,00) ≈ 11 930 J ≈ 11,93 kJ.

Adicionalmente se estimó la **constante de enfriamiento efectiva (k)** ajustando por **regresión lineal sobre los trece puntos** de cada serie el modelo linealizado ln[(Tₐ − T)/(Tₐ − T₀)] = −k·t. A diferencia de un ajuste con solo dos puntos (minutos 0 y 60), la regresión usa toda la curva y permite reportar la bondad del ajuste (R²).

### Tabla 8. Resultados térmicos derivados de la simulación de 60 minutos

| Configuración | T₆₀ (°C) | ΔT (°C) | Q (kJ) | k ef. (min⁻¹) | R² |
|---|---:|---:|---:|---:|---:|
| Control (sin empaque)      | 21,47 | 18,47 | 38,65 | 0,05534 | 0,941 |
| Caja de cartón             | 18,93 | 15,93 | 33,35 | 0,03000 | 0,985 |
| Bolsa térmica aluminizada  | 14,27 | 11,27 | 23,58 | 0,01503 | 0,998 |
| Recipiente EPS             |  8,70 |  5,70 | 11,93 | 0,00604 | 0,999 |

*Nota. SIMULACIÓN. La k ef. se obtuvo por regresión lineal del modelo de enfriamiento newtoniano (T ambiente = 22 °C). Los R² altos confirman que el modelo exponencial describe bien las series. La k ef. no equivale a la conductividad térmica del material.*

---

## Sección 5.2 (NUEVA) — Ley de transferencia de calor por conducción

> **Esta sección responde a la observación de que el informe solo usaba calor sensible (Q = mcΔT) y no una ley de transferencia.** Es el aporte físico más importante del avance.

Además del calor sensible, se aplicó la **ley de conducción de calor** a la pared aislante de cada empaque. La resistencia térmica por conducción se calcula como

$$ R = \frac{L}{k \cdot A} $$

donde L es el espesor de la pared, k la conductividad del material y A el área de intercambio (0,04 m²). El flujo de calor inicial que atraviesa la pared es

$$ \dot{Q} = \frac{\Delta T}{R} = \frac{T_a - T_0}{R} $$

y la conductancia global por conducción resulta U·A = 1/R. La Tabla 9 muestra estos valores con los datos de cada empaque (ΔT inicial = 22 − 3 = 19 °C).

### Tabla 9. Resistencia térmica y flujo de calor por conducción

| Configuración | k [W/(m·K)] | L (mm) | R = L/(k·A) [K/W] | U·A conductivo [W/K] | Q̇ inicial [W] |
|---|---:|---:|---:|---:|---:|
| Caja de cartón            | 0,065 |  3 | 1,154 | 0,867 | 16,47 |
| Bolsa térmica aluminizada | 0,045 |  5 | 2,778 | 0,360 | 6,84 |
| Recipiente EPS            | 0,038 | 15 | 9,868 | 0,101 | 1,93 |

*Nota. El control no tiene pared aislante propia, por lo que no se calcula R. Un mayor espesor y menor conductividad elevan la resistencia R y reducen el flujo de calor Q̇: el EPS, con 15 mm de pared, ofrece la mayor resistencia (9,87 K/W) y el menor flujo inicial (1,93 W).*

### Comparación entre el U·A teórico (conducción) y el U·A medido (enfriamiento)

El modelo de enfriamiento también permite estimar la conductancia global como U·A = k·m·c (con k en s⁻¹). Comparar este valor "medido" con el U·A puramente conductivo cuantifica el peso de los demás mecanismos (convección del aire y del líquido, la propia botella):

### Tabla 10. U·A teórico frente a U·A ajustado

| Configuración | U·A conductivo [W/K] | U·A ajustado = k·m·c [W/K] | Cociente ajustado/conductivo |
|---|---:|---:|---:|
| Caja de cartón            | 0,867 | 1,046 | 1,21 |
| Bolsa térmica aluminizada | 0,360 | 0,524 | 1,46 |
| Recipiente EPS            | 0,101 | 0,211 | 2,08 |

*Nota. El U·A ajustado es sistemáticamente mayor que el conductivo. En el EPS el ajustado duplica al teórico (cociente 2,08), lo que evidencia que la transferencia real no ocurre solo por conducción en la pared: la convección y la botella aportan una fracción creciente a medida que el aislamiento mejora. Esto confirma numéricamente lo señalado en la sección 2.2: **U describe el sistema completo y no equivale a la conductividad k de un material.***

---

## Sección 5.3 — Análisis económico con sensibilidad de usos

El costo por uso se calculó como precio de compra dividido entre el número de usos. Dado que el resultado depende fuertemente de ese supuesto —señalado como punto crítico—, se presenta un **análisis de sensibilidad** para distintos números de usos.

### Tabla 11. Costo por uso (S/) según el número de usos supuesto

| Empaque | Precio (S/) | 1 uso | 10 usos | 30 usos | 60 usos |
|---|---:|---:|---:|---:|---:|
| Control (sin empaque)      | 0,00 | 0,000 | 0,000 | 0,000 | 0,000 |
| Caja de cartón             | 0,50 | 0,500 | 0,050 | 0,017 | 0,008 |
| Bolsa térmica aluminizada  | 2,50 | 2,500 | 0,250 | 0,083 | 0,042 |
| Recipiente EPS             | 3,00 | 3,000 | 0,300 | 0,100 | 0,050 |

*Nota. Precios hipotéticos en soles; no incluyen limpieza, desgaste ni reposición. El costo por uso cae de forma inversamente proporcional al número de usos: la ventaja de un empaque reutilizable solo se materializa si realmente se reutiliza muchas veces.*

Para integrar desempeño térmico y costo se usó el indicador **soles por °C evitado** respecto al control (cuántos grados menos se calentó la bebida frente a no usar empaque, al minuto 60). La Tabla 12 combina un supuesto de uso realista por empaque.

### Tabla 12. Indicador combinado costo–desempeño (a los 60 min)

| Empaque | Usos sup. | Costo/uso (S/) | °C evitados vs. control | S/ por °C evitado |
|---|---:|---:|---:|---:|
| Bolsa térmica aluminizada | 60 | 0,042 | 7,20 | **0,0058** |
| Recipiente EPS            | 10 | 0,300 | 12,77 | 0,0235 |
| Caja de cartón            |  1 | 0,500 | 2,54 | 0,1974 |

*Nota. "°C evitados" = T₆₀ del control (21,47 °C) menos la T₆₀ del empaque. La bolsa térmica logra el menor costo por grado evitado gracias a su reutilización; el EPS es el que más grados evita en términos absolutos, pero con un costo por uso mayor.*

---

## Sección 5.4 — Tiempo hasta el umbral de calidad (umbral justificado con varios valores)

> **Responde a la crítica de que el umbral de 10 °C era arbitrario.** Se presenta el tiempo que tarda cada empaque en alcanzar tres umbrales.

A partir del modelo ajustado se calculó el tiempo que tarda la bebida en cruzar distintos umbrales de calidad, mediante t = −ln[(Tₐ − T_umbral)/(Tₐ − T₀)] / k.

### Tabla 13. Tiempo (min) hasta alcanzar cada umbral de temperatura

| Configuración | 8 °C | 10 °C | 12 °C |
|---|---:|---:|---:|
| Control (sin empaque)      |  5,5 |  8,3 | 11,6 |
| Caja de cartón             | 10,2 | 15,3 | 21,4 |
| Bolsa térmica aluminizada  | 20,3 | 30,6 | 42,7 |
| Recipiente EPS             | 50,6 | 76,1 | 106,3 |

*Nota. Valores derivados del modelo ajustado (los del EPS para 10 y 12 °C son extrapolaciones más allá de los 60 min medidos). Para una entrega de una hora con objetivo de 10 °C, solo el EPS mantiene la bebida bajo el umbral durante todo el trayecto; la bolsa térmica lo cruza a los ~31 min.*

---

## Sección 6 — Conclusiones (versión actualizada con resultados reales)

**Conclusión 1.** El modelo mostró un aumento de temperatura de 5,70 °C en el recipiente de EPS frente a 18,47 °C en el control durante 60 minutos; es decir, el EPS redujo el calentamiento en ~69 %. Los altos valores de R² (0,94–0,999) confirman que el modelo de enfriamiento newtoniano describe bien las series, aunque esto no constituye todavía una comprobación experimental.

**Conclusión 2.** Al aplicar la ley de conducción R = L/(k·A), el EPS presentó la mayor resistencia térmica (9,87 K/W) y el menor flujo de calor inicial (1,93 W), coherente con su mayor espesor de pared (15 mm). La comparación entre el U·A conductivo y el ajustado (cociente de hasta 2,08 en el EPS) evidencia que la convección y la botella aportan una parte importante de la transferencia real, confirmando que U ≠ k del material.

**Conclusión 3.** El análisis de sensibilidad mostró que el ranking económico depende del número de usos: con 60 usos, la bolsa térmica alcanza el menor costo por uso (S/ 0,042) y el menor costo por °C evitado (S/ 0,0058). Sin reutilización elevada, esta ventaja desaparece. La decisión empresarial, por tanto, depende tanto de la exigencia de temperatura como de la reutilización real, la limpieza y el desgaste.

**Conclusión 4.** Existe una disyuntiva entre conservación y costo: el EPS es el que mejor conserva el frío (T₆₀ = 8,70 °C, único que cumple el umbral de 10 °C a los 60 min), mientras que la bolsa térmica ofrece el mejor equilibrio costo–desempeño cuando se reutiliza. La elección final debe validarse con mediciones reales y cotizaciones locales.

---

## Anexo — Nota metodológica sobre la herramienta

El procesamiento se realizó con una herramienta en Python (módulos de cálculo verificados con 23 pruebas automatizadas y una interfaz web en Streamlit). La herramienta importa el CSV de lecturas, calcula promedios y desviaciones por intervalo, estima ΔT, Q y la constante de enfriamiento por regresión, aplica la ley de conducción, evalúa el tiempo al umbral y compara costos, generando curvas con barras de error, gráficos de costo y una tabla de ranking descargable. Está preparada para procesar mediciones reales con el mismo formato cuando se realicen.
