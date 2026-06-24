"""
validacion_trayectorias_cad.py
==============================
Valida las trayectorias exportadas del modelo CAD (SolidWorks) contra las
trayectorias calculadas por la cinematica del tercer mecanismo.

ENTRADAS
--------
  - IFP.csv, IFD.csv, TIP.csv : trazas exportadas de SolidWorks (un punto por
        fila, formato "X(mm), Y(mm), Z(mm)"; 2 lineas de cabecera). El CAD
        entrega 57 puntos por traza y la cinematica 133, por lo que NO hay
        correspondencia 1:1 y hay que re-muestrear / ajustar.
  - trayectorias_cinematica_ref.csv : salida de la cinematica
        (columnas IFP_x/y, IFD_x/y, PF_x/y, ...). PF = punta del dedo = TIP.

METODOLOGIA
-----------
  1. Se parametriza cada curva por longitud de arco NORMALIZADA s in [0,1] y se
     re-muestrea a una grilla comun (ajuste para igualar el numero de puntos).
  2. ALINEACION RIGIDA GLOBAL (Kabsch/Procrustes 2D, rotacion + traslacion, sin
     escala) calculada con TODAS las trazas a la vez, porque el CAD tiene un
     unico sistema de coordenadas. Se reporta el angulo, la traslacion y un
     factor de escala de diagnostico (deben salir ~0 / ~1 si el CAD se
     construyo en el mismo marco que la cinematica).
  3. ERROR por traza, ya alineadas:
       (a) por longitud de arco: distancia euclidiana entre ambas curvas
           evaluadas en la misma s (error punto-a-punto correspondiente).
       (b) punto-mas-cercano: distancia de cada punto CAD a la polilinea de la
           cinematica (independiente de la parametrizacion; mide desviacion
           puramente geometrica de la trayectoria).
     Se reportan RMS, media y maximo.
  4. Graficas B/N de ingenieria: superposicion CAD vs cinematica y curvas de
     error a lo largo del recorrido.

SALIDAS
-------
  - validacion_trayectorias.png  : figura comparativa.
  - validacion_trayectorias_error.csv : error por traza y por punto.
  - resumen impreso en consola.
"""
import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# ----------------------------------------------------------------------------
# Carga de datos
# ----------------------------------------------------------------------------
def cargar_cad(ruta):
    """Lee un CSV de SolidWorks (2 lineas de cabecera, luego X,Y,Z en mm).

    Devuelve un array Nx2 con (x, y) en mm (se descarta Z, que es constante).
    """
    pts = []
    with open(ruta, "r") as fh:
        for i, linea in enumerate(fh):
            if i < 2:                      # 'Ruta de trazoNN' y cabecera X,Y,Z
                continue
            linea = linea.strip()
            if not linea:
                continue
            campos = linea.split(",")
            if len(campos) < 2:
                continue
            x = float(campos[0]); y = float(campos[1])
            pts.append((x, y))
    return np.asarray(pts, dtype=float)


def cargar_cinematica(ruta, columnas):
    """Lee trayectorias_cinematica_ref.csv y extrae las columnas (x, y) pedidas.

    `columnas` es por ejemplo ("IFP_x", "IFP_y").
    """
    with open(ruta, "r") as fh:
        rd = csv.DictReader(fh)
        cx, cy = columnas
        pts = [(float(fila[cx]), float(fila[cy])) for fila in rd]
    return np.asarray(pts, dtype=float)


# ----------------------------------------------------------------------------
# Re-muestreo por longitud de arco
# ----------------------------------------------------------------------------
def long_arco_normalizada(curva):
    """Devuelve el parametro de longitud de arco acumulada normalizado [0,1]."""
    d = np.diff(curva, axis=0)
    seg = np.hypot(d[:, 0], d[:, 1])
    s = np.concatenate([[0.0], np.cumsum(seg)])
    total = s[-1]
    if total <= 0:
        raise ValueError("Curva degenerada (longitud cero).")
    return s / total, total


