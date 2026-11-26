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
- **Laboratorio 3D:** las cuatro botellas de 600 mL dentro de sus empaques, en 3D y a
  la misma escala. El agua cambia de color con su temperatura minuto a minuto
  (control deslizante o «Reproducir»), y unas flechas muestran el calor que entra
  (largo proporcional a Q̇ = U·A·(T ambiente − T agua)). Vista en corte o completa.
- **Simulador por ciudad:** ¿cómo le iría a cada empaque en otro departamento? Con la k
  medida de cada empaque y la ley de Newton, predice la temperatura de entrega, el calor
  absorbido (Q = m·c·ΔT) y el minuto en que se pasa el límite, para la temperatura de la
  capital elegida (normales climáticas en `data/ciudades_peru.csv`, con su fuente).
  Incluye un mapa del Perú, un factor de viento («en moto», ilustrativo) y una
  **votación en vivo**: el público escanea un código QR y vota desde su celular
  (página `/votar`). Para que el QR sirva, abre la app con la dirección de red
  (la «Network URL» que muestra Streamlit) y conecta los celulares a la misma WiFi.
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
python tests/test_escenarios.py
```

---

> Los datos incluidos son las **mediciones reales del grupo** (Tabla 7 de la parte
> experimental): gaseosa de 600 mL, T₀ = 12,5 °C, ambiente 24,0 °C, una lectura cada
> 5 min durante 60 min. Precios cotizados: cartón S/ 0,80, bolsa térmica S/ 40,00 y
> tecnopor S/ 30,00. Conductividad, espesor y área no se midieron: son valores de referencia.
