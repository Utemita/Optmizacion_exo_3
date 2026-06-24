"""
cinematica_subactuado.py
========================
NUEVO mecanismo SUBACTUADO (1 actuador, 3 articulaciones con FLEXION) para el
exoesqueleto de rehabilitacion de dedo. Disenado para MAYOR rango de movimiento
que el mecanismo original (que daba ~15 deg en la IFD).

RESULTADO (1 grado de libertad):
    MCF (alpha):  0  ->  75 deg
    IFP (beta) :  0  ->  ~74 deg   (flexion monotona)
    IFD (gamma):  0  ->  ~63 deg   (flexion monotona)

POR QUE SEIS-BARRAS (Watt-II) Y NO 4 BARRAS:
  Un 4 barras dorsal anclado al metacarpo acopla la MCF en EXTENSION de la IFP
  (y se bloquea ~alpha=20 deg); un 4 barras anclado a la proximal solo logra
  ~12 deg en la IFD porque su balancin debe barrer beta+gamma. Para gran ROM con
  buena transmision, CADA articulacion acoplada usa un seis-barras Watt-II cuyo
  balancin de salida barre SOLO el angulo relativo de esa articulacion.

ARQUITECTURA (montaje DORSAL, para no chocar con la palma al cerrar el puno):
  - Entrada activa: la falange PROXIMAL es impulsada directamente en la MCF por
    el actuador (motor/engranaje en el eje MCF)  ->  alpha.
  - Acoplamiento A (MCF -> IFP), seis-barras Watt-II:
      * Balancin biela "campana" (bell-crank) pivota en Q, FIJO a la proximal.
      * 1a etapa (4 barras): tierra metacarpo (MCF, B0) -> gira el bell-crank.
      * 2a etapa (4 barras): tierra proximal (Q, IFP) -> mueve el balancin Ma
        solidario a la falange MEDIAL  ->  beta. Balancin barre solo beta.
  - Acoplamiento B (IFP -> IFD), seis-barras Watt-II:
      * Bell-crank pivota en R, FIJO a la falange MEDIAL.
      * 1a etapa: tierra (S en proximal, R en medial) -> el cierre de la IFP
        gira el bell-crank.
      * 2a etapa: tierra medial (R, IFD) -> mueve el balancin Dc solidario a la
        falange DISTAL  ->  gamma. Balancin barre solo gamma.

CONVENCION:
  - MCF en el origen (0,0). Dedo extendido a lo largo de +x. Dorsal = +y.
  - Flexion = las falanges se curvan hacia -y (lado palmar).
  - Angulos articulares RELATIVOS: alpha (MCF), beta (IFP), gamma (IFD), >0 flex.
  - Orientaciones ABSOLUTAS: Phi1=-alpha, Phi2=-(alpha+beta),
    Phi3=-(alpha+beta+gamma).

Todas las posiciones se resuelven por interseccion de circunferencias (cierre de
lazo de cada 4 barras), igual que en cinematica_tercer_mecanismo.py. Parametros
hallados por sintesis con busqueda Monte Carlo (ver tune_subactuado.py).
"""
import numpy as np

# =============================================================================
# PARAMETROS DE DISENO
# =============================================================================
fp = 49.0   # falange proximal (mm)
fm = 26.0   # falange medial   (mm)
fd = 24.0   # falange distal   (mm)

ALPHA_MAX = 75.0
ALPHA_STEP = 1.0

# Seis-barras A (MCF -> IFP). Bell-crank en Q (proximal); anclaje B0 (metacarpo)
P6 = dict(qL=12.274, qU=6.294, b0x=-4.183, b0y=25.639, La1=20.901,
          psi1=70.528, rho=-146.590, La2=14.346, mbx=-9.413, mby=9.852,
          BR1=1, BR2=1)

# Seis-barras B (IFP -> IFD). Bell-crank en R (medial); anclaje S (proximal)
PD = dict(rL=6.737, rU=12.930, sL=40.903, sU=8.339, Lf1=19.133,
          phi0=138.184, sig=97.091, Lf2=12.615, dcx=-5.351, dcy=6.303,
          BF1=1, BF2=1)


# =============================================================================
# UTILIDADES
# =============================================================================
def _ang(v):
    return np.arctan2(v[1], v[0])


