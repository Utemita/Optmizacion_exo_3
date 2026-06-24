"""
tune_subactuado.py
==================
Busqueda de parametros para el mecanismo subactuado.
- beta (IFP) depende SOLO del acoplamiento A  -> se afina A primero.
- gamma (IFD) depende de A (via beta) y de B   -> se afina B con la mejor A.
Criterios: ensamblaje COMPLETO en toda la carrera, flexion MONOTONA (>0),
rango objetivo y angulos de transmision dentro de [~35,145] deg.
"""
import numpy as np
from itertools import product

fp, fm, fd = 49.0, 26.0, 24.0
ALPHA = np.arange(0, 70.0 + 1e-9, 2.0)


def _ang(v):
    return np.arctan2(v[1], v[0])


def _ci(c0, r0, c1, r1):
    c0 = np.asarray(c0, float); c1 = np.asarray(c1, float)
    d = c1 - c0; dist = np.hypot(*d)
    if dist > r0 + r1 or dist < abs(r0 - r1) or dist == 0:
        return None
    a = (r0**2 - r1**2 + dist**2) / (2 * dist); h2 = r0**2 - a**2
    if h2 < 0:
        return None
    h = np.sqrt(h2); pm = c0 + a * d / dist
    perp = np.array([-d[1], d[0]]) / dist
    return pm + h * perp, pm - h * perp


def eval_A(A_ba, A_ua, A_Nx, A_Ny, A_BR):
    Lda = np.hypot(A_ba, A_ua); phia = np.arctan2(A_ua, A_ba)
    Ma0 = np.array([fp + A_ba, A_ua]); N = np.array([A_Nx, A_Ny])
    LcA = np.hypot(*(Ma0 - N))
    betas = []; mus = []; prevMa = None; PIPs = []; Phi2s = []
    for al in ALPHA:
        a = np.deg2rad(al); Phi1 = -a
        PIP = fp * np.array([np.cos(Phi1), np.sin(Phi1)])
        s = _ci(PIP, Lda, N, LcA)
        if s is None:
            return None
        if prevMa is None:
            Ma = s[A_BR]
        else:
            Ma = s[0] if np.hypot(*(s[0]-prevMa)) <= np.hypot(*(s[1]-prevMa)) else s[1]
        prevMa = Ma
        Phi2 = _ang(Ma - PIP) - phia
        betas.append(np.degrees(-Phi2 - a))
        mu = np.degrees(np.arccos(np.clip(np.dot(
            (PIP-Ma)/np.hypot(*(PIP-Ma)), (N-Ma)/np.hypot(*(N-Ma))), -1, 1)))
        mus.append(mu); PIPs.append(PIP); Phi2s.append(Phi2)
    betas = np.array(betas); mus = np.array(mus)
    return betas, mus, LcA


def eval_B(A, B_along, B_up, B_bb, B_ub, B_BR):
    """A = (A_ba,A_ua,A_Nx,A_Ny,A_BR). Devuelve gammas, muB o None."""
    A_ba, A_ua, A_Nx, A_Ny, A_BR = A
    Lda = np.hypot(A_ba, A_ua); phia = np.arctan2(A_ua, A_ba)
    Ma0 = np.array([fp + A_ba, A_ua]); N = np.array([A_Nx, A_Ny])
    LcA = np.hypot(*(Ma0 - N))
    Ldb = np.hypot(B_bb, B_ub); phib = np.arctan2(B_ub, B_bb)
    Dc0 = np.array([fp + fm + B_bb, B_ub]); Pa0 = np.array([B_along, B_up])
    LcB = np.hypot(*(Dc0 - Pa0))
    gammas = []; mus = []; prevMa = None; prevDc = None
    for al in ALPHA:
        a = np.deg2rad(al); Phi1 = -a
        u1 = np.array([np.cos(Phi1), np.sin(Phi1)])
        n1 = np.array([-np.sin(Phi1), np.cos(Phi1)])
        PIP = fp * u1
        s = _ci(PIP, Lda, N, LcA)
        if s is None:
            return None
        Ma = s[A_BR] if prevMa is None else (
            s[0] if np.hypot(*(s[0]-prevMa)) <= np.hypot(*(s[1]-prevMa)) else s[1])
        prevMa = Ma
        Phi2 = _ang(Ma - PIP) - phia
        u2 = np.array([np.cos(Phi2), np.sin(Phi2)])
        DIP = PIP + fm * u2
        Pa = B_along * u1 + B_up * n1
        s2 = _ci(DIP, Ldb, Pa, LcB)
        if s2 is None:
            return None
        Dc = s2[B_BR] if prevDc is None else (
            s2[0] if np.hypot(*(s2[0]-prevDc)) <= np.hypot(*(s2[1]-prevDc)) else s2[1])
        prevDc = Dc
        Phi3 = _ang(Dc - DIP) - phib
        gammas.append(np.degrees(-Phi3 + Phi2))
        mu = np.degrees(np.arccos(np.clip(np.dot(
            (DIP-Dc)/np.hypot(*(DIP-Dc)), (Pa-Dc)/np.hypot(*(Pa-Dc))), -1, 1)))
        mus.append(mu)
    return np.array(gammas), np.array(mus), LcB


