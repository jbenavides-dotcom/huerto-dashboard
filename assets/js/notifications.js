'use strict';

  // notifPermission is declared in config.js (Safari iOS TDZ fix)

/* ──────────────────────────────────────────
     BROWSER PUSH NOTIFICATIONS
  ────────────────────────────────────────── */
  // notifPermission declarada temprano para evitar TDZ en Safari iOS
  // (la declaración original causaba "Cannot access before initialization")

  async function requestNotifPermission() {
    if (!('Notification' in window)) return;
    if (notifPermission === 'default') {
      notifPermission = await Notification.requestPermission();
    }
  }

  function sendBrowserNotif(title, body, tag) {
    if (notifPermission !== 'granted') return;
    try {
      new Notification(title, {
        body,
        icon: '🌱',
        tag, // prevents duplicate notifs with same tag
        requireInteraction: true,
      });
    } catch (e) { /* silent fail on iOS if not supported */ }
  }

  /**
   * Check data and fire browser notifications for critical conditions.
   * Called from updateDashboard after each refresh.
   */
  function checkBrowserAlerts(data) {
    if (notifPermission !== 'granted') return;

    const alerts = [];

    // Soil alerts — only for beds with an active sensor assignment
    const sensorAssignments = loadSensorAssignments();
    Object.entries(sensorAssignments).forEach(([bedId, sensorKey]) => {
      if (!sensorKey) return;
      const pct = parseVal(data[sensorKey]?.soilmoisture?.value);
      if (pct === null) return;
      const bed = BEDS.find(b => b.id === bedId);
      const group = bed ? bed.group : (bedId === 'invernadero' ? 'tomate' : 'hojas');
      const t = CROP_THRESHOLDS[group] || CROP_THRESHOLDS.rotacion;
      const chNum = sensorKey.replace('soil_ch', 'CH');
      const bedName = bed ? bed.name : (bedId === 'invernadero' ? 'Invernadero' : bedId);
      if (pct < t.critical) {
        alerts.push(`🚨 ${chNum} (${bedName}): ${Math.round(pct)}% — ¡Riego urgente!`);
      } else if (pct < t.alert) {
        alerts.push(`⚠️ ${chNum} (${bedName}): ${Math.round(pct)}% — Riego recomendado`);
      }
    });

    // Rain alert
    const rainRate = parseVal(data.rainfall?.rain_rate?.value);
    if (rainRate !== null && rainRate > 0) {
      alerts.push(`🌧️ Lluvia activa: ${rainRate.toFixed(1)} mm/hr`);
    }

    // Frost alert
    const tempExt = parseVal(data.outdoor?.temperature?.value);
    if (tempExt !== null && tempExt < 8) {
      alerts.push(`🥶 Temperatura ${tempExt.toFixed(1)}°C — Proteger cultivos`);
    }

    // Battery alert
    const battery = data.battery || {};
    Object.entries(battery).forEach(([key, batt]) => {
      if (batt.unit === 'V' && parseVal(batt.value) < 1.2) {
        const name = BATTERY_SENSOR_NAMES[key] || key;
        alerts.push(`🔋 ${name}: batería baja ${batt.value}V`);
      }
    });

    // Send one combined notification if there are alerts
    if (alerts.length > 0) {
      sendBrowserNotif(
        `Huerto — ${alerts.length} alerta${alerts.length > 1 ? 's' : ''}`,
        alerts.join('\n'),
        'huerto-alert'
      );
    }
  }
