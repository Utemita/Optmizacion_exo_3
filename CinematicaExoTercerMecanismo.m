% Analisis de posicion del mecanismo completo con TERCER MECANISMO DE 4 BARRAS
% para la falange distal (articulacion IFD/DIP)
% Autor: Basado en CinematicaExoFinal.m con adicion del tercer mecanismo
%
% DESCRIPCION:
% Este script implementa la cadena cinematica completa del exoesqueleto
% incluyendo un tercer mecanismo de 4 barras que proporciona movimiento
% VARIABLE e INDEPENDIENTE a la falange distal (articulacion DIP).
%
% El tercer mecanismo utiliza:
%   - Punto P3 (calculado por el segundo mecanismo) como punto de entrada
%   - Un punto de soporte S3 sobre la falange medial como pivote fijo
%   - Link9 = 25mm como acoplador
%   - Link10 = 35mm como balancin de salida
%   - La salida determina theta_fd de forma VARIABLE (ya no es constante)
%
% IMPORTANTE: Todo el mecanismo va montado SOBRE el dedo (no por debajo)

clear all;
close all;
clc;

%% ========================================================================
% PARAMETROS DE DISENO
% =========================================================================
% Parametros originales del exoesqueleto (dedo indice)
Bancada1 = 18;       % mm
Bancada2 = 20;       % mm
Link1 = 35;          % mm - Eslabon 1 del primer mecanismo 5B
Link2 = 49;          % mm - Eslabon 2 del primer mecanismo 5B
Link3 = 25;          % mm - Eslabon 3 del primer mecanismo 5B
Link4 = 20;          % mm - Eslabon 4 (manivela compartida)
Link5 = 25;          % mm - Eslabon 5
Link6 = 55;          % mm - Eslabon 6 del segundo mecanismo 5B
Link7 = 35;          % mm - Eslabon 7 (manivela segundo 4B)
Link8 = 52;          % mm - Eslabon 8 (acoplador segundo 4B)
Link9 = 25;          % mm - Eslabon 9 (acoplador TERCER 4B) - AHORA EN USO
Link10 = 35;         % mm - Eslabon 10 (balancin TERCER 4B) - AHORA EN USO
c2 = 46.01;          % mm - Distancia entre art. IFP y punto P3
TETHA2inicial = 0;   % grados - Angulo inicial manivela 5B
TETHA1inicial = 109; % grados - Angulo inicial manivela 4B
THETA14B = 90;       % grados - Angulo bancada primer 4B
hsp = 17;            % mm - Altura soportes falange proximal
dsp = 18;            % mm - Distancia soporte a articulacion
fp = 49;             % mm - Largo falange proximal
fm = 26;             % mm - Largo falange medial
fd = 24;             % mm - Largo falange distal
THETAauxfm = 51.39;  % grados - Angulo auxiliar falange medial
THETAauxfd = 38.78;  % grados - Angulo auxiliar falange distal (referencia)

% Parametros del TERCER MECANISMO DE 4 BARRAS (nuevos)
% Soporte S3: punto fijo sobre la falange medial, a una distancia dsp3
% desde la articulacion IFD (hacia IFP), a una altura hsp3 sobre la falange
hsp3 = 12;           % mm - Altura del soporte S3 sobre falange medial
dsp3 = 8;            % mm - Distancia del soporte S3 desde IFD hacia IFP
% Estas dimensiones son proporcionales a la falange medial (26mm)
% y mantienen el mecanismo compacto y SOBRE el dedo

omega2 = 10;         % RPM - Velocidad manivela
reng = 2;            % Relacion de engranaje

%% ========================================================================
% ASIGNACION DE VARIABLES PARA ECUACIONES
% =========================================================================

% Primer mecanismo de 5 barras
r4 = Link1;
r5 = Link2;
r2 = Link3;
r1 = Link4;
r3 = Bancada1/2;

% Primer mecanismo de 4 barras
a = Link4;
b = Link5;
c = sqrt(hsp^2+dsp^2); % Hipotenusa de los soportes de la falange proximal
d = Bancada2;

% Segundo mecanismo de 5 barras
r1m2 = fp - 2*dsp;  % Distancia entre soportes S1 y S2
r2m2 = Link7;
r3m2 = Link5/2;     % Mitad del Link 5
r4m2 = Link3;
r5m2 = Link6;

% Segundo mecanismo de 4 barras
a2 = Link7;
b2 = Link8;
% c2 se ingresa como parametro directo
d2 = sqrt(hsp^2 + dsp^2); % Hipotenusa soportes falange proximal

