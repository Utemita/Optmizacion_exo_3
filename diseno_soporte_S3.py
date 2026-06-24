"""
diseno_soporte_S3.py
====================
Diagrama de DISENO del soporte/tierra S3 del tercer mecanismo (IFD/DIP).

Responde a la duda: "que es ese eslabon que sale de la falange proximal".
Ese eslabon es el SOPORTE S3 (la 'tierra' del 4 barras): una pieza rigida que
se sujeta a la falange PROXIMAL y termina en el pivote fijo Pa, donde se conecta
el acoplador L9.

La figura tiene 3 zonas (grande, para leerse bien):
  (A) Arriba: el mecanismo completo con el soporte S3 RESALTADO en rojo + flecha.
  (B) Abajo-izq: DETALLE DE DISENO del soporte S3, acotado (vista lateral, en el
       marco local de la falange proximal). Muestra la abrazadera, el brazo que
       cruza por encima de la IFP, y el pivote Pa (12 mm adelante de IFP, 2 mm
       dorsal respecto a la linea central del modelo).
  (C) Abajo-der: notas de fabricacion + cotas criticas.

Convencion de lineas: rigido fabricado = continua; falange (hueso) = punteada.
Usa la cinematica REAL del modulo (cotas consistentes con el resto del proyecto).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Arc, Circle

import cinematica_tercer_mecanismo as K

RED = "#c0392b"
SOLID = dict(color="black", lw=2.8, solid_capstyle="round", zorder=5)
DASH = dict(color="0.45", lw=2.0, linestyle=(0, (1, 2)), zorder=3)
THIN = dict(color="black", lw=1.6, zorder=4)
GHOST = dict(color="0.82", lw=1.4, zorder=1)


def pose(j, gamma=None, dorsal=None):
    est = K.cinematica_paso(float(j))
    tm = K.tercer_mecanismo(est, gamma_bracket=gamma, dorsal_sign=dorsal)
    return est, tm


def dim_line(ax, p0, p1, text, off=6.0, fs=10, color="0.15"):
    """Dibuja una linea de cota con doble flecha y texto al centro."""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    ax.annotate("", p1, p0, arrowprops=dict(arrowstyle="<->", color=color, lw=1.2))
    mid = (p0 + p1) / 2.0
    d = p1 - p0
    n = np.array([-d[1], d[0]])
    nlen = np.hypot(*n)
    if nlen > 1e-9:
        n = n / nlen
    ax.text(*(mid + off * n), text, ha="center", va="center", fontsize=fs,
            color=color)


# =============================================================================
# Calibracion / poses
# =============================================================================
est0, tm0 = pose(0)
gamma, dorsal = tm0["gamma_bracket"], tm0["dorsal_sign"]
est0, tm0 = pose(0, gamma, dorsal)
estF, tmF = pose(132, gamma, dorsal)

fig = plt.figure(figsize=(16.5, 12.0))
gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.15], width_ratios=[1.35, 1.0],
                      hspace=0.18, wspace=0.12)
axA = fig.add_subplot(gs[0, :])
axB = fig.add_subplot(gs[1, 0])
axC = fig.add_subplot(gs[1, 1])

# =============================================================================
# (A) MECANISMO COMPLETO  -  S3 resaltado
# =============================================================================
MCF = est0["MCF"]; IFP = est0["IFP"]; IFD = est0["IFD"]
PF = tm0["PF"]; D3 = tm0["D3"]; Pa = tm0["Pa"]

# pose flexionada (fantasma)
for a, b in [(estF["MCF"], estF["IFP"]), (estF["IFP"], estF["IFD"]),
             (estF["IFD"], tmF["PF"]), (estF["IFD"], tmF["D3"]),
             (tmF["D3"], tmF["Pa"]), (tmF["Pa"], estF["IFP"])]:
    axA.plot([a[0], b[0]], [a[1], b[1]], **GHOST)

# falanges punteadas
axA.plot([MCF[0], IFP[0]], [MCF[1], IFP[1]], **DASH)
axA.plot([IFP[0], IFD[0]], [IFP[1], IFD[1]], **DASH)
axA.plot([IFD[0], PF[0]], [IFD[1], PF[1]], **DASH)

# eslabones rigidos
axA.plot([D3[0], Pa[0]], [D3[1], Pa[1]], **SOLID)     # L9
axA.plot([IFD[0], D3[0]], [IFD[1], D3[1]], **SOLID)   # L10
# tierra S3 (Pa-IFP) RESALTADA
axA.plot([Pa[0], IFP[0]], [Pa[1], IFP[1]], color=RED, lw=5.0,
         solid_capstyle="round", zorder=6)

# juntas
for name, p in {"MCF": MCF, "IFP": IFP, "IFD": IFD, "D3": D3}.items():
    axA.plot(p[0], p[1], "o", mfc="white", mec="black", ms=10, mew=1.7, zorder=7)
axA.plot(Pa[0], Pa[1], "^", mfc=RED, mec="black", ms=13, zorder=8)

offA = {"MCF": (8, -16), "IFP": (-2, 14), "IFD": (10, -16), "D3": (8, 8)}
for name, p in {"MCF": MCF, "IFP": IFP, "IFD": IFD, "D3": D3}.items():
    axA.annotate(name, p, textcoords="offset points", xytext=offA[name],
                 fontsize=12, fontweight="bold")
axA.annotate("Pa", Pa, textcoords="offset points", xytext=(-26, 6),
             fontsize=12, fontweight="bold", color=RED)
axA.annotate("punta", PF, textcoords="offset points", xytext=(6, -12), fontsize=10)

axA.annotate("L9 = 25 (acoplador)", (D3 + Pa) / 2, textcoords="offset points",
             xytext=(-60, 8), fontsize=10)
axA.annotate("L10 = 35 (balancin)", (IFD + D3) / 2, textcoords="offset points",
             xytext=(10, -4), fontsize=10)

# flecha senalando S3
mid_s3 = (Pa + IFP) / 2
axA.annotate("ESTE ESLABON = SOPORTE / TIERRA  S3\n"
             "(se sujeta a la falange PROXIMAL\n y termina en el pivote Pa)",
             xy=mid_s3, xytext=(mid_s3[0] - 4, mid_s3[1] - 40),
             fontsize=11, fontweight="bold", color=RED, ha="center",
             arrowprops=dict(arrowstyle="-|>", color=RED, lw=2.0))

axA.set_aspect("equal", adjustable="box")
axA.axis("off")
axA.set_title("(A)  Donde esta el soporte S3 dentro del mecanismo  (pose en reposo, mm)",
              fontsize=12.5, fontweight="bold")

# =============================================================================
# (B) DETALLE DE DISENO DEL SOPORTE  (marco local de la falange proximal)
# =============================================================================
thetafp = np.deg2rad(est0["THETAfp"])
prox_dir = np.array([np.cos(thetafp), np.sin(thetafp)])
prox_norm = np.array([-prox_dir[1], prox_dir[0]])
dorsal_norm = dorsal * prox_norm
R = np.array([prox_dir, dorsal_norm])  # mapea prox->(1,0), dorsal->(0,1)


def loc(p):
    return R @ (np.asarray(p, float) - IFP)


MCFl, IFPl, IFDl = loc(MCF), loc(IFP), loc(IFD)
Pal, D3l, PFl = loc(Pa), loc(D3), loc(PF)

# --- falanges (centerlines, punteadas) ---
axB.plot([MCFl[0], IFPl[0]], [MCFl[1], IFPl[1]], **DASH)
axB.plot([IFPl[0], IFDl[0]], [IFPl[1], IFDl[1]], **DASH)
axB.plot([IFDl[0], PFl[0]], [IFDl[1], PFl[1]], **DASH)
axB.annotate("falange proximal", (MCFl + IFPl) / 2, textcoords="offset points",
             xytext=(-10, -16), fontsize=9, color="0.35")
axB.annotate("falange medial\n(manivela)", (IFPl + IFDl) / 2,
             textcoords="offset points", xytext=(0, 10), fontsize=9, color="0.35")
axB.annotate("falange distal", (IFDl + PFl) / 2, textcoords="offset points",
             xytext=(6, -14), fontsize=9, color="0.35")

# --- mecanismo (L9, L10) tenue para contexto ---
axB.plot([Pal[0], D3l[0]], [Pal[1], D3l[1]], **THIN)
axB.plot([IFDl[0], D3l[0]], [IFDl[1], D3l[1]], **THIN)
axB.annotate("L9", (Pal + D3l) / 2, textcoords="offset points", xytext=(-16, 4),
             fontsize=9)
axB.annotate("L10", (IFDl + D3l) / 2, textcoords="offset points", xytext=(6, 2),
             fontsize=9)

# --- linea cinematica de la tierra S3 (Pa-IFP), tenue roja ---
axB.plot([Pal[0], IFPl[0]], [Pal[1], IFPl[1]], color=RED, lw=1.4,
         linestyle=(0, (4, 3)), zorder=4)

# --- PIEZA FISICA: soporte S3 (abrazadera + brazo) en CONTINUA gruesa ---
clamp_x = -22.0           # posicion de la abrazadera (eleccion de diseno)
clamp_h = 7.0             # media altura de la abrazadera (banda)
# abrazadera: banda en C alrededor de la falange proximal (vista lateral)
axB.plot([clamp_x, clamp_x], [-clamp_h, clamp_h], color="black", lw=3.0, zorder=6)
axB.plot([clamp_x, clamp_x + 4], [clamp_h, clamp_h], color="black", lw=3.0, zorder=6)
axB.plot([clamp_x, clamp_x + 4], [-clamp_h, -clamp_h], color="black", lw=3.0, zorder=6)
# brazo: del tope dorsal de la abrazadera hasta Pa, cruzando sobre la IFP
axB.plot([clamp_x, Pal[0]], [clamp_h - 0.5, Pal[1]], **SOLID)
axB.annotate("abrazadera (clamp)\na la falange proximal", (clamp_x, -clamp_h),
             textcoords="offset points", xytext=(-6, -16), fontsize=9,
             ha="center")
axB.annotate("brazo del soporte\n(cruza por ENCIMA de la IFP, sin tocarla)",
             (clamp_x / 2, (clamp_h - 0.5 + Pal[1]) / 2 + 2),
             textcoords="offset points", xytext=(34, 18), fontsize=9, ha="center",
             arrowprops=dict(arrowstyle="-", color="0.4", lw=0.8))

# --- juntas ---
for p in (IFPl, IFDl, D3l):
    axB.plot(p[0], p[1], "o", mfc="white", mec="black", ms=9, mew=1.6, zorder=7)
# pivote Pa: ojo con perno (doble circulo)
axB.add_patch(Circle(Pal, 2.6, fill=False, ec=RED, lw=2.0, zorder=8))
axB.add_patch(Circle(Pal, 1.0, fc=RED, ec=RED, zorder=8))
axB.annotate("Pa  (pivote/perno del acoplador L9)", Pal,
             textcoords="offset points", xytext=(8, 10), fontsize=10,
             fontweight="bold", color=RED)
axB.annotate("IFP", IFPl, textcoords="offset points", xytext=(-2, -16),
             fontsize=11, fontweight="bold")
axB.annotate("IFD", IFDl, textcoords="offset points", xytext=(8, -14),
             fontsize=11, fontweight="bold")
axB.annotate("D3", D3l, textcoords="offset points", xytext=(8, 6),
             fontsize=11, fontweight="bold")

# --- cotas criticas de Pa respecto a IFP ---
# 12 mm adelante (horizontal) a la altura y=-6
ylev = -6.5
dim_line(axB, [IFPl[0], ylev], [Pal[0], ylev],
         "12 mm  (adelante de IFP)", off=-4.5, fs=10, color=RED)
axB.plot([IFPl[0], IFPl[0]], [IFPl[1], ylev], color=RED, lw=0.7, ls=":")
axB.plot([Pal[0], Pal[0]], [Pal[1], ylev], color=RED, lw=0.7, ls=":")
# 2 mm dorsal (vertical) en x=Pa
dim_line(axB, [Pal[0] + 8, 0.0], [Pal[0] + 8, Pal[1]],
         "2 mm dorsal\n(resp. linea central)", off=12, fs=9, color=RED)
axB.plot([Pal[0], Pal[0] + 8], [0, 0], color=RED, lw=0.7, ls=":")
axB.plot([Pal[0], Pal[0] + 8], [Pal[1], Pal[1]], color=RED, lw=0.7, ls=":")

axB.set_aspect("equal", adjustable="box")
axB.axis("off")
axB.set_title("(B)  Como disenar el soporte S3  (vista lateral, cotas en mm)",
              fontsize=12.5, fontweight="bold")
xs = [MCFl[0], Pal[0], IFDl[0], D3l[0], PFl[0], clamp_x]
ys = [MCFl[1], Pal[1], IFDl[1], D3l[1], PFl[1], -clamp_h, ylev]
axB.set_xlim(min(xs) - 12, max(xs) + 12)
axB.set_ylim(min(ys) - 12, max(ys) + 14)

# =============================================================================
# (C) NOTAS DE FABRICACION + COTAS CRITICAS
# =============================================================================
axC.axis("off")
notas = (
    "SOPORTE / TIERRA  S3  -  guia de fabricacion\n"
    "-------------------------------------------------\n"
    "Es UNA sola pieza rigida = abrazadera + brazo + ojo de pivote.\n\n"
    "1) ABRAZADERA: banda en C que sujeta el DORSO de la falange\n"
    "   proximal. Ajustar el radio al dedo real del paciente.\n"
    "   Fijacion: velcro o tornillo. Posicion ~20-25 mm de la IFP\n"
    "   (es libre; no afecta la cinematica).\n\n"
    "2) BRAZO: se proyecta hacia ADELANTE y cruza por ENCIMA de la\n"
    "   articulacion IFP sin tocarla (perfil bajo, dorsal).\n\n"
    "3) PIVOTE Pa  (CRITICO - define el movimiento):\n"
    "      - 12 mm por delante del eje IFP (a lo largo del dedo)\n"
    "      - 2 mm dorsal respecto a la linea central (modelo)\n"
    "   En Pa va un perno M2-M3 que une S3 con el acoplador L9.\n\n"
    "4) El modelo usa LINEAS CENTRALES de las falanges. Al fabricar,\n"
    "   eleva la pieza por encima de la piel manteniendo el EJE Pa\n"
    "   en su posicion relativa a IFP. Holgura dorsal con el hueso\n"
    "   de la falange medial ~5 mm.\n\n"
    "5) Material sugerido: PLA/nylon (prototipo) o aluminio.\n"
    "\n"
    "COTAS CRITICAS DEL TERCER MECANISMO\n"
    "-------------------------------------------------\n"
    "   Pa respecto a IFP ....... 12 mm adelante, 2 mm dorsal\n"
    "   L9  (Pa  -> D3) ......... 25 mm   (acoplador)\n"
    "   L10 (IFD -> D3) ......... 35 mm   (balancin)\n"
    "   Manivela (IFP -> IFD) ... 26 mm   (falange medial)\n"
    "   Angulo rigido L10-distal . ~161 deg\n"
    "   Flexion IFD resultante ... 0 -> ~15 deg (gradual)"
)
axC.text(0.0, 1.0, notas, ha="left", va="top", fontsize=10.3, family="monospace",
         transform=axC.transAxes)
axC.set_title("(C)  Notas de fabricacion", fontsize=12.5, fontweight="bold",
              loc="left")

# --- leyenda global ---
leg = [
    Line2D([0], [0], color="black", lw=2.8, label="Eslabon rigido FABRICADO (continua)"),
    Line2D([0], [0], color="0.45", lw=2.0, linestyle=(0, (1, 2)), label="Falange / hueso (punteada)"),
    Line2D([0], [0], color=RED, lw=5.0, label="Soporte / tierra S3 (la pieza que preguntas)"),
    Line2D([0], [0], marker="^", color=RED, mec="black", lw=0, ms=12, label="Pivote fijo Pa (perno del acoplador)"),
]
fig.legend(handles=leg, loc="lower center", ncol=4, fontsize=10,
           framealpha=0.95, bbox_to_anchor=(0.5, 0.005))

fig.suptitle("DISENO DEL SOPORTE S3  -  el eslabon que sale de la falange proximal",
             fontsize=15, fontweight="bold", y=0.99)
fig.tight_layout(rect=[0, 0.035, 1, 0.97])

out = "diseno_soporte_S3.png"
fig.savefig(out, dpi=180)
plt.close(fig)
print("Diagrama de diseno generado:", out)