def feasible(vals, mus, lo, hi, mu_lo=35, mu_hi=145):
    """monotona creciente, sin extension, rango objetivo, transmision sana."""
    d = np.diff(vals)
    if np.any(d < -0.4):              # debe ser monotona creciente
        return False
    if vals[0] < -3:                  # parte de ~0
        return False
    if not (lo <= vals[-1] <= hi):    # rango final objetivo
        return False
    if np.any(mus < mu_lo) or np.any(mus > mu_hi):
        return False
    return True


def search_A():
    cands = []
    grid = product(
        [-12, -9, -6, -3, 0, 3],   # A_ba
        [8, 11, 14, 17, 20, 23],   # A_ua
        [-10, -4, 2, 8, 14, 20],   # A_Nx
        [12, 16, 20, 24, 28, 32],  # A_Ny
        [0, 1])                    # A_BR
    for A_ba, A_ua, A_Nx, A_Ny, A_BR in grid:
        r = eval_A(A_ba, A_ua, A_Nx, A_Ny, A_BR)
        if r is None:
            continue
        betas, mus, LcA = r
        # relajado: monotona flexion, sin extension, transmision en [25,155]
        if not feasible(betas, mus, 25, 95, mu_lo=25, mu_hi=155):
            continue
        worst = np.max(np.abs(mus - 90))
        cands.append((betas[-1], worst, (A_ba, A_ua, A_Nx, A_Ny, A_BR),
                      mus.min(), mus.max()))
    cands.sort(key=lambda c: (-c[0], c[1]))   # mayor beta, mejor transmision
    return cands


def search_B(A):
    cands = []
    grid = product(
        [48, 52, 56, 60, 64, 68],  # B_along
        [4, 8, 12, 16, 20],        # B_up
        [-14, -11, -8, -5, -2],    # B_bb
        [8, 11, 14, 17, 20],       # B_ub
        [0, 1])                    # B_BR
    for B_along, B_up, B_bb, B_ub, B_BR in grid:
        r = eval_B(A, B_along, B_up, B_bb, B_ub, B_BR)
        if r is None:
            continue
        gammas, mus, LcB = r
        if not feasible(gammas, mus, 20, 75, mu_lo=25, mu_hi=155):
            continue
        worst = np.max(np.abs(mus - 90))
        cands.append((gammas[-1], worst, (B_along, B_up, B_bb, B_ub, B_BR),
                      mus.min(), mus.max()))
    cands.sort(key=lambda c: (-c[0], c[1]))
    return cands


if __name__ == "__main__":
    print("Buscando acoplamiento A (MCF->IFP)...")
    cA = search_A()
    if not cA:
        print("  No se encontro A factible ni relajado.")
        raise SystemExit
    print(f"  {len(cA)} candidatos. Top-6 por beta_max:")
    for beta, worst, p, mn, mx in cA[:6]:
        print(f"    beta_max={beta:5.1f}  muA=[{mn:.0f},{mx:.0f}]  "
              f"|mu-90|max={worst:.0f}  params={p}")
    A = cA[0][2]
    print(f"  -> Usando A={A}")
    print("Buscando acoplamiento B (IFP->IFD)...")
    cB = search_B(A)
    if not cB:
        print("  No se encontro B factible ni relajado.")
        raise SystemExit
    print(f"  {len(cB)} candidatos. Top-6 por gamma_max:")
    for g, worst, p, mn, mx in cB[:6]:
        print(f"    gamma_max={g:5.1f}  muB=[{mn:.0f},{mx:.0f}]  "
              f"|mu-90|max={worst:.0f}  params={p}")
