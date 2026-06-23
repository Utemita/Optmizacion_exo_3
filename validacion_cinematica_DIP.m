function R = validacion_cinematica_DIP()
% =========================================================================
% validacion_cinematica_DIP.m
% -------------------------------------------------------------------------
% Valida el RANGO DE MOVIMIENTO de las tres articulaciones del dedo
% (MCP, IFP, IFD/DIP) y verifica que NO existan cambios bruscos, usando la
% cinematica REAL del exoesqueleto MAS el tercer mecanismo de 4 barras
% (Link9 = 25 mm, Link10 = 35 mm) que da movimiento relativo a la falange
% distal.
%
% Este script:
%   1) Porta fielmente la cinematica de CinematicaExoFinal.m
%      (dos mecanismos de 5 barras + dos de 4 barras).
%   2) AGREGA el tercer mecanismo de 4 barras resuelto por interseccion de
%      circulos (sin funciones "hacky"): la falange distal deja de moverse
%      con un offset constante y pasa a girar segun el cierre del 4 barras.
%   3) Recorre el bucle completo del actuador (THETA2 = 0..132 grados).
%   4) Calcula el ROM de MCP, IFP, IFD y el salto maximo entre pasos
%      consecutivos (criterio de suavidad: < 5 grados => movimiento gradual).
%   5) Grafica los angulos articulares y los saltos entre pasos.
%
% Uso:
%   >> R = validacion_cinematica_DIP;     % R contiene los resultados
%   o simplemente:
%   >> validacion_cinematica_DIP
%
% Compatible con MATLAB y GNU Octave.
% =========================================================================

clc;
P = parametros();

N = 133;                 % THETA2 = 0..132 (igual que el .m original)
dtheta = 360 / 360;      % jnodos = 360 -> dtheta = 1 grado

THETA2   = zeros(1, N);
THETAfp  = zeros(1, N);   % flexion absoluta falange proximal
THETAfm  = zeros(1, N);   % flexion absoluta falange medial
THETAfd  = nan(1, N);     % flexion absoluta falange distal (tercer mec.)
ensamble = false(1, N);

gamma  = [];   % offset de soporte (bracket) del tercer mecanismo
dorsal = [];   % signo dorsal (montaje SOBRE el dedo), fijado una sola vez

for j = 1:N
    THETA2(j) = (j - 1) * dtheta + P.TETHA2inicial;
    est = cinematica_paso(THETA2(j), P);

    THETAfp(j) = est.THETAfp;
    THETAfm(j) = est.THETAfm;

    % Calibracion (una sola vez) del bracket y del lado dorsal
    if isempty(gamma)
        tm0 = tercer_mecanismo(est, P, [], []);
        if ~tm0.ok
            continue;   % si no ensambla en reposo, se pospone la calibracion
        end
        gamma  = tm0.gamma_bracket;
        dorsal = tm0.dorsal_sign;
    end

    tm = tercer_mecanismo(est, P, gamma, dorsal);
    if tm.ok
        THETAfd(j)  = tm.THETAfd;
        ensamble(j) = true;
    end
end

% -------------------------------------------------------------------------
% RANGO DE MOVIMIENTO (relativo al reposo, j = 1)
% -------------------------------------------------------------------------
% MCP : flexion absoluta de la falange proximal respecto al reposo
% IFP : flexion de la medial RELATIVA a la proximal, respecto al reposo
% IFD : flexion de la distal RELATIVA a la medial, respecto al reposo
fp0      = THETAfp(1);
rel_ifp  = wrap180(THETAfm - THETAfp);
rel_ifd  = wrap180(THETAfd - THETAfm);
fm0_rel  = rel_ifp(1);
fd0_rel  = rel_ifd(1);

MCP = wrap180(THETAfp - fp0);
IFP = wrap180(rel_ifp - fm0_rel);
IFD = wrap180(rel_ifd - fd0_rel);

% Suavidad del movimiento de la IFD: salto maximo entre pasos consecutivos
idx        = find(ensamble);
IFD_ok     = IFD(idx);
salto_ifd  = abs(diff(IFD_ok));
salto_max  = max(salto_ifd);

% -------------------------------------------------------------------------
% REPORTE EN CONSOLA
% -------------------------------------------------------------------------
fprintf('================================================================\n');
fprintf(' VALIDACION CINEMATICA DEL TERCER MECANISMO (IFD / DIP)\n');
fprintf(' Link9 = %g mm | Link10 = %g mm | fp = %g | fm = %g | fd = %g\n', ...
        P.Link9, P.Link10, P.fp, P.fm, P.fd);
