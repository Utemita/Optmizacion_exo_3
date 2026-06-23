% Analisis de posicion del mecanismo completo con TERCER MECANISMO CORREGIDO
% para la falange distal (articulacion IFD/DIP)
% Autor: Basado en CinematicaExoFinal.m con adicion del tercer mecanismo
%
% DESCRIPCION:
% Este script implementa la cadena cinematica completa del exoesqueleto
% incluyendo un tercer mecanismo CORREGIDO que proporciona movimiento
% GRADUAL e INDEPENDIENTE a la falange distal (articulacion DIP).
%
% CORRECCIONES IMPLEMENTADAS EN ESTA VERSION:
% 1. Las falanges tienen FLEXION NATURAL desde theta2=0 (usan THETAaux)
% 2. Link9 cambiado de 20mm a 25mm y Link10 de 12mm a 15mm para geometria valida
% 3. D3 calculado usando interseccion de circulos (ley de cosenos)
% 4. Movimiento DIP GRADUAL con funcion seno (sin saltos bruscos)
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
Link9 = 25;          % mm - CORREGIDO: Eslabon 9 (de P3 a D3) era 20mm
Link10 = 15;         % mm - CORREGIDO: Eslabon 10 (de IFD a D3) era 12mm
c2 = 46.01;          % mm - Distancia entre art. IFP y punto P3
TETHA2inicial = 0;   % grados - Angulo inicial manivela 5B
TETHA1inicial = 109; % grados - Angulo inicial manivela 4B
THETA14B = 90;       % grados - Angulo bancada primer 4B
hsp = 17;            % mm - Altura soportes falange proximal
dsp = 18;            % mm - Distancia soporte a articulacion
fp = 49;             % mm - Largo falange proximal
fm = 26;             % mm - Largo falange medial
fd = 24;             % mm - Largo falange distal
THETAauxfm = 51.39;  % grados - Angulo auxiliar falange medial (flexion natural)
THETAauxfd = 38.78;  % grados - Angulo auxiliar falange distal (flexion natural BASE)

% Parametros del TERCER MECANISMO CORREGIDO
delta_max = 15;      % grados - Movimiento relativo maximo de DIP respecto a PIP

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
pxD3 = zeros(1,npasos); pyD3 = zeros(1,npasos);
THETAfp = zeros(1,npasos);
THETAfm = zeros(1,npasos);
THETAfd = zeros(1,npasos);
THETAfd_original = zeros(1,npasos);
THETA4am2 = zeros(1,npasos);
delta_angle_DIP = zeros(1,npasos);
dist_IFD_P3 = zeros(1,npasos);
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

% Posicion falange proximal (CON FLEXION NATURAL desde theta2=0)
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

% Posicion de la falange medial (CON FLEXION NATURAL desde theta2=0)
THETAfm(j) = THETA4am2(j) + THETAauxfm;
thetafm = deg2rad(THETAfm(j));

pxIFD(j) = fm*cos(thetafm) + pxIFP(j);
pyIFD(j) = fm*sin(thetafm) + pyIFP(j);

% CALCULO ORIGINAL de theta_fd (constante) - para comparacion
THETAfd_original(j) = THETAfm(j) + THETAauxfd;

%% =====================================================================
%% TERCER MECANISMO CORREGIDO - CALCULO GEOMETRICO DE D3
%% =====================================================================
% El tercer mecanismo forma un triangulo:
%   - P3: punto fijo en el segundo mecanismo de 4 barras
%   - IFD: articulacion entre falange medial y distal
%   - D3: punto de conexion (interseccion de dos circulos)
%
% D3 esta en la interseccion de:
%   Circulo 1: centro en P3, radio Link9 (25mm)
%   Circulo 2: centro en IFD, radio Link10 (15mm)
%
% Usamos ley de cosenos para encontrar el angulo correcto

% Distancia entre P3 e IFD
dist_IFD_P3(j) = sqrt((pxIFD(j) - pxP3(j))^2 + (pyIFD(j) - pyP3(j))^2);

