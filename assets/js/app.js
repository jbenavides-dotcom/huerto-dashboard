'use strict';

/* ──────────────────────────────────────────
     UPDATE: HISTORY CHART
  ────────────────────────────────────────── */
  function updateHistory(data) {
    // Build datasets for soil channels
    const soilDatasets = SOIL_CHANNELS.map(ch => {
      const soilList = data[ch.key]?.soilmoisture?.list || {};
      const points = Object.entries(soilList).map(([ts, val]) => ({
        x: new Date(parseInt(ts, 10) * 1000),
        y: parseFloat(val),
      })).sort((a, b) => a.x - b.x);

      return {
        label:           ch.label,
        data:            points,
        borderColor:     ch.color,
        backgroundColor: ch.color + '18',
        borderWidth:     2,
        pointRadius:     0,
        pointHoverRadius:4,
        tension:         0.3,
        yAxisID:         'ySoil',
        fill:            false,
      };
    });

    // Temperature dataset (secondary Y)
    const tempList = data.outdoor?.temperature?.list || {};
    const tempPoints = Object.entries(tempList).map(([ts, val]) => ({
      x: new Date(parseInt(ts, 10) * 1000),
      y: parseFloat(val),
    })).sort((a, b) => a.x - b.x);

    const tempDataset = {
      label:           'Temp. Exterior (°C)',
      data:            tempPoints,
      borderColor:     '#FF8A95',
      backgroundColor: '#FF4757' + '10',
      borderWidth:     1.5,
      borderDash:      [4, 4],
      pointRadius:     0,
      pointHoverRadius:4,
      tension:         0.3,
      yAxisID:         'yTemp',
      fill:            false,
    };

    const allDatasets = [...soilDatasets, tempDataset];

    const annotations = {
      dryLine: {
        type: 'line',
        yMin: CONFIG.soilAlertThreshold,
        yMax: CONFIG.soilAlertThreshold,
        borderColor: 'rgba(255,71,87,0.6)',
        borderWidth: 1,
        borderDash: [6, 4],
        yScaleID: 'ySoil',
        label: { content: 'Riego 35%', display: true, position: 'end', color: '#FF4757', font: { size: 10 }, yAdjust: -8 },
      },
      wetLine: {
        type: 'line',
        yMin: CONFIG.soilOptimalMax,
        yMax: CONFIG.soilOptimalMax,
        borderColor: 'rgba(78,205,196,0.6)',
        borderWidth: 1,
        borderDash: [6, 4],
        yScaleID: 'ySoil',
        label: { content: 'Exceso 80%', display: true, position: 'end', color: '#4ECDC4', font: { size: 10 }, yAdjust: 8 },
      },
    };

    if (historyChart) {
      historyChart.data.datasets = allDatasets;
      historyChart.update('none');
    } else {
      const ctx = document.getElementById('historyChart').getContext('2d');
      historyChart = new Chart(ctx, {
        type: 'line',
        data: { datasets: allDatasets },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: 'index', intersect: false },
          plugins: {
            legend: {
              position: 'top',
              labels: { color: '#8888AA', font: { size: 11 }, boxWidth: 14, padding: 16 },
            },
            tooltip: {
              backgroundColor: '#1A1A2E',
              borderColor: '#2A2A4A',
              borderWidth: 1,
              titleColor: '#E8E8F0',
              bodyColor: '#8888AA',
              padding: 10,
              callbacks: {
                title: items => {
                  if (!items.length) return '';
                  return formatTime(items[0].raw.x);
                },
                label: item => {
                  const v = item.raw.y;
                  const unit = item.dataset.yAxisID === 'yTemp' ? '°C' : '%';
                  return ` ${item.dataset.label}: ${v !== undefined ? v.toFixed(1) : '—'}${unit}`;
                },
              },
            },
            annotation: { annotations },
          },
          scales: {
            x: {
              type: 'time',
              time: { unit: 'hour', tooltipFormat: 'HH:mm', displayFormats: { hour: 'HH:mm' } },
              ticks: { color: '#8888AA', font: { size: 10 }, maxTicksLimit: 12 },
              grid:  { color: 'rgba(42,42,74,0.6)' },
            },
            ySoil: {
              type: 'linear',
              position: 'left',
              min: 0,
              max: 100,
              title: { display: true, text: 'Humedad del suelo (%)', color: '#8888AA', font: { size: 11 } },
              ticks: { color: '#8888AA', font: { size: 10 }, stepSize: 10 },
              grid:  { color: 'rgba(42,42,74,0.6)' },
            },
            yTemp: {
              type: 'linear',
              position: 'right',
              title: { display: true, text: 'Temperatura (°C)', color: '#FF8A95', font: { size: 11 } },
              ticks: { color: '#FF8A95', font: { size: 10 } },
              grid:  { drawOnChartArea: false },
            },
          },
        },
      });
    }
  }

  /* ──────────────────────────────────────────
     MAIN UPDATE DASHBOARD
  ────────────────────────────────────────── */
  function updateDashboard(data) {
    // Determine timestamp for status dot (outdoor sensor time)
    const ts = parseInt(data.outdoor?.temperature?.time, 10) || null;
    lastDataTimestamp = ts;
    updateStatusDot(ts);

    // Last updated display
    setText('lastUpdated', formatDatetime(new Date()));

    updateKPI(data);
    updateSoil(data);
    updateBedMap(data);
    updateCompanionship();
    updateNotifications(data);
    updateClima(data);
    updateRain(data);
    updateBattery(data);
    checkBrowserAlerts(data);
    updateRecommendations(data);

    hideError('globalError');
  }

  /* ──────────────────────────────────────────
     COUNTDOWN TIMER
  ────────────────────────────────────────── */
  function startCountdown() {
    if (countdownTimer) clearInterval(countdownTimer);
    countdownSeconds = CONFIG.refreshInterval / 1000;

    countdownTimer = setInterval(() => {
      countdownSeconds--;
      if (countdownSeconds < 0) countdownSeconds = 0;
      const m = Math.floor(countdownSeconds / 60);
      const s = countdownSeconds % 60;
      setText('countdownDisplay', `${m}:${String(s).padStart(2, '0')}`);
    }, 1000);
  }

  /* ──────────────────────────────────────────
     REFRESH BUTTON SPIN
  ────────────────────────────────────────── */
  function setRefreshSpinning(spinning) {
    const btn = document.getElementById('refreshBtn');
    if (spinning) btn.classList.add('spinning');
    else           btn.classList.remove('spinning');
    btn.disabled = spinning;
  }

  /* ──────────────────────────────────────────
     LOAD REALTIME DATA
  ────────────────────────────────────────── */
  async function loadRealtime() {
    setRefreshSpinning(true);
    try {
      const data = await fetchRealtime();
      updateDashboard(data);
      startCountdown();
    } catch (err) {
      console.error('Realtime fetch error:', err);
      showError('globalError', `Error al obtener datos: ${err.message}. Se reintentará en ${CONFIG.refreshInterval / 60000} minutos.`);
    } finally {
      setRefreshSpinning(false);
    }
  }

  /* ──────────────────────────────────────────
     LOAD HISTORY DATA
  ────────────────────────────────────────── */
  async function loadHistory() {
    try {
      const data = await fetchHistory();
      updateHistory(data);
      hideError('historyError');
    } catch (err) {
      console.error('History fetch error:', err);
      showError('historyError', `Error al cargar historial: ${err.message}`);
    }
  }

  /* ──────────────────────────────────────────
     MANUAL REFRESH
  ────────────────────────────────────────── */
  function manualRefresh() {
    loadRealtime();
  }

  async function init() {
    // Request notification permission on first load
    await requestNotifPermission();

    // Check Supabase availability (non-blocking for the rest of init)
    await checkSupabaseAvailable();
    if (SUPABASE.available) {
      // Sync camas + bitacora before first render
      await Promise.allSettled([
        syncCamasFromSupabase(),
        syncBitacoraFromSupabase(),
      ]);
    }

    // Render greenhouse crops immediately from localStorage (no API needed)
    renderGreenhouseCrops();

    // Populate glossary
    populateGlossary();

    // Load bitacora
    loadBitacora();
    renderBitacora();

    // Load companion planting matrix (cached in module-level variable)
    fetchCompanionMatrix();

    // Load both in parallel on first load
    await Promise.allSettled([loadRealtime(), loadHistory()]);

    // Schedule auto-refresh for real-time data
    setInterval(loadRealtime, CONFIG.refreshInterval);

    // Schedule auto-refresh for history
    setInterval(loadHistory, CONFIG.historyRefreshInterval);
  }

  // Kick off
  init();
