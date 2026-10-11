"""
buildDensitySheet.py
--------------------
Builds a spreadsheet (triDensityModel.xlsx) from the triathlon dataset.
Every number in the workbook that depends on start times, grid size,
thresholds, etc. is a LIVE FORMULA, so you can change any input on the
"Control" tab (in Google Sheets or Excel) and every table and graph updates.

How to run:
    1. Put this file and triData.csv (the dataset exported as CSV) in one folder.
    2. pip install openpyxl
    3. python buildDensitySheet.py
    4. Upload triDensityModel.xlsx to Google Drive and open it with Google Sheets.

Each section below is labeled with the equation number from our prompt
(eq. 1 = units, eq. 2 = speeds, ... eq. 14 = shifting a curve).

Written with Claude (Anthropic) from our own equations.
"""

import csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.worksheet.datavalidation import DataValidation

# ---------------------------------------------------------------------------
# SETTINGS YOU MIGHT CHANGE IN THIS SCRIPT
# (Everything else is changed inside the spreadsheet on the Control tab.)
# ---------------------------------------------------------------------------
inputFile = "triData.csv"
outputFile = "triDensityModel.xlsx"

maxDistRows = 104     # distance rows built in the grid. 104 rows covers 51,500 m when deltaX >= 500 m
maxTimeCols = 100     # time columns built in the grid. 100 columns covers 8.25 h when deltaT = 300 s
maxWindowRows = 600   # time rows in the single-window table. 600 rows covers 10 h at 60 s steps
maxBins = 150         # finish-time histogram bins. 150 bins covers 12.5 h at 300 s bins
maxWaves = 8          # one wave per category at most (8 categories)
includeSmooth = False # True also builds the "smoother option" of eq. 8 (much slower in Sheets)

# Categories exactly as they are spelled in the dataset, with the description from our prompt
categoryList = [
    ("M PRO", "male professional"),
    ("F PRO", "female professional"),
    ("M PREMIER", "male premier"),
    ("F PREMIER", "female premier"),
    ("M OPEN", "male open race"),
    ("F OPEN", "female open race"),
    ("CLY", "open Clydesdale, men over 220 lbs"),
    ("ATH", "open Athena, women over 165 lbs"),
]

# ---------------------------------------------------------------------------
# Styles (just for looks)
# ---------------------------------------------------------------------------
baseFont = Font(name="Arial", size=10)
boldFont = Font(name="Arial", size=10, bold=True)
titleFont = Font(name="Arial", size=14, bold=True)
inputFont = Font(name="Arial", size=10, color="0000FF")         # blue text = you can edit it
linkFont = Font(name="Arial", size=10, color="008000")          # green text = copied from another tab
inputFill = PatternFill("solid", start_color="DDEBF7")          # light blue = input cell
placeholderFill = PatternFill("solid", start_color="FFFF00")    # yellow = placeholder value, replace it
resultFill = PatternFill("solid", start_color="E2EFDA")         # light green = key result
headerFill = PatternFill("solid", start_color="D9D9D9")


# ---------------------------------------------------------------------------
# eq. 1: convert hh:mm:ss to seconds -> seconds = 3600*hh + 60*mm + ss
# ---------------------------------------------------------------------------
def hmsToSeconds(timeText):
    parts = timeText.strip().split(":")
    hh = int(parts[0])
    mm = int(parts[1])
    ss = int(parts[2])
    return 3600 * hh + 60 * mm + ss


# ---------------------------------------------------------------------------
# Read the dataset (only the 10 columns we use; skip blank and summary rows)
# ---------------------------------------------------------------------------
athleteRows = []
with open(inputFile, newline="") as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if len(row) < 10 or row[0].strip() == "":
            continue  # blank row or the max/min/stdev rows at the bottom
        athleteRows.append(row[:10])

n = len(athleteRows)          # number of athletes
firstRow = 2                  # athlete data starts on row 2 of the athlete tabs
lastRow = n + 1               # and ends here
print("Athletes read:", n)


# ---------------------------------------------------------------------------
# Small helper functions for writing cells
# ---------------------------------------------------------------------------
def setCell(sheet, cellRef, value, font=baseFont, fill=None, numberFormat=None):
    cell = sheet[cellRef]
    cell.value = value
    cell.font = font
    if fill is not None:
        cell.fill = fill
    if numberFormat is not None:
        cell.number_format = numberFormat
    return cell


def addName(workbook, name, sheetName, cellRef):
    # A named range lets formulas say "dSwim" instead of "Control!$B$5"
    col = "".join(ch for ch in cellRef if ch.isalpha())
    rowNum = "".join(ch for ch in cellRef if ch.isdigit())
    workbook.defined_names[name] = DefinedName(name, attr_text=f"{sheetName}!${col}${rowNum}")


def addRangeName(workbook, name, sheetName, firstRef, lastRef):
    def absolute(ref):
        col = "".join(ch for ch in ref if ch.isalpha())
        rowNum = "".join(ch for ch in ref if ch.isdigit())
        return f"${col}${rowNum}"
    workbook.defined_names[name] = DefinedName(
        name, attr_text=f"{sheetName}!{absolute(firstRef)}:{absolute(lastRef)}")


def clockFormula(secondsRef):
    # shows seconds as h:mm:ss text (blank or text like "never" shows blank)
    return f'=IF(ISNUMBER({secondsRef}),TEXT({secondsRef}/86400,"[h]:mm:ss"),"")'


wb = Workbook()

# Tab order: Guide first, then Control, then everything else
guide = wb.active
guide.title = "Guide"
control = wb.create_sheet("Control")
athletes = wb.create_sheet("Athletes")
positions = wb.create_sheet("Positions")
countMap = wb.create_sheet("CountMap")
densityMap = wb.create_sheet("DensityMap")
loadMap = wb.create_sheet("LoadMap")
window = wb.create_sheet("Window")
histFinish = wb.create_sheet("HistFinish")
histSpread = wb.create_sheet("HistSpread")
waveOverlap = wb.create_sheet("WaveOverlap")
shiftDemo = wb.create_sheet("ShiftDemo")
rawData = wb.create_sheet("RawData")


