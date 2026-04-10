'use strict';

/* ──────────────────────────────────────────
     DOM HELPERS
  ────────────────────────────────────────── */
  function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  function showError(id, msg) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = msg;
    el.classList.add('visible');
  }

  function hideError(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.remove('visible');
  }

/* ──────────────────────────────────────────
     UPDATE: NOTIFICATIONS
  ────────────────────────────────────────── */

  /**
   * Generate a list of notification objects from real-time sensor data.
   * @param {object} data - Ecowitt real-time API data object
   * @returns {Array<{ severity: string, icon: string, msg: string }>}
   */
  function generateNotifications(data) {
    const notifications = [];
    const now = formatTime(new Date());

    // ── 1. Check soil channels against crop-specific thresholds
    // Only generate alerts for beds that have a sensor actively assigned
    const sensorAssignments = loadSensorAssignments();
    Object.entries(sensorAssignments).forEach(([bedId, sensorKey]) => {
      if (!sensorKey) return; // no sensor assigned to this bed

      const pct = parseVal(data[sensorKey]?.soilmoisture?.value);
      if (pct === null) return;

      const bed = BEDS.find(b => b.id === bedId);
      const group = bed ? bed.group : (bedId === 'invernadero' ? 'tomate' : 'hojas');
      const t = CROP_THRESHOLDS[group] || CROP_THRESHOLDS.rotacion;
      const groupLabel = t.label;
      const chNum = sensorKey.replace('soil_ch', 'CH');
      const bedName = bed ? bed.name : (bedId === 'invernadero' ? 'Invernadero' : bedId);
      const sensorLabel = `${chNum} → ${bedName}`;

      if (pct < t.critical) {
        notifications.push({
          severity: 'critical',
          icon: '🚨',
          msg: `${sensorLabel} (${groupLabel}): Humedad ${Math.round(pct)}% — ¡Riego urgente! (crítico: <${t.critical}%)`,
        });
      } else if (pct < t.alert) {
        notifications.push({
          severity: 'warning',
          icon: '⚠️',
          msg: `${sensorLabel} (${groupLabel}): Humedad ${Math.round(pct)}% — Riego recomendado (aviso: <${t.alert}%)`,
        });
      } else if (pct > t.optMax + 15) {
        notifications.push({
          severity: 'rain',
          icon: '💧',
          msg: `${sensorLabel} (${groupLabel}): Humedad ${Math.round(pct)}% — Suelo saturado, no regar`,
        });
      } else if (pct > t.optMax) {
        notifications.push({
          severity: 'info',
          icon: 'ℹ️',
          msg: `${sensorLabel} (${groupLabel}): Humedad ${Math.round(pct)}% — Sobre el óptimo (máx: ${t.optMax}%), reducir riego`,
        });
      }
    });

    // ── 2. Battery low alerts
    const battery = data.battery || {};
    Object.entries(battery).forEach(([key, batt]) => {
      if (batt.unit !== 'V') return;
      const v = parseVal(batt.value);
      if (v !== null && v < 1.2) {
        const chMatch = key.match(/ch(\d+)/);
        const chLabel = chMatch ? `CH${chMatch[1]}` : key;
        notifications.push({
          severity: 'critical',
          icon: '🔋',
          msg: `Sensor ${chLabel} batería baja: ${v.toFixed(2)}V — Cambiar pila`,
        });
      }
    });

    // ── 3. Rain active
    const rainRate = parseVal(data.rainfall?.rain_rate?.value);
    if (rainRate !== null && rainRate > 0) {
      notifications.push({
        severity: 'rain',
        icon: '🌧️',
        msg: `Lluvia activa: ${rainRate.toFixed(1)} mm/hr — Suspender riego manual`,
      });
    }

    // ── 4. Low temperature alert
    const tempExt = parseVal(data.outdoor?.temperature?.value);
    if (tempExt !== null && tempExt < 8) {
      notifications.push({
        severity: 'warning',
        icon: '🥶',
        msg: `Temperatura ${tempExt.toFixed(1)}°C — Proteger cultivos sensibles`,
      });
    }

    // ── 5. All good fallback
    if (notifications.length === 0) {
      notifications.push({
        severity: 'info',
        icon: '✅',
        msg: 'Todos los sensores en rango óptimo',
      });
    }

    return notifications;
  }

  /**
   * Render the notification center panel with current alerts.
   * @param {object} data - Ecowitt real-time API data object
   */
  function updateNotifications(data) {
    const notifications = generateNotifications(data);

    // Limit to 10 most recent (critical first, then warnings, then info)
    const sorted = [
      ...notifications.filter(n => n.severity === 'critical'),
      ...notifications.filter(n => n.severity === 'warning'),
      ...notifications.filter(n => n.severity === 'rain'),
      ...notifications.filter(n => n.severity === 'info'),
    ].slice(0, 10);

    // Count badges
    const critCount = notifications.filter(n => n.severity === 'critical').length;
    const warnCount = notifications.filter(n => n.severity === 'warning').length;

    const badgesEl = document.getElementById('notifBadges');
    badgesEl.innerHTML = '';
    if (critCount > 0) {
      const b = document.createElement('span');
      b.className = 'notif-badge critical';
      b.textContent = `${critCount} 🚨`;
      badgesEl.appendChild(b);
    }
    if (warnCount > 0) {
      const b = document.createElement('span');
      b.className = 'notif-badge warning';
      b.textContent = `${warnCount} ⚠️`;
      badgesEl.appendChild(b);
    }
    if (critCount === 0 && warnCount === 0) {
      const b = document.createElement('span');
      b.className = 'notif-badge info';
      b.textContent = 'Todo normal';
      badgesEl.appendChild(b);
    }

    // Timestamp
    setText('notifTimestamp', `Actualizado: ${formatTime(new Date())}`);

    // Render list
    const listEl = document.getElementById('notifList');
    listEl.innerHTML = '';

    if (sorted.length === 0) {
      const empty = document.createElement('div');
      empty.className = 'notif-empty';
      empty.textContent = 'Sin notificaciones';
      listEl.appendChild(empty);
      return;
    }

    sorted.forEach(notif => {
      const item = document.createElement('div');
      item.className = `notif-item severity-${notif.severity}`;
      item.innerHTML = `
        <div class="notif-icon">${notif.icon}</div>
        <div class="notif-msg">${notif.msg}</div>
        <div class="notif-time">${formatTime(new Date())}</div>
      `;
      listEl.appendChild(item);
    });
  }

