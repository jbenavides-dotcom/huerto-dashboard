"""Extender el bot con animales: prompt + fast parse + execute action + animal read node."""
import urllib.request
import json
import os
import subprocess
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

key = json.load(open(os.path.expanduser('~/Documents/cerebro-claude/key-apis/apis.json')))['n8n']['api_key']
wf_id = 'IeHSEjjZ1GE6JMU1'

base = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base, 'system-prompt.md'), 'r', encoding='utf-8') as f:
    raw = f.read()
first = raw.find('```')
start = raw.find('\n', first) + 1
end = raw.find('```', start)
SYSTEM_PROMPT = raw[start:end].strip()
print(f'Nuevo prompt: {len(SYSTEM_PROMPT)} chars')


# =============================
# 1. Fast Parse extendido (código del nodo Prep Gemini Input)
# =============================
NEW_PREP = r'''
const msg = $('Telegram Trigger').first().json.message;
const rawText = (msg.text || '').trim();
const userText = rawText.toLowerCase();
const chatId = msg.chat.id;
const userName = msg.from.first_name || 'usuario';
const today = new Date().toISOString().slice(0, 10);

const items = $input.all();
let pending = null;
let memory = null;
if (items.length > 0 && items[0].json && items[0].json.chat_id !== undefined) {
  const st = items[0].json;
  const now = new Date();
  if (st.expires_at && new Date(st.expires_at) > now) {
    if (st.pending_type === 'confirmation') pending = st.pending_action;
    else if (st.pending_type === 'clarification') memory = st.pending_action;
  }
}

function fastParse(text) {
  const t = text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, ' ').trim();

  // Confirmaciones
  if (pending) {
    if (/^(si|sii|ok|dale|confirmo|listo|yes|acepto|va|okey|okay)$/.test(t)) {
      return { action: 'confirmed', reply: null };
    }
    if (/^(no|cancela|cancelar|ya no|espera|atras|stop)$/.test(t)) {
      return { action: 'cancelled', reply: 'Cancelado. ¿Qué querés hacer?' };
    }
  }

  // --- HUERTA ---
  if (/^(listar camas?|lista(r)?|ver todas|mostrar camas?|resumen|estado huerta|ver camas)$/.test(t)) {
    return { action: 'list_camas', reply: null };
  }
  const mQueryCama = t.match(/^(?:cama\s*|c|la\s+)(\d{1,2}|invernadero|inver|greenhouse)$/);
  if (mQueryCama) {
    const n = mQueryCama[1];
    if (n === 'invernadero' || n === 'inver' || n === 'greenhouse') return { action: 'query_cama', cama_id: 'invernadero', reply: null };
    const num = parseInt(n, 10);
    if (num >= 1 && num <= 12) return { action: 'query_cama', cama_id: 'cama' + num, reply: null };
  }
  if (/^(invernadero|inver|greenhouse)$/.test(t)) return { action: 'query_cama', cama_id: 'invernadero', reply: null };

  // --- ANIMALES ---
  if (/^(animales|listar animales|inventario animales|ver animales|resumen animales)$/.test(t)) {
    return { action: 'list_animales', reply: null };
  }

  // "cuantos X" / "cuantas X"
  const mCount = t.match(/^cuant[oa]s?\s+(pollit[oa]s?|gallinas?|gallos?|pollos?|conejos?|cuyes?|patos?|gansos?|pavos?|codornices?)(?:\s+(muert[oa]s?|fallecid[oa]s?|vendid[oa]s?|activ[oa]s?))?$/);
  if (mCount) {
    const raw = mCount[1];
    const estadoRaw = mCount[2];
    let tipo = 'Ave', sexo = null, nombre_base = null;
    if (/^pollit/.test(raw)) { nombre_base = 'Pollito'; sexo = 'Indeterminado'; }
    else if (/^gallina/.test(raw)) { nombre_base = 'Gallina'; sexo = 'Hembra'; }
    else if (/^gallo/.test(raw)) { nombre_base = 'Gallo'; sexo = 'Macho'; }
    else if (/^pollo/.test(raw)) { nombre_base = 'Pollito'; sexo = 'Indeterminado'; }
    else if (/^conejo/.test(raw)) { tipo = 'Conejo'; nombre_base = 'Conejo'; }
    else if (/^cuy/.test(raw)) { tipo = 'Cuy'; nombre_base = 'Cuy'; }
    else if (/^pato/.test(raw)) { nombre_base = 'Pato'; }
    else if (/^ganso/.test(raw)) { nombre_base = 'Ganso'; }
    else if (/^pavo/.test(raw)) { nombre_base = 'Pavo'; }
    else if (/^codorniz|^codornice/.test(raw)) { nombre_base = 'Codorniz'; }

    let estado = 'Activo';
    if (estadoRaw) {
      if (/muert|fallecid/.test(estadoRaw)) estado = 'Fallecido';
      else if (/vendid/.test(estadoRaw)) estado = 'Vendido';
    }
    const filtro = { tipo: tipo, estado: estado };
    if (sexo) filtro.sexo = sexo;
    if (nombre_base) filtro.nombre_base = nombre_base;
    return { action: 'query_animales', filtro: filtro, reply: null };
  }

  return null;
}

const fast = fastParse(userText);

if (fast) {
  return [{
    json: {
      skip_gemini: true,
      action: fast.action,
      cama_id: fast.cama_id || null,
      filtro: fast.filtro || null,
      reply: fast.reply,
      _chat_id: chatId,
      _user_text: rawText,
      _today: today,
      _pending: pending,
      _memory: memory,
      gemini_body: null,
    }
  }];
}

// SLOW PATH
const NL = String.fromCharCode(10);
const userMessageForGemini =
  'HOY: ' + today + NL +
  'USUARIO: ' + userName + NL +
  'PENDING: ' + (pending ? JSON.stringify(pending) : 'null') + NL +
  'MEMORY: ' + (memory ? JSON.stringify(memory) : 'null') + NL +
  'MENSAJE: ' + userText;

const SYSTEM_PROMPT = __SYSTEM_PROMPT__;

const gemini_body = {
  systemInstruction: { parts: [{ text: SYSTEM_PROMPT }] },
  contents: [{ role: 'user', parts: [{ text: userMessageForGemini }] }],
  generationConfig: {
    temperature: 0,
    maxOutputTokens: 800,
    responseMimeType: 'application/json',
    thinkingConfig: { thinkingBudget: 0 }
  }
};

return [{
  json: {
    skip_gemini: false,
    chat_id: chatId,
    user_text: rawText,
    today: today,
    pending: pending,
    memory: memory,
    gemini_user_message: userMessageForGemini,
    gemini_body: gemini_body
  }
}];
'''