def _circ_int(c0, r0, c1, r1):
    """Interseccion de dos circunferencias. Devuelve (sol+, sol-) o None."""
    c0 = np.asarray(c0, float)
    c1 = np.asarray(c1, float)
    d = c1 - c0
    dist = np.hypot(*d)
    if dist > (r0 + r1) or dist < abs(r0 - r1) or dist == 0:
        return None
    a = (r0**2 - r1**2 + dist**2) / (2 * dist)
    h2 = r0**2 - a**2
    if h2 < 0:
        return None
    h = np.sqrt(h2)
    pm = c0 + a * d / dist
    perp = np.array([-d[1], d[0]]) / dist
    return pm + h * perp, pm - h * perp


def _branch(sols, idx, prev):
    """Rama por continuidad (cercana a prev); si no hay prev, usa idx fijo."""
    if prev is None:
        return sols[idx]
    return sols[0] if np.hypot(*(sols[0] - prev)) <= np.hypot(*(sols[1] - prev)) \
        else sols[1]


def _mu(a, vertex, b):
    """Angulo de transmision en 'vertex' entre los segmentos a-vertex y b-vertex."""
    u = a - vertex
    w = b - vertex
    return np.degrees(np.arccos(np.clip(
        np.dot(u, w) / (np.hypot(*u) * np.hypot(*w)), -1, 1)))


# --- Constantes derivadas (longitudes de acoplador fijadas por la pose recta) -
_B0 = np.array([P6['b0x'], P6['b0y']])
_psi1 = np.deg2rad(P6['psi1'])
_rho = np.deg2rad(P6['rho'])
_Q0 = np.array([P6['qL'], P6['qU']])
_E10 = _Q0 + P6['La1'] * np.array([np.cos(_psi1), np.sin(_psi1)])
_Lc1 = np.hypot(*(_E10 - _B0))
_PIP0 = np.array([fp, 0.0])
_Ma0 = _PIP0 + np.array([P6['mbx'], P6['mby']])
_Lr = np.hypot(P6['mbx'], P6['mby'])
_lam0 = _ang(np.array([P6['mbx'], P6['mby']]))
_E20 = _Q0 + P6['La2'] * np.array([np.cos(_psi1 + _rho), np.sin(_psi1 + _rho)])
_Lc2 = np.hypot(*(_E20 - _Ma0))

_phi0 = np.deg2rad(PD['phi0'])
_sig = np.deg2rad(PD['sig'])
_R0 = _PIP0 + np.array([PD['rL'], PD['rU']])
_S0 = np.array([PD['sL'], PD['sU']])
_F10 = _R0 + PD['Lf1'] * np.array([np.cos(_phi0), np.sin(_phi0)])
_Lcf1 = np.hypot(*(_F10 - _S0))
_F20 = _R0 + PD['Lf2'] * np.array([np.cos(_phi0 + _sig), np.sin(_phi0 + _sig)])
_DIP0 = np.array([fp + fm, 0.0])
_Dc0 = _DIP0 + np.array([PD['dcx'], PD['dcy']])
_Lcf2 = np.hypot(*(_F20 - _Dc0))
_Ldc = np.hypot(PD['dcx'], PD['dcy'])
_lam0d = _ang(np.array([PD['dcx'], PD['dcy']]))


