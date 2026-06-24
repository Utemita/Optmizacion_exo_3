function R = trayectorias_tercer_mecanismo()
% =========================================================================
% trayectorias_tercer_mecanismo.m
% -------------------------------------------------------------------------
% Comprueba las TRAYECTORIAS del exoesqueleto de dedo CON el tercer mecanismo
% de 4 barras (Link9 = 25 mm, Link10 = 35 mm) que da movimiento relativo a la
% articulacion interfalangica distal (IFD/DIP).
%
% Pensado para COMPARAR contra el modelo CAD:
%   1) Recorre todo el rango del actuador (THETA2 = 0..132 grados).
%   2) Calcula la posicion (x,y) de cada articulacion y de la punta del dedo
%      usando la cinematica REAL portada de CinematicaExoFinal.m + el tercer
%      mecanismo resuelto por interseccion de circulos.
%   3) Dibuja:
%        - Figura 1: las trayectorias trazadas por IFP, IFD, punta del dedo y
%          D3 (punta del balancin L10), con el mecanismo dibujado en varias
%          poses (estilo B/N de ingenieria).
%        - Figura 2: angulos articulares MCP/IFP/IFD vs entrada del actuador.
%   4) Exporta 'trayectorias_DIP.csv' con todas las coordenadas por paso, para
%      importarlo en el CAD y verificar que las trayectorias coinciden.
%   5) Reporta longitud de trayectoria y desplazamiento de la punta del dedo.
%
% El tercer mecanismo va montado por el lado DORSAL (mismo lado que el resto
% del exoesqueleto) para no chocar con la palma; aun asi la IFD FLEXIONA hacia
% la palma de forma gradual.
%
% Uso:
%   >> R = trayectorias_tercer_mecanismo;   % R contiene las trayectorias
%   o simplemente:
%   >> trayectorias_tercer_mecanismo
%
% Compatible con MATLAB y GNU Octave.
% =========================================================================

clc;
P = parametros();

N = 133;                 % THETA2 = 0..132 (igual que el .m original)
dtheta = 1;              % grados por paso

% Reservar trayectorias
THETA2 = zeros(1, N);
MCF = nan(N, 2); IFP = nan(N, 2); IFD = nan(N, 2);
PF  = nan(N, 2); D3  = nan(N, 2); Pa  = nan(N, 2); P3 = nan(N, 2);
THETAfp = nan(1, N); THETAfm = nan(1, N); THETAfd = nan(1, N);
ok = false(1, N);

gamma = []; dorsal = [];

for j = 1:N
    THETA2(j) = (j - 1) * dtheta + P.TETHA2inicial;
    est = cinematica_paso(THETA2(j), P);

    if isempty(gamma)
        tm0 = tercer_mecanismo(est, P, [], []);
        if ~tm0.ok
            continue;
        end
        gamma = tm0.gamma_bracket;
        dorsal = tm0.dorsal_sign;
    end
    tm = tercer_mecanismo(est, P, gamma, dorsal);
    if ~tm.ok
        continue;
    end

    MCF(j, :) = est.MCF;
    IFP(j, :) = est.IFP;
    IFD(j, :) = est.IFD;
    P3(j, :)  = est.P3;
    Pa(j, :)  = tm.Pa;
    D3(j, :)  = tm.D3;
    PF(j, :)  = tm.PF;
    THETAfp(j) = est.THETAfp;
    THETAfm(j) = est.THETAfm;
    THETAfd(j) = tm.THETAfd;
    ok(j) = true;
end

idx = find(ok);

% -------------------------------------------------------------------------
% EXPORTAR CSV (para comparar con el CAD)
% -------------------------------------------------------------------------
csvname = 'trayectorias_DIP.csv';
fid = fopen(csvname, 'w');
fprintf(fid, ['THETA2,MCF_x,MCF_y,IFP_x,IFP_y,IFD_x,IFD_y,', ...
              'PF_x,PF_y,D3_x,D3_y,Pa_x,Pa_y,P3_x,P3_y,', ...
              'THETAfp,THETAfm,THETAfd\n']);