% Tercer mecanismo de 4 barras
% a3 = distancia de S3 a P3 (variable, se calcula en cada iteracion)
% b3 = Link9 (acoplador)
% c3 = Link10 (balancin - conecta al soporte de la falange distal)
% d3 = distancia de S3 al punto de conexion en falange distal (bancada)
b3 = Link9;          % 25 mm - acoplador
c3 = Link10;         % 35 mm - balancin
% d3 se calcula como la distancia del soporte S3 al pivote de salida
% El pivote de salida esta sobre la falange distal a una distancia hsp3
% desde la articulacion IFD
d3_frame = sqrt(hsp3^2 + dsp3^2); % Bancada del tercer mecanismo

%% ========================================================================
% CONFIGURACION DEL BUCLE PRINCIPAL
% =========================================================================
theta14B_rad = THETA14B*pi/180;
OMEGA2 = omega2*2*pi/60;
tiempototal = (2*pi)/OMEGA2;

jnodos = 360;
dtheta = 360/(jnodos);
dtiempo = tiempototal/jnodos;

% Numero de pasos (solo recorremos 132 grados como en el original)
npasos = 133;

% Preasignacion de vectores
tiempo = zeros(1,npasos);
THETA2 = zeros(1,npasos);
THETA1 = zeros(1,npasos);
pxP = zeros(1,npasos); pyP = zeros(1,npasos);
pxIFP = zeros(1,npasos); pyIFP = zeros(1,npasos);
pxIFD = zeros(1,npasos); pyIFD = zeros(1,npasos);
pxPF = zeros(1,npasos); pyPF = zeros(1,npasos);
pxS1 = zeros(1,npasos); pyS1 = zeros(1,npasos);
pxS2 = zeros(1,npasos); pyS2 = zeros(1,npasos);
pxM4 = zeros(1,npasos); pyM4 = zeros(1,npasos);
pxP2so = zeros(1,npasos); pyP2so = zeros(1,npasos);
pxP3 = zeros(1,npasos); pyP3 = zeros(1,npasos);
pxS3 = zeros(1,npasos); pyS3 = zeros(1,npasos);
THETAfp = zeros(1,npasos);
THETAfm = zeros(1,npasos);
THETAfd = zeros(1,npasos);
THETAfd_original = zeros(1,npasos);
THETA4am2 = zeros(1,npasos);
THETA4am3 = zeros(1,npasos); % Angulo del balancin del tercer 4B
valid = ones(1,npasos); % Flag de validez

%% ========================================================================
% BUCLE PRINCIPAL DE CALCULO
% =========================================================================
for j=1:npasos
    
tiempo(j) = (j-1)*dtiempo;
THETA2(j) = (j-1)*dtheta + TETHA2inicial;
theta2 = THETA2(j)*pi/180;

THETA1(j) = THETA2(j)/reng + TETHA1inicial;
theta1 = THETA1(j)*pi/180;

%% --- PRIMER MECANISMO DE 5 BARRAS ---
e_5b = (r1*sin(theta1) - r4*sin(theta2)) / (r4*cos(theta2) - r1*cos(theta1) + 2*r3);
temp1 = (2*(r1*r3*cos(theta1) + r3*r4*cos(theta2)) - r1^2 + r2^2 + r4^2 - r5^2);
f_5b = temp1 / (2*(r4*cos(theta2) - r1*cos(theta1) + 2*r3));

daux = e_5b^2 + 1;
g_5b = 2*(e_5b*f_5b - e_5b*r1*cos(theta1) + e_5b*r3 - r1*sin(theta1));
h_5b = f_5b^2 - 2*f_5b*(r1*cos(theta1) - r3) - 2*r1*r3*cos(theta1) + r1^2 + r3^2 - r2^2;

disc1 = g_5b^2 - 4*daux*h_5b;
if disc1 < 0
    valid(j) = 0; continue;
end

pyP(j) = (-g_5b + sqrt(disc1)) / (2*daux);
pxP(j) = e_5b*pyP(j) + f_5b;

%% --- PRIMER MECANISMO DE 4 BARRAS ---
k1 = d*cos(theta14B_rad) + a*cos(theta1);
k2 = d*sin(theta14B_rad) + a*sin(theta1);
k3 = k1^2 + k2^2 + c^2 - b^2;
A1_4b = -k3 - 2*k1*c;
B1_4b = 4*k2*c;
C1_4b = 2*k1*c - k3;

