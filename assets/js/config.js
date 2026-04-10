'use strict';

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

/* ──────────────────────────────────────────
     PLANT CATALOG
  ────────────────────────────────────────── */
  var PLANT_CATALOG = [
    // HOJAS
    { id: 'lechuga_batavia',   nombre: 'Lechuga Batavia',   emoji: '🥬', grupo: 'hojas',       dias: '40-55',   espaciamiento: 25, humMin: 30, humMax: 50, tempMin: 10, tempMax: 24, companeras: ['zanahoria','remolacha','cebolla'], enemigos: ['perejil','apio'] },
    { id: 'lechuga_romana',    nombre: 'Lechuga Romana',    emoji: '🥬', grupo: 'hojas',       dias: '50-65',   espaciamiento: 30, humMin: 30, humMax: 50, tempMin: 10, tempMax: 24, companeras: ['zanahoria','remolacha','cebolla'], enemigos: ['perejil','apio'] },
    { id: 'lechuga_crespa',    nombre: 'Lechuga Crespa',    emoji: '🥬', grupo: 'hojas',       dias: '35-50',   espaciamiento: 25, humMin: 30, humMax: 50, tempMin: 10, tempMax: 24, companeras: ['zanahoria','remolacha','cebolla'], enemigos: ['perejil','apio'] },
    { id: 'lechuga_morada_lisa', nombre: 'Lechuga Morada Lisa', emoji: '🥬', grupo: 'hojas',    dias: '45-60',   espaciamiento: 25, humMin: 30, humMax: 50, tempMin: 10, tempMax: 22, companeras: ['zanahoria','remolacha','cebolla','cebollin'], enemigos: ['perejil','apio'] },
    { id: 'rucula',            nombre: 'Rúcula',            emoji: '🥗', grupo: 'hojas',       dias: '25-35',   espaciamiento: 15, humMin: 30, humMax: 50, tempMin: 8,  tempMax: 22, companeras: ['lechuga','espinaca','zanahoria'],  enemigos: ['brassicas'] },
    { id: 'espinaca',          nombre: 'Espinaca',          emoji: '🥬', grupo: 'hojas',       dias: '35-50',   espaciamiento: 15, humMin: 35, humMax: 55, tempMin: 5,  tempMax: 22, companeras: ['lechuga','acelga','remolacha'],    enemigos: ['girasol'] },
    { id: 'acelga_comun',      nombre: 'Acelga Común',      emoji: '🥬', grupo: 'hojas',       dias: '50-65',   espaciamiento: 25, humMin: 35, humMax: 55, tempMin: 8,  tempMax: 24, companeras: ['lechuga','cebolla','zanahoria'],   enemigos: ['maiz'] },
    { id: 'acelga_roja',       nombre: 'Acelga Roja',       emoji: '🥬', grupo: 'hojas',       dias: '50-65',   espaciamiento: 25, humMin: 35, humMax: 55, tempMin: 8,  tempMax: 24, companeras: ['lechuga','cebolla'],              enemigos: ['maiz'] },
    { id: 'acelga_amarilla',   nombre: 'Acelga Amarilla',   emoji: '🥬', grupo: 'hojas',       dias: '50-65',   espaciamiento: 25, humMin: 35, humMax: 55, tempMin: 8,  tempMax: 24, companeras: ['lechuga','cebolla'],              enemigos: ['maiz'] },
    { id: 'mizuna_verde',      nombre: 'Mizuna Verde',      emoji: '🥬', grupo: 'hojas',       dias: '30-40',   espaciamiento: 20, humMin: 30, humMax: 50, tempMin: 5,  tempMax: 25, companeras: ['lechuga','espinaca'],             enemigos: [] },
    { id: 'mizuna_roja',       nombre: 'Mizuna Roja',       emoji: '🥬', grupo: 'hojas',       dias: '30-40',   espaciamiento: 20, humMin: 30, humMax: 50, tempMin: 5,  tempMax: 25, companeras: ['lechuga','espinaca'],             enemigos: [] },
    { id: 'mostaza_red',       nombre: 'Mostaza Red',       emoji: '🌿', grupo: 'hojas',       dias: '30-45',   espaciamiento: 20, humMin: 30, humMax: 50, tempMin: 8,  tempMax: 24, companeras: ['lechuga','espinaca'],             enemigos: [] },
    { id: 'tat_soi',           nombre: 'Tat Soi',           emoji: '🥬', grupo: 'hojas',       dias: '30-45',   espaciamiento: 20, humMin: 35, humMax: 55, tempMin: 3,  tempMax: 25, companeras: ['lechuga','cebolla'],              enemigos: ['brassicas'] },
    // AROMÁTICAS
    { id: 'albahaca',          nombre: 'Albahaca',          emoji: '🌿', grupo: 'aromaticas',  dias: '50-70',   espaciamiento: 25, humMin: 25, humMax: 45, tempMin: 15, tempMax: 30, companeras: ['tomate','pimiento'],              enemigos: ['salvia','ruda'] },
    { id: 'albahaca_morada',   nombre: 'Albahaca Morada',   emoji: '🌿', grupo: 'aromaticas',  dias: '50-70',   espaciamiento: 25, humMin: 25, humMax: 45, tempMin: 15, tempMax: 30, companeras: ['tomate','pimiento'],              enemigos: ['salvia','ruda'] },
    { id: 'perejil_liso',      nombre: 'Perejil Liso',      emoji: '🌿', grupo: 'aromaticas',  dias: '60-80',   espaciamiento: 15, humMin: 30, humMax: 50, tempMin: 8,  tempMax: 25, companeras: ['tomate','zanahoria'],             enemigos: ['lechuga'] },
    { id: 'cilantro',          nombre: 'Cilantro',          emoji: '🌿', grupo: 'aromaticas',  dias: '40-55',   espaciamiento: 10, humMin: 30, humMax: 50, tempMin: 10, tempMax: 25, companeras: ['tomate','espinaca'],              enemigos: ['hinojo'] },
    { id: 'oregano',           nombre: 'Orégano',           emoji: '🌿', grupo: 'aromaticas',  dias: '80-100',  espaciamiento: 30, humMin: 20, humMax: 40, tempMin: 10, tempMax: 30, companeras: ['tomate','pimiento','albahaca'],   enemigos: [] },
    { id: 'tomillo',           nombre: 'Tomillo',           emoji: '🌿', grupo: 'aromaticas',  dias: '80-100',  espaciamiento: 25, humMin: 20, humMax: 35, tempMin: 8,  tempMax: 28, companeras: ['repollo','fresa','zanahoria'],    enemigos: [] },
    { id: 'cebollin',          nombre: 'Cebollín',          emoji: '🌿', grupo: 'aromaticas',  dias: '60-80',   espaciamiento: 15, humMin: 30, humMax: 50, tempMin: 8,  tempMax: 25, companeras: ['zanahoria','tomate','lechuga'],   enemigos: ['frijol','arveja'] },
    { id: 'menta',             nombre: 'Menta',             emoji: '🌿', grupo: 'aromaticas',  dias: '60-90',   espaciamiento: 30, humMin: 35, humMax: 60, tempMin: 5,  tempMax: 25, companeras: ['tomate','repollo'],               enemigos: ['manzanilla'] },
    { id: 'hierbabuena',       nombre: 'Hierbabuena',       emoji: '🌿', grupo: 'aromaticas',  dias: '60-90',   espaciamiento: 30, humMin: 35, humMax: 55, tempMin: 10, tempMax: 25, companeras: ['repollo','tomate','zanahoria'],   enemigos: ['perejil','manzanilla'] },
    { id: 'romero',            nombre: 'Romero',            emoji: '🌿', grupo: 'aromaticas',  dias: '120-180', espaciamiento: 40, humMin: 15, humMax: 35, tempMin: 8,  tempMax: 30, companeras: ['repollo','zanahoria','frijol'],   enemigos: [] },
    { id: 'calendula',         nombre: 'Caléndula',         emoji: '🌼', grupo: 'aromaticas',  dias: '50-70',   espaciamiento: 30, humMin: 25, humMax: 45, tempMin: 8,  tempMax: 25, companeras: ['tomate','lechuga','zanahoria','repollo','brocoli','coliflor'], enemigos: [] },
    { id: 'aji_jalapeno',      nombre: 'Ají Jalapeño',      emoji: '🌶️', grupo: 'aromaticas',  dias: '70-90',   espaciamiento: 45, humMin: 25, humMax: 40, tempMin: 15, tempMax: 30, companeras: ['tomate','albahaca','zanahoria','cebolla','calendula'], enemigos: ['hinojo','repollo','brocoli','coliflor'] },
    // BRÁSICAS
    { id: 'brocoli',           nombre: 'Brócoli',           emoji: '🥦', grupo: 'brasicas',    dias: '60-80',   espaciamiento: 40, humMin: 30, humMax: 50, tempMin: 10, tempMax: 24, companeras: ['cebolla','menta','romero'],       enemigos: ['tomate','fresa'] },
    { id: 'coliflor_blanca',   nombre: 'Coliflor Blanca',   emoji: '🥦', grupo: 'brasicas',    dias: '70-90',   espaciamiento: 45, humMin: 30, humMax: 50, tempMin: 10, tempMax: 22, companeras: ['cebolla','apio','menta'],         enemigos: ['tomate','fresa'] },
    { id: 'coliflor_verde',    nombre: 'Coliflor Verde',    emoji: '🥦', grupo: 'brasicas',    dias: '70-90',   espaciamiento: 45, humMin: 30, humMax: 50, tempMin: 10, tempMax: 22, companeras: ['cebolla','apio'],                 enemigos: ['tomate','fresa'] },
    { id: 'repollo_verde',     nombre: 'Repollo Verde',     emoji: '🥬', grupo: 'brasicas',    dias: '80-100',  espaciamiento: 40, humMin: 30, humMax: 50, tempMin: 8,  tempMax: 24, companeras: ['cebolla','menta','tomillo'],      enemigos: ['tomate','fresa'] },
    { id: 'repollo_morado',    nombre: 'Repollo Morado',    emoji: '🥬', grupo: 'brasicas',    dias: '85-110',  espaciamiento: 40, humMin: 30, humMax: 50, tempMin: 8,  tempMax: 24, companeras: ['cebolla','menta','tomillo'],      enemigos: ['tomate','fresa'] },
    { id: 'kale_toscano',      nombre: 'Kale Toscano',      emoji: '🥬', grupo: 'brasicas',    dias: '55-70',   espaciamiento: 35, humMin: 30, humMax: 50, tempMin: 5,  tempMax: 25, companeras: ['cebolla','remolacha','cebollin'], enemigos: ['tomate','fresa'] },
    { id: 'kale_rizado',       nombre: 'Kale Rizado',       emoji: '🥬', grupo: 'brasicas',    dias: '55-70',   espaciamiento: 35, humMin: 30, humMax: 50, tempMin: 5,  tempMax: 25, companeras: ['cebolla','remolacha'],            enemigos: ['tomate','fresa'] },
    // RAÍCES
    { id: 'cebolla_larga',     nombre: 'Cebolla Larga',     emoji: '🧅', grupo: 'raices',      dias: '90-120',  espaciamiento: 10, humMin: 25, humMax: 45, tempMin: 10, tempMax: 25, companeras: ['zanahoria','lechuga','remolacha'],enemigos: ['frijol','arveja'] },
    { id: 'zanahoria',         nombre: 'Zanahoria',         emoji: '🥕', grupo: 'raices',      dias: '70-90',   espaciamiento: 5,  humMin: 30, humMax: 50, tempMin: 8,  tempMax: 24, companeras: ['cebolla','lechuga','tomate'],     enemigos: ['eneldo'] },
    { id: 'remolacha',         nombre: 'Remolacha',         emoji: '🥕', grupo: 'raices',      dias: '55-70',   espaciamiento: 10, humMin: 30, humMax: 50, tempMin: 8,  tempMax: 24, companeras: ['lechuga','cebolla','repollo'],    enemigos: ['frijol'] },
    // INVERNADERO
    { id: 'tomate_san_marzano',    nombre: 'Tomate San Marzano',    emoji: '🍅', grupo: 'invernadero', dias: '75-90', espaciamiento: 50, humMin: 20, humMax: 35, tempMin: 18, tempMax: 30, companeras: ['albahaca','cebollin','zanahoria'], enemigos: ['brocoli','repollo'] },
    { id: 'tomate_cherry',         nombre: 'Tomate Cherry',         emoji: '🍅', grupo: 'invernadero', dias: '60-75', espaciamiento: 40, humMin: 20, humMax: 35, tempMin: 18, tempMax: 32, companeras: ['albahaca','cebollin','zanahoria'], enemigos: ['brocoli','repollo'] },
    { id: 'tomate_chonto',         nombre: 'Tomate Chonto',         emoji: '🍅', grupo: 'invernadero', dias: '70-85', espaciamiento: 50, humMin: 20, humMax: 35, tempMin: 18, tempMax: 30, companeras: ['albahaca','cebollin','zanahoria'], enemigos: ['brocoli','repollo'] },
    { id: 'albahaca_invernadero',  nombre: 'Albahaca (Invernadero)',emoji: '🌿', grupo: 'invernadero', dias: '50-70', espaciamiento: 25, humMin: 25, humMax: 45, tempMin: 15, tempMax: 30, companeras: ['tomate'],                          enemigos: ['salvia','ruda'] },
  ];

  /** Botanical family + bosque de niebla metadata enrichment.
   *  Fused into PLANT_MAP so every plant object gets: familia, riesgoHongos,
   *  termofilico, antifungico. Fuente: companion_planting_matrix.json + manual. */
  var PLANT_ENRICHMENT = {
    lechuga_batavia:       { familia: 'asteraceae',     riesgoHongos: 'alto',  termofilico: false, antifungico: false },
    lechuga_romana:        { familia: 'asteraceae',     riesgoHongos: 'alto',  termofilico: false, antifungico: false },
    lechuga_crespa:        { familia: 'asteraceae',     riesgoHongos: 'alto',  termofilico: false, antifungico: false },
    lechuga_morada_lisa:   { familia: 'asteraceae',     riesgoHongos: 'alto',  termofilico: false, antifungico: false },
    rucula:                { familia: 'brassicaceae',   riesgoHongos: 'medio', termofilico: false, antifungico: false },
    espinaca:              { familia: 'amaranthaceae',  riesgoHongos: 'alto',  termofilico: false, antifungico: false },
    acelga_comun:          { familia: 'amaranthaceae',  riesgoHongos: 'alto',  termofilico: false, antifungico: false },
    acelga_roja:           { familia: 'amaranthaceae',  riesgoHongos: 'alto',  termofilico: false, antifungico: false },
    acelga_amarilla:       { familia: 'amaranthaceae',  riesgoHongos: 'alto',  termofilico: false, antifungico: false },
    mizuna_verde:          { familia: 'brassicaceae',   riesgoHongos: 'medio', termofilico: false, antifungico: false },
    mizuna_roja:           { familia: 'brassicaceae',   riesgoHongos: 'medio', termofilico: false, antifungico: false },
    mostaza_red:           { familia: 'brassicaceae',   riesgoHongos: 'medio', termofilico: false, antifungico: false },
    tat_soi:               { familia: 'brassicaceae',   riesgoHongos: 'medio', termofilico: false, antifungico: false },
    albahaca:              { familia: 'lamiaceae',      riesgoHongos: 'alto',  termofilico: true,  antifungico: false },
    albahaca_morada:       { familia: 'lamiaceae',      riesgoHongos: 'alto',  termofilico: true,  antifungico: false },
    perejil_liso:          { familia: 'apiaceae',       riesgoHongos: 'medio', termofilico: false, antifungico: false },
    cilantro:              { familia: 'apiaceae',       riesgoHongos: 'medio', termofilico: false, antifungico: false },
    oregano:               { familia: 'lamiaceae',      riesgoHongos: 'bajo',  termofilico: true,  antifungico: true  },
    tomillo:               { familia: 'lamiaceae',      riesgoHongos: 'bajo',  termofilico: false, antifungico: true  },
    cebollin:              { familia: 'amaryllidaceae', riesgoHongos: 'bajo',  termofilico: false, antifungico: true  },
    menta:                 { familia: 'lamiaceae',      riesgoHongos: 'medio', termofilico: false, antifungico: false },
    hierbabuena:           { familia: 'lamiaceae',      riesgoHongos: 'medio', termofilico: false, antifungico: false },
    romero:                { familia: 'lamiaceae',      riesgoHongos: 'bajo',  termofilico: false, antifungico: true  },
    calendula:             { familia: 'asteraceae',     riesgoHongos: 'bajo',  termofilico: false, antifungico: false },
    aji_jalapeno:          { familia: 'solanaceae',     riesgoHongos: 'alto',  termofilico: true,  antifungico: false },
    brocoli:               { familia: 'brassicaceae',   riesgoHongos: 'alto',  termofilico: false, antifungico: false },
    coliflor_blanca:       { familia: 'brassicaceae',   riesgoHongos: 'alto',  termofilico: false, antifungico: false },
    coliflor_verde:        { familia: 'brassicaceae',   riesgoHongos: 'alto',  termofilico: false, antifungico: false },
    repollo_verde:         { familia: 'brassicaceae',   riesgoHongos: 'alto',  termofilico: false, antifungico: false },
    repollo_morado:        { familia: 'brassicaceae',   riesgoHongos: 'alto',  termofilico: false, antifungico: false },
    kale_toscano:          { familia: 'brassicaceae',   riesgoHongos: 'medio', termofilico: false, antifungico: false },
    kale_rizado:           { familia: 'brassicaceae',   riesgoHongos: 'medio', termofilico: false, antifungico: false },
    cebolla_larga:         { familia: 'amaryllidaceae', riesgoHongos: 'bajo',  termofilico: false, antifungico: false },
    zanahoria:             { familia: 'apiaceae',       riesgoHongos: 'bajo',  termofilico: false, antifungico: false },
    remolacha:             { familia: 'amaranthaceae',  riesgoHongos: 'bajo',  termofilico: false, antifungico: false },
    tomate_san_marzano:    { familia: 'solanaceae',     riesgoHongos: 'alto',  termofilico: true,  antifungico: false },
    tomate_cherry:         { familia: 'solanaceae',     riesgoHongos: 'alto',  termofilico: true,  antifungico: false },
    tomate_chonto:         { familia: 'solanaceae',     riesgoHongos: 'alto',  termofilico: true,  antifungico: false },
    albahaca_invernadero:  { familia: 'lamiaceae',      riesgoHongos: 'alto',  termofilico: true,  antifungico: false },
  };

  /** Labels legibles de familias botánicas */
  var FAMILIA_LABELS = {
    asteraceae:     'Asteráceas (compuestas)',
    brassicaceae:   'Brassicáceas (coles)',
    amaranthaceae:  'Amarantáceas',
    lamiaceae:      'Lamiáceas (aromáticas)',
    apiaceae:       'Apiáceas (umbelíferas)',
    amaryllidaceae: 'Amarilidáceas (aliáceas)',
    solanaceae:     'Solanáceas',
  };

  /** Reglas del bosque de niebla (fuente: companion_planting_matrix.json) */
  var BOSQUE_NIEBLA_REGLAS = [
    'Alta humedad ambiental (70-98%): favorecer plantas con buena circulación de aire para evitar hongos.',
    'Temperaturas frescas (12-24°C): priorizar cultivos de clima frío; evitar termófilos sin protección.',
    'Neblina frecuente: las aromáticas mediterráneas (romero, orégano, tomillo) actúan como antifúngicos naturales.',
    'Suelo húmedo natural: brásicas y hojas agradecen, pero los tomates necesitan el invernadero.',
    'Altitud 1780 msnm: ciclos de crecimiento un 20-30% más lentos que en tierras bajas.',
  ];

  var ANTIFUNGICOS_IDS = ['tomillo','oregano','romero','cebollin'];

  /** Quick lookup map: plantId -> plant object (enriched with PLANT_ENRICHMENT) */
  var PLANT_MAP = Object.fromEntries(
    PLANT_CATALOG.map(p => [p.id, { ...p, ...(PLANT_ENRICHMENT[p.id] || {}) }])
  );

  /* ──────────────────────────────────────────
     DEFAULT BED PLANT ASSIGNMENTS
  ────────────────────────────────────────── */
  // Siembra real reportada por Jhon Huerta el 2026-04-07
  var DEFAULT_BED_PLANTS = {
    cama1:       ['repollo_morado', 'coliflor_blanca', 'cebollin'],
    cama2:       ['zanahoria', 'perejil_liso'],
    cama3:       ['lechuga_crespa', 'lechuga_morada_lisa'],
    cama4:       ['acelga_comun', 'calendula'],
    cama5:       ['calendula', 'aji_jalapeno', 'repollo_morado'],
    cama6:       ['repollo_morado'],
    cama7:       ['cebolla_larga', 'hierbabuena'],
    cama8:       ['tomillo'],
    cama9:       [],
    cama10:      ['remolacha', 'coliflor_blanca', 'repollo_morado'],
    cama11:      [],
    cama12:      [],
    invernadero: ['tomate_san_marzano', 'tomate_cherry', 'tomate_chonto'],
  };

  /** localStorage key for plant assignments — bumped to v2 on 2026-04-07
   *  to force-reset stale plant data saved before the real-planting update. */
  var LS_KEY = 'huerta_bed_plants_v2';

  /** localStorage keys for sensor assignment system */
  var LS_SENSOR_ASSIGNMENTS = 'huerta_sensor_assignments';
  var LS_BED_READINGS        = 'huerta_bed_readings';

  /* ──────────────────────────────────────────
     CONFIG
  ────────────────────────────────────────── */
  var CONFIG = {
    applicationKey:          '2A298127832EF7B5F0495F16B07F7B5E',
    apiKey:                  '83b66e21-a6cf-445f-b14e-2810189d3e6d',
    mac:                     '8C:4F:00:4F:C1:E6',
    apiBase:                 'https://api.ecowitt.net/api/v3',
    unitParams:              'temp_unitid=1&pressure_unitid=3&rainfall_unitid=12',
    refreshInterval:         300000,   // 5 min (real-time)
    historyRefreshInterval:  1800000,  // 30 min (history)
    soilAlertThreshold:      35,
    soilOptimalMin:          50,
    soilOptimalMax:          80,
  };

  /* Channel labels & chart colours */
  var SOIL_CHANNELS = [
    { key: 'soil_ch1', label: 'CH1 — Cama 3 (Hojas)',         color: '#00D68F' },
    { key: 'soil_ch2', label: 'CH2 — Cama 1 (Hojas)',         color: '#4ECDC4' },
    { key: 'soil_ch3', label: 'CH3 — Cama 4 (Hojas)',         color: '#A855F7' },
    { key: 'soil_ch4', label: 'CH4 — Invernadero (Tomate)',   color: '#FFB800' },
    { key: 'soil_ch5', label: 'CH5 — Cama 2 (Hojas)',         color: '#FF6B6B' },
  ];

  var BATTERY_SENSOR_NAMES = {
    outdoor_t_rh_sensor:        'Exterior (WH32)',
    temp_humidity_sensor_ch1:   'Termo CH1 (WN31)',
    soilmoisture_sensor_ch1:    'Suelo CH1',
    soilmoisture_sensor_ch2:    'Suelo CH2',
    soilmoisture_sensor_ch3:    'Suelo CH3',
    soilmoisture_sensor_ch4:    'Suelo CH4',
    soilmoisture_sensor_ch5:    'Suelo CH5',
  };

  /* ──────────────────────────────────────────
     BED MAP DATA
  ────────────────────────────────────────── */

  /**
   * Sensor-to-bed mapping.
   * beds: which bed IDs share this sensor reading.
   */
  var SENSOR_BED_MAP = {
    'soil_ch1': { beds: ['cama3', 'cama5', 'cama7'],    label: 'CH1 → Cama 3 (+ 5,7)',    group: 'hojas',    sensorIn: 'Cama 3' },
    'soil_ch2': { beds: ['cama1', 'cama2', 'cama4'],    label: 'CH2 → Cama 1 (+ 2,4)',    group: 'hojas',    sensorIn: 'Cama 1' },
    'soil_ch3': { beds: ['cama6', 'cama8', 'cama9'],    label: 'CH3 → Cama 4 (+ 6,8,9)',  group: 'hojas',    sensorIn: 'Cama 4' },
    'soil_ch4': { beds: ['invernadero'],                 label: 'CH4 → Invernadero',        group: 'tomate',   sensorIn: 'Invernadero' },
    'soil_ch5': { beds: ['cama10', 'cama11', 'cama12'], label: 'CH5 → Cama 2 (+ 10-12)',  group: 'hojas',    sensorIn: 'Cama 2' },
  };

  /** Crop-specific moisture thresholds (separate from cloud-forest bars above). */
  var CROP_THRESHOLDS = {
    hojas:    { optMin: 30, optMax: 45, alert: 28, critical: 22, label: 'Hojas' },
    hierbas:  { optMin: 30, optMax: 45, alert: 28, critical: 22, label: 'Hierbas' },
    brasicas: { optMin: 25, optMax: 40, alert: 22, critical: 18, label: 'Brásicas' },
    tomate:   { optMin: 20, optMax: 30, alert: 18, critical: 15, label: 'Tomate' },
    rotacion: { optMin: 25, optMax: 40, alert: 22, critical: 18, label: 'Rotación' },
  };

  /** Full bed definitions — impares = derecha, pares = izquierda.
   *  Actualizado 2026-04-07 con siembra real reportada por Jhon Huerta. */
  var BEDS = [
    { id: 'cama1',  name: 'Cama 1',  group: 'brasicas', crops: ['🥬 Repollo morado', '🥦 Coliflor', '🌿 Cebollín'],        sensor: 'soil_ch2', hasSensor: true },
    { id: 'cama2',  name: 'Cama 2',  group: 'hierbas',  crops: ['🥕 Zanahoria', '🌿 Perejil liso'],                         sensor: 'soil_ch5', hasSensor: true },
    { id: 'cama3',  name: 'Cama 3',  group: 'hojas',    crops: ['🥬 Lechuga crespa', '🥬 Lechuga morada lisa'],             sensor: 'soil_ch1', hasSensor: true },
    { id: 'cama4',  name: 'Cama 4',  group: 'hojas',    crops: ['🥬 Acelga', '🌼 Caléndula'],                                sensor: 'soil_ch3', hasSensor: true },
    { id: 'cama5',  name: 'Cama 5',  group: 'brasicas', crops: ['🌼 Caléndula', '🌶️ Ají jalapeño', '🥬 Repollo morado'],     sensor: 'soil_ch1' },
    { id: 'cama6',  name: 'Cama 6',  group: 'brasicas', crops: ['🥬 Repollo morado'],                                       sensor: 'soil_ch3' },
    { id: 'cama7',  name: 'Cama 7',  group: 'hierbas',  crops: ['🌿 Cebolla larga', '🌿 Hierbabuena'],                      sensor: 'soil_ch1' },
    { id: 'cama8',  name: 'Cama 8',  group: 'hierbas',  crops: ['🌿 Tomillo'],                                              sensor: 'soil_ch3' },
    { id: 'cama9',  name: 'Cama 9',  group: 'rotacion', crops: ['🟤 Vacía'],                                                sensor: 'soil_ch3' },
    { id: 'cama10', name: 'Cama 10', group: 'brasicas', crops: ['🟣 Remolacha', '🥦 Coliflor', '🥬 Repollo morado'],        sensor: 'soil_ch5' },
    { id: 'cama11', name: 'Cama 11', group: 'rotacion', crops: ['🟤 Vacía'],                                                sensor: 'soil_ch5' },
    { id: 'cama12', name: 'Cama 12', group: 'rotacion', crops: ['🟤 Vacía'],                                                sensor: 'soil_ch5' },
  ];

  /** Group display labels. */
  var GROUP_LABELS = {
    hojas:    'Hojas',
    hierbas:  'Hierbas',
    brasicas: 'Brásicas',
    rotacion: 'Rotación',
  };

/* ──────────────────────────────────────────
     STATE
  ────────────────────────────────────────── */
  var historyChart       = null;
  var countdownSeconds   = CONFIG.refreshInterval / 1000;
  var countdownTimer     = null;
  var lastDataTimestamp  = null;
