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

## Secciones de la app (TermoPack)

- **Vista general:** indicadores clave, curvas de temperatura con bandas de
  desviación, recomendación y comparativo. «Configurar experimento» fija el
  límite de temperatura y el tiempo de entrega.
- **Laboratorio 3D:** las cuatro botellas de 500 mL dentro de sus empaques, en 3D y a
  la misma escala. El agua cambia de color con su temperatura minuto a minuto
  (control deslizante o «Reproducir»), y unas flechas muestran el calor que entra
  (largo proporcional a Q̇ = U·A·(T ambiente − T agua)). Vista en corte o completa.
- **Datos del experimento:** usar el ejemplo del Grupo 3, subir un CSV (con
  plantilla descargable) o escribir/editar las mediciones en la propia app.
- **Evaluación económica:** precio, usos, limpieza y otros costos por material;
  pedidos, costo máximo y peso conservación/costo. Ranking con puntaje.
- **Fundamento físico:** modelo de Newton y fórmulas (Q, k_ef, R) evaluadas en
  el tiempo de entrega.

Una alternativa es **viable** si todas sus lecturas hasta el tiempo de entrega
quedan bajo el límite, tiene costo registrado y no supera el costo máximo.

## Ejecutar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Estructura

```
app.py                 Punto de entrada (estilo, barra lateral, navegación)
paginas/               Vista general · Datos · Evaluación económica · Fundamento físico
ui/                    Estado compartido, estilos TermoPack y gráficos
editor.py              Editor de datos dentro de la app
core/                  Núcleo de cálculo verificado con pruebas
  fisica.py            Leyes físicas
  costos.py            Indicadores económicos
  decision.py          Viabilidad y puntaje de alternativas
  datos.py             Carga y validación de CSV
  analisis.py          Motor que integra todo por empaque
tests/                 Pruebas automatizadas
data/                  Datasets de entrada (CSV)
scripts/               Utilidades (figuras, informe, CSV de ejemplo)
salidas/               Resultados generados (figuras, informe)
assets/                Logo de la universidad (paleta de la app)
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
python tests/test_decision.py
python tests/test_estado.py
```

---

> Los datos incluidos son **simulados**. Reemplázalos con mediciones reales
> antes de informar resultados experimentales.