# ===========================================================================
# CONTROL TAB: all inputs (column A-C) and key results (columns E-H)
# ===========================================================================
setCell(control, "A1", "Control panel: change blue cells, everything else updates", titleFont)
setCell(control, "A2", "Blue = input.  Yellow = placeholder value (not from any source), replace with your own.", baseFont)
control.column_dimensions["A"].width = 34
control.column_dimensions["B"].width = 14
control.column_dimensions["C"].width = 58
control.column_dimensions["E"].width = 30
control.column_dimensions["F"].width = 16
control.column_dimensions["G"].width = 16
control.column_dimensions["H"].width = 16
control.column_dimensions["I"].width = 14

controlRow = 4  # next free row in columns A-C


def addSection(title):
    global controlRow
    controlRow += 1
    setCell(control, f"A{controlRow}", title, boldFont, headerFill)
    setCell(control, f"B{controlRow}", "value", boldFont, headerFill)
    setCell(control, f"C{controlRow}", "note", boldFont, headerFill)
    controlRow += 1


def addInput(label, name, value, note, isPlaceholder=False, numberFormat=None):
    """One labeled input cell. It also becomes a named range."""
    global controlRow
    setCell(control, f"A{controlRow}", label)
    fill = placeholderFill if isPlaceholder else inputFill
    setCell(control, f"B{controlRow}", value, inputFont, fill, numberFormat)
    setCell(control, f"C{controlRow}", note)
    addName(wb, name, "Control", f"B{controlRow}")
    controlRow += 1


def addFormula(label, name, formula, note, numberFormat=None):
    """One labeled formula cell (not an input). Also becomes a named range."""
    global controlRow
    setCell(control, f"A{controlRow}", label)
    setCell(control, f"B{controlRow}", formula, baseFont, None, numberFormat)
    setCell(control, f"C{controlRow}", note)
    addName(wb, name, "Control", f"B{controlRow}")
    controlRow += 1


# ---- eq. 1: course lengths --------------------------------------------------
addSection("COURSE (eq. 1), meters")
addInput("dSwim (m)", "dSwim", 1500, "swim length")
addInput("dBike (m)", "dBike", 40000, "bike length")
addInput("dRun (m)", "dRun", 10000, "run length")
addFormula("dTotal (m)", "dTotal", "=dSwim+dBike+dRun", "dTotal = dSwim + dBike + dRun")

# ---- eq. 3: wave start inputs -----------------------------------------------
addSection("START TIMES (eq. 3), seconds")
addInput("firstStart (s)", "firstStart", 0, "clock time of the first wave; t = 0 is the first start")
addInput("waveGap (s)", "waveGap", 300, "Default mode: waveStart[w] = firstStart + (w - 1) * waveGap")
addInput("startMode", "startMode", "Default", "type Default or Manual. Manual uses the offset[w] column in the wave table")
modeCell = f"B{controlRow - 1}"
modeCheck = DataValidation(type="list", formula1='"Default,Manual"', allow_blank=False)
control.add_data_validation(modeCheck)
modeCheck.add(modeCell)

# ---- eq. 8: grid size ---------------------------------------------------------
addSection("DENSITY MAP GRID (eq. 8)")
addInput("deltaX (m)", "deltaX", 500, f"row height in meters. Keep >= {51500 // (maxDistRows - 1) + 1} m or the grid runs out of rows. 500 m lines rows up with T1 (1500 m) and T2 (41500 m)")
addInput("deltaT (s)", "deltaT", 300, f"column width in seconds. The grid has {maxTimeCols} columns")

# ---- eq. 7: one congestion window --------------------------------------------
addSection("CONGESTION WINDOW (eq. 7)")
addInput("xStart (m)", "xStart", 804.67, "board example: 0.5 mi = 804.67 m")
addInput("xEnd (m)", "xEnd", 1609.34, "board example: 1 mi = 1609.34 m (note: this window crosses T1 at 1500 m)")
addInput("window time step (s)", "windowStep", 60, f"time step for the Window tab ({maxWindowRows} rows)")
addInput("report from t (s)", "windowFrom", 3600, "board example: t = 1 h")
addInput("report to t (s)", "windowTo", 5400, "board example: t = 1.5 h")
addInput("swimWidth (m)", "swimWidth", 50, "PLACEHOLDER. Width of the swim course for swimmers per m^2", True)

# ---- eq. 9: thresholds --------------------------------------------------------
addSection("THRESHOLDS (eq. 9)")
addInput("cSwim (per m^2)", "cSwim", 0.5, "PLACEHOLDER. max safe swim density", True)
addInput("cBike (per km)", "cBike", 100, "PLACEHOLDER. max safe bike density", True)
addInput("cRun (per km)", "cRun", 300, "PLACEHOLDER. max safe run density", True)

# ---- eq. 10: road closure -----------------------------------------------------
addSection("ROAD CLOSURE (eq. 10)")
addInput("setupBuffer (s)", "setupBuffer", 0, "roadClose = min bikeStart - setupBuffer")
addInput("closure limit (s)", "closureLimit", 19800, "5.5 h = 19800 s")

# ---- eq. 12: scaling ------------------------------------------------------------
addSection("SCALING TO 2000 ATHLETES (eq. 12)")
addInput("scale counts? (1 = yes, 0 = no)", "scaleOn", 1, "1 multiplies every count by 2000 / n")
addFormula("n (athletes in dataset)", "nAthletes", f"=COUNT(Athletes!$A${firstRow}:$A${lastRow})", "rows in dataset")
addFormula("scale", "scale", "=IF(scaleOn=1,2000/nAthletes,1)", "scale = 2000 / n", "0.0000")

# ---- eq. 13: histogram inputs -----------------------------------------------------
addSection("HISTOGRAMS (eq. 13)")
addInput("h, finish bin width (s)", "binH", 300, f"Histogram A bin width ({maxBins} bins)")
addInput("tStar (s)", "tStar", 3600, "Histogram B: where is everyone at this clock time?")

# ---- results in columns E-H ---------------------------------------------------------
setCell(control, "E5", "RESULTS (update live)", boldFont, headerFill)
setCell(control, "F5", "seconds / value", boldFont, headerFill)
setCell(control, "G5", "h:mm:ss", boldFont, headerFill)

resultRow = 6


def addResult(label, name, formula, showClock=False, numberFormat="0", highlight=False):
    global resultRow
    setCell(control, f"E{resultRow}", label)
    setCell(control, f"F{resultRow}", formula, boldFont if highlight else baseFont,
            resultFill if highlight else None, numberFormat)
    if name:
        addName(wb, name, "Control", f"F{resultRow}")
    if showClock:
        setCell(control, f"G{resultRow}", clockFormula(f"F{resultRow}"))
    resultRow += 1


