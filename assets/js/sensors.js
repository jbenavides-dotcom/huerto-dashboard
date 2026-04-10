'use strict';

/* ──────────────────────────────────────────
     UTILS
  ────────────────────────────────────────── */

  /**
   * Format a Date to HH:MM (local, Colombia UTC-5).
   * @param {Date} date
   * @returns {string}
   */
  function formatTime(date) {
    return date.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit', hour12: false });
  }

  /**
   * Format a Date to a readable datetime string.
   * @param {Date} date
   * @returns {string}
   */
  function formatDatetime(date) {
    return date.toLocaleString('es-CO', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit',
      hour12: false,
    });
  }

  /**
   * Get a UTC date string for the Ecowitt history API.
   * @param {Date} date - Date object (will be interpreted as local; we shift to UTC manually)
   * @returns {string} "YYYY-MM-DD HH:MM:SS"
   */
  function toApiDateString(date) {
    const pad = n => String(n).padStart(2, '0');
    return `${date.getUTCFullYear()}-${pad(date.getUTCMonth()+1)}-${pad(date.getUTCDate())} ${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}:${pad(date.getUTCSeconds())}`;
  }

  /**
   * Determine soil bar colour from moisture percentage (cloud forest thresholds).
   * @param {number} pct
   * @returns {string}
   */
  function soilColor(pct) {
    if (pct < CONFIG.soilAlertThreshold)  return '#FF4757'; // red — dry
    if (pct < CONFIG.soilOptimalMin)       return '#FFB800'; // yellow — getting dry
    if (pct <= CONFIG.soilOptimalMax)      return '#00D68F'; // green — optimal
    return '#4ECDC4';                                        // blue — very wet
  }

  /**
   * Determine bed card glow class and humidity colour using crop-specific thresholds.
   * @param {number|null} pct
   * @param {string} group
   * @returns {{ glowClass: string, color: string }}
   */
  function bedHumidityStatus(pct, group) {
    if (pct === null) return { glowClass: '', color: 'var(--muted)' };
    const t = CROP_THRESHOLDS[group] || CROP_THRESHOLDS.rotacion;
    if (pct < t.critical)             return { glowClass: 'glow-red',    color: '#FF4757' };
    if (pct < t.alert)                return { glowClass: 'glow-yellow', color: '#FFB800' };
    if (pct >= t.optMin && pct <= t.optMax) return { glowClass: 'glow-green', color: '#00D68F' };
    if (pct > t.optMax)               return { glowClass: 'glow-blue',   color: '#4ECDC4' };
    // between critical and optMin (dry but not alarming)
    return { glowClass: 'glow-yellow', color: '#FFB800' };
  }

  /**
   * Safely parse a numeric value from the API (string | undefined).
   * @param {string|undefined} val
   * @returns {number|null}
   */
  function parseVal(val) {
    const n = parseFloat(val);
    return isNaN(n) ? null : n;
  }

  /**
   * Build the base URL params shared across requests.
   * @returns {string}
   */
  function baseParams() {
    return `application_key=${CONFIG.applicationKey}&api_key=${CONFIG.apiKey}&mac=${encodeURIComponent(CONFIG.mac)}&${CONFIG.unitParams}`;
  }

  /* ──────────────────────────────────────────
     API FETCH: REAL-TIME
  ────────────────────────────────────────── */
  async function fetchRealtime() {
    const url = `${CONFIG.apiBase}/device/real_time?${baseParams()}&call_back=all`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    if (json.code !== 0) throw new Error(`API error: ${json.msg}`);
    return json.data;
  }

  /* ──────────────────────────────────────────
     API FETCH: HISTORY (last 24 h)
  ────────────────────────────────────────── */
  async function fetchHistory() {
    const now   = new Date();
    const start = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    const fields = 'outdoor.temperature,soil_ch1,soil_ch2,soil_ch3,soil_ch4,soil_ch5';
    const url = `${CONFIG.apiBase}/device/history?${baseParams()}&call_back=${fields}&start_date=${encodeURIComponent(toApiDateString(start))}&end_date=${encodeURIComponent(toApiDateString(now))}&cycle_type=5min`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    if (json.code !== 0) throw new Error(`API error: ${json.msg}`);
    return json.data;
  }

  /* ──────────────────────────────────────────
     UPDATE: STATUS DOT
  ────────────────────────────────────────── */
  function updateStatusDot(unixTimestamp) {
    const dot = document.getElementById('statusDot');
    if (!unixTimestamp) { dot.className = 'status-dot'; return; }
    const ageMs = Date.now() - (unixTimestamp * 1000);
    const ageMins = ageMs / 60000;
    if (ageMins < 10)       { dot.className = 'status-dot green'; }
    else if (ageMins < 30)  { dot.className = 'status-dot yellow'; }
    else                    { dot.className = 'status-dot red'; }
  }

  /* ──────────────────────────────────────────
     UPDATE: KPI CARDS
  ────────────────────────────────────────── */
  function updateKPI(data) {
    const outdoor  = data.outdoor  || {};
    const rainfall = data.rainfall || {};
    const pressure = data.pressure || {};

    const tempExt  = parseVal(outdoor.temperature?.value);
    const feelsLike= parseVal(outdoor.feels_like?.value);
    const dewPoint = parseVal(outdoor.dew_point?.value);
    const humExt   = parseVal(outdoor.humidity?.value);
    const pressRel = parseVal(pressure.relative?.value);
    const pressAbs = parseVal(pressure.absolute?.value);
    const rainDay  = parseVal(rainfall.daily?.value);
    const rainRate = parseVal(rainfall.rain_rate?.value);

    setText('kpiTempExt',    tempExt   !== null ? tempExt.toFixed(1)   : '—');
    setText('kpiFeelsLike',  feelsLike !== null ? `Sensación: ${feelsLike.toFixed(1)}°C` : 'Sensación: —');
    setText('kpiHumExt',     humExt    !== null ? Math.round(humExt)   : '—');
    setText('kpiDewPoint',   dewPoint  !== null ? `Rocío: ${dewPoint.toFixed(1)}°C` : 'Rocío: —');
    setText('kpiPressure',   pressRel  !== null ? pressRel.toFixed(1)  : '—');
    setText('kpiAbsPressure',pressAbs  !== null ? `Abs: ${pressAbs.toFixed(1)} hPa` : 'Abs: —');
    setText('kpiRainDay',    rainDay   !== null ? rainDay.toFixed(1)   : '—');
    setText('kpiRainRate',   rainRate  !== null ? `Tasa: ${rainRate.toFixed(1)} mm/hr` : 'Tasa: — mm/hr');
  }

  /* ──────────────────────────────────────────
     UPDATE: SOIL CHANNELS
  ────────────────────────────────────────── */
  function updateSoil(data) {
    const container = document.getElementById('soilChannels');
    container.innerHTML = '';

    const values = [];

    SOIL_CHANNELS.forEach(ch => {
      const raw = data[ch.key]?.soilmoisture?.value;
      const pct = parseVal(raw);
      if (pct === null) return; // skip missing channels
      values.push(pct);

      const adRaw = data[ch.key]?.ad?.value;
      const adVal = adRaw !== undefined && adRaw !== null ? adRaw : null;

      const color = soilColor(pct);
      const widthPct = Math.min(Math.max(pct, 0), 100);

      const adHtml = adVal !== null
        ? `<span class="channel-ad">(AD: ${adVal})</span>`
        : '';

      const row = document.createElement('div');
      row.className = 'channel-row';
      row.innerHTML = `
        <div class="channel-label">${ch.label.split(' — ')[0]}</div>
        <div class="progress-track">
          <div class="progress-fill" style="width:${widthPct}%;background:${color}"></div>
          <div class="threshold-marker dry"  data-label="35%"></div>
          <div class="threshold-marker opt"  data-label="50%"></div>
          <div class="threshold-marker wet"  data-label="80%"></div>
        </div>
        <div class="channel-pct" style="color:${color}">${Math.round(pct)}%${adHtml}</div>
      `;
      container.appendChild(row);
    });

    // Average
    if (values.length > 0) {
      const avg = values.reduce((a, b) => a + b, 0) / values.length;
      const avgEl = document.getElementById('soilAvgValue');
      avgEl.textContent = Math.round(avg) + '%';
      avgEl.style.color = soilColor(avg);
    }

    checkAlerts(data);
  }

  /* ──────────────────────────────────────────
     CHECK: IRRIGATION ALERTS
  ────────────────────────────────────────── */
  function checkAlerts(data) {
    const banner = document.getElementById('alertBanner');
    const items  = document.getElementById('alertItems');
    items.innerHTML = '';

    const sensorAssignments = loadSensorAssignments();
    const needsWater = [];

    // Only alert for beds that have an active sensor assigned
    Object.entries(sensorAssignments).forEach(([bedId, sensorKey]) => {
      if (!sensorKey) return; // no sensor — skip
      const pct = parseVal(data[sensorKey]?.soilmoisture?.value);
      if (pct === null) return;

      // Find the bed group for crop-specific thresholds
      const bed = BEDS.find(b => b.id === bedId);
      const group = bed ? bed.group : (bedId === 'invernadero' ? 'tomate' : 'hojas');
      const t = CROP_THRESHOLDS[group] || CROP_THRESHOLDS.hojas;

      if (pct < t.alert) {
        const chNum = sensorKey.replace('soil_ch', 'CH');
        const bedName = bed ? bed.name : (bedId === 'invernadero' ? 'Invernadero' : bedId);
        needsWater.push({
          label: `${chNum} (${bedName})`,
          pct,
          critical: pct < t.critical,
        });
      }
    });

    if (needsWater.length > 0) {
      needsWater.forEach(({ label, pct, critical }) => {
        const div = document.createElement('div');
        div.className = 'alert-item';
        const icon = critical ? '🚨' : '⚠';
        const msg = critical ? 'riego urgente' : 'necesita riego';
        div.textContent = `${icon} ${label} ${msg} — ${Math.round(pct)}% humedad`;
        items.appendChild(div);
      });
      banner.classList.add('visible');
    } else {
      banner.classList.remove('visible');
    }
  }

  /* ──────────────────────────────────────────
     UPDATE: CLIMA COMPLETO
  ────────────────────────────────────────── */
  function updateClima(data) {
    const outdoor = data.outdoor || {};
    const indoor  = data.indoor  || {};
    const ch1     = data.temp_and_humidity_ch1 || {};

    const fmt = (val, unit) => val !== null ? `${val}${unit}` : '—';

    setText('climaTempExt',   fmt(parseVal(outdoor.temperature?.value), '°C'));
    setText('climaTempInt',   fmt(parseVal(indoor.temperature?.value),  '°C'));
    setText('climaHumExt',    fmt(parseVal(outdoor.humidity?.value),    '%'));
    setText('climaHumInt',    fmt(parseVal(indoor.humidity?.value),     '%'));
    setText('climaDewPoint',  fmt(parseVal(outdoor.dew_point?.value),   '°C'));
    setText('climaFeelsLike', fmt(parseVal(outdoor.feels_like?.value),  '°C'));
    setText('climaTempCh1',   fmt(parseVal(ch1.temperature?.value),     '°C'));
    setText('climaHumCh1',    fmt(parseVal(ch1.humidity?.value),        '%'));
  }

  /* ──────────────────────────────────────────
     UPDATE: RAIN SECTION
  ────────────────────────────────────────── */
  function updateRain(data) {
    const r = data.rainfall || {};
    const fmt = (val, decimals = 1) => val !== null ? val.toFixed(decimals) : '—';

    setText('rainRateValue', fmt(parseVal(r.rain_rate?.value)));
    setText('rain1h',   fmt(parseVal(r['1_hour']?.value)) + ' mm');
    setText('rainDay2', fmt(parseVal(r.daily?.value))    + ' mm');
    setText('rainWeek', fmt(parseVal(r.weekly?.value))   + ' mm');
    setText('rainMonth',fmt(parseVal(r.monthly?.value))  + ' mm');
    setText('rainYear', fmt(parseVal(r.yearly?.value))   + ' mm');
  }

  /* ──────────────────────────────────────────
     UPDATE: BATTERY TABLE
  ────────────────────────────────────────── */
  function updateBattery(data) {
    const battery = data.battery || {};
    const tbody   = document.getElementById('batteryTableBody');
    tbody.innerHTML = '';

    Object.entries(battery).forEach(([key, batt]) => {
      const name  = BATTERY_SENSOR_NAMES[key] || key;
      const unit  = batt.unit;
      const value = parseVal(batt.value);
      if (value === null) return;

      let levelText, badgeClass, icon;

      if (unit === 'V') {
        // Voltage sensor (soil moisture sensors)
        levelText = `${value.toFixed(2)} V`;
        if (value >= 1.4) {
          badgeClass = 'ok';     icon = '●';
        } else if (value >= 1.2) {
          badgeClass = 'medium'; icon = '◑';
        } else {
          badgeClass = 'low';    icon = '○';
        }
      } else {
        // Status code sensor (0 = OK, ≥5 = low)
        levelText = value === 0 ? 'Normal' : `Código ${value}`;
        if (value === 0) {
          badgeClass = 'ok';     icon = '●';
        } else if (value < 5) {
          badgeClass = 'medium'; icon = '◑';
        } else {
          badgeClass = 'low';    icon = '○';
        }
      }

      const statusLabel = { ok: 'Buena', medium: 'Media', low: 'Baja' }[badgeClass];

      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${name}</td>
        <td>${levelText}</td>
        <td><span class="batt-badge ${badgeClass}"><span class="batt-icon">${icon}</span>${statusLabel}</span></td>
      `;
      tbody.appendChild(tr);
    });
  }
