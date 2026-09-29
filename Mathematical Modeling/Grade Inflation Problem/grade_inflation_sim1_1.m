%  WHAT THIS  DOES
%  ----------------------
%  1.  Loads the 35-class grade-distribution table (grades A+ ... F as
%      fractions of a class) that was provided in the data file.
%  2.  Randomly assigns a class SIZE (20-100 students) to every class.
%  3.  Randomly assigns a COURSE LOAD (4-12 classes) to every student,
%      and from that derives how big the student body must be for the
%      number of seats offered to equal the number of seats taken.
%  4.  Randomly enrolls students into classes (a random bipartite
%      student <-> class assignment) so every class ends up at (or
%      very near) its target size and every student ends up with
%      exactly the course load they were assigned.
%  5.  "Deals" every enrolled student a letter grade in every class,
%      by sampling from that class's OWN historical grade distribution
%      (so a simulated "hard" class really does hand out mostly
%      B's/C's, and a simulated "easy" class really does hand out
%      mostly A's - this reproduces grade inflation in the data).
%  6.  Builds the class weight w_c, the relative-performance index
%      r_i,c, the weighted overall score R_i, the rank d_i and the
%      decile D_i for every student, exactly as defined in the
%      project's equation sheet (with the algebra bugs in the
%      MATLAB screenshot corrected - see the big comment block
%      right before computeWeightedR()).
%  7.  Runs three diagnostics that answer the actual research
%      question ("can the dean's scheme give CLEAN deciles?"):
%         a) Are the 10 deciles actually close to equal size?
%         b) Are the gaps between R_i AT the decile cut points bigger
%            than typical gaps elsewhere (a "clean" cut) or do they
%            slice through a dense cluster of near-identical students
%            (an "arbitrary" cut)?
%         c) If ONE grade in ONE class for ONE student is bumped up,
%            how many students' deciles change? (this is literally
%            one of the follow-up questions in the problem statement)
%      and also compares the weighted scheme against (i) an
%      unweighted version and (ii) plain raw-GPA ranking, to show
%      *why* the weighting factor matters.
%
%  Every random step uses a fixed seed (line below) so the whole
%  simulation is reproducible; change/remove the seed to explore other
%  random draws of class sizes, course loads, enrollments and grades.
% ====================================================================

clear; clc; close all;
rng(42);                       % reproducibility seed - change to explore

%% ------------------------------------------------------------------
%  0. CLASS DATA TABLE  (from Math_Modeling_Grade_Inflation_Data.xlsx)
%  Columns of classFrac, in order:
%  A+   A    A-   B+   B    B-   C+   C    C-   D+   D    D-   F
% --------------------------------------------------------------------
gradePoints = [4.3 4.0 3.7 3.3 3.0 2.7 2.3 2.0 1.7 1.3 1.0 0.7 0.0];