athleteRange = lambda col: f"Athletes!${col}${firstRow}:${col}${lastRow}"

# eq. 10
addResult("roadClose = min bikeStart - setupBuffer", "roadClose", f"=MIN({athleteRange('S')})-setupBuffer", True)
addResult("roadOpen = max finish", "roadOpen", f"=MAX({athleteRange('V')})", True)
addResult("closureTime = roadOpen - roadClose", "closureTime", "=roadOpen-roadClose", True)
addResult("closureTime <= 19800 s ?", "closurePass", '=IF(closureTime<=closureLimit,"PASS","FAIL")', False, "General", True)
addResult("maxFinish (latest finish clock time)", "maxFinish", f"=MAX({athleteRange('V')})", True)
# eq. 2 data check
addResult("rows failing data check (> 2 s off)", "flagCount", f'=COUNTIF({athleteRange("O")},"CHECK")')
# eq. 9 (filled in after the LoadMap tab exists; addresses fixed here)
maxLoadRow = resultRow
addResult("maxLoad (above 1 = over safe limit)", "maxLoad", "=0", False, "0.00", True)
addResult("  at distance x (m)", None, "=0")
addResult("  at time t (s)", None, "=0", True)
addResult("  cells with load > 1", None, "=0")
# eq. 7 window summary (filled in later)
windowResultRow = resultRow
addResult("window peak density (per km), report range", None, "=0", False, "0.0")
addResult("  at time t (s)", None, "=0", True)
addResult("  window peak swim density (per m^2)", None, "=0", False, "0.000")
# eq. 13 wave catch (filled in later)
catchResultRow = resultRow
addResult("first wave catch-up time (s)", None, "=0", True)
# grid coverage checks
coverageRow = resultRow
addResult("grid time coverage", None,
          f'=IF(firstStart+{maxTimeCols - 1}*deltaT<maxFinish,"Grid ends before last finisher: raise deltaT","OK")', False, "General")
addResult("grid distance coverage", None,
          f'=IF(ROUNDUP(dTotal/deltaX,0)>{maxDistRows},"Grid runs out of rows: raise deltaX","OK")', False, "General")
addResult("window time coverage", None,
          f'=IF(firstStart+{maxWindowRows - 1}*windowStep<maxFinish,"Window table ends early: raise step","OK")', False, "General")

# ---- category -> wave table (eq. 3: which categories share a wave) ---------------
catTop = resultRow + 2
setCell(control, f"E{catTop}", "CATEGORY -> WAVE (eq. 3)", boldFont, headerFill)
setCell(control, f"F{catTop}", "wave number", boldFont, headerFill)
setCell(control, f"G{catTop}", "athletes", boldFont, headerFill)
setCell(control, f"H{catTop}", "description", boldFont, headerFill)
for i, (catName, catDescription) in enumerate(categoryList):
    r = catTop + 1 + i
    setCell(control, f"E{r}", catName)
    setCell(control, f"F{r}", 1, inputFont, inputFill)  # default: everyone in wave 1
    setCell(control, f"G{r}", f'=COUNTIF({athleteRange("D")},E{r})')
    setCell(control, f"H{r}", catDescription)
catFirst = catTop + 1
catLast = catTop + len(categoryList)
addRangeName(wb, "catWaveTable", "Control", f"E{catFirst}", f"F{catLast}")
setCell(control, f"E{catLast + 1}", "Default: every category is wave 1, so all groups start together.")

# ---- wave start table (eq. 3) -------------------------------------------------------
waveTop = catLast + 3
setCell(control, f"E{waveTop}", "WAVE START TIMES (eq. 3)", boldFont, headerFill)
setCell(control, f"F{waveTop}", "offset[w] (s)", boldFont, headerFill)
setCell(control, f"G{waveTop}", "waveStart[w] (s)", boldFont, headerFill)
setCell(control, f"H{waveTop}", "h:mm:ss", boldFont, headerFill)
setCell(control, f"I{waveTop}", "athletes", boldFont, headerFill)
for w in range(1, maxWaves + 1):
    r = waveTop + w
    setCell(control, f"E{r}", w, boldFont)
    setCell(control, f"F{r}", 0, inputFont, inputFill)  # Manual mode offsets
    # Default: firstStart + (w - 1) * waveGap      Manual: firstStart + offset[w]
    setCell(control, f"G{r}", f'=IF(startMode="Manual",firstStart+F{r},firstStart+(E{r}-1)*waveGap)')
    setCell(control, f"H{r}", clockFormula(f"G{r}"))
    setCell(control, f"I{r}", f'=COUNTIF({athleteRange("P")},E{r})')
addRangeName(wb, "waveStartList", "Control", f"G{waveTop + 1}", f"G{waveTop + maxWaves}")
setCell(control, f"E{waveTop + maxWaves + 1}", "Waves are numbered in start order (wave w+1 starts after wave w) for the catch-up check.")


# ===========================================================================
# RAW DATA TAB: the dataset as given (text), for reference only
# ===========================================================================
for c, name in enumerate(header[:10], start=1):
    setCell(rawData, f"{get_column_letter(c)}1", name, boldFont, headerFill)
for i, row in enumerate(athleteRows):
    for c, value in enumerate(row, start=1):
        rawData.cell(row=i + 2, column=c, value=value).font = baseFont


# ===========================================================================
# ATHLETES TAB: one row per athlete (eq. 1, 2, 3, 4, 5 at tStar, 6 at window edges)
# ===========================================================================
athleteHeaders = [
    "BIB", "AGE", "GENDER", "CATEGORY",
    "swim (s)", "t1 (s)", "bike (s)", "t2 (s)", "run (s)", "finalTime (s)",   # A-J  eq. 1
    "vSwim (m/s)", "vBike (m/s)", "vRun (m/s)",                               # K-M  eq. 2
    "sum - finalTime (s)", "data check",                                      # N-O  eq. 2 check
    "wave", "start",                                                          # P-Q  eq. 3
    "swimEnd", "bikeStart", "bikeEnd", "runStart", "finish",                  # R-V  eq. 4
    "d(tStar) (m)",                                                           # W    eq. 5
    "tAt(xStart)", "tAt(xEnd)",                                               # X-Y  eq. 6
]
for c, name in enumerate(athleteHeaders, start=1):
    setCell(athletes, f"{get_column_letter(c)}1", name, boldFont, headerFill)
    athletes.column_dimensions[get_column_letter(c)].width = 12