def remuestrear(curva, s_obj):
    """Interpola la curva (Nx2) sobre los parametros de arco objetivo s_obj."""
    s, _ = long_arco_normalizada(curva)
    x = np.interp(s_obj, s, curva[:, 0])
    y = np.interp(s_obj, s, curva[:, 1])
    return np.column_stack([x, y])


# ----------------------------------------------------------------------------
# Alineacion rigida (Kabsch / Procrustes 2D)
# ----------------------------------------------------------------------------
def alinear_rigido(P, Q):
    """Mejor transformacion rigida (R, t) que lleva P sobre Q: Q ~= R*P + t.

    P, Q son arrays Nx2 de puntos correspondientes. Sin escala.
    Devuelve (R, t, escala_diagnostico).
    """
    cP = P.mean(axis=0)
    cQ = Q.mean(axis=0)
    P0 = P - cP
    Q0 = Q - cQ
    H = P0.T @ Q0
    U, S, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    D = np.diag([1.0, d])
    R = Vt.T @ D @ U.T
    t = cQ - R @ cP
    # factor de escala de diagnostico (no se aplica): razon de dispersiones
    escala = float(np.sum(S * np.array([1.0, d])) / np.sum(P0 ** 2))
    return R, t, escala


def aplicar_rigido(curva, R, t):
    return (R @ curva.T).T + t


# ----------------------------------------------------------------------------
# Metricas de error
# ----------------------------------------------------------------------------
def dist_punto_polilinea(p, poli):
    """Distancia minima de un punto p a una polilinea (segmentos de `poli`)."""
    a = poli[:-1]
    b = poli[1:]
    ab = b - a
    ap = p - a
    denom = np.einsum("ij,ij->i", ab, ab)
    denom = np.where(denom == 0, 1e-12, denom)
    tt = np.clip(np.einsum("ij,ij->i", ap, ab) / denom, 0.0, 1.0)
    proy = a + tt[:, None] * ab
    d = np.hypot(p[0] - proy[:, 0], p[1] - proy[:, 1])
    return float(d.min())


def error_punto_mas_cercano(cad, cin):
    """Para cada punto CAD, distancia a la polilinea de la cinematica."""
    return np.array([dist_punto_polilinea(p, cin) for p in cad])


def stats(vec):
    return {
        "rms": float(np.sqrt(np.mean(vec ** 2))),
        "media": float(np.mean(vec)),
        "max": float(np.max(vec)),
    }


# ----------------------------------------------------------------------------
# Programa principal
# ----------------------------------------------------------------------------
TRAZAS = [
    ("IFP", "IFP.csv", ("IFP_x", "IFP_y")),
    ("IFD", "IFD.csv", ("IFD_x", "IFD_y")),
    ("TIP", "TIP.csv", ("PF_x", "PF_y")),
]
REF_CIN = "trayectorias_cinematica_ref.csv"
N_RES = 200          # puntos de la grilla comun de longitud de arco