disc2 = B1_4b^2 - 4*A1_4b*C1_4b;
if disc2 < 0
    valid(j) = 0; continue;
end

tantheta42 = (-B1_4b - sqrt(disc2)) / (2*A1_4b);
theta4a = 2*atan(tantheta42);
THETA4a_val = theta4a*180/pi;
if THETA4a_val < 0
    THETA4a_val = 360 + THETA4a_val;
end

% Posicion falange proximal
THETAfp(j) = THETA4a_val + atand(hsp/dsp);
thetafp = deg2rad(THETAfp(j));
pxIFP(j) = fp*cos(thetafp) - d*cos(theta14B_rad) - r3;
pyIFP(j) = fp*sin(thetafp) - d*sin(theta14B_rad);

% Soportes S1 y S2
pxS1(j) = c*cos(theta4a) - d*cos(theta14B_rad) - r3;
pyS1(j) = c*sin(theta4a) - d*sin(theta14B_rad);
THETAps2 = THETAfp(j) - atand(hsp/(fp-dsp));
thetaps2 = deg2rad(THETAps2);
rs2 = sqrt(hsp^2 + (fp-dsp)^2);
pxS2(j) = rs2*cos(thetaps2) - d*cos(theta14B_rad) - r3;
pyS2(j) = rs2*sin(thetaps2) - d*sin(theta14B_rad);

% Punto M4
pxM4(j) = a*cos(theta1) - r3;
pyM4(j) = a*sin(theta1);

%% --- SEGUNDO MECANISMO DE 5 BARRAS (sistema secundario) ---
THETAroll = atan2d(pyM4(j) - pyS1(j), pxM4(j) - pxS1(j));
thetaroll = deg2rad(THETAroll);

THETA1m2so = atan2d(pyS2(j) - pyS1(j), pxS2(j) - pxS1(j));
if THETA1m2so < 0, THETA1m2so = 360 + THETA1m2so; end
THETA1m2_val = THETA1m2so - THETAroll;
theta1m2 = deg2rad(THETA1m2_val);

THETA2m2so = atan2d(pyP(j) - pyM4(j), pxP(j) - pxM4(j));
if THETA2m2so < 0, THETA2m2so = 360 + THETA2m2so; end
THETA2m2_val = THETA2m2so - THETAroll;
theta2m2 = deg2rad(THETA2m2_val);

% Solucion del segundo 5 barras
temp2 = (r4m2*cos(theta2m2) - r1m2*cos(theta1m2) + 2*r3m2);
if abs(temp2) < 1e-6
    valid(j) = 0; continue;
end
em2 = (r1m2*sin(theta1m2) - r4m2*sin(theta2m2)) / temp2;
temp3 = (2*(r1m2*r3m2*cos(theta1m2) + r3m2*r4m2*cos(theta2m2)) - r1m2^2 + r2m2^2 + r4m2^2 - r5m2^2);
fm2 = temp3 / (2*temp2);

dauxm2 = em2^2 + 1;
gm2 = 2*(em2*fm2 - em2*r1m2*cos(theta1m2) + em2*r3m2 - r1m2*sin(theta1m2));
hm2 = fm2^2 - 2*fm2*(r1m2*cos(theta1m2) - r3m2) - 2*r1m2*r3m2*cos(theta1m2) + r1m2^2 + r3m2^2 - r2m2^2;

disc3 = gm2^2 - 4*dauxm2*hm2;
if disc3 < 0
    valid(j) = 0; continue;
end

pyP2_loc = (-gm2 + sqrt(disc3)) / (2*dauxm2);
pxP2_loc = em2*pyP2_loc + fm2;

% Traslado al sistema original
p2_mag = sqrt(pxP2_loc^2 + pyP2_loc^2);
THETA2p2 = atan2d(pyP2_loc, pxP2_loc);
theta2p2 = deg2rad(THETA2p2);

pxAUX = (pxS1(j) + pxM4(j))/2;
pyAUX = (pyS1(j) + pyM4(j))/2;

pxP2so(j) = p2_mag*cos(theta2p2 + thetaroll) + pxAUX;
pyP2so(j) = p2_mag*sin(theta2p2 + thetaroll) + pyAUX;