athletes.freeze_panes = "E2"

for i, row in enumerate(athleteRows):
    r = firstRow + i
    bib, age, gender, category = row[0], row[1], row[2], row[3]
    athletes.cell(row=r, column=1, value=int(bib))
    athletes.cell(row=r, column=2, value=int(age))
    athletes.cell(row=r, column=3, value=gender)
    athletes.cell(row=r, column=4, value=category.strip())
    # eq. 1: hh:mm:ss -> seconds (done here in Python, values written to E-J)
    for c in range(4, 10):
        athletes.cell(row=r, column=c + 1, value=hmsToSeconds(row[c]))

    # eq. 2: constant speeds
    athletes[f"K{r}"] = f"=dSwim/E{r}"
    athletes[f"L{r}"] = f"=dBike/G{r}"
    athletes[f"M{r}"] = f"=dRun/I{r}"
    # eq. 2 data check: swim + t1 + bike + t2 + run = finalTime, flag if off by more than 2 s
    athletes[f"N{r}"] = f"=E{r}+F{r}+G{r}+H{r}+I{r}-J{r}"
    athletes[f"O{r}"] = f'=IF(ABS(N{r})>2,"CHECK","ok")'
    # eq. 3: wave from category, start = waveStart[wave]
    athletes[f"P{r}"] = f"=VLOOKUP(D{r},catWaveTable,2,FALSE)"
    athletes[f"Q{r}"] = f"=INDEX(waveStartList,P{r})"
    # eq. 4: event clock times
    athletes[f"R{r}"] = f"=Q{r}+E{r}"   # swimEnd   = start + swim
    athletes[f"S{r}"] = f"=R{r}+F{r}"   # bikeStart = swimEnd + t1
    athletes[f"T{r}"] = f"=S{r}+G{r}"   # bikeEnd   = bikeStart + bike
    athletes[f"U{r}"] = f"=T{r}+H{r}"   # runStart  = bikeEnd + t2
    athletes[f"V{r}"] = f"=U{r}+I{r}"   # finish    = runStart + run
    # eq. 5: position at t = tStar ("" means not on course)
    athletes[f"W{r}"] = (
        f'=IF(OR(tStar<Q{r},tStar>V{r}),"",'
        f"IF(tStar<R{r},K{r}*(tStar-Q{r}),"
        f"IF(tStar<S{r},dSwim,"
        f"IF(tStar<T{r},dSwim+L{r}*(tStar-S{r}),"
        f"IF(tStar<U{r},dSwim+dBike,"
        f"dSwim+dBike+M{r}*(tStar-U{r}))))))"
    )
    # eq. 6: time the athlete reaches x = xStart and x = xEnd
    for col, xName in (("X", "xStart"), ("Y", "xEnd")):
        athletes[f"{col}{r}"] = (
            f"=IF({xName}<=dSwim,Q{r}+{xName}/K{r},"
            f"IF({xName}<=dSwim+dBike,S{r}+({xName}-dSwim)/L{r},"
            f"U{r}+({xName}-dSwim-dBike)/M{r}))"
        )
    for c in range(1, len(athleteHeaders) + 1):
        athletes.cell(row=r, column=c).font = baseFont
    for col in "KLM":
        athletes[f"{col}{r}"].number_format = "0.000"
    for col in "WXY":
        athletes[f"{col}{r}"].number_format = "0"


# ===========================================================================
# POSITIONS TAB: eq. 5, d[i](t) for every athlete at every grid time t[k]
# ===========================================================================
# Columns A-K copy what eq. 5 needs from the Athletes tab (green text).
positionInfo = [
    ("BIB", "A"), ("wave", "P"), ("start", "Q"), ("swimEnd", "R"), ("bikeStart", "S"),
    ("bikeEnd", "T"), ("runStart", "U"), ("finish", "V"),
    ("vSwim", "K"), ("vBike", "L"), ("vRun", "M"),
]
timeColStart = len(positionInfo) + 1  # column L = first time column

for c, (name, sourceCol) in enumerate(positionInfo, start=1):
    setCell(positions, f"{get_column_letter(c)}1", name, boldFont, headerFill)
    for r in range(firstRow, lastRow + 1):
        cell = positions.cell(row=r, column=c, value=f"=Athletes!{sourceCol}{r}")
        cell.font = linkFont
positions["A1"].value = "BIB  \\  t[k] (s) ->"

for k in range(maxTimeCols):
    col = get_column_letter(timeColStart + k)
    # eq. 8 columns: t[k] = firstStart + k * deltaT, only up to max finish
    setCell(positions, f"{col}1", f'=IF(firstStart+{k}*deltaT<=maxFinish,firstStart+{k}*deltaT,"")', boldFont, headerFill)
    t = f"{col}$1"
    for r in range(firstRow, lastRow + 1):
        # eq. 5, line by line:
        #   not on course                        t < start or t > finish   -> ""
        #   vSwim * (t - start)                  start <= t < swimEnd
        #   dSwim                                swimEnd <= t < bikeStart (T1)
        #   dSwim + vBike * (t - bikeStart)      bikeStart <= t < bikeEnd
        #   dSwim + dBike                        bikeEnd <= t < runStart (T2)
        #   dSwim + dBike + vRun * (t - runStart) runStart <= t <= finish
        positions[f"{col}{r}"] = (
            f'=IF({t}="","",IF(OR({t}<$C{r},{t}>$H{r}),"",'
            f"IF({t}<$D{r},$I{r}*({t}-$C{r}),"
            f"IF({t}<$E{r},dSwim,"
            f"IF({t}<$F{r},dSwim+$J{r}*({t}-$E{r}),"
            f"IF({t}<$G{r},dSwim+dBike,"
            f"dSwim+dBike+$K{r}*({t}-$G{r})))))))"
        )
positions.freeze_panes = positions.cell(row=2, column=timeColStart)


# ===========================================================================
# GRID TABS: CountMap (eq. 7 + 12), DensityMap (eq. 8), LoadMap (eq. 9)
# Rows are distance x[j], columns are time t[k]
# ===========================================================================
gridFirstRow = 4
gridLastRow = gridFirstRow + maxDistRows - 1
gridColStart = 4  # column D = first time column
gridLastCol = get_column_letter(gridColStart + maxTimeCols - 1)
gridFirstCol = get_column_letter(gridColStart)