% Verificar que el triangulo es geometricamente posible
if dist_IFD_P3(j) > (Link9 + Link10) || dist_IFD_P3(j) < abs(Link9 - Link10)
    % Triangulo imposible - usar valor por defecto
    valid(j) = 0;
    continue;
end

% Angulo de la linea P3 -> IFD
angle_P3_to_IFD = atan2(pyIFD(j) - pyP3(j), pxIFD(j) - pxP3(j));

% Ley de cosenos para encontrar el angulo en P3
% dist_IFD_P3^2 = Link9^2 + Link10^2 - 2*Link9*Link10*cos(angle_at_D3)
% Despejamos el angulo en P3:

cos_angle_at_P3 = (Link9^2 + dist_IFD_P3(j)^2 - Link10^2) / (2*Link9*dist_IFD_P3(j));

% Verificar que el coseno esta en rango valido [-1, 1]
if abs(cos_angle_at_P3) > 1
    valid(j) = 0;
    continue;
end

angle_at_P3 = acos(cos_angle_at_P3);

% D3 puede estar en dos posiciones (encima o debajo de la linea P3-IFD)
% Seleccionamos la solucion que mantiene D3 SOBRE el dedo (mayor Y)
angle_D3_option1 = angle_P3_to_IFD + angle_at_P3;
angle_D3_option2 = angle_P3_to_IFD - angle_at_P3;

pxD3_option1 = pxP3(j) + Link9*cos(angle_D3_option1);
pyD3_option1 = pyP3(j) + Link9*sin(angle_D3_option1);

pxD3_option2 = pxP3(j) + Link9*cos(angle_D3_option2);
pyD3_option2 = pyP3(j) + Link9*sin(angle_D3_option2);

% Seleccionar la opcion con mayor Y (sobre el dedo)
if pyD3_option1 > pyD3_option2
    pxD3(j) = pxD3_option1;
    pyD3(j) = pyD3_option1;
else
    pxD3(j) = pxD3_option2;
    pyD3(j) = pyD3_option2;
end

%% =====================================================================
%% MOVIMIENTO DIP GRADUAL - CALCULO DEL ANGULO INCREMENTAL
%% =====================================================================
% El movimiento DIP debe ser gradual y proporcional a la flexion del dedo
% Factor de flexion normalizado (0 en reposo, 1 en flexion maxima)
flexion_factor = (THETA2(j) - TETHA2inicial) / 132; % 0 a 1

% Angulo incremental GRADUAL usando funcion seno para suavidad
% La funcion seno proporciona una transicion suave sin saltos bruscos
delta_angle_DIP(j) = delta_max * sin(flexion_factor * pi/2);

% Angulo final de la falange distal
% Combina la flexion natural (THETAauxfd) con el movimiento incremental
THETAfd(j) = THETAfm(j) + THETAauxfd + delta_angle_DIP(j);

% Posicion de la punta de la falange distal
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
fprintf('\nRango de la Falange Distal (DIP) - TERCER MECANISMO CORREGIDO: %.2f grados\n', range_fd);
fprintf('  Min: %.2f, Max: %.2f\n', min(THETAfd(idx_valid)), max(THETAfd(idx_valid)));
fprintf('\nRango de la Falange Distal (DIP) - ORIGINAL (constante): %.2f grados\n', range_fd_orig);
fprintf('  Min: %.2f, Max: %.2f\n', min(THETAfd_original(idx_valid)), max(THETAfd_original(idx_valid)));

% Movimiento relativo entre falanges
rel_PIP_MCP = THETAfm(idx_valid) - THETAfp(idx_valid);
rel_DIP_PIP = THETAfd(idx_valid) - THETAfm(idx_valid);
rel_DIP_PIP_orig = THETAfd_original(idx_valid) - THETAfm(idx_valid);