new_prep_code = NEW_PREP.replace('__SYSTEM_PROMPT__', json.dumps(SYSTEM_PROMPT))

# Validar
with open(os.path.expanduser('~/AppData/Local/Temp/prep_an.js'), 'w', encoding='utf-8') as f:
    f.write(new_prep_code)
r = subprocess.run(
    ['node', '-e', "new Function(require('fs').readFileSync(process.env.F,'utf8'));console.log('OK')"],
    capture_output=True, text=True,
    env={**os.environ, 'F': os.path.expanduser('~/AppData/Local/Temp/prep_an.js')}
)
print('Prep syntax:', r.stdout.strip() or r.stderr.strip()[:300])
if 'OK' not in r.stdout:
    sys.exit(1)


# =============================
# 2. Execute Action extendido (agrega animal writes)
# =============================
NEW_EXEC = r'''
const item = $json;
const pending = item._pending;
if (!pending || !pending.type) {
  return [{ json: { _chat_id: item._chat_id, reply: 'No había nada pendiente para confirmar.' } }];
}

const base = 'https://pzkxbymwvimwnfmqoihj.supabase.co/rest/v1/';
const headers = {
  apikey: 'sb_publishable_VzKz-KApgtUosdpch3mdVQ_Ojt4pEp0',
  Authorization: 'Bearer sb_publishable_VzKz-KApgtUosdpch3mdVQ_Ojt4pEp0',
  'Content-Type': 'application/json',
  Prefer: 'return=representation',
};

let reply = 'Listo.';

async function getNextAniId() {
  const rows = await this.helpers.httpRequest({
    method: 'GET', url: base + 'animales?select=id&order=id.desc&limit=1',
    headers, json: true,
  });
  if (!rows || !rows.length) return 'ANI-001';
  const last = rows[0].id || 'ANI-000';
  const n = parseInt(last.split('-')[1] || '0', 10) + 1;
  return 'ANI-' + String(n).padStart(3, '0');
}

async function getNextNumberForName(nombreBase) {
  // Encuentra el siguiente número disponible para ese nombre_base (ej: Pollito-51)
  const rows = await this.helpers.httpRequest({
    method: 'GET',
    url: base + 'animales?select=nombre&nombre=like.' + encodeURIComponent(nombreBase + '-%') + '&order=nombre.desc&limit=1',
    headers, json: true,
  });
  if (!rows || !rows.length) return 1;
  const match = (rows[0].nombre || '').match(/-(\d+)$/);
  return match ? (parseInt(match[1], 10) + 1) : 1;
}

try {
  // -------- HUERTA --------
  if (pending.type === 'update_plantas') {
    await this.helpers.httpRequest({
      method: 'PATCH', url: base + 'huerta_camas?cama_id=eq.' + encodeURIComponent(pending.cama_id),
      headers, body: { plantas: pending.plantas, updated_by: 'telegram' }, json: true,
    });
    reply = 'Cama actualizada.';
  } else if (pending.type === 'add_plantas' || pending.type === 'remove_plantas') {
    const cur = await this.helpers.httpRequest({
      method: 'GET', url: base + 'huerta_camas?cama_id=eq.' + encodeURIComponent(pending.cama_id) + '&select=plantas',
      headers, json: true,
    });
    const currentPlantas = (cur[0] && cur[0].plantas) || [];
    let newPlantas;
    if (pending.type === 'add_plantas') {
      newPlantas = [...new Set([...currentPlantas, ...(pending.plantas || [])])];
    } else {
      newPlantas = currentPlantas.filter(p => !(pending.plantas || []).includes(p));
    }
    await this.helpers.httpRequest({
      method: 'PATCH', url: base + 'huerta_camas?cama_id=eq.' + encodeURIComponent(pending.cama_id),
      headers, body: { plantas: newPlantas, updated_by: 'telegram' }, json: true,
    });
    reply = 'Cama actualizada.';
  } else if (pending.type === 'update_sensor') {
    if (pending.sensor_asignado) {
      await this.helpers.httpRequest({
        method: 'PATCH',
        url: base + 'huerta_camas?sensor_asignado=eq.' + encodeURIComponent(pending.sensor_asignado) + '&cama_id=neq.' + encodeURIComponent(pending.cama_id),
        headers, body: { sensor_asignado: null, updated_by: 'telegram' }, json: true,
      });
    }
    await this.helpers.httpRequest({
      method: 'PATCH', url: base + 'huerta_camas?cama_id=eq.' + encodeURIComponent(pending.cama_id),
      headers, body: { sensor_asignado: pending.sensor_asignado, updated_by: 'telegram' }, json: true,
    });
    reply = 'Sensor actualizado.';
  } else if (pending.type === 'add_bitacora') {
    const b = pending.bitacora || {};
    await this.helpers.httpRequest({
      method: 'POST', url: base + 'huerta_bitacora',
      headers, json: true,
      body: {
        local_id: 'tg_' + item._chat_id + '_' + Date.now(),
        fecha: b.fecha || item._today,
        cama_id: b.cama_id || null,
        tipo: b.tipo,
        planta_id: b.planta_id || null,
        cantidad: (b.cantidad === undefined ? null : b.cantidad),
        unidad: b.unidad || null,
        nota: b.nota || null,
        created_by: 'telegram',
      },
    });
    reply = 'Registrado en bitácora.';

  // -------- ANIMALES --------
  } else if (pending.type === 'add_animales') {
    const cantidad = pending.cantidad || 1;
    const tipo = pending.tipo || 'Ave';
    const sexo = pending.sexo || 'Indeterminado';
    const nombreBase = pending.nombre_base || 'Animal';
    const procedencia = pending.procedencia || 'Compra';

    let nextNum = await getNextNumberForName.call(this, nombreBase);
    const lastRow = await this.helpers.httpRequest({
      method: 'GET', url: base + 'animales?select=id&order=id.desc&limit=1', headers, json: true,
    });
    let nextIdNum = lastRow && lastRow.length ? parseInt((lastRow[0].id || 'ANI-000').split('-')[1], 10) + 1 : 1;

    const rowsToInsert = [];
    for (let i = 0; i < cantidad; i++) {
      rowsToInsert.push({
        id: 'ANI-' + String(nextIdNum + i).padStart(3, '0'),
        nombre: nombreBase + '-' + String(nextNum + i).padStart(2, '0'),
        tipo: tipo,
        raza: 'Criollo',
        sexo: sexo,
        estado: 'Activo',
        ubicacion: 'Finca',
        procedencia: procedencia,
        fecha_ingreso: item._today,
        observaciones: 'Registrado via telegram ' + item._today,
      });
    }
    await this.helpers.httpRequest({
      method: 'POST', url: base + 'animales',
      headers: Object.assign({}, headers, { Prefer: 'return=minimal' }),
      body: rowsToInsert, json: true,
    });
    reply = 'Registrados ' + cantidad + ' ' + nombreBase.toLowerCase() + (cantidad > 1 ? 's' : '') + ' nuevos.';

  } else if (pending.type === 'update_animal_estado') {
    const cantidad = pending.cantidad || 1;
    const tipo = pending.tipo;
    const sexo = pending.sexo;
    const nombreBase = pending.nombre_base;
    const nuevoEstado = pending.nuevo_estado || 'Fallecido';

    // Buscar animales activos del tipo (últimos N por id)
    let filterUrl = 'animales?select=id,nombre&estado=eq.Activo&order=id.desc&limit=' + cantidad;
    if (tipo) filterUrl += '&tipo=eq.' + encodeURIComponent(tipo);
    if (sexo) filterUrl += '&sexo=eq.' + encodeURIComponent(sexo);
    if (nombreBase) filterUrl += '&nombre=like.' + encodeURIComponent(nombreBase + '-%');

    const toUpdate = await this.helpers.httpRequest({
      method: 'GET', url: base + filterUrl, headers, json: true,
    });
    if (!toUpdate || toUpdate.length === 0) {
      reply = 'No encontré animales activos para actualizar.';
    } else {
      const ids = toUpdate.map(a => a.id);
      const idFilter = 'in.(' + ids.map(i => '"' + i + '"').join(',') + ')';
      const obsMotivo = pending.motivo ? ('. Motivo: ' + pending.motivo) : '';
      await this.helpers.httpRequest({
        method: 'PATCH',
        url: base + 'animales?id=' + idFilter,
        headers: Object.assign({}, headers, { Prefer: 'return=minimal' }),
        body: { estado: nuevoEstado, observaciones: nuevoEstado + ' ' + item._today + obsMotivo },
        json: true,
      });
      // Registrar en actividades
      const actRow = await this.helpers.httpRequest({
        method: 'GET', url: base + 'actividades?select=id&order=id.desc&limit=1', headers, json: true,
      });
      let actNum = (actRow && actRow.length) ? parseInt((actRow[0].id || 'ACT-000').split('-')[1], 10) + 1 : 1;
      await this.helpers.httpRequest({
        method: 'POST', url: base + 'actividades',
        headers: Object.assign({}, headers, { Prefer: 'return=minimal' }),
        body: {
          id: 'ACT-' + String(actNum).padStart(3, '0'),
          fecha: item._today,
          animal_id: ids[0],
          nombre_animal: 'Lote ' + (nombreBase || 'animales') + ' (' + cantidad + ')',
          tipo_actividad: nuevoEstado === 'Fallecido' ? 'Muerte' : nuevoEstado,
          descripcion: cantidad + ' animales cambiados a ' + nuevoEstado,
          costo: 0,
          estado: 'Completada',
          observaciones: 'Via telegram' + obsMotivo,
        }, json: true,
      });
      reply = nuevoEstado + ': ' + cantidad + ' ' + (nombreBase || 'animales').toLowerCase() + (cantidad > 1 ? 's' : '') + '.';
    }

  } else if (pending.type === 'add_huevos') {
    const h = pending.huevos || {};
    const hueRow = await this.helpers.httpRequest({
      method: 'GET', url: base + 'huevos?select=id&order=id.desc&limit=1', headers, json: true,
    });
    let hueNum = (hueRow && hueRow.length) ? parseInt((hueRow[0].id || 'HUE-000').split('-')[1], 10) + 1 : 1;
    await this.helpers.httpRequest({
      method: 'POST', url: base + 'huevos',
      headers: Object.assign({}, headers, { Prefer: 'return=minimal' }),
      body: {
        id: 'HUE-' + String(hueNum).padStart(3, '0'),
        fecha: h.fecha || item._today,
        cantidad: h.cantidad || 0,
        rotos: h.rotos || 0,
        ubicacion: h.ubicacion || 'Gallinero',
        observaciones: 'Via telegram',
      }, json: true,
    });
    reply = 'Huevos registrados: ' + (h.cantidad || 0) + ' (' + (h.rotos || 0) + ' rotos).';

  } else if (pending.type === 'add_actividad') {
    const a = pending.actividad || {};
    const actRow = await this.helpers.httpRequest({
      method: 'GET', url: base + 'actividades?select=id&order=id.desc&limit=1', headers, json: true,
    });
    let actNum = (actRow && actRow.length) ? parseInt((actRow[0].id || 'ACT-000').split('-')[1], 10) + 1 : 1;
    await this.helpers.httpRequest({
      method: 'POST', url: base + 'actividades',
      headers: Object.assign({}, headers, { Prefer: 'return=minimal' }),
      body: {
        id: 'ACT-' + String(actNum).padStart(3, '0'),
        fecha: item._today,
        nombre_animal: 'Lote ' + (a.cantidad_animales || 0) + ' ' + (a.nombre_base || a.tipo_animal || 'animales'),
        tipo_actividad: a.tipo_actividad || 'Otro',
        descripcion: a.descripcion || '',
        producto: a.producto || null,
        dosis: a.dosis || null,
        veterinario: a.veterinario || null,
        costo: a.costo || 0,
        proxima_fecha: a.proxima_fecha || null,
        estado: 'Completada',
        observaciones: 'Via telegram',
      }, json: true,
    });
    reply = 'Actividad registrada.';
  }

  // Clear pending state
  await this.helpers.httpRequest({
    method: 'DELETE', url: base + 'huerta_bot_state?chat_id=eq.' + encodeURIComponent(item._chat_id),
    headers: Object.assign({}, headers, { Prefer: 'return=minimal' }), json: true,
  });
} catch (e) {
  reply = 'Error ejecutando: ' + (e.message || 'desconocido');
}

return [{ json: { _chat_id: item._chat_id, reply: reply } }];
'''