def main():
    # --- carga ---
    datos = {}
    for nombre, ruta_cad, cols in TRAZAS:
        cad = cargar_cad(ruta_cad)
        cin = cargar_cinematica(REF_CIN, cols)
        datos[nombre] = {"cad": cad, "cin": cin}

    # --- grilla comun de longitud de arco ---
    s_obj = np.linspace(0.0, 1.0, N_RES)

    # Re-muestreo de ambas curvas a la grilla comun (AJUSTE 57 vs 133 puntos)
    for nombre in datos:
        datos[nombre]["cad_rs"] = remuestrear(datos[nombre]["cad"], s_obj)
        datos[nombre]["cin_rs"] = remuestrear(datos[nombre]["cin"], s_obj)

    # --- alineacion rigida GLOBAL (un solo marco para las 3 trazas) ---
    P = np.vstack([datos[n]["cad_rs"] for n in datos])   # CAD apilado
    Q = np.vstack([datos[n]["cin_rs"] for n in datos])   # cinematica apilada
    R, t, escala = alinear_rigido(P, Q)
    ang_deg = np.degrees(np.arctan2(R[1, 0], R[0, 0]))

    # Aplicar la alineacion a las trazas CAD (re-muestreadas y originales)
    for nombre in datos:
        datos[nombre]["cad_rs_al"] = aplicar_rigido(datos[nombre]["cad_rs"], R, t)
        datos[nombre]["cad_al"] = aplicar_rigido(datos[nombre]["cad"], R, t)

    # --- errores por traza ---
    resumen = {}
    for nombre in datos:
        cad_rs_al = datos[nombre]["cad_rs_al"]
        cin_rs = datos[nombre]["cin_rs"]
        # (a) error por longitud de arco (correspondencia por s)
        e_arco = np.hypot(cad_rs_al[:, 0] - cin_rs[:, 0],
                          cad_rs_al[:, 1] - cin_rs[:, 1])
        # (b) error punto-mas-cercano (puntos CAD originales alineados)
        e_cerca = error_punto_mas_cercano(datos[nombre]["cad_al"],
                                          datos[nombre]["cin"])
        datos[nombre]["e_arco"] = e_arco
        datos[nombre]["e_cerca"] = e_cerca
        resumen[nombre] = {"arco": stats(e_arco), "cerca": stats(e_cerca)}

    # --- impresion de resultados ---
    print("=" * 70)
    print(" VALIDACION DE TRAYECTORIAS  CAD (SolidWorks) vs CINEMATICA")
    print("=" * 70)
    for nombre in datos:
        n_cad = len(datos[nombre]["cad"])
        n_cin = len(datos[nombre]["cin"])
        print(f"  {nombre}: CAD={n_cad} pts | cinematica={n_cin} pts")
    print("-" * 70)
    print(" Alineacion rigida global (CAD -> cinematica):")
    print(f"   rotacion   = {ang_deg:+.4f} deg")
    print(f"   traslacion = ({t[0]:+.4f}, {t[1]:+.4f}) mm   |t|={np.hypot(*t):.4f} mm")
    print(f"   escala diag.= {escala:.6f}  (≈1 confirma misma unidad/marco)")
    print("-" * 70)
    print(f"{'traza':>6} | {'error por long. de arco (mm)':^32} | {'punto-cercano (mm)':^26}")
    print(f"{'':>6} | {'RMS':>9} {'media':>9} {'max':>9} | {'RMS':>8} {'media':>8} {'max':>8}")
    for nombre in datos:
        a = resumen[nombre]["arco"]; c = resumen[nombre]["cerca"]
        print(f"{nombre:>6} | {a['rms']:9.4f} {a['media']:9.4f} {a['max']:9.4f} "
              f"| {c['rms']:8.4f} {c['media']:8.4f} {c['max']:8.4f}")
    print("-" * 70)
    # error global (todas las trazas juntas, por longitud de arco)
    e_all = np.concatenate([datos[n]["e_arco"] for n in datos])
    g = stats(e_all)
    print(f" GLOBAL (arco): RMS={g['rms']:.4f} mm  media={g['media']:.4f} mm  "
          f"max={g['max']:.4f} mm")
    print("=" * 70)

    exportar_error_csv(datos, s_obj)
    graficar(datos, s_obj, ang_deg, t, escala, resumen, g)
    print("Figura  : validacion_trayectorias.png")
    print("CSV error: validacion_trayectorias_error.csv")
    return datos, resumen


def exportar_error_csv(datos, s_obj, ruta="validacion_trayectorias_error.csv"):
    with open(ruta, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["traza", "s_norm", "cad_x", "cad_y", "cin_x", "cin_y",
                    "error_arco_mm"])
        for nombre in datos:
            cad = datos[nombre]["cad_rs_al"]; cin = datos[nombre]["cin_rs"]
            e = datos[nombre]["e_arco"]
            for i in range(len(s_obj)):
                w.writerow([nombre, f"{s_obj[i]:.4f}",
                            f"{cad[i,0]:.4f}", f"{cad[i,1]:.4f}",
                            f"{cin[i,0]:.4f}", f"{cin[i,1]:.4f}",
                            f"{e[i]:.5f}"])
    return ruta


