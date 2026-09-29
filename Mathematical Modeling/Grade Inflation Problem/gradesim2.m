clear; clc;
rng(2026);

gradePoints = [4.3 4.0 3.7 3.3 3.0 2.7 2.3 2.0 1.7 1.3 1.0 0.7 0.0];

classNames = {
    'bio 1a',
    'aerospace engineering',
    'asian diaspora',
    'public health',
    'sociology',
    'chemical engineering',
    'comparative literature',
    'env sci, policy and mgmt',
    'physics',
    'data science',
    'history',
    'civil and env eng',
    'slavic languages',
    'neuroscience',
    'business admin',
    'material science',
    'comp bio',
    'japanese',
    'molecular and cell bio',
    'celtic studies',
    'legal studies',
    'education',
    'econ',
    'ethnic studies',
    'statistics',
    'comp sci',
    'astronomy',
    'gender +womens studies',
    'french',
    'linguistics',
    'electrical eng',
    'history of art',
    'public policy',
    'mech eng',
    'south and SE asian studies'
};

classFrac = [
    0.0200 0.1300 0.1300 0.1100 0.1600 0.1000 0.0700 0.0900 0.0600 0.0400 0.0400 0.0100 0.0400;
    0.2100 0.3600 0.2100 0.0700 0.0800 0.0000 0.0700 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000;
    0.4100 0.4600 0.0800 0.0200 0.0200 0.0100 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000;
    0.1700 0.3700 0.1200 0.0900 0.0900 0.0500 0.0400 0.0300 0.0200 0.0000 0.0200 0.0000 0.0000;
    0.0500 0.3200 0.1800 0.1600 0.1100 0.0700 0.0400 0.0300 0.0300 0.0000 0.0000 0.0000 0.0100;
    0.0400 0.2600 0.1000 0.1200 0.2000 0.1300 0.0700 0.0500 0.0200 0.0100 0.0000 0.0000 0.0000;
    0.0800 0.4600 0.1500 0.0800 0.1500 0.0000 0.0800 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000;
    0.0000 0.3200 0.0700 0.0400 0.1800 0.0500 0.1600 0.1100 0.0400 0.0000 0.0000 0.0000 0.0300;
    0.1200 0.2200 0.1600 0.1900 0.1900 0.0000 0.0300 0.0500 0.0200 0.0000 0.0000 0.0000 0.0200;
    0.0200 0.2000 0.2900 0.2100 0.1800 0.0500 0.0200 0.0100 0.0000 0.0000 0.0100 0.0000 0.0100;
    0.3900 0.4500 0.0000 0.0600 0.0400 0.0000 0.0000 0.0200 0.0000 0.0000 0.0100 0.0000 0.0300;
    0.0100 0.1200 0.1200 0.1700 0.1800 0.1900 0.1200 0.0800 0.0100 0.0000 0.0000 0.0000 0.0000;
    0.0000 0.2500 0.3300 0.0800 0.1700 0.0000 0.0000 0.0000 0.1700 0.0000 0.0000 0.0000 0.0000;
    0.1000 0.1800 0.2100 0.1100 0.1100 0.1200 0.0500 0.0400 0.0400 0.0100 0.0100 0.0000 0.0200;
    0.0300 0.2200 0.1900 0.2500 0.1000 0.0600 0.0700 0.0700 0.0000 0.0000 0.0000 0.0000 0.0100;
    0.0600 0.0600 0.1700 0.2400 0.1500 0.1700 0.0600 0.0500 0.0200 0.0200 0.0000 0.0000 0.0000;
    0.1100 0.1700 0.0000 0.1100 0.2200 0.1100 0.1700 0.0000 0.1100 0.0000 0.0000 0.0000 0.0000;
    0.0000 0.3600 0.0000 0.0700 0.2100 0.1400 0.0000 0.1400 0.0800 0.0000 0.0000 0.0000 0.0000;
    0.0300 0.1700 0.1700 0.1000 0.3600 0.1300 0.0100 0.0100 0.0000 0.0000 0.0100 0.0000 0.0100;
    0.0300 0.6000 0.1000 0.0700 0.0000 0.0300 0.1000 0.0100 0.0300 0.0000 0.0000 0.0000 0.0300;
    0.0100 0.3500 0.3300 0.1400 0.1000 0.0400 0.0000 0.0000 0.0100 0.0100 0.0000 0.0000 0.0100;
    0.3700 0.3200 0.0900 0.1200 0.0300 0.0300 0.0000 0.0000 0.0200 0.0000 0.0000 0.0000 0.0200;
    0.0400 0.2500 0.1900 0.1900 0.1400 0.0900 0.0400 0.0400 0.0100 0.0100 0.0000 0.0000 0.0000;
    0.2600 0.1600 0.2100 0.1100 0.1600 0.0000 0.0000 0.0500 0.0500 0.0000 0.0000 0.0000 0.0000;
    0.0400 0.1500 0.1800 0.0700 0.1800 0.1400 0.0500 0.0700 0.0600 0.0300 0.0000 0.0300 0.0000;
    0.0300 0.2200 0.3200 0.2400 0.1300 0.0500 0.0100 0.0000 0.0000 0.0000 0.0000 0.0000 0.0000;
    0.2000 0.3100 0.3000 0.0400 0.0400 0.0400 0.0000 0.0400 0.0000 0.0200 0.0000 0.0000 0.0100;
    0.0000 0.5700 0.1100 0.1100 0.0900 0.0600 0.0000 0.0200 0.0000 0.0000 0.0000 0.0000 0.0400;
    0.0400 0.6900 0.0400 0.0800 0.0800 0.0000 0.0000 0.0000 0.0000 0.0000 0.0400 0.0000 0.0300;
    0.1200 0.4100 0.1200 0.0000 0.1200 0.0700 0.0500 0.0500 0.0000 0.0500 0.0000 0.0000 0.0100;
    0.0500 0.2500 0.2400 0.1700 0.1600 0.0600 0.0300 0.0200 0.0200 0.0000 0.0000 0.0000 0.0000;
    0.0500 0.5300 0.1900 0.0000 0.0500 0.0700 0.0500 0.0000 0.0200 0.0000 0.0000 0.0000 0.0400;
    0.0700 0.5400 0.1600 0.1100 0.0600 0.0300 0.0100 0.0000 0.0200 0.0000 0.0000 0.0000 0.0000;
    0.0300 0.3800 0.0400 0.2000 0.1700 0.1400 0.0100 0.0100 0.0200 0.0000 0.0000 0.0000 0.0000;
    0.2100 0.3000 0.1800 0.0600 0.0900 0.0600 0.0600 0.0000 0.0100 0.0000 0.0000 0.0300 0.0000
];