fprintf('================================================================\n');
fprintf(' MCP : rango = %6.2f deg  (min = %7.2f, max = %7.2f)\n', ...
        max(MCP) - min(MCP), min(MCP), max(MCP));
fprintf(' IFP : rango = %6.2f deg  (min = %7.2f, max = %7.2f)\n', ...
        max(IFP) - min(IFP), min(IFP), max(IFP));
fprintf(' IFD : rango = %6.2f deg  (min = %7.2f, max = %7.2f)\n', ...
        max(IFD_ok) - min(IFD_ok), min(IFD_ok), max(IFD_ok));
fprintf('----------------------------------------------------------------\n');
fprintf(' Pasos ensamblados : %d / %d\n', numel(idx), N);
fprintf(' Salto maximo IFD entre pasos adyacentes = %.2f deg\n', salto_max);
if salto_max < 5.0
    fprintf(' -> Movimiento DIP GRADUAL verificado (sin saltos bruscos).\n');
else
    fprintf(' -> ADVERTENCIA: se detecto un salto > 5 deg en la IFD.\n');
end
fprintf('================================================================\n');

% -------------------------------------------------------------------------
% GRAFICAS
% -------------------------------------------------------------------------
% Figura 1: rango de movimiento articular vs entrada del actuador
figure('Name', 'Rango de movimiento articular', 'Color', 'w');
plot(THETA2, MCP, 'k-',  'LineWidth', 1.8); hold on;
plot(THETA2, IFP, 'k--', 'LineWidth', 1.8);
plot(THETA2(idx), IFD_ok, 'k:', 'LineWidth', 1.8);
xl = xlim;
plot(xl, [0 0], 'k-', 'LineWidth', 0.8);   % linea de referencia en 0
grid on;
xlabel('Entrada del actuador  \theta_2  (grados)');
ylabel('Flexion articular relativa al reposo  (grados)');
title('Rango de movimiento articular con el tercer mecanismo (IFD)');
legend({'MCP (falange proximal)', ...
        'IFP (medial rel. proximal)', ...
        'IFD (distal rel. medial)'}, 'Location', 'best');
hold off;

% Figura 2: suavidad del movimiento distal (saltos entre pasos)
figure('Name', 'Suavidad del movimiento IFD', 'Color', 'w');
plot(THETA2(idx(2:end)), salto_ifd, 'k-', 'LineWidth', 1.5); hold on;
xl2 = xlim;
plot(xl2, [5 5], 'k--', 'LineWidth', 1.0);   % umbral de "salto brusco"
grid on;
xlabel('Entrada del actuador  \theta_2  (grados)');
ylabel('|\Delta IFD| entre pasos consecutivos  (grados)');
title(sprintf('Suavidad del movimiento IFD (salto maximo = %.2f deg)', salto_max));
legend({'Salto |\Delta IFD|', 'Umbral 5 deg'}, 'Location', 'best');
hold off;

% -------------------------------------------------------------------------
% RESULTADOS DEVUELTOS
% -------------------------------------------------------------------------
R = struct();
R.THETA2      = THETA2;
R.THETAfp     = THETAfp;
R.THETAfm     = THETAfm;
R.THETAfd     = THETAfd;
R.MCP         = MCP;
R.IFP         = IFP;
R.IFD         = IFD;
R.salto_ifd   = salto_ifd;
R.salto_max   = salto_max;
R.ensamblados = numel(idx);
end


% =========================================================================
% FUNCIONES LOCALES
% =========================================================================
function P = parametros()
% Parametros de diseno ORIGINALES (CinematicaExoFinal.m, dedo indice)
P.Bancada1 = 18;
P.Bancada2 = 20;
P.Link1 = 35;
P.Link2 = 49;
P.Link3 = 25;
P.Link4 = 20;
P.Link5 = 25;
P.Link6 = 55;
P.Link7 = 35;
P.Link8 = 52;
P.Link9 = 25;        % tercer mecanismo: acoplador (valor original)
P.Link10 = 35;       % tercer mecanismo: balancin  (valor original)
P.c2 = 46.01;
P.TETHA2inicial = 0;
P.TETHA1inicial = 109;
P.THETA14B = 90;
P.hsp = 17;
P.dsp = 18;
P.fp = 49;
P.fm = 26;
P.fd = 24;
P.THETAauxfm = 51.39;
P.THETAauxfd = 38.78;
P.reng = 2;

