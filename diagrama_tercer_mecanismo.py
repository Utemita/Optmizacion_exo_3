"""
Diagrama del mecanismo completo del exoesqueleto con tercer mecanismo de 4 barras.
Genera una imagen similar a diagrama.png pero incluyendo el tercer mecanismo
que proporciona movimiento variable a la falange distal (DIP).

Todos los mecanismos van montados SOBRE el dedo.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch

# =============================================================================
# PARAMETROS DEL MECANISMO (en mm)
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
Link9 = 25
Link10 = 35
c2 = 46.01
hsp = 17
dsp = 18
fp = 49
fm = 26
fd = 24
hsp3 = 12
dsp3 = 8
reng = 2
THETA1inicial = 109  # grados
THETA14B = 90  # grados

# Parametros derivados
r3 = Bancada1 / 2
c_hip = np.sqrt(hsp**2 + dsp**2)
rs2 = np.sqrt(hsp**2 + (fp - dsp)**2)
d3_frame = np.sqrt(hsp3**2 + dsp3**2)


# =============================================================================
# CINEMATICA PARA UNA POSICION REPRESENTATIVA
# =============================================================================
def compute_mechanism_position(THETA2_deg):
    """Calcula todas las posiciones del mecanismo para un angulo de entrada."""
    theta2 = np.deg2rad(THETA2_deg)
    THETA1_deg = THETA2_deg / reng + THETA1inicial
    theta1 = np.deg2rad(THETA1_deg)
    theta14B = np.deg2rad(THETA14B)

    # Primer mecanismo de 5 barras
    r4 = Link1
    r5 = Link2
    r2 = Link3
    r1 = Link4

    den = r4*np.cos(theta2) - r1*np.cos(theta1) + 2*r3
    e = (r1*np.sin(theta1) - r4*np.sin(theta2)) / den
    temp1 = (2*(r1*r3*np.cos(theta1) + r3*r4*np.cos(theta2))
             - r1**2 + r2**2 + r4**2 - r5**2)
    f = temp1 / (2*den)
    d_ = e**2 + 1
    g = 2*(e*f - e*r1*np.cos(theta1) + e*r3 - r1*np.sin(theta1))
    h = (f**2 - 2*f*(r1*np.cos(theta1) - r3)
         - 2*r1*r3*np.cos(theta1) + r1**2 + r3**2 - r2**2)
    disc = g**2 - 4*d_*h
    if disc < 0:
        return None
    pyP = (-g + np.sqrt(disc)) / (2*d_)
    pxP = e*pyP + f

    # Primer mecanismo de 4 barras
    a = Link4
    b = Link5
    c_val = c_hip
    d_val = Bancada2

    k1 = d_val*np.cos(theta14B) + a*np.cos(theta1)
    k2 = d_val*np.sin(theta14B) + a*np.sin(theta1)
    k3 = k1**2 + k2**2 + c_val**2 - b**2
    A1 = -k3 - 2*k1*c_val
    B1 = 4*k2*c_val
    C1 = 2*k1*c_val - k3
    disc2 = B1**2 - 4*A1*C1
    if disc2 < 0:
        return None
    tantheta42 = (-B1 - np.sqrt(disc2)) / (2*A1)
    theta4a = 2*np.arctan(tantheta42)
    THETA4a = np.rad2deg(theta4a)
    if THETA4a < 0:
        THETA4a += 360

    # Falange proximal
    THETAfp_val = THETA4a + np.rad2deg(np.arctan2(hsp, dsp))
    thetafp = np.deg2rad(THETAfp_val)
    pxIFP = fp*np.cos(thetafp) - d_val*np.cos(theta14B) - r3
    pyIFP = fp*np.sin(thetafp) - d_val*np.sin(theta14B)

    # Soportes
    pxS1 = c_val*np.cos(theta4a) - d_val*np.cos(theta14B) - r3
    pyS1 = c_val*np.sin(theta4a) - d_val*np.sin(theta14B)
    THETAps2 = THETAfp_val - np.rad2deg(np.arctan2(hsp, fp-dsp))
    thetaps2 = np.deg2rad(THETAps2)
    pxS2 = rs2*np.cos(thetaps2) - d_val*np.cos(theta14B) - r3
    pyS2 = rs2*np.sin(thetaps2) - d_val*np.sin(theta14B)

    pxM4 = a*np.cos(theta1) - r3
    pyM4 = a*np.sin(theta1)

    # Segundo mecanismo de 5 barras
    theta_roll = np.arctan2(pyM4 - pyS1, pxM4 - pxS1)
    theta1m2so = np.arctan2(pyS2 - pyS1, pxS2 - pxS1)
    if theta1m2so < 0:
        theta1m2so += 2*np.pi
    theta1m2 = theta1m2so - theta_roll
    theta2m2so = np.arctan2(pyP - pyM4, pxP - pxM4)
    if theta2m2so < 0:
        theta2m2so += 2*np.pi
    theta2m2 = theta2m2so - theta_roll

    r1m2 = fp - 2*dsp
    r2m2 = Link7
    r3m2 = Link5/2
    r4m2 = Link3
    r5m2 = Link6

    temp2 = r4m2*np.cos(theta2m2) - r1m2*np.cos(theta1m2) + 2*r3m2
    if abs(temp2) < 1e-6:
        return None
    em2 = (r1m2*np.sin(theta1m2) - r4m2*np.sin(theta2m2)) / temp2
    temp3 = (2*(r1m2*r3m2*np.cos(theta1m2) + r3m2*r4m2*np.cos(theta2m2))
             - r1m2**2 + r2m2**2 + r4m2**2 - r5m2**2)
    fm2 = temp3 / (2*temp2)
    dauxm2 = em2**2 + 1
    gm2 = 2*(em2*fm2 - em2*r1m2*np.cos(theta1m2) + em2*r3m2 - r1m2*np.sin(theta1m2))
    hm2 = (fm2**2 - 2*fm2*(r1m2*np.cos(theta1m2) - r3m2)
            - 2*r1m2*r3m2*np.cos(theta1m2) + r1m2**2 + r3m2**2 - r2m2**2)
    disc3 = gm2**2 - 4*dauxm2*hm2
    if disc3 < 0:
        return None
    pyP2_loc = (-gm2 + np.sqrt(disc3)) / (2*dauxm2)
    pxP2_loc = em2*pyP2_loc + fm2

    p2_mag = np.sqrt(pxP2_loc**2 + pyP2_loc**2)
    theta2p2 = np.arctan2(pyP2_loc, pxP2_loc)
    pxAUX = (pxS1 + pxM4) / 2
    pyAUX = (pyS1 + pyM4) / 2
    pxP2so = p2_mag*np.cos(theta2p2 + theta_roll) + pxAUX
    pyP2so = p2_mag*np.sin(theta2p2 + theta_roll) + pyAUX

    # Segundo mecanismo de 4 barras
    theta14B2 = np.arctan2(pyS2 - pyIFP, pxS2 - pxIFP)
    theta24B2 = np.arctan2(pyP2so - pyS2, pxP2so - pxS2)
    if theta24B2 < 0:
        theta24B2 += 2*np.pi

    a2 = Link7
    b2 = Link8
    d2 = c_hip

    k1m2 = d2*np.cos(theta14B2) + a2*np.cos(theta24B2)
    k2m2 = d2*np.sin(theta14B2) + a2*np.sin(theta24B2)
    k3m2 = k1m2**2 + k2m2**2 + c2**2 - b2**2
    A1m2 = -k3m2 - 2*k1m2*c2
    B1m2 = 4*k2m2*c2
    C1m2 = 2*k1m2*c2 - k3m2
    disc4 = B1m2**2 - 4*A1m2*C1m2
    if disc4 < 0:
        return None
    tantheta42m2 = (-B1m2 - np.sqrt(disc4)) / (2*A1m2)
    theta4am2 = 2*np.arctan(tantheta42m2)
    THETA4am2 = np.rad2deg(theta4am2)
    if THETA4am2 < 0:
        THETA4am2 += 360

    # Punto P3
    pxP3 = pxIFP + c2*np.cos(np.deg2rad(THETA4am2))
    pyP3 = pyIFP + c2*np.sin(np.deg2rad(THETA4am2))

    # Falange medial
    THETAfm_val = THETA4am2 + 51.39
    thetafm = np.deg2rad(THETAfm_val)
    pxIFD = fm*np.cos(thetafm) + pxIFP
    pyIFD = fm*np.sin(thetafm) + pyIFP

    # Soporte S3
    theta_s3_offset = np.arctan2(hsp3, dsp3)
    dist_s3 = np.sqrt(hsp3**2 + dsp3**2)
    theta_s3_abs = thetafm + np.pi - theta_s3_offset
    pxS3 = pxIFD + dist_s3*np.cos(theta_s3_abs)
    pyS3 = pyIFD + dist_s3*np.sin(theta_s3_abs)

    # Tercer mecanismo de 4 barras
    dx3 = pxP3 - pxIFD
    dy3 = pyP3 - pyIFD
    R3 = np.sqrt(dx3**2 + dy3**2)
    phi3 = np.arctan2(dy3, dx3)

    if R3 > (Link10 + Link9) or R3 < abs(Link10 - Link9):
        thetafd = thetafm + np.deg2rad(38.78)
    else:
        cos_arg = (R3**2 + Link10**2 - Link9**2) / (2*Link10*R3)
        if abs(cos_arg) > 1:
            thetafd = thetafm + np.deg2rad(38.78)
        else:
            delta = np.arccos(cos_arg)
            tfd_sol1 = phi3 + delta
            tfd_sol2 = phi3 - delta
            dir_up = thetafm + np.pi/2
            proj1 = Link10*np.cos(tfd_sol1 - dir_up)
            proj2 = Link10*np.cos(tfd_sol2 - dir_up)
            thetafd = tfd_sol1 if proj1 >= proj2 else tfd_sol2

    # Punto D3 (conexion Link10 en falange distal)
    D3x = pxIFD + Link10*np.cos(thetafd)
    D3y = pyIFD + Link10*np.sin(thetafd)

    # Punta de la falange distal
    pxPF = pxIFD + fd*np.cos(thetafd)
    pyPF = pyIFD + fd*np.sin(thetafd)

    # MCF position
    mcf_x = -r3
    mcf_y = -Bancada2

    return {
        'mcf': (mcf_x, mcf_y),
        'ifp': (pxIFP, pyIFP),
        'ifd': (pxIFD, pyIFD),
        'pf': (pxPF, pyPF),
        'P': (pxP, pyP),
        'P2': (pxP2so, pyP2so),
        'P3': (pxP3, pyP3),
        'S1': (pxS1, pyS1),
        'S2': (pxS2, pyS2),
        'S3': (pxS3, pyS3),
        'M4': (pxM4, pyM4),
        'D3': (D3x, D3y),
        'thetafp': thetafp,
        'thetafm': thetafm,
        'thetafd': thetafd,
        'theta1': theta1,
        'theta2': theta2,
    }


# =============================================================================
# GENERAR DIAGRAMA
# =============================================================================
def draw_dimension(ax, p1, p2, offset, label, fontsize=7, color='gray'):
    """Dibuja una linea de dimension con etiqueta."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = np.sqrt(dx**2 + dy**2)
    # Normal direction
    if length > 0:
        nx = -dy/length * offset
        ny = dx/length * offset
    else:
        nx, ny = 0, offset

    x1o, y1o = p1[0]+nx, p1[1]+ny
    x2o, y2o = p2[0]+nx, p2[1]+ny
    ax.plot([p1[0], x1o], [p1[1], y1o], '-', color=color, lw=0.5, alpha=0.6)
    ax.plot([p2[0], x2o], [p2[1], y2o], '-', color=color, lw=0.5, alpha=0.6)
    ax.annotate('', xy=(x2o, y2o), xytext=(x1o, y1o),
                arrowprops=dict(arrowstyle='<->', color=color, lw=0.8))
    mx, my = (x1o+x2o)/2, (y1o+y2o)/2
    ax.text(mx, my, label, fontsize=fontsize, ha='center', va='bottom',
            color=color, fontweight='bold')


