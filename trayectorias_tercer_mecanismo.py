"""
trayectorias_tercer_mecanismo.py
================================
Espejo en Python del script MATLAB `trayectorias_tercer_mecanismo.m`.

Sirve para VERIFICAR (el sandbox no tiene MATLAB/Octave) y para generar dos
artefactos de referencia que el usuario puede comparar contra su modelo CAD:

  - trayectorias_DIP.csv  : coordenadas (x, y) de cada articulacion y de la
                            punta del dedo para cada angulo del actuador.
  - trayectorias_tercer_mecanismo.png : grafico B/N de ingenieria con las
                            trayectorias trazadas + el mecanismo en varias poses.

Usa el modulo de cinematica REAL (`cinematica_tercer_mecanismo.py`), de modo que
las trayectorias coinciden exactamente con las del diagrama y la validacion.
"""
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import cinematica_tercer_mecanismo as K


def recorrer():
    """Recorre el rango completo del actuador y devuelve las trayectorias."""
    pasos = range(0, 133)              # THETA2 = 0..132 grados
    gamma = None
    dorsal = None
    T = {k: [] for k in
         ["THETA2", "MCF", "Pa", "IFP", "IFD", "D3", "PF", "P3",
          "THETAfp", "THETAfm", "THETAfd"]}
    for j in pasos:
        est = K.cinematica_paso(float(j))
        if gamma is None:
            tm0 = K.tercer_mecanismo(est)
            if tm0 is None:
                continue
            gamma = tm0["gamma_bracket"]
            dorsal = tm0["dorsal_sign"]
        tm = K.tercer_mecanismo(est, gamma_bracket=gamma, dorsal_sign=dorsal)
        if tm is None:
            continue
        T["THETA2"].append(est["THETA2"])
        T["MCF"].append(est["MCF"])
        T["Pa"].append(tm["Pa"])
        T["IFP"].append(est["IFP"])
        T["IFD"].append(est["IFD"])
        T["D3"].append(tm["D3"])
        T["PF"].append(tm["PF"])
        T["P3"].append(est["P3"])
        T["THETAfp"].append(est["THETAfp"])
        T["THETAfm"].append(est["THETAfm"])
        T["THETAfd"].append(tm["THETAfd"])
    for k in T:
        T[k] = np.array(T[k])
    return T


def exportar_csv(T, ruta="trayectorias_DIP.csv"):
    cols = ["THETA2",
            "MCF_x", "MCF_y", "IFP_x", "IFP_y", "IFD_x", "IFD_y",
            "PF_x", "PF_y", "D3_x", "D3_y", "Pa_x", "Pa_y", "P3_x", "P3_y",
            "THETAfp", "THETAfm", "THETAfd"]
    with open(ruta, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for i in range(len(T["THETA2"])):
            w.writerow([
                f"{T['THETA2'][i]:.3f}",
                f"{T['MCF'][i,0]:.4f}", f"{T['MCF'][i,1]:.4f}",
                f"{T['IFP'][i,0]:.4f}", f"{T['IFP'][i,1]:.4f}",
                f"{T['IFD'][i,0]:.4f}", f"{T['IFD'][i,1]:.4f}",
                f"{T['PF'][i,0]:.4f}", f"{T['PF'][i,1]:.4f}",
                f"{T['D3'][i,0]:.4f}", f"{T['D3'][i,1]:.4f}",
                f"{T['Pa'][i,0]:.4f}", f"{T['Pa'][i,1]:.4f}",
                f"{T['P3'][i,0]:.4f}", f"{T['P3'][i,1]:.4f}",
                f"{T['THETAfp'][i]:.3f}", f"{T['THETAfm'][i]:.3f}",
                f"{T['THETAfd'][i]:.3f}"])
    return ruta


def graficar(T, ruta="trayectorias_tercer_mecanismo.png"):
    fig, ax = plt.subplots(figsize=(11, 8))
    ax.set_facecolor("white")

    # Mecanismo (esqueleto) en varias poses, en gris claro
    idx_poses = np.linspace(0, len(T["THETA2"]) - 1, 7).astype(int)
    for i in idx_poses:
        MCF, IFP, IFD, PF = T["MCF"][i], T["IFP"][i], T["IFD"][i], T["PF"][i]
        D3, Pa = T["D3"][i], T["Pa"][i]
        # Falanges
        ax.plot([MCF[0], IFP[0]], [MCF[1], IFP[1]], color="0.75", lw=1.0, zorder=1)
        ax.plot([IFP[0], IFD[0]], [IFP[1], IFD[1]], color="0.75", lw=1.0, zorder=1)
        ax.plot([IFD[0], PF[0]], [IFD[1], PF[1]], color="0.75", lw=1.0, zorder=1)
        # Tercer 4 barras: IFD->D3 (balancin), D3->Pa (acoplador), Pa->IFP (tierra)
        ax.plot([IFD[0], D3[0]], [IFD[1], D3[1]], color="0.55", lw=1.0, zorder=1)
        ax.plot([D3[0], Pa[0]], [D3[1], Pa[1]], color="0.55", lw=1.0, zorder=1)
        ax.plot([Pa[0], IFP[0]], [Pa[1], IFP[1]], color="0.55", lw=1.0, zorder=1)

    # Trayectorias (lineas negras de distinto estilo)
    estilos = {
        "IFP": ("-", "IFP (interfalangica proximal)"),
        "IFD": ("--", "IFD (interfalangica distal)"),
        "PF":  ("-.", "Punta del dedo"),
        "D3":  (":", "D3 (punta del balancin L10)"),
    }
    for k, (ls, lab) in estilos.items():
        ax.plot(T[k][:, 0], T[k][:, 1], color="black", ls=ls, lw=2.0,
                zorder=3, label=lab)

    # Puntos de inicio/fin
    for k in ["IFP", "IFD", "PF", "D3"]:
        ax.plot(T[k][0, 0], T[k][0, 1], "o", mfc="white", mec="black",
                ms=6, zorder=4)
        ax.plot(T[k][-1, 0], T[k][-1, 1], "s", mfc="black", mec="black",
                ms=6, zorder=4)
    ax.plot(T["MCF"][0, 0], T["MCF"][0, 1], "^", mfc="black", mec="black",
            ms=9, zorder=5)
    ax.annotate("MCF (fijo)", T["MCF"][0], textcoords="offset points",
                xytext=(8, -12), fontsize=9)

    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, color="0.9", lw=0.6)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_title("Trayectorias de las articulaciones y de la punta del dedo\n"
                 "(circulo = reposo, cuadrado = flexion maxima)")
    ax.legend(loc="best", fontsize=9)
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    return ruta


def longitud(curve):
    d = np.diff(curve, axis=0)
    return float(np.sum(np.hypot(d[:, 0], d[:, 1])))


if __name__ == "__main__":
    T = recorrer()
    csv_path = exportar_csv(T)
    png_path = graficar(T)
    print(f"Pasos calculados: {len(T['THETA2'])}")
    print(f"CSV de trayectorias : {csv_path}")
    print(f"Grafico             : {png_path}")
    print("--- Longitud de trayectoria (mm) ---")
    for k in ["IFP", "IFD", "PF", "D3"]:
        print(f"  {k:4s}: {longitud(T[k]):7.2f} mm")
    pf0, pff = T["PF"][0], T["PF"][-1]
    print(f"Punta dedo: reposo=({pf0[0]:.1f},{pf0[1]:.1f}) "
          f"final=({pff[0]:.1f},{pff[1]:.1f})  "
          f"desplazamiento={np.hypot(*(pff-pf0)):.1f} mm")
