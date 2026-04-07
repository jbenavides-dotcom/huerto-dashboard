import json, urllib.request

js_code = """const data = $input.first().json.data;
const alerts = [];
const now = Date.now();
const COOLDOWN_MS = 30 * 60 * 1000;
const NL = String.fromCharCode(10);

const staticData = $getWorkflowStaticData('global');
if (!staticData.sentAlerts) staticData.sentAlerts = {};

const SENSORS = {
  soil_ch1: { label: 'Cama 3 (Hojas)', group: 'hojas' },
  soil_ch2: { label: 'Cama 1 (Hojas)', group: 'hojas' },
  soil_ch3: { label: 'Cama 4 (Hojas)', group: 'hojas' },
  soil_ch4: { label: 'Invernadero (Tomate)', group: 'tomate' },
  soil_ch5: { label: 'Cama 2 (Hojas)', group: 'hojas' }
};

const THRESHOLDS = {
  hojas:    { alert: 28, critical: 22, optMax: 45 },
  hierbas:  { alert: 28, critical: 22, optMax: 45 },
  brasicas: { alert: 22, critical: 18, optMax: 40 },
  tomate:   { alert: 18, critical: 15, optMax: 30 }
};

for (const [key, sensor] of Object.entries(SENSORS)) {
  const pct = parseFloat(data[key]?.soilmoisture?.value);
  if (isNaN(pct)) continue;
  const t = THRESHOLDS[sensor.group] || THRESHOLDS.hojas;
  if (pct < t.critical) {
    alerts.push({ id: key + '_critical', text: '[URGENTE] ' + sensor.label + ': ' + pct + '% - Riego urgente!' });
  } else if (pct < t.alert) {
    alerts.push({ id: key + '_alert', text: '[AVISO] ' + sensor.label + ': ' + pct + '% - Riego recomendado' });
  } else if (pct > t.optMax + 15) {
    alerts.push({ id: key + '_saturado', text: '[INFO] ' + sensor.label + ': ' + pct + '% - Suelo saturado' });
  }
}

const rainRate = parseFloat(data.rainfall?.rain_rate?.value);
if (!isNaN(rainRate) && rainRate > 0) {
  alerts.push({ id: 'rain_active', text: '[LLUVIA] Lluvia activa: ' + rainRate.toFixed(1) + ' mm/hr - Suspender riego' });
}

const temp = parseFloat(data.outdoor?.temperature?.value);
if (!isNaN(temp) && temp < 8) {
  alerts.push({ id: 'frost_' + Math.floor(temp), text: '[FRIO] Temperatura ' + temp.toFixed(1) + ' C - Proteger cultivos!' });
}
if (!isNaN(temp) && temp > 35) {
  alerts.push({ id: 'heat_' + Math.floor(temp), text: '[CALOR] Temperatura ' + temp.toFixed(1) + ' C - Calor extremo!' });
}

const battery = data.battery || {};
for (const [key, batt] of Object.entries(battery)) {
  if (batt.unit === 'V' && parseFloat(batt.value) < 1.2) {
    alerts.push({ id: 'batt_' + key, text: '[BATERIA] ' + key + ': ' + batt.value + 'V - Cambiar pila' });
  }
}

const newAlerts = alerts.filter(a => {
  const lastSent = staticData.sentAlerts[a.id] || 0;
  return (now - lastSent) > COOLDOWN_MS;
});

for (const a of newAlerts) {
  staticData.sentAlerts[a.id] = now;
}

for (const [id, ts] of Object.entries(staticData.sentAlerts)) {
  if ((now - ts) > 2 * 60 * 60 * 1000) delete staticData.sentAlerts[id];
}

if (newAlerts.length === 0) {
  return [{ json: { hasAlerts: false, message: '' } }];
}

const lines = ['HUERTA INTELIGENTE - ALERTAS', ''];
newAlerts.forEach(a => lines.push(a.text));
lines.push('');
lines.push('Dashboard: https://jbenavides-dotcom.github.io/huerto-dashboard/');
const msg = lines.join(NL);

return [{ json: { hasAlerts: true, message: msg, alertCount: newAlerts.length } }];"""