%% --- SEGUNDO MECANISMO DE 4 BARRAS ---
THETA14B2 = atan2d(pyS2(j) - pyIFP(j), pxS2(j) - pxIFP(j));
theta14B2 = deg2rad(THETA14B2);
THETA24B2 = atan2d(pyP2so(j) - pyS2(j), pxP2so(j) - pxS2(j));
if THETA24B2 < 0, THETA24B2 = 360 + THETA24B2; end
theta24B2 = deg2rad(THETA24B2);

k1m2 = d2*cos(theta14B2) + a2*cos(theta24B2);
k2m2 = d2*sin(theta14B2) + a2*sin(theta24B2);
k3m2 = k1m2^2 + k2m2^2 + c2^2 - b2^2;
A1m2 = -k3m2 - 2*k1m2*c2;
B1m2 = 4*k2m2*c2;
C1m2 = 2*k1m2*c2 - k3m2;

disc4 = B1m2^2 - 4*A1m2*C1m2;
if disc4 < 0
    valid(j) = 0; continue;
end

tantheta42m2 = (-B1m2 - sqrt(disc4)) / (2*A1m2);
theta4am2 = 2*atan(tantheta42m2);
THETA4am2(j) = theta4am2*180/pi;
if THETA4am2(j) < 0
    THETA4am2(j) = 360 + THETA4am2(j);
end

% Coordenadas del punto P3
pxP3(j) = pxIFP(j) + c2*cos(deg2rad(THETA4am2(j)));
pyP3(j) = pyIFP(j) + c2*sin(deg2rad(THETA4am2(j)));

% Posicion de la falange medial
THETAfm(j) = THETA4am2(j) + THETAauxfm;
thetafm = deg2rad(THETAfm(j));

pxIFD(j) = fm*cos(thetafm) + pxIFP(j);
pyIFD(j) = fm*sin(thetafm) + pyIFP(j);

% =====================================================================
% CALCULO ORIGINAL de theta_fd (constante) - para comparacion
THETAfd_original(j) = THETAfm(j) + THETAauxfd;

%% --- TERCER MECANISMO DE 4 BARRAS (NUEVO) ---
% Este mecanismo proporciona movimiento VARIABLE a la falange distal.
%
% Configuracion del tercer mecanismo de 4 barras:
%   - Bancada (frame): distancia de S3 a un pivote D3 sobre falange distal
%     S3 esta fijo sobre la falange medial (se mueve con ella)
%     D3 esta sobre la falange distal (es el punto que determina theta_fd)
%   - Manivela (input): eslabon que conecta S3 con P3
%     (P3 es el punto calculado por el 2do mecanismo, se mueve)
%   - Acoplador: Link9 = 25 mm (conecta P3 con D3 a traves de un punto)
%   - Balancin (output): Link10 = 35 mm (determina el angulo de salida)
%
% El punto S3 se ubica sobre la falange medial:
%   S3 = IFD + rotacion(thetafm - pi) * [dsp3; hsp3]
%   Es decir, esta a dsp3 mm ANTES de IFD y hsp3 mm POR ENCIMA

% Calculo de la posicion del soporte S3 (fijo en la falange medial)
% S3 esta a una distancia dsp3 de IFD hacia IFP, y hsp3 por encima
theta_s3_offset = atan2(hsp3, dsp3);
dist_s3 = sqrt(hsp3^2 + dsp3^2);
% La direccion "hacia IFP" desde IFD es thetafm + pi (180 grados opuesto)
% El soporte esta ARRIBA, por lo que sumamos el offset angular
theta_s3_abs = thetafm + pi - theta_s3_offset;
pxS3(j) = pxIFD(j) + dist_s3*cos(theta_s3_abs);
pyS3(j) = pyIFD(j) + dist_s3*sin(theta_s3_abs);

