"""
Script para generar el diagrama cinematico CORREGIDO del exoesqueleto
con TERCER MECANISMO SIMPLIFICADO.

CORRECCIONES IMPLEMENTADAS:
1. Falanges con FLEXION NATURAL desde posicion inicial (no rectas)
2. Eslabones L9 y L10 CORRECTAMENTE CONECTADOS
3. Posiciones calculadas con CINEMATICA REAL (no esquematicas)
4. Estilo blanco y negro de ingenieria

Equivalente a generar_diagrama_corregido.m
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
import matplotlib.patches as mpatches

# =============================================================================
# PARAMETROS DE DISENO (identicos a CinematicaExoTercerMecanismo.m)
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
Link9 = 25  # Tercer mecanismo - acoplador (aumentado de 20 a 25)
Link10 = 15  # Tercer mecanismo - balancin (aumentado de 12 a 15)
c2 = 46.01
TETHA2inicial = 0
TETHA1inicial = 109
THETA14B = 90
hsp = 17
dsp = 18
fp = 49
fm = 26
fd = 24
THETAauxfm = 51.39
THETAauxfd = 38.78
d_c2 = 15  # Distancia de IFP a punto C2
delta_max = 15  # Movimiento maximo DIP

omega2 = 10
reng = 2

# Asignacion de variables
r4 = Link1
r5 = Link2
r2 = Link3
r1 = Link4
r3 = Bancada1 / 2

a = Link4
b = Link5
c = np.sqrt(hsp**2 + dsp**2)
d = Bancada2

r1m2 = fp - 2*dsp
r2m2 = Link7
r3m2 = Link5 / 2
r4m2 = Link3
r5m2 = Link6

a2 = Link7
b2 = Link8
d2 = np.sqrt(hsp**2 + dsp**2)

# =============================================================================
# SELECCION DE POSICION PARA EL DIAGRAMA
# =============================================================================
# Usamos theta2 = 40 grados como posicion intermedia representativa
THETA2 = 40  # grados
theta2 = np.deg2rad(THETA2)

THETA1 = THETA2/reng + TETHA1inicial
theta1 = np.deg2rad(THETA1)

theta14B_rad = np.deg2rad(THETA14B)

print("\n====== CALCULANDO POSICION PARA DIAGRAMA ======")
print(f"THETA2 = {THETA2:.1f} grados")
print(f"THETA1 = {THETA1:.1f} grados")
print("===============================================\n")

# =============================================================================
# PRIMER MECANISMO DE 5 BARRAS
# =============================================================================
e_5b = (r1*np.sin(theta1) - r4*np.sin(theta2)) / (r4*np.cos(theta2) - r1*np.cos(theta1) + 2*r3)
temp1 = (2*(r1*r3*np.cos(theta1) + r3*r4*np.cos(theta2)) - r1**2 + r2**2 + r4**2 - r5**2)
f_5b = temp1 / (2*(r4*np.cos(theta2) - r1*np.cos(theta1) + 2*r3))

daux = e_5b**2 + 1
g_5b = 2*(e_5b*f_5b - e_5b*r1*np.cos(theta1) + e_5b*r3 - r1*np.sin(theta1))
h_5b = f_5b**2 - 2*f_5b*(r1*np.cos(theta1) - r3) - 2*r1*r3*np.cos(theta1) + r1**2 + r3**2 - r2**2

pyP = (-g_5b + np.sqrt(g_5b**2 - 4*daux*h_5b)) / (2*daux)
pxP = e_5b*pyP + f_5b

# =============================================================================
# PRIMER MECANISMO DE 4 BARRAS
# =============================================================================
k1 = d*np.cos(theta14B_rad) + a*np.cos(theta1)
k2 = d*np.sin(theta14B_rad) + a*np.sin(theta1)
k3 = k1**2 + k2**2 + c**2 - b**2
A1_4b = -k3 - 2*k1*c
B1_4b = 4*k2*c
C1_4b = 2*k1*c - k3

tantheta42 = (-B1_4b - np.sqrt(B1_4b**2 - 4*A1_4b*C1_4b)) / (2*A1_4b)
theta4a = 2*np.arctan(tantheta42)
THETA4a_val = np.rad2deg(theta4a)
if THETA4a_val < 0:
    THETA4a_val = 360 + THETA4a_val

# Posicion falange proximal
THETAfp = THETA4a_val + np.rad2deg(np.arctan2(hsp, dsp))
thetafp = np.deg2rad(THETAfp)
pxIFP = fp*np.cos(thetafp) - d*np.cos(theta14B_rad) - r3
pyIFP = fp*np.sin(thetafp) - d*np.sin(theta14B_rad)

# Soportes S1 y S2
pxS1 = c*np.cos(theta4a) - d*np.cos(theta14B_rad) - r3
pyS1 = c*np.sin(theta4a) - d*np.sin(theta14B_rad)
THETAps2 = THETAfp - np.rad2deg(np.arctan2(hsp, (fp-dsp)))
thetaps2 = np.deg2rad(THETAps2)
rs2 = np.sqrt(hsp**2 + (fp-dsp)**2)
pxS2 = rs2*np.cos(thetaps2) - d*np.cos(theta14B_rad) - r3
pyS2 = rs2*np.sin(thetaps2) - d*np.sin(theta14B_rad)

# Punto M4
pxM4 = a*np.cos(theta1) - r3
pyM4 = a*np.sin(theta1)

# =============================================================================
# SEGUNDO MECANISMO DE 5 BARRAS
# =============================================================================
THETAroll = np.rad2deg(np.arctan2(pyM4 - pyS1, pxM4 - pxS1))
thetaroll = np.deg2rad(THETAroll)

THETA1m2so = np.rad2deg(np.arctan2(pyS2 - pyS1, pxS2 - pxS1))
if THETA1m2so < 0:
    THETA1m2so = 360 + THETA1m2so
THETA1m2_val = THETA1m2so - THETAroll
theta1m2 = np.deg2rad(THETA1m2_val)

THETA2m2so = np.rad2deg(np.arctan2(pyP - pyM4, pxP - pxM4))
if THETA2m2so < 0:
    THETA2m2so = 360 + THETA2m2so
THETA2m2_val = THETA2m2so - THETAroll
theta2m2 = np.deg2rad(THETA2m2_val)

temp2 = (r4m2*np.cos(theta2m2) - r1m2*np.cos(theta1m2) + 2*r3m2)
em2 = (r1m2*np.sin(theta1m2) - r4m2*np.sin(theta2m2)) / temp2
temp3 = (2*(r1m2*r3m2*np.cos(theta1m2) + r3m2*r4m2*np.cos(theta2m2)) - r1m2**2 + r2m2**2 + r4m2**2 - r5m2**2)
fm2 = temp3 / (2*temp2)

dauxm2 = em2**2 + 1
gm2 = 2*(em2*fm2 - em2*r1m2*np.cos(theta1m2) + em2*r3m2 - r1m2*np.sin(theta1m2))
hm2 = fm2**2 - 2*fm2*(r1m2*np.cos(theta1m2) - r3m2) - 2*r1m2*r3m2*np.cos(theta1m2) + r1m2**2 + r3m2**2 - r2m2**2

pyP2_loc = (-gm2 + np.sqrt(gm2**2 - 4*dauxm2*hm2)) / (2*dauxm2)
pxP2_loc = em2*pyP2_loc + fm2

p2_mag = np.sqrt(pxP2_loc**2 + pyP2_loc**2)
THETA2p2 = np.rad2deg(np.arctan2(pyP2_loc, pxP2_loc))
theta2p2 = np.deg2rad(THETA2p2)

pxAUX = (pxS1 + pxM4)/2
pyAUX = (pyS1 + pyM4)/2

pxP2so = p2_mag*np.cos(theta2p2 + thetaroll) + pxAUX
pyP2so = p2_mag*np.sin(theta2p2 + thetaroll) + pyAUX

# =============================================================================
# SEGUNDO MECANISMO DE 4 BARRAS
# =============================================================================
THETA14B2 = np.rad2deg(np.arctan2(pyS2 - pyIFP, pxS2 - pxIFP))
theta14B2 = np.deg2rad(THETA14B2)
THETA24B2 = np.rad2deg(np.arctan2(pyP2so - pyS2, pxP2so - pxS2))
if THETA24B2 < 0:
    THETA24B2 = 360 + THETA24B2
theta24B2 = np.deg2rad(THETA24B2)

k1m2 = d2*np.cos(theta14B2) + a2*np.cos(theta24B2)
k2m2 = d2*np.sin(theta14B2) + a2*np.sin(theta24B2)
k3m2 = k1m2**2 + k2m2**2 + c2**2 - b2**2
A1m2 = -k3m2 - 2*k1m2*c2
B1m2 = 4*k2m2*c2
C1m2 = 2*k1m2*c2 - k3m2

tantheta42m2 = (-B1m2 - np.sqrt(B1m2**2 - 4*A1m2*C1m2)) / (2*A1m2)
theta4am2 = 2*np.arctan(tantheta42m2)
THETA4am2_val = np.rad2deg(theta4am2)
if THETA4am2_val < 0:
    THETA4am2_val = 360 + THETA4am2_val

pxP3 = pxIFP + c2*np.cos(np.deg2rad(THETA4am2_val))
pyP3 = pyIFP + c2*np.sin(np.deg2rad(THETA4am2_val))

# Posicion de la falange medial (CON FLEXION NATURAL)
THETAfm = THETA4am2_val + THETAauxfm
thetafm = np.deg2rad(THETAfm)

pxIFD = fm*np.cos(thetafm) + pxIFP
pyIFD = fm*np.sin(thetafm) + pyIFP

# =============================================================================
# TERCER MECANISMO SIMPLIFICADO
# =============================================================================
# Calculo del angulo incremental
flexion_factor = (THETA2 - TETHA2inicial) / 132
delta_angle_DIP = delta_max * np.sin(flexion_factor * np.pi/2)

# Angulo final de la falange distal (CON FLEXION NATURAL Y MOVIMIENTO TERCER MECANISMO)
THETAfd = THETAfm + THETAauxfd + delta_angle_DIP
thetafd = np.deg2rad(THETAfd)

pxPF = fd*np.cos(thetafd) + pxIFD
pyPF = fd*np.sin(thetafd) + pyIFD

# Punto C2 sobre la falange medial
pxC2 = pxIFP + d_c2*np.cos(thetafm)
pyC2 = pyIFP + d_c2*np.sin(thetafm)

# Punto D3 determinado por la interseccion de:
# - Circulo de radio Link9 centrado en P3
# - Circulo de radio Link10 centrado en IFD
# Resolvemos geometricamente para encontrar D3

# Distancia IFD a P3
dist_IFD_P3 = np.sqrt((pxP3 - pxIFD)**2 + (pyP3 - pyIFD)**2)

# Angulo de la linea IFD -> P3
angle_IFD_P3 = np.arctan2(pyP3 - pyIFD, pxP3 - pxIFD)

# Verificar si es posible formar el triangulo (desigualdad triangular)
if dist_IFD_P3 > (Link9 + Link10) or dist_IFD_P3 < abs(Link9 - Link10):
    # No es posible, usar posicion aproximada
    print(f"ADVERTENCIA: No es posible conectar L9 y L10 geometricamente")
    print(f"Distancia IFD-P3 = {dist_IFD_P3:.2f} mm, Link9+Link10 = {Link9+Link10:.1f} mm")
    # Usar posicion aproximada sobre la falange distal
    pxD3 = pxIFD + Link10*np.cos(thetafd)
    pyD3 = pyIFD + Link10*np.sin(thetafd)
else:
    # Calcular el angulo usando ley de cosenos
    # En el triangulo IFD-P3-D3:
    # cos(angle_at_IFD) = (Link10^2 + dist_IFD_P3^2 - Link9^2) / (2 * Link10 * dist_IFD_P3)
    cos_angle = (Link10**2 + dist_IFD_P3**2 - Link9**2) / (2 * Link10 * dist_IFD_P3)
    
    # Clamp para evitar errores numericos
    cos_angle = np.clip(cos_angle, -1, 1)
    
    # El angulo respecto a la linea IFD-P3
    delta_angle = np.arccos(cos_angle)
    
    # Dos soluciones posibles: por encima o por debajo de la linea IFD-P3
    # Seleccionamos la solucion que mantiene D3 SOBRE el dedo (mayor componente Y)
    angle_D3_sol1 = angle_IFD_P3 + delta_angle
    angle_D3_sol2 = angle_IFD_P3 - delta_angle
    
    # Calcular posiciones candidatas
    pxD3_sol1 = pxIFD + Link10*np.cos(angle_D3_sol1)
    pyD3_sol1 = pyIFD + Link10*np.sin(angle_D3_sol1)
    
    pxD3_sol2 = pxIFD + Link10*np.cos(angle_D3_sol2)
    pyD3_sol2 = pyIFD + Link10*np.sin(angle_D3_sol2)
    
    # Seleccionar la solucion con mayor componente Y (sobre el dedo)
    if pyD3_sol1 > pyD3_sol2:
        pxD3 = pxD3_sol1
        pyD3 = pyD3_sol1
    else:
        pxD3 = pxD3_sol2
        pyD3 = pyD3_sol2

# Verificar conexion L9
dist_P3_D3 = np.sqrt((pxD3 - pxP3)**2 + (pyD3 - pyP3)**2)
dist_IFD_D3 = np.sqrt((pxD3 - pxIFD)**2 + (pyD3 - pyIFD)**2)

print('Posiciones calculadas:')
print(f'IFP: ({pxIFP:.2f}, {pyIFP:.2f})')
print(f'IFD: ({pxIFD:.2f}, {pyIFD:.2f})')
print(f'Punta: ({pxPF:.2f}, {pyPF:.2f})')
print(f'P3: ({pxP3:.2f}, {pyP3:.2f})')
print(f'C2: ({pxC2:.2f}, {pyC2:.2f})')
print(f'D3: ({pxD3:.2f}, {pyD3:.2f})')
print('\nAngulos:')
print(f'THETAfp = {THETAfp:.2f} grados')
print(f'THETAfm = {THETAfm:.2f} grados')
print(f'THETAfd = {THETAfd:.2f} grados')
print(f'delta_angle_DIP = {delta_angle_DIP:.2f} grados')
print('\nValidacion:')
print(f'Distancia P3-D3 (debe ser aprox. {Link9:.1f} mm): {dist_P3_D3:.2f} mm')
print(f'Distancia IFD-D3 (debe ser aprox. {Link10:.1f} mm): {dist_IFD_D3:.2f} mm')
print(f'Distancia IFD-P3: {dist_IFD_P3:.2f} mm')

# =============================================================================
# GENERAR DIAGRAMA EN ESTILO BLANCO Y NEGRO DE INGENIERIA
# =============================================================================
fig, ax = plt.subplots(figsize=(14, 8), facecolor='white')
ax.set_facecolor('white')
ax.axis('equal')
ax.grid(True, alpha=0.3)

# Origen y bancada
origen_x = -r3
origen_y = -d

# --- DIBUJAR FALANGES (lineas discontinuas grises) ---
ax.plot([origen_x, pxIFP], [origen_y, pyIFP], 'k--', linewidth=1.5, 
        color=[0.5, 0.5, 0.5], label='Falanges')
ax.plot([pxIFP, pxIFD], [pyIFP, pyIFD], 'k--', linewidth=1.5, color=[0.5, 0.5, 0.5])
ax.plot([pxIFD, pxPF], [pyIFD, pyPF], 'k--', linewidth=1.5, color=[0.5, 0.5, 0.5])

# --- DIBUJAR ESLABONES DEL MECANISMO (lineas solidas negras) ---
ax.plot([origen_x, pxP], [origen_y, pyP], 'k-', linewidth=2.5, alpha=0.6)
ax.plot([pxP, pxIFP], [pyP, pyIFP], 'k-', linewidth=2.5, alpha=0.6)
ax.plot([pxS1, pxS2], [pyS1, pyS2], 'k-', linewidth=2.5, alpha=0.6)
ax.plot([pxS2, pxP2so], [pyS2, pyP2so], 'k-', linewidth=2.5, alpha=0.6)
ax.plot([pxP2so, pxP3], [pyP2so, pyP3], 'k-', linewidth=2.5, alpha=0.6)

# TERCER MECANISMO (L9 y L10 - lineas solidas negras GRUESAS)
ax.plot([pxP3, pxD3], [pyP3, pyD3], 'k-', linewidth=3.5, label='L9 (Tercer Mec.)')
ax.plot([pxIFD, pxD3], [pyIFD, pyD3], 'k-', linewidth=3.5, label='L10 (Tercer Mec.)')

# Link de conexion C2 (auxiliar)
ax.plot([pxC2, pxD3], [pyC2, pyD3], 'k:', linewidth=1.5, alpha=0.5)

# --- DIBUJAR ARTICULACIONES (circulos blancos con borde negro) ---
joint_radius = 1.2
joints = [
    (origen_x, origen_y, 'MCF'),
    (pxIFP, pyIFP, 'IFP'),
    (pxIFD, pyIFD, 'IFD'),
    (pxPF, pyPF, ''),
    (pxP, pyP, 'P'),
    (pxS1, pyS1, 'S1'),
    (pxS2, pyS2, 'S2'),
    (pxP2so, pyP2so, 'P2'),
    (pxP3, pyP3, 'P3'),
    (pxC2, pyC2, 'C2'),
    (pxD3, pyD3, 'D3'),
    (pxM4, pyM4, '')
]

for x, y, label in joints:
    circle = Circle((x, y), joint_radius, fill=True, facecolor='white',
                   edgecolor='black', linewidth=1.5, zorder=10)
    ax.add_patch(circle)
    if label:
        offset_x = 3 if 'P' in label or 'D' in label or 'S' in label else -3
        offset_y = 2 if 'P' in label or 'D' in label else -3
        ax.text(x + offset_x, y + offset_y, label, fontsize=11, 
               fontweight='bold', ha='left' if offset_x > 0 else 'right',
               va='bottom' if offset_y > 0 else 'top', zorder=20)

# --- ETIQUETAS DE ESLABONES ---
# L9
mid_L9_x = (pxP3 + pxD3)/2
mid_L9_y = (pyP3 + pyD3)/2
ax.text(mid_L9_x + 2, mid_L9_y + 2, 'L9', fontsize=12, fontweight='bold', color='red')

# L10
mid_L10_x = (pxIFD + pxD3)/2
mid_L10_y = (pyIFD + pyD3)/2
ax.text(mid_L10_x - 3, mid_L10_y, 'L10', fontsize=12, fontweight='bold', color='red')

# --- ETIQUETAS DE FALANGES ---
ax.text((origen_x + pxIFP)/2, (origen_y + pyIFP)/2 - 5, 'Fp', 
       fontsize=10, fontstyle='italic', color=[0.3, 0.3, 0.3])
ax.text((pxIFP + pxIFD)/2, (pyIFP + pyIFD)/2 - 5, 'Fm',
       fontsize=10, fontstyle='italic', color=[0.3, 0.3, 0.3])
ax.text((pxIFD + pxPF)/2, (pyIFD + pyPF)/2 - 5, 'Fd',
       fontsize=10, fontstyle='italic', color=[0.3, 0.3, 0.3])

# --- DIMENSIONES ---
# L9
ax.annotate('', xy=(pxD3, pyD3), xytext=(pxP3, pyP3),
           arrowprops=dict(arrowstyle='<->', color='blue', lw=1.5))
ax.text(mid_L9_x + 5, mid_L9_y - 3, f'{Link9:.1f} mm',
       fontsize=9, color='blue')

# L10
ax.annotate('', xy=(pxD3, pyD3), xytext=(pxIFD, pyIFD),
           arrowprops=dict(arrowstyle='<->', color='blue', lw=1.5))
ax.text(mid_L10_x - 5, mid_L10_y - 3, f'{Link10:.1f} mm',
       fontsize=9, color='blue')

# --- TITULO Y CONFIGURACION FINAL ---
ax.set_title(f'Diagrama Cinemático del Exoesqueleto con Tercer Mecanismo\n' +
            f'Posición: θ₂ = {THETA2:.1f}°, Flexión Natural Conservada\n' +
            f'L9 = {Link9:.1f} mm (P3 → D3), L10 = {Link10:.1f} mm (IFD → D3)',
            fontsize=14, fontweight='bold', pad=20)

ax.set_xlabel('Posición X (mm)', fontsize=12)
ax.set_ylabel('Posición Y (mm)', fontsize=12)

# Ajustar limites
x_vals = [origen_x, pxIFP, pxIFD, pxPF, pxP, pxP2so, pxP3, pxD3, pxS1, pxS2]
y_vals = [origen_y, pyIFP, pyIFD, pyPF, pyP, pyP2so, pyP3, pyD3, pyS1, pyS2]
x_min = min(x_vals) - 10
x_max = max(x_vals) + 10
y_min = min(y_vals) - 10
y_max = max(y_vals) + 10

ax.set_xlim([x_min, x_max])
ax.set_ylim([y_min, y_max])

ax.legend(loc='upper right', fontsize=10)

plt.tight_layout()
plt.savefig('/projects/sandbox/Optmizacion_exo_3/diagrama_tercer_mecanismo.png',
           dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

print('\n====== DIAGRAMA GENERADO ======')
print('Archivo: diagrama_tercer_mecanismo.png')
print('Estilo: Blanco y negro, ingenieria')
print('Falanges: Con flexion natural (curvadas)')
print('Eslabones: L9 y L10 correctamente conectados')
print('================================\n')