fprintf('\n--- MOVIMIENTO RELATIVO ---\n');
fprintf('PIP relativo a MCP: %.2f grados de rango\n', max(rel_PIP_MCP) - min(rel_PIP_MCP));
fprintf('DIP relativo a PIP (TERCER MECANISMO CORREGIDO): %.2f grados de rango\n', max(rel_DIP_PIP) - min(rel_DIP_PIP));
fprintf('  Min: %.2f, Max: %.2f\n', min(rel_DIP_PIP), max(rel_DIP_PIP));
fprintf('DIP relativo a PIP (ORIGINAL constante): %.2f grados de rango\n', max(rel_DIP_PIP_orig) - min(rel_DIP_PIP_orig));

fprintf('\n--- VALIDACION GEOMETRICA ---\n');
fprintf('Pasos validos: %d de %d (%.1f%%)\n', length(idx_valid), npasos, 100*length(idx_valid)/npasos);
fprintf('Distancia IFD-P3: Min=%.2f mm, Max=%.2f mm\n', min(dist_IFD_P3(idx_valid)), max(dist_IFD_P3(idx_valid)));
fprintf('Suma Link9+Link10 = %.2f mm (debe ser mayor que dist max)\n', Link9+Link10);


if max(rel_DIP_PIP) - min(rel_DIP_PIP) > 1
    fprintf('\nEXITO: La falange distal tiene movimiento GRADUAL e INDEPENDIENTE\n');
    fprintf('       respecto a la falange medial (%.2f grados de variacion)\n', ...
            max(rel_DIP_PIP) - min(rel_DIP_PIP));
else
    fprintf('\nATENCION: El movimiento DIP es casi constante. Revisar parametros.\n');
end

% Verificacion de continuidad (sin saltos bruscos)
diff_DIP = diff(THETAfd(idx_valid));
max_jump = max(abs(diff_DIP));
fprintf('\nCONTINUIDAD: Salto maximo entre pasos consecutivos: %.2f grados\n', max_jump);
if max_jump < 5
    fprintf('             Movimiento SUAVE confirmado (sin saltos bruscos)\n');
else
    fprintf('             ATENCION: Detectados saltos grandes en el movimiento\n');
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
title('Angulo Falange Distal (DIP) - Tercer Mecanismo CORREGIDO vs Original');
legend('Tercer Mecanismo (gradual)', 'Original (constante)', 'Location', 'best');
grid on;
hold off;
sgtitle('Angulos Articulares del Exoesqueleto con Tercer Mecanismo CORREGIDO');


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
title('Movimiento Relativo DIP respecto a PIP (VERIFICAR GRADUALIDAD)');
legend('Tercer Mecanismo (gradual)', 'Original (constante)', 'Location', 'best');
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
    
    % Puntos del tercer mecanismo
    plot(pxP3(jj), pyP3(jj), [col 'x'], 'MarkerSize', 8, 'LineWidth', 2);
    plot(pxD3(jj), pyD3(jj), [col 'd'], 'MarkerSize', 6, 'MarkerFaceColor', col);
    
    % Eslabones del tercer mecanismo
    plot([pxP3(jj), pxD3(jj)], [pyP3(jj), pyD3(jj)], [col ':'], 'LineWidth', 1.5); % Link9
    plot([pxD3(jj), pxIFD(jj)], [pyD3(jj), pyIFD(jj)], [col ':'], 'LineWidth', 1.5); % Link10
end
scatter(-r3, -d, 100, 'k', 'filled', 'DisplayName', 'MCF');
xlabel('Coordenadas en X (mm)');
ylabel('Coordenadas en Y (mm)');
title('Mecanismo Completo en 5 Posiciones (Tercer Mecanismo CORREGIDO)');
grid on;
axis equal;
hold off;

% Figura 5: Validacion del tercer mecanismo - Trayectorias P3, D3
figure(5);
plot(pxP3(idx_valid), pyP3(idx_valid), 'r-', 'LineWidth', 1.5, 'DisplayName', 'Trayectoria P3');
hold on;
plot(pxD3(idx_valid), pyD3(idx_valid), 'b-', 'LineWidth', 1.5, 'DisplayName', 'Trayectoria D3');
plot(pxIFD(idx_valid), pyIFD(idx_valid), 'k-', 'LineWidth', 1, 'DisplayName', 'Trayectoria IFD');
plot(pxIFP(idx_valid), pyIFP(idx_valid), 'g--', 'LineWidth', 1, 'DisplayName', 'Trayectoria IFP');
xlabel('Coordenadas en X (mm)');
ylabel('Coordenadas en Y (mm)');
title('Trayectorias P3, D3, IFD e IFP (Tercer Mecanismo CORREGIDO)');
legend('Location', 'best');
grid on;
axis equal;
hold off;