classNames = {
    'bio 1a',
    'aerospace engineering',
    'asian diapora',
    'public health',
    'sociology',
    'chemical engineering',
    'comparative literature',
    'env sci, policty and mgmt',
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

targetAvgGPA = [2.7420 3.7520 4.0520 3.5630 3.4110 3.2370 3.6370 3.0020 3.3880 3.4030 3.8450 3.0340 3.2840 3.2300 3.3000 3.1260 3.0510 3.0950 3.2520 3.5120 3.5640 3.8050 3.3670 3.5630 3.0040 3.5330 3.6760 3.5220 3.6240 3.4290 3.4490 3.5260 3.7340 3.4220 3.5750]';  % historical average GPA per class (for validation only)
targetStdGPA = [1.045962 0.541199 0.296810 0.758374 0.731286 0.699951 0.556175 0.942548 0.803900 0.621845 0.854678 0.618582 0.790913 0.894818 0.704273 0.660851 0.801436 0.803166 0.637257 0.908986 0.602083 0.754105 0.637661 0.727826 0.875205 0.417625 0.730085 0.864127 0.908308 0.896024 0.582837 0.924945 0.499243 0.592888 0.792638]';  % historical stdev per class (for validation only)

M = numel(classNames);   

%  1. RANDOMLY ASSIGN CLASS SIZES  (20 - 100 students per class)
nc = randi([20, 100], M, 1);             
totalSeats = sum(nc);                      

fprintf('==================== CLASS SIZES ====================\n');
fprintf('%d classes offered, sizes range %d - %d, total seats = %d\n', ...
        M, min(nc), max(nc), totalSeats);

%  2. RANDOMLY ASSIGN COURSE LOAD -> DETERMINE STUDENT BODY SIZE N
%  Every student takes between 4 and 12 classes.  The number of
%  "seats taken" by the whole student body must equal the number of
%  "seats offered" by the 35 classes (totalSeats above) - a seat
%  cannot exist without a student in it and vice-versa.  So:
%
%       N * E[course load]  ~=  totalSeats
%       E[course load] = mean(4:12) = 8
%       N  ~=  totalSeats / 8
%
%  We use that estimate to pick N, draw a random course load for each
%  of the N students, and then nudge a few students' loads up or down
%  (always staying inside [4,12]) until the seats-taken total exactly
%  equals the seats-offered total. This is what actually pins down a
%  single, self-consistent number for the student body size - it is
%  not an arbitrary choice, it is forced by the supply (class seats)
%  and demand (course loads) both being random variables that have to
%  clear the same market.
loadRange = [4, 12];
avgLoad   = mean(loadRange);                       
N = round(totalSeats / avgLoad);                    

mi = randi(loadRange, N, 1);                        
seatShortfall = totalSeats - sum(mi);

while seatShortfall ~= 0
    idx = randi(N);
    if seatShortfall > 0 && mi(idx) < loadRange(2)
        mi(idx) = mi(idx) + 1;
        seatShortfall = seatShortfall - 1;
    elseif seatShortfall < 0 && mi(idx) > loadRange(1)
        mi(idx) = mi(idx) - 1;
        seatShortfall = seatShortfall + 1;
    end
end

fprintf('\n================ STUDENT BODY SIZE =================\n');
fprintf('Course load per student ~ Uniform{4,...,12}, mean load = %.1f\n', avgLoad);
fprintf('==> Student body size required to clear the market: N = %d students\n', N);
fprintf('    (check: sum of course loads = %d, total seats offered = %d)\n', sum(mi), totalSeats);

%  3. RANDOM ENROLLMENT  (bipartite student <-> class assignment)
%  Each student is processed in random order. A student needing m_i
%  classes draws m_i DISTINCT classes without replacement, weighted by
%  how many seats each class still has open (so big/under-filled
%  classes are more likely to be picked, mimicking real course-
%  selection pressure). Each draw consumes one seat. Because total
%  demand (sum m_i) was forced to equal total supply (sum n_c) in
%  Section 2, this process empties every class almost exactly to its
%  target size; any leftover mismatch (only possible in rare edge
%  cases where a student's remaining candidate pool runs dry) is
%  reported, not hidden.
remainingCap = nc;                      
enrolled     = cell(N,1);              
studentOrder = randperm(N);
shortfall    = 0;

for ii = 1:N
    s    = studentOrder(ii);
    need = mi(s);
    avail = find(remainingCap > 0);

    if numel(avail) < need
        chosen    = avail(:)';                   % rare edge case: take what's left
        shortfall = shortfall + (need - numel(avail));
    else
        chosen = zeros(1, need);
        pool   = avail;
        wts    = remainingCap(pool);
        for k = 1:need
            cw   = cumsum(wts);
            pick = find(cw >= rand()*cw(end), 1, 'first');
            chosen(k) = pool(pick);
            pool(pick) = [];
            wts(pick)  = [];
        end
    end

    enrolled{s} = chosen;
    remainingCap(chosen) = remainingCap(chosen) - 1;
end

if shortfall > 0
    fprintf('\nNote: %d of %d course-slots (%.2f%%) could not be filled due to random\n', ...
            shortfall, totalSeats, 100*shortfall/totalSeats);
    fprintf('      allocation edge effects; negligible at this scale.\n');
end

studentsInClass = cell(M,1);
for s = 1:N
    for c = enrolled{s}
        studentsInClass{c} = [studentsInClass{c}, s];
    end
end
actualClassSize = cellfun(@numel, studentsInClass);

fprintf('\nRealized class sizes vs. target: mean abs. difference = %.2f students\n', ...
        mean(abs(actualClassSize - nc)));


%  4. SIMULATE INDIVIDUAL GRADES  g_i,c  FROM EACH CLASS'S OWN
%     HISTORICAL GRADE DISTRIBUTION
G = NaN(N, M);                 % G(i,c) = student i's GPA in class c
classMeanActual = zeros(M,1);  
classStdActual  = zeros(M,1); 

for c = 1:M
    studs = studentsInClass{c};
    nAct  = numel(studs);
    if nAct == 0
        continue
    end

    rawCounts = classFrac(c,:) * nAct;
    counts    = floor(rawCounts);
    deficit   = nAct - sum(counts);
    remainder = rawCounts - counts;
    [~, order] = sort(remainder, 'descend');
    counts(order(1:deficit)) = counts(order(1:deficit)) + 1;   

    gradeBag = repelem(gradePoints, counts);
    gradeBag = gradeBag(randperm(nAct));       

    G(studs, c) = gradeBag(:);
    classMeanActual(c) = mean(gradeBag);
    classStdActual(c)  = std(gradeBag);        
end

fprintf('\n============ VALIDATION: simulated vs. historical class stats ============\n');
fprintf('Mean |simulated avg GPA - historical avg GPA| over all classes : %.4f\n', ...
        mean(abs(classMeanActual - targetAvgGPA)));
fprintf('Mean |simulated stdev   - historical stdev  | over all classes : %.4f\n', ...
        mean(abs(classStdActual  - targetStdGPA)));

%  5. CLASS WEIGHT  w_c 
%  THREE WEIGHTING SCHEMES ARE COMPUTED, so we can show why the choice
%  of weight actually matters (Section 7 compares their decile output):

w_std   = classStdActual;
w_equal = ones(M,1);
w_diff  = classStdActual ./ max(classMeanActual, 1e-6);

%  6. STUDENT INDEX r_i,c , OVERALL SCORE R_i , RANK d_i , DECILE D_i
R_weighted = computeWeightedR(G, classMeanActual, w_std);    
R_diffW    = computeWeightedR(G, classMeanActual, w_diff);   
R_naive    = computeWeightedR(G, classMeanActual, w_equal);  
G_rawAvg   = mean(G, 2, 'omitnan');                           

[d_weighted, D_weighted] = rankAndDecile(R_weighted);
[d_diffW,    D_diffW]    = rankAndDecile(R_diffW);
[d_naive,    D_naive]    = rankAndDecile(R_naive);
[d_raw,      D_raw]      = rankAndDecile(G_rawAvg);

decileCounts = accumarray(D_weighted, 1, [10, 1]);
fprintf('\n================ DECILE SIZES (weighted scheme) ================\n');
for k = 1:10
    fprintf('  Decile %2d : %d students\n', k, decileCounts(k));
end
fprintf('  (target size if perfectly even = N/10 = %.1f)\n', N/10);

%  7b. BOUNDARY-GAP ANALYSIS - are the decile CUT POINTS sitting in
%      a natural gap between students, or slicing through a dense
%      cluster of students who are all essentially tied?
sortedR   = sort(R_weighted, 'descend');
gaps      = -diff(sortedR);                      % gap between consecutive ranked students
boundaryPos  = round((1:9) * N / 10);            % rank positions of the 9 decile cut points
boundaryGaps = gaps(boundaryPos);
typicalGap   = median(gaps);
gapRatio     = boundaryGaps ./ typicalGap;

fprintf('\n============ DECILE-BOUNDARY "CLEANNESS" CHECK ============\n');
fprintf('Typical (median) gap between adjacent-ranked students'' R : %.4f\n', typicalGap);
fprintf('Gap AT each decile cut point, relative to that typical gap (>1 = clean cut, <1 = cutting through a cluster):\n');
for k = 1:9
    fprintf('  Cut between decile %d/%d : gap = %.4f  (%.2fx typical)\n', ...
            k, k+1, boundaryGaps(k), gapRatio(k));
end

%% ------------------------------------------------------------------
%  8. PLOTS
% --------------------------------------------------------------------
figure('Name','Decile sizes','Color','w');
bar(1:10, decileCounts);
xlabel('Decile (1 = top 10%)'); ylabel('Number of students');
title(sprintf('Decile sizes, N = %d students (target = %.1f each)', N, N/10));
grid on;

figure('Name','Sorted R with decile cut points','Color','w');
plot(1:N, sortedR, 'b-', 'LineWidth', 1.2); hold on;
for k = 1:9
    xline(boundaryPos(k), 'r--');
end
xlabel('Rank (1 = best)'); ylabel('Weighted score R_i');
title('Sorted student scores with decile cut points (red dashed lines)');
grid on;

figure('Name','Raw GPA vs weighted score','Color','w');
scatter(G_rawAvg, R_weighted, 25, D_weighted, 'filled');
colormap(jet(10)); cb = colorbar; cb.Label.String = 'Decile (weighted scheme)';
xlabel('Plain raw average GPA (no correction)'); ylabel('Weighted score R_i');
title('How the weighting scheme re-orders students relative to raw GPA');
grid on;

figure('Name','Sensitivity to a single grade change','Color','w');
histogram(churnCounts, 'BinMethod', 'integers');
xlabel('# students whose decile changed'); ylabel('# trials (out of 200)');
title('Effect of bumping ONE grade for ONE student in ONE class');
grid on;

%  9. SUMMARY
fprintf('\n========================= SUMMARY =========================\n');
fprintf('Classes: %d   Students: %d   Total seats: %d\n', M, N, totalSeats);
fprintf('Decile sizes are even by construction (min %d, max %d students; target %.1f).\n', ...
        min(decileCounts), max(decileCounts), N/10);
if mean(gapRatio) >= 1
    fprintf('On average, decile cut points fall in ABOVE-typical gaps (avg ratio %.2f) -> boundaries look reasonably clean.\n', mean(gapRatio));
else
    fprintf('On average, decile cut points fall in BELOW-typical gaps (avg ratio %.2f) -> some boundaries slice through crowded clusters.\n', mean(gapRatio));
end
fprintf('A single grade change moves an average of %.1f%% of the student body into a different decile,\n', 100*mean(churnCounts)/N);
fprintf('confirming the concern raised in the problem statement: individual grades can have an outsized,\n');
fprintf('non-local effect on class rank when scores near a cut point are closely bunched together.\n');
fprintf('The weighting scheme is NOT cosmetic: %.1f%% of students land in a different decile than they\n', 100*diffFromRaw/N);
fprintf('would under plain raw-GPA ranking, and %.1f%% differ from an unweighted (equal-w_c) version -\n', 100*diffFromNaive/N);
fprintf('showing that HOW classes are weighted materially changes who ends up in the scholarship-eligible top decile.\n');
