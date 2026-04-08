"""Deploy del workflow del bot huerta a n8n.

- Lee credenciales de apis.json (nunca las hardcodea)
- Lee el system-prompt.md y lo inyecta en el nodo Gemini
- Construye el workflow completo en memoria
- POST a /api/v1/workflows
"""
import json
import os
import sys
import io
import urllib.request
import urllib.error

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.dirname(os.path.abspath(__file__))
APIS_PATH = os.path.expanduser('~/Documents/cerebro-claude/key-apis/apis.json')

with open(APIS_PATH, 'r', encoding='utf-8') as f:
    apis = json.load(f)

N8N_URL = apis['n8n']['url']
N8N_KEY = apis['n8n']['api_key']
SUPABASE_URL = 'https://pzkxbymwvimwnfmqoihj.supabase.co'
SUPABASE_KEY = 'sb_publishable_VzKz-KApgtUosdpch3mdVQ_Ojt4pEp0'

# IDs de credenciales creadas previamente
TELEGRAM_CRED_ID = 'vn8nSW2QajDXL4uB'  # Huerta Bot Telegram
GEMINI_CRED_ID = '8gb6CIrrFxb9PAw4'    # Gemini API Huerta (httpQueryAuth)

# Whitelist de chat_ids autorizados
AUTHORIZED_CHAT_IDS = [
    1511283217,   # Jhonatan
    # Agregar aquí el 2do chat_id cuando se defina
]

# Leer system prompt
with open(os.path.join(BASE, 'system-prompt.md'), 'r', encoding='utf-8') as f:
    raw = f.read()
first = raw.find('```')
start = raw.find('\n', first) + 1
end = raw.find('```', start)
SYSTEM_PROMPT = raw[start:end].strip()
print('System prompt loaded: ' + str(len(SYSTEM_PROMPT)) + ' chars')


def n_code(name, code, position):
    return {
        'parameters': {'jsCode': code},
        'name': name,
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': position,
    }


def n_http(name, method, url, body=None, position=None, credentials=None, headers=None):
    params = {
        'method': method,
        'url': url,
        'sendHeaders': True,
        'headerParameters': {'parameters': headers or [
            {'name': 'apikey', 'value': SUPABASE_KEY},
            {'name': 'Authorization', 'value': 'Bearer ' + SUPABASE_KEY},
            {'name': 'Content-Type', 'value': 'application/json'},
            {'name': 'Prefer', 'value': 'return=representation'},
        ]},
        'options': {},
    }
    if body is not None:
        params['sendBody'] = True
        params['specifyBody'] = 'json'
        params['jsonBody'] = body
    node = {
        'parameters': params,
        'name': name,
        'type': 'n8n-nodes-base.httpRequest',
        'typeVersion': 4.2,
        'position': position,
    }
    if credentials:
        node['credentials'] = credentials
    return node


# Chat IDs para la condición IF
whitelist_conditions = [
    {
        'id': f'cond-{i}',
        'leftValue': '={{ $json.message.chat.id }}',
        'rightValue': str(chat_id),
        'operator': {'type': 'number', 'operation': 'equals'},
    }
    for i, chat_id in enumerate(AUTHORIZED_CHAT_IDS)
]

