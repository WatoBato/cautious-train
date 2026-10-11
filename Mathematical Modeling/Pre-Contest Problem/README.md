# Triathlon density model

`buildDensitySheet.py` reads `triData.csv` and writes `triDensityModel.xlsx`. Every result in the workbook is a live formula built from our equations (eq. 1 to eq. 14), so changing any blue cell on the Control tab updates every table and graph. The code was written with Claude (Anthropic) from our equations; cite it as AI-assisted code.

The workbook opens in default mode: every category is wave 1, so all groups start at t = 0.

## 1. Build the workbook (only needed if you change the script or data)

1. Put `buildDensitySheet.py` and `triData.csv` in the same folder.
2. In a terminal: `pip install openpyxl`
3. Run `python buildDensitySheet.py`. It prints the athlete count (3217) and saves `triDensityModel.xlsx`.

Settings at the top of the script control how big the grid is (`maxDistRows`, `maxTimeCols`, and so on). The defaults cover deltaX down to 500 m and deltaT down to about 260 s. If you set deltaX or deltaT smaller than that, the Control tab shows a warning; raise the setting in the script and build again.

## 2. Open it in Google Sheets

1. Go to drive.google.com, click New > File upload, pick `triDensityModel.xlsx`.
2. Right-click the file > Open with > Google Sheets.
3. Click File > Save as Google Sheets. Work in the new copy.
4. Wait for the first calculation to finish (the workbook has about 450,000 formulas, so this can take a minute). Later edits recalculate faster.

## 3. Use the Control tab

- **Blue cells** are inputs. **Yellow cells** are placeholder values I had to fill in so the formulas run: `swimWidth`, `cSwim`, `cBike`, `cRun`. They do not come from any source. Replace them with your own values.
- **Start times (eq. 3).** `startMode` is `Default` or `Manual`.
  - Default: waveStart[w] = firstStart + (w - 1) * waveGap.
  - Manual: waveStart[w] = firstStart + offset[w], using the offset column in the wave table.
- **Category → wave table.** Type a wave number (1 to 8) next to each category. Categories with the same number start together. Number waves in start order, because the catch-up check compares wave w+1 with wave w.
- **Results (columns E to G)** update live: roadClose, roadOpen, closureTime with PASS/FAIL (eq. 10), maxLoad with its x and t and the number of cells above 1 (eq. 9), the window peak (eq. 7), and the first wave catch-up time (eq. 13).

## 4. What each tab is, with the equation behind it

| Tab | What it shows | Equation |
|---|---|---|
| Athletes | One row per athlete: seconds, speeds, wave, start, clock times | eq. 1: seconds = 3600·hh + 60·mm + ss. eq. 2: vSwim = dSwim / swim, vBike = dBike / bike, vRun = dRun / run. Data check flags rows where swim + t1 + bike + t2 + run differs from finalTime by more than 2 s (none do). eq. 4: swimEnd = start + swim, bikeStart = swimEnd + t1, bikeEnd = bikeStart + bike, runStart = bikeEnd + t2, finish = runStart + run |
| Positions | d[i](t) for every athlete at every grid time t[k]; blank means not on course | eq. 5, each branch in order: vSwim(t − start), dSwim (in T1), dSwim + vBike(t − bikeStart), dSwim + dBike (in T2), dSwim + dBike + vRun(t − runStart) |
| CountMap | Athletes in each row [x[j], x[j] + deltaX) at each t[k], times scale | eq. 7: count(t) = number with x[j] ≤ d[i](t) < x[j] + deltaX. eq. 12: count · scale, scale = 2000 / n |
| DensityMap | The heat map: rows are distance, columns are time, color is density | eq. 8: D[j][k] = 1000 · count / deltaX (athletes per km) |
| LoadMap | Density over the safe limit: white 0, yellow 1, red above 1 | eq. 9: load = D / limit(x[j]); swim rows use densitySwim = count / (deltaX · swimWidth) |
| Window | One rectangle [xStart, xEnd) tracked over time | eq. 6: an athlete is inside when tAt(xStart) ≤ t < tAt(xEnd). eq. 7: densityKm = 1000 · count / deltaX, densitySwim = count / (deltaX · swimWidth) |
| HistFinish | Histogram A: finish clock times, stacked by wave | eq. 13: H[w][b] = athletes in wave w with finish in [b·h, (b+1)·h) |
| HistSpread | Histogram B: where everyone is at t = tStar, stacked by wave | eq. 13: count by d[i](tStar) in bins of deltaX |
| WaveOverlap | Front and tail of each wave over time; flag row = 1 when wave w+1 has caught wave w | eq. 13: front[w](t) = max d, tail[w](t) = min d, catch when front[w+1](t) > tail[w](t). Column B gives the first t, column C gives front[w+1] at that t |
| ShiftDemo | f(x) and f(x − g) side by side | eq. 14. Each athlete's d(t) uses (t − start), so the wave start plays the role of g |
| RawData | The dataset as given | — |