for j = idx
    fprintf(fid, ['%.3f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,', ...
                  '%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,%.4f,', ...
                  '%.3f,%.3f,%.3f\n'], ...
        THETA2(j), MCF(j,1), MCF(j,2), IFP(j,1), IFP(j,2), ...
        IFD(j,1), IFD(j,2), PF(j,1), PF(j,2), D3(j,1), D3(j,2), ...
        Pa(j,1), Pa(j,2), P3(j,1), P3(j,2), ...
        THETAfp(j), THETAfm(j), THETAfd(j));
end
fclose(fid);

% -------------------------------------------------------------------------
% METRICAS DE TRAYECTORIA
% -------------------------------------------------------------------------
lenIFP = longitud(IFP(idx, :));
lenIFD = longitud(IFD(idx, :));
lenPF  = longitud(PF(idx, :));
lenD3  = longitud(D3(idx, :));
desplPF = hypot(PF(idx(end),1) - PF(idx(1),1), ...
                PF(idx(end),2) - PF(idx(1),2));

fprintf('================================================================\n');
fprintf(' TRAYECTORIAS DEL EXOESQUELETO CON TERCER MECANISMO (IFD)\n');
fprintf(' Link9 = %g mm | Link10 = %g mm | fp = %g | fm = %g | fd = %g\n', ...
        P.Link9, P.Link10, P.fp, P.fm, P.fd);
fprintf('================================================================\n');
fprintf(' Pasos calculados (ensamblan): %d / %d\n', numel(idx), N);
fprintf(' Longitud de trayectoria (mm):\n');
fprintf('   IFP : %7.2f\n', lenIFP);
fprintf('   IFD : %7.2f\n', lenIFD);
fprintf('   Punta dedo : %7.2f\n', lenPF);
fprintf('   D3  : %7.2f\n', lenD3);
fprintf(' Punta del dedo: reposo=(%.1f,%.1f)  final=(%.1f,%.1f)\n', ...
        PF(idx(1),1), PF(idx(1),2), PF(idx(end),1), PF(idx(end),2));
fprintf(' Desplazamiento de la punta del dedo: %.1f mm\n', desplPF);
fprintf(' CSV de trayectorias exportado: %s\n', csvname);
fprintf('================================================================\n');

% -------------------------------------------------------------------------
% FIGURA 1: trayectorias + mecanismo en varias poses (B/N ingenieria)
% -------------------------------------------------------------------------
figure('Name', 'Trayectorias', 'Color', 'w');
hold on;

% Mecanismo en varias poses (gris)
nposes = 7;
sel = round(linspace(1, numel(idx), nposes));
for s = sel
    j = idx(s);
    % Falanges
    plot([MCF(j,1) IFP(j,1)], [MCF(j,2) IFP(j,2)], '-', 'Color', [.75 .75 .75], 'LineWidth', 1.0);
    plot([IFP(j,1) IFD(j,1)], [IFP(j,2) IFD(j,2)], '-', 'Color', [.75 .75 .75], 'LineWidth', 1.0);
    plot([IFD(j,1) PF(j,1)],  [IFD(j,2) PF(j,2)],  '-', 'Color', [.75 .75 .75], 'LineWidth', 1.0);
    % Tercer 4 barras: balancin IFD->D3, acoplador D3->Pa, tierra Pa->IFP
    plot([IFD(j,1) D3(j,1)], [IFD(j,2) D3(j,2)], '-', 'Color', [.55 .55 .55], 'LineWidth', 1.0);
    plot([D3(j,1) Pa(j,1)],  [D3(j,2) Pa(j,2)],  '-', 'Color', [.55 .55 .55], 'LineWidth', 1.0);
    plot([Pa(j,1) IFP(j,1)], [Pa(j,2) IFP(j,2)], '-', 'Color', [.55 .55 .55], 'LineWidth', 1.0);
end

% Trayectorias (negro, distinto estilo)
hIFP = plot(IFP(idx,1), IFP(idx,2), 'k-',  'LineWidth', 2.0);
hIFD = plot(IFD(idx,1), IFD(idx,2), 'k--', 'LineWidth', 2.0);
hPF  = plot(PF(idx,1),  PF(idx,2),  'k-.', 'LineWidth', 2.0);
hD3  = plot(D3(idx,1),  D3(idx,2),  'k:',  'LineWidth', 2.0);

