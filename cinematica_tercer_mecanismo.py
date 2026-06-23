"""
cinematica_tercer_mecanismo.py
================================
Modulo de cinematica del exoesqueleto de rehabilitacion de dedo.

Porta FIELMENTE la cinematica de `CinematicaExoFinal.m` (dos mecanismos de
5 barras + dos de 4 barras) y AGREGA el tercer mecanismo de 4 barras (eslabones
Link9 = 25 mm y Link10 = 35 mm) que da movimiento relativo GRADUAL a la
articulacion interfalangica distal (IFD/DIP).

Diferencia clave respecto al diseno original:
  En `CinematicaExoFinal.m` la falange distal usa un offset CONSTANTE
      THETAfd(j) = THETAfm(j) + THETAauxfd
  por lo que la IFD se mueve rigidamente con la falange medial (sin flexion
  relativa). Aqui ese offset constante se REEMPLAZA por el angulo de salida de
  un mecanismo de 4 barras real (Link9, Link10) impulsado por la flexion de la
  articulacion IFP. El resultado es un movimiento distal GRADUAL, y la flexion
  natural en reposo se conserva calibrando el offset del soporte (bracket).

Todos los parametros de diseno son los ORIGINALES del archivo .m del disenador.
"""
import numpy as np

# =============================================================================
# PARAMETROS DE DISENO ORIGINALES (CinematicaExoFinal.m, dedo indice)
# =============================================================================
Bancada1 = 18
Bancada2 = 20
Link1 = 35
Link2 = 49
Link3 = 25
Link4 = 20
Link5 = 25
Link6 = 55
Link7 = 35
Link8 = 52
Link9 = 25     # Tercer mecanismo: acoplador (valor ORIGINAL del disenador)
Link10 = 35    # Tercer mecanismo: balancin  (valor ORIGINAL del disenador)
c2 = 46.01     # Distancia entre la art. IFP y el punto P3
TETHA2inicial = 0
TETHA1inicial = 109
THETA14B = 90
hsp = 17
dsp = 18
fp = 49        # falange proximal
fm = 26        # falange medial
fd = 24        # falange distal
THETAauxfm = 51.39
THETAauxfd = 38.78
reng = 2

# --- Parametros del tercer mecanismo de 4 barras (montado SOBRE el dedo) ---
# El 4 barras usa la PROPIA falange medial como manivela de entrada y un punto
# fijo Pa (soporte S3) RIGIDO a la falange proximal como pivote del acoplador.
# TODO el mecanismo (Pa, acoplador L9, balancin L10, punto D3) va por el lado
# DORSAL del dedo -el mismo lado que el resto del exoesqueleto- para NO chocar
# con la palma de la mano al cerrar el puno. Aun asi, la geometria del 4 barras
# hace que al flexionar la IFP la falange distal FLEXIONE (se curva hacia la
# palma) de forma GRADUAL, como un dedo real.
# Pa se define respecto a IFP con:
#   back3 : desplazamiento a lo largo de la falange proximal. NEGATIVO = el
#           soporte dorsal se extiende HACIA ADELANTE, pasando la IFP (mm).
#   up3   : standoff DORSAL (perpendicular a la falange proximal), perfil bajo (mm).
# Valores calibrados para flexion DIP gradual (~15 deg pico) manteniendo holgura
# dorsal con los huesos (Pa-falange medial ~5 mm) y sin colision con la palma.
back3 = -12.0
up3 = 2.0

# Asignacion a variables de las ecuaciones (igual que el .m)
r4 = Link1
r5 = Link2
r2 = Link3
r1 = Link4
r3 = Bancada1 / 2.0

a = Link4
b = Link5
c = np.sqrt(hsp**2 + dsp**2)
d = Bancada2

r1m2 = fp - 2 * dsp
r2m2 = Link7
r3m2 = Link5 / 2.0
r4m2 = Link3
r5m2 = Link6

a2 = Link7
b2 = Link8
d2 = np.sqrt(hsp**2 + dsp**2)

theta14B = np.deg2rad(THETA14B)