# Compute mechanism at a representative position (THETA2 = 40 degrees)
pos = compute_mechanism_position(40)
if pos is None:
    # Try other angles
    for angle in [30, 50, 20, 60, 10]:
        pos = compute_mechanism_position(angle)
        if pos is not None:
            break

if pos is None:
    print("ERROR: No se pudo calcular una posicion valida del mecanismo")
    exit(1)

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(16, 10))

# Extract points
mcf = pos['mcf']
ifp = pos['ifp']
ifd = pos['ifd']
pf = pos['pf']
P = pos['P']
P2 = pos['P2']
P3 = pos['P3']
S1 = pos['S1']
S2 = pos['S2']
S3 = pos['S3']
M4 = pos['M4']
D3 = pos['D3']
origin = (0, 0)

# --- DIBUJAR FALANGES (en gris claro, como el dedo) ---
finger_width = 8  # mm de ancho del dedo (visual)

# Falange proximal
ax.plot([mcf[0], ifp[0]], [mcf[1], ifp[1]], '-', color='#DEB887',
        lw=12, alpha=0.3, solid_capstyle='round', zorder=0)
# Falange medial
ax.plot([ifp[0], ifd[0]], [ifp[1], ifd[1]], '-', color='#DEB887',
        lw=10, alpha=0.3, solid_capstyle='round', zorder=0)