workflow = {
    "name": "Huerta - Alertas Telegram",
    "nodes": [
        {
            "parameters": {"rule": {"interval": [{"field": "minutes", "minutesInterval": 5}]}},
            "id": "schedule-1", "name": "Cada 5 min",
            "type": "n8n-nodes-base.scheduleTrigger", "typeVersion": 1.2,
            "position": [220, 300]
        },
        {
            "parameters": {
                "url": "https://api.ecowitt.net/api/v3/device/real_time",
                "sendQuery": True,
                "queryParameters": {"parameters": [
                    {"name": "application_key", "value": "2A298127832EF7B5F0495F16B07F7B5E"},
                    {"name": "api_key", "value": "83b66e21-a6cf-445f-b14e-2810189d3e6d"},
                    {"name": "mac", "value": "8C:4F:00:4F:C1:E6"},
                    {"name": "call_back", "value": "all"},
                    {"name": "temp_unitid", "value": "1"},
                    {"name": "pressure_unitid", "value": "3"},
                    {"name": "rainfall_unitid", "value": "12"}
                ]},
                "options": {}
            },
            "id": "ecowitt-1", "name": "Ecowitt API",
            "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
            "position": [440, 300]
        },
        {
            "parameters": {"jsCode": js_code},
            "id": "code-1", "name": "Evaluar Alertas",
            "type": "n8n-nodes-base.code", "typeVersion": 2,
            "position": [660, 300]
        },
        {
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": ""},
                    "conditions": [{"id": "cond-1", "leftValue": "={{ $json.hasAlerts }}", "rightValue": True,
                        "operator": {"type": "boolean", "operation": "equals", "singleValue": True}}],
                    "combinator": "and"
                }
            },
            "id": "if-1", "name": "Hay alertas?",
            "type": "n8n-nodes-base.if", "typeVersion": 2.2,
            "position": [880, 300]
        },
        {
            "parameters": {
                "method": "POST",
                "url": "https://api.telegram.org/bot8723932539:AAEpxznYjgF8zEiAJ1ggPvdlH8eQoUkisMM/sendMessage",
                "sendBody": True, "specifyBody": "keypair",
                "bodyParameters": {
                    "parameters": [
                        {"name": "chat_id", "value": "1511283217"},
                        {"name": "text", "value": "={{ $json.message }}"}
                    ]
                },
                "options": {}
            },
            "id": "telegram-1", "name": "Enviar Telegram",
            "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
            "position": [1100, 200]
        }
    ],
    "connections": {
        "Cada 5 min": {"main": [[{"node": "Ecowitt API", "type": "main", "index": 0}]]},
        "Ecowitt API": {"main": [[{"node": "Evaluar Alertas", "type": "main", "index": 0}]]},
        "Evaluar Alertas": {"main": [[{"node": "Hay alertas?", "type": "main", "index": 0}]]},
        "Hay alertas?": {"main": [[{"node": "Enviar Telegram", "type": "main", "index": 0}], []]}
    },
    "settings": {"executionOrder": "v1", "callerPolicy": "workflowsFromSameOwner"}
}

# Save and upload
payload = json.dumps(workflow, ensure_ascii=True).encode('utf-8')

req = urllib.request.Request(
    'https://jhona.app.n8n.cloud/api/v1/workflows/2C2z3jDdH4kyo95o',
    data=payload,
    headers={
        'Content-Type': 'application/json',
        'X-N8N-API-KEY': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIwZTQ1NmU3Ni00NTExLTRjZDQtOTc2My01ZDFiMmRhMmVjOTMiLCJpc3MiOiJuOG4iLCJhdWQiOiJwdWJsaWMtYXBpIiwianRpIjoiNjMzMDU3ODMtYTBmOC00ZTgwLWFiNWItYzRkZWRhNzUzNzRkIiwiaWF0IjoxNzcwNzU1NzUyLCJleHAiOjE3NzMyOTE2MDB9.Z0G2XNU248zOh9Py-tBCrS4zBDTwGSIdqD9ozMphknc'
    },
    method='PUT'
)
resp = urllib.request.urlopen(req)
result = json.loads(resp.read())
print(f"OK - {result['name']} - Active: {result['active']}")

# Verify the jsCode doesn't have unescaped newlines in string literals
code_node = [n for n in result['nodes'] if n['name'] == 'Evaluar Alertas'][0]
code = code_node['parameters']['jsCode']
print(f"Code length: {len(code)} chars")
print(f"Uses String.fromCharCode: {'String.fromCharCode' in code}")
print(f"Has emoji: {any(ord(c) > 127 for c in code)}")