def cinematica_paso(THETA2_deg):
    """Calcula todas las posiciones del mecanismo para un angulo de manivela.

    Devuelve un diccionario con los puntos (numpy arrays [x, y]) y angulos
    relevantes, replicando exactamente las ecuaciones de CinematicaExoFinal.m.
    """
    theta2 = np.deg2rad(THETA2_deg)
    THETA1 = THETA2_deg / reng + TETHA1inicial
    theta1 = np.deg2rad(THETA1)

    # --- PRIMER MECANISMO DE 5 BARRAS ---
    e = (r1 * np.sin(theta1) - r4 * np.sin(theta2)) / (
        r4 * np.cos(theta2) - r1 * np.cos(theta1) + 2 * r3)
    temp1 = (2 * (r1 * r3 * np.cos(theta1) + r3 * r4 * np.cos(theta2))
             - r1**2 + r2**2 + r4**2 - r5**2)
    f = temp1 / (2 * (r4 * np.cos(theta2) - r1 * np.cos(theta1) + 2 * r3))
    daux = e**2 + 1
    g = 2 * (e * f - e * r1 * np.cos(theta1) + e * r3 - r1 * np.sin(theta1))
    h = (f**2 - 2 * f * (r1 * np.cos(theta1) - r3)
         - 2 * r1 * r3 * np.cos(theta1) + r1**2 + r3**2 - r2**2)
    pyP = (-g + np.sqrt(g**2 - 4 * daux * h)) / (2 * daux)
    pxP = e * pyP + f

    # --- PRIMER MECANISMO DE 4 BARRAS ---
    k1 = d * np.cos(theta14B) + a * np.cos(theta1)
    k2 = d * np.sin(theta14B) + a * np.sin(theta1)
    k3 = k1**2 + k2**2 + c**2 - b**2
    A1 = -k3 - 2 * k1 * c
    B1 = 4 * k2 * c
    C1 = 2 * k1 * c - k3
    tantheta42 = (-B1 - np.sqrt(B1**2 - 4 * A1 * C1)) / (2 * A1)
    theta4a = 2 * np.arctan(tantheta42)
    THETA4a = np.rad2deg(theta4a)
    if THETA4a < 0:
        THETA4a += 360

    THETAfp = THETA4a + np.rad2deg(np.arctan2(hsp, dsp))
    thetafp = np.deg2rad(THETAfp)
    pxIFP = fp * np.cos(thetafp) - d * np.cos(theta14B) - r3
    pyIFP = fp * np.sin(thetafp) - d * np.sin(theta14B)

    pxS1 = c * np.cos(theta4a) - d * np.cos(theta14B) - r3
    pyS1 = c * np.sin(theta4a) - d * np.sin(theta14B)
    THETAps2 = THETAfp - np.rad2deg(np.arctan2(hsp, (fp - dsp)))
    thetaps2 = np.deg2rad(THETAps2)
    rs2 = np.sqrt(hsp**2 + (fp - dsp)**2)
    pxS2 = rs2 * np.cos(thetaps2) - d * np.cos(theta14B) - r3
    pyS2 = rs2 * np.sin(thetaps2) - d * np.sin(theta14B)

    pxM4 = a * np.cos(theta1) - r3
    pyM4 = a * np.sin(theta1)

    # --- SEGUNDO MECANISMO DE 5 BARRAS (sistema secundario) ---
    THETAroll = np.rad2deg(np.arctan2(pyM4 - pyS1, pxM4 - pxS1))
    thetaroll = np.deg2rad(THETAroll)

    THETA1m2so = np.rad2deg(np.arctan2(pyS2 - pyS1, pxS2 - pxS1))
    if THETA1m2so < 0:
        THETA1m2so += 360
    theta1m2 = np.deg2rad(THETA1m2so - THETAroll)

    THETA2m2so = np.rad2deg(np.arctan2(pyP - pyM4, pxP - pxM4))
    if THETA2m2so < 0:
        THETA2m2so += 360
    theta2m2 = np.deg2rad(THETA2m2so - THETAroll)

    temp2 = (r4m2 * np.cos(theta2m2) - r1m2 * np.cos(theta1m2) + 2 * r3m2)
    em2 = (r1m2 * np.sin(theta1m2) - r4m2 * np.sin(theta2m2)) / temp2
    temp3 = (2 * (r1m2 * r3m2 * np.cos(theta1m2)
                  + r3m2 * r4m2 * np.cos(theta2m2))
             - r1m2**2 + r2m2**2 + r4m2**2 - r5m2**2)
    fm2 = temp3 / (2 * temp2)
    dauxm2 = em2**2 + 1
    gm2 = 2 * (em2 * fm2 - em2 * r1m2 * np.cos(theta1m2)
               + em2 * r3m2 - r1m2 * np.sin(theta1m2))
    hm2 = (fm2**2 - 2 * fm2 * (r1m2 * np.cos(theta1m2) - r3m2)
           - 2 * r1m2 * r3m2 * np.cos(theta1m2)
           + r1m2**2 + r3m2**2 - r2m2**2)
    pyP2 = (-gm2 + np.sqrt(gm2**2 - 4 * dauxm2 * hm2)) / (2 * dauxm2)
    pxP2 = em2 * pyP2 + fm2

    p2mag = np.sqrt(pxP2**2 + pyP2**2)
    theta2p2 = np.deg2rad(np.rad2deg(np.arctan2(pyP2, pxP2)))
    pxAUX = (pxS1 + pxM4) / 2
    pyAUX = (pyS1 + pyM4) / 2
    pxP2so = p2mag * np.cos(theta2p2 + thetaroll) + pxAUX
    pyP2so = p2mag * np.sin(theta2p2 + thetaroll) + pyAUX

    # --- SEGUNDO MECANISMO DE 4 BARRAS ---
    THETA14B2 = np.rad2deg(np.arctan2(pyS2 - pyIFP, pxS2 - pxIFP))
    theta14B2 = np.deg2rad(THETA14B2)
    THETA24B2 = np.rad2deg(np.arctan2(pyP2so - pyS2, pxP2so - pxS2))
    if THETA24B2 < 0:
        THETA24B2 += 360
    theta24B2 = np.deg2rad(THETA24B2)

    k1m2 = d2 * np.cos(theta14B2) + a2 * np.cos(theta24B2)
    k2m2 = d2 * np.sin(theta14B2) + a2 * np.sin(theta24B2)
    k3m2 = k1m2**2 + k2m2**2 + c2**2 - b2**2
    A1m2 = -k3m2 - 2 * k1m2 * c2
    B1m2 = 4 * k2m2 * c2
    C1m2 = 2 * k1m2 * c2 - k3m2
    tantheta42m2 = (-B1m2 - np.sqrt(B1m2**2 - 4 * A1m2 * C1m2)) / (2 * A1m2)
    theta4am2 = 2 * np.arctan(tantheta42m2)
    THETA4am2 = np.rad2deg(theta4am2)
    if THETA4am2 < 0:
        THETA4am2 += 360

    pxP3 = pxIFP + c2 * np.cos(np.deg2rad(THETA4am2))
    pyP3 = pyIFP + c2 * np.sin(np.deg2rad(THETA4am2))

    # Falange medial (con flexion natural)
    THETAfm = THETA4am2 + THETAauxfm
    thetafm = np.deg2rad(THETAfm)
    pxIFD = fm * np.cos(thetafm) + pxIFP
    pyIFD = fm * np.sin(thetafm) + pyIFP

    return {
        "THETA2": THETA2_deg,
        "THETA1": THETA1,
        "MCF": np.array([-r3, -d]),
        "P": np.array([pxP, pyP]),
        "M4": np.array([pxM4, pyM4]),
        "S1": np.array([pxS1, pyS1]),
        "S2": np.array([pxS2, pyS2]),
        "IFP": np.array([pxIFP, pyIFP]),
        "P2": np.array([pxP2so, pyP2so]),
        "P3": np.array([pxP3, pyP3]),
        "IFD": np.array([pxIFD, pyIFD]),
        "THETAfp": THETAfp,
        "THETAfm": THETAfm,
    }