def setUpGrid(sheet, title):
    setCell(sheet, "A1", title, titleFont)
    setCell(sheet, "A2", "", boldFont)
    setCell(sheet, "C2", "clock ->", boldFont)
    setCell(sheet, "A3", "j", boldFont, headerFill)
    setCell(sheet, "B3", "x[j] (m)", boldFont, headerFill)
    setCell(sheet, "C3", "segment  \\  t[k] (s)", boldFont, headerFill)
    sheet.column_dimensions["C"].width = 18
    for k in range(maxTimeCols):
        col = get_column_letter(gridColStart + k)
        posCol = get_column_letter(timeColStart + k)
        setCell(sheet, f"{col}3", f"=Positions!{posCol}$1", boldFont, headerFill)
        setCell(sheet, f"{col}2", f'=IF({col}3="","",TEXT({col}3/86400,"h:mm"))', boldFont)
        sheet.column_dimensions[col].width = 7
    for j in range(maxDistRows):
        r = gridFirstRow + j
        setCell(sheet, f"A{r}", j)
        # eq. 8 rows: x[j] = j * deltaX (blank once past the finish line)
        setCell(sheet, f"B{r}", f'=IF({j}*deltaX<dTotal,{j}*deltaX,"")')
        # eq. 9 limit(x): which segment the row starts in
        setCell(sheet, f"C{r}", f'=IF(B{r}="","",IF(B{r}<dSwim,"Swim",IF(B{r}<dSwim+dBike,"Bike","Run")))')
    sheet.freeze_panes = f"{gridFirstCol}{gridFirstRow}"


setUpGrid(countMap, "CountMap: scaled count of athletes in [x[j], x[j] + deltaX) at time t[k]  (eq. 7, 12)")
setUpGrid(densityMap, "DensityMap: D[j][k] = 1000 * count / deltaX, athletes per km  (eq. 8)")
setUpGrid(loadMap, "LoadMap: load[j][k] = density / limit(x[j]); above 1 = over safe limit  (eq. 9)")

for j in range(maxDistRows):
    r = gridFirstRow + j
    for k in range(maxTimeCols):
        col = get_column_letter(gridColStart + k)
        posCol = get_column_letter(timeColStart + k)
        posRange = f"Positions!{posCol}${firstRow}:{posCol}${lastRow}"
        blankTest = f'OR($B{r}="",{col}$3="")'
        # eq. 7 + 12: count(t) = athletes with x[j] <= d(t) < x[j] + deltaX, times scale
        countMap[f"{col}{r}"] = (
            f'=IF({blankTest},"",scale*COUNTIFS({posRange},">="&$B{r},{posRange},"<"&($B{r}+deltaX)))'
        )
        # eq. 8: D = 1000 * count / deltaX
        densityMap[f"{col}{r}"] = f'=IF({blankTest},"",1000*CountMap!{col}{r}/deltaX)'
        # eq. 9: load = density / limit. Swim rows use densitySwim = count / (deltaX * swimWidth)
        loadMap[f"{col}{r}"] = (
            f'=IF({blankTest},"",IF($C{r}="Swim",(CountMap!{col}{r}/(deltaX*swimWidth))/cSwim,'
            f'IF($C{r}="Bike",DensityMap!{col}{r}/cBike,DensityMap!{col}{r}/cRun)))'
        )
        countMap[f"{col}{r}"].number_format = "0.0"
        densityMap[f"{col}{r}"].number_format = "0.0"
        loadMap[f"{col}{r}"].number_format = "0.00"

gridRange = f"{gridFirstCol}{gridFirstRow}:{gridLastCol}{gridLastRow}"

# Heat map coloring (Sheets has no heat map chart, so the grid itself is colored)
densityMap.conditional_formatting.add(gridRange, ColorScaleRule(
    start_type="min", start_color="FFFFFF",
    mid_type="percentile", mid_value=50, mid_color="FFEB84",
    end_type="max", end_color="F8696B"))
loadMap.conditional_formatting.add(gridRange, ColorScaleRule(
    start_type="num", start_value=0, start_color="FFFFFF",
    mid_type="num", mid_value=1, mid_color="FFEB84",
    end_type="max", end_color="F8696B"))

# eq. 9 summary: helper column with each row's max, then find maxLoad and where it is
rowMaxCol = get_column_letter(gridColStart + maxTimeCols + 1)
setCell(loadMap, f"{rowMaxCol}3", "row max", boldFont, headerFill)
for j in range(maxDistRows):
    r = gridFirstRow + j
    loadMap[f"{rowMaxCol}{r}"] = f'=IF(COUNT({gridFirstCol}{r}:{gridLastCol}{r})=0,"",MAX({gridFirstCol}{r}:{gridLastCol}{r}))'
rowMaxRange = f"LoadMap!${rowMaxCol}${gridFirstRow}:${rowMaxCol}${gridLastRow}"
loadGrid = f"LoadMap!${gridFirstCol}${gridFirstRow}:${gridLastCol}${gridLastRow}"
loadRowIndex = f"MATCH(maxLoad,{rowMaxRange},0)"
control[f"F{maxLoadRow}"] = f"=MAX({loadGrid})"
control[f"F{maxLoadRow + 1}"] = f"=INDEX(LoadMap!$B${gridFirstRow}:$B${gridLastRow},{loadRowIndex})"
control[f"F{maxLoadRow + 2}"] = (
    f"=INDEX(LoadMap!${gridFirstCol}$3:${gridLastCol}$3,MATCH(maxLoad,INDEX({loadGrid},{loadRowIndex},0),0))"
)
control[f"F{maxLoadRow + 3}"] = f'=COUNTIF({loadGrid},">1")'


# ===========================================================================
# WINDOW TAB: eq. 6 + 7 for one rectangle [xStart, xEnd) over time
# ===========================================================================
setCell(window, "A1", "Window: athletes inside [xStart, xEnd) over time  (eq. 6, 7, 12)", titleFont)
windowHeaders = ["k", "t (s)", "clock", "count(t) (scaled)", "densityKm (per km)",
                 "densitySwim (per m^2)", "densityKm in report range"]
for c, name in enumerate(windowHeaders, start=1):
    setCell(window, f"{get_column_letter(c)}3", name, boldFont, headerFill)
    window.column_dimensions[get_column_letter(c)].width = 16
