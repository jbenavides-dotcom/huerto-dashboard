'use strict';

/* ──────────────────────────────────────────
     SUPABASE BACKEND (con fallback a localStorage)

     Si las tablas no existen (404) o hay error de red,
     el dashboard sigue funcionando con localStorage como antes.
     Cuando se crean las tablas, el dashboard empieza a leer/escribir
     de Supabase automáticamente.
  ────────────────────────────────────────── */
  var SUPABASE = {
    url: 'https://pzkxbymwvimwnfmqoihj.supabase.co',
    key: 'sb_publishable_VzKz-KApgtUosdpch3mdVQ_Ojt4pEp0',
    available: false,           // se setea en checkSupabaseAvailable()
    lastError: null,
  };
  var SUPABASE_HEADERS = {
    'apikey': SUPABASE.key,
    'Authorization': 'Bearer ' + SUPABASE.key,
    'Content-Type': 'application/json',
  };

  async function supabaseFetch(path, options = {}) {
    const res = await fetch(SUPABASE.url + '/rest/v1/' + path, {
      ...options,
      headers: { ...SUPABASE_HEADERS, ...(options.headers || {}) },
    });
    if (!res.ok) {
      const err = new Error('Supabase ' + res.status);
      err.status = res.status;
      throw err;
    }
    const text = await res.text();
    return text ? JSON.parse(text) : null;
  }

  /**
   * Check if huerta_camas table exists. If 200 → available.
   * If 404 → tables not created yet, stay on localStorage-only mode.
   */
  async function checkSupabaseAvailable() {
    try {
      await supabaseFetch('huerta_camas?select=cama_id&limit=1');
      SUPABASE.available = true;
      console.log('[Huerta] Supabase conectado ✓');
    } catch (e) {
      SUPABASE.available = false;
      SUPABASE.lastError = e.message;
      console.warn('[Huerta] Supabase no disponible — usando localStorage:', e.message);
    }
  }

  /**
   * Pulls ALL camas from Supabase and hydrates BED_PLANTS + SENSOR_ASSIGNMENTS.
   * Silent no-op if Supabase not available.
   */
  async function syncCamasFromSupabase() {
    if (!SUPABASE.available) return;
    try {
      const rows = await supabaseFetch('huerta_camas?select=*&order=orden');
      if (!Array.isArray(rows) || rows.length === 0) return;

      const bedPlants = {};
      const sensorAssign = {};
      rows.forEach(r => {
        bedPlants[r.cama_id] = Array.isArray(r.plantas) ? r.plantas : [];
        sensorAssign[r.cama_id] = r.sensor_asignado || null;
      });

      // Update in-memory state and localStorage cache
      BED_PLANTS = bedPlants;
      saveBedPlants(BED_PLANTS);
      saveSensorAssignments(sensorAssign);

      console.log('[Huerta] Camas sincronizadas desde Supabase:', rows.length);
    } catch (e) {
      console.warn('[Huerta] Error sincronizando camas:', e.message);
    }
  }

  /**
   * Persist a single cama's plant list and/or sensor assignment to Supabase.
   * Called after every edit. Best-effort — no throw.
   */
  async function pushCamaToSupabase(camaId, updates) {
    if (!SUPABASE.available) return;
    try {
      await supabaseFetch('huerta_camas?cama_id=eq.' + encodeURIComponent(camaId), {
        method: 'PATCH',
        headers: { 'Prefer': 'return=minimal' },
        body: JSON.stringify(updates),
      });
    } catch (e) {
      console.warn('[Huerta] Error guardando cama ' + camaId + ':', e.message);
    }
  }

  /**
   * Push a single bitacora entry to Supabase. Best-effort.
   */
  async function pushBitacoraToSupabase(entry) {
    if (!SUPABASE.available) return;
    try {
      await supabaseFetch('huerta_bitacora', {
        method: 'POST',
        headers: { 'Prefer': 'return=minimal' },
        body: JSON.stringify({
          local_id:   entry.id,
          fecha:      entry.fecha,
          hora:       entry.hora || null,
          cama_id:    entry.cama || null,
          tipo:       entry.tipo,
          planta_id:  entry.plantaId || null,
          cantidad:   entry.cantidad || null,
          unidad:     entry.unidad || null,
          nota:       entry.nota || null,
          ts:         entry.ts || null,
          created_by: 'dashboard',
        }),
      });
    } catch (e) {
      console.warn('[Huerta] Error guardando bitácora:', e.message);
    }
  }

  async function deleteBitacoraFromSupabase(localId) {
    if (!SUPABASE.available) return;
    try {
      await supabaseFetch('huerta_bitacora?local_id=eq.' + encodeURIComponent(localId), {
        method: 'DELETE',
        headers: { 'Prefer': 'return=minimal' },
      });
    } catch (e) {
      console.warn('[Huerta] Error eliminando bitácora:', e.message);
    }
  }

  async function syncBitacoraFromSupabase() {
    if (!SUPABASE.available) return;
    try {
      const rows = await supabaseFetch('huerta_bitacora?select=*&order=ts.desc&limit=500');
      if (!Array.isArray(rows)) return;
      bitacoraData = rows.map(r => ({
        id:       r.local_id || 'db_' + r.id,
        fecha:    r.fecha,
        hora:     r.hora || '',
        cama:     r.cama_id || '',
        tipo:     r.tipo,
        plantaId: r.planta_id || '',
        cantidad: r.cantidad || 0,
        unidad:   r.unidad || 'kg',
        nota:     r.nota || '',
        ts:       r.ts ? Number(r.ts) : 0,
      }));
      saveBitacora();
      console.log('[Huerta] Bitácora sincronizada desde Supabase:', rows.length);
    } catch (e) {
      console.warn('[Huerta] Error sincronizando bitácora:', e.message);
    }
  }