def solve(alpha_deg, prev=None):
    """Cinematica completa para un angulo de entrada MCF (alpha).

    prev: dict opcional {'Ma','E1','Dc','F1'} para continuidad de rama.
    Devuelve dict con TODOS los puntos del mecanismo y los angulos, o None.
    """
    a = np.deg2rad(alpha_deg)
    Phi1 = -a
    u1 = np.array([np.cos(Phi1), np.sin(Phi1)])
    n1 = np.array([-np.sin(Phi1), np.cos(Phi1)])
    MCP = np.array([0.0, 0.0])
    PIP = MCP + fp * u1

    # ----- Seis-barras A: MCF -> IFP -----
    Q = MCP + P6['qL'] * u1 + P6['qU'] * n1
    s1 = _circ_int(Q, P6['La1'], _B0, _Lc1)
    if s1 is None:
        return None
    E1 = _branch(s1, P6['BR1'], prev.get('E1') if prev else None)
    psi = _ang(E1 - Q)
    E2 = Q + P6['La2'] * np.array([np.cos(psi + _rho), np.sin(psi + _rho)])
    s2 = _circ_int(PIP, _Lr, E2, _Lc2)
    if s2 is None:
        return None
    Ma = _branch(s2, P6['BR2'], prev.get('Ma') if prev else None)
    Phi2 = _ang(Ma - PIP) - _lam0
    beta = -Phi2 - a
    u2 = np.array([np.cos(Phi2), np.sin(Phi2)])
    n2 = np.array([-np.sin(Phi2), np.cos(Phi2)])
    DIP = PIP + fm * u2

    # ----- Seis-barras B: IFP -> IFD -----
    S = MCP + PD['sL'] * u1 + PD['sU'] * n1
    R = PIP + PD['rL'] * u2 + PD['rU'] * n2
    f1 = _circ_int(R, PD['Lf1'], S, _Lcf1)
    if f1 is None:
        return None
    F1 = _branch(f1, PD['BF1'], prev.get('F1') if prev else None)
    th = _ang(F1 - R)
    F2 = R + PD['Lf2'] * np.array([np.cos(th + _sig), np.sin(th + _sig)])
    f2 = _circ_int(DIP, _Ldc, F2, _Lcf2)
    if f2 is None:
        return None
    Dc = _branch(f2, PD['BF2'], prev.get('Dc') if prev else None)
    Phi3 = _ang(Dc - DIP) - _lam0d
    gamma = -Phi3 + Phi2
    u3 = np.array([np.cos(Phi3), np.sin(Phi3)])
    TIP = DIP + fd * u3

    return {
        "alpha": alpha_deg, "beta": np.degrees(beta), "gamma": np.degrees(gamma),
        "Phi1": np.degrees(Phi1), "Phi2": np.degrees(Phi2),
        "Phi3": np.degrees(Phi3),
        # falange / articulaciones
        "MCP": MCP, "PIP": PIP, "DIP": DIP, "TIP": TIP,
        # seis-barras A
        "B0": _B0, "Q": Q, "E1": E1, "E2": E2, "Ma": Ma,
        # seis-barras B
        "S": S, "R": R, "F1": F1, "F2": F2, "Dc": Dc,
        # angulos de transmision (en juntas acoplador-balancin)
        "muA1": _mu(Q, E1, _B0), "muA2": _mu(PIP, Ma, E2),
        "muB1": _mu(R, F1, S), "muB2": _mu(DIP, Dc, F2),
        "u1": u1, "u2": u2, "u3": u3, "n1": n1, "n2": n2,
    }


def barrido(alpha_max=ALPHA_MAX, step=ALPHA_STEP):
    estados = []
    prev = None
    a = 0.0
    while a <= alpha_max + 1e-9:
        st = solve(a, prev)
        if st is None:
            estados.append({"alpha": a, "fail": True})
            a += step
            continue
        estados.append(st)
        prev = {k: st[k] for k in ("Ma", "E1", "Dc", "F1")}
        a += step
    return estados


if __name__ == "__main__":
    sts = barrido()
    ok = [s for s in sts if not s.get("fail")]
    fail = [s for s in sts if s.get("fail")]
    print("=" * 66)
    print(" CINEMATICA MECANISMO SUBACTUADO  (3 art. con flexion, 1 actuador)")
    print("=" * 66)
    print(f"Falanges: fp={fp}  fm={fm}  fd={fd}")
    print(f"Pasos ensamblables: {len(ok)} | fallos: {len(fail)}")
    if ok:
        b = np.array([s["beta"] for s in ok])
        g = np.array([s["gamma"] for s in ok])
        mono_b = np.all(np.diff(b) >= -0.4)
        mono_g = np.all(np.diff(g) >= -0.4)
        muA = [min(s["muA1"], s["muA2"], 180 - s["muA1"], 180 - s["muA2"])
               for s in ok]
        muB = [min(s["muB1"], s["muB2"], 180 - s["muB1"], 180 - s["muB2"])
               for s in ok]
        print("-" * 66)
        print(f"ROM MCF (alpha): {ok[0]['alpha']:.0f} -> {ok[-1]['alpha']:.0f} deg")
        print(f"ROM IFP (beta) : {b.min():+.1f} -> {b.max():+.1f} deg  "
              f"(rango {b.max()-b.min():.1f})  monotona={mono_b}")
        print(f"ROM IFD (gamma): {g.min():+.1f} -> {g.max():+.1f} deg  "
              f"(rango {g.max()-g.min():.1f})  monotona={mono_g}")
        print(f"Margen transmision A (min dist a 0/180): {min(muA):.0f} deg")
        print(f"Margen transmision B (min dist a 0/180): {min(muB):.0f} deg")
        print("-" * 66)
        print(" alpha   beta   gamma | muA1 muA2 muB1 muB2")
        for s in ok[::max(1, len(ok)//12)]:
            print(f" {s['alpha']:5.0f}  {s['beta']:6.1f} {s['gamma']:6.1f} |"
                  f" {s['muA1']:4.0f} {s['muA2']:4.0f} {s['muB1']:4.0f} "
                  f"{s['muB2']:4.0f}")