/* ──────────────────────────────────────────
     PLANT TOOLTIP
  ────────────────────────────────────────── */

  /**
   * Show the plant info tooltip near the cursor.
   * @param {MouseEvent} event
   * @param {string} plantId
   */
  function showPlantTooltip(event, plantId) {
    const plant = PLANT_MAP[plantId];
    if (!plant) return;

    const tooltip = document.getElementById('plantTooltip');
    tooltip.innerHTML = `
      <div class="plant-tooltip-name">${plant.emoji} ${plant.nombre}</div>
      <div class="plant-tooltip-row"><span>Cosecha:</span><span>${plant.dias} días</span></div>
      <div class="plant-tooltip-row"><span>Espacio:</span><span>${plant.espaciamiento} cm</span></div>
      <div class="plant-tooltip-row"><span>Hum. suelo:</span><span>${plant.humMin}–${plant.humMax}%</span></div>
      <div class="plant-tooltip-row"><span>Temp. óptima:</span><span>${plant.tempMin}–${plant.tempMax}°C</span></div>
    `;

    positionTooltip(event);
    tooltip.classList.add('visible');
  }

  /**
   * Hide the plant tooltip.
   */
  function hidePlantTooltip() {
    document.getElementById('plantTooltip').classList.remove('visible');
  }

  /**
   * Move tooltip to follow cursor.
   * @param {MouseEvent} event
   */
  function movePlantTooltip(event) {
    positionTooltip(event);
  }

  /**
   * Position the tooltip element near the mouse cursor.
   * @param {MouseEvent} event
   */
  function positionTooltip(event) {
    const tooltip = document.getElementById('plantTooltip');
    const offset = 14;
    let x = event.clientX + offset;
    let y = event.clientY + offset;

    // Prevent tooltip from going off-screen to the right
    const tooltipWidth = 220;
    if (x + tooltipWidth > window.innerWidth) {
      x = event.clientX - tooltipWidth - offset;
    }

    // Prevent overflow at bottom
    const tooltipHeight = tooltip.offsetHeight || 120;
    if (y + tooltipHeight > window.innerHeight) {
      y = event.clientY - tooltipHeight - offset;
    }

    tooltip.style.left = x + 'px';
    tooltip.style.top  = y + 'px';
  }