% Inicio (circulo) y fin (cuadrado)
for C = {IFP, IFD, PF, D3}
    M = C{1};
    plot(M(idx(1),1),  M(idx(1),2),  'o', 'MarkerFaceColor', 'w', 'MarkerEdgeColor', 'k', 'MarkerSize', 6);
    plot(M(idx(end),1), M(idx(end),2), 's', 'MarkerFaceColor', 'k', 'MarkerEdgeColor', 'k', 'MarkerSize', 6);
end
plot(MCF(idx(1),1), MCF(idx(1),2), '^', 'MarkerFaceColor', 'k', 'MarkerEdgeColor', 'k', 'MarkerSize', 9);
text(MCF(idx(1),1) + 2, MCF(idx(1),2) - 4, 'MCF (fijo)');

axis equal; grid on;
xlabel('x (mm)'); ylabel('y (mm)');
title({'Trayectorias de las articulaciones y de la punta del dedo', ...
       '(circulo = reposo, cuadrado = flexion maxima)'});
legend([hIFP hIFD hPF hD3], ...
       {'IFP (interfalangica proximal)', 'IFD (interfalangica distal)', ...
        'Punta del dedo', 'D3 (punta del balancin L10)'}, 'Location', 'best');
hold off;

% -------------------------------------------------------------------------
% FIGURA 2: angulos articulares vs entrada del actuador
% -------------------------------------------------------------------------
fp0 = THETAfp(idx(1));
rel_ifp = wrap180(THETAfm - THETAfp);
rel_ifd = wrap180(THETAfd - THETAfm);
MCP = wrap180(THETAfp - fp0);
IFPang = wrap180(rel_ifp - rel_ifp(idx(1)));
IFDang = wrap180(rel_ifd - rel_ifd(idx(1)));

figure('Name', 'Angulos articulares', 'Color', 'w');
plot(THETA2(idx), MCP(idx), 'k-',  'LineWidth', 1.8); hold on;
plot(THETA2(idx), IFPang(idx), 'k--', 'LineWidth', 1.8);
plot(THETA2(idx), IFDang(idx), 'k:', 'LineWidth', 1.8);
grid on;
xlabel('Entrada del actuador  \theta_2  (grados)');
ylabel('Flexion articular relativa al reposo (grados)');
title('Angulos articulares con el tercer mecanismo (IFD)');
legend({'MCP', 'IFP (medial rel. proximal)', 'IFD (distal rel. medial)'}, ...
       'Location', 'best');
hold off;

% -------------------------------------------------------------------------
% RESULTADOS
% -------------------------------------------------------------------------
R = struct();
R.THETA2 = THETA2(idx);
R.MCF = MCF(idx, :);  R.IFP = IFP(idx, :);  R.IFD = IFD(idx, :);
R.PF  = PF(idx, :);   R.D3  = D3(idx, :);   R.Pa = Pa(idx, :);  R.P3 = P3(idx, :);
R.THETAfp = THETAfp(idx);  R.THETAfm = THETAfm(idx);  R.THETAfd = THETAfd(idx);
R.long_IFP = lenIFP;  R.long_IFD = lenIFD;  R.long_PF = lenPF;  R.long_D3 = lenD3;
R.despl_PF = desplPF;  R.csv = csvname;
end


function L = longitud(curve)
% Longitud acumulada de una polilinea (mm)
d = diff(curve, 1, 1);
L = sum(hypot(d(:,1), d(:,2)));
end


% =========================================================================
% FUNCIONES LOCALES (cinematica REAL, identicas a validacion_cinematica_DIP.m)
% =========================================================================
function P = parametros()
P.Bancada1 = 18; P.Bancada2 = 20;
P.Link1 = 35; P.Link2 = 49; P.Link3 = 25; P.Link4 = 20; P.Link5 = 25;
P.Link6 = 55; P.Link7 = 35; P.Link8 = 52;
P.Link9 = 25;        % tercer mecanismo: acoplador (valor original)
P.Link10 = 35;       % tercer mecanismo: balancin  (valor original)
P.c2 = 46.01;
P.TETHA2inicial = 0; P.TETHA1inicial = 109; P.THETA14B = 90;
P.hsp = 17; P.dsp = 18;
P.fp = 49; P.fm = 26; P.fd = 24;
P.THETAauxfm = 51.39; P.THETAauxfd = 38.78; P.reng = 2;

