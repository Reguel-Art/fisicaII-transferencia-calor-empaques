"""Genera las figuras del informe en PNG de alta resolución.

Ejecutar:
    python generar_figuras.py

Crea en la carpeta figuras/:
    Figura1_curvas.png        Curvas de temperatura con barras de error
    Figura2_costo_barras.png  Costo por uso por empaque
    Figura3_costo_vs_T60.png  Costo por uso vs. T60 (dispersión)
    Figura4_conduccion.png    Resistencia térmica y flujo de calor por conducción
    Figura5_umbrales.png      Tiempo hasta cruzar umbrales 8/10/12 °C
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from core import analisis, datos, fisica

RAIZ = Path(__file__).resolve().parent
CSV = RAIZ / "Grupo_3_Datos_Termicos_Web.csv"
DEST = RAIZ / "figuras"
DEST.mkdir(exist_ok=True)

# Orden y nombres cortos para las figuras.
ORDEN = [
    "Control (Sin empaque)",
    "Caja de Cartón",
    "Bolsa Térmica Aluminizada",
    "Recipiente Aislante (EPS)",
]
CORTO = {
    "Control (Sin empaque)": "Control",
    "Caja de Cartón": "Cartón",
    "Bolsa Térmica Aluminizada": "Bolsa térmica",
    "Recipiente Aislante (EPS)": "EPS",
}
COLORES = {
    "Control (Sin empaque)": "#D1495B",
    "Caja de Cartón": "#EDAE49",
    "Bolsa Térmica Aluminizada": "#00798C",
    "Recipiente Aislante (EPS)": "#2E7D32",
}
MARCAS = {"Control (Sin empaque)": "o", "Caja de Cartón": "s",
          "Bolsa Térmica Aluminizada": "D", "Recipiente Aislante (EPS)": "^"}

NOTA_SIM = "SERIES SIMULADAS · NO MEDICIONES"

plt.rcParams.update({
    "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold",
    "figure.dpi": 200, "savefig.dpi": 200,
})


def _marca_sim(ax):
    ax.text(0.99, 0.02, NOTA_SIM, transform=ax.transAxes, ha="right",
            va="bottom", fontsize=8, alpha=0.6, style="italic")


def fig_curvas(df, umbral=10.0):
    ag = datos.agregar(df)
    fig, ax = plt.subplots(figsize=(9, 5))
    for emp in ORDEN:
        sub = ag[ag["empaque"] == emp].sort_values("tiempo_min")
        ax.errorbar(
            sub["tiempo_min"], sub["temp_media"], yerr=sub["temp_std"],
            label=CORTO[emp], color=COLORES[emp], marker=MARCAS[emp],
            markersize=5, linewidth=2, capsize=3, capthick=1,
        )
    ax.axhline(umbral, color="gray", linestyle="--", linewidth=1.2)
    ax.text(1, umbral + 0.3, f"Umbral {umbral:.0f} °C", color="gray", fontsize=9)
    ax.set_xlabel("Tiempo (min)")
    ax.set_ylabel("Temperatura media del agua (°C)")
    ax.set_title("Evolución de la temperatura durante 60 minutos")
    ax.set_xlim(0, 60); ax.set_xticks(np.arange(0, 61, 10))
    ax.grid(axis="y", alpha=0.3)
    ax.legend(loc="upper left", frameon=False, ncol=2)
    _marca_sim(ax)
    fig.tight_layout()
    fig.savefig(DEST / "Figura1_curvas.png", bbox_inches="tight")
    plt.close(fig)


def fig_costo_barras(res):
    r = res.set_index("empaque").loc[ORDEN].reset_index()
    fig, ax = plt.subplots(figsize=(8, 4.8))
    nombres = [CORTO[e] for e in r["empaque"]]
    barras = ax.bar(nombres, r["costo_por_uso"],
                    color=[COLORES[e] for e in r["empaque"]])
    for b, v in zip(barras, r["costo_por_uso"]):
        ax.text(b.get_x() + b.get_width() / 2, v, f"S/ {v:.3f}",
                ha="center", va="bottom", fontsize=10)
    ax.set_ylabel("Costo por uso (S/)")
    ax.set_title("Costo por uso de cada empaque")
    ax.set_ylim(0, max(r["costo_por_uso"]) * 1.2 + 0.01)
    ax.grid(axis="y", alpha=0.3)
    _marca_sim(ax)
    fig.tight_layout()
    fig.savefig(DEST / "Figura2_costo_barras.png", bbox_inches="tight")
    plt.close(fig)


def fig_costo_vs_t60(res, umbral=10.0):
    fig, ax = plt.subplots(figsize=(8, 5.2))
    for _, row in res.iterrows():
        emp = row["empaque"]
        ax.scatter(row["t60_C"], row["costo_por_uso"], s=180,
                   color=COLORES[emp], edgecolor="white", zorder=3)
        ax.annotate(CORTO[emp], (row["t60_C"], row["costo_por_uso"]),
                    textcoords="offset points", xytext=(0, 12),
                    ha="center", fontsize=10, fontweight="bold")
    ax.axvline(umbral, color="gray", linestyle="--", linewidth=1.2)
    ax.text(umbral + 0.2, ax.get_ylim()[1] * 0.9, f"Umbral {umbral:.0f} °C",
            color="gray", fontsize=9)
    ax.set_xlabel("T₆₀ (°C)   ←  conserva mejor")
    ax.set_ylabel("Costo por uso (S/)   ↓ más barato")
    ax.set_title("Costo por uso vs. temperatura a los 60 min")
    ax.grid(alpha=0.3)
    _marca_sim(ax)
    fig.tight_layout()
    fig.savefig(DEST / "Figura3_costo_vs_T60.png", bbox_inches="tight")
    plt.close(fig)


def fig_conduccion(res):
    sub = res[res["r_cond_KW"].notna()].set_index("empaque").loc[
        [e for e in ORDEN if e != "Control (Sin empaque)"]
    ].reset_index()
    nombres = [CORTO[e] for e in sub["empaque"]]
    x = np.arange(len(nombres))
    fig, ax1 = plt.subplots(figsize=(8.5, 5))
    col_r = "#3D348B"
    b = ax1.bar(x - 0.2, sub["r_cond_KW"], width=0.4, color=col_r, label="R (K/W)")
    ax1.set_ylabel("Resistencia térmica R = L/(k·A)  [K/W]", color=col_r)
    ax1.tick_params(axis="y", labelcolor=col_r)
    for bi, v in zip(b, sub["r_cond_KW"]):
        ax1.text(bi.get_x() + bi.get_width() / 2, v, f"{v:.2f}",
                 ha="center", va="bottom", fontsize=9, color=col_r)

    ax2 = ax1.twinx()
    col_q = "#E4572E"
    b2 = ax2.bar(x + 0.2, sub["qdot_cond_W"], width=0.4, color=col_q, label="Q̇ (W)")
    ax2.set_ylabel("Flujo de calor inicial Q̇ = ΔT/R  [W]", color=col_q)
    ax2.tick_params(axis="y", labelcolor=col_q)
    for bi, v in zip(b2, sub["qdot_cond_W"]):
        ax2.text(bi.get_x() + bi.get_width() / 2, v, f"{v:.2f}",
                 ha="center", va="bottom", fontsize=9, color=col_q)

    ax1.set_xticks(x); ax1.set_xticklabels(nombres)
    ax1.set_title("Ley de conducción: resistencia térmica y flujo de calor")
    _marca_sim(ax1)
    fig.tight_layout()
    fig.savefig(DEST / "Figura4_conduccion.png", bbox_inches="tight")
    plt.close(fig)


def fig_umbrales(df, res):
    t_amb = datos.temperatura_ambiente(df)
    umbrales = [8.0, 10.0, 12.0]
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(ORDEN))
    ancho = 0.25
    paleta = ["#8ECAE6", "#219EBC", "#023047"]
    for j, u in enumerate(umbrales):
        tiempos = []
        for emp in ORDEN:
            row = res[res["empaque"] == emp].iloc[0]
            k_s = row["k_fit_min"] / 60.0
            t = fisica.tiempo_a_umbral(k_s, t_amb, row["t0_C"], u) / 60.0
            tiempos.append(t if np.isfinite(t) else 0)
        barras = ax.bar(x + (j - 1) * ancho, tiempos, ancho,
                        label=f"{u:.0f} °C", color=paleta[j])
        for b, v in zip(barras, tiempos):
            if v > 0:
                ax.text(b.get_x() + b.get_width() / 2, v, f"{v:.0f}",
                        ha="center", va="bottom", fontsize=8)
    ax.axhline(60, color="red", linestyle=":", linewidth=1.2)
    ax.text(0, 62, "Entrega de 60 min", color="red", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels([CORTO[e] for e in ORDEN])
    ax.set_ylabel("Tiempo hasta alcanzar el umbral (min)")
    ax.set_title("Tiempo hasta cruzar cada umbral de temperatura")
    ax.legend(title="Umbral", frameon=False)
    ax.grid(axis="y", alpha=0.3)
    _marca_sim(ax)
    fig.tight_layout()
    fig.savefig(DEST / "Figura5_umbrales.png", bbox_inches="tight")
    plt.close(fig)


def main():
    df = datos.cargar_csv(CSV)
    res = analisis.analizar(
        df,
        usos_por_empaque={"Bolsa Térmica Aluminizada": 60,
                          "Recipiente Aislante (EPS)": 10,
                          "Caja de Cartón": 1},
        umbral_override=10.0,
    )
    fig_curvas(df)
    fig_costo_barras(res)
    fig_costo_vs_t60(res)
    fig_conduccion(res)
    fig_umbrales(df, res)
    print("Figuras generadas en:", DEST)
    for p in sorted(DEST.glob("*.png")):
        print("  -", p.name)


if __name__ == "__main__":
    main()
