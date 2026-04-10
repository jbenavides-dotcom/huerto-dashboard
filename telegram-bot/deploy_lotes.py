"""Deploy lotes productivos: prompt + execute action + animal read + switch + fast parse."""
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
print(f'Prompt: {len(SYSTEM_PROMPT)} chars')

# Leer workflow
req = urllib.request.Request(f'https://jhona.app.n8n.cloud/api/v1/workflows/{wf_id}', headers={'X-N8N-API-KEY': key})
with urllib.request.urlopen(req, timeout=15) as r:
    wf = json.loads(r.read())

# 1. Actualizar prompt
for node in wf['nodes']:
    if node['name'] == 'Prep Gemini Input':
        code = node['parameters']['jsCode']
        start_idx = code.find('const SYSTEM_PROMPT = ')
        end_idx = code.find(';\n', start_idx)
        if start_idx != -1 and end_idx != -1:
            old = code[start_idx:end_idx+1]
            new = 'const SYSTEM_PROMPT = ' + json.dumps(SYSTEM_PROMPT) + ';'
            code = code.replace(old, new)
            node['parameters']['jsCode'] = code
            print('Prep prompt actualizado')

        # Agregar fast-path para lotes
        old_fastparse = "return null;  // necesita Gemini"
        new_fastparse = """// --- LOTES ---
  if (/^(lotes|listar lotes|produccion|ver lotes)$/.test(t)) {
    return { action: 'list_lotes', reply: null };
  }
  const mLotes = t.match(/^lotes\\s+(bsf|truchas|conejos|lombrices)$/);
  if (mLotes) {
    return { action: 'query_lotes', modulo_id: mLotes[1], reply: null };
  }

  return null;  // necesita Gemini"""
        if old_fastparse in code:
            code = code.replace(old_fastparse, new_fastparse)
            node['parameters']['jsCode'] = code
            print('Fast-path lotes agregado')

