'use strict';

/* ──────────────────────────────────────────
     BITACORA DE CULTIVO
  ────────────────────────────────────────── */
  var TIPO_LABELS = {
    siembra: 'Siembra', cosecha: 'Cosecha', fertilizacion: 'Fertilización',
    riego_manual: 'Riego manual', plagas: 'Plagas', observacion: 'Observación'
  };

  var bitacoraData = [];
  var bitacoraChartCama = null;
  var bitacoraChartPlanta = null;
  var bitacoraChartTendencia = null;

  function loadBitacora() {
    try {
      bitacoraData = JSON.parse(localStorage.getItem('huerta_bitacora') || '[]');
    } catch { bitacoraData = []; }
    // Populate cama filter
    const camaFilter = document.getElementById('bitacoraFilterCama');
    if (camaFilter && camaFilter.options.length <= 1) {
      BEDS.forEach(b => {
        const o = document.createElement('option');
        o.value = b.id; o.textContent = b.name;
        camaFilter.appendChild(o);
      });
      const oInv = document.createElement('option');
      oInv.value = 'invernadero'; oInv.textContent = 'Invernadero';
      camaFilter.appendChild(oInv);
    }
    // Populate month filter from data
    populateBitacoraMeses();
    // Populate modal selects
    populateBitacoraModalSelects();
  }

  function saveBitacora() {
    localStorage.setItem('huerta_bitacora', JSON.stringify(bitacoraData));
  }

  function populateBitacoraMeses() {
    const sel = document.getElementById('bitacoraFilterMes');
    if (!sel) return;
    const current = sel.value;
    const months = new Set();
    bitacoraData.forEach(e => { if (e.fecha) months.add(e.fecha.slice(0, 7)); });
    const sorted = [...months].sort().reverse();
    sel.innerHTML = '<option value="">Todos los meses</option>';
    sorted.forEach(m => {
      const o = document.createElement('option');
      o.value = m;
      const [y, mo] = m.split('-');
      const names = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
      o.textContent = names[parseInt(mo)-1] + ' ' + y;
      sel.appendChild(o);
    });
    if (current) sel.value = current;
  }

  function populateBitacoraModalSelects() {
    // Cama select in modal
    const camaSel = document.getElementById('btk_cama');
    if (camaSel && camaSel.options.length <= 1) {
      BEDS.forEach(b => {
        const o = document.createElement('option');
        o.value = b.id; o.textContent = b.name;
        camaSel.appendChild(o);
      });
      const oInv = document.createElement('option');
      oInv.value = 'invernadero'; oInv.textContent = 'Invernadero';
      camaSel.appendChild(oInv);
    }
    // Planta select in modal
    const plantaSel = document.getElementById('btk_planta');
    if (plantaSel && plantaSel.options.length <= 1) {
      const groups = {};
      PLANT_CATALOG.forEach(p => {
        if (!groups[p.grupo]) groups[p.grupo] = [];
        groups[p.grupo].push(p);
      });
      Object.keys(groups).sort().forEach(g => {
        const og = document.createElement('optgroup');
        og.label = g.charAt(0).toUpperCase() + g.slice(1);
        groups[g].forEach(p => {
          const o = document.createElement('option');
          o.value = p.id; o.textContent = p.emoji + ' ' + p.nombre;
          og.appendChild(o);
        });
        plantaSel.appendChild(og);
      });
    }
  }

  function openBitacoraModal() {
    const now = new Date();
    document.getElementById('btk_fecha').value = now.toISOString().slice(0, 10);
    document.getElementById('btk_hora').value = now.toTimeString().slice(0, 5);
    document.getElementById('btk_cama').value = '';
    document.getElementById('btk_tipo').value = '';
    document.getElementById('btk_planta').value = '';
    document.getElementById('btk_cantidad').value = '';
    document.getElementById('btk_unidad').value = 'kg';
    document.getElementById('btk_nota').value = '';
    document.getElementById('btk_cantidad_row').classList.remove('visible');
    document.getElementById('bitacoraModalOverlay').classList.add('open');
  }

  function closeBitacoraModal() {
    document.getElementById('bitacoraModalOverlay').classList.remove('open');
  }

  function onBitacoraTipoChange() {
    const tipo = document.getElementById('btk_tipo').value;
    const row = document.getElementById('btk_cantidad_row');
    if (tipo === 'cosecha') row.classList.add('visible');
    else row.classList.remove('visible');
  }

  function saveBitacoraEntry() {
    const fecha = document.getElementById('btk_fecha').value;
    const hora = document.getElementById('btk_hora').value;
    const cama = document.getElementById('btk_cama').value;
    const tipo = document.getElementById('btk_tipo').value;
    const plantaId = document.getElementById('btk_planta').value;
    const cantidad = parseFloat(document.getElementById('btk_cantidad').value) || 0;
    const unidad = document.getElementById('btk_unidad').value;
    const nota = document.getElementById('btk_nota').value.trim().slice(0, 300);

    if (!fecha || !tipo) {
      alert('Fecha y tipo de acción son obligatorios.');
      return;
    }

    const entry = {
      id: 'btk_' + Date.now(),
      fecha, hora, cama, tipo, plantaId,
      cantidad: tipo === 'cosecha' ? cantidad : 0,
      unidad: tipo === 'cosecha' ? unidad : 'kg',
      nota,
      ts: new Date(fecha + 'T' + (hora || '00:00')).getTime()
    };

    bitacoraData.push(entry);
    saveBitacora();
    pushBitacoraToSupabase(entry);
    closeBitacoraModal();
    renderBitacora();
  }

  function deleteBitacoraEntry(id) {
    if (!confirm('¿Eliminar este registro?')) return;
    bitacoraData = bitacoraData.filter(e => e.id !== id);
    saveBitacora();
    deleteBitacoraFromSupabase(id);
    renderBitacora();
  }

  function getFilteredBitacora() {
    const filterTipo = document.getElementById('bitacoraFilterTipo').value;
    const filterCama = document.getElementById('bitacoraFilterCama').value;
    const filterMes = document.getElementById('bitacoraFilterMes').value;
    let data = [...bitacoraData];
    if (filterTipo) data = data.filter(e => e.tipo === filterTipo);
    if (filterCama) data = data.filter(e => e.cama === filterCama);
    if (filterMes) data = data.filter(e => e.fecha && e.fecha.startsWith(filterMes));
    data.sort((a, b) => (b.ts || 0) - (a.ts || 0));
    return data;
  }

  function getBedName(camaId) {
    if (camaId === 'invernadero') return 'Invernadero';
    const bed = BEDS.find(b => b.id === camaId);
    return bed ? bed.name : camaId || '—';
  }

  function getPlantName(plantaId) {
    if (!plantaId) return '—';
    const p = PLANT_CATALOG.find(pl => pl.id === plantaId);
    return p ? (p.emoji + ' ' + p.nombre) : plantaId;
  }

  function renderBitacoraStats() {
    const container = document.getElementById('bitacoraStats');
    if (!container) return;
    const total = bitacoraData.length;
    const cosechas = bitacoraData.filter(e => e.tipo === 'cosecha');
    const totalKg = cosechas.reduce((s, e) => s + (e.unidad === 'kg' ? (e.cantidad || 0) : 0), 0);
    const totalUnidades = cosechas.reduce((s, e) => s + (e.unidad === 'unidades' ? (e.cantidad || 0) : 0), 0);
    const siembras = bitacoraData.filter(e => e.tipo === 'siembra').length;

    let html = '';
    html += '<span class="bitacora-stat-pill"><strong>' + total + '</strong> registros</span>';
    if (totalKg > 0) html += '<span class="bitacora-stat-pill"><strong>' + totalKg.toFixed(1) + '</strong> kg cosechados</span>';
    if (totalUnidades > 0) html += '<span class="bitacora-stat-pill"><strong>' + totalUnidades + '</strong> unidades cosechadas</span>';
    if (siembras > 0) html += '<span class="bitacora-stat-pill"><strong>' + siembras + '</strong> siembras</span>';
    container.innerHTML = html;
  }

  function renderBitacoraTable() {
    const tbody = document.getElementById('bitacoraTableBody');
    const emptyMsg = document.getElementById('bitacoraEmpty');
    const table = document.getElementById('bitacoraTable');
    if (!tbody) return;
    const data = getFilteredBitacora();

    if (data.length === 0) {
      table.style.display = 'none';
      emptyMsg.style.display = 'block';
      return;
    }
    table.style.display = '';
    emptyMsg.style.display = 'none';

    tbody.innerHTML = data.map(e => {
      const cosechaStr = e.tipo === 'cosecha' && e.cantidad ? (e.cantidad + ' ' + (e.unidad || 'kg')) : '—';
      return '<tr>' +
        '<td style="white-space:nowrap">' + e.fecha + (e.hora ? ' ' + e.hora : '') + '</td>' +
        '<td>' + getBedName(e.cama) + '</td>' +
        '<td><span class="bitacora-tipo-badge ' + e.tipo + '">' + (TIPO_LABELS[e.tipo] || e.tipo) + '</span></td>' +
        '<td>' + getPlantName(e.plantaId) + '</td>' +
        '<td>' + cosechaStr + '</td>' +
        '<td style="max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="' + (e.nota || '').replace(/"/g, '&quot;') + '">' + (e.nota || '—') + '</td>' +
        '<td><button class="bitacora-delete-btn" onclick="deleteBitacoraEntry(\'' + e.id + '\')" title="Eliminar">✕</button></td>' +
        '</tr>';
    }).join('');
  }

  function toggleBitacoraCharts() {
    const body = document.getElementById('bitacoraChartsBody');
    const chevron = document.getElementById('bitacoraChartsChevron');
    body.classList.toggle('visible');
    chevron.classList.toggle('open');
    if (body.classList.contains('visible')) renderBitacoraCharts();
  }

  function renderBitacoraCharts() {
    const cosechas = bitacoraData.filter(e => e.tipo === 'cosecha' && e.cantidad > 0 && e.unidad === 'kg');
    if (cosechas.length === 0) return;

    const chartColors = ['#00D68F','#FFB800','#4ECDC4','#A855F7','#FF4757','#FF8A65','#64B5F6','#AED581','#FFD54F','#BA68C8','#4DD0E1','#E57373','#81C784'];

    // Chart 1: Cosecha por cama (bar vertical)
    const camaTotals = {};
    cosechas.forEach(e => {
      const name = getBedName(e.cama);
      camaTotals[name] = (camaTotals[name] || 0) + e.cantidad;
    });
    const camaLabels = Object.keys(camaTotals);
    const camaValues = Object.values(camaTotals);

    if (bitacoraChartCama) bitacoraChartCama.destroy();
    const ctx1 = document.getElementById('bitacoraChartCama');
    if (ctx1) {
      bitacoraChartCama = new Chart(ctx1, {
        type: 'bar',
        data: {
          labels: camaLabels,
          datasets: [{
            data: camaValues,
            backgroundColor: camaLabels.map((_, i) => chartColors[i % chartColors.length]),
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: '#8888AA', font: { size: 10 } }, grid: { display: false } },
            y: { ticks: { color: '#8888AA', font: { size: 10 } }, grid: { color: 'rgba(42,42,74,0.4)' }, title: { display: true, text: 'kg', color: '#8888AA' } }
          }
        }
      });
    }

    // Chart 2: Cosecha por planta (bar horizontal)
    const plantaTotals = {};
    cosechas.forEach(e => {
      const name = getPlantName(e.plantaId) || 'Sin planta';
      plantaTotals[name] = (plantaTotals[name] || 0) + e.cantidad;
    });
    const plantaLabels = Object.keys(plantaTotals).sort((a,b) => plantaTotals[b] - plantaTotals[a]);
    const plantaValues = plantaLabels.map(l => plantaTotals[l]);

    if (bitacoraChartPlanta) bitacoraChartPlanta.destroy();
    const ctx2 = document.getElementById('bitacoraChartPlanta');
    if (ctx2) {
      bitacoraChartPlanta = new Chart(ctx2, {
        type: 'bar',
        data: {
          labels: plantaLabels,
          datasets: [{
            data: plantaValues,
            backgroundColor: plantaLabels.map((_, i) => chartColors[i % chartColors.length]),
            borderRadius: 4
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: '#8888AA', font: { size: 10 } }, grid: { color: 'rgba(42,42,74,0.4)' }, title: { display: true, text: 'kg', color: '#8888AA' } },
            y: { ticks: { color: '#8888AA', font: { size: 10 } }, grid: { display: false } }
          }
        }
      });
    }

    // Chart 3: Tendencia mensual (line)
    const monthTotals = {};
    cosechas.forEach(e => {
      if (!e.fecha) return;
      const m = e.fecha.slice(0, 7);
      monthTotals[m] = (monthTotals[m] || 0) + e.cantidad;
    });
    const monthLabels = Object.keys(monthTotals).sort();
    const monthValues = monthLabels.map(m => monthTotals[m]);
    const monthDisplayLabels = monthLabels.map(m => {
      const [y, mo] = m.split('-');
      const names = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];
      return names[parseInt(mo)-1] + ' ' + y.slice(2);
    });

    if (bitacoraChartTendencia) bitacoraChartTendencia.destroy();
    const ctx3 = document.getElementById('bitacoraChartTendencia');
    if (ctx3) {
      bitacoraChartTendencia = new Chart(ctx3, {
        type: 'line',
        data: {
          labels: monthDisplayLabels,
          datasets: [{
            data: monthValues,
            borderColor: '#00D68F',
            backgroundColor: 'rgba(0,214,143,0.1)',
            fill: true,
            tension: 0.3,
            pointRadius: 4,
            pointBackgroundColor: '#00D68F'
          }]
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: '#8888AA', font: { size: 10 } }, grid: { display: false } },
            y: { ticks: { color: '#8888AA', font: { size: 10 } }, grid: { color: 'rgba(42,42,74,0.4)' }, title: { display: true, text: 'kg', color: '#8888AA' }, beginAtZero: true }
          }
        }
      });
    }
  }

  function renderBitacora() {
    populateBitacoraMeses();
    renderBitacoraStats();
    renderBitacoraTable();
    if (document.getElementById('bitacoraChartsBody').classList.contains('visible')) {
      renderBitacoraCharts();
    }
  }