% Tercer mecanismo, montaje DORSAL (no choca con la palma):
P.back3 = -12.0;   % NEGATIVO: soporte dorsal adelantado pasando la IFP (mm)
P.up3   = 2.0;     % standoff DORSAL de perfil bajo (mm)

P.r4 = P.Link1; P.r5 = P.Link2; P.r2 = P.Link3; P.r1 = P.Link4;
P.r3 = P.Bancada1 / 2;
P.a = P.Link4; P.b = P.Link5; P.c = sqrt(P.hsp^2 + P.dsp^2); P.d = P.Bancada2;
P.r1m2 = P.fp - 2 * P.dsp; P.r2m2 = P.Link7; P.r3m2 = P.Link5 / 2;
P.r4m2 = P.Link3; P.r5m2 = P.Link6;
P.a2 = P.Link7; P.b2 = P.Link8; P.d2 = sqrt(P.hsp^2 + P.dsp^2);
P.theta14B = P.THETA14B * pi / 180;
end


function est = cinematica_paso(THETA2_deg, P)
theta2 = THETA2_deg * pi / 180;
THETA1 = THETA2_deg / P.reng + P.TETHA1inicial;
theta1 = THETA1 * pi / 180;

% PRIMER MECANISMO DE 5 BARRAS
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

% PRIMER MECANISMO DE 4 BARRAS
k1 = P.d * cos(P.theta14B) + P.a * cos(theta1);
k2 = P.d * sin(P.theta14B) + P.a * sin(theta1);
k3 = k1^2 + k2^2 + P.c^2 - P.b^2;
A1 = -k3 - 2 * k1 * P.c; B1 = 4 * k2 * P.c; C1 = 2 * k1 * P.c - k3;
tantheta42 = (-B1 - sqrt(B1^2 - 4 * A1 * C1)) / (2 * A1);
theta4a = 2 * atan(tantheta42);
THETA4a = theta4a * 180 / pi;
if THETA4a < 0, THETA4a = THETA4a + 360; end

THETAfp = THETA4a + atan2d(P.hsp, P.dsp);
thetafp = THETAfp * pi / 180;
pxIFP = P.fp * cos(thetafp) - P.d * cos(P.theta14B) - P.r3;
pyIFP = P.fp * sin(thetafp) - P.d * sin(P.theta14B);

pxS1 = P.c * cos(theta4a) - P.d * cos(P.theta14B) - P.r3;
pyS1 = P.c * sin(theta4a) - P.d * sin(P.theta14B);
THETAps2 = THETAfp - atan2d(P.hsp, (P.fp - P.dsp));
thetaps2 = THETAps2 * pi / 180;
rs2 = sqrt(P.hsp^2 + (P.fp - P.dsp)^2);
pxS2 = rs2 * cos(thetaps2) - P.d * cos(P.theta14B) - P.r3;
pyS2 = rs2 * sin(thetaps2) - P.d * sin(P.theta14B);

pxM4 = P.a * cos(theta1) - P.r3;
pyM4 = P.a * sin(theta1);

% SEGUNDO MECANISMO DE 5 BARRAS
THETAroll = atan2d(pyM4 - pyS1, pxM4 - pxS1);
thetaroll = THETAroll * pi / 180;
THETA1m2so = atan2d(pyS2 - pyS1, pxS2 - pxS1);
if THETA1m2so < 0, THETA1m2so = THETA1m2so + 360; end
theta1m2 = (THETA1m2so - THETAroll) * pi / 180;
THETA2m2so = atan2d(pyP - pyM4, pxP - pxM4);
if THETA2m2so < 0, THETA2m2so = THETA2m2so + 360; end
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
pxAUX = (pxS1 + pxM4) / 2; pyAUX = (pyS1 + pyM4) / 2;
pxP2so = p2mag * cos(theta2p2 + thetaroll) + pxAUX;
pyP2so = p2mag * sin(theta2p2 + thetaroll) + pyAUX;

% SEGUNDO MECANISMO DE 4 BARRAS
THETA14B2 = atan2d(pyS2 - pyIFP, pxS2 - pxIFP);
theta14B2 = THETA14B2 * pi / 180;
THETA24B2 = atan2d(pyP2so - pyS2, pxP2so - pxS2);
if THETA24B2 < 0, THETA24B2 = THETA24B2 + 360; end
theta24B2 = THETA24B2 * pi / 180;