# 2. Agregar lote operations al Execute Action
for node in wf['nodes']:
    if node['name'] == 'Execute Action':
        code = node['parameters']['jsCode']

        # Insertar bloque de lotes antes del "// Clear pending state"
        lotes_block = """
  } else if (pending.type === 'crear_lote') {
    const l = pending.lote || {};
    // Crear ubicacion si no existe
    let ubicacionId = null;
    if (l.ubicacion_nombre) {
      const existing = await this.helpers.httpRequest({
        method: 'GET', url: base + 'ubicaciones?nombre=eq.' + encodeURIComponent(l.ubicacion_nombre) + '&modulo_id=eq.' + encodeURIComponent(l.modulo_id) + '&select=id',
        headers, json: true,
      });
      if (existing && existing.length > 0) {
        ubicacionId = existing[0].id;
      } else {
        const newUb = await this.helpers.httpRequest({
          method: 'POST', url: base + 'ubicaciones',
          headers: Object.assign({}, headers, { Prefer: 'return=representation' }),
          body: { modulo_id: l.modulo_id, nombre: l.ubicacion_nombre, tipo: l.ubicacion_tipo || 'general' },
          json: true,
        });
        ubicacionId = newUb[0].id;
      }
    }
    // Generar codigo del lote
    var prefijos = { bsf: 'BSF', truchas: 'TRU', conejos: 'CON', lombrices: 'LOM' };
    var prefix = prefijos[l.modulo_id] || 'LOT';
    var lastLote = await this.helpers.httpRequest({
      method: 'GET', url: base + 'lotes?select=codigo&codigo=like.' + prefix + '-%25&order=codigo.desc&limit=1',
      headers, json: true,
    });
    var nextNum = 1;
    if (lastLote && lastLote.length > 0) {
      var match = lastLote[0].codigo.match(/-(\d+)$/);
      if (match) nextNum = parseInt(match[1], 10) + 1;
    }
    var codigo = prefix + '-' + String(nextNum).padStart(3, '0');
    await this.helpers.httpRequest({
      method: 'POST', url: base + 'lotes',
      headers: Object.assign({}, headers, { Prefer: 'return=minimal' }),
      body: {
        codigo: codigo,
        modulo_id: l.modulo_id,
        ubicacion_id: ubicacionId,
        etapa: l.etapa || 'larva',
        estado: 'Activo',
        fecha_inicio: item._today,
        cantidad_inicial: l.cantidad_inicial || null,
        unidad_cantidad: l.unidad_cantidad || 'unidades',
        cantidad_actual: l.cantidad_inicial || null,
        origen: l.origen || 'Produccion propia',
        created_by: 'telegram',
      }, json: true,
    });
    reply = 'Lote ' + codigo + ' creado.';

  } else if (pending.type === 'medir_lote') {
    var m = pending.medicion || {};
    var loteRow = await this.helpers.httpRequest({
      method: 'GET', url: base + 'lotes?codigo=eq.' + encodeURIComponent(m.lote_codigo) + '&select=id',
      headers, json: true,
    });
    if (!loteRow || !loteRow.length) {
      reply = 'Lote ' + m.lote_codigo + ' no encontrado.';
    } else {
      await this.helpers.httpRequest({
        method: 'POST', url: base + 'lote_mediciones',
        headers: Object.assign({}, headers, { Prefer: 'return=minimal' }),
        body: {
          lote_id: loteRow[0].id,
          fecha: item._today,
          tipo: m.tipo || 'peso',
          valor: m.valor || 0,
          unidad: m.unidad || '',
          nota: m.nota || null,
          created_by: 'telegram',
        }, json: true,
      });
      if (m.tipo === 'peso') {
        await this.helpers.httpRequest({
          method: 'PATCH', url: base + 'lotes?codigo=eq.' + encodeURIComponent(m.lote_codigo),
          headers: Object.assign({}, headers, { Prefer: 'return=minimal' }),
          body: { cantidad_actual: m.valor }, json: true,
        });
      }
      reply = 'Medicion registrada: ' + m.lote_codigo + ' ' + m.tipo + ' = ' + m.valor + ' ' + (m.unidad || '');
    }

  } else if (pending.type === 'alimentar_lote') {
    var a = pending.alimentacion || {};
    var loteRow = await this.helpers.httpRequest({
      method: 'GET', url: base + 'lotes?codigo=eq.' + encodeURIComponent(a.lote_codigo) + '&select=id',
      headers, json: true,
    });
    if (!loteRow || !loteRow.length) {
      reply = 'Lote ' + a.lote_codigo + ' no encontrado.';
    } else {
      await this.helpers.httpRequest({
        method: 'POST', url: base + 'lote_alimentacion',
        headers: Object.assign({}, headers, { Prefer: 'return=minimal' }),
        body: {
          lote_id: loteRow[0].id,
          fecha: item._today,
          alimento: a.alimento || 'Alimento',
          cantidad: a.cantidad || 0,
          unidad: a.unidad || 'kg',
          origen: a.origen || null,
          costo: a.costo || 0,
          created_by: 'telegram',
        }, json: true,
      });
      reply = 'Alimentacion registrada: ' + a.lote_codigo + ' ' + (a.cantidad || 0) + ' ' + (a.unidad || 'kg') + ' de ' + (a.alimento || 'alimento');
    }

  } else if (pending.type === 'cosechar_lote') {
    var c = pending.cosecha || {};
    var loteRow = await this.helpers.httpRequest({
      method: 'GET', url: base + 'lotes?codigo=eq.' + encodeURIComponent(c.lote_codigo) + '&select=id,modulo_id',
      headers, json: true,
    });
    if (!loteRow || !loteRow.length) {
      reply = 'Lote ' + c.lote_codigo + ' no encontrado.';
    } else {
      await this.helpers.httpRequest({
        method: 'POST', url: base + 'cosechas',
        headers: Object.assign({}, headers, { Prefer: 'return=minimal' }),
        body: {
          lote_id: loteRow[0].id,
          fecha: item._today,
          producto: c.producto || 'Producto',
          cantidad: c.cantidad || 0,
          unidad: c.unidad || 'kg',
          destino: c.destino || null,
          created_by: 'telegram',
        }, json: true,
      });
      // Registrar flujo de materia si tiene destino
      if (c.destino) {
        var destinoMap = { Gallinas: 'aves', Truchas: 'truchas', Huerta: 'huerta', Hotel: null };
        var destMod = destinoMap[c.destino] || null;
        if (destMod) {
          await this.helpers.httpRequest({
            method: 'POST', url: base + 'flujos_materia',
            headers: Object.assign({}, headers, { Prefer: 'return=minimal' }),
            body: {
              fecha: item._today,
              origen_modulo: loteRow[0].modulo_id,
              destino_modulo: destMod,
              material: c.producto || 'Producto',
              cantidad: c.cantidad || 0,
              unidad: c.unidad || 'kg',
              lote_origen_id: loteRow[0].id,
              created_by: 'telegram',
            }, json: true,
          });
        }
      }
      reply = 'Cosecha registrada: ' + (c.cantidad || 0) + ' ' + (c.unidad || '') + ' de ' + (c.producto || 'producto') + (c.destino ? ' -> ' + c.destino : '');
    }

  } else if (pending.type === 'cambiar_etapa_lote') {
    var ch = pending.cambio || {};
    await this.helpers.httpRequest({
      method: 'PATCH', url: base + 'lotes?codigo=eq.' + encodeURIComponent(ch.lote_codigo),
      headers: Object.assign({}, headers, { Prefer: 'return=minimal' }),
      body: { etapa: ch.nueva_etapa }, json: true,
    });
    reply = 'Lote ' + ch.lote_codigo + ' -> etapa ' + ch.nueva_etapa;
  }"""

        old_marker = "\n\n  // Clear pending state"
        if old_marker in code:
            code = code.replace(old_marker, lotes_block + "\n\n  // Clear pending state")
            node['parameters']['jsCode'] = code
            print('Execute Action: lotes block agregado')
        else:
            # Alt marker
            old2 = "\n  }\n\n  // Clear pending state"
            if old2 in code:
                code = code.replace(old2, lotes_block + "\n\n  // Clear pending state")
                node['parameters']['jsCode'] = code
                print('Execute Action: lotes block agregado (alt)')
            else:
                print('WARNING: no encontre marker')

