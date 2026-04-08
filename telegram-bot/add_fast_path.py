"""Agregar fast-path al workflow del bot para bypassear Gemini en comandos simples."""
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

NEW_PREP = r'''
const msg = $('Telegram Trigger').first().json.message;
const rawText = (msg.text || '').trim();
const userText = rawText.toLowerCase();
const chatId = msg.chat.id;
const userName = msg.from.first_name || 'usuario';
const today = new Date().toISOString().slice(0, 10);

// Cargar state
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

// FAST PATH: parseo local sin llamar a Gemini
function fastParse(text) {
  const t = text.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, ' ').trim();

  // Confirmaciones (solo si hay pending)
  if (pending) {
    if (/^(si|sii|ok|dale|confirmo|listo|yes|acepto|va|okey|okay)$/.test(t)) {
      return { action: 'confirmed', reply: null };
    }
    if (/^(no|cancela|cancelar|ya no|espera|atras|stop)$/.test(t)) {
      return { action: 'cancelled', reply: '❎ Cancelado. ¿Qué querés hacer?' };
    }
  }

  // Listar camas
  if (/^(listar camas?|lista(r)?|ver todas|mostrar camas?|resumen|estado huerta|ver camas)$/.test(t)) {
    return { action: 'list_camas', reply: null };
  }

  // Query cama: 'cama N', 'cama invernadero', 'c1', 'la 1'
  const mQuery = t.match(/^(?:cama\s*|c|la\s+)(\d{1,2}|invernadero|inver|greenhouse)$/);
  if (mQuery) {
    const n = mQuery[1];
    if (n === 'invernadero' || n === 'inver' || n === 'greenhouse') {
      return { action: 'query_cama', cama_id: 'invernadero', reply: null };
    }
    const num = parseInt(n, 10);
    if (num >= 1 && num <= 12) {
      return { action: 'query_cama', cama_id: 'cama' + num, reply: null };
    }
  }

  // Solo 'invernadero' sin 'cama'
  if (/^(invernadero|inver|greenhouse)$/.test(t)) {
    return { action: 'query_cama', cama_id: 'invernadero', reply: null };
  }

  return null;  // necesita Gemini
}

const fast = fastParse(userText);

if (fast) {
  return [{
    json: {
      skip_gemini: true,
      action: fast.action,
      cama_id: fast.cama_id || null,
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

# Validar sintaxis
with open(os.path.expanduser('~/AppData/Local/Temp/prep_fast.js'), 'w', encoding='utf-8') as f:
    f.write(new_prep_code)
r = subprocess.run(
    ['node', '-e', "new Function(require('fs').readFileSync(process.env.F,'utf8'));console.log('OK')"],
    capture_output=True, text=True,
    env={**os.environ, 'F': os.path.expanduser('~/AppData/Local/Temp/prep_fast.js')}
)
print('Prep syntax:', r.stdout.strip() or r.stderr.strip()[:400])
if 'OK' not in r.stdout:
    sys.exit(1)

# Leer workflow actual
req = urllib.request.Request(
    f'https://jhona.app.n8n.cloud/api/v1/workflows/{wf_id}',
    headers={'X-N8N-API-KEY': key}
)
with urllib.request.urlopen(req, timeout=15) as r:
    wf = json.loads(r.read())

# Update Prep code
for node in wf['nodes']:
    if node['name'] == 'Prep Gemini Input':
        node['parameters']['jsCode'] = new_prep_code
        print('Prep code actualizado')

# Agregar nodo IF si no existe
exists = any(n['name'] == 'IF Skip Gemini' for n in wf['nodes'])
if not exists:
    wf['nodes'].append({
        'parameters': {
            'conditions': {
                'options': {'caseSensitive': True, 'leftValue': '', 'typeValidation': 'loose', 'version': 2},
                'combinator': 'and',
                'conditions': [{
                    'id': 'cond-skip',
                    'leftValue': '={{ $json.skip_gemini }}',
                    'rightValue': '',
                    'operator': {'type': 'boolean', 'operation': 'true', 'singleValue': True}
                }]
            },
            'options': {}
        },
        'name': 'IF Skip Gemini',
        'type': 'n8n-nodes-base.if',
        'typeVersion': 2,
        'position': [1090, 220],
    })
    print('IF Skip Gemini node agregado')

# Re-wire: Prep -> IF -> (true: Switch) / (false: Gemini -> Parse -> Switch)
wf['connections']['Prep Gemini Input'] = {
    'main': [[{'node': 'IF Skip Gemini', 'type': 'main', 'index': 0}]]
}
wf['connections']['IF Skip Gemini'] = {
    'main': [
        [{'node': 'Switch Action', 'type': 'main', 'index': 0}],
        [{'node': 'Gemini 2.5 Flash', 'type': 'main', 'index': 0}]
    ]
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
    print(e.read().decode()[:500])