% --- Tercer mecanismo (montado SOBRE el dedo) ---
% Anclaje Pa de la manivela, fijo a la falange proximal en el lado dorsal:
%   back3 : retroceso a lo largo de la falange proximal (hacia MCF), mm
%   up3   : separacion dorsal (perpendicular a la falange proximal), mm
P.back3 = 6.0;
P.up3   = 18.0;

% Variables derivadas (igual que en el .m original)
P.r4 = P.Link1;
P.r5 = P.Link2;
P.r2 = P.Link3;
P.r1 = P.Link4;
P.r3 = P.Bancada1 / 2;

P.a = P.Link4;
P.b = P.Link5;
P.c = sqrt(P.hsp^2 + P.dsp^2);
P.d = P.Bancada2;

P.r1m2 = P.fp - 2 * P.dsp;
P.r2m2 = P.Link7;
P.r3m2 = P.Link5 / 2;
P.r4m2 = P.Link3;
P.r5m2 = P.Link6;

P.a2 = P.Link7;
P.b2 = P.Link8;
P.d2 = sqrt(P.hsp^2 + P.dsp^2);

P.theta14B = P.THETA14B * pi / 180;
end


function est = cinematica_paso(THETA2_deg, P)
% Porta fielmente las ecuaciones de CinematicaExoFinal.m para un angulo de
% manivela THETA2_deg (grados). Devuelve los puntos y angulos relevantes.
theta2 = THETA2_deg * pi / 180;
THETA1 = THETA2_deg / P.reng + P.TETHA1inicial;
theta1 = THETA1 * pi / 180;

% --- PRIMER MECANISMO DE 5 BARRAS ---
e = (P.r1 * sin(theta1) - P.r4 * sin(theta2)) / ...
    (P.r4 * cos(theta2) - P.r1 * cos(theta1) + 2 * P.r3);
temp1 = (2 * (P.r1 * P.r3 * cos(theta1) + P.r3 * P.r4 * cos(theta2)) ...
         - P.r1^2 + P.r2^2 + P.r4^2 - P.r5^2);
f = temp1 / (2 * (P.r4 * cos(theta2) - P.r1 * cos(theta1) + 2 * P.r3));
daux = e^2 + 1;
g = 2 * (e * f - e * P.r1 * cos(theta1) + e * P.r3 - P.r1 * sin(theta1));
h = f^2 - 2 * f * (P.r1 * cos(theta1) - P.r3) ...
    - 2 * P.r1 * P.r3 * cos(theta1) + P.r1^2 + P.r3^2 - P.r2^2;
pyP = (-g + sqrt(g^2 - 4 * daux * h)) / (2 * daux);
pxP = e * pyP + f;

% --- PRIMER MECANISMO DE 4 BARRAS ---
k1 = P.d * cos(P.theta14B) + P.a * cos(theta1);
k2 = P.d * sin(P.theta14B) + P.a * sin(theta1);
k3 = k1^2 + k2^2 + P.c^2 - P.b^2;
A1 = -k3 - 2 * k1 * P.c;
B1 = 4 * k2 * P.c;
C1 = 2 * k1 * P.c - k3;
tantheta42 = (-B1 - sqrt(B1^2 - 4 * A1 * C1)) / (2 * A1);
theta4a = 2 * atan(tantheta42);
THETA4a = theta4a * 180 / pi;
if THETA4a < 0
    THETA4a = THETA4a + 360;
end

THETAfp = THETA4a + atan2d(P.hsp, P.dsp);
thetafp = THETAfp * pi / 180;
pxIFP = P.fp * cos(thetafp) - P.d * cos(P.theta14B) - P.r3;
pyIFP = P.fp * sin(thetafp) - P.d * sin(P.theta14B);

theta4a_rad = theta4a;
pxS1 = P.c * cos(theta4a_rad) - P.d * cos(P.theta14B) - P.r3;
pyS1 = P.c * sin(theta4a_rad) - P.d * sin(P.theta14B);
THETAps2 = THETAfp - atan2d(P.hsp, (P.fp - P.dsp));
thetaps2 = THETAps2 * pi / 180;
rs2 = sqrt(P.hsp^2 + (P.fp - P.dsp)^2);
pxS2 = rs2 * cos(thetaps2) - P.d * cos(P.theta14B) - P.r3;
pyS2 = rs2 * sin(thetaps2) - P.d * sin(P.theta14B);