def _circle_intersections(c0, r0, c1, r1):
    """Interseccion de dos circulos. Devuelve (sol_a, sol_b) o None."""
    c0 = np.asarray(c0, dtype=float)
    c1 = np.asarray(c1, dtype=float)
    dvec = c1 - c0
    dist = np.hypot(*dvec)
    if dist > (r0 + r1) or dist < abs(r0 - r1) or dist == 0:
        return None
    aa = (r0**2 - r1**2 + dist**2) / (2 * dist)
    hh2 = r0**2 - aa**2
    if hh2 < 0:
        return None
    hh = np.sqrt(hh2)
    pm = c0 + aa * dvec / dist
    perp = np.array([-dvec[1], dvec[0]]) / dist
    return pm + hh * perp, pm - hh * perp


def tercer_mecanismo(estado, gamma_bracket=None, dorsal_sign=None):
    """Resuelve el tercer mecanismo de 4 barras para una pose dada.

    Cuadrilatero de 4 barras del tercer mecanismo:
      - Tierra:     Pa -> IFP  (bracket S3 rigido sobre la falange PROXIMAL)
      - Manivela:   IFP -> IFD (la PROPIA falange medial, fm = 26 mm)
      - Balancin:   IFD -> D3  (Link10 = 35 mm), rigido con la falange distal
      - Acoplador:  D3 -> Pa   (Link9 = 25 mm), por el lado DORSAL

    TODO el mecanismo va montado por el lado DORSAL del dedo (el mismo lado que
    el resto del exoesqueleto), para NO chocar con la palma al cerrar la mano.
    Aun asi, la geometria del 4 barras hace que al flexionar la IFP la falange
    distal FLEXIONE (se curva hacia la palma) de forma GRADUAL, igual que un
    dedo real.
    `gamma_bracket` calibra el offset del soporte para conservar la flexion
    natural inicial; `dorsal_sign` fija de forma CONSISTENTE el lado del montaje.
    """
    IFP = estado["IFP"]
    IFD = estado["IFD"]
    thetafp = np.deg2rad(estado["THETAfp"])

    # Direcciones de la falange proximal y su normal
    prox_dir = np.array([np.cos(thetafp), np.sin(thetafp)])
    prox_norm = np.array([-prox_dir[1], prox_dir[0]])

    # Signo dorsal: se decide UNA sola vez (calibracion) usando el lado de P3
    # (el resto del exoesqueleto va por el dorso) y luego se mantiene fijo.
    if dorsal_sign is None:
        dorsal_sign = 1.0 if np.dot(estado["P3"] - IFP, prox_norm) >= 0 else -1.0

    # TODO el tercer mecanismo va por el lado DORSAL (mismo lado que P3 y el
    # resto del exoesqueleto), para NO chocar con la palma al cerrar la mano.
    dorsal_norm = dorsal_sign * prox_norm

    # Anclaje del acoplador FIJO a la falange proximal mediante el soporte S3.
    # back3 negativo => el soporte se extiende hacia ADELANTE pasando la IFP;
    # up3 => standoff DORSAL de perfil bajo.
    Pa = IFP - back3 * prox_dir + up3 * dorsal_norm

    sols = _circle_intersections(Pa, Link9, IFD, Link10)
    if sols is None:
        return None

    # Rama del 4 barras (interseccion -perp). Con el anclaje dorsal adelantado,
    # esta rama coloca D3 por el DORSO de la falange distal y produce FLEXION
    # distal GRADUAL al cerrarse el dedo.
    D3 = sols[1]

    ang_rocker = np.arctan2(D3[1] - IFD[1], D3[0] - IFD[0])  # rad

    if gamma_bracket is None:
        # Calibrar para que esta pose conserve la flexion natural
        thetafd_nat = np.deg2rad(estado["THETAfm"] + THETAauxfd)
        gamma_bracket = thetafd_nat - ang_rocker

    THETAfd = np.rad2deg(ang_rocker + gamma_bracket)
    thetafd = np.deg2rad(THETAfd)
    PF = IFD + fd * np.array([np.cos(thetafd), np.sin(thetafd)])

    return {
        "Pa": Pa,
        "D3": D3,
        "PF": PF,
        "THETAfd": THETAfd,
        "gamma_bracket": gamma_bracket,
        "dorsal_sign": dorsal_sign,
        "ang_rocker": np.rad2deg(ang_rocker),
    }


