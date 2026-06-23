"""
generar_diagrama_completo.py
=============================
Genera el diagrama cinematico del exoesqueleto CON el tercer mecanismo de
4 barras (Link9 = 25 mm, Link10 = 35 mm) para la articulacion IFD/DIP.

El diagrama:
  - Usa las POSICIONES REALES calculadas por la cinematica completa
    (cinematica_tercer_mecanismo.py), portada fielmente de CinematicaExoFinal.m.
  - Conserva la flexion natural de las falanges (curvadas, no rectas).
  - Muestra TODOS los eslabones correctamente conectados, incluido el tercer
    mecanismo P_a -> D3 (L9) y IFD -> D3 (L10).
  - Estilo BLANCO Y NEGRO de ingenieria, identico en espiritu a `diagrama.png`:
    fondo blanco, lineas negras, articulaciones como circulos blancos con borde
    negro, soportes con achurado, sin colores, sin leyenda, sin grilla.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import cinematica_tercer_mecanismo as K

# =============================================================================
# 1) CALCULO DE LA POSE A DIBUJAR (posicion representativa, flexion natural)
# =============================================================================
THETA2_diagrama = 40.0  # grados (pose intermedia, flexion clara)

est = K.cinematica_paso(THETA2_diagrama)
# Calibracion del tercer mecanismo en la pose inicial (j=0) para conservar la
# flexion natural en reposo y mantener el lado dorsal consistente.
est0 = K.cinematica_paso(0.0)
cal = K.tercer_mecanismo(est0)
gamma = cal["gamma_bracket"]
dorsal = cal["dorsal_sign"]
tm = K.tercer_mecanismo(est, gamma_bracket=gamma, dorsal_sign=dorsal)

# Puntos principales
MCF = est["MCF"]
IFP = est["IFP"]
IFD = est["IFD"]
P = est["P"]
P2 = est["P2"]
P3 = est["P3"]
S1 = est["S1"]
S2 = est["S2"]
M4 = est["M4"]
Pa = tm["Pa"]
D3 = tm["D3"]
PF = tm["PF"]

# Bancadas (puntos fijos)
r3 = K.r3
G1 = np.array([-r3, 0.0])   # pivote manivela theta1 / manivela 4B1
G2 = np.array([r3, 0.0])    # pivote manivela theta2 (5 barras 1)

# Tip de la manivela theta2 (Link1) del primer 5 barras
theta2 = np.deg2rad(THETA2_diagrama)
T2 = G2 + K.Link1 * np.array([np.cos(theta2), np.sin(theta2)])

# =============================================================================
# 2) ESTILO B/N
# =============================================================================
LW_LINK = 1.1     # eslabones del mecanismo
LW_PHAL = 2.4     # falanges (hueso del dedo)
LW_GROUND = 1.4
R_JOINT = 1.5     # radio de articulaciones
FS_PT = 9.5       # tamano etiqueta de puntos
FS_LINK = 8.5     # tamano etiqueta de eslabones

fig, ax = plt.subplots(figsize=(11, 10))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")


def link(p1, p2, lw=LW_LINK, ls="-", z=4):
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="black",
            linewidth=lw, linestyle=ls, zorder=z, solid_capstyle="round")


def joint(p, r=R_JOINT, z=10):
    ax.add_patch(plt.Circle((p[0], p[1]), r, facecolor="white",
                            edgecolor="black", linewidth=1.3, zorder=z))


def ground(p, ang=270, size=7):
    """Soporte fijo: triangulo pequeno + achurado, apuntando segun 'ang'."""
    a = np.deg2rad(ang)
    nx, ny = np.cos(a), np.sin(a)              # direccion del soporte
    px, py = -ny, nx                           # perpendicular
    base_c = np.array([p[0] + nx * size, p[1] + ny * size])
    b1 = base_c + np.array([px, py]) * size * 0.6
    b2 = base_c - np.array([px, py]) * size * 0.6
    ax.plot([p[0], b1[0]], [p[1], b1[1]], color="black", lw=1.0, zorder=6)
    ax.plot([p[0], b2[0]], [p[1], b2[1]], color="black", lw=1.0, zorder=6)
    ax.plot([b1[0], b2[0]], [b1[1], b2[1]], color="black", lw=1.0, zorder=6)
    # achurado
    for t in np.linspace(0, 1, 6):
        h = b1 + (b2 - b1) * t
        ax.plot([h[0], h[0] + nx * 2.6 + px * 1.8],
                [h[1], h[1] + ny * 2.6 + py * 1.8],
                color="black", lw=0.7, zorder=6)


def lbl_pt(p, text, dx=2.5, dy=2.5, ha="left", va="bottom"):
    ax.text(p[0] + dx, p[1] + dy, text, fontsize=FS_PT, color="black",
            ha=ha, va=va, zorder=20)


def lbl_link(p1, p2, text, dx=0.0, dy=0.0):
    mx = (p1[0] + p2[0]) / 2 + dx
    my = (p1[1] + p2[1]) / 2 + dy
    ax.text(mx, my, text, fontsize=FS_LINK, color="black", style="italic",
            ha="center", va="center", zorder=18)


# =============================================================================
# 3) DIBUJO DE ESLABONES (mecanismo)
# =============================================================================
# --- Bancada (fija) ---
link(G1, G2, lw=LW_GROUND)                         # Bancada1 (B1)
link(G1, MCF, lw=LW_GROUND)                        # Bancada2 (B2 = d)
lbl_link(G1, G2, r"$B_1$", dy=2.5)
lbl_link(G1, MCF, r"$B_2$", dx=-4)

# --- Primer mecanismo de 5 barras ---
link(G2, T2)                                       # L1 (r4)
link(T2, P)                                        # L2 (r5)
link(M4, P)                                        # L3 (r2)
link(G1, M4)                                       # L4 (r1 = manivela 4B1)
lbl_link(G2, T2, r"$L_1$", dx=3)
lbl_link(T2, P, r"$L_2$", dx=-3, dy=2)
lbl_link(M4, P, r"$L_3$", dx=3)
lbl_link(G1, M4, r"$L_4$", dx=-4)

# --- Primer mecanismo de 4 barras ---
link(M4, S1)                                       # L5 (acoplador)
link(MCF, S1)                                      # rocker c (soporte S1)
lbl_link(M4, S1, r"$L_5$", dy=2)
lbl_link(MCF, S1, r"$c$", dx=3, dy=-1)

# --- Soportes de la falange proximal ---
link(IFP, S2)                                      # d2 (ground 4B2)
link(S1, S2)                                       # base soportes (r1m2)

# --- Segundo mecanismo de 5 barras ---
link(P, P2)                                        # L6 (r5m2)
link(S2, P2)                                       # L7 (r2m2 = manivela 4B2)
lbl_link(P, P2, r"$L_6$", dy=2)
lbl_link(S2, P2, r"$L_7$", dx=-3)

# --- Segundo mecanismo de 4 barras ---
link(P2, P3)                                       # L8 (acoplador)
link(IFP, P3)                                      # c2 (rocker -> falange medial)
lbl_link(P2, P3, r"$L_8$", dy=2)
lbl_link(IFP, P3, r"$c_2$", dx=-4)

# --- TERCER MECANISMO DE 4 BARRAS (IFD / DIP) ---
link(IFP, Pa)                                      # manivela (sobre f. proximal)
link(Pa, D3, lw=1.6)                               # L9 (acoplador)
link(IFD, D3, lw=1.6)                              # L10 (balancin)
lbl_link(IFP, Pa, r"$r_{3m}$", dx=4, dy=-1)
lbl_link(Pa, D3, r"$L_9$", dy=2.5)
lbl_link(IFD, D3, r"$L_{10}$", dx=3.5)

# =============================================================================
# 4) FALANGES (hueso del dedo, con flexion natural)
# =============================================================================
link(MCF, IFP, lw=LW_PHAL, z=3)                    # falange proximal Fp
link(IFP, IFD, lw=LW_PHAL, z=3)                    # falange medial   Fm
link(IFD, PF, lw=LW_PHAL, z=3)                     # falange distal   Fd

# Etiquetas de falanges (sobre el hueso, lado palmar)
def midoff(p1, p2, perp=-7):
    mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
    v = np.array(p2) - np.array(p1)
    n = np.array([-v[1], v[0]])
    n = n / np.hypot(*n)
    return mx + n[0] * perp, my + n[1] * perp

fpx, fpy = midoff(MCF, IFP)
ax.text(fpx, fpy, r"$F_p$", fontsize=10, style="italic", ha="center", va="center", zorder=18)
fmx, fmy = midoff(IFP, IFD)
ax.text(fmx, fmy, r"$F_m$", fontsize=10, style="italic", ha="center", va="center", zorder=18)
fdx, fdy = midoff(IFD, PF)
ax.text(fdx, fdy, r"$F_d$", fontsize=10, style="italic", ha="center", va="center", zorder=18)

# =============================================================================
# 5) ARTICULACIONES Y SOPORTES FIJOS
# =============================================================================
for p in [T2, P, M4, S1, S2, P2, P3, Pa, D3, PF, MCF, IFP, IFD, G1, G2]:
    joint(p)

# Soportes fijos (bancada)
ground(G1, ang=90, size=6)
ground(G2, ang=90, size=6)

# =============================================================================
# 6) ETIQUETAS DE PUNTOS
# =============================================================================
lbl_pt(MCF, "MCF", dx=3, dy=-6, va="top")
lbl_pt(IFP, "IFP", dx=-3, dy=-6, ha="right", va="top")
lbl_pt(IFD, "IFD", dx=2, dy=-6, va="top")
lbl_pt(PF, "PF", dx=-4, dy=-3, ha="right", va="top")
lbl_pt(P, r"$P$", dx=3, dy=2)
lbl_pt(P2, r"$P_2$", dx=-3, dy=3, ha="right")
lbl_pt(P3, r"$P_3$", dx=-3, dy=2, ha="right")
lbl_pt(S1, r"$S_1$", dx=2, dy=3)
lbl_pt(S2, r"$S_2$", dx=-2, dy=-5, ha="right", va="top")
lbl_pt(M4, r"$M_4$", dx=3, dy=2)
lbl_pt(Pa, r"$P_a$", dx=3, dy=3)
lbl_pt(D3, r"$D_3$", dx=3, dy=2)
lbl_pt(G1, r"$G_1$", dx=-3, dy=3, ha="right")
lbl_pt(G2, r"$G_2$", dx=3, dy=3)

# =============================================================================
# 7) AJUSTES FINALES
# =============================================================================
ax.set_aspect("equal")
ax.axis("off")

xs = [T2[0], P[0], M4[0], S1[0], S2[0], P2[0], P3[0], Pa[0], D3[0], PF[0],
      MCF[0], IFP[0], IFD[0], G1[0], G2[0]]
ys = [T2[1], P[1], M4[1], S1[1], S2[1], P2[1], P3[1], Pa[1], D3[1], PF[1],
      MCF[1], IFP[1], IFD[1], G1[1], G2[1]]
mx, my = 14, 12
ax.set_xlim(min(xs) - mx, max(xs) + mx)
ax.set_ylim(min(ys) - my, max(ys) + my)

plt.tight_layout()
out = "/projects/sandbox/Optmizacion_exo_3/diagrama_tercer_mecanismo.png"
plt.savefig(out, dpi=200, bbox_inches="tight", facecolor="white")
plt.close()
print("Diagrama generado:", out)
print(f"Pose: THETA2={THETA2_diagrama} deg | THETAfm={est['THETAfm']:.2f} "
      f"THETAfd={tm['THETAfd']:.2f}")
print("Estilo: blanco y negro, ingenieria. Falanges con flexion natural.")
print("Tercer mecanismo: IFP->Pa (manivela), Pa->D3 (L9=25), IFD->D3 (L10=35).")