NODES = [
    # 1. Telegram Trigger
    {
        'parameters': {'updates': ['message'], 'additionalFields': {}},
        'name': 'Telegram Trigger',
        'type': 'n8n-nodes-base.telegramTrigger',
        'typeVersion': 1.2,
        'position': [100, 300],
        'webhookId': 'huerta-bot-webhook',
        'credentials': {'telegramApi': {'id': TELEGRAM_CRED_ID, 'name': 'Huerta Bot Telegram'}},
    },

    # 2. IF whitelist
    {
        'parameters': {
            'conditions': {
                'options': {'caseSensitive': False, 'typeValidation': 'loose', 'version': 2},
                'combinator': 'or',
                'conditions': whitelist_conditions,
            },
            'options': {},
        },
        'name': 'IF Autorizado',
        'type': 'n8n-nodes-base.if',
        'typeVersion': 2,
        'position': [320, 300],
    },

    # 3. Get Bot State from Supabase
    n_http(
        'Get Bot State', 'GET',
        '=' + SUPABASE_URL + '/rest/v1/huerta_bot_state?chat_id=eq.{{ $json.message.chat.id }}&select=*',
        position=[540, 220],
        headers=[
            {'name': 'apikey', 'value': SUPABASE_KEY},
            {'name': 'Authorization', 'value': 'Bearer ' + SUPABASE_KEY},
        ],
    ),

    # 4. Prep Gemini Input
    n_code('Prep Gemini Input', '''
const msg = $('Telegram Trigger').first().json.message;
const userText = msg.text || '';
const chatId = msg.chat.id;
const userName = msg.from.first_name || 'usuario';
const today = new Date().toISOString().slice(0, 10);

const stateRows = $input.first().json;
let pending = null;
let memory = null;
if (Array.isArray(stateRows) && stateRows.length > 0) {
  const st = stateRows[0];
  const now = new Date();
  if (st.expires_at && new Date(st.expires_at) > now) {
    if (st.pending_type === 'confirmation') pending = st.pending_action;
    else if (st.pending_type === 'clarification') memory = st.pending_action;
  }
}

const userMessageForGemini = [
  'HOY: ' + today,
  'USUARIO: ' + userName,
  'PENDING: ' + (pending ? JSON.stringify(pending) : 'null'),
  'MEMORY: ' + (memory ? JSON.stringify(memory) : 'null'),
  'MENSAJE: ' + userText,
].join('\\n');

return [{ json: { chat_id: chatId, user_text: userText, user_name: userName, today, pending, memory, gemini_user_message: userMessageForGemini } }];
''', [760, 220]),

    # 5. Gemini API call
    {
        'parameters': {
            'method': 'POST',
            'url': '=https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent',
            'authentication': 'genericCredentialType',
            'genericAuthType': 'httpQueryAuth',
            'sendHeaders': True,
            'headerParameters': {
                'parameters': [{'name': 'Content-Type', 'value': 'application/json'}]
            },
            'sendBody': True,
            'specifyBody': 'json',
            'jsonBody': json.dumps({
                'systemInstruction': {'parts': [{'text': SYSTEM_PROMPT}]},
                'contents': [{'role': 'user', 'parts': [{'text': '={{ $json.gemini_user_message }}'}]}],
                'generationConfig': {
                    'temperature': 0,
                    'maxOutputTokens': 800,
                    'responseMimeType': 'application/json',
                    'thinkingConfig': {'thinkingBudget': 0},
                },
            }, ensure_ascii=False),
            'options': {},
        },
        'name': 'Gemini 2.5 Flash',
        'type': 'n8n-nodes-base.httpRequest',
        'typeVersion': 4.2,
        'position': [980, 220],
        'credentials': {'httpQueryAuth': {'id': GEMINI_CRED_ID, 'name': 'Gemini API Huerta'}},
    },

    # 6. Parse Gemini JSON
    n_code('Parse Gemini JSON', '''
const resp = $input.first().json;
const rawText = resp.candidates?.[0]?.content?.parts?.[0]?.text || '';
let parsed;
try {
  const cleaned = rawText.trim().replace(/^```json\\s*/, '').replace(/^```\\s*/, '').replace(/\\s*```$/, '');
  parsed = JSON.parse(cleaned);
} catch (e) {
  parsed = { action: 'error', reply: '❌ Error parseando respuesta del bot.' };
}
const ctx = $('Prep Gemini Input').first().json;
return [{ json: { ...parsed, _chat_id: ctx.chat_id, _user_text: ctx.user_text, _today: ctx.today, _pending: ctx.pending, _memory: ctx.memory } }];
''', [1200, 220]),

    # 7. Switch action
    {
        'parameters': {
            'dataType': 'string',
            'value1': '={{ $json.action }}',
            'rules': {
                'rules': [
                    {'operation': 'equal', 'value2': 'confirm', 'output': 0},
                    {'operation': 'equal', 'value2': 'confirmed', 'output': 1},
                    {'operation': 'equal', 'value2': 'cancelled', 'output': 2},
                    {'operation': 'equal', 'value2': 'ask', 'output': 3},
                    {'operation': 'equal', 'value2': 'query_cama', 'output': 4},
                    {'operation': 'equal', 'value2': 'list_camas', 'output': 5},
                ],
            },
            'fallbackOutput': 6,
        },
        'name': 'Switch Action',
        'type': 'n8n-nodes-base.switch',
        'typeVersion': 1,
        'position': [1420, 220],
    },

    # 8. Save Confirm State (after confirm action)
    n_http(
        'Save Confirm State', 'POST',
        SUPABASE_URL + '/rest/v1/huerta_bot_state',
        body='={\n  "chat_id": {{ $json._chat_id }},\n  "pending_action": {{ JSON.stringify($json.payload) }},\n  "pending_type": "confirmation",\n  "question": {{ JSON.stringify($json.reply) }},\n  "expires_at": "{{ new Date(Date.now() + 10*60*1000).toISOString() }}"\n}',
        position=[1640, -40],
        headers=[
            {'name': 'apikey', 'value': SUPABASE_KEY},
            {'name': 'Authorization', 'value': 'Bearer ' + SUPABASE_KEY},
            {'name': 'Content-Type', 'value': 'application/json'},
            {'name': 'Prefer', 'value': 'return=minimal,resolution=merge-duplicates'},
        ],
    ),

    # 9. Execute Pending Action (after confirmed)
    n_code('Execute Action', '''
const item = $json;
const pending = item._pending;
if (!pending || !pending.type) {
  return [{ json: { _chat_id: item._chat_id, reply: '❌ No había nada pendiente para confirmar.' } }];
}

const base = 'https://pzkxbymwvimwnfmqoihj.supabase.co/rest/v1/';
const headers = {
  apikey: 'sb_publishable_VzKz-KApgtUosdpch3mdVQ_Ojt4pEp0',
  Authorization: 'Bearer sb_publishable_VzKz-KApgtUosdpch3mdVQ_Ojt4pEp0',
  'Content-Type': 'application/json',
  Prefer: 'return=representation',
};

let reply = '✅ Listo.';

try {
  if (pending.type === 'update_plantas') {
    await this.helpers.httpRequest({
      method: 'PATCH', url: base + 'huerta_camas?cama_id=eq.' + encodeURIComponent(pending.cama_id),
      headers, body: { plantas: pending.plantas, updated_by: 'telegram' }, json: true,
    });
    reply = '✅ Cama actualizada.';
  } else if (pending.type === 'add_plantas' || pending.type === 'remove_plantas') {
    const cur = await this.helpers.httpRequest({
      method: 'GET', url: base + 'huerta_camas?cama_id=eq.' + encodeURIComponent(pending.cama_id) + '&select=plantas',
      headers, json: true,
    });
    const currentPlantas = (cur[0]?.plantas) || [];
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
    reply = '✅ Cama actualizada.';
  } else if (pending.type === 'update_sensor') {
    await this.helpers.httpRequest({
      method: 'PATCH', url: base + 'huerta_camas?cama_id=eq.' + encodeURIComponent(pending.cama_id),
      headers, body: { sensor_asignado: pending.sensor_asignado, updated_by: 'telegram' }, json: true,
    });
    reply = '✅ Sensor actualizado.';
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
    reply = '✅ Registrado en bitácora.';
  }

  // Clear pending state
  await this.helpers.httpRequest({
    method: 'DELETE', url: base + 'huerta_bot_state?chat_id=eq.' + encodeURIComponent(item._chat_id),
    headers: { ...headers, Prefer: 'return=minimal' }, json: true,
  });
} catch (e) {
  reply = '❌ Error ejecutando: ' + (e.message || 'desconocido');
}

return [{ json: { _chat_id: item._chat_id, reply } }];
''', [1640, 100]),

    # 10. Clear State (on cancel)
    n_http(
        'Clear State', 'DELETE',
        '=' + SUPABASE_URL + '/rest/v1/huerta_bot_state?chat_id=eq.{{ $json._chat_id }}',
        position=[1640, 240],
        headers=[
            {'name': 'apikey', 'value': SUPABASE_KEY},
            {'name': 'Authorization', 'value': 'Bearer ' + SUPABASE_KEY},
            {'name': 'Prefer', 'value': 'return=minimal'},
        ],
    ),

    # 11. Save Ask State (clarification)
    n_http(
        'Save Ask State', 'POST',
        SUPABASE_URL + '/rest/v1/huerta_bot_state',
        body='={\n  "chat_id": {{ $json._chat_id }},\n  "pending_action": {{ JSON.stringify($json.memory || {}) }},\n  "pending_type": "clarification",\n  "question": {{ JSON.stringify($json.reply) }},\n  "expires_at": "{{ new Date(Date.now() + 10*60*1000).toISOString() }}"\n}',
        position=[1640, 380],
        headers=[
            {'name': 'apikey', 'value': SUPABASE_KEY},
            {'name': 'Authorization', 'value': 'Bearer ' + SUPABASE_KEY},
            {'name': 'Content-Type', 'value': 'application/json'},
            {'name': 'Prefer', 'value': 'return=minimal,resolution=merge-duplicates'},
        ],
    ),

    # 12. Query Cama
    n_http(
        'Query Cama', 'GET',
        '=' + SUPABASE_URL + '/rest/v1/huerta_camas?cama_id=eq.{{ $json.cama_id }}&select=*',
        position=[1640, 520],
        headers=[
            {'name': 'apikey', 'value': SUPABASE_KEY},
            {'name': 'Authorization', 'value': 'Bearer ' + SUPABASE_KEY},
        ],
    ),

    # 13. List Camas
    n_http(
        'List Camas', 'GET',
        SUPABASE_URL + '/rest/v1/huerta_camas?select=cama_id,nombre,grupo,plantas,sensor_asignado&order=orden',
        position=[1640, 660],
        headers=[
            {'name': 'apikey', 'value': SUPABASE_KEY},
            {'name': 'Authorization', 'value': 'Bearer ' + SUPABASE_KEY},
        ],
    ),

    # 14. Format Reply
    n_code('Format Reply', '''
const item = $input.first().json;
let reply = item.reply || '';
let chat_id = item._chat_id || item.chat_id;

if (Array.isArray(item)) {
  if (item.length > 1) {
    const lines = item.map(c => {
      const plantas = (Array.isArray(c.plantas) && c.plantas.length) ? c.plantas.join(', ') : 'sin ocupación';
      const sensor = c.sensor_asignado ? c.sensor_asignado.replace('soil_', '').toUpperCase() : '—';
      return '• ' + c.nombre + ' (' + c.grupo + ') · ' + sensor + '\\n  ' + plantas;
    });
    reply = '🌿 Camas de la huerta:\\n\\n' + lines.join('\\n');
  } else if (item.length === 1) {
    const c = item[0];
    const plantas = (Array.isArray(c.plantas) && c.plantas.length) ? c.plantas.join(', ') : 'sin ocupación';
    const sensor = c.sensor_asignado ? c.sensor_asignado.replace('soil_', '').toUpperCase() : 'sin sensor';
    reply = '📍 ' + c.nombre + '\\nGrupo: ' + c.grupo + '\\nSensor: ' + sensor + '\\nPlantas: ' + plantas;
  } else {
    reply = '⚠️ No encontré esa cama.';
  }
  chat_id = $('Prep Gemini Input').first().json.chat_id;
}

if (!chat_id) chat_id = $('Telegram Trigger').first().json.message.chat.id;
if (!reply) reply = '✅ OK';
return [{ json: { chat_id, reply } }];
''', [1880, 300]),

    # 15. Telegram Reply
    {
        'parameters': {
            'chatId': '={{ $json.chat_id }}',
            'text': '={{ $json.reply }}',
            'additionalFields': {},
        },
        'name': 'Telegram Reply',
        'type': 'n8n-nodes-base.telegram',
        'typeVersion': 1.2,
        'position': [2100, 300],
        'credentials': {'telegramApi': {'id': TELEGRAM_CRED_ID, 'name': 'Huerta Bot Telegram'}},
    },

    # 16. Telegram Unauthorized
    {
        'parameters': {
            'chatId': "={{ $('Telegram Trigger').first().json.message.chat.id }}",
            'text': '⛔ No autorizado. Tu chat_id no está en la whitelist.',
            'additionalFields': {},
        },
        'name': 'Telegram Unauthorized',
        'type': 'n8n-nodes-base.telegram',
        'typeVersion': 1.2,
        'position': [540, 440],
        'credentials': {'telegramApi': {'id': TELEGRAM_CRED_ID, 'name': 'Huerta Bot Telegram'}},
    },
]