targetAvgGPA = [2.7420 3.7520 4.0520 3.5630 3.4110 3.2370 3.6370 3.0020 3.3880 3.4030 3.8450 3.0340 3.2840 3.2300 3.3000 3.1260 3.0510 3.0950 3.2520 3.5120 3.5640 3.8050 3.3670 3.5630 3.0040 3.5330 3.6760 3.5220 3.6240 3.4290 3.4490 3.5260 3.7340 3.4220 3.5750]';
targetStdGPA = [1.045962 0.541199 0.296810 0.758374 0.731286 0.699951 0.556175 0.942548 0.803900 0.621845 0.854678 0.618582 0.790913 0.894818 0.704273 0.660851 0.801436 0.803166 0.637257 0.908986 0.602083 0.754105 0.637661 0.727826 0.875205 0.417625 0.730085 0.864127 0.908308 0.896024 0.582837 0.924945 0.499243 0.592888 0.792638]';

M = numel(classNames);
mTaken = 32;
N = 2000;
reps = 100;
rhoSim = [0.2 0.4 0.6 0.8];
rhoGrid = [0.05:0.05:0.95, 0.99];
aGrid = linspace(-8, 8, 1601);
phiA = exp(-aGrid.^2/2)/sqrt(2*pi);
excl = nchoosek(1:M, 3);

avgHist = mean(targetAvgGPA);
kScale = 3.7/avgHist;
avgFromFrac = classFrac*gradePoints';
[Ftilt, theta] = tiltFrac(classFrac, gradePoints, 3.7);