# Validar con wrapper async
with open(os.path.expanduser('~/AppData/Local/Temp/exec_an.js'), 'w', encoding='utf-8') as f:
    f.write('async function test() {\n' + NEW_EXEC + '\n}')
r = subprocess.run(
    ['node', '-e', "new Function(require('fs').readFileSync(process.env.F,'utf8'));console.log('OK')"],
    capture_output=True, text=True,
    env={**os.environ, 'F': os.path.expanduser('~/AppData/Local/Temp/exec_an.js')}
)
print('Execute syntax:', r.stdout.strip() or r.stderr.strip()[:500])
if 'OK' not in r.stdout:
    sys.exit(1)


# =============================
# 3. Nuevo nodo: Animal Read (handles query_animales + list_animales)
# =============================
ANIMAL_READ = r'''
const action = $json.action;
const filtro = $json.filtro || {};
const base = 'https://pzkxbymwvimwnfmqoihj.supabase.co/rest/v1/';
const headers = {
  apikey: 'sb_publishable_VzKz-KApgtUosdpch3mdVQ_Ojt4pEp0',
  Authorization: 'Bearer sb_publishable_VzKz-KApgtUosdpch3mdVQ_Ojt4pEp0',
};

const NL = String.fromCharCode(10);
const chat_id = $json._chat_id || $('Telegram Trigger').first().json.message.chat.id;
let reply = '';

try {
  if (action === 'query_animales') {
    let url = 'animales?select=id,tipo,sexo,estado,nombre';
    const parts = [];
    if (filtro.tipo) parts.push('tipo=eq.' + encodeURIComponent(filtro.tipo));
    if (filtro.sexo) parts.push('sexo=eq.' + encodeURIComponent(filtro.sexo));
    if (filtro.estado) parts.push('estado=eq.' + encodeURIComponent(filtro.estado));
    else parts.push('estado=eq.Activo');
    if (filtro.nombre_base) parts.push('nombre=like.' + encodeURIComponent(filtro.nombre_base + '-%'));
    if (parts.length) url += '&' + parts.join('&');
    const rows = await this.helpers.httpRequest({ method: 'GET', url: base + url, headers, json: true });
    const n = rows ? rows.length : 0;
    const nombre = filtro.nombre_base || filtro.tipo || 'animales';
    const estadoTxt = filtro.estado || 'activos';
    reply = n + ' ' + nombre.toLowerCase() + (n === 1 ? '' : 's') + ' ' + estadoTxt.toLowerCase();
  } else if (action === 'list_animales') {
    const rows = await this.helpers.httpRequest({
      method: 'GET', url: base + 'animales?select=tipo,sexo,estado,nombre&order=id',
      headers, json: true,
    });
    // Agrupar: nombre_base (primera parte antes de -) por estado
    const groups = {};
    (rows || []).forEach(r => {
      const nombreBase = (r.nombre || '').split('-')[0] || r.tipo;
      const key = nombreBase;
      if (!groups[key]) groups[key] = { Activo: 0, Fallecido: 0, Vendido: 0, Perdido: 0, Robado: 0, Otro: 0 };
      const st = r.estado || 'Otro';
      if (groups[key][st] !== undefined) groups[key][st]++;
      else groups[key].Otro++;
    });

    const lines = ['🐾 Inventario animales:', ''];
    Object.keys(groups).sort().forEach(k => {
      const g = groups[k];
      const activos = g.Activo;
      const extras = [];
      if (g.Fallecido) extras.push(g.Fallecido + ' muertos');
      if (g.Vendido) extras.push(g.Vendido + ' vendidos');
      if (g.Perdido) extras.push(g.Perdido + ' perdidos');
      const extraStr = extras.length ? ' (' + extras.join(', ') + ')' : '';
      lines.push('• ' + k + ': ' + activos + ' activos' + extraStr);
    });
    reply = lines.join(NL);
  }
} catch (e) {
  reply = 'Error consultando animales: ' + (e.message || 'desconocido');
}

return [{ json: { chat_id: chat_id, reply: reply } }];
'''