k1m2 = P.d2 * cos(theta14B2) + P.a2 * cos(theta24B2);
k2m2 = P.d2 * sin(theta14B2) + P.a2 * sin(theta24B2);
k3m2 = k1m2^2 + k2m2^2 + P.c2^2 - P.b2^2;
A1m2 = -k3m2 - 2 * k1m2 * P.c2; B1m2 = 4 * k2m2 * P.c2;
C1m2 = 2 * k1m2 * P.c2 - k3m2;
tantheta42m2 = (-B1m2 - sqrt(B1m2^2 - 4 * A1m2 * C1m2)) / (2 * A1m2);
theta4am2 = 2 * atan(tantheta42m2);
THETA4am2 = theta4am2 * 180 / pi;
if THETA4am2 < 0, THETA4am2 = THETA4am2 + 360; end

pxP3 = pxIFP + P.c2 * cos(THETA4am2 * pi / 180);
pyP3 = pyIFP + P.c2 * sin(THETA4am2 * pi / 180);

THETAfm = THETA4am2 + P.THETAauxfm;
thetafm = THETAfm * pi / 180;
pxIFD = P.fm * cos(thetafm) + pxIFP;
pyIFD = P.fm * sin(thetafm) + pyIFP;

est.THETA2 = THETA2_deg; est.THETAfp = THETAfp; est.THETAfm = THETAfm;
est.MCF = [-P.r3, -P.d];
est.IFP = [pxIFP, pyIFP]; est.IFD = [pxIFD, pyIFD];
est.P3 = [pxP3, pyP3];
end


function tm = tercer_mecanismo(est, P, gamma_bracket, dorsal_sign)
% Tercer 4 barras (DORSAL): tierra Pa-IFP (sobre falange proximal),
% manivela IFP-IFD (falange medial), balancin IFD-D3 (L10),
% acoplador D3-Pa (L9). La falange distal es rigida al balancin.
tm.ok = false;
tm.gamma_bracket = gamma_bracket; tm.dorsal_sign = dorsal_sign;

IFP = est.IFP; IFD = est.IFD;
thetafp = est.THETAfp * pi / 180;
prox_dir  = [cos(thetafp), sin(thetafp)];
prox_norm = [-prox_dir(2), prox_dir(1)];

if isempty(dorsal_sign)
    if dot(est.P3 - IFP, prox_norm) >= 0
        dorsal_sign = 1.0;
    else
        dorsal_sign = -1.0;
    end
    tm.dorsal_sign = dorsal_sign;
end
dorsal_norm = dorsal_sign * prox_norm;

Pa = IFP - P.back3 * prox_dir + P.up3 * dorsal_norm;

[solA, solB, okFlag] = circle_intersections(Pa, P.Link9, IFD, P.Link10);
if ~okFlag, return; end
D3 = solB;

ang_rocker = atan2(D3(2) - IFD(2), D3(1) - IFD(1));
if isempty(gamma_bracket)
    thetafd_nat = (est.THETAfm + P.THETAauxfd) * pi / 180;
    gamma_bracket = thetafd_nat - ang_rocker;
    tm.gamma_bracket = gamma_bracket;
end
THETAfd = (ang_rocker + gamma_bracket) * 180 / pi;
thetafd = THETAfd * pi / 180;
PF = IFD + P.fd * [cos(thetafd), sin(thetafd)];

tm.ok = true; tm.Pa = Pa; tm.D3 = D3; tm.PF = PF;
tm.THETAfd = THETAfd; tm.ang_rocker = ang_rocker * 180 / pi;
end


function [solA, solB, okFlag] = circle_intersections(c0, r0, c1, r1)
solA = [NaN, NaN]; solB = [NaN, NaN]; okFlag = false;
dvec = c1 - c0;
dist = hypot(dvec(1), dvec(2));
if dist > (r0 + r1) || dist < abs(r0 - r1) || dist == 0, return; end
aa = (r0^2 - r1^2 + dist^2) / (2 * dist);
hh2 = r0^2 - aa^2;
if hh2 < 0, return; end
hh = sqrt(hh2);
pm = c0 + aa * dvec / dist;
perp = [-dvec(2), dvec(1)] / dist;
solA = pm + hh * perp; solB = pm - hh * perp; okFlag = true;
end


function a = wrap180(a)
a = mod(a + 180, 360) - 180;
end