CONNECTIONS = {
    'Telegram Trigger': {'main': [[{'node': 'IF Autorizado', 'type': 'main', 'index': 0}]]},
    'IF Autorizado': {'main': [
        [{'node': 'Get Bot State', 'type': 'main', 'index': 0}],
        [{'node': 'Telegram Unauthorized', 'type': 'main', 'index': 0}],
    ]},
    'Get Bot State': {'main': [[{'node': 'Prep Gemini Input', 'type': 'main', 'index': 0}]]},
    'Prep Gemini Input': {'main': [[{'node': 'Gemini 2.5 Flash', 'type': 'main', 'index': 0}]]},
    'Gemini 2.5 Flash': {'main': [[{'node': 'Parse Gemini JSON', 'type': 'main', 'index': 0}]]},
    'Parse Gemini JSON': {'main': [[{'node': 'Switch Action', 'type': 'main', 'index': 0}]]},
    'Switch Action': {'main': [
        [{'node': 'Save Confirm State', 'type': 'main', 'index': 0}],
        [{'node': 'Execute Action', 'type': 'main', 'index': 0}],
        [{'node': 'Clear State', 'type': 'main', 'index': 0}],
        [{'node': 'Save Ask State', 'type': 'main', 'index': 0}],
        [{'node': 'Query Cama', 'type': 'main', 'index': 0}],
        [{'node': 'List Camas', 'type': 'main', 'index': 0}],
        [{'node': 'Format Reply', 'type': 'main', 'index': 0}],
    ]},
    'Save Confirm State': {'main': [[{'node': 'Format Reply', 'type': 'main', 'index': 0}]]},
    'Execute Action':     {'main': [[{'node': 'Format Reply', 'type': 'main', 'index': 0}]]},
    'Clear State':        {'main': [[{'node': 'Format Reply', 'type': 'main', 'index': 0}]]},
    'Save Ask State':     {'main': [[{'node': 'Format Reply', 'type': 'main', 'index': 0}]]},
    'Query Cama':         {'main': [[{'node': 'Format Reply', 'type': 'main', 'index': 0}]]},
    'List Camas':         {'main': [[{'node': 'Format Reply', 'type': 'main', 'index': 0}]]},
    'Format Reply':       {'main': [[{'node': 'Telegram Reply', 'type': 'main', 'index': 0}]]},
}

workflow = {
    'name': 'Huerta Bot - Telegram + Gemini',
    'nodes': NODES,
    'connections': CONNECTIONS,
    'settings': {'executionOrder': 'v1'},
}

# POST al n8n
payload = json.dumps(workflow, ensure_ascii=False).encode('utf-8')
req = urllib.request.Request(
    N8N_URL + '/api/v1/workflows',
    data=payload,
    headers={'X-N8N-API-KEY': N8N_KEY, 'Content-Type': 'application/json'},
    method='POST'
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read())
        print('\n✅ Workflow creado')
        print('ID:', resp.get('id'))
        print('Nombre:', resp.get('name'))
        print('Active:', resp.get('active'))
        print('\nEditalo en:', N8N_URL + '/workflow/' + resp.get('id', ''))
except urllib.error.HTTPError as e:
    print('\n❌ HTTP', e.code)
    print(e.read().decode()[:1500])
