"""
generar_diagrama_subactuado.py
==============================
Diagrama de eslabones (estilo B/N de ingenieria) del mecanismo SUBACTUADO de
3 articulaciones con flexion, a partir de la cinematica REAL calculada en
cinematica_subactuado.py.

Convencion grafica:
  - Falanges (dedo)            : linea discontinua gris, gruesa.
  - Eslabones fabricados rigidos: linea continua negra.
  - Bielas-campana (bell-crank) : triangulo relleno gris claro (eslabon ternario).
  - Articulaciones (revolutas)  : circulo blanco con borde negro.
  - Pivotes FIJOS a tierra      : circulo + rayado de tierra (MCF y B0).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

import cinematica_subactuado as K

BLACK = "#000000"
GRAY = "#888888"
FILL = "#d9d9d9"
BLUE = "#1f4e79"
GREEN = "#1a7f37"


def _seg(ax, p, q, **kw):
    ax.plot([p[0], q[0]], [p[1], q[1]], **kw)


def _joint(ax, p, r=1.7, z=5):
    ax.plot(p[0], p[1], "o", ms=r * 2, mfc="white", mec=BLACK,
            mew=1.3, zorder=z)


def _ground(ax, p, ang=-90, size=6):
    """Dibuja simbolo de tierra (rayado) en un pivote fijo p."""
    a = np.deg2rad(ang)
    d = np.array([np.cos(a), np.sin(a)])
    perp = np.array([-d[1], d[0]])
    base_c = p + d * size
    b1 = base_c + perp * size * 0.9
    b2 = base_c - perp * size * 0.9
    _seg(ax, b1, b2, color=BLACK, lw=1.4, zorder=2)
    for t in np.linspace(0, 1, 7):
        s = b2 + (b1 - b2) * t
        _seg(ax, s, s + (-d + perp) * size * 0.45, color=BLACK, lw=0.8, zorder=2)
    _seg(ax, p, base_c, color=BLACK, lw=1.4, zorder=2)


def _label(ax, p, txt, dx=2.2, dy=2.2, color=BLACK, fs=8.5, w="bold"):
    ax.text(p[0] + dx, p[1] + dy, txt, color=color, fontsize=fs,
            fontweight=w, ha="left", va="center", zorder=8)


def draw_mech(ax, st, full=True):
    MCP, PIP, DIP, TIP = st["MCP"], st["PIP"], st["DIP"], st["TIP"]
    B0, Q, E1, E2, Ma = st["B0"], st["Q"], st["E1"], st["E2"], st["Ma"]
    S, R, F1, F2, Dc = st["S"], st["R"], st["F1"], st["F2"], st["Dc"]

    # --- Falanges (dedo) ---
    for p, q in [(MCP, PIP), (PIP, DIP), (DIP, TIP)]:
        _seg(ax, p, q, color=GRAY, lw=4.0, ls=(0, (6, 4)), zorder=3,
             solid_capstyle="round")

    # --- Soporte de la mano (tierra): MCF - B0 ---
    _seg(ax, MCP, B0, color=BLACK, lw=2.2, zorder=3)

    # ================= SEIS-BARRAS A (MCF -> IFP) =================
    # postes rigidos a la falange proximal: MCF->Q  y  PIP->Ma (balancin medial)
    _seg(ax, MCP, Q, color=BLACK, lw=1.6, zorder=3)
    # bell-crank A: triangulo Q-E1-E2 (eslabon ternario)
    ax.add_patch(Polygon([Q, E1, E2], closed=True, facecolor=FILL,
                         edgecolor=BLACK, lw=1.8, zorder=4))
    # acoplador A1: B0 -> E1
    _seg(ax, B0, E1, color=BLACK, lw=2.0, zorder=4)
    # acoplador A2: E2 -> Ma
    _seg(ax, E2, Ma, color=BLACK, lw=2.0, zorder=4)
    # balancin A (bracket solidario a la medial): PIP -> Ma
    _seg(ax, PIP, Ma, color=BLACK, lw=2.0, zorder=4)

    # ================= SEIS-BARRAS B (IFP -> IFD) =================
    # postes rigidos: proximal->S , medial->R , distal->Dc(balancin)
    _seg(ax, MCP, S, color=BLUE, lw=1.4, zorder=3)
    _seg(ax, PIP, R, color=BLUE, lw=1.4, zorder=3)
    # bell-crank B: triangulo R-F1-F2
    ax.add_patch(Polygon([R, F1, F2], closed=True, facecolor="#dce6f1",
                         edgecolor=BLUE, lw=1.8, zorder=4))
    # acoplador B1: S -> F1
    _seg(ax, S, F1, color=BLUE, lw=2.0, zorder=4)
    # acoplador B2: F2 -> Dc
    _seg(ax, F2, Dc, color=BLUE, lw=2.0, zorder=4)
    # balancin B (bracket solidario a la distal): DIP -> Dc
    _seg(ax, DIP, Dc, color=BLUE, lw=2.0, zorder=4)

    # --- Articulaciones ---
    for p in (PIP, DIP, TIP, E1, E2, Ma, Q, F1, F2, Dc, R, S):
        _joint(ax, p)
    # pivotes fijos a tierra
    _ground(ax, MCP, ang=-110, size=6)
    _ground(ax, B0, ang=70, size=6)
    _joint(ax, MCP, r=2.0)
    _joint(ax, B0, r=2.0)

    if full:
        _label(ax, MCP, "MCF", dx=-13, dy=-7)
        _label(ax, PIP, "IFP", dx=-2, dy=-7)
        _label(ax, DIP, "IFD", dx=1, dy=-7)
        _label(ax, TIP, "punta", dx=2, dy=-2)
        _label(ax, B0, "B0", dx=2, dy=4, color=BLACK)
        _label(ax, Q, "Q", dx=-6, dy=3)
        _label(ax, E1, "E1", dx=2, dy=2)
        _label(ax, E2, "E2", dx=-7, dy=2)
        _label(ax, Ma, "Ma", dx=2, dy=2)
        _label(ax, S, "S", dx=-5, dy=3, color=BLUE)
        _label(ax, R, "R", dx=2, dy=3, color=BLUE)
        _label(ax, F1, "F1", dx=2, dy=-3, color=BLUE)
        _label(ax, F2, "F2", dx=2, dy=2, color=BLUE)
        _label(ax, Dc, "Dc", dx=2, dy=2, color=BLUE)


def main():
    sts = [s for s in K.barrido() if not s.get("fail")]

    fig = plt.figure(figsize=(16, 9))
    gs = fig.add_gridspec(3, 2, width_ratios=[1.55, 1.0],
                          height_ratios=[1, 1, 1], wspace=0.16, hspace=0.42)

    # ---------- Panel principal: diagrama de eslabones (pose flexionada) ------
    axm = fig.add_subplot(gs[:, 0])
    pose = min(sts, key=lambda s: abs(s["alpha"] - 45))
    draw_mech(axm, pose, full=True)
    axm.set_title("Diagrama de eslabones - mecanismo subactuado (1 actuador, "
                  "3 art. con flexion)\n"
                  f"pose: MCF={pose['alpha']:.0f}deg  IFP={pose['beta']:.0f}deg  "
                  f"IFD={pose['gamma']:.0f}deg",
                  fontsize=11, fontweight="bold")
    axm.set_aspect("equal")
    axm.grid(True, ls=":", lw=0.5, color="#cccccc")
    axm.set_xlabel("x [mm]"); axm.set_ylabel("y [mm]")
    # leyenda
    axm.plot([], [], color=GRAY, lw=4, ls=(0, (6, 4)), label="falanges (dedo)")
    axm.plot([], [], color=BLACK, lw=2, label="seis-barras A (MCF->IFP)")
    axm.plot([], [], color=BLUE, lw=2, label="seis-barras B (IFP->IFD)")
    axm.plot([], [], "o", mfc="white", mec=BLACK, label="junta revoluta")
    axm.legend(loc="lower left", fontsize=8, framealpha=0.95)

    # ---------- Panel ROM: superposicion de poses ----------
    axr = fig.add_subplot(gs[0, 1])
    poses = [min(sts, key=lambda s: abs(s["alpha"] - t)) for t in (0, 38, 75)]
    cols = ["#bdbdbd", "#6e6e6e", "#000000"]
    for st, c in zip(poses, cols):
        pts = [st["MCP"], st["PIP"], st["DIP"], st["TIP"]]
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        axr.plot(xs, ys, "-o", color=c, lw=3, ms=4,
                 label=f"MCF={st['alpha']:.0f} IFP={st['beta']:.0f} "
                       f"IFD={st['gamma']:.0f}")
    axr.set_title("Rango de movimiento (abierto -> cerrado)", fontsize=10,
                  fontweight="bold")
    axr.set_aspect("equal"); axr.grid(True, ls=":", lw=0.5, color="#cccccc")
    axr.legend(fontsize=7.5, loc="upper right")
    axr.set_xlabel("x [mm]"); axr.set_ylabel("y [mm]")

    # ---------- Panel coordinacion ----------
    axc = fig.add_subplot(gs[1, 1])
    al = [s["alpha"] for s in sts]
    be = [s["beta"] for s in sts]
    ga = [s["gamma"] for s in sts]
    axc.plot(al, be, color=BLUE, lw=2.4, label="IFP (beta)")
    axc.plot(al, ga, color=GREEN, lw=2.4, label="IFD (gamma)")
    axc.plot(al, al, color=GRAY, lw=1.4, ls="--", label="MCF (alpha)")
    axc.set_title("Coordinacion articular (subactuacion)", fontsize=10,
                  fontweight="bold")
    axc.set_xlabel("entrada MCF  alpha [deg]")
    axc.set_ylabel("flexion [deg]")
    axc.grid(True, ls=":", lw=0.5, color="#cccccc")
    axc.legend(fontsize=8, loc="upper left")

    # ---------- Panel trayectorias ----------
    axt = fig.add_subplot(gs[2, 1])
    for key, c, lab in [("PIP", "#6e6e6e", "IFP"), ("DIP", "#3a3a3a", "IFD"),
                        ("TIP", "#000000", "punta")]:
        xs = [s[key][0] for s in sts]; ys = [s[key][1] for s in sts]
        axt.plot(xs, ys, color=c, lw=2.2, label=lab)
    # dedo extendido y flexionado como referencia
    for st, c in [(sts[0], "#cfcfcf"), (sts[-1], "#999999")]:
        pts = [st["MCP"], st["PIP"], st["DIP"], st["TIP"]]
        axt.plot([p[0] for p in pts], [p[1] for p in pts], "-", color=c, lw=1.2)
    axt.set_title("Trayectorias de articulaciones y punta", fontsize=10,
                  fontweight="bold")
    axt.set_aspect("equal"); axt.grid(True, ls=":", lw=0.5, color="#cccccc")
    axt.legend(fontsize=8, loc="upper right")
    axt.set_xlabel("x [mm]"); axt.set_ylabel("y [mm]")

    fig.suptitle("Exoesqueleto de dedo - mecanismo SUBACTUADO de mayor ROM "
                 "(MCF 0-75, IFP 0-74, IFD 0-64 deg)", fontsize=13,
                 fontweight="bold")
    fig.savefig("diagrama_subactuado.png", dpi=130, bbox_inches="tight")
    print("Diagrama generado: diagrama_subactuado.png")


if __name__ == "__main__":
    main()