# Falange distal
ax.plot([ifd[0], pf[0]], [ifd[1], pf[1]], '-', color='#DEB887',
        lw=8, alpha=0.3, solid_capstyle='round', zorder=0)

# --- PRIMER MECANISMO (5B + 4B) - Color AZUL ---
# Bancada (origen a r3 offset)
ax.plot([origin[0]-r3, origin[0]+r3], [origin[1], origin[1]], 'b-', lw=2.5, zorder=2)

# Manivela Link4 del primer 5B (de origen a M4)
theta1_val = pos['theta1']
ax.plot([origin[0]-r3, M4[0]], [origin[1], M4[1]], 'b-', lw=2, zorder=2)

# Eslabones del primer 5B
ax.plot([origin[0]-r3, P[0]], [origin[1], P[1]], 'b--', lw=1.5, zorder=2)
ax.plot([M4[0], P[0]], [M4[1], P[1]], 'b--', lw=1.5, zorder=2)

# Link1 (de origen+r3 a P)
ax.plot([origin[0]+r3, P[0]], [origin[1], P[1]], 'b-', lw=2, zorder=2)

# Manivela Link4 del 4B (de M4 al punto bancada del 4B)
theta14B_rad = np.deg2rad(THETA14B)
bancada_4b_x = origin[0] - r3 - Bancada2*np.cos(theta14B_rad)
bancada_4b_y = origin[1] - Bancada2*np.sin(theta14B_rad)
ax.plot([origin[0]-r3, bancada_4b_x], [origin[1], bancada_4b_y],
        'b-', lw=2.5, zorder=2, label='1er Mecanismo (5B+4B)')