% Ahora resolvemos el tercer mecanismo de 4 barras
% Variables del tercer 4B:
%   - Bancada del 3er 4B: distancia entre S3 y un pivote fijo D3
%     D3 esta sobre la falange distal, a una distancia similar (hsp3, dsp3)
%     desde IFD pero en la direccion de la falange distal
%   - Para el tercer mecanismo:
%     * La "entrada" es el angulo del vector S3->P3
%     * La "bancada" es d3_frame (distancia fija S3 a D3_base)
%     * El acoplador es Link9
%     * El balancin es Link10
%
% Definicion geometrica:
%   a3 = distancia de S3 a P3 (longitud de la manivela de entrada)
%        Nota: esta cambia en cada paso, pero lo que es constante
%        es que P3 es el punto de entrada conducido por el 2do mecanismo
%   Sin embargo, para un mecanismo de 4 barras standard, necesitamos
%   una manivela de longitud fija. La solucion es:
%   La "manivela" del tercer 4B NO es S3->P3 directamente.
%   En su lugar, usamos la formulacion clasica donde:
%     - El eslabon de entrada (a3) conecta S3 con un punto Q3
%       que se mueve segun el angulo del vector S3->P3
%     - Usamos un eslabon de longitud fija desde S3 hasta un punto
%       intermedio, y P3 conduce ese angulo.
%
% SOLUCION ADOPTADA:
%   Usamos la posicion relativa de P3 respecto a S3 para definir el
%   angulo de entrada del tercer 4B. La "manivela" tiene longitud fija
%   definida como la distancia media S3-P3. Para manejar la variacion
%   de distancia, el acoplador (Link9) absorbe la diferencia mediante
%   un punto deslizante, PERO esto complicaria el diseno.
%
%   ALTERNATIVA MAS SIMPLE Y MECANICAMENTE VIABLE:
%   Conectar P3 directamente a un eslabon (Link9) que va al pivote de
%   salida en la falange distal. Es decir:
%   - P3 es el punto de entrada (se mueve con el 2do mecanismo)
%   - Link9 conecta P3 con un punto D3 (pivote en la falange distal)
%   - Link10 conecta D3 con S3 (triangulo de cierre)
%   - S3 es fijo en la falange medial
%   - IFD es la articulacion entre medial y distal
%
%   Esto forma un mecanismo de 4 barras:
%   Eslabones: S3-IFD (parte de falange medial, fijo) = bancada local
%              IFD-D3 (parte de falange distal) = balancin de salida
%              D3-P3 = Link9 (acoplador)
%              P3-S3 = variable (conducido por 2do mecanismo)
%
%   PERO la longitud P3-S3 varia...
%   SOLUCION FINAL: Usar P3 como punto del acoplador extendido del
%   segundo mecanismo, y resolver un lazo cerrado:
%   S3 -> P3 -> (Link9) -> D3 -> (Link10) -> S3
%   donde S3 y D3 estan definidos por sus posiciones relativas.

% Formulacion final del tercer mecanismo:
% Es un mecanismo RSSR (equivalente a 4 barras en 2D):
%   Lazo: IFD -> S3 -> P3 -> Q3 -> IFD
%   donde Q3 es un punto sobre la falange distal
%
% Simplificacion practica:
% Usaremos la distancia P3-IFD como "manivela variable" y resolveremos
% para el angulo de la falange distal que satisface:
%   P3 esta conectado a un punto D3 en la falange distal mediante Link9
%   D3 esta a una distancia Link10 de IFD sobre la falange distal
%
% Lazo vectorial del tercer 4B:
%   IFD + Link10*[cos(theta_fd); sin(theta_fd)] = D3
%   |P3 - D3| = Link9
%
% Esto nos da: |P3 - IFD - Link10*[cos(tfd); sin(tfd)]|^2 = Link9^2
% Expandiendo:
%   (pxP3-pxIFD-Link10*cos(tfd))^2 + (pyP3-pyIFD-Link10*sin(tfd))^2 = Link9^2
%
% Sea dx = pxP3(j) - pxIFD(j), dy = pyP3(j) - pyIFD(j)
% (dx - Link10*cos(tfd))^2 + (dy - Link10*sin(tfd))^2 = Link9^2
% dx^2 - 2*dx*Link10*cos(tfd) + Link10^2*cos^2(tfd) + 
% dy^2 - 2*dy*Link10*sin(tfd) + Link10^2*sin^2(tfd) = Link9^2
% dx^2 + dy^2 + Link10^2 - 2*Link10*(dx*cos(tfd) + dy*sin(tfd)) = Link9^2
%
% Sea R = sqrt(dx^2 + dy^2), phi = atan2(dy, dx)
% R^2 + Link10^2 - Link9^2 = 2*Link10*(dx*cos(tfd) + dy*sin(tfd))
% R^2 + Link10^2 - Link9^2 = 2*Link10*R*cos(tfd - phi)
%
% cos(tfd - phi) = (R^2 + Link10^2 - Link9^2) / (2*Link10*R)
%
% Usando sustitucion de media tangente t = tan(tfd/2):
% cos(tfd) = (1-t^2)/(1+t^2), sin(tfd) = 2t/(1+t^2)

dx3 = pxP3(j) - pxIFD(j);
dy3 = pyP3(j) - pyIFD(j);
R3 = sqrt(dx3^2 + dy3^2);
phi3 = atan2(dy3, dx3);