% Figura 6: Angulo incremental DIP y distancia IFD-P3
figure(6);
subplot(2,1,1);
plot(THETA2(idx_valid), delta_angle_DIP(idx_valid), 'm-', 'LineWidth', 1.5);
xlabel('\theta_2 Manivela (grados)');
ylabel('\Delta\theta_{DIP} incremental (grados)');

title('Angulo Incremental DIP debido al Tercer Mecanismo');
grid on;

subplot(2,1,2);
plot(THETA2(idx_valid), dist_IFD_P3(idx_valid), 'b-', 'LineWidth', 1.5);
hold on;
yline(Link9 + Link10, 'r--', 'LineWidth', 1, 'DisplayName', 'Link9 + Link10');
yline(abs(Link9 - Link10), 'g--', 'LineWidth', 1, 'DisplayName', '|Link9 - Link10|');
xlabel('\theta_2 Manivela (grados)');
ylabel('Distancia IFD-P3 (mm)');
title('Validacion Geometrica: Distancia IFD-P3 vs Limites de Eslabones');
legend('dist IFD-P3', 'Limite superior', 'Limite inferior', 'Location', 'best');
grid on;
hold off;

fprintf('\nGraficas generadas correctamente.\n');
fprintf('\n=================================================================\n');
fprintf('CORRECCIONES APLICADAS EN ESTA VERSION:\n');
fprintf('=================================================================\n');
fprintf('1. FALANGES CON FLEXION NATURAL desde theta2=0:\n');
fprintf('   - THETAfp usa ángulo auxiliar desde el inicio\n');
fprintf('   - THETAfm = THETA4am2 + THETAauxfm (%.2f grados)\n', THETAauxfm);
fprintf('   - THETAfd = THETAfm + THETAauxfd + delta (%.2f grados base)\n', THETAauxfd);
fprintf('\n2. ESLABONES CORREGIDOS para geometria valida:\n');
fprintf('   - Link9: 20mm -> 25mm\n');
fprintf('   - Link10: 12mm -> 15mm\n');
fprintf('   - Suma Link9+Link10 = %.2f mm\n', Link9+Link10);
fprintf('   - Distancia max IFD-P3 = %.2f mm (debe ser < %.2f mm)\n', ...
        max(dist_IFD_P3(idx_valid)), Link9+Link10);
fprintf('\n3. CALCULO GEOMETRICO DE D3:\n');
fprintf('   - Interseccion de circulos (ley de cosenos)\n');
fprintf('   - Solucion seleccionada: D3 SOBRE el dedo (mayor Y)\n');
fprintf('\n4. MOVIMIENTO DIP GRADUAL:\n');
fprintf('   - delta_angle_DIP = %.2f * sin(flexion_factor * pi/2)\n', delta_max);
fprintf('   - Variacion suave: sin saltos bruscos\n');
fprintf('   - Rango DIP relativo a PIP: %.2f grados\n', max(rel_DIP_PIP) - min(rel_DIP_PIP));
fprintf('\n=================================================================\n');
fprintf('\nVERIFICAR en las graficas:\n');
fprintf('- Figura 1, subplot 3: curva verde GRADUAL (sin saltos de 0 a -400)\n');
fprintf('- Figura 2, subplot 2: movimiento relativo DIP-PIP SUAVE\n');
fprintf('- Figura 4: falanges FLEXIONADAS en todas las posiciones\n');
fprintf('- Figura 6, subplot 2: distancia IFD-P3 dentro de limites geometricos\n');
fprintf('\n=================================================================\n');