# Link5 (S1 a S2 implicitamente via el 4B)
ax.plot([S1[0], S2[0]], [S1[1], S2[1]], 'b-', lw=1.5, zorder=2)

# --- SEGUNDO MECANISMO (5B + 4B) - Color ROJO ---
# Enlace del segundo mecanismo
ax.plot([S1[0], M4[0]], [S1[1], M4[1]], 'r-', lw=1.5, zorder=3)
ax.plot([S2[0], P2[0]], [S2[1], P2[1]], 'r-', lw=2, zorder=3)
ax.plot([M4[0], P2[0]], [M4[1], P2[1]], 'r--', lw=1.5, zorder=3)
ax.plot([S1[0], P2[0]], [S1[1], P2[1]], 'r--', lw=1.5, zorder=3,
        label='2do Mecanismo (5B+4B)')

# Link8 del segundo 4B (P2 a P3)
ax.plot([P2[0], P3[0]], [P2[1], P3[1]], 'r-', lw=2, zorder=3)

# --- TERCER MECANISMO (4B) - Color VERDE ---
# Link9: P3 a D3 (acoplador)
ax.plot([P3[0], D3[0]], [P3[1], D3[1]], 'g-', lw=2.5, zorder=4,
        label='3er Mecanismo (4B - DIP)')