# 3. Agregar lote writes al normalizer
for node in wf['nodes']:
    if node['name'] == 'Parse Gemini JSON':
        code = node['parameters']['jsCode']
        if "'add_costo'" in code and "'crear_lote'" not in code:
            code = code.replace("'add_costo'", "'add_costo','crear_lote','medir_lote','alimentar_lote','cosechar_lote','cambiar_etapa_lote'")
            node['parameters']['jsCode'] = code
            print('Normalizer: lote writes agregados')

# 4. Agregar query_lotes y list_lotes al Animal Read node
for node in wf['nodes']:
    if node['name'] == 'Animal Read':
        code = node['parameters']['jsCode']
        # Agregar handlers para lotes
        old_end = "} catch (e) {"
        new_lotes_handlers = """  } else if (action === 'query_lotes') {
    var modId = $json.modulo_id || '';
    var url = 'lotes?select=codigo,modulo_id,etapa,estado,cantidad_actual,unidad_cantidad,fecha_inicio&estado=eq.Activo&order=codigo';
    if (modId) url += '&modulo_id=eq.' + encodeURIComponent(modId);
    var lotes = await this.helpers.httpRequest({ method: 'GET', url: base + url, headers, json: true });
    if (!lotes || lotes.length === 0) {
      reply = 'No hay lotes activos' + (modId ? ' de ' + modId : '') + '.';
    } else {
      var lines = lotes.map(function(l) {
        return '• ' + l.codigo + ' (' + l.etapa + ') · ' + (l.cantidad_actual || '?') + ' ' + (l.unidad_cantidad || '') + ' · desde ' + l.fecha_inicio;
      });
      reply = '📦 Lotes activos' + (modId ? ' (' + modId + ')' : '') + ':' + NL + NL + lines.join(NL);
    }
  } else if (action === 'list_lotes') {
    var lotes = await this.helpers.httpRequest({ method: 'GET', url: base + 'lotes?select=codigo,modulo_id,etapa,estado,cantidad_actual,unidad_cantidad&estado=eq.Activo&order=modulo_id,codigo', headers, json: true });
    if (!lotes || lotes.length === 0) {
      reply = 'No hay lotes activos.';
    } else {
      var byMod = {};
      lotes.forEach(function(l) {
        var m = l.modulo_id || '?';
        if (!byMod[m]) byMod[m] = [];
        byMod[m].push(l.codigo + ' (' + l.etapa + ') · ' + (l.cantidad_actual || '?') + ' ' + (l.unidad_cantidad || ''));
      });
      var lines = ['📦 Lotes activos:', ''];
      Object.keys(byMod).sort().forEach(function(m) {
        lines.push(m.toUpperCase() + ':');
        byMod[m].forEach(function(s) { lines.push('  • ' + s); });
      });
      reply = lines.join(NL);
    }
  }
} catch (e) {"""
        if old_end in code:
            code = code.replace(old_end, new_lotes_handlers)
            node['parameters']['jsCode'] = code
            print('Animal Read: lotes queries agregados')

# 5. Agregar query_lotes y list_lotes al Switch Action
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
        rules = node['parameters'].get('rules', {}).get('values', [])
        existing = [r.get('outputKey') for r in rules]
        if 'query_lotes' not in existing:
            rules.append(build_rule('query_lotes', 'query_lotes'))
            rules.append(build_rule('list_lotes', 'list_lotes'))
            node['parameters']['rules']['values'] = rules
            print(f'Switch Action: {len(rules)} rules')

# 6. Agregar connections para query_lotes y list_lotes
conns = wf['connections'].get('Switch Action', {}).get('main', [])
# Agregar las 2 nuevas antes del fallback (último elemento)
if len(conns) > 0:
    fallback = conns[-1]  # el último es el fallback
    # Insertar antes del fallback
    conns.insert(-1, [{'node': 'Animal Read', 'type': 'main', 'index': 0}])  # query_lotes
    conns.insert(-1, [{'node': 'Animal Read', 'type': 'main', 'index': 0}])  # list_lotes
    wf['connections']['Switch Action']['main'] = conns
    print(f'Connections: {len(conns)} outputs en Switch')

# PUT
payload = {'name': wf['name'], 'nodes': wf['nodes'], 'connections': wf['connections'], 'settings': wf.get('settings', {'executionOrder': 'v1'})}
data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(f'https://jhona.app.n8n.cloud/api/v1/workflows/{wf_id}', data=data, headers={'X-N8N-API-KEY': key, 'Content-Type': 'application/json'}, method='PUT')
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read())
        print(f'\nWorkflow actualizado. active: {resp.get("active")}')
        print(f'Nodos: {len(resp.get("nodes", []))}')
except urllib.error.HTTPError as e:
    print('HTTP', e.code)
    print(e.read().decode()[:800])