pxM4 = P.a * cos(theta1) - P.r3;
pyM4 = P.a * sin(theta1);

% --- SEGUNDO MECANISMO DE 5 BARRAS (sistema secundario) ---
THETAroll = atan2d(pyM4 - pyS1, pxM4 - pxS1);
thetaroll = THETAroll * pi / 180;

THETA1m2so = atan2d(pyS2 - pyS1, pxS2 - pxS1);
if THETA1m2so < 0
    THETA1m2so = THETA1m2so + 360;
end
theta1m2 = (THETA1m2so - THETAroll) * pi / 180;

THETA2m2so = atan2d(pyP - pyM4, pxP - pxM4);
if THETA2m2so < 0
    THETA2m2so = THETA2m2so + 360;
end
theta2m2 = (THETA2m2so - THETAroll) * pi / 180;

temp2 = (P.r4m2 * cos(theta2m2) - P.r1m2 * cos(theta1m2) + 2 * P.r3m2);
em2 = (P.r1m2 * sin(theta1m2) - P.r4m2 * sin(theta2m2)) / temp2;
temp3 = (2 * (P.r1m2 * P.r3m2 * cos(theta1m2) ...
              + P.r3m2 * P.r4m2 * cos(theta2m2)) ...
         - P.r1m2^2 + P.r2m2^2 + P.r4m2^2 - P.r5m2^2);
fm2 = temp3 / (2 * temp2);
dauxm2 = em2^2 + 1;
gm2 = 2 * (em2 * fm2 - em2 * P.r1m2 * cos(theta1m2) ...
           + em2 * P.r3m2 - P.r1m2 * sin(theta1m2));
hm2 = fm2^2 - 2 * fm2 * (P.r1m2 * cos(theta1m2) - P.r3m2) ...
      - 2 * P.r1m2 * P.r3m2 * cos(theta1m2) ...
      + P.r1m2^2 + P.r3m2^2 - P.r2m2^2;
pyP2 = (-gm2 + sqrt(gm2^2 - 4 * dauxm2 * hm2)) / (2 * dauxm2);
pxP2 = em2 * pyP2 + fm2;

p2mag = sqrt(pxP2^2 + pyP2^2);
theta2p2 = atan2d(pyP2, pxP2) * pi / 180;
pxAUX = (pxS1 + pxM4) / 2;
pyAUX = (pyS1 + pyM4) / 2;
pxP2so = p2mag * cos(theta2p2 + thetaroll) + pxAUX;
pyP2so = p2mag * sin(theta2p2 + thetaroll) + pyAUX;

% --- SEGUNDO MECANISMO DE 4 BARRAS ---
THETA14B2 = atan2d(pyS2 - pyIFP, pxS2 - pxIFP);
theta14B2 = THETA14B2 * pi / 180;
THETA24B2 = atan2d(pyP2so - pyS2, pxP2so - pxS2);
if THETA24B2 < 0
    THETA24B2 = THETA24B2 + 360;
end
theta24B2 = THETA24B2 * pi / 180;

k1m2 = P.d2 * cos(theta14B2) + P.a2 * cos(theta24B2);
k2m2 = P.d2 * sin(theta14B2) + P.a2 * sin(theta24B2);
k3m2 = k1m2^2 + k2m2^2 + P.c2^2 - P.b2^2;
A1m2 = -k3m2 - 2 * k1m2 * P.c2;
B1m2 = 4 * k2m2 * P.c2;
C1m2 = 2 * k1m2 * P.c2 - k3m2;
tantheta42m2 = (-B1m2 - sqrt(B1m2^2 - 4 * A1m2 * C1m2)) / (2 * A1m2);
theta4am2 = 2 * atan(tantheta42m2);
THETA4am2 = theta4am2 * 180 / pi;
if THETA4am2 < 0
    THETA4am2 = THETA4am2 + 360;
end

pxP3 = pxIFP + P.c2 * cos(THETA4am2 * pi / 180);
pyP3 = pyIFP + P.c2 * sin(THETA4am2 * pi / 180);

% Falange medial (flexion natural)
THETAfm = THETA4am2 + P.THETAauxfm;
thetafm = THETAfm * pi / 180;
pxIFD = P.fm * cos(thetafm) + pxIFP;
pyIFD = P.fm * sin(thetafm) + pyIFP;