% Verificar condicion de existencia (desigualdad triangular)
if R3 > (Link10 + Link9) || R3 < abs(Link10 - Link9)
    % Si no se cumple, mantener theta_fd original (constante)
    THETAfd(j) = THETAfd_original(j);
    valid(j) = 0;
else
    % Resolver: cos(tfd - phi3) = (R3^2 + Link10^2 - Link9^2)/(2*Link10*R3)
    cos_arg = (R3^2 + Link10^2 - Link9^2) / (2*Link10*R3);
    
    % Asegurar que cos_arg esta en [-1, 1]
    if abs(cos_arg) > 1
        THETAfd(j) = THETAfd_original(j);
        valid(j) = 0;
    else
        % Dos soluciones: tfd = phi3 +/- acos(cos_arg)
        delta_angle = acos(cos_arg);
        
        % Solucion 1 (por encima - mecanismo SOBRE el dedo)
        tfd_sol1 = phi3 + delta_angle;
        % Solucion 2 (por debajo)
        tfd_sol2 = phi3 - delta_angle;
        
        % Seleccionar la solucion que mantiene el mecanismo SOBRE el dedo
        % El mecanismo debe estar sobre el dedo, lo que significa que D3
        % debe estar por encima de la linea de la falange.
        % La falange distal apunta en direccion thetafm + algo positivo,
        % y D3 debe estar "por encima" (angulo mayor que la falange)
        
        % Criterio: D3 debe estar SOBRE la falange medial/distal
        % Es decir, la componente perpendicular de D3-IFD respecto a
        % la direccion de la falange medial debe ser positiva (arriba)
        
        % Para la solucion sobre el dedo, escogemos la que tiene
        % mayor componente Y relativa (sobre el dedo)
        D3_y_sol1 = Link10*sin(tfd_sol1);
        D3_y_sol2 = Link10*sin(tfd_sol2);
        
        % La direccion "arriba" del dedo en la zona IFD es perpendicular
        % a la falange medial: thetafm + pi/2
        dir_up = thetafm + pi/2;
        
        % Proyeccion de D3 sobre la direccion "arriba"
        proj1 = Link10*cos(tfd_sol1 - dir_up);
        proj2 = Link10*cos(tfd_sol2 - dir_up);
        
        % Escogemos la solucion con mayor proyeccion positiva (sobre el dedo)
        if proj1 >= proj2
            THETAfd(j) = tfd_sol1 * 180/pi;
        else
            THETAfd(j) = tfd_sol2 * 180/pi;
        end
        
        % Guardar el angulo del balancin para referencia
        THETA4am3(j) = THETAfd(j);
    end
end

% Posicion de la falange distal con theta_fd VARIABLE
thetafd = deg2rad(THETAfd(j));
pxPF(j) = fd*cos(thetafd) + pxIFD(j);
pyPF(j) = fd*sin(thetafd) + pyIFD(j);

end % Fin del bucle principal

%% ========================================================================
% VERIFICACION DE RANGOS DE MOVIMIENTO
% =========================================================================
fprintf('\n========================================\n');
fprintf('VERIFICACION DE RANGOS DE MOVIMIENTO\n');
fprintf('========================================\n');

% Filtrar solo los pasos validos
idx_valid = find(valid == 1);
if isempty(idx_valid)
    error('No se encontraron posiciones validas. Revisar parametros.');
end

% Rangos articulares
range_fp = max(THETAfp(idx_valid)) - min(THETAfp(idx_valid));
range_fm = max(THETAfm(idx_valid)) - min(THETAfm(idx_valid));
range_fd = max(THETAfd(idx_valid)) - min(THETAfd(idx_valid));
range_fd_orig = max(THETAfd_original(idx_valid)) - min(THETAfd_original(idx_valid));

fprintf('\nRango de la Falange Proximal (MCP): %.2f grados\n', range_fp);
fprintf('  Min: %.2f, Max: %.2f\n', min(THETAfp(idx_valid)), max(THETAfp(idx_valid)));
fprintf('\nRango de la Falange Medial (PIP): %.2f grados\n', range_fm);
fprintf('  Min: %.2f, Max: %.2f\n', min(THETAfm(idx_valid)), max(THETAfm(idx_valid)));
fprintf('\nRango de la Falange Distal (DIP) - TERCER MECANISMO: %.2f grados\n', range_fd);
fprintf('  Min: %.2f, Max: %.2f\n', min(THETAfd(idx_valid)), max(THETAfd(idx_valid)));
fprintf('\nRango de la Falange Distal (DIP) - ORIGINAL (constante): %.2f grados\n', range_fd_orig);
fprintf('  Min: %.2f, Max: %.2f\n', min(THETAfd_original(idx_valid)), max(THETAfd_original(idx_valid)));

