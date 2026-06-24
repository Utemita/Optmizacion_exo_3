"""
validacion_cinematica_DIP.py
=============================
Validacion del rango de movimiento (ROM) del exoesqueleto con el TERCER
mecanismo de 4 barras (Link9 = 25 mm, Link10 = 35 mm) que da movimiento
relativo GRADUAL a la articulacion interfalangica distal (IFD/DIP).

Recorre el bucle completo de la entrada (THETA2 = 0..132 grados, igual que el
.m original) usando la cinematica REAL portada en `cinematica_tercer_mecanismo.py`
y verifica:

  1) Rango de movimiento de cada articulacion:
        - MCP : flexion de la falange proximal      (THETAfp)
        - IFP : flexion de la falange medial relativa a la proximal
        - IFD : flexion de la falange distal relativa a la medial  <-- nuevo
  2) Que el movimiento de la IFD es GRADUAL (sin saltos bruscos).
  3) Movimiento relativo entre falanges adyacentes.

Genera la grafica `validacion_cinematica_DIP.png` (estilo B/N de ingenieria)
con los angulos articulares a lo largo del recorrido del actuador.

NOTA: el sandbox solo dispone de Python; este script reemplaza al antiguo
`validacion_cinematica_DIP.m`. La cinematica es identica a la del modelo MATLAB,
por lo que los resultados son directamente trasladables a MATLAB/Octave.
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import cinematica_tercer_mecanismo as K


def _wrap180(a):
    """Normaliza un angulo (grados) al rango (-180, 180]."""
    return (a + 180.0) % 360.0 - 180.0


def recorrer():
    """Recorre el bucle del actuador y devuelve los ROM articulares."""
    pasos = list(range(0, 133))  # THETA2 = 0..132 (igual que el .m original)

    THETA2 = []
    mcp_abs = []     # THETAfp (flexion absoluta de la proximal)
    ifp_rel = []     # IFP relativa = THETAfm - THETAfp
    ifd_rel = []     # IFD relativa = THETAfd - THETAfm
    ifd_abs = []     # THETAfd (flexion absoluta de la distal)

    gamma = None
    dorsal = None
    # Referencias en reposo (j=0) para medir el movimiento RELATIVO desde cero
    fp0 = fm0_rel = fd0_rel = None

    for j in pasos:
        est = K.cinematica_paso(float(j))
        if gamma is None:
            cal = K.tercer_mecanismo(est)
            if cal is None:
                continue
            gamma = cal["gamma_bracket"]
            dorsal = cal["dorsal_sign"]
        tm = K.tercer_mecanismo(est, gamma_bracket=gamma, dorsal_sign=dorsal)
        if tm is None:
            continue

        thetafp = est["THETAfp"]
        thetafm = est["THETAfm"]
        thetafd = tm["THETAfd"]

        rel_ifp = _wrap180(thetafm - thetafp)
        rel_ifd = _wrap180(thetafd - thetafm)

        if fp0 is None:
            fp0 = thetafp
            fm0_rel = rel_ifp
            fd0_rel = rel_ifd

        THETA2.append(j)
        mcp_abs.append(_wrap180(thetafp - fp0))       # MCP desde reposo
        ifp_rel.append(_wrap180(rel_ifp - fm0_rel))   # IFP relativa desde reposo
        ifd_rel.append(_wrap180(rel_ifd - fd0_rel))   # IFD relativa desde reposo
        ifd_abs.append(thetafd)

    return {
        "THETA2": np.array(THETA2),
        "MCP": np.array(mcp_abs),
        "IFP": np.array(ifp_rel),
        "IFD": np.array(ifd_rel),
        "IFD_abs": np.array(ifd_abs),
    }


def reportar(data):
    """Imprime el rango de movimiento y la suavidad del movimiento distal."""
    print("=" * 64)
    print(" VALIDACION CINEMATICA DEL TERCER MECANISMO (IFD / DIP)")
    print(f" Parametros: Link9={K.Link9} mm, Link10={K.Link10} mm, "
          f"fp={K.fp}, fm={K.fm}, fd={K.fd}")
    print("=" * 64)

    for nombre in ("MCP", "IFP", "IFD"):
        v = data[nombre]
        print(f" {nombre:4s}: rango = {v.max() - v.min():6.2f} deg   "
              f"(min={v.min():7.2f}, max={v.max():7.2f})")

    # Suavidad del movimiento IFD: maximo salto entre pasos adyacentes
    difs = np.abs(np.diff(data["IFD"]))
    print("-" * 64)
    print(f" Suavidad IFD: salto maximo entre pasos adyacentes = "
          f"{difs.max():.2f} deg")
    print(f" Pasos ensamblados correctamente: {len(data['THETA2'])} / 133")
    if difs.max() < 5.0:
        print(" -> Movimiento DIP GRADUAL verificado (sin saltos bruscos).")
    else:
        print(" -> ADVERTENCIA: se detecto un salto > 5 deg en la IFD.")
    print("=" * 64)


def graficar(data, out):
    """Genera la grafica de ROM articular en estilo B/N de ingenieria."""
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    x = data["THETA2"]
    ax.plot(x, data["MCP"], color="black", linewidth=1.8, linestyle="-",
            label="MCP (falange proximal)")
    ax.plot(x, data["IFP"], color="black", linewidth=1.8, linestyle="--",
            label="IFP (medial rel. proximal)")
    ax.plot(x, data["IFD"], color="black", linewidth=1.8, linestyle=":",
            label="IFD (distal rel. medial)")

    ax.set_xlabel("Entrada del actuador  THETA2  [grados]", fontsize=11)
    ax.set_ylabel("Flexion articular relativa al reposo  [grados]", fontsize=11)
    ax.set_title("Rango de movimiento articular con el tercer mecanismo (IFD)",
                 fontsize=12)
    ax.grid(True, color="0.85", linewidth=0.6)
    ax.axhline(0, color="black", linewidth=0.8)
    leg = ax.legend(loc="best", framealpha=1.0, edgecolor="black")
    leg.get_frame().set_facecolor("white")

    plt.tight_layout()
    plt.savefig(out, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close()
    print("Grafica de validacion generada:", out)


if __name__ == "__main__":
    datos = recorrer()
    reportar(datos)
    graficar(datos,
             "/projects/sandbox/Optmizacion_exo_3/validacion_cinematica_DIP.png")