# Link10: IFD a D3 (balancin)
ax.plot([ifd[0], D3[0]], [ifd[1], D3[1]], 'g-', lw=2.5, zorder=4)
# S3 connection
ax.plot([S3[0], P3[0]], [S3[1], P3[1]], 'g--', lw=1.5, zorder=4)
ax.plot([S3[0], ifd[0]], [S3[1], ifd[1]], 'g:', lw=1.5, zorder=4)

# --- PUNTOS ARTICULARES ---
joint_size = 60
ax.scatter(*mcf, s=joint_size, c='black', zorder=5, edgecolors='white', lw=1)
ax.scatter(*ifp, s=joint_size, c='blue', zorder=5, edgecolors='white', lw=1)
ax.scatter(*ifd, s=joint_size, c='red', zorder=5, edgecolors='white', lw=1)
ax.scatter(*pf, s=joint_size, c='green', zorder=5, edgecolors='white', lw=1)
ax.scatter(*origin, s=50, c='gray', zorder=5, marker='s')
ax.scatter(*P, s=40, c='blue', zorder=5, marker='^')
ax.scatter(*P2, s=40, c='red', zorder=5, marker='^')
ax.scatter(*P3, s=50, c='darkgreen', zorder=5, marker='D')
ax.scatter(*S1, s=40, c='blue', zorder=5, marker='s')
ax.scatter(*S2, s=40, c='purple', zorder=5, marker='s')
ax.scatter(*S3, s=50, c='green', zorder=5, marker='s')
ax.scatter(*M4, s=40, c='navy', zorder=5, marker='o')
ax.scatter(*D3, s=50, c='limegreen', zorder=5, marker='p')

# --- ETIQUETAS ---
offset_label = 2
ax.annotate('MCF', xy=mcf, xytext=(mcf[0]-5, mcf[1]-4), fontsize=8, fontweight='bold')
ax.annotate('IFP (PIP)', xy=ifp, xytext=(ifp[0]+2, ifp[1]-5), fontsize=8, fontweight='bold', color='blue')
ax.annotate('IFD (DIP)', xy=ifd, xytext=(ifd[0]+2, ifd[1]-5), fontsize=8, fontweight='bold', color='red')
ax.annotate('Punta', xy=pf, xytext=(pf[0]+2, pf[1]-3), fontsize=8, fontweight='bold', color='green')
ax.annotate('P', xy=P, xytext=(P[0]+2, P[1]+2), fontsize=7, color='blue')
ax.annotate('P2', xy=P2, xytext=(P2[0]+2, P2[1]+2), fontsize=7, color='red')
ax.annotate('P3', xy=P3, xytext=(P3[0]+2, P3[1]+2), fontsize=8, fontweight='bold', color='darkgreen')
ax.annotate('S1', xy=S1, xytext=(S1[0]-6, S1[1]+2), fontsize=7, color='blue')
ax.annotate('S2', xy=S2, xytext=(S2[0]+2, S2[1]+2), fontsize=7, color='purple')
ax.annotate('S3', xy=S3, xytext=(S3[0]+2, S3[1]+2), fontsize=8, fontweight='bold', color='green')
ax.annotate('M4', xy=M4, xytext=(M4[0]+2, M4[1]+2), fontsize=7, color='navy')
ax.annotate('D3', xy=D3, xytext=(D3[0]+2, D3[1]+2), fontsize=8, fontweight='bold', color='limegreen')
ax.annotate('Origen', xy=origin, xytext=(origin[0]+2, origin[1]+2), fontsize=6, color='gray')