if __name__ == "__main__":
    # Diagnostico: recorrer el bucle y reportar el rango de movimiento distal.
    pasos = range(0, 133)
    gamma = None
    dorsal = None
    rel_dip = []
    ok = 0
    fallos = 0
    primer = None
    for j in pasos:
        est = cinematica_paso(float(j))
        if gamma is None:
            tm0 = tercer_mecanismo(est)
            if tm0 is None:
                continue
            gamma = tm0["gamma_bracket"]
            dorsal = tm0["dorsal_sign"]
            primer = j
        tm = tercer_mecanismo(est, gamma_bracket=gamma, dorsal_sign=dorsal)
        if tm is None:
            fallos += 1
            continue
        ok += 1
        # Movimiento relativo en la IFD respecto al offset natural (desenrollado)
        rel = tm["THETAfd"] - (est["THETAfm"] + THETAauxfd)
        rel = (rel + 180) % 360 - 180
        rel_dip.append((j, rel, tm["THETAfd"], est["THETAfm"]))

    print(f"Parametros tercer mecanismo: back3={back3}, up3={up3}, "
          f"Link9={Link9}, Link10={Link10}")
    print(f"Calibracion gamma_bracket fijada en j={primer}")
    print(f"Pasos ensamblables: {ok}  | fallos de ensamble: {fallos}")
    if rel_dip:
        rels = [r[1] for r in rel_dip]
        print(f"Movimiento relativo IFD (gradual): "
              f"min={min(rels):.2f} deg, max={max(rels):.2f} deg, "
              f"rango={max(rels) - min(rels):.2f} deg")
        for j, rel, tfd, tfm in rel_dip[::20]:
            print(f"  j={j:3d}  THETAfm={tfm:7.2f}  THETAfd={tfd:7.2f}  "
                  f"rel_IFD={rel:+6.2f}")