windowFirstRow = 4
windowLastRow = windowFirstRow + maxWindowRows - 1
for k in range(maxWindowRows):
    r = windowFirstRow + k
    window[f"A{r}"] = k
    window[f"B{r}"] = f'=IF(firstStart+{k}*windowStep<=maxFinish,firstStart+{k}*windowStep,"")'
    window[f"C{r}"] = clockFormula(f"B{r}")
    # eq. 6: inside the window when tAt(xStart) <= t < tAt(xEnd)
    window[f"D{r}"] = (
        f'=IF(B{r}="","",scale*COUNTIFS({athleteRange("X")},"<="&B{r},{athleteRange("Y")},">"&B{r}))'
    )
    # eq. 7: densityKm = 1000 * count / deltaX,  densitySwim = count / (deltaX * swimWidth)
    window[f"E{r}"] = f'=IF(B{r}="","",1000*D{r}/(xEnd-xStart))'
    window[f"F{r}"] = f'=IF(B{r}="","",D{r}/((xEnd-xStart)*swimWidth))'
    window[f"G{r}"] = f'=IF(B{r}="","",IF(AND(B{r}>=windowFrom,B{r}<=windowTo),E{r},""))'
    window[f"D{r}"].number_format = "0.0"
    window[f"E{r}"].number_format = "0.0"
    window[f"F{r}"].number_format = "0.0000"
    window[f"G{r}"].number_format = "0.0"
window.freeze_panes = "A4"

winCol = lambda col: f"Window!${col}${windowFirstRow}:${col}${windowLastRow}"
control[f"F{windowResultRow}"] = f'=IF(COUNT({winCol("G")})=0,"",MAX({winCol("G")}))'
control[f"F{windowResultRow + 1}"] = (
    f'=IF(F{windowResultRow}="","",INDEX({winCol("B")},MATCH(F{windowResultRow},{winCol("G")},0)))'
)
control[f"F{windowResultRow + 2}"] = f'=IF(F{windowResultRow}="","",F{windowResultRow}*(xEnd-xStart)/1000/((xEnd-xStart)*swimWidth))'


# ===========================================================================
# HISTFINISH TAB: eq. 13 Histogram A, finish times by wave
# ===========================================================================
setCell(histFinish, "A1", "Histogram A: finish clock times, bin width h, colored by wave  (eq. 13)", titleFont)
setCell(histFinish, "A3", "bin b", boldFont, headerFill)
setCell(histFinish, "B3", "bin start (s)", boldFont, headerFill)
setCell(histFinish, "C3", "bin label", boldFont, headerFill)
for w in range(1, maxWaves + 1):
    setCell(histFinish, f"{get_column_letter(3 + w)}3", f"wave {w}", boldFont, headerFill)
totalCol = get_column_letter(4 + maxWaves)
setCell(histFinish, f"{totalCol}3", "total", boldFont, headerFill)
for b in range(maxBins):
    r = 4 + b
    histFinish[f"A{r}"] = b
    # only show bins that start at or before the latest finish
    histFinish[f"B{r}"] = f'=IF({b}*binH<=maxFinish,{b}*binH,"")'
    histFinish[f"C{r}"] = f'=IF(B{r}="","",TEXT(B{r}/86400,"h:mm"))'
    for w in range(1, maxWaves + 1):
        col = get_column_letter(3 + w)
        # H[w][b] = athletes in wave w with finish in [b*h, (b+1)*h)
        histFinish[f"{col}{r}"] = (
            f'=IF($B{r}="","",scale*COUNTIFS({athleteRange("P")},{w},'
            f'{athleteRange("V")},">="&$B{r},{athleteRange("V")},"<"&($B{r}+binH)))'
        )
        histFinish[f"{col}{r}"].number_format = "0.0"
    histFinish[f"{totalCol}{r}"] = f'=IF($B{r}="","",SUM(D{r}:{get_column_letter(3 + maxWaves)}{r}))'
    histFinish[f"{totalCol}{r}"].number_format = "0.0"
histFinish.freeze_panes = "D4"


# ===========================================================================
# HISTSPREAD TAB: eq. 13 Histogram B, positions at tStar by wave
# ===========================================================================
setCell(histSpread, "A1", "Histogram B: where athletes are at t = tStar, bins of deltaX, colored by wave  (eq. 13)", titleFont)
setCell(histSpread, "A2", "tStar (s):", boldFont)
setCell(histSpread, "B2", "=tStar", linkFont)
setCell(histSpread, "C2", clockFormula("B2"))
setCell(histSpread, "A3", "j", boldFont, headerFill)
setCell(histSpread, "B3", "x[j] (m)", boldFont, headerFill)
setCell(histSpread, "C3", "bin label (km)", boldFont, headerFill)
for w in range(1, maxWaves + 1):
    setCell(histSpread, f"{get_column_letter(3 + w)}3", f"wave {w}", boldFont, headerFill)
setCell(histSpread, f"{totalCol}3", "total", boldFont, headerFill)
for j in range(maxDistRows):
    r = 4 + j
    histSpread[f"A{r}"] = j
    histSpread[f"B{r}"] = f'=IF({j}*deltaX<dTotal,{j}*deltaX,"")'
    histSpread[f"C{r}"] = f'=IF(B{r}="","",TEXT(B{r}/1000,"0.0"))'
    for w in range(1, maxWaves + 1):
        col = get_column_letter(3 + w)
        # athletes in wave w with x[j] <= d(tStar) < x[j] + deltaX
        histSpread[f"{col}{r}"] = (
            f'=IF($B{r}="","",scale*COUNTIFS({athleteRange("P")},{w},'
            f'{athleteRange("W")},">="&$B{r},{athleteRange("W")},"<"&($B{r}+deltaX)))'
        )
        histSpread[f"{col}{r}"].number_format = "0.0"
    histSpread[f"{totalCol}{r}"] = f'=IF($B{r}="","",SUM(D{r}:{get_column_letter(3 + maxWaves)}{r}))'
    histSpread[f"{totalCol}{r}"].number_format = "0.0"
histSpread.freeze_panes = "D4"


