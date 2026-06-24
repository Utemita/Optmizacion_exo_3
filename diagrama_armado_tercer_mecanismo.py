"""
diagrama_armado_tercer_mecanismo.py
===================================
Genera un DIAGRAMA DE ARMADO limpio del tercer mecanismo de 4 barras (IFD/DIP),
pensado para guiar el modelado en CAD.

Convencion de lineas (segun pedido):
  - ESLABONES RIGIDOS FABRICADOS  -> LINEA CONTINUA (negra, gruesa)
        * Soporte/bancada S3 (tierra Pa-IFP, fija a la falange proximal)
        * Acoplador  L9  (D3 -> Pa)
        * Balancin   L10 (IFD -> D3), rigido con la falange distal
  - FALANGES DEL DEDO (huesos, NO se fabrican) -> LINEA PUNTEADA (gris)
        * Falange proximal (MCF -> IFP)
        * Falange medial   (IFP -> IFD)  [hace de manivela del 4 barras]
        * Falange distal   (IFD -> punta)

Estilo B/N de ingenieria. Usa la cinematica REAL del modulo.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import cinematica_tercer_mecanismo as K


def pose(j, gamma=None, dorsal=None):
    est = K.cinematica_paso(float(j))
    tm = K.tercer_mecanismo(est, gamma_bracket=gamma, dorsal_sign=dorsal)
    return est, tm


def dibujar():
    # Calibrar en reposo y obtener pose de reposo y pose flexionada
    est0, tm0 = pose(0)
    gamma, dorsal = tm0["gamma_bracket"], tm0["dorsal_sign"]
    est0, tm0 = pose(0, gamma, dorsal)
    estF, tmF = pose(132, gamma, dorsal)

    MCF = est0["MCF"]; IFP = est0["IFP"]; IFD = est0["IFD"]
    PF = tm0["PF"]; D3 = tm0["D3"]; Pa = tm0["Pa"]
    P3 = est0["P3"]   # punta del balancin de salida del 2.o mecanismo (4 barras)

    fig, ax = plt.subplots(figsize=(13, 9.5))
    ax.set_facecolor("white")

    SOLID = dict(color="black", lw=2.6, solid_capstyle="round", zorder=5)
    SOLID2 = dict(color="#1f4e79", lw=2.6, solid_capstyle="round", zorder=5)  # 2.o mec.
    DASH  = dict(color="0.45", lw=1.8, linestyle=(0, (1, 2)), zorder=3)  # punteada
    GHOST = dict(color="0.8", lw=1.4, zorder=1)

    # --- Pose flexionada (fantasma, para indicar el movimiento) ---
    for a, b in [(estF["MCF"], estF["IFP"]), (estF["IFP"], estF["IFD"]),
                 (estF["IFD"], tmF["PF"]), (estF["IFD"], tmF["D3"]),
                 (tmF["D3"], tmF["Pa"]), (tmF["Pa"], estF["IFP"]),
                 (estF["IFP"], estF["P3"])]:
        ax.plot([a[0], b[0]], [a[1], b[1]], **GHOST)

    # --- Falanges (PUNTEADA) ---
    ax.plot([MCF[0], IFP[0]], [MCF[1], IFP[1]], **DASH)
    ax.plot([IFP[0], IFD[0]], [IFP[1], IFD[1]], **DASH)
    ax.plot([IFD[0], PF[0]],  [IFD[1], PF[1]],  **DASH)

    # --- Eslabones rigidos fabricados (CONTINUA) ---
    ax.plot([Pa[0], IFP[0]], [Pa[1], IFP[1]], **SOLID)   # tierra / soporte S3
    ax.plot([D3[0], Pa[0]],  [D3[1], Pa[1]],  **SOLID)   # acoplador L9
    ax.plot([IFD[0], D3[0]], [IFD[1], D3[1]], **SOLID)   # balancin L10

    # --- Barra rigida del 2.o MECANISMO: IFP -> P3 (c2) -------------------
    # P3 NO flota: es la punta del balancin de salida del segundo 4 barras,
    # que pivota en la IFP. Esta barra (c2 = 46.01 mm) es un cuerpo RIGIDO con
    # la falange medial (mismo solido, offset angular fijo THETAauxfm = 51.39).
    ax.plot([IFP[0], P3[0]], [IFP[1], P3[1]], **SOLID2)  # balancin 2.o mec (c2)

    # Arco que evidencia el offset RIGIDO entre la barra IFP->P3 y la falange
    # medial (IFP->IFD): ambos son el MISMO cuerpo rigido (THETAauxfm fijo).
    def arc_menor(a, b):
        """Devuelve (theta1, theta2, theta_medio) del ARCO MENOR (<=180) que
        va del angulo a al angulo b, dibujado CCW por matplotlib.Arc."""
        d = ((b - a + 180) % 360) - 180
        t1, t2 = (a, a + d) if d >= 0 else (a + d, a)
        return t1, t2, (t1 + t2) / 2.0

    def dibujar_arco(centro, ang_a, ang_b, radio, color, texto, ls="--",
                     lw=1.2, rtxt=None, fs=7.8):
        t1, t2, tm_ang = arc_menor(ang_a, ang_b)
        arc = plt.matplotlib.patches.Arc(centro, radio, radio, angle=0,
                                         theta1=t1, theta2=t2,
                                         color=color, lw=lw, ls=ls, zorder=4)
        ax.add_patch(arc)
        r = rtxt if rtxt is not None else radio * 0.9 + 14
        amid = np.radians(tm_ang)
        ax.annotate(texto,
                    centro + r * np.array([np.cos(amid), np.sin(amid)]),
                    fontsize=fs, ha="center", va="center", color=color)

    aP3 = np.degrees(np.arctan2(P3[1] - IFP[1], P3[0] - IFP[0]))
    aFM = np.degrees(np.arctan2(IFD[1] - IFP[1], IFD[0] - IFP[0]))
    dibujar_arco(IFP, aP3, aFM, 26, "#1f4e79",
                 "ang. AUXILIAR\nTHETAauxfm=51.39\n(IFP->P3 a falange medial,\n"
                 "mismo cuerpo rigido)", rtxt=34)

    # --- Arco que marca el angulo rigido balancin<->falange distal en IFD ---
    a1 = np.degrees(np.arctan2(D3[1] - IFD[1], D3[0] - IFD[0]))
    a2 = np.degrees(np.arctan2(PF[1] - IFD[1], PF[0] - IFD[0]))
    dibujar_arco(IFD, a1, a2, 16, "black",
                 "angulo rigido\n~161 (balancin-distal)", ls="-", lw=1.2,
                 rtxt=20, fs=8.5)

    # --- Arco del angulo AUXILIAR THETAauxfd (falange medial -> distal) en IFD
    # THETAfd_natural = THETAfm + THETAauxfd: es el offset natural en reposo
    # entre la falange medial (IFP->IFD) y la falange distal (IFD->punta).
    afm_dir = np.degrees(np.arctan2(IFD[1] - IFP[1], IFD[0] - IFP[0]))  # THETAfm
    afd_dir = np.degrees(np.arctan2(PF[1] - IFD[1], PF[0] - IFD[0]))    # THETAfd
    # Linea guia que prolonga la falange medial a traves de IFD (origen del ang.)
    gdir = np.radians(afm_dir)
    ax.plot([IFD[0], IFD[0] + 17 * np.cos(gdir)],
            [IFD[1], IFD[1] + 17 * np.sin(gdir)],
            color="#7a3b00", lw=0.8, ls=":", zorder=3)
    dibujar_arco(IFD, afm_dir, afd_dir, 30, "#7a3b00",
                 "ang. AUXILIAR\nTHETAauxfd=38.78\n(medial -> distal)", rtxt=40)

    # --- Articulaciones (revoluta): circulos blancos borde negro ---
    joints = {"MCF": MCF, "IFP": IFP, "IFD": IFD, "Pa": Pa, "D3": D3, "P3": P3}
    for name, p in joints.items():
        ax.plot(p[0], p[1], "o", mfc="white", mec="black", ms=9,
                mew=1.6, zorder=6)
    # Bancada fija (triangulo) en Pa para indicar anclaje a falange proximal
    ax.plot(Pa[0], Pa[1], "^", mfc="black", mec="black", ms=11, zorder=7)

    # --- Etiquetas de puntos ---
    off = {"MCF": (6, -14), "IFP": (-4, 12), "IFD": (8, -14),
           "Pa": (-30, 6), "D3": (6, 8), "P3": (8, 4)}
    for name, p in joints.items():
        dx, dy = off[name]
        ax.annotate(name, p, textcoords="offset points", xytext=(dx, dy),
                    fontsize=11, fontweight="bold")
    ax.annotate("punta del dedo", PF, textcoords="offset points",
                xytext=(6, -12), fontsize=9)

    # --- Etiquetas de eslabones ---
    def mid(a, b):
        return (a + b) / 2.0
    ax.annotate("L9 = 25\n(acoplador)", mid(D3, Pa),
                textcoords="offset points", xytext=(-58, 6), fontsize=9.5)
    ax.annotate("L10 = 35\n(balancin)", mid(IFD, D3),
                textcoords="offset points", xytext=(10, -2), fontsize=9.5)
    ax.annotate("S3 / tierra\nPa-IFP ~12.17", mid(Pa, IFP),
                textcoords="offset points", xytext=(-4, -28), fontsize=9.5)
    ax.annotate("c2 = 46.01\n(balancin 2.o mec.,\nrigido -> P3 no flota)", mid(IFP, P3),
                textcoords="offset points", xytext=(8, -6), fontsize=9,
                color="#1f4e79")
    ax.annotate("falange proximal (fp=49)", mid(MCF, IFP),
                textcoords="offset points", xytext=(-30, -22), fontsize=8.5,
                color="0.3")
    ax.annotate("falange medial (fm=26)\n[manivela]", mid(IFP, IFD),
                textcoords="offset points", xytext=(-70, 18), fontsize=8.5,
                color="0.3")
    ax.annotate("falange distal (fd=24)", mid(IFD, PF),
                textcoords="offset points", xytext=(-30, -24), fontsize=8.5,
                color="0.3")

    # --- Leyenda con la convencion de lineas ---
    leg = [
        Line2D([0], [0], color="black", lw=2.6, label="Eslabon rigido FABRICADO (S3, L9, L10) - linea continua"),
        Line2D([0], [0], color="#1f4e79", lw=2.6, label="Eslabon rigido del 2.o mecanismo (IFP->P3, c2) - rigido con falange medial"),
        Line2D([0], [0], color="0.45", lw=1.8, linestyle=(0, (1, 2)), label="Falange del dedo (hueso, no se fabrica) - linea punteada"),
        Line2D([0], [0], color="0.8", lw=1.4, label="Pose en flexion (referencia de movimiento)"),
        Line2D([0], [0], marker="o", mfc="white", mec="black", lw=0, ms=9, label="Junta de revoluta (perno)"),
        Line2D([0], [0], marker="^", color="black", lw=0, ms=10, label="Anclaje fijo a la falange proximal (Pa)"),
    ]
    ax.legend(handles=leg, loc="lower right", fontsize=9, framealpha=0.95)

    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    ax.set_title("Diagrama de armado - Tercer mecanismo de 4 barras (IFD / DIP)\n"
                 "Montaje DORSAL  |  cotas en mm  |  pose en reposo",
                 fontsize=12)

    # Margenes
    xs = [MCF[0], IFP[0], IFD[0], PF[0], D3[0], Pa[0], P3[0],
          estF["IFD"][0], tmF["PF"][0], tmF["D3"][0], estF["P3"][0]]
    ys = [MCF[1], IFP[1], IFD[1], PF[1], D3[1], Pa[1], P3[1],
          estF["IFD"][1], tmF["PF"][1], tmF["D3"][1], estF["P3"][1]]
    m = 18
    ax.set_xlim(min(xs) - m, max(xs) + m)
    ax.set_ylim(min(ys) - m, max(ys) + m)

    fig.tight_layout()
    out = "diagrama_armado_tercer_mecanismo.png"
    fig.savefig(out, dpi=160)
    plt.close(fig)
    return out


if __name__ == "__main__":
    out = dibujar()
    print("Diagrama de armado generado:", out)