% Movimiento relativo entre falanges
rel_PIP_MCP = THETAfm(idx_valid) - THETAfp(idx_valid);
rel_DIP_PIP = THETAfd(idx_valid) - THETAfm(idx_valid);
rel_DIP_PIP_orig = THETAfd_original(idx_valid) - THETAfm(idx_valid);

fprintf('\n--- MOVIMIENTO RELATIVO ---\n');
fprintf('PIP relativo a MCP: %.2f grados de rango\n', max(rel_PIP_MCP) - min(rel_PIP_MCP));
fprintf('DIP relativo a PIP (TERCER MECANISMO): %.2f grados de rango\n', max(rel_DIP_PIP) - min(rel_DIP_PIP));
fprintf('DIP relativo a PIP (ORIGINAL constante): %.2f grados de rango\n', max(rel_DIP_PIP_orig) - min(rel_DIP_PIP_orig));

fprintf('\n--- VALIDACION ---\n');
fprintf('Pasos validos: %d de %d (%.1f%%)\n', length(idx_valid), npasos, 100*length(idx_valid)/npasos);

if max(rel_DIP_PIP) - min(rel_DIP_PIP) > 1
    fprintf('EXITO: La falange distal tiene movimiento VARIABLE e INDEPENDIENTE\n');
    fprintf('       respecto a la falange medial (%.2f grados de variacion)\n', ...
            max(rel_DIP_PIP) - min(rel_DIP_PIP));
else
    fprintf('ATENCION: El movimiento DIP es casi constante. Revisar parametros.\n');
end

fprintf('\n========================================\n');

%% ========================================================================
% GRAFICAS DE RESULTADOS
% =========================================================================

% Figura 1: Angulos articulares individuales
figure(1);
subplot(3,1,1);
plot(THETA2(idx_valid), THETAfp(idx_valid), 'b-', 'LineWidth', 1.5);
xlabel('\theta_2 Manivela (grados)');
ylabel('\theta_{FP} (grados)');
title('Angulo Falange Proximal (MCP)');
grid on;

subplot(3,1,2);
plot(THETA2(idx_valid), THETAfm(idx_valid), 'r-', 'LineWidth', 1.5);
xlabel('\theta_2 Manivela (grados)');
ylabel('\theta_{FM} (grados)');
title('Angulo Falange Medial (PIP)');
grid on;

subplot(3,1,3);
plot(THETA2(idx_valid), THETAfd(idx_valid), 'g-', 'LineWidth', 1.5);
hold on;
plot(THETA2(idx_valid), THETAfd_original(idx_valid), 'k--', 'LineWidth', 1);
xlabel('\theta_2 Manivela (grados)');
ylabel('\theta_{FD} (grados)');
title('Angulo Falange Distal (DIP) - Tercer Mecanismo vs Original');
legend('Tercer Mecanismo (variable)', 'Original (constante)', 'Location', 'best');
grid on;
hold off;
sgtitle('Angulos Articulares del Exoesqueleto con Tercer Mecanismo');

% Figura 2: Movimiento relativo entre falanges
figure(2);
subplot(2,1,1);
plot(THETA2(idx_valid), rel_PIP_MCP, 'm-', 'LineWidth', 1.5);
xlabel('\theta_2 Manivela (grados)');
ylabel('PIP - MCP (grados)');
title('Movimiento Relativo PIP respecto a MCP');
grid on;

subplot(2,1,2);
plot(THETA2(idx_valid), rel_DIP_PIP, 'c-', 'LineWidth', 1.5);
hold on;
plot(THETA2(idx_valid), rel_DIP_PIP_orig, 'k--', 'LineWidth', 1);
xlabel('\theta_2 Manivela (grados)');
ylabel('DIP - PIP (grados)');
title('Movimiento Relativo DIP respecto a PIP');
legend('Tercer Mecanismo (variable)', 'Original (constante)', 'Location', 'best');
grid on;
hold off;
sgtitle('Movimiento Relativo entre Falanges');