def graficar(datos, s_obj, ang_deg, t, escala, resumen, g,
             ruta="validacion_trayectorias.png"):
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    estilos = {"IFP": "-", "IFD": "--", "TIP": "-."}

    # (1) Superposicion de trayectorias
    ax = axes[0, 0]
    ax.set_facecolor("white")
    for nombre in datos:
        cin = datos[nombre]["cin"]
        cad = datos[nombre]["cad_al"]
        ls = estilos[nombre]
        ax.plot(cin[:, 0], cin[:, 1], color="black", ls=ls, lw=2.0,
                zorder=3, label=f"{nombre} cinematica")
        ax.plot(cad[:, 0], cad[:, 1], color="0.5", ls="none", marker="o",
                ms=3.0, zorder=4, label=f"{nombre} CAD")
    # marcar inicio (circulo) y fin (cuadrado) de la cinematica
    for nombre in datos:
        cin = datos[nombre]["cin"]
        ax.plot(cin[0, 0], cin[0, 1], "o", mfc="white", mec="black", ms=6, zorder=5)
        ax.plot(cin[-1, 0], cin[-1, 1], "s", mfc="black", mec="black", ms=6, zorder=5)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, color="0.9", lw=0.6)
    ax.set_xlabel("x (mm)"); ax.set_ylabel("y (mm)")
    ax.set_title("Superposicion: trayectorias CAD vs cinematica\n"
                 "(linea = cinematica, puntos = CAD; o=reposo, []=flexion max)")
    ax.legend(loc="best", fontsize=8, ncol=2)

    # (2) Error por longitud de arco
    ax = axes[0, 1]
    for nombre in datos:
        ax.plot(s_obj, datos[nombre]["e_arco"], ls=estilos[nombre],
                color="black", lw=1.8, label=nombre)
    ax.grid(True, color="0.9", lw=0.6)
    ax.set_xlabel("progresion normalizada del recorrido  s")
    ax.set_ylabel("error (mm)")
    ax.set_title("Error por longitud de arco (CAD alineado vs cinematica)")
    ax.legend(loc="best", fontsize=9)

    # (3) Error punto-mas-cercano (histograma/curva por punto CAD)
    ax = axes[1, 0]
    for nombre in datos:
        e = datos[nombre]["e_cerca"]
        ax.plot(np.linspace(0, 1, len(e)), e, ls=estilos[nombre],
                color="black", lw=1.8, marker=".", ms=4, label=nombre)
    ax.grid(True, color="0.9", lw=0.6)
    ax.set_xlabel("indice de punto CAD (normalizado)")
    ax.set_ylabel("dist. a polilinea cinematica (mm)")
    ax.set_title("Error punto-mas-cercano (geometrico, indep. de parametrizacion)")
    ax.legend(loc="best", fontsize=9)

    # (4) Tabla-resumen como texto
    ax = axes[1, 1]
    ax.axis("off")
    lineas = [
        "RESUMEN DE VALIDACION",
        "",
        f"Alineacion rigida global CAD -> cinematica:",
        f"   rotacion    = {ang_deg:+.4f} deg",
        f"   traslacion  = ({t[0]:+.3f}, {t[1]:+.3f}) mm",
        f"   |traslacion|= {np.hypot(*t):.4f} mm",
        f"   escala diag.= {escala:.5f}",
        "",
        f"{'traza':>6}  {'RMS_arco':>9}  {'max_arco':>9}  {'RMS_cerca':>10}",
    ]
    for nombre in datos:
        a = resumen[nombre]["arco"]; c = resumen[nombre]["cerca"]
        lineas.append(f"{nombre:>6}  {a['rms']:9.4f}  {a['max']:9.4f}  {c['rms']:10.4f}")
    lineas += [
        "",
        f"GLOBAL (arco): RMS={g['rms']:.4f} mm  max={g['max']:.4f} mm",
        "",
        "Unidades en mm. Error pequeno (sub-mm) => el CAD",
        "reproduce la trayectoria de la cinematica.",
    ]
    ax.text(0.0, 1.0, "\n".join(lineas), va="top", ha="left",
            family="monospace", fontsize=10, transform=ax.transAxes)

    fig.suptitle("Validacion de trayectorias del modelo CAD frente a la cinematica",
                 fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    return ruta


if __name__ == "__main__":
    main()