% Empaquetar resultados
est.THETA2  = THETA2_deg;
est.THETAfp = THETAfp;
est.THETAfm = THETAfm;
est.IFP = [pxIFP, pyIFP];
est.IFD = [pxIFD, pyIFD];
est.P3  = [pxP3, pyP3];
end


function tm = tercer_mecanismo(est, P, gamma_bracket, dorsal_sign)
% Resuelve el tercer mecanismo de 4 barras (montado SOBRE el dedo):
%   Tierra:    IFP -> IFD (falange medial, fm)
%   Manivela:  IFP -> Pa   (Pa fijo en la falange proximal, lado dorsal)
%   Acoplador: Pa  -> D3   (Link9)
%   Balancin:  IFD -> D3   (Link10), rigido con la falange distal
%
% Si gamma_bracket / dorsal_sign vienen vacios, se calibran en esta pose y se
% devuelven para reutilizarlos en TODO el recorrido (evita saltos por re-elegir
% el lado dorsal en cada cuadro).
tm.ok = false;
tm.gamma_bracket = gamma_bracket;
tm.dorsal_sign   = dorsal_sign;

IFP = est.IFP;
IFD = est.IFD;
thetafp = est.THETAfp * pi / 180;

prox_dir  = [cos(thetafp), sin(thetafp)];
prox_norm = [-prox_dir(2), prox_dir(1)];

% Signo dorsal: se decide UNA sola vez (calibracion) por el lado de P3
if isempty(dorsal_sign)
    if dot(est.P3 - IFP, prox_norm) >= 0
        dorsal_sign = 1.0;
    else
        dorsal_sign = -1.0;
    end
    tm.dorsal_sign = dorsal_sign;
end
prox_norm = dorsal_sign * prox_norm;

% Anclaje de la manivela, fijo a la falange proximal (lado dorsal)
Pa = IFP - P.back3 * prox_dir + P.up3 * prox_norm;

[solA, solB, okFlag] = circle_intersections(Pa, P.Link9, IFD, P.Link10);
if ~okFlag
    return;
end

% Eleccion de la solucion dorsal respecto al eje IFP->IFD
medial_dir = (IFD - IFP);
medial_dir = medial_dir / hypot(medial_dir(1), medial_dir(2));
normal = dorsal_sign * [-medial_dir(2), medial_dir(1)];
sideA = dot(solA - IFP, normal);
sideB = dot(solB - IFP, normal);
if sideA >= sideB
    D3 = solA;
else
    D3 = solB;
end

ang_rocker = atan2(D3(2) - IFD(2), D3(1) - IFD(1));   % rad

% Calibracion del bracket para conservar la flexion natural en reposo
if isempty(gamma_bracket)
    thetafd_nat = (est.THETAfm + P.THETAauxfd) * pi / 180;
    gamma_bracket = thetafd_nat - ang_rocker;
    tm.gamma_bracket = gamma_bracket;
end

THETAfd = (ang_rocker + gamma_bracket) * 180 / pi;
thetafd = THETAfd * pi / 180;
PF = IFD + P.fd * [cos(thetafd), sin(thetafd)];

tm.ok = true;
tm.Pa = Pa;
tm.D3 = D3;
tm.PF = PF;
tm.THETAfd = THETAfd;
tm.ang_rocker = ang_rocker * 180 / pi;
end


function [solA, solB, okFlag] = circle_intersections(c0, r0, c1, r1)
% Interseccion de dos circulos. okFlag = false si no se cortan.
solA = [NaN, NaN];
solB = [NaN, NaN];
okFlag = false;

dvec = c1 - c0;
dist = hypot(dvec(1), dvec(2));
if dist > (r0 + r1) || dist < abs(r0 - r1) || dist == 0
    return;
end
aa = (r0^2 - r1^2 + dist^2) / (2 * dist);
hh2 = r0^2 - aa^2;
if hh2 < 0
    return;
end
hh = sqrt(hh2);
pm = c0 + aa * dvec / dist;
perp = [-dvec(2), dvec(1)] / dist;
solA = pm + hh * perp;
solB = pm - hh * perp;
okFlag = true;
end


function a = wrap180(a)
% Normaliza angulos (grados) al rango (-180, 180]
a = mod(a + 180, 360) - 180;
end