# Validar con wrapper async
with open(os.path.expanduser('~/AppData/Local/Temp/an_read.js'), 'w', encoding='utf-8') as f:
    f.write('async function test() {\n' + ANIMAL_READ + '\n}')
r = subprocess.run(
    ['node', '-e', "new Function(require('fs').readFileSync(process.env.F,'utf8'));console.log('OK')"],
    capture_output=True, text=True,
    env={**os.environ, 'F': os.path.expanduser('~/AppData/Local/Temp/an_read.js')}
)
print('Animal Read syntax:', r.stdout.strip() or r.stderr.strip()[:500])
if 'OK' not in r.stdout:
    sys.exit(1)


# =============================
# 4. Leer workflow actual y actualizarlo
# =============================
req = urllib.request.Request(f'https://jhona.app.n8n.cloud/api/v1/workflows/{wf_id}', headers={'X-N8N-API-KEY': key})
with urllib.request.urlopen(req, timeout=15) as r:
    wf = json.loads(r.read())

# Update Prep
for node in wf['nodes']:
    if node['name'] == 'Prep Gemini Input':
        node['parameters']['jsCode'] = new_prep_code
        print('Prep actualizado')
    elif node['name'] == 'Execute Action':
        node['parameters']['jsCode'] = NEW_EXEC
        print('Execute Action actualizado')