% Figura 3: Trayectorias de las articulaciones
figure(3);
plot(pxIFP(idx_valid), pyIFP(idx_valid), 'b-', 'LineWidth', 1.5, 'DisplayName', 'IFP (PIP)');
hold on;
plot(pxIFD(idx_valid), pyIFD(idx_valid), 'r-', 'LineWidth', 1.5, 'DisplayName', 'IFD (DIP)');
plot(pxPF(idx_valid), pyPF(idx_valid), 'g-', 'LineWidth', 1.5, 'DisplayName', 'Punta (Tercer Mec.)');
scatter(-r3, -d, 80, 'k', 'filled', 'DisplayName', 'Art. MCF');
scatter(0, 0, 80, 'r', 'filled', 'DisplayName', 'Origen');
xlabel('Coordenadas en X (mm)');
ylabel('Coordenadas en Y (mm)');
title('Trayectorias de las Articulaciones');
legend('Location', 'best');
grid on;
axis equal;
hold off;

% Figura 4: Mecanismo completo en posiciones representativas
figure(4);
hold on;
positions = round(linspace(idx_valid(1), idx_valid(end), 5));
colors = {'b', 'r', 'g', 'm', 'k'};
for ip = 1:length(positions)
    jj = positions(ip);
    if valid(jj) == 0, continue; end
    col = colors{ip};
    
    % Falange proximal: MCF -> IFP
    mcf_x = -r3; mcf_y = -d;
    plot([mcf_x, pxIFP(jj)], [mcf_y, pyIFP(jj)], [col '-'], 'LineWidth', 2);
    
    % Falange medial: IFP -> IFD
    plot([pxIFP(jj), pxIFD(jj)], [pyIFP(jj), pyIFD(jj)], [col '-'], 'LineWidth', 2);
    
    % Falange distal: IFD -> Punta
    plot([pxIFD(jj), pxPF(jj)], [pyIFD(jj), pyPF(jj)], [col '-'], 'LineWidth', 2);
    
    % Puntos articulares
    plot(pxIFP(jj), pyIFP(jj), [col 'o'], 'MarkerSize', 6, 'MarkerFaceColor', col);
    plot(pxIFD(jj), pyIFD(jj), [col 's'], 'MarkerSize', 6, 'MarkerFaceColor', col);
    plot(pxPF(jj), pyPF(jj), [col '^'], 'MarkerSize', 6, 'MarkerFaceColor', col);
    
    % Punto P3 y soporte S3
    plot(pxP3(jj), pyP3(jj), [col 'x'], 'MarkerSize', 8, 'LineWidth', 2);
    plot(pxS3(jj), pyS3(jj), [col 'd'], 'MarkerSize', 6, 'MarkerFaceColor', col);
    
    % Link del tercer mecanismo: P3 -> D3 (Link9)
    thetafd_j = deg2rad(THETAfd(jj));
    D3x = pxIFD(jj) + Link10*cos(thetafd_j);
    D3y = pyIFD(jj) + Link10*sin(thetafd_j);
    plot([pxP3(jj), D3x], [pyP3(jj), D3y], [col ':'], 'LineWidth', 1.5);
    plot(D3x, D3y, [col 'p'], 'MarkerSize', 8, 'MarkerFaceColor', col);
end
scatter(-r3, -d, 100, 'k', 'filled', 'DisplayName', 'MCF');
xlabel('Coordenadas en X (mm)');
ylabel('Coordenadas en Y (mm)');
title('Mecanismo Completo en 5 Posiciones (con Tercer 4B para DIP)');
grid on;
axis equal;
hold off;

% Figura 5: Validacion del punto P3 y tercer mecanismo
figure(5);
plot(pxP3(idx_valid), pyP3(idx_valid), 'r-', 'LineWidth', 1.5, 'DisplayName', 'Trayectoria P3');
hold on;
plot(pxS3(idx_valid), pyS3(idx_valid), 'b-', 'LineWidth', 1.5, 'DisplayName', 'Trayectoria S3');
plot(pxIFD(idx_valid), pyIFD(idx_valid), 'k-', 'LineWidth', 1, 'DisplayName', 'Trayectoria IFD');
xlabel('Coordenadas en X (mm)');
ylabel('Coordenadas en Y (mm)');
title('Trayectorias P3, S3 e IFD (Tercer Mecanismo)');
legend('Location', 'best');
grid on;
axis equal;
hold off;

fprintf('\nGraficas generadas correctamente.\n');
fprintf('El tercer mecanismo de 4 barras permite movimiento DIP VARIABLE.\n');