Three things to know when reading the maps:

- The grid rows use x[j] = j · deltaX, so with deltaX = 500 m the rows line up with T1 (1500 m) and T2 (41,500 m). With deltaX = 1000 m, one row would hold both swimmers and cyclists.
- Transitions have no length (our definition), so everyone in T1 sits at exactly x = 1500. Because the count uses x[j] ≤ d < x[j] + deltaX, they land in the row that starts at 1500 m (the first bike row). The same happens at 41,500 m for T2.
- The board example window (0.5 mi to 1 mi) runs past 1500 m, so it holds swimmers, athletes in T1, and cyclists at once.

## 5. Set up the graphs in Google Sheets

### Density heat map (DensityMap and LoadMap)

Sheets has no heat map chart, so the grid itself is the graph. The color scale comes already applied. If it is missing after import:

1. Open the DensityMap tab and select `D4:CY107`.
2. Click Format > Conditional formatting.
3. In the panel, click the **Color scale** tab.
4. Set Minpoint = Min value, white. Midpoint = Percentile 50, yellow. Maxpoint = Max value, red.
5. Click Done.
6. Repeat on LoadMap with the same range, but set Midpoint = **Number**, value **1**, yellow, and Minpoint = Number 0, white. Now any red cell is over the safe limit.

Optional, to see more of the map at once: select columns D to CY, right-click > Resize columns > 40 pixels.

How to read it: each row is a 500 m strip of course (row label in column B, segment in column C), each column is one moment (clock in row 2). A diagonal band of color is the field moving down the course. A steeper band means faster travel. Starting waves later shifts their band to the right (eq. 14).

### Single-window density over time (Window tab)

1. Open the Window tab. Select `C3:C603`, then hold Cmd (Mac) or Ctrl and select `E3:E603`.
2. Click Insert > Chart.
3. In the Chart editor > Setup, set Chart type = **Line chart**. Check "Use row 3 as headers" and "Use column C as labels".
4. For swimmers per m², use column F in place of E.

### Histogram A: finish times by wave (HistFinish tab)

1. Select `C3:K153` (bin label plus waves 1 to 8).
2. Click Insert > Chart.
3. Setup > Chart type = **Stacked column chart**.
4. Check "Use row 3 as headers" and "Use column C as labels".
5. Customize > Chart style: set Column gap or bar width to taste; each wave gets its own color.
6. To change the bin width, edit `h` on the Control tab. In default mode only wave 1 has athletes, so the chart is one color until you split categories into waves.

### Histogram B: positions at tStar (HistSpread tab)

1. Select `C3:K107`.
2. Insert > Chart > **Stacked column chart**, headers in row 3, labels in column C (km).
3. Change `tStar` on the Control tab to move the snapshot in time. Overlapping colors in one bin are waves running into each other.

### Wave fronts and tails (WaveOverlap tab)

1. Select `A2:CY2`, then hold Cmd/Ctrl and select `A4:CY19`.
2. Insert > Chart > **Line chart**.
3. In Setup, check "Switch rows / columns" if the lines look wrong, so each front[w] and tail[w] row becomes one line, with row 2 (clock) along the bottom.
4. Where front[w+1] rises above tail[w], wave w+1 has caught wave w.

### Shift demo (ShiftDemo tab)

1. Select `A4:C29`.
2. Insert > Chart > **Line chart**, use column A as labels.
3. Change g in cell B2 and watch the f(x − g) line move right by g.

## 6. Optional smoother map (eq. 8)

Set `includeSmooth = True` at the top of the script and build again. This adds an Arrivals tab (eq. 6 at every grid edge) and a DensitySmooth tab:

Dsmooth[j][k] = 1000 · (sum over i of timeIn[i][j][k]) / (deltaX · deltaT), where timeIn is the overlap of [tAt(x[j]), tAt(x[j] + deltaX)] with [t[k], t[k] + deltaT].

It is off by default because it nearly doubles the formula count and recalculates slowly in Sheets.