# Agregar nodo Animal Read si no existe
if not any(n['name'] == 'Animal Read' for n in wf['nodes']):
    wf['nodes'].append({
        'parameters': {'jsCode': ANIMAL_READ},
        'name': 'Animal Read',
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [1640, 800],
    })
    print('Animal Read node agregado')
else:
    for node in wf['nodes']:
        if node['name'] == 'Animal Read':
            node['parameters']['jsCode'] = ANIMAL_READ
            print('Animal Read actualizado')

# Update Switch Action con 2 reglas nuevas
def build_rule(value, output_key):
    return {
        'conditions': {
            'options': {'caseSensitive': True, 'leftValue': '', 'typeValidation': 'loose'},
            'combinator': 'and',
            'conditions': [{
                'id': 'cond-' + output_key,
                'leftValue': '={{ $json.action }}',
                'rightValue': value,
                'operator': {'type': 'string', 'operation': 'equals', 'name': 'filter.operator.equals'}
            }]
        },
        'renameOutput': True,
        'outputKey': output_key
    }

for node in wf['nodes']:
    if node['name'] == 'Switch Action':
        node['typeVersion'] = 3.2
        node['parameters'] = {
            'rules': {
                'values': [
                    build_rule('confirm', 'confirm'),
                    build_rule('confirmed', 'confirmed'),
                    build_rule('cancelled', 'cancelled'),
                    build_rule('ask', 'ask'),
                    build_rule('query_cama', 'query_cama'),
                    build_rule('list_camas', 'list_camas'),
                    build_rule('query_animales', 'query_animales'),
                    build_rule('list_animales', 'list_animales'),
                ]
            },
            'options': {'fallbackOutput': 'extra', 'renameFallbackOutput': 'other'}
        }
        print('Switch Action actualizado (8 rules + fallback)')

