"""Prueba local del bot contra Gemini API real.
Lee la key de apis.json (NO la hardcodea).
Simula varios comandos del usuario y muestra qué JSON devuelve Gemini.
"""
import json
import os
import sys
import io
import urllib.request
import urllib.error

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# --- Cargar credenciales desde apis.json ---
APIS_PATH = os.path.expanduser('~/Documents/cerebro-claude/key-apis/apis.json')
with open(APIS_PATH, 'r', encoding='utf-8') as f:
    apis = json.load(f)
GEMINI_KEY = apis['gemini']['api_key']
MODEL = apis['gemini'].get('model', 'gemini-2.5-flash')

# --- Leer system prompt del archivo .md ---
PROMPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'system-prompt.md')
with open(PROMPT_PATH, 'r', encoding='utf-8') as f:
    raw = f.read()

# Extraer el contenido entre los primeros ``` ... ```
first = raw.find('```')
if first == -1:
    print('ERROR: no encontré bloque ``` en system-prompt.md')
    sys.exit(1)
# Saltamos el primer ``` y su newline
start = raw.find('\n', first) + 1
end = raw.find('```', start)
SYSTEM_PROMPT = raw[start:end].strip()
print('System prompt cargado: ' + str(len(SYSTEM_PROMPT)) + ' chars')
print()


def ask_gemini(user_message, pending=None, memory=None, today='2026-04-07'):
    full_user = '\n'.join([
        'HOY: ' + today,
        'USUARIO: Jhonatan',
        'PENDING: ' + (json.dumps(pending) if pending else 'null'),
        'MEMORY: ' + (json.dumps(memory) if memory else 'null'),
        'MENSAJE: ' + user_message,
    ])

    payload = {
        'systemInstruction': {'parts': [{'text': SYSTEM_PROMPT}]},
        'contents': [{'role': 'user', 'parts': [{'text': full_user}]}],
        'generationConfig': {
            'temperature': 0,
            'maxOutputTokens': 800,
            'responseMimeType': 'application/json',
            'thinkingConfig': {'thinkingBudget': 0}
        }
    }

    url = 'https://generativelanguage.googleapis.com/v1beta/models/' + MODEL + ':generateContent?key=' + GEMINI_KEY
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}, method='POST'
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.loads(r.read())
        txt = resp['candidates'][0]['content']['parts'][0]['text']
        return json.loads(txt)
    except urllib.error.HTTPError as e:
        return {'_error': 'HTTP ' + str(e.code) + ': ' + e.read().decode()[:300]}
    except Exception as e:
        return {'_error': type(e).__name__ + ': ' + str(e)}


# --- Casos de prueba ---
tests = [
    ('Consulta simple',        'cama 1',                                        None, None),
    ('Listar todo',            'listar camas',                                  None, None),
    ('Cambiar plantas',        'cama 11 cambiar plantas por rucula y espinaca', None, None),
    ('Dejar vacia',            'cama 9 sin ocupacion',                          None, None),
    ('Ambiguo repollo',        'cama 12 cambiar plantas por repollo',           None, None),
    ('Responder ambiguo',      'morado',                                        None, {'intent':'update_plantas','cama_id':'cama12'}),
    ('Ambiguo lechuga cosecha','cosecha cama 3 lechuga 2 kg',                   None, None),
    ('Cosecha especifica',     'cosecha cama 3 lechuga crespa 2 kg',            None, None),
    ('Riego',                  'regue la cama 5',                               None, None),
    ('Plaga',                  'plaga cama 4 pulgones',                         None, None),
    ('Sensor',                 'cama 5 sensor ch3',                             None, None),
    ('Sin sensor',             'cama 5 sin sensor',                             None, None),
    ('Confirmar',              'si',                                            {'type':'update_plantas','cama_id':'cama11','plantas':['rucula','espinaca']}, None),
    ('Cancelar',               'no, cancela',                                   {'type':'update_plantas','cama_id':'cama11','plantas':['rucula','espinaca']}, None),
    ('Ruido',                  'hola',                                          None, None),
]

for (name, msg, pending, memory) in tests:
    print('─' * 60)
    print('[' + name + ']')
    print('> ' + msg)
    if pending:
        print('  (PENDING: ' + json.dumps(pending) + ')')
    if memory:
        print('  (MEMORY: ' + json.dumps(memory) + ')')
    result = ask_gemini(msg, pending=pending, memory=memory)
    print('< ' + json.dumps(result, ensure_ascii=False, indent=2))
    print()
