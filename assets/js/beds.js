'use strict';

/** Default physical sensor placement */
  // La cama 11 llega a 6 cultivos (siembra real 29-ago-2026).
  const MAX_CULTIVOS_POR_CAMA = 6;

  const DEFAULT_SENSOR_ASSIGNMENTS = {
    // Canales verificados fisicamente en la huerta el 24-ago-2026.
    // Fuente de verdad: config/huerta_config.json (campo canal_ecowitt).
    cama1:       'soil_ch2',
    cama2:       'soil_ch4',
    cama3:       'soil_ch5',
    cama4:       null,
    cama5:       'soil_ch3',
    cama6:       null,
    cama7:       null,
    cama8:       null,   // WH51-4 reubicado
    cama9:       null,
    cama10:      null,
    cama11:      null,   // WH51-5 reubicado
    cama12:      null,
    invernadero: 'soil_ch1',
  };

  /**
   * Load sensor-to-bed assignments from localStorage or use defaults.
   * @returns {Object<string, string|null>}
   */
  function loadSensorAssignments() {
    try {
      const raw = localStorage.getItem(LS_SENSOR_ASSIGNMENTS);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (typeof parsed === 'object' && parsed !== null) {
          return parsed;
        }
      }
    } catch (e) {
      console.warn('Failed to parse sensor assignments:', e);
    }
    return JSON.parse(JSON.stringify(DEFAULT_SENSOR_ASSIGNMENTS));
  }

  /**
   * Save sensor-to-bed assignments to localStorage.
   * @param {Object<string, string|null>} data
   */
  function saveSensorAssignments(data) {
    try {
      localStorage.setItem(LS_SENSOR_ASSIGNMENTS, JSON.stringify(data));
    } catch (e) {
      console.warn('Failed to save sensor assignments:', e);
    }
  }

  /**
   * Load last-known bed readings cache from localStorage.
   * @returns {Object<string, { humidity: number, timestamp: number, sensor: string }>}
   */
  function loadBedReadings() {
    try {
      const raw = localStorage.getItem(LS_BED_READINGS);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (typeof parsed === 'object' && parsed !== null) {
          return parsed;
        }
      }
    } catch (e) {
      console.warn('Failed to parse bed readings:', e);
    }
    return {};
  }

  /**
   * Save bed readings cache to localStorage.
   * @param {Object} data
   */
  function saveBedReadings(data) {
    try {
      localStorage.setItem(LS_BED_READINGS, JSON.stringify(data));
    } catch (e) {
      console.warn('Failed to save bed readings:', e);
    }
  }

  /**
   * Reverse lookup: which bed (if any) is currently using this sensor key.
   * @param {string} sensorKey - e.g. 'soil_ch1'
   * @returns {string|null} bedId or null
   */
  function getSensorBed(sensorKey) {
    const assignments = loadSensorAssignments();
    for (const [bedId, assigned] of Object.entries(assignments)) {
      if (assigned === sensorKey) return bedId;
    }
    return null;
  }

  /**
   * Assign a sensor to a bed.  Auto-unassigns it from any other bed first.
   * Pass null/empty string as sensorKey to remove sensor from the bed.
   * @param {string} bedId
   * @param {string|null} sensorKey
   */
  function assignSensorToBed(bedId, sensorKey) {
    const assignments = loadSensorAssignments();

    // Normalize empty string to null
    const newKey = sensorKey || null;

    // If this sensor is already in another bed, clear it there first
    if (newKey) {
      for (const [bid, assigned] of Object.entries(assignments)) {
        if (bid !== bedId && assigned === newKey) {
          assignments[bid] = null;
        }
      }
    }

    assignments[bedId] = newKey;
    saveSensorAssignments(assignments);

    // Push to Supabase (best-effort)
    pushCamaToSupabase(bedId, { sensor_asignado: newKey });
    // Clear the previously-assigned bed too, if any
    if (newKey) {
      for (const [bid, val] of Object.entries(assignments)) {
        if (bid !== bedId && val === null) {
          pushCamaToSupabase(bid, { sensor_asignado: null });
        }
      }
    }

    // Re-render the entire bed map with the cached last API data
    refreshBedCardsOnly();
  }

  /**
   * Format a relative time string from a millisecond timestamp.
   * @param {number} timestampMs
   * @returns {string}
   */
  function timeAgo(timestampMs) {
    const diff = Date.now() - timestampMs;
    const mins = Math.floor(diff / 60000);
    if (mins < 1)  return 'ahora';
    if (mins < 60) return `hace ${mins}min`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24)  return `hace ${hrs}h`;
    const days = Math.floor(hrs / 24);
    return `hace ${days}d`;
  }

  /**
   * Build the sensor select dropdown options for a given bed.
   * @param {string} bedId
   * @param {string|null} assignedSensor - currently assigned sensor key for this bed
   * @param {Object<string,string|null>} assignments - full assignment map
   * @returns {string} HTML string of <option> elements
   */
  function buildSensorOptions(bedId, assignedSensor, assignments) {
    let html = '<option value="">Sin sensor</option>';
    SOIL_CHANNELS.forEach(ch => {
      const isSelected = assignedSensor === ch.key;
      // Check if assigned to ANOTHER bed
      const occupiedBy = Object.entries(assignments).find(
        ([bid, sk]) => bid !== bedId && sk === ch.key
      );
      const chNum = ch.key.replace('soil_ch', 'CH');
      let label = `📡 ${chNum}`;
      if (occupiedBy) {
        // Find bed name for display
        const occBed = BEDS.find(b => b.id === occupiedBy[0]);
        const occName = occBed ? occBed.name : (occupiedBy[0] === 'invernadero' ? 'Invernadero' : occupiedBy[0]);
        label += ` (en ${occName})`;
      }
      html += `<option value="${ch.key}"${isSelected ? ' selected' : ''}>${label}</option>`;
    });
    return html;
  }

  /**
   * Load bed plant assignments from localStorage or fall back to defaults.
   * @returns {Object<string, string[]>}
   */
  function loadBedPlants() {
    try {
      const raw = localStorage.getItem(LS_KEY);
      if (raw) {
        const parsed = JSON.parse(raw);
        // Validate: must be an object with string arrays
        if (typeof parsed === 'object' && parsed !== null) {
          return parsed;
        }
      }
    } catch (e) {
      console.warn('Failed to parse localStorage plant data:', e);
    }
    return JSON.parse(JSON.stringify(DEFAULT_BED_PLANTS)); // deep copy
  }

  /**
   * Save bed plant assignments to localStorage.
   * @param {Object<string, string[]>} data
   */
  function saveBedPlants(data) {
    try {
      localStorage.setItem(LS_KEY, JSON.stringify(data));
    } catch (e) {
      console.warn('Failed to save plant data to localStorage:', e);
    }
  }

  /** Live bed plant assignments (mutable, persisted to localStorage) */
  var BED_PLANTS = loadBedPlants();

  /* ──────────────────────────────────────────
     UPDATE: BED MAP
  ────────────────────────────────────────── */

  /**
   * Build crop item HTML for a plant ID or fallback string.
   * @param {string} plantId
   * @returns {string}
   */
  function buildCropItemHtml(plantId) {
    const plant = PLANT_MAP[plantId];
    if (plant) {
      return `<div class="bed-crop-item" data-plant-id="${plant.id}"
                   onmouseenter="showPlantTooltip(event, '${plant.id}')"
                   onmouseleave="hidePlantTooltip()"
                   onmousemove="movePlantTooltip(event)">${plant.emoji} ${plant.nombre}</div>`;
    }
    // Fallback: treat as raw emoji string
    return `<div class="bed-crop-item">${plantId}</div>`;
  }

  /**
   * Render a single bed card element.
   * @param {object} bed - Bed definition from BEDS array
   * @param {number|null} humidity - Humidity value (live or cached) or null
   * @param {boolean} isLive - True if the humidity comes from a currently assigned sensor
   * @param {number|null} cachedTimestamp - Epoch ms of last cached reading (when not live)
   * @param {string|null} adValue - Raw AD sensor value
   * @returns {HTMLElement}
   */
  function renderBedCard(bed, humidity, isLive, cachedTimestamp, adValue) {
    const { glowClass, color } = bedHumidityStatus(humidity, bed.group);
    const t = CROP_THRESHOLDS[bed.group] || CROP_THRESHOLDS.rotacion;

    const card = document.createElement('div');
    card.className = `bed-card${glowClass ? ' ' + glowClass : ''}`;
    card.dataset.group = bed.group;
    card.dataset.bedId = bed.id;

    const groupLabel = GROUP_LABELS[bed.group] || bed.group;

    // Use BED_PLANTS (from localStorage) as source of truth for crops
    const plantIds = BED_PLANTS[bed.id] || bed.crops || [];
    const cropsHtml = plantIds.map(id => buildCropItemHtml(id)).join('');

    // Build sensor selector
    const assignments = loadSensorAssignments();
    const assignedSensor = assignments[bed.id] || null;
    const sensorOptionsHtml = buildSensorOptions(bed.id, assignedSensor, assignments);
    const sensorRowHtml = `
      <div class="bed-sensor-row">
        <select class="bed-sensor-select" onchange="assignSensorToBed('${bed.id}', this.value)">
          ${sensorOptionsHtml}
        </select>
      </div>
    `;

    // Build humidity display
    let humidityHtml;
    const adHtml = adValue !== null ? `<span class="channel-ad">(AD: ${adValue})</span>` : '';
    if (humidity !== null && isLive) {
      humidityHtml = `
        <div style="display:flex;align-items:baseline;flex-wrap:wrap;gap:0.1rem">
          <div class="bed-humidity" style="color:${color}">${Math.round(humidity)}% ${adHtml}</div>
          <span class="bed-live-badge">En vivo</span>
        </div>
        <div class="bed-humidity-sub">Óptimo: ${t.optMin}–${t.optMax}%</div>
      `;
    } else if (humidity !== null && cachedTimestamp) {
      humidityHtml = `
        <div class="bed-humidity-cached" style="color:${color}">${Math.round(humidity)}%</div>
        <div class="bed-cached-info">Último: ${timeAgo(cachedTimestamp)}</div>
      `;
    } else {
      humidityHtml = `<div class="bed-no-sensor">Sin datos</div>`;
    }

    card.innerHTML = `
      <button class="bed-edit-btn" onclick="openPlantModal('${bed.id}')" title="Editar plantas">✏️</button>
      <div class="bed-card-name">${bed.name} · ${groupLabel}</div>
      <div class="bed-card-crops">${cropsHtml}</div>
      ${sensorRowHtml}
      ${humidityHtml}
    `;

    return card;
  }

  // (_lastApiData and notifPermission are declared in config.js — Safari iOS TDZ fix)

  /**
   * Update the visual bed map with live humidity data using the sensor assignment system.
   * @param {object} data - Ecowitt real-time API data object
   */
  function updateBedMap(data) {
    const sensorAssignments = loadSensorAssignments();
    const bedReadings = loadBedReadings();

    // Cache for lightweight re-renders (stores the raw API data)
    _lastApiData = data;

    const rowOdd  = document.getElementById('bedsRow1'); // impares (derecha)
    const rowEven = document.getElementById('bedsRow2'); // pares (izquierda)
    rowOdd.innerHTML = '';
    rowEven.innerHTML = '';

    BEDS.forEach(bed => {
      const assignedSensor = sensorAssignments[bed.id] || null;
      let humidity = null;
      let isLive = false;
      let cachedTimestamp = null;
      let adValue = null;

      if (assignedSensor) {
        // Try to get live reading from assigned sensor
        const liveVal = parseVal(data[assignedSensor]?.soilmoisture?.value);
        if (liveVal !== null) {
          humidity = liveVal;
          isLive = true;
          adValue = data[assignedSensor]?.ad?.value ?? null;
          // Cache this reading (include AD)
          bedReadings[bed.id] = { humidity: liveVal, timestamp: Date.now(), sensor: assignedSensor, ad: adValue };
        }
      }

      if (!isLive && bedReadings[bed.id]) {
        // Fall back to cached reading
        humidity = bedReadings[bed.id].humidity;
        cachedTimestamp = bedReadings[bed.id].timestamp;
      }

      const card = renderBedCard(bed, humidity, isLive, cachedTimestamp, adValue);
      const bedNum = parseInt(bed.id.replace('cama', ''), 10);
      if (bedNum % 2 === 1) {
        rowOdd.appendChild(card);  // 1,3,5,7,9,11
      } else {
        rowEven.appendChild(card); // 2,4,6,8,10,12
      }
    });

    // Save updated bed readings cache
    saveBedReadings(bedReadings);

    // Update greenhouse card
    const ghAssigned = sensorAssignments['invernadero'] || null;
    let ghHum = null;
    let ghIsLive = false;
    let ghCachedTs = null;

    let ghAd = null;

    if (ghAssigned) {
      const liveGh = parseVal(data[ghAssigned]?.soilmoisture?.value);
      if (liveGh !== null) {
        ghHum = liveGh;
        ghIsLive = true;
        ghAd = data[ghAssigned]?.ad?.value ?? null;
        bedReadings['invernadero'] = { humidity: liveGh, timestamp: Date.now(), sensor: ghAssigned, ad: ghAd };
        saveBedReadings(bedReadings);
      }
    }
    if (!ghIsLive && bedReadings['invernadero']) {
      ghHum = bedReadings['invernadero'].humidity;
      ghCachedTs = bedReadings['invernadero'].timestamp;
    }

    // Greenhouse temp from WN31 (temp_and_humidity_ch1)
    const ghTempData = data.temp_and_humidity_ch1 || {};
    const ghTemp = parseVal(ghTempData.temperature?.value);
    const ghTempHum = parseVal(ghTempData.humidity?.value);

    _updateGreenhouseHumidity(ghHum, ghIsLive, ghCachedTs, ghAd, ghTemp, ghTempHum);
    _updateGreenhouseSensorSelect(sensorAssignments);

    // Update greenhouse crops display from BED_PLANTS
    renderGreenhouseCrops();
  }

  /**
   * Update the greenhouse humidity display.
   * @param {number|null} ghHum
   * @param {boolean} isLive
   * @param {number|null} cachedTs
   */
  function _updateGreenhouseHumidity(ghHum, isLive, cachedTs, ghAd, ghTemp, ghTempHum) {
    const ghEl   = document.getElementById('greenhouseHumidity');
    const ghCard = document.getElementById('greenhouseCard');
    const ghLabel= document.getElementById('greenhouseDimsLabel');
    const ghTempEl = document.getElementById('greenhouseTemp');

    if (ghHum !== null) {
      const adStr = ghAd !== null && ghAd !== undefined ? ` <span class="channel-ad">(AD: ${ghAd})</span>` : '';
      ghEl.innerHTML = Math.round(ghHum) + '%' + (isLive ? adStr : '');
      const t = CROP_THRESHOLDS.tomate;
      if (ghHum < t.critical)                        { ghEl.style.color = '#FF4757'; ghCard.style.borderLeftColor = '#FF4757'; }
      else if (ghHum < t.alert)                      { ghEl.style.color = '#FFB800'; ghCard.style.borderLeftColor = '#FFB800'; }
      else if (ghHum >= t.optMin && ghHum <= t.optMax){ ghEl.style.color = '#00D68F'; ghCard.style.borderLeftColor = '#00D68F'; }
      else                                            { ghEl.style.color = '#4ECDC4'; ghCard.style.borderLeftColor = '#4ECDC4'; }

      if (isLive) {
        ghLabel.innerHTML = 'Humedad suelo <span class="bed-live-badge">En vivo</span>';
      } else if (cachedTs) {
        ghLabel.textContent = `Último: ${timeAgo(cachedTs)}`;
      } else {
        ghLabel.textContent = 'Humedad suelo';
      }
    } else {
      ghEl.textContent = '—';
      ghLabel.textContent = 'Humedad suelo';
    }

    // Greenhouse ambient temp/hum from WN31
    if (ghTempEl) {
      if (ghTemp !== null) {
        let tempStr = ghTemp.toFixed(1) + '°C';
        if (ghTempHum !== null) tempStr += ' · ' + Math.round(ghTempHum) + '% aire';
        ghTempEl.textContent = tempStr;
      } else {
        ghTempEl.textContent = '—';
      }
    }
  }

  /**
   * Update the greenhouse sensor select dropdown.
   * @param {Object<string, string|null>} assignments
   */
  function _updateGreenhouseSensorSelect(assignments) {
    const select = document.getElementById('greenhouseSensorSelect');
    if (!select) return;
    const assignedSensor = assignments['invernadero'] || null;
    select.innerHTML = buildSensorOptions('invernadero', assignedSensor, assignments);
  }

  /**
   * Render the greenhouse crops row from BED_PLANTS['invernadero'].
   * Also refreshes the sensor select dropdown.
   */
  function renderGreenhouseCrops() {
    const cropsEl = document.getElementById('greenhouseCropsDisplay');
    if (!cropsEl) return;
    const plantIds = BED_PLANTS['invernadero'] || DEFAULT_BED_PLANTS['invernadero'];
    cropsEl.innerHTML = plantIds.map(id => {
      const plant = PLANT_MAP[id];
      if (plant) {
        return `<span class="greenhouse-crop"
                     data-plant-id="${plant.id}"
                     onmouseenter="showPlantTooltip(event, '${plant.id}')"
                     onmouseleave="hidePlantTooltip()"
                     onmousemove="movePlantTooltip(event)"
                     style="cursor:help">${plant.emoji} ${plant.nombre}</span>`;
      }
      return `<span class="greenhouse-crop">${id}</span>`;
    }).join('');

    // Ensure greenhouse sensor select is populated on initial render
    const select = document.getElementById('greenhouseSensorSelect');
    if (select && select.options.length <= 1) {
      _updateGreenhouseSensorSelect(loadSensorAssignments());
    }
  }

  /* ──────────────────────────────────────────
     PLANT MODAL STATE
  ────────────────────────────────────────── */
  var currentEditBedId = null; // which bed is being edited

  /**
   * Open the plant selection modal for a given bed ID.
   * @param {string} bedId - e.g. 'cama1', 'invernadero'
   */
  function openPlantModal(bedId) {
    currentEditBedId = bedId;

    // Set title
    const bed = BEDS.find(b => b.id === bedId);
    const titleEl = document.getElementById('plantModalTitle');
    if (bedId === 'invernadero') {
      titleEl.textContent = 'Editar plantas — Invernadero';
    } else if (bed) {
      titleEl.textContent = `Editar plantas — ${bed.name}`;
    } else {
      titleEl.textContent = `Editar plantas — ${bedId}`;
    }

    // Populate dropdown (filter by bed type)
    populatePlantDropdown(bedId);

    // Render current plants list
    renderCurrentPlantsList();

    // Show overlay
    document.getElementById('plantModalOverlay').classList.add('open');
  }

  /**
   * Close the plant modal and refresh the bed cards to reflect changes.
   */
  function closePlantModal() {
    document.getElementById('plantModalOverlay').classList.remove('open');
    currentEditBedId = null;
    // Re-render bed map to show updated plants (keep last known data)
    // We trigger a lightweight re-render using the last known humidity map
    refreshBedCardsOnly();
  }

  /**
   * Close modal when clicking the overlay (outside the modal card).
   * @param {MouseEvent} event
   */
  function handleOverlayClick(event) {
    if (event.target === document.getElementById('plantModalOverlay')) {
      closePlantModal();
    }
  }

  /**
   * Populate the plant selection <select> with groups.
   * @param {string} bedId
   */
  function populatePlantDropdown(bedId) {
    const select = document.getElementById('plantSelectDropdown');
    select.innerHTML = '<option value="">— Seleccionar planta —</option>';

    const isGreenhouse = bedId === 'invernadero';

    // Group order and labels
    const groups = isGreenhouse
      ? [{ key: 'invernadero', label: 'Invernadero' }]
      : [
          { key: 'hojas',      label: 'Hojas' },
          { key: 'aromaticas', label: 'Aromáticas' },
          { key: 'brasicas',   label: 'Brásicas' },
          { key: 'raices',     label: 'Raíces' },
          { key: 'frutos',     label: 'Frutos' },
        ];

    const currentIds = BED_PLANTS[bedId] || [];

    groups.forEach(({ key, label }) => {
      const plants = PLANT_CATALOG.filter(p => p.grupo === key);
      if (plants.length === 0) return;

      const optgroup = document.createElement('optgroup');
      optgroup.label = label;

      plants.forEach(plant => {
        const opt = document.createElement('option');
        opt.value = plant.id;
        opt.textContent = `${plant.emoji} ${plant.nombre}`;
        if (currentIds.includes(plant.id)) {
          opt.disabled = true;
          opt.textContent += ' ✓';
        }
        optgroup.appendChild(opt);
      });

      select.appendChild(optgroup);
    });

    // Disable add button if already at max
    updateAddButtonState();
  }

  /**
   * Render the list of currently assigned plants inside the modal.
   */
  function renderCurrentPlantsList() {
    const listEl = document.getElementById('plantCurrentList');
    const plantIds = BED_PLANTS[currentEditBedId] || [];

    if (plantIds.length === 0) {
      listEl.innerHTML = '<div class="plant-empty-msg">Sin plantas asignadas</div>';
      return;
    }

    listEl.innerHTML = plantIds.map(id => {
      const plant = PLANT_MAP[id];
      const label = plant ? `${plant.emoji} ${plant.nombre}` : id;
      return `
        <div class="plant-current-item">
          <span>${label}</span>
          <button class="plant-remove-btn" onclick="removePlantFromBed('${id}')" title="Quitar planta">❌</button>
        </div>
      `;
    }).join('');

    updateAddButtonState();
  }

  /**
   * Enable/disable the add button based on plant count.
   */
  function updateAddButtonState() {
    const addBtn = document.getElementById('plantAddBtn');
    const plantIds = BED_PLANTS[currentEditBedId] || [];
    addBtn.disabled = plantIds.length >= MAX_CULTIVOS_POR_CAMA;
  }

  /**
   * Add the selected plant from the dropdown to the current bed.
   */
  function addPlantToCurrentBed() {
    if (!currentEditBedId) return;
    const select = document.getElementById('plantSelectDropdown');
    const plantId = select.value;
    if (!plantId) return;

    const currentIds = BED_PLANTS[currentEditBedId] || [];
    if (currentIds.length >= MAX_CULTIVOS_POR_CAMA) return;
    if (currentIds.includes(plantId)) return;

    BED_PLANTS[currentEditBedId] = [...currentIds, plantId];
    saveBedPlants(BED_PLANTS);
    pushCamaToSupabase(currentEditBedId, { plantas: BED_PLANTS[currentEditBedId] });

    // Reset dropdown and re-render
    select.value = '';
    populatePlantDropdown(currentEditBedId);
    renderCurrentPlantsList();
    refreshBedCardsOnly();
    updateCompanionship();
  }

  /**
   * Remove a plant from the current bed assignment.
   * @param {string} plantId
   */
  function removePlantFromBed(plantId) {
    if (!currentEditBedId) return;
    const currentIds = BED_PLANTS[currentEditBedId] || [];
    BED_PLANTS[currentEditBedId] = currentIds.filter(id => id !== plantId);
    saveBedPlants(BED_PLANTS);
    pushCamaToSupabase(currentEditBedId, { plantas: BED_PLANTS[currentEditBedId] });

    populatePlantDropdown(currentEditBedId);
    renderCurrentPlantsList();
    refreshBedCardsOnly();
    updateCompanionship();
  }

  /* ──────────────────────────────────────────
     COMPAÑERISMO DE CULTIVOS
  ────────────────────────────────────────── */

  /**
   * Analyze a single bed's plant combination. Returns a rich diagnostic with:
   * - positive/conflict pairs (compañeras/enemigos substring match on nombre)
   * - family duplicates (mismo familia botánica → competencia y plagas compartidas)
   * - termofilicos (plantas que sufren por temperatura en Zipacón)
   * - riesgo de hongos del bosque de niebla
   * - sugerencia de antifúngico natural si hay plantas con riesgo alto sin aromática
   * - compañeras sugeridas faltantes
   * @param {string[]} plantIds
   * @returns {object}
   */
  function analyzeBedCompanionship(plantIds) {
    const plants = (plantIds || []).map(id => PLANT_MAP[id]).filter(Boolean);
    if (plants.length === 0) {
      return {
        status: 'empty', statusLabel: 'Vacía',
        positive: [], conflicts: [], familyDupes: [],
        termofilicos: [], needsAntifungico: false, riesgoAlto: false,
        missing: [], plants: [],
      };
    }

    const positive = [];
    const conflicts = [];

    for (let i = 0; i < plants.length; i++) {
      for (let j = i + 1; j < plants.length; j++) {
        const a = plants[i], b = plants[j];
        const aName = a.nombre.toLowerCase();
        const bName = b.nombre.toLowerCase();
        const aEn = (a.enemigos || []).map(s => s.toLowerCase());
        const bEn = (b.enemigos || []).map(s => s.toLowerCase());
        const aCo = (a.companeras || []).map(s => s.toLowerCase());
        const bCo = (b.companeras || []).map(s => s.toLowerCase());

        const isConflict = aEn.some(e => bName.includes(e)) || bEn.some(e => aName.includes(e));
        if (isConflict) {
          conflicts.push([a, b]);
          continue;
        }
        const isPositive = aCo.some(c => bName.includes(c)) || bCo.some(c => aName.includes(c));
        if (isPositive) positive.push([a, b]);
      }
    }

    // Familia duplicada (>= 2 plantas de la misma familia)
    const famGroups = {};
    plants.forEach(p => {
      if (!p.familia) return;
      (famGroups[p.familia] = famGroups[p.familia] || []).push(p);
    });
    const familyDupes = Object.entries(famGroups)
      .filter(([_, list]) => list.length >= 2)
      .map(([fam, list]) => ({ familia: fam, label: FAMILIA_LABELS[fam] || fam, plants: list }));

    // Termofilicos
    const termofilicos = plants.filter(p => p.termofilico);

    // Riesgo de hongos (algo tiene riesgo alto)
    const riesgoAlto = plants.some(p => p.riesgoHongos === 'alto');

    // ¿Tiene antifúngico natural en la cama?
    const hasAntifungico = plants.some(p => p.antifungico);
    const needsAntifungico = riesgoAlto && !hasAntifungico;

    // Suggested missing companions
    const allCo = new Set();
    plants.forEach(p => (p.companeras || []).forEach(c => allCo.add(c.toLowerCase())));
    const presentText = plants.map(p => p.nombre.toLowerCase()).join(' ');
    const missing = [...allCo].filter(c => !presentText.includes(c)).slice(0, 4);

    // Status determination: danger > warning > success > neutral
    let status, statusLabel;
    if (conflicts.length > 0) {
      status = 'danger';
      statusLabel = 'Conflicto';
    } else if (termofilicos.length > 0 || familyDupes.length > 0) {
      status = 'warning';
      statusLabel = familyDupes.length > 0 ? 'Familia duplicada' : 'Termófilo en niebla';
    } else if (positive.length > 0) {
      status = 'success';
      statusLabel = 'Óptima';
    } else if (plants.length === 1) {
      status = 'neutral';
      statusLabel = 'Monocultivo';
    } else {
      status = 'neutral';
      statusLabel = 'Neutral';
    }

    return {
      status, statusLabel,
      positive, conflicts, familyDupes,
      termofilicos, needsAntifungico, riesgoAlto,
      missing, plants,
    };
  }

  /**
   * Render the companionship section: summary pills + per-bed cards + bosque de niebla rules.
   */
  function updateCompanionship() {
    const grid = document.getElementById('companionshipGrid');
    const summary = document.getElementById('companionshipSummary');
    const rulesBox = document.getElementById('companionshipRules');
    if (!grid || !summary) return;

    grid.innerHTML = '';
    summary.innerHTML = '';

    // Reglas del bosque de niebla (una sola vez)
    if (rulesBox && !rulesBox.dataset.rendered) {
      const antifList = ANTIFUNGICOS_IDS
        .map(id => PLANT_MAP[id])
        .filter(Boolean)
        .map(p => `${p.emoji} ${p.nombre}`)
        .join(' · ');
      rulesBox.innerHTML = `
        <div class="comp-rules-title">🌫️ Reglas del Bosque de Niebla — Zipacón 1,780 msnm</div>
        <ul class="comp-rules-list">
          ${BOSQUE_NIEBLA_REGLAS.map(r => `<li>${r}</li>`).join('')}
        </ul>
        <div class="comp-rules-antifun">
          <strong>Antifúngicos naturales recomendados:</strong> ${antifList}
        </div>
      `;
      rulesBox.dataset.rendered = '1';
    }

    const allTargets = [
      ...BEDS.map(b => ({ id: b.id, name: b.name })),
      { id: 'invernadero', name: 'Invernadero' },
    ];

    const counts = { success: 0, warning: 0, danger: 0, neutral: 0, empty: 0 };

    allTargets.forEach(target => {
      const plantIds = BED_PLANTS[target.id] || [];
      const analysis = analyzeBedCompanionship(plantIds);
      counts[analysis.status] = (counts[analysis.status] || 0) + 1;

      const card = document.createElement('div');
      card.className = `comp-card ${analysis.status}`;

      let html = `
        <div class="comp-header">
          <div class="comp-title">${target.name}</div>
          <div class="comp-badge ${analysis.status}">${analysis.statusLabel}</div>
        </div>
      `;

      if (analysis.status === 'empty') {
        html += `<div style="color:#777;font-size:0.72rem">Sin plantas asignadas.</div>`;
      } else {
        // Lista de plantas con familia mini
        html += `<div class="comp-plants">` +
                analysis.plants.map(p => `${p.emoji} ${p.nombre}`).join(' · ') +
                `</div>`;

        // Conflictos (rojo, prioridad máxima)
        if (analysis.conflicts.length > 0) {
          html += `<div class="comp-section"><div class="comp-section-label">🔴 Conflictos (plantas enemigas)</div>`;
          analysis.conflicts.forEach(([a, b]) => {
            html += `<span class="comp-chip danger">${a.nombre} ✗ ${b.nombre}</span>`;
          });
          html += `</div>`;
        }

        // Familia duplicada
        if (analysis.familyDupes.length > 0) {
          html += `<div class="comp-section"><div class="comp-section-label">⚠️ Misma familia botánica</div>`;
          analysis.familyDupes.forEach(dup => {
            const names = dup.plants.map(p => p.nombre).join(' + ');
            html += `<span class="comp-chip warning">${dup.label}: ${names}</span>`;
          });
          html += `<div class="comp-note">Compiten por los mismos nutrientes y atraen las mismas plagas. Evitar en rotación.</div>`;
          html += `</div>`;
        }

        // Termófilos en bosque de niebla
        if (analysis.termofilicos.length > 0) {
          html += `<div class="comp-section"><div class="comp-section-label">🌡️ Termófilos (sufren en niebla)</div>`;
          analysis.termofilicos.forEach(p => {
            html += `<span class="comp-chip warning">${p.emoji} ${p.nombre} · óptimo ${p.tempMin}-${p.tempMax}°C</span>`;
          });
          html += `<div class="comp-note">Zipacón 12-22°C exterior. Considerar invernadero o ubicación soleada.</div>`;
          html += `</div>`;
        }

        // Buenas combinaciones
        if (analysis.positive.length > 0) {
          html += `<div class="comp-section"><div class="comp-section-label">✅ Buenas combinaciones</div>`;
          analysis.positive.forEach(([a, b]) => {
            html += `<span class="comp-chip">${a.nombre} + ${b.nombre}</span>`;
          });
          html += `</div>`;
        }

        // Riesgo alto de hongos sin antifúngico
        if (analysis.needsAntifungico) {
          html += `<div class="comp-section"><div class="comp-section-label">🦠 Riesgo alto de hongos</div>`;
          html += `<div class="comp-note">Sin aromática antifúngica en la cama. Añadir <strong>tomillo, orégano o cebollín</strong> cerca para proteger.</div>`;
          html += `</div>`;
        }

        // Compañeras sugeridas faltantes (solo si no hay conflicto grave)
        if (analysis.missing.length > 0 && analysis.status !== 'danger') {
          html += `<div class="comp-section"><div class="comp-section-label">💡 Compañeras sugeridas</div>`;
          analysis.missing.forEach(m => {
            html += `<span class="comp-chip suggest">${m}</span>`;
          });
          html += `</div>`;
        }
      }

      card.innerHTML = html;
      grid.appendChild(card);
    });

    // Summary pills
    summary.innerHTML = `
      <div class="comp-summary-pill"><span style="color:#90EE90">●</span> Óptimas <strong>${counts.success || 0}</strong></div>
      <div class="comp-summary-pill"><span style="color:#FFD166">●</span> Advertencias <strong>${counts.warning || 0}</strong></div>
      <div class="comp-summary-pill"><span style="color:#FF6B6B">●</span> Conflictos <strong>${counts.danger || 0}</strong></div>
      <div class="comp-summary-pill"><span style="color:#DEB887">●</span> Neutrales <strong>${counts.neutral || 0}</strong></div>
      <div class="comp-summary-pill"><span style="color:#888">●</span> Vacías <strong>${counts.empty || 0}</strong></div>
    `;
  }

  /**
   * Lightweight re-render of just the bed cards without making a new API call.
   * Uses the last known API data stored in state plus the current sensor assignments
   * and cached bed readings from localStorage.
   */
  function refreshBedCardsOnly() {
    const rowOdd  = document.getElementById('bedsRow1');
    const rowEven = document.getElementById('bedsRow2');
    if (!rowOdd || !rowEven) return;

    const sensorAssignments = loadSensorAssignments();
    const bedReadings = loadBedReadings();

    rowOdd.innerHTML = '';
    rowEven.innerHTML = '';

    BEDS.forEach(bed => {
      const assignedSensor = sensorAssignments[bed.id] || null;
      let humidity = null;
      let isLive = false;
      let cachedTimestamp = null;
      let adValue = null;

      if (assignedSensor && _lastApiData) {
        const liveVal = parseVal(_lastApiData[assignedSensor]?.soilmoisture?.value);
        if (liveVal !== null) {
          humidity = liveVal;
          isLive = true;
          adValue = _lastApiData[assignedSensor]?.ad?.value ?? null;
        }
      }

      if (!isLive && bedReadings[bed.id]) {
        humidity = bedReadings[bed.id].humidity;
        cachedTimestamp = bedReadings[bed.id].timestamp;
      }

      const card = renderBedCard(bed, humidity, isLive, cachedTimestamp, adValue);
      const bedNum = parseInt(bed.id.replace('cama', ''), 10);
      if (bedNum % 2 === 1) {
        rowOdd.appendChild(card);
      } else {
        rowEven.appendChild(card);
      }
    });

    // Refresh greenhouse as well
    const ghAssigned = sensorAssignments['invernadero'] || null;
    let ghHum = null;
    let ghIsLive = false;
    let ghCachedTs = null;
    let ghAd = null;

    if (ghAssigned && _lastApiData) {
      const liveGh = parseVal(_lastApiData[ghAssigned]?.soilmoisture?.value);
      if (liveGh !== null) {
        ghHum = liveGh;
        ghIsLive = true;
        ghAd = _lastApiData[ghAssigned]?.ad?.value ?? null;
      }
    }
    if (!ghIsLive && bedReadings['invernadero']) {
      ghHum = bedReadings['invernadero'].humidity;
      ghCachedTs = bedReadings['invernadero'].timestamp;
    }

    // Greenhouse temp from WN31
    const ghTempData2 = _lastApiData ? (_lastApiData.temp_and_humidity_ch1 || {}) : {};
    const ghTemp2 = parseVal(ghTempData2.temperature?.value);
    const ghTempHum2 = parseVal(ghTempData2.humidity?.value);

    _updateGreenhouseHumidity(ghHum, ghIsLive, ghCachedTs, ghAd, ghTemp2, ghTempHum2);
    _updateGreenhouseSensorSelect(sensorAssignments);

    renderGreenhouseCrops();
  }