/* ──────────────────────────────────────────
     INIT
  ────────────────────────────────────────── */
  /* ──────────────────────────────────────────
     GLOSSARY
  ────────────────────────────────────────── */
  var GLOSSARY = [
    { term: 'Humedad del suelo (%)', def: 'Porcentaje de agua en el suelo medido por el sensor WH51. Cada tipo de cultivo tiene su rango optimo.' },
    { term: 'AD (Analog-to-Digital)', def: 'Valor crudo del sensor de suelo (0-255). Es la lectura electrica antes de convertirse a porcentaje. Mayor AD = suelo mas humedo.' },
    { term: 'Umbral de riego', def: 'Nivel minimo de humedad del suelo antes de necesitar riego. Varia por cultivo: hojas 28%, brasicas 22%, tomate 18%.' },
    { term: 'Optimo / Aviso / Critico', def: 'Tres niveles de humedad: Optimo (verde) = rango ideal. Aviso (amarillo) = regar pronto. Critico (rojo) = regar ya.' },
    { term: 'EN VIVO', def: 'La cama tiene un sensor fisico conectado mostrando datos en tiempo real (actualiza cada 5 min).' },
    { term: 'Ultimo registro', def: 'Dato guardado de la ultima vez que un sensor estuvo en esa cama. Se muestra cuando el sensor fue movido a otra ubicacion.' },
    { term: 'Temperatura (C)', def: 'Temperatura del aire exterior medida por el sensor WH32. El bosque de niebla oscila entre 12-24 grados C.' },
    { term: 'Humedad del aire (%)', def: 'Porcentaje de humedad relativa del aire. En bosque de niebla es normal 70-98%. No confundir con humedad del suelo.' },
    { term: 'Presion barometrica (hPa)', def: 'Presion atmosferica medida por el gateway GW1100. Util para predecir cambios de clima. A 1,780m la presion normal es ~820 hPa.' },
    { term: 'Punto de rocio', def: 'Temperatura a la cual el aire se satura y se forma rocio o niebla. Importante en bosque de niebla donde frecuentemente la temperatura real esta cerca del punto de rocio.' },
    { term: 'Sensacion termica', def: 'Temperatura percibida considerando humedad y viento. Puede sentirse mas frio o caliente que la temperatura real.' },
    { term: 'Tasa de lluvia (mm/hr)', def: 'Cantidad de lluvia por hora medida por el pluviometro WH40. Si es mayor a 0, esta lloviendo activamente.' },
    { term: 'Lluvia acumulada (mm)', def: 'Total de lluvia acumulada en un periodo (hora, dia, semana, mes, anio). 1mm = 1 litro por metro cuadrado.' },
    { term: 'Gateway GW1100', def: 'El "cerebro" del sistema Ecowitt. Recibe datos de todos los sensores por radio y los envia a la nube via WiFi.' },
    { term: 'WH51', def: 'Sensor de humedad de suelo Ecowitt. Mide cada 72 segundos. Alcance: 100m. Alimentacion: 1 pila AA. Se tienen 5 unidades.' },
    { term: 'WH32', def: 'Sensor de temperatura y humedad exterior. Ubicado a 1.5m del suelo en sombra ligera.' },
    { term: 'WH40', def: 'Pluviometro (sensor de lluvia). Ubicado en zona abierta sin obstrucciones.' },
    { term: 'Bosque de niebla', def: 'Ecosistema de la finca a 1,780 msnm en Zipacon. Caracterizado por humedad alta constante (70-98%), neblina frecuente y temperaturas frescas (12-24 C). El suelo tiende a mantenerse humedo naturalmente.' },
    { term: 'Cooldown', def: 'Sistema anti-spam de alertas. Cuando se envia una alerta por Telegram, no se repite el mismo tipo de alerta hasta que pasen 30 minutos.' },
    { term: 'Sensor rotativo', def: 'Sistema que permite mover los 5 sensores fisicos entre las 12 camas. Cada cama guarda su ultimo dato cuando el sensor se mueve a otra ubicacion.' },
  ];

  function toggleGlossary() {
    const body = document.getElementById('glossaryBody');
    const chevron = document.getElementById('glossaryChevron');
    body.classList.toggle('visible');
    chevron.classList.toggle('open');
  }

  function populateGlossary() {
    const grid = document.getElementById('glossaryGrid');
    if (!grid) return;
    GLOSSARY.forEach(item => {
      const div = document.createElement('div');
      div.className = 'glossary-item';
      div.innerHTML = `<div class="glossary-term">${item.term}</div><div class="glossary-def">${item.def}</div>`;
      grid.appendChild(div);
    });
  }

  /* ──────────────────────────────────────────
     ASISTENTE DE CULTIVO — Sistema de Recomendaciones
  ────────────────────────────────────────── */

  /** Cached companion planting matrix */
  var _companionMatrix = null;

  /** Toggle collapse/expand for Asistente section */
  function toggleAsistente() {
    const body = document.getElementById('asistenteBody');
    const chevron = document.getElementById('asistenteChevron');
    body.classList.toggle('visible');
    chevron.classList.toggle('open');
  }

  /**
   * Fetch the companion planting matrix JSON once and cache it.
   * After loading, renders the companion panel if matrix was pending.
   */
  async function fetchCompanionMatrix() {
    try {
      const res = await fetch('data/companion_planting_matrix.json');
      if (!res.ok) throw new Error('HTTP ' + res.status);
      _companionMatrix = await res.json();
      // Render companion panel now that matrix is loaded
      renderCompanionPanel();
    } catch (e) {
      console.warn('No se pudo cargar companion_planting_matrix.json:', e);
      const el = document.getElementById('companionContainer');
      if (el) el.innerHTML = '<div class="asistente-loading">⚠️ No se pudo cargar la matriz de compañeras.</div>';
    }
  }

  /**
   * Calculate how well current ambient conditions match a plant's ideal ranges.
   * Returns a score 0-100.
   * @param {object} plant - PLANT_CATALOG entry
   * @param {number} temp  - current outdoor temperature °C
   * @param {number} hum   - current outdoor humidity %
   * @returns {number} score 0-100
   */
  function calcConditionMatch(plant, temp, hum) {
    // Temperature score
    let tempScore = 100;
    if (temp < plant.tempMin) {
      const gap = plant.tempMin - temp;
      tempScore = Math.max(0, 100 - gap * 8);
    } else if (temp > plant.tempMax) {
      const gap = temp - plant.tempMax;
      tempScore = Math.max(0, 100 - gap * 8);
    }

    // Humidity score (air humidity mapped loosely to soil preference as orientation)
    // We use air humidity as a proxy for ambient suitability
    let humScore = 100;
    // High air humidity (>85%) is generally OK for moisture-loving plants
    // but may indicate fungal risk for dry-loving ones
    if (plant.humMin > 30 && hum > 85) {
      humScore = 85; // slight penalty for very high humidity in general
    } else if (plant.humMin < 25 && hum < 50) {
      humScore = 90;
    }

    return Math.round((tempScore * 0.75) + (humScore * 0.25));
  }

  /**
   * Render Panel 1: ranked list of plants by condition match.
   * @param {number} temp - outdoor temperature
   * @param {number} hum  - outdoor humidity
   */
  function renderMatchList(temp, hum) {
    const container = document.getElementById('matchListContainer');
    if (!container) return;

    const scored = PLANT_CATALOG.map(p => ({
      plant: p,
      score: calcConditionMatch(p, temp, hum),
    })).sort((a, b) => b.score - a.score);

    const top10   = scored.slice(0, 10);
    const bottom5 = scored.slice(-5).reverse();

    function scoreColor(s) {
      if (s >= 90) return 'match-green';
      if (s >= 70) return 'match-yellow';
      return 'match-red';
    }
    function barColor(s) {
      if (s >= 90) return '#00D68F';
      if (s >= 70) return '#FFB800';
      return '#FF4757';
    }

    function buildItems(list) {
      return list.map(({ plant, score }) => {
        const cls = scoreColor(score);
        return `
          <div class="match-item">
            <span class="match-item-name">${plant.emoji} ${plant.nombre}</span>
            <div class="match-bar-wrap">
              <div class="match-bar-fill" style="width:${score}%;background:${barColor(score)}"></div>
            </div>
            <span class="match-score ${cls}">${score}%</span>
          </div>`;
      }).join('');
    }

    container.innerHTML = `
      <div style="font-size:0.7rem;color:var(--muted);margin-bottom:0.5rem;">
        Temp exterior: <strong style="color:var(--text)">${temp.toFixed(1)}°C</strong>
        &nbsp;·&nbsp; Humedad aire: <strong style="color:var(--text)">${hum.toFixed(0)}%</strong>
      </div>
      <div class="match-list">
        <div class="match-divider">— TOP 10 MEJORES CONDICIONES —</div>
        ${buildItems(top10)}
        <div class="match-divider" style="margin-top:0.4rem">— PEOR ADAPTADAS AHORA —</div>
        ${buildItems(bottom5)}
      </div>`;
  }

  /**
   * Render Panel 2: per-bed performance alerts based on soil moisture + temp.
   * @param {object} data - raw Ecowitt API data
   */
  function renderPerfAlerts(data) {
    const container = document.getElementById('perfAlertsContainer');
    if (!container) return;

    const sensorAssignments = loadSensorAssignments();
    const bedReadings       = loadBedReadings();
    const outdoorTemp       = parseVal(data.outdoor?.temperature?.value);
    const antifungicos      = _companionMatrix ? _companionMatrix.antifungicos_recomendados : ['tomillo', 'oregano', 'romero', 'cebollin'];

    // Build list of beds that have sensor data
    const allBedIds = [...BEDS.map(b => b.id), 'invernadero'];
    const items = [];

    allBedIds.forEach(bedId => {
      const plantIds = BED_PLANTS[bedId] || [];
      if (plantIds.length === 0) return;

      const assignedSensor = sensorAssignments[bedId] || null;
      let humidity = null;

      if (assignedSensor && data[assignedSensor]?.soilmoisture?.value != null) {
        humidity = parseVal(data[assignedSensor].soilmoisture.value);
      } else if (bedReadings[bedId]?.humidity != null) {
        humidity = bedReadings[bedId].humidity;
      }

      const bedDef  = BEDS.find(b => b.id === bedId);
      const bedName = bedDef ? bedDef.name : (bedId === 'invernadero' ? 'Invernadero' : bedId);
      const group   = bedDef ? bedDef.group : 'hojas';
      const thresh  = CROP_THRESHOLDS[group] || CROP_THRESHOLDS.hojas;

      const lines = [];

      // Soil moisture check per plant
      plantIds.forEach(pid => {
        const plant = PLANT_MAP[pid];
        if (!plant) return;
        const name  = plant.emoji + ' ' + plant.nombre;

        if (humidity !== null) {
          if (humidity < thresh.critical) {
            lines.push(`<div class="perf-line perf-crit">💧 ${name} — ${humidity}% suelo ⛔ CRÍTICO, regar urgente</div>`);
          } else if (humidity < thresh.alert) {
            lines.push(`<div class="perf-line perf-warn">💧 ${name} — ${humidity}% suelo ⚠️ Bajo, regar pronto</div>`);
          } else if (humidity > thresh.optMax + 15) {
            lines.push(`<div class="perf-line perf-warn">💧 ${name} — ${humidity}% suelo ⚠️ Saturado, drenar</div>`);
          } else {
            lines.push(`<div class="perf-line perf-ok">💧 ${name} — ${humidity}% suelo ✅ Óptimo</div>`);
          }
        } else {
          lines.push(`<div class="perf-line" style="color:var(--muted)">💧 ${name} — sin sensor activo</div>`);
        }

        // Temperature check
        if (outdoorTemp !== null) {
          if (outdoorTemp < plant.tempMin) {
            lines.push(`<div class="perf-line perf-warn">🌡️ ${name} — ${outdoorTemp.toFixed(1)}°C ⚠️ Por debajo del mínimo (${plant.tempMin}°C)</div>`);
          } else if (outdoorTemp > plant.tempMax) {
            lines.push(`<div class="perf-line perf-crit">🌡️ ${name} — ${outdoorTemp.toFixed(1)}°C ⛔ Excede máximo (${plant.tempMax}°C)</div>`);
          }
        }
      });

      // Companion enemy check within bed
      if (_companionMatrix && plantIds.length > 1) {
        const enemies = _companionMatrix.enemigos || {};
        for (let i = 0; i < plantIds.length; i++) {
          for (let j = i + 1; j < plantIds.length; j++) {
            const a = plantIds[i], b = plantIds[j];
            const aEnemies = enemies[a] || [];
            if (aEnemies.includes(b)) {
              const nameA = PLANT_MAP[a]?.nombre || a;
              const nameB = PLANT_MAP[b]?.nombre || b;
              lines.push(`<div class="perf-line perf-warn">⚠️ Conflicto: ${nameA} y ${nameB} son enemigas</div>`);
            }
          }
        }
      }

      // Suggest antifungal herb if missing
      const hasAntifungal = plantIds.some(pid => antifungicos.includes(pid));
      if (!hasAntifungal && group !== 'invernadero') {
        lines.push(`<div class="perf-tip">💡 Sin hierba antifúngica — considerar agregar tomillo u orégano</div>`);
      }

      if (lines.length > 0) {
        items.push(`
          <div class="perf-item">
            <div class="perf-item-bed">${bedName}</div>
            ${lines.join('')}
          </div>`);
      }
    });

    if (items.length === 0) {
      container.innerHTML = '<div class="perf-empty">Sin alertas activas. Todas las camas con sensor están en rango óptimo.</div>';
    } else {
      container.innerHTML = `<div class="perf-list">${items.join('')}</div>`;
    }
  }

  /**
   * Render Panel 3: companion and enemy combinations per bed.
   */
  function renderCompanionPanel() {
    const container = document.getElementById('companionContainer');
    if (!container) return;
    if (!_companionMatrix) {
      container.innerHTML = '<div class="asistente-loading">Cargando matriz de compañeras…</div>';
      return;
    }

    const companionMap = _companionMatrix.companeras || {};
    const enemyMap     = _companionMatrix.enemigos   || {};
    const allBedIds    = [...BEDS.map(b => b.id), 'invernadero'];
    const blocks       = [];

    allBedIds.forEach(bedId => {
      const plantIds = BED_PLANTS[bedId] || [];
      if (plantIds.length === 0) return;

      const bedDef  = BEDS.find(b => b.id === bedId);
      const bedName = bedDef ? bedDef.name : (bedId === 'invernadero' ? 'Invernadero' : bedId);

      const goodPairs = [];
      const badPairs  = [];

      for (let i = 0; i < plantIds.length; i++) {
        for (let j = i + 1; j < plantIds.length; j++) {
          const a = plantIds[i], b = plantIds[j];
          const aComp = companionMap[a] || [];
          const aEnem = enemyMap[a]     || [];
          const nameA = PLANT_MAP[a]?.nombre || a;
          const nameB = PLANT_MAP[b]?.nombre || b;
          if (aComp.includes(b))  goodPairs.push(`${nameA} + ${nameB}`);
          if (aEnem.includes(b))  badPairs.push(`${nameA} ✗ ${nameB}`);
        }
      }

      // Suggested companions (not in bed yet, but top recommended for plants present)
      const suggestedSet = new Set();
      plantIds.forEach(pid => {
        const comps = companionMap[pid] || [];
        comps.forEach(cid => {
          if (!plantIds.includes(cid) && PLANT_MAP[cid]) {
            suggestedSet.add(cid);
          }
        });
      });
      // Limit to top 3 suggestions
      const suggestions = Array.from(suggestedSet).slice(0, 3);

      const rows = [];

      if (goodPairs.length > 0) {
        goodPairs.forEach(p => {
          rows.push(`<div class="comp-row comp-ok"><span class="comp-icon">✅</span><span>${p} — buena combinación</span></div>`);
        });
      } else if (plantIds.length > 1) {
        rows.push(`<div class="comp-row" style="color:var(--muted)"><span class="comp-icon">➖</span><span>Sin sinergias especiales entre las plantas actuales</span></div>`);
      }

      if (badPairs.length > 0) {
        badPairs.forEach(p => {
          rows.push(`<div class="comp-row comp-bad"><span class="comp-icon">⚠️</span><span>${p} — se inhiben mutuamente</span></div>`);
        });
      }

      if (suggestions.length > 0) {
        const sugNames = suggestions.map(sid => {
          const p = PLANT_MAP[sid];
          return p ? `${p.emoji} ${p.nombre}` : sid;
        }).join(', ');
        rows.push(`<div class="comp-row comp-tip"><span class="comp-icon">💡</span><span>Agregar: ${sugNames}</span></div>`);
      }

      if (rows.length > 0) {
        blocks.push(`
          <div class="comp-bed-block">
            <div class="comp-bed-name">${bedName}</div>
            ${rows.join('')}
          </div>`);
      }
    });

    // Cloud forest rules footer
    const rules = (_companionMatrix.reglas_bosque_niebla || [])
      .map(r => `<div class="comp-rule-item">🌿 ${r}</div>`)
      .join('');

    const blocksHtml = blocks.length > 0
      ? blocks.join('')
      : '<div class="perf-empty">Asigna plantas a las camas para ver recomendaciones de compañeras.</div>';

    container.innerHTML = `
      ${blocksHtml}
      ${rules ? `<div class="comp-rules">
        <div class="comp-rules-title">Reglas del Bosque de Niebla</div>
        ${rules}
      </div>` : ''}`;
  }

  /**
   * Main entry point called from updateDashboard(data).
   * Renders all three recommendation panels.
   * @param {object} data - raw Ecowitt API response
   */
  function updateRecommendations(data) {
    const temp = parseVal(data.outdoor?.temperature?.value);
    const hum  = parseVal(data.outdoor?.humidity?.value);

    if (temp !== null && hum !== null) {
      renderMatchList(temp, hum);
    }

    renderPerfAlerts(data);
    renderCompanionPanel();
  }