# ===========================================================================
# WAVEOVERLAP TAB: eq. 13 front[w](t), tail[w](t), and catch-up check
# Time runs across the columns, matching the Positions tab
# ===========================================================================
setCell(waveOverlap, "A1", "Wave overlap: front = max d(t) in wave, tail = min d(t) in wave  (eq. 13)", titleFont)
setCell(waveOverlap, "A2", "clock", boldFont)
setCell(waveOverlap, "A3", "t[k] (s)", boldFont, headerFill)
setCell(waveOverlap, "B3", "first t (s)", boldFont, headerFill)
setCell(waveOverlap, "C3", "x there (m)", boldFont, headerFill)
waveOverlap.column_dimensions["A"].width = 26
waveColStart = 4  # column D = first time column
waveIdRange = f"Positions!$B${firstRow}:$B${lastRow}"
frontRow = {}
tailRow = {}
catchRow = {}
for w in range(1, maxWaves + 1):
    frontRow[w] = 3 + w
    tailRow[w] = 3 + maxWaves + w
    setCell(waveOverlap, f"A{frontRow[w]}", f"front[{w}] (m)")
    setCell(waveOverlap, f"A{tailRow[w]}", f"tail[{w}] (m)")
for w in range(1, maxWaves):
    catchRow[w] = 3 + 2 * maxWaves + w
    setCell(waveOverlap, f"A{catchRow[w]}", f"wave {w + 1} catches wave {w}? (1 = yes)", boldFont)

for k in range(maxTimeCols):
    col = get_column_letter(waveColStart + k)
    posCol = get_column_letter(timeColStart + k)
    posRange = f"Positions!{posCol}${firstRow}:{posCol}${lastRow}"
    setCell(waveOverlap, f"{col}3", f"=Positions!{posCol}$1", boldFont, headerFill)
    setCell(waveOverlap, f"{col}2", f'=IF({col}3="","",TEXT({col}3/86400,"h:mm"))', boldFont)
    for w in range(1, maxWaves + 1):
        # how many athletes of wave w are on course right now (blank if none)
        onCourse = f'COUNTIFS({waveIdRange},{w},{posRange},">=0")'
        waveOverlap[f"{col}{frontRow[w]}"] = f'=IF({col}$3="","",IF({onCourse}=0,"",_xlfn.MAXIFS({posRange},{waveIdRange},{w})))'
        waveOverlap[f"{col}{tailRow[w]}"] = f'=IF({col}$3="","",IF({onCourse}=0,"",_xlfn.MINIFS({posRange},{waveIdRange},{w})))'
        waveOverlap[f"{col}{frontRow[w]}"].number_format = "0"
        waveOverlap[f"{col}{tailRow[w]}"].number_format = "0"
    for w in range(1, maxWaves):
        front = f"{col}{frontRow[w + 1]}"
        tail = f"{col}{tailRow[w]}"
        # wave w+1 catches wave w when front[w+1](t) > tail[w](t)
        waveOverlap[f"{col}{catchRow[w]}"] = f'=IF(OR({front}="",{tail}=""),"",IF({front}>{tail},1,0))'

waveFirstCol = get_column_letter(waveColStart)
waveLastCol = get_column_letter(waveColStart + maxTimeCols - 1)
for w in range(1, maxWaves):
    r = catchRow[w]
    catchRange = f"${waveFirstCol}{r}:${waveLastCol}{r}"
    # first time the catch flag is 1, and the front of wave w+1 at that time
    waveOverlap[f"B{r}"] = f'=IFERROR(INDEX(${waveFirstCol}$3:${waveLastCol}$3,MATCH(1,{catchRange},0)),"never")'
    waveOverlap[f"C{r}"] = (
        f'=IFERROR(INDEX(${waveFirstCol}${frontRow[w + 1]}:${waveLastCol}${frontRow[w + 1]},MATCH(1,{catchRange},0)),"")'
    )
    waveOverlap[f"C{r}"].number_format = "0"
waveOverlap.freeze_panes = "D4"
firstCatchRange = f"WaveOverlap!$B${catchRow[1]}:$B${catchRow[maxWaves - 1]}"
control[f"F{catchResultRow}"] = f'=IF(COUNT({firstCatchRange})=0,"never",MIN({firstCatchRange}))'


# ===========================================================================
# SHIFTDEMO TAB: eq. 14, f(t - g) moves a curve right by g
# ===========================================================================
setCell(shiftDemo, "A1", "Shift demo: f(x) and f(x - g)  (eq. 14)", titleFont)
setCell(shiftDemo, "A2", "g =", boldFont)
setCell(shiftDemo, "B2", 1, inputFont, inputFill)
setCell(shiftDemo, "C2", "change g and watch the second curve slide right by g")
setCell(shiftDemo, "A4", "x", boldFont, headerFill)
setCell(shiftDemo, "B4", "f(x) = 4x^3 + 2x^2 + 3x", boldFont, headerFill)
setCell(shiftDemo, "C4", "f(x - g)", boldFont, headerFill)
shiftDemo.column_dimensions["B"].width = 24
shiftDemo.column_dimensions["C"].width = 14
for i in range(25):
    r = 5 + i
    shiftDemo[f"A{r}"] = -3 + 0.25 * i
    shiftDemo[f"B{r}"] = f"=4*A{r}^3+2*A{r}^2+3*A{r}"
    shiftDemo[f"C{r}"] = f"=4*(A{r}-$B$2)^3+2*(A{r}-$B$2)^2+3*(A{r}-$B$2)"


# ===========================================================================
# OPTIONAL: eq. 8 "smoother option" (time spent in each cell, averaged)
# ===========================================================================
if includeSmooth:
    arrivals = wb.create_sheet("Arrivals")
    smooth = wb.create_sheet("DensitySmooth")
    # Arrivals: eq. 6 tAt[i](x) at every grid boundary x = j * deltaX (capped at dTotal)
    setCell(arrivals, "A1", "BIB \\ x (m) ->", boldFont, headerFill)
    arrivalInfo = [("start", "Q"), ("bikeStart", "S"), ("runStart", "U"),
                   ("vSwim", "K"), ("vBike", "L"), ("vRun", "M")]
    for c, (name, sourceCol) in enumerate(arrivalInfo, start=2):
        setCell(arrivals, f"{get_column_letter(c)}1", name, boldFont, headerFill)
    for r in range(firstRow, lastRow + 1):
        arrivals[f"A{r}"] = f"=Athletes!A{r}"
        for c, (name, sourceCol) in enumerate(arrivalInfo, start=2):
            arrivals.cell(row=r, column=c, value=f"=Athletes!{sourceCol}{r}").font = linkFont
    arrColStart = 8  # column H = boundary j = 0
    for j in range(maxDistRows + 1):
        col = get_column_letter(arrColStart + j)
        setCell(arrivals, f"{col}1", f'=IF({j}*deltaX-deltaX<dTotal,MIN({j}*deltaX,dTotal),"")', boldFont, headerFill)
        x = f"{col}$1"
        for r in range(firstRow, lastRow + 1):
            arrivals[f"{col}{r}"] = (
                f'=IF({x}="","",IF({x}<=dSwim,$B{r}+{x}/$E{r},'
                f"IF({x}<=dSwim+dBike,$C{r}+({x}-dSwim)/$F{r},"
                f"$D{r}+({x}-dSwim-dBike)/$G{r})))"
            )
    setUpGrid(smooth, "DensitySmooth: 1000 * (sum of time each athlete spends in the cell) / (deltaX * deltaT)  (eq. 8)")
    for j in range(maxDistRows):
        r = gridFirstRow + j
        enterRange = f"Arrivals!{get_column_letter(arrColStart + j)}${firstRow}:{get_column_letter(arrColStart + j)}${lastRow}"
        leaveRange = f"Arrivals!{get_column_letter(arrColStart + j + 1)}${firstRow}:{get_column_letter(arrColStart + j + 1)}${lastRow}"
        for k in range(maxTimeCols):
            col = get_column_letter(gridColStart + k)
            t0 = f"{col}$3"
            t1 = f"({col}$3+deltaT)"
            # overlap of [enter, leave] with [t0, t1] = max(0, min(leave, t1) - max(enter, t0))
            # min(a, b) = (a + b - |a - b|) / 2   and   max(a, b) = (a + b + |a - b|) / 2
            low = f"({enterRange}+{t0}+ABS({enterRange}-{t0}))/2"
            high = f"({leaveRange}+{t1}-ABS({leaveRange}-{t1}))/2"
            gap = f"({high}-{low})"
            smooth[f"{col}{r}"] = (
                f'=IF(OR($B{r}="",{t0}=""),"",1000*scale*SUMPRODUCT(({gap}+ABS({gap}))/2)/(deltaX*deltaT))'
            )
            smooth[f"{col}{r}"].number_format = "0.0"
    smooth.conditional_formatting.add(gridRange, ColorScaleRule(
        start_type="min", start_color="FFFFFF",
        mid_type="percentile", mid_value=50, mid_color="FFEB84",
        end_type="max", end_color="F8696B"))


# ===========================================================================
# GUIDE TAB: what each tab is, and which of our equations it uses
# ===========================================================================
guideRows = [
    ("Tab", "What it shows", "Our equation behind it"),
    ("Control", "Every input (blue) and the key results, including PASS/FAIL for the road closure.",
     "eq. 3: waveStart[w] = firstStart + (w - 1) * waveGap  (Default)   or   firstStart + offset[w]  (Manual)"),
    ("Athletes", "One row per athlete: times in seconds, speeds, wave, start, and event clock times.",
     "eq. 1: seconds = 3600*hh + 60*mm + ss.   eq. 2: vSwim = dSwim / swim, vBike = dBike / bike, vRun = dRun / run.   "
     "eq. 4: swimEnd = start + swim, bikeStart = swimEnd + t1, bikeEnd = bikeStart + bike, runStart = bikeEnd + t2, finish = runStart + run"),
    ("Positions", "Where each athlete is at each grid time t[k]. Blank = not on course.",
     "eq. 5: d[i](t) = vSwim*(t - start) | dSwim | dSwim + vBike*(t - bikeStart) | dSwim + dBike | dSwim + dBike + vRun*(t - runStart)"),
    ("CountMap", "How many athletes (times scale) sit in each distance row at each time.",
     "eq. 7: count(t) = number with x[j] <= d[i](t) < x[j] + deltaX.   eq. 12: count * scale, scale = 2000 / n"),
    ("DensityMap", "The density heat map. Rows = distance, columns = time, color = density.",
     "eq. 8: D[j][k] = 1000 * count / deltaX  (athletes per km)"),
    ("LoadMap", "Density divided by the safe limit. White = 0, yellow = 1 (at the limit), red = above.",
     "eq. 9: load = D / limit(x[j]); swim rows use densitySwim = count / (deltaX * swimWidth)"),
    ("Window", "One congestion rectangle [xStart, xEnd) tracked over time. Chart density against clock.",
     "eq. 6: inside when tAt(xStart) <= t < tAt(xEnd).   eq. 7: densityKm = 1000 * count / deltaX"),
    ("HistFinish", "Histogram A: finish times stacked by wave.",
     "eq. 13: H[w][b] = athletes in wave w with finish in [b*h, (b+1)*h)"),
    ("HistSpread", "Histogram B: where everyone is at t = tStar, stacked by wave.",
     "eq. 13: count by d[i](tStar) in bins of deltaX"),
    ("WaveOverlap", "Front and tail of each wave over time, and when a later wave catches an earlier one.",
     "eq. 13: front[w](t) = max d, tail[w](t) = min d; catch when front[w+1](t) > tail[w](t)"),
    ("ShiftDemo", "A small example of moving a curve right by g.",
     "eq. 14: f(t - g). Every athlete's d(t) uses (t - start), so start acts as g"),
    ("RawData", "The dataset exactly as given (text), for reference.", "-"),
]
if includeSmooth:
    guideRows.insert(7, ("DensitySmooth", "Same map, averaged over each whole cell instead of one instant.",
                         "eq. 8: Dsmooth = 1000 * (sum of timeIn) / (deltaX * deltaT)"))
setCell(guide, "A1", "Triathlon density model: tab guide", titleFont)
setCell(guide, "A2", "Built by buildDensitySheet.py from our equations. See README.md for chart setup steps in Google Sheets.")
for i, (tab, what, eq) in enumerate(guideRows):
    r = 4 + i
    font = boldFont if i == 0 else baseFont
    fill = headerFill if i == 0 else None
    setCell(guide, f"A{r}", tab, boldFont if i > 0 else font, fill)
    setCell(guide, f"B{r}", what, font, fill)
    setCell(guide, f"C{r}", eq, font, fill)
    for col in "BC":
        guide[f"{col}{r}"].alignment = Alignment(wrap_text=True, vertical="top")
    guide[f"A{r}"].alignment = Alignment(vertical="top")
guide.column_dimensions["A"].width = 14
guide.column_dimensions["B"].width = 55
guide.column_dimensions["C"].width = 90

wb.save(outputFile)
print("Saved", outputFile)