# Update connections del Switch: agregar las 2 nuevas al final (antes del fallback)
# El orden debe matchear: 0=confirm, 1=confirmed, 2=cancelled, 3=ask, 4=query_cama, 5=list_camas, 6=query_animales, 7=list_animales, 8=fallback
wf['connections']['Switch Action'] = {
    'main': [
        [{'node': 'Save Confirm State', 'type': 'main', 'index': 0}],    # 0 confirm
        [{'node': 'Execute Action', 'type': 'main', 'index': 0}],         # 1 confirmed
        [{'node': 'Clear State', 'type': 'main', 'index': 0}],            # 2 cancelled
        [{'node': 'Save Ask State', 'type': 'main', 'index': 0}],         # 3 ask
        [{'node': 'Query Cama', 'type': 'main', 'index': 0}],             # 4 query_cama
        [{'node': 'List Camas', 'type': 'main', 'index': 0}],             # 5 list_camas
        [{'node': 'Animal Read', 'type': 'main', 'index': 0}],            # 6 query_animales
        [{'node': 'Animal Read', 'type': 'main', 'index': 0}],            # 7 list_animales
        [{'node': 'Format Reply', 'type': 'main', 'index': 0}],           # 8 fallback
    ]
}
# Animal Read → Format Reply
wf['connections']['Animal Read'] = {
    'main': [[{'node': 'Format Reply', 'type': 'main', 'index': 0}]]
}
print('Connections actualizadas')

# PUT
payload = {
    'name': wf['name'],
    'nodes': wf['nodes'],
    'connections': wf['connections'],
    'settings': wf.get('settings', {'executionOrder': 'v1'})
}
data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(
    f'https://jhona.app.n8n.cloud/api/v1/workflows/{wf_id}',
    data=data,
    headers={'X-N8N-API-KEY': key, 'Content-Type': 'application/json'},
    method='PUT'
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read())
        print(f'\nWorkflow actualizado. active: {resp.get("active")}')
        print(f'Nodos totales: {len(resp.get("nodes", []))}')
except urllib.error.HTTPError as e:
    print('HTTP', e.code)
    print(e.read().decode()[:800])