# --- DIMENSIONES ---
draw_dimension(ax, P3, D3, 4, f'Link9={Link9}mm', fontsize=7, color='darkgreen')
draw_dimension(ax, ifd, D3, -4, f'Link10={Link10}mm', fontsize=7, color='green')

# --- TEXTO INFORMATIVO ---
info_text = (
    f"PARAMETROS DEL MECANISMO\n"
    f"{'='*35}\n"
    f"Bancada1 = {Bancada1} mm\n"
    f"Bancada2 = {Bancada2} mm\n"
    f"Link1 = {Link1} mm  |  Link2 = {Link2} mm\n"
    f"Link3 = {Link3} mm  |  Link4 = {Link4} mm\n"
    f"Link5 = {Link5} mm  |  Link6 = {Link6} mm\n"
    f"Link7 = {Link7} mm  |  Link8 = {Link8} mm\n"
    f"Link9 = {Link9} mm (acoplador 3er 4B)\n"
    f"Link10 = {Link10} mm (balancin 3er 4B)\n"
    f"c2 = {c2} mm (IFP a P3)\n"
    f"{'='*35}\n"
    f"hsp = {hsp} mm  |  dsp = {dsp} mm\n"
    f"hsp3 = {hsp3} mm  |  dsp3 = {dsp3} mm\n"
    f"fp = {fp} mm  |  fm = {fm} mm  |  fd = {fd} mm\n"
    f"Relacion engranaje = {reng}\n"
    f"{'='*35}\n"
    f"TERCER MECANISMO (4 BARRAS - DIP):\n"
    f"  Entrada: P3 (conducido por 2do mec.)\n"
    f"  Acoplador: Link9 = {Link9} mm\n"
    f"  Balancin: Link10 = {Link10} mm\n"
    f"  Soporte S3: hsp3={hsp3}, dsp3={dsp3} mm\n"
    f"  Articul. salida: IFD\n"
    f"  Todo SOBRE el dedo"
)
ax.text(0.02, 0.98, info_text, transform=ax.transAxes, fontsize=7,
        verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))

# --- CONFIGURACION DEL GRAFICO ---
ax.set_aspect('equal')
ax.grid(True, linestyle=':', alpha=0.4)
ax.legend(loc='lower right', fontsize=9, framealpha=0.9)
ax.set_title('Diagrama del Mecanismo Completo - Exoesqueleto con Tercer Mecanismo de 4 Barras (DIP)',
             fontsize=12, fontweight='bold')
ax.set_xlabel('Coordenada X (mm)', fontsize=10)
ax.set_ylabel('Coordenada Y (mm)', fontsize=10)

plt.tight_layout()
plt.savefig('/projects/sandbox/Optmizacion_exo_3/diagrama_tercer_mecanismo.png', dpi=150,
            bbox_inches='tight')
plt.close()

print("Diagrama generado exitosamente: diagrama_tercer_mecanismo.png")
print(f"Posicion calculada para THETA2 = 40 grados")
print(f"  IFP: ({ifp[0]:.2f}, {ifp[1]:.2f}) mm")
print(f"  IFD: ({ifd[0]:.2f}, {ifd[1]:.2f}) mm")
print(f"  P3:  ({P3[0]:.2f}, {P3[1]:.2f}) mm")
print(f"  S3:  ({S3[0]:.2f}, {S3[1]:.2f}) mm")
print(f"  D3:  ({D3[0]:.2f}, {D3[1]:.2f}) mm")
print(f"  Punta: ({pf[0]:.2f}, {pf[1]:.2f}) mm")

