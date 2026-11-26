# %% [markdown]
# # Cálculo reproducible · TermoPack
# Física II · Grupo 3 · Gaseosa de 600 mL, T₀ = 12,5 °C, ambiente 24,0 °C

# %%
# Librerías
import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# %% [markdown]
# ## Datos experimentales
# 13 lecturas por configuración, cada 5 minutos (Tabla 5 del informe).

# %%
RAIZ = Path(__file__).resolve().parents[1] if "__file__" in globals() else Path.cwd()
if not (RAIZ / "data").exists():          # ventana interactiva abierta desde scripts/
    RAIZ = RAIZ.parent
df = pd.read_csv(RAIZ / "data" / "Grupo_3_Datos_Termicos_Web.csv")

NOMBRES = {"CTRL": "Sin empaque", "CART": "Cartón", "BOLS": "Bolsa térmica", "EPS": "Tecnopor"}
lecturas = (df.pivot(index="tiempo_min", columns="codigo_empaque", values="temp_agua_c")
              [list(NOMBRES)].rename(columns=NOMBRES).rename_axis(columns=None))
lecturas

# %% [markdown]
# ## Calor sensible y constante de calentamiento
# $$Q = m\,c\,(T_{60} - T_0) \qquad k = -\frac{1}{60}\ln\frac{T_a - T_{60}}{T_a - T_0}$$

# %%
T0, Ta, m, c = 12.5, 24.0, 0.60, 4186          # °C, °C, kg, J/(kg·°C)

T60 = lecturas.loc[60]
Q = m * c * (T60 - T0) / 1000                  # kJ
k = -((Ta - T60) / (Ta - T0)).apply(math.log) / 60
evitado = (Q["Sin empaque"] - Q) / Q["Sin empaque"] * 100

resultados = pd.DataFrame({
    "T60 (°C)": T60,
    "ΔT (°C)": (T60 - T0).round(1),
    "Q (kJ)": Q.round(2),
    "Calor evitado (%)": evitado.round(2),
    "k (1/min)": k.round(5),
})
resultados

# %% [markdown]
# ## Evaluación económica
# Costo por uso = precio ÷ usos · costo por kJ evitado = costo por uso ÷ (Q del control − Q)

# %%
precio = pd.Series({"Sin empaque": 0.00, "Cartón": 0.80, "Bolsa térmica": 40.00, "Tecnopor": 30.00})
usos = pd.Series({"Sin empaque": 1, "Cartón": 1, "Bolsa térmica": 60, "Tecnopor": 10})

por_uso = precio / usos
q_evitado = Q["Sin empaque"] - Q
economia = pd.DataFrame({
    "Precio (S/)": precio,
    "Usos": usos,
    "S/ por uso": por_uso.round(2),
    "Q evitado (kJ)": q_evitado.round(2),
    "S/ por kJ": (por_uso / q_evitado).where(q_evitado > 0).round(2),
})
economia

# %% [markdown]
# ## Evolución de la temperatura
# La línea punteada horizontal es la temperatura ambiente del ensayo.

# %%
COLORES = {"Sin empaque": "#868C93", "Cartón": "#D2691E",
           "Bolsa térmica": "#2E9FB5", "Tecnopor": "#3B5BC4"}

fig, ax = plt.subplots(figsize=(8, 4.5))
for nombre, serie in lecturas.items():
    ax.plot(serie.index, serie, marker="o", markersize=4, linewidth=2, color=COLORES[nombre],
            linestyle="--" if nombre == "Sin empaque" else "-", label=nombre)
ax.axhline(Ta, color="#5F6B85", linestyle=":", linewidth=1)
ax.text(1, Ta + 0.2, "Ambiente 24,0 °C", color="#5F6B85", fontsize=9)
ax.set(xlabel="Tiempo (min)", ylabel="Temperatura de la gaseosa (°C)", xlim=(0, 61), ylim=(12, 25))
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", alpha=0.3)
ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.15))
plt.tight_layout()
plt.show()

# %% [markdown]
# ## Predicción para la recomendación
# Bolsa térmica, bebida despachada a 5 °C, entrega de 30 minutos:
# $$T(t) = T_a + (T_0 - T_a)\,e^{-k t}$$

# %%
k_bolsa = k["Bolsa térmica"]
T30 = Ta + (5 - Ta) * math.exp(-k_bolsa * 30)
print(f"k = {k_bolsa:.5f} 1/min  →  T(30) = {T30:.2f} °C")