p1 = classFrac(:,1);
p12 = classFrac(:,1) + classFrac(:,2);
p12t = Ftilt(:,1) + Ftilt(:,2);

fprintf('Mean historical class average: %.4f\n', avgHist);
fprintf('Scaling factor k = 3.7/%.4f = %.4f\n', avgHist, kScale);
fprintf('Max |table average - fraction implied average|: %.2e\n', max(abs(avgFromFrac - targetAvgGPA)));
fprintf('Std of class averages: %.4f\n', std(targetAvgGPA));
fprintf('Classes awarding no A+: %d of %d\n', sum(p1 == 0), M);
fprintf('Mean A+ share: %.4f   Mean A+ or A share: %.4f\n', mean(p1), mean(p12));
fprintf('Tilt parameter: %.4f   Mean class average after tilt: %.4f\n', theta, mean(Ftilt*gradePoints'));
fprintf('Mean A+ share after tilt: %.4f   Mean A+ or A share after tilt: %.4f\n', mean(Ftilt(:,1)), mean(p12t));

fprintf('\nClass table: name, A+ share, A+ or A share, mean, sd\n');
for c = 1:M
    fprintf('%-28s %.2f %.2f %.3f %.3f\n', classNames{c}, p1(c), p12(c), targetAvgGPA(c), targetStdGPA(c));
end

perfA = perfectStats(p1, rhoGrid, aGrid, phiA, excl);
perfB = perfectStats(p12, rhoGrid, aGrid, phiA, excl);
perfC = perfectStats(p12t, rhoGrid, aGrid, phiA, excl);

mList = [8 16 32];
hitTab = zeros(numel(rhoGrid), numel(mList));
for j = 1:numel(mList)
    for r = 1:numel(rhoGrid)
        hitTab(r,j) = hitRate(rhoGrid(r), mList(j));
    end
end

fprintf('\nrho, Pperf(A+), Pperf(A+ or A) mean, max, Pperf(A+ or A, inflated) mean, max, reliability(m=32), k_a, hit(m=8), hit(m=16), hit(m=32)\n');
for r = 1:numel(rhoGrid)
    rl = relyVal(rhoGrid(r), 32);
    fprintf('%.2f  %.4g  %.4g %.4g  %.4g %.4g  %.4f %.4f  %.4f %.4f %.4f\n', rhoGrid(r), perfA(r,1), perfB(r,1), perfB(r,3), perfC(r,1), perfC(r,3), rl, sqrt(rl), hitTab(r,1), hitTab(r,2), hitTab(r,3));
end

thr = [0.5 0.7 0.8 0.9];
rhoFine = linspace(0.001, 0.99, 990);
hFine = arrayfun(@(x) hitRate(x, 32), rhoFine);
fprintf('\nSmallest rho giving analytic hit rate at least the threshold (m = 32)\n');
for t = 1:numel(thr)
    k = find(hFine >= thr(t), 1, 'first');
    fprintf('threshold %.2f : rho = %.3f\n', thr(t), rhoFine(k));
end

scen = {classFrac, Ftilt};
scenName = {'As collected', 'Inflated to 3.70'};
fprintf('\nSimulation, N = %d, m = %d, reps = %d\n', N, mTaken, reps);
fprintf('scenario, rho, then hit/band/tied for Dean weighted, equal weights, raw GPA (means), then max standard error of hit\n');
for s = 1:2
    for r = 1:numel(rhoSim)
        v = simulate(scen{s}, gradePoints, rhoSim(r), N, mTaken, reps);
        fprintf('%-18s %.1f  %.3f %.1f %.3f  %.3f %.1f %.3f  %.3f %.1f %.3f  se %.4f\n', scenName{s}, rhoSim(r), v(1,1), v(1,2), v(1,3), v(1,4), v(1,5), v(1,6), v(1,7), v(1,8), v(1,9), max(v(2,[1 4 7])));
    end
end

[Gc, ~] = drawGrades(classFrac, gradePoints, 0.6, N, mTaken);
Ra = deanR(Gc, true);
Rb = deanR(kScale*Gc, true);
fprintf('\nScaling check: max |R(kG) - R(G)| = %.2e, students changing decile = %d\n', max(abs(Ra - Rb)), sum(decileOf(Ra) ~= decileOf(Rb)));

function y = Phi(x)
y = 0.5*erfc(-x/sqrt(2));
end

function x = PhiInv(p)
x = -sqrt(2)*erfcinv(2*p);
end

function out = perfectStats(p, rhoGrid, aGrid, phiA, excl)
z = PhiInv(1 - p(:));
zc = find(p(:) == 0);
valid = double(sum(ismember(excl, zc), 2) == numel(zc));
out = zeros(numel(rhoGrid), 4);
for r = 1:numel(rhoGrid)
    rho = rhoGrid(r);
    T = (sqrt(rho)*aGrid - z)/sqrt(1 - rho);
    L = log(max(Phi(T), 1e-300));
    S = sum(L, 1) - L(excl(:,1),:) - L(excl(:,2),:) - L(excl(:,3),:);
    vals = trapz(aGrid, phiA.*exp(S), 2).*valid;
    out(r,:) = [mean(vals) min(vals) max(vals) mean(vals > 0.10)];
end
end

function v = relyVal(rho, m)
v = m*rho/(1 + (m - 1)*rho);
end

function h = hitRate(rho, m)
ka = sqrt(relyVal(rho, m));
z90 = PhiInv(0.9);
if ka >= 1
    h = 1;
else
    a = linspace(z90, 8, 4001);
    ph = exp(-a.^2/2)/sqrt(2*pi);
    h = trapz(a, ph.*(1 - Phi((z90 - ka*a)/sqrt(1 - ka^2))))/0.10;
end
end

function mu = tiltMean(F, gp, th)
W = F.*exp(th*gp);
mu = (W*gp')./sum(W, 2);
end

function [Ft, theta] = tiltFrac(F, gp, target)
theta = fzero(@(th) mean(tiltMean(F, gp, th)) - target, [0 5]);
W = F.*exp(theta*gp);
Ft = W./sum(W, 2);
end

function [G, a] = drawGrades(F, gp, rho, N, m)
M = size(F, 1);
cum = cumsum(F, 2);
cum = cum(:, 1:12);
gpc = gp(:);
a = randn(N, 1);
U = sqrt(rho)*a + sqrt(1 - rho)*randn(N, M);
T = Phi(-U);
G = zeros(N, M);
for c = 1:M
    idx = 1 + sum(T(:,c) >= cum(c,:), 2);
    G(:,c) = gpc(idx);
end
[~, ord] = sort(rand(N, M), 2);
for j = 1:(M - m)
    G(sub2ind([N M], (1:N)', ord(:,j))) = NaN;
end
end

function R = deanR(G, weighted)
gbar = mean(G, 1, 'omitnan');
Rrel = G./gbar;
if weighted
    sc = std(G, 0, 1, 'omitnan');
    mask = ~isnan(G);
    R = sum(Rrel.*sc, 2, 'omitnan')./(mask*sc');
else
    R = mean(Rrel, 2, 'omitnan');
end
end

function D = decileOf(R)
N = numel(R);
d = 1 + sum(R' > R, 2);
D = ceil(10*d/N);
end

function v = scoreOne(R, truth, n10)
N = numel(R);
[~, ord] = sortrows([-R rand(N, 1)]);
chosen = false(N, 1);
chosen(ord(1:n10)) = true;
hit = sum(chosen & truth)/n10;
Rs = sort(R, 'descend');
band = sum(R >= Rs(n10) - 1e-12);
dRs = abs(diff(Rs)) < 1e-12;
tied = [dRs; false] | [false; dRs];
v = [hit band sum(tied)/N];
end

function v = simulate(F, gp, rho, N, m, reps)
n10 = N/10;
res = zeros(reps, 9);
for t = 1:reps
    [G, a] = drawGrades(F, gp, rho, N, m);
    [~, ao] = sort(a, 'descend');
    truth = false(N, 1);
    truth(ao(1:n10)) = true;
    res(t,:) = [scoreOne(deanR(G, true), truth, n10), scoreOne(deanR(G, false), truth, n10), scoreOne(mean(G, 2, 'omitnan'), truth, n10)];
end
v = [mean(res, 1); std(res, 0, 1)/sqrt(reps)];
end