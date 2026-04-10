#!/usr/bin/env python3
"""
refactor.py — Splits the monolithic huerto-dashboard index.html into
separate CSS + JS module files.

Usage:
    python refactor.py

Output structure:
    assets/css/style.css
    assets/js/config.js
    assets/js/supabase.js
    assets/js/sensors.js
    assets/js/beds.js
    assets/js/bitacora.js
    assets/js/notifications.js
    assets/js/ui.js
    assets/js/app.js
    index.html  (rewritten — links to the above files)
"""

import os
import re
import subprocess
import sys

# ── Paths ────────────────────────────────────────────────────────────────────
BASE    = os.path.dirname(os.path.abspath(__file__))
SRC     = os.path.join(BASE, 'index.html')
CSS_DIR = os.path.join(BASE, 'assets', 'css')
JS_DIR  = os.path.join(BASE, 'assets', 'js')
DUP     = os.path.join(BASE, 'huerto-dashboard.html')

os.makedirs(CSS_DIR, exist_ok=True)
os.makedirs(JS_DIR,  exist_ok=True)

# ── Read source ───────────────────────────────────────────────────────────────
with open(SRC, 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Extract CSS ────────────────────────────────────────────────────────────
css_match = re.search(r'<style>(.*?)</style>', html, re.DOTALL)
if not css_match:
    sys.exit('ERROR: Could not find <style> block.')
css_content = css_match.group(1)
# Strip leading/trailing blank lines
css_content = css_content.strip('\n')

# ── 2. Extract HTML body (between <body> and <script>) ───────────────────────
body_match = re.search(r'<body>(.*?)<script>', html, re.DOTALL)
if not body_match:
    sys.exit('ERROR: Could not find body section.')
body_html = body_match.group(1)

# ── 3. Extract raw JS block ───────────────────────────────────────────────────
js_match = re.search(r"<script>\s*'use strict';(.*?)</script>\s*</body>", html, re.DOTALL)
if not js_match:
    sys.exit('ERROR: Could not find <script> block.')
raw_js = js_match.group(1)  # everything after 'use strict';

# ── Helper: write file ────────────────────────────────────────────────────────
def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'  wrote {os.path.relpath(path, BASE)}')

# ── Helper: validate JS with Node ────────────────────────────────────────────
def validate_js(path):
    rel = os.path.relpath(path, BASE)
    try:
        result = subprocess.run(
            ['node', '-e', f"new Function(require('fs').readFileSync({repr(path)},'utf8'))"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print(f'  [OK]  {rel}')
        else:
            print(f'  [ERR] {rel}: {result.stderr.strip()[:200]}')
    except FileNotFoundError:
        print(f'  [SKIP] node not found — skipping syntax check for {rel}')
    except subprocess.TimeoutExpired:
        print(f'  [SKIP] timeout checking {rel}')

# ─────────────────────────────────────────────────────────────────────────────
# SPLIT JS INTO SECTIONS
#
# Strategy: locate known boundary comments / declarations to find where each
# section starts/ends, then slice the raw_js string accordingly.
# We identify boundary markers by their leading comment blocks.
# ─────────────────────────────────────────────────────────────────────────────

# We'll build each JS file as a list of "chunks" (substrings of raw_js).
# chunk boundaries are character offsets into raw_js.

def find(pattern, text, start=0, flags=re.DOTALL):
    m = re.search(pattern, text[start:], flags)
    if m:
        return start + m.start(), start + m.end()
    return None, None

# Locate key positions in raw_js for splitting
def pos(pattern, flags=re.DOTALL):
    """Return start offset of first match of pattern in raw_js."""
    m = re.search(pattern, raw_js, flags)
    if m:
        return m.start()
    return None

# ── Locate major section boundaries ──────────────────────────────────────────
#
# The JS has clearly labeled sections with comments like:
#   /* ──────  PLANT CATALOG  ────── */
#
# We identify start positions of logical groups:

p_plant_catalog     = pos(r'/\*\s*─+\s*PLANT CATALOG')
p_supabase          = pos(r'/\*\s*─+\s*SUPABASE BACKEND')
p_default_sensor    = pos(r'/\*\* Default physical sensor placement \*/')
p_load_sensor       = pos(r'function loadSensorAssignments\(\)')
p_config            = pos(r'/\*\s*─+\s*CONFIG\s*─+\s*\*/')
p_state             = pos(r'/\*\s*─+\s*STATE\s*─+\s*\*/')
p_utils             = pos(r'/\*\s*─+\s*UTILS\s*─+\s*\*/')
p_fetch_realtime    = pos(r'/\*\s*─+\s*API FETCH: REAL-TIME')
p_fetch_history     = pos(r'/\*\s*─+\s*API FETCH: HISTORY')
p_update_statusdot  = pos(r'/\*\s*─+\s*UPDATE: STATUS DOT')
p_update_kpi        = pos(r'/\*\s*─+\s*UPDATE: KPI CARDS')
p_update_soil       = pos(r'/\*\s*─+\s*UPDATE: SOIL CHANNELS')
p_check_alerts      = pos(r'/\*\s*─+\s*CHECK: IRRIGATION ALERTS')
p_update_clima      = pos(r'/\*\s*─+\s*UPDATE: CLIMA COMPLETO')
p_update_rain       = pos(r'/\*\s*─+\s*UPDATE: RAIN SECTION')
p_update_battery    = pos(r'/\*\s*─+\s*UPDATE: BATTERY TABLE')
p_update_bedmap     = pos(r'/\*\s*─+\s*UPDATE: BED MAP')
p_lastApiData       = pos(r'// Cache for last raw API data')
p_update_notif      = pos(r'/\*\s*─+\s*UPDATE: NOTIFICATIONS')
p_update_history    = pos(r'/\*\s*─+\s*UPDATE: HISTORY CHART')
p_main_update       = pos(r'/\*\s*─+\s*MAIN UPDATE DASHBOARD')
p_countdown         = pos(r'/\*\s*─+\s*COUNTDOWN TIMER')
p_refresh_btn       = pos(r'/\*\s*─+\s*REFRESH BUTTON SPIN')
p_load_realtime     = pos(r'/\*\s*─+\s*LOAD REALTIME DATA')
p_load_history_fn   = pos(r'/\*\s*─+\s*LOAD HISTORY DATA')
p_manual_refresh    = pos(r'/\*\s*─+\s*MANUAL REFRESH')
p_browser_notif     = pos(r'/\*\s*─+\s*BROWSER PUSH NOTIFICATIONS')
p_dom_helpers       = pos(r'/\*\s*─+\s*DOM HELPERS')
p_plant_modal_state = pos(r'/\*\s*─+\s*PLANT MODAL STATE')
p_companionship     = pos(r'/\*\s*─+\s*COMP[AÑ]ERISMO DE CULTIVOS')
p_plant_tooltip     = pos(r'/\*\s*─+\s*PLANT TOOLTIP')
p_init_comment      = pos(r'/\*\s*─+\s*INIT\s*─+\s*\*/\s*/\*\s*─+\s*GLOSSARY')
p_glossary          = pos(r'/\*\s*─+\s*GLOSSARY\s*─+\s*\*/')
p_asistente         = pos(r'/\*\s*─+\s*ASISTENTE DE CULTIVO')
p_bitacora          = pos(r'/\*\s*─+\s*BITACORA DE CULTIVO')
p_init_fn           = pos(r'\s+async function init\(\)')
p_init_call         = pos(r'\s+// Kick off\s+init\(\);')

# Print found positions for debugging
sections = {
    'PLANT_CATALOG':    p_plant_catalog,
    'SUPABASE':         p_supabase,
    'DEFAULT_SENSOR':   p_default_sensor,
    'LOAD_SENSOR':      p_load_sensor,
    'CONFIG':           p_config,
    'STATE':            p_state,
    'UTILS':            p_utils,
    'FETCH_REALTIME':   p_fetch_realtime,
    'FETCH_HISTORY':    p_fetch_history,
    'UPDATE_STATUSDOT': p_update_statusdot,
    'UPDATE_KPI':       p_update_kpi,
    'UPDATE_SOIL':      p_update_soil,
    'CHECK_ALERTS':     p_check_alerts,
    'UPDATE_CLIMA':     p_update_clima,
    'UPDATE_RAIN':      p_update_rain,
    'UPDATE_BATTERY':   p_update_battery,
    'UPDATE_BEDMAP':    p_update_bedmap,
    'LAST_API_DATA':    p_lastApiData,
    'UPDATE_NOTIF':     p_update_notif,
    'UPDATE_HISTORY':   p_update_history,
    'MAIN_UPDATE':      p_main_update,
    'COUNTDOWN':        p_countdown,
    'REFRESH_BTN':      p_refresh_btn,
    'LOAD_REALTIME':    p_load_realtime,
    'LOAD_HISTORY_FN':  p_load_history_fn,
    'MANUAL_REFRESH':   p_manual_refresh,
    'BROWSER_NOTIF':    p_browser_notif,
    'DOM_HELPERS':      p_dom_helpers,
    'PLANT_MODAL':      p_plant_modal_state,
    'COMPANIONSHIP':    p_companionship,
    'PLANT_TOOLTIP':    p_plant_tooltip,
    'INIT_COMMENT':     p_init_comment,
    'GLOSSARY':         p_glossary,
    'ASISTENTE':        p_asistente,
    'BITACORA':         p_bitacora,
    'INIT_FN':          p_init_fn,
    'INIT_CALL':        p_init_call,
}
missing = [k for k, v in sections.items() if v is None]
if missing:
    print('WARNING: Could not locate these sections (may cause incorrect splitting):')
    for m in missing:
        print(f'  {m}')

# ─────────────────────────────────────────────────────────────────────────────
# BUILD EACH JS FILE
# ─────────────────────────────────────────────────────────────────────────────

def slice_js(start, end=None):
    """Slice raw_js from start to end (or EOF), strip trailing whitespace."""
    chunk = raw_js[start:end] if end is not None else raw_js[start:]
    return chunk.rstrip()

# ─────────────────────────────────────────────────────────────────────────────
# config.js
#   - PLANT_CATALOG, PLANT_ENRICHMENT, FAMILIA_LABELS, BOSQUE_NIEBLA_REGLAS,
#     ANTIFUNGICOS_IDS, PLANT_MAP, DEFAULT_BED_PLANTS, LS_KEY, LS_SENSOR_ASSIGNMENTS,
#     LS_BED_READINGS, DEFAULT_SENSOR_ASSIGNMENTS, CONFIG, SOIL_CHANNELS,
#     BATTERY_SENSOR_NAMES, SENSOR_BED_MAP, CROP_THRESHOLDS, BEDS, GROUP_LABELS
#   - Early TDZ-safe declarations: _lastApiData, notifPermission
# ─────────────────────────────────────────────────────────────────────────────

# config.js spans: PLANT_CATALOG → end of GROUP_LABELS (= start of STATE)
config_raw = slice_js(p_plant_catalog, p_state)

# Replace `const` and `let` → `var` for all cross-file variables in config
# We do targeted replacements to avoid changing local block-scope vars
def make_var(text, names):
    """Replace leading const/let with var for specific variable names."""
    for name in names:
        # Match `const NAME` or `let NAME` at start of a line (with optional leading spaces)
        text = re.sub(
            r'^(\s*)(const|let)(\s+' + re.escape(name) + r'\b)',
            r'\1var\3',
            text,
            flags=re.MULTILINE
        )
    return text

config_vars = [
    'PLANT_CATALOG', 'PLANT_ENRICHMENT', 'FAMILIA_LABELS', 'BOSQUE_NIEBLA_REGLAS',
    'ANTIFUNGICOS_IDS', 'PLANT_MAP', 'DEFAULT_BED_PLANTS',
    'LS_KEY', 'LS_SENSOR_ASSIGNMENTS', 'LS_BED_READINGS',
    'SUPABASE', 'SUPABASE_HEADERS',  # also used in supabase.js
    'DEFAULT_SENSOR_ASSIGNMENTS',
    'CONFIG', 'SOIL_CHANNELS', 'BATTERY_SENSOR_NAMES',
    'SENSOR_BED_MAP', 'CROP_THRESHOLDS', 'BEDS', 'GROUP_LABELS',
]
config_raw = make_var(config_raw, config_vars)

# Also change the STATE vars that need cross-file access
state_section = slice_js(p_state, p_utils)
state_raw = make_var(state_section, ['historyChart', 'countdownSeconds', 'countdownTimer', 'lastDataTimestamp'])

# Combine config + state into config.js
# Add TDZ-safe early declarations at the top
TDZ_DECLARATIONS = """\
  // ── TDZ-safe early declarations (Safari iOS fix) ──────────────────────────
  // Declared here (config.js, first script loaded) so that any reference from
  // any other module never hits a Temporal Dead Zone regardless of parse order.
  var _lastApiData     = null;   // cache of last Ecowitt real-time API response
  var notifPermission  = 'denied'; // browser Notification.permission
  try {
    if (typeof Notification !== 'undefined') {
      notifPermission = Notification.permission || 'denied';
    }
  } catch(e) {}

"""

config_js_content = (
    "'use strict';\n\n"
    + TDZ_DECLARATIONS
    + config_raw.lstrip('\n')
    + '\n\n'
    + state_raw.lstrip('\n')
    + '\n'
)

# ─────────────────────────────────────────────────────────────────────────────
# supabase.js  (SUPABASE object + all supabaseFetch/sync functions)
# ─────────────────────────────────────────────────────────────────────────────

# Supabase section: from SUPABASE_BACKEND comment → DEFAULT_SENSOR_ASSIGNMENTS
supabase_raw = slice_js(p_supabase, p_default_sensor)

supabase_vars = ['SUPABASE', 'SUPABASE_HEADERS']
supabase_raw = make_var(supabase_raw, supabase_vars)

supabase_js_content = "'use strict';\n\n" + supabase_raw.lstrip('\n') + '\n'

# ─────────────────────────────────────────────────────────────────────────────
# sensors.js
#   fetchRealtime, fetchHistory, updateStatusDot, updateKPI, updateSoil,
#   checkAlerts, updateClima, updateRain, updateBattery, updateHistory (chart)
# ─────────────────────────────────────────────────────────────────────────────

# sensors.js: UTILS + FETCH_REALTIME + FETCH_HISTORY + all UPDATE sections up
#             to (but not including) UPDATE_BEDMAP (which is beds.js territory)
sensors_raw = slice_js(p_utils, p_update_bedmap)
sensors_js_content = "'use strict';\n\n" + sensors_raw.lstrip('\n') + '\n'

# ─────────────────────────────────────────────────────────────────────────────
# beds.js
#   updateBedMap, _updateGreenhouseHumidity, _updateGreenhouseSensorSelect,
#   renderGreenhouseCrops, loadSensorAssignments, saveSensorAssignments,
#   loadBedReadings, saveBedReadings, getSensorBed, assignSensorToBed,
#   buildSensorOptions, loadBedPlants, saveBedPlants, BED_PLANTS,
#   buildCropItemHtml, renderBedCard, refreshBedCardsOnly, openPlantModal,
#   closePlantModal, handleOverlayClick, populatePlantDropdown,
#   renderCurrentPlantsList, updateAddButtonState, addPlantToCurrentBed,
#   removePlantFromBed, analyzeBedCompanionship, updateCompanionship,
#   timeAgo, currentEditBedId
#
# Starts at DEFAULT_SENSOR_ASSIGNMENTS (sensor assignments + BED_PLANTS),
# goes through plant tooltip section (exclusive).
# ─────────────────────────────────────────────────────────────────────────────

beds_raw = slice_js(p_default_sensor, p_lastApiData)

# Also grab from _lastApiData up to UPDATE_NOTIFICATIONS
# (_lastApiData and notifPermission are in config.js now; we SKIP those two lines)
# Then grab updateBedMap → end of updateCompanionship + refreshBedCardsOnly

# Actually the split is:
#  beds.js = p_default_sensor → p_update_notif (exclusive)
#  But we need to EXCLUDE the two TDZ declarations that are now in config.js.
#  The block at p_lastApiData contains:
#    let _lastApiData = null;
#    let notifPermission = ...
#  which we handle by already having them in config.js, so we skip them here.

beds_raw_2 = slice_js(p_lastApiData, p_update_notif)

# Remove the two TDZ declarations from beds_raw_2 (they go to config.js instead)
beds_raw_2 = re.sub(
    r'// Cache for last raw API data.*?try \{ if \(typeof Notification.*?\} catch\(e\) \{\}\n',
    '  // (_lastApiData and notifPermission are declared in config.js — Safari iOS TDZ fix)\n',
    beds_raw_2,
    flags=re.DOTALL
)

beds_full_raw = beds_raw.lstrip('\n') + '\n\n' + beds_raw_2.lstrip('\n')

# Change let BED_PLANTS and let currentEditBedId to var
beds_full_raw = make_var(beds_full_raw, ['BED_PLANTS', 'currentEditBedId'])

beds_js_content = "'use strict';\n\n" + beds_full_raw.lstrip('\n') + '\n'

# ─────────────────────────────────────────────────────────────────────────────
# notifications.js
#   notifPermission var (early decl in config.js), requestNotifPermission,
#   sendBrowserNotif, checkBrowserAlerts
# ─────────────────────────────────────────────────────────────────────────────

notif_raw = slice_js(p_browser_notif, p_dom_helpers)
notif_js_content = (
    "'use strict';\n\n"
    "  // notifPermission is declared in config.js (Safari iOS TDZ fix)\n\n"
    + notif_raw.lstrip('\n')
    + '\n'
)

# ─────────────────────────────────────────────────────────────────────────────
# ui.js
#   setText, showError, hideError, formatDatetime (& other utils already in
#   sensors.js? No — formatDatetime and parseVal live in the UTILS section
#   which we put in sensors.js.  We'll move the DOM helpers + glossary +
#   tooltip + updateNotifications + updateRecommendations here).
#
# Sections:
#   DOM_HELPERS → end of PLANT_TOOLTIP
#   GLOSSARY + ASISTENTE (but NOT BITACORA, not INIT)
# ─────────────────────────────────────────────────────────────────────────────

# DOM helpers + plant tooltip
ui_dom_raw      = slice_js(p_dom_helpers, p_plant_modal_state)
ui_tooltip_raw  = slice_js(p_plant_tooltip, p_init_comment or p_glossary)

# Glossary + Asistente (recommendations system)
# These live between INIT comment and BITACORA
if p_init_comment is not None:
    ui_glossary_raw = slice_js(p_init_comment, p_bitacora)
else:
    ui_glossary_raw = slice_js(p_glossary, p_bitacora)

# updateNotifications lives in UPDATE_NOTIF → UPDATE_HISTORY
ui_notif_raw = slice_js(p_update_notif, p_update_history)

# Make _companionMatrix a var so it's accessible
ui_glossary_raw = make_var(ui_glossary_raw, ['_companionMatrix', 'GLOSSARY'])

ui_js_content = (
    "'use strict';\n\n"
    + ui_dom_raw.lstrip('\n')
    + '\n\n'
    + ui_notif_raw.lstrip('\n')
    + '\n\n'
    + ui_tooltip_raw.lstrip('\n')
    + '\n\n'
    + ui_glossary_raw.lstrip('\n')
    + '\n'
)

# ─────────────────────────────────────────────────────────────────────────────
# bitacora.js
#   TIPO_LABELS, bitacoraData, bitacoraChart*, loadBitacora, saveBitacora,
#   populateBitacoraMeses, populateBitacoraModalSelects, openBitacoraModal,
#   closeBitacoraModal, onBitacoraTipoChange, saveBitacoraEntry,
#   deleteBitacoraEntry, getFilteredBitacora, getBedName, getPlantName,
#   renderBitacoraStats, renderBitacoraTable, toggleBitacoraCharts,
#   renderBitacoraCharts, renderBitacora
# ─────────────────────────────────────────────────────────────────────────────

bitacora_raw = slice_js(p_bitacora, p_init_fn)
bitacora_raw = make_var(bitacora_raw, [
    'TIPO_LABELS', 'bitacoraData',
    'bitacoraChartCama', 'bitacoraChartPlanta', 'bitacoraChartTendencia',
])
bitacora_js_content = "'use strict';\n\n" + bitacora_raw.lstrip('\n') + '\n'

# ─────────────────────────────────────────────────────────────────────────────
# app.js  (orchestration — init, loadRealtime, loadHistory, manualRefresh,
#           updateDashboard, startCountdown, setRefreshSpinning, setInterval)
# ─────────────────────────────────────────────────────────────────────────────

# Covers: UPDATE_HISTORY + MAIN_UPDATE + COUNTDOWN + REFRESH_BTN +
#         LOAD_REALTIME + LOAD_HISTORY_FN + MANUAL_REFRESH + INIT_FN + INIT_CALL
#
# NOTE: slice(p_update_history, p_browser_notif) already contains ALL of:
#   updateHistory, updateDashboard, startCountdown, setRefreshSpinning,
#   loadRealtime, loadHistory, manualRefresh — so we just append init().
app_raw = (
    slice_js(p_update_history, p_browser_notif)  # everything up to (not incl.) browser notifs
    + '\n\n'
    + slice_js(p_init_fn)                         # init() + kick off
)

app_js_content = "'use strict';\n\n" + app_raw.lstrip('\n') + '\n'

# ─────────────────────────────────────────────────────────────────────────────
# WRITE CSS
# ─────────────────────────────────────────────────────────────────────────────
write_file(os.path.join(CSS_DIR, 'style.css'), css_content + '\n')

# ─────────────────────────────────────────────────────────────────────────────
# WRITE JS FILES
# ─────────────────────────────────────────────────────────────────────────────
js_files = [
    ('config.js',        config_js_content),
    ('ui.js',            ui_js_content),
    ('supabase.js',      supabase_js_content),
    ('notifications.js', notif_js_content),
    ('sensors.js',       sensors_js_content),
    ('beds.js',          beds_js_content),
    ('bitacora.js',      bitacora_js_content),
    ('app.js',           app_js_content),
]

for fname, content in js_files:
    write_file(os.path.join(JS_DIR, fname), content)

# ─────────────────────────────────────────────────────────────────────────────
# WRITE NEW index.html
# ─────────────────────────────────────────────────────────────────────────────

# Extract <head> content (up to first <style>)
head_match = re.search(r'<head>(.*?)<style>', html, re.DOTALL)
head_content = head_match.group(1) if head_match else ''

script_tags = '\n'.join([
    f'  <script src="assets/js/{fname}"></script>'
    for fname, _ in js_files
])

new_html = f"""<!DOCTYPE html>
<html lang="es">
<head>{head_content}  <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
{body_html.rstrip()}

  <!-- ════════════════════════════════════════
       JAVASCRIPT — modular (split from monolith 2026-04-08)
       Load order matters: config → ui → supabase → notifications
                         → sensors → beds → bitacora → app
  ════════════════════════════════════════ -->
{script_tags}
</body>
</html>
"""

write_file(SRC, new_html)

# ─────────────────────────────────────────────────────────────────────────────
# DELETE DUPLICATE
# ─────────────────────────────────────────────────────────────────────────────
if os.path.exists(DUP):
    os.remove(DUP)
    print(f'  deleted {os.path.relpath(DUP, BASE)}')
else:
    print(f'  (no duplicate file to delete at {os.path.relpath(DUP, BASE)})')

# ─────────────────────────────────────────────────────────────────────────────
# VALIDATE JS FILES
# ─────────────────────────────────────────────────────────────────────────────
print('\nValidating JS syntax with Node.js...')
for fname, _ in js_files:
    validate_js(os.path.join(JS_DIR, fname))

print('\nDone. Check output above for any [ERR] entries.')
