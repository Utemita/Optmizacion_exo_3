"""
Diagrama esquematico/cinematico del mecanismo completo del exoesqueleto
con tercer mecanismo de 4 barras para la articulacion IFD (DIP).

Este diagrama sigue EXACTAMENTE el estilo del diagrama original (diagrama.png):
- Diagrama en blanco y negro estilo ingenieria
- Dedo horizontal en la parte inferior (de derecha a izquierda)
- Mecanismos dibujados SOBRE el dedo
- Links como lineas solidas entre circulos de articulacion
- Falanges como lineas discontinuas
- Articulaciones como circulos blancos con borde negro
- Soportes con marcas de achurado (hatching)
- Etiquetas en italica para links (L1, L2, etc.)
- Angulos etiquetados con arcos
- Dimensiones etiquetadas

La DIFERENCIA CLAVE respecto al original: L9 y L10 ahora estan correctamente
conectados formando el tercer mecanismo de 4 barras que impulsa la falange
distal, mostrando como P3 se conecta a traves de L9 al punto D3, y L10
conecta D3 a IFD.
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Arc, FancyArrowPatch

# =============================================================================
# PARAMETROS DEL MECANISMO (en mm)
# =============================================================================
Bancada1 = 18  # B1
Bancada2 = 20  # B2 = d
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
fp = 49   # falange proximal
fm = 26   # falange medial
fd = 24   # falange distal
hsp3 = 12  # altura soporte S3
dsp3 = 8   # distancia soporte S3 desde IFD
r3 = Bancada1 / 2


# =============================================================================
# FUNCIONES AUXILIARES DE DIBUJO
# =============================================================================
def draw_joint(ax, pos, radius=1.2, zorder=10):
    """Dibuja una articulacion como un circulo blanco con borde negro."""
    circle = plt.Circle(pos, radius, fill=True, facecolor='white',
                        edgecolor='black', linewidth=1.5, zorder=zorder)
    ax.add_patch(circle)


def draw_ground(ax, pos, width=6, height=4, angle=0):
    """Dibuja un soporte fijo con marcas de achurado (hatching)."""
    # Dibuja linea horizontal
    hw = width / 2
    x, y = pos
    # Linea de base
    ax.plot([x - hw, x + hw], [y, y], 'k-', linewidth=1.5, zorder=5)
    # Lineas de achurado (diagonal)
    n_lines = 5
    for i in range(n_lines):
        xi = x - hw + i * width / (n_lines - 1)
        ax.plot([xi, xi - 2], [y, y - 3], 'k-', linewidth=0.8, zorder=5)


def draw_link(ax, p1, p2, linewidth=1.8, linestyle='-', zorder=5):
    """Dibuja un link (linea solida) entre dos puntos."""
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'k' + linestyle,
            linewidth=linewidth, zorder=zorder)


def draw_phalanx(ax, p1, p2, linewidth=1.8, zorder=3):
    """Dibuja una falange como linea discontinua."""
    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'k--',
            linewidth=linewidth, zorder=zorder)


def label_link(ax, p1, p2, text, offset=(0, 2), fontsize=10):
    """Etiqueta un link con texto en italica."""
    mx = (p1[0] + p2[0]) / 2 + offset[0]
    my = (p1[1] + p2[1]) / 2 + offset[1]
    ax.text(mx, my, text, fontsize=fontsize, fontstyle='italic',
            ha='center', va='bottom', zorder=20)


def label_dimension(ax, p1, p2, text, offset=5, fontsize=8, side='above'):
    """Etiqueta una dimension."""
    mx = (p1[0] + p2[0]) / 2
    my = (p1[1] + p2[1]) / 2
    if side == 'above':
        my += offset
    elif side == 'below':
        my -= offset
    elif side == 'left':
        mx -= offset
    elif side == 'right':
        mx += offset
    ax.text(mx, my, text, fontsize=fontsize, fontstyle='italic',
            ha='center', va='center', zorder=20)


def draw_angle_arc(ax, center, radius, angle1, angle2, label='',
                   label_offset=3, fontsize=8):
    """Dibuja un arco de angulo con etiqueta."""
    arc = Arc(center, 2*radius, 2*radius, angle=0,
              theta1=angle1, theta2=angle2,
              color='black', linewidth=0.8, zorder=6)
    ax.add_patch(arc)
    # Etiqueta en el punto medio del arco
    mid_angle = np.deg2rad((angle1 + angle2) / 2)
    lx = center[0] + (radius + label_offset) * np.cos(mid_angle)
    ly = center[1] + (radius + label_offset) * np.sin(mid_angle)
    if label:
        ax.text(lx, ly, label, fontsize=fontsize, fontstyle='italic',
                ha='center', va='center', zorder=20)


# =============================================================================
# POSICIONES ESQUEMATICAS (NO CALCULADAS - TOPOLOGIA PURA)
# =============================================================================
# El diagrama es ESQUEMATICO, no una posicion calculada del mecanismo.
# Las posiciones se eligen para mostrar claramente la topologia.

# Dedo horizontal en la parte inferior, de DERECHA a IZQUIERDA
# MCF (metacarpofalangica) -> IFP (interfalangica proximal) ->
# IFD (interfalangica distal) -> Punta

# Posiciones del dedo (horizontal)
MCF = np.array([140, 0])
IFP = MCF + np.array([-fp, 0])   # IFP esta a la izquierda de MCF
IFD = IFP + np.array([-fm, 0])   # IFD esta a la izquierda de IFP
TIP = IFD + np.array([-fd, 0])   # Punta esta a la izquierda de IFD

# --- PRIMER MECANISMO (5 barras + 4 barras) ---
# Bancada/Soporte S1 (sobre MCF, desplazado)
# S1 esta arriba del dedo, cerca de MCF
S1 = MCF + np.array([0, hsp])

# Punto de la bancada (origen del mecanismo) - a la derecha
# La bancada esta a la derecha, encima de MCF
BANCADA_R = S1 + np.array([r3, 0])   # extremo derecho de bancada
BANCADA_L = S1 + np.array([-r3, 0])  # extremo izquierdo de bancada

# Soporte S2 (sobre la falange proximal, desplazado)
S2 = MCF + np.array([-dsp, hsp])

# Punto P (vertice del 5-barras) - arriba y a la izquierda
P = S1 + np.array([-15, 30])

# Primer mecanismo de 4 barras
# M4 = punto de manivela del primer 4-barras
M4 = BANCADA_L + np.array([-3, -Bancada2])

# --- SEGUNDO MECANISMO (5 barras + 4 barras) ---
# Punto P2 (vertice del segundo 5-barras) - arriba de S1/S2
P2 = np.array([(S1[0] + S2[0])/2 - 20, S1[1] + 30])

# Punto P3 (salida del segundo 4-barras) - sobre IFP, desplazado
# P3 se calcula usando c2 desde IFP
P3 = IFP + np.array([-10, c2 * 0.7])  # posicion esquematica

# --- TERCER MECANISMO (4 barras para DIP) ---
# Soporte S3 (sobre la falange medial, cerca de IFD)
S3 = IFD + np.array([dsp3, hsp3])

# D3 (punto de conexion de Link10 en la falange distal)
# D3 esta arriba de IFD, conectado por Link10
D3 = IFD + np.array([-5, Link10 * 0.6])


# =============================================================================
# GENERAR DIAGRAMA
# =============================================================================
fig, ax = plt.subplots(1, 1, figsize=(18, 12))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# --- DIBUJAR FALANGES (lineas discontinuas) ---
draw_phalanx(ax, MCF, IFP)
draw_phalanx(ax, IFP, IFD)
draw_phalanx(ax, IFD, TIP)

# Etiquetas de falanges
label_dimension(ax, MCF, IFP, r'$F_p$', offset=-6, fontsize=10, side='below')
label_dimension(ax, IFP, IFD, r'$F_m$', offset=-6, fontsize=10, side='below')
label_dimension(ax, IFD, TIP, r'$F_d$', offset=-6, fontsize=10, side='below')

# --- PRIMER MECANISMO (5B + 4B) ---
# Bancada
draw_link(ax, BANCADA_L, BANCADA_R, linewidth=2.5)
draw_ground(ax, BANCADA_R + np.array([0, 0]))

# Links del primer 5-barras
# L1: de BANCADA_R a P
draw_link(ax, BANCADA_R, P)
label_link(ax, BANCADA_R, P, r'$L_1$', offset=(3, 1))

# L2: de P a algun punto (acoplador largo)
# En el diagrama original, L2 es el acoplador mas largo
P_ext = P + np.array([-25, -10])  # punto extension del acoplador
draw_link(ax, P, P_ext)
label_link(ax, P, P_ext, r'$L_2$', offset=(0, 3))

# L3: manivela corta
draw_link(ax, BANCADA_L, P)
label_link(ax, BANCADA_L, P, r'$L_3$', offset=(-4, 0))

# L4: de BANCADA_L a M4 (primer 4-barras input)
draw_link(ax, BANCADA_L, M4)
label_link(ax, BANCADA_L, M4, r'$L_4$', offset=(3, 0))

# L5: del primer 4-barras (de S1 a S2)
draw_link(ax, S1, S2)
label_link(ax, S1, S2, r'$L_5$', offset=(0, 2))

# --- SEGUNDO MECANISMO (5B + 4B) ---
# Links del segundo 5-barras
# L6: acoplador largo del segundo mecanismo
draw_link(ax, S2, P2)
label_link(ax, S2, P2, r'$L_6$', offset=(3, 0))

# L7: del segundo mecanismo
draw_link(ax, P2, P3)
label_link(ax, P2, P3, r'$L_7$', offset=(-4, 0))

# L8: del segundo 4-barras (P2 a P3)
# Realmente L8 conecta partes del segundo mecanismo
draw_link(ax, S1, P2)
label_link(ax, S1, P2, r'$L_8$', offset=(-3, 2))

# --- TERCER MECANISMO (4 barras para DIP) ---
# L9: acoplador del tercer mecanismo (P3 a D3)
draw_link(ax, P3, D3, linewidth=2.0)
label_link(ax, P3, D3, r'$L_9$', offset=(3, 0))

# L10: balancin del tercer mecanismo (IFD a D3)
draw_link(ax, IFD, D3, linewidth=2.0)
label_link(ax, IFD, D3, r'$L_{10}$', offset=(3, 0))

# Conexion de marco del tercer mecanismo (S3 como soporte)
draw_link(ax, S3, IFD, linewidth=1.0, linestyle='-')

# --- ARTICULACIONES (circulos blancos con borde negro) ---
draw_joint(ax, MCF)
draw_joint(ax, IFP)
draw_joint(ax, IFD)
draw_joint(ax, TIP)
draw_joint(ax, S1)
draw_joint(ax, S2)
draw_joint(ax, BANCADA_L)
draw_joint(ax, BANCADA_R)
draw_joint(ax, M4)
draw_joint(ax, P)
draw_joint(ax, P2)
draw_joint(ax, P3)
draw_joint(ax, S3)
draw_joint(ax, D3)

# --- SOPORTES FIJOS (achurado) ---
draw_ground(ax, MCF + np.array([0, -2]))
draw_ground(ax, IFP + np.array([0, -2]))
draw_ground(ax, IFD + np.array([0, -2]))

# --- ETIQUETAS DE PUNTOS ---
ax.text(MCF[0] + 2, MCF[1] - 8, 'MCF', fontsize=9, ha='center',
        va='top', zorder=20)
ax.text(IFP[0], IFP[1] - 8, 'IFP', fontsize=9, ha='center',
        va='top', zorder=20)
ax.text(IFD[0], IFD[1] - 8, 'IFD', fontsize=9, ha='center',
        va='top', zorder=20)
ax.text(S1[0] + 3, S1[1] + 2, r'$S_1$', fontsize=9, ha='left',
        va='bottom', zorder=20)
ax.text(S2[0] - 3, S2[1] + 2, r'$S_2$', fontsize=9, ha='right',
        va='bottom', zorder=20)
ax.text(S3[0] + 2, S3[1] + 2, r'$S_3$', fontsize=9, ha='left',
        va='bottom', zorder=20)
ax.text(P[0] + 2, P[1] + 2, r'$P$', fontsize=9, ha='left',
        va='bottom', zorder=20)
ax.text(P2[0] - 2, P2[1] + 2, r'$P_2$', fontsize=9, ha='right',
        va='bottom', zorder=20)
ax.text(P3[0] - 2, P3[1] + 2, r'$P_3$', fontsize=9, ha='right',
        va='bottom', zorder=20)
ax.text(D3[0] + 2, D3[1] + 2, r'$D_3$', fontsize=9, ha='left',
        va='bottom', zorder=20)
ax.text(M4[0] + 2, M4[1] - 2, r'$M_4$', fontsize=9, ha='left',
        va='top', zorder=20)
ax.text(BANCADA_R[0] + 3, BANCADA_R[1], 'Bancada', fontsize=8,
        ha='left', va='center', zorder=20)

# --- ETIQUETAS DE DIMENSIONES ---
# hsp
ax.annotate('', xy=(MCF[0] + 8, S1[1]), xytext=(MCF[0] + 8, MCF[1]),
            arrowprops=dict(arrowstyle='<->', color='black', lw=0.8))
ax.text(MCF[0] + 12, (MCF[1] + S1[1])/2, r'$h_{sp}$', fontsize=8,
        fontstyle='italic', ha='left', va='center')

# dsp
ax.annotate('', xy=(S2[0], MCF[1] - 12), xytext=(MCF[0], MCF[1] - 12),
            arrowprops=dict(arrowstyle='<->', color='black', lw=0.8))
ax.text((S2[0] + MCF[0])/2, MCF[1] - 16, r'$d_{sp}$', fontsize=8,
        fontstyle='italic', ha='center', va='top')

# B1
ax.annotate('', xy=(BANCADA_L[0], BANCADA_L[1] + 5),
            xytext=(BANCADA_R[0], BANCADA_R[1] + 5),
            arrowprops=dict(arrowstyle='<->', color='black', lw=0.8))
ax.text((BANCADA_L[0] + BANCADA_R[0])/2, BANCADA_R[1] + 8,
        r'$B_1$', fontsize=8, fontstyle='italic',
        ha='center', va='bottom')

# B2 = d
ax.annotate('', xy=(BANCADA_L[0] + 5, BANCADA_L[1]),
            xytext=(M4[0] + 5, M4[1]),
            arrowprops=dict(arrowstyle='<->', color='black', lw=0.8))
ax.text(BANCADA_L[0] + 9, (BANCADA_L[1] + M4[1])/2,
        r'$B_2=d$', fontsize=8, fontstyle='italic',
        ha='left', va='center')

# c2
ax.annotate('', xy=(IFP[0] - 5, IFP[1]), xytext=(P3[0] - 5, P3[1]),
            arrowprops=dict(arrowstyle='<->', color='black', lw=0.8))
ax.text(IFP[0] - 12, (IFP[1] + P3[1])/2, r'$c_2$', fontsize=8,
        fontstyle='italic', ha='right', va='center')

# hsp3 y dsp3 para el soporte S3
ax.annotate('', xy=(IFD[0] + dsp3 + 3, IFD[1]),
            xytext=(IFD[0] + dsp3 + 3, S3[1]),
            arrowprops=dict(arrowstyle='<->', color='black', lw=0.8))
ax.text(IFD[0] + dsp3 + 7, (IFD[1] + S3[1])/2, r'$h_{sp3}$',
        fontsize=7, fontstyle='italic', ha='left', va='center')

# --- ANGULOS ---
# theta_1_inicial
draw_angle_arc(ax, BANCADA_L, 8, 0, 70,
               label=r'$\theta_{1,ini}$', label_offset=5, fontsize=7)

# theta_aux_fm
draw_angle_arc(ax, IFP, 10, 160, 180,
               label=r'$\theta_{aux,fm}$', label_offset=5, fontsize=7)

# theta_aux_fd
draw_angle_arc(ax, IFD, 10, 160, 180,
               label=r'$\theta_{aux,fd}$', label_offset=5, fontsize=7)

# --- CONFIGURACION DEL GRAFICO ---
ax.set_aspect('equal')
ax.set_xlim([TIP[0] - 25, MCF[0] + 35])
ax.set_ylim([MCF[1] - 30, max(P[1], P2[1], P3[1], D3[1]) + 15])
ax.axis('off')

# Titulo
ax.set_title(
    'Diagrama Esquematico - Mecanismo Completo con Tercer 4-Barras (DIP)\n'
    r'$L_9$ y $L_{10}$ conectados: $P_3 \rightarrow D_3 \rightarrow IFD$',
    fontsize=12, fontweight='bold', pad=15
)

plt.tight_layout()
plt.savefig('/projects/sandbox/Optmizacion_exo_3/diagrama_tercer_mecanismo.png',
            dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print("Diagrama esquematico generado exitosamente: diagrama_tercer_mecanismo.png")
print("Estilo: blanco y negro, ingenieria, esquematico (topologia)")
print("Incluye tercer mecanismo de 4 barras: P3 -> L9 -> D3 -> L10 -> IFD")
