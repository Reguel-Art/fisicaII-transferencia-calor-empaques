# 🧊 Comparación de empaques térmicos — Grupo 3

Herramienta web para comparar el desempeño térmico y económico de empaques
económicos usados para conservar bebidas frías durante el transporte.

**Curso:** Física II para Ingeniería · **Evaluación Continua 3** · Grupo 3.

## ¿Qué hace?

A partir de un CSV de mediciones de temperatura, la herramienta:

- Calcula promedios y desviación estándar por empaque e instante.
- Aplica el **calor sensible** (Q = m·c·ΔT) y ajusta la **constante de enfriamiento**
  por regresión lineal sobre toda la curva (con R²).
- Aplica la **ley de conducción** (R = L/(k·A), Q̇ = ΔT/R, U·A = 1/R).
- Estima el **tiempo hasta el umbral** de calidad.
- Compara **costos por uso**, con análisis de sensibilidad y S/ por °C evitado.
- Muestra curvas con barras de error, gráficos de costo y un **ranking descargable**.

## Tres formas de cargar datos (barra lateral → «1 · Datos»)

1. **📊 Ejemplo del Grupo 3**: el dataset simulado del informe.
2. **📁 Subir CSV**: tu propio archivo; hay un botón para descargar la plantilla.
3. **✏️ Ingresar / editar datos**: abre la pestaña **✏️ Datos** con dos tablas
   editables (empaques con sus parámetros, y temperaturas por instante y
   repetición). Puedes agregar o renombrar empaques, añadir instantes y cambiar
   el número de repeticiones; todo se recalcula al instante y puedes descargar
   el resultado como CSV para volver a subirlo después.

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Estructura

```
app.py                 Interfaz web (Streamlit) — punto de entrada
core/                  Núcleo de cálculo (verificado con 23 pruebas)
  fisica.py            Leyes físicas
  costos.py            Análisis económico
  datos.py             Carga y validación de CSV
  analisis.py          Motor que integra todo por empaque
tests/                 Pruebas automatizadas
data/                  Datasets de entrada (CSV)
scripts/               Utilidades de uso local
  generar_figuras.py   Genera las figuras del informe
  construir_docx.py    Ensambla el informe .docx
salidas/               Resultados generados (figuras, informe)
documentos_fuente/     Documentos .docx originales del informe
```

## Formato del CSV de entrada

Columnas: `codigo_empaque, empaque, repeticion, tiempo_min, temp_agua_c,
temp_ambiente_c, conductividad_k_wmk, espesor_pared_mm, area_superficial_m2,
masa_agua_kg, calor_especifico_j_kgk, costo_empaque_pen, umbral_calidad_c`.

## Pruebas

```bash
python tests/test_fisica.py
python tests/test_costos_datos.py
python tests/test_analisis.py
python tests/test_editor.py
```

---

> Los datos incluidos son **simulados**. Reemplázalos con mediciones reales
> antes de informar resultados experimentales.
