# Bot Telegram — Huerta LP&ET

Bot que permite actualizar la huerta desde Telegram usando lenguaje natural. Flujo:

```
Usuario → @HuertaInteligentebot → n8n webhook → Claude Haiku → Supabase → Telegram response
```

## Estado

- ✅ SQL de tablas ejecutado (`huerta_camas`, `huerta_bitacora`)
- ✅ Dashboard conectado a Supabase
- ✅ System prompt para Claude Haiku diseñado
- ✅ Workflow n8n JSON generado
- ⏳ **Pendiente:** importar workflow en n8n y configurar credenciales
- ⏳ **Pendiente:** probar end-to-end

## Archivos

| Archivo | Propósito |
|---|---|
| `system-prompt.md` | System prompt completo de Claude Haiku con catálogo de plantas y ejemplos |
| `workflow.json` | Workflow n8n listo para importar |
| `test-examples.md` | Mensajes de prueba para validar cada acción |

## Setup (en n8n)

### 1. Crear credenciales

Antes de importar el workflow, crea 2 credenciales en n8n:

#### a) Telegram API (bot @HuertaInteligentebot)
- Menú izquierdo → **Credentials** → **+ New**
- Buscar **"Telegram API"**
- **Access Token:** ver `memory/key-apis/apis.json` → `telegram.bot_token` (NUNCA pegar el token en archivos del repo)
- Guardar con nombre exacto: **"Telegram Huerta Bot"**

#### b) Gemini API (Google AI Studio)
- **Credentials** → **+ New**
- Buscar **"Header Auth"** (aunque Gemini usa query param `?key=`, guardamos la key en una credencial para evitar hardcodearla)
- **Name:** `x-goog-api-key` (dummy, no se usa como header)
- **Value:** tu API key de Gemini (ej: `AIzaSy...`)
- Guardar con nombre exacto: **"Gemini API Key"**

Nota: el nodo HTTP del workflow inyecta la key en el query string del URL usando `{{ $credentials.genericApi.apiKey }}`. Así la key queda fuera del código del workflow.

Si no tienes API key de Gemini:
1. Ir a https://aistudio.google.com/apikey
2. Clic en **"Create API key"**
3. Seleccionar un proyecto de Google Cloud o crear uno nuevo
4. Copiar la key (empieza con `AIzaSy...`)

**Costo:** Gemini 2.5 Flash tiene tier gratuito (ver https://ai.google.dev/gemini-api/docs/rate-limits):
- 10 RPM (requests per minute)
- 250 RPD (requests per day)
- 250k TPM (tokens per minute)

Para el volumen esperado de la huerta (<50 mensajes/día) el tier gratuito sobra.

⚠️ **Si tu proyecto muestra "quota exceeded"** incluso sin haber usado nada, puede ser que necesites:
1. Activar la Generative Language API en Google Cloud Console del proyecto
2. Asegurarte que la región del proyecto soporta el tier gratuito (la mayoría sí)
3. Esperar unos minutos tras crear la key (propagación)

### 2. Importar el workflow

1. En n8n → **Workflows** → clic en el menú (**⋯**) arriba → **Import from File**
2. Selecciona `workflow.json`
3. El workflow se carga con 12 nodos
4. **IMPORTANTE:** después de importar, entra a cada nodo que use credenciales y re-selecciona la credencial:
   - **Telegram Trigger** → seleccionar "Telegram Huerta Bot"
   - **Telegram Reply** → seleccionar "Telegram Huerta Bot"
   - **Telegram Unauthorized** → seleccionar "Telegram Huerta Bot"
   - **Gemini 2.5 Flash** → seleccionar "Gemini API Key"

### 3. Activar el workflow

1. Toggle **Active** arriba a la derecha
2. n8n registra el webhook automáticamente en Telegram
3. Listo

### 4. Probar

Enviá al bot por Telegram:
```
cama 1
```
Debería responder con las plantas actuales de la cama 1.

Si **no responde**, revisá la ejecución en n8n → pestaña **Executions** del workflow → ver en qué nodo falló.

## Comandos soportados

Ver `test-examples.md` para la lista completa. Resumen:

### Cambiar plantas
- `cama 1 cambiar plantas por repollo morado, coliflor y cebollín`
- `cama 9 sin ocupación`
- `cama 5 agregar albahaca`
- `cama 5 quitar ají jalapeño`

### Sensores
- `cama 5 sensor ch3`
- `cama 5 sin sensor`

### Bitácora
- `cosecha cama 3 lechuga 2 kg`
- `regué la cama 5`
- `plaga cama 4 pulgones`
- `nota cama 1 se ve amarilla`

### Consultas
- `cama 1`
- `listar camas`

## Defaults (se pueden cambiar)

| Default | Valor |
|---|---|
| Whitelist chat_ids | Solo `1511283217` (Jhonatan) |
| Planta genérica "repollo" | repollo_morado |
| Planta genérica "lechuga" | lechuga_crespa |
| Planta genérica "coliflor" | coliflor_blanca |
| Planta genérica "acelga" | acelga_comun |
| Modelo LLM | `gemini-2.5-flash` |
| Temperature | 0 (determinístico) |
| Max output tokens | 800 |
| Thinking budget | 0 (desactivado — respuestas directas) |
| Response MIME | `application/json` (fuerza JSON válido) |

Para agregar más personas a la whitelist, editar el nodo **IF Autorizado** y añadir condiciones OR con los chat_ids adicionales.

## Limitaciones conocidas

1. **add_plantas y remove_plantas no están completos** — el nodo "Prep Add Plantas" solo prepara la estructura; falta un paso de GET → merge → PATCH. Se puede resolver con Claude mismo manejando el "merge": en vez de add_plantas/remove_plantas, Claude siempre devuelve el set completo final y usamos update_plantas. Ajuste pendiente en el prompt.

2. **No hay histórico de quién cambió qué** a nivel de auditoría — solo el campo `updated_by: "telegram"`. Para más detalle habría que agregar un log separado.

3. **No hay rate limiting** — si alguien manda 100 mensajes seguidos, Claude los procesa todos. Para la finca no es problema.

## Seguridad

- Whitelist de chat_ids → solo usuarios autorizados pueden escribir a la BD
- Credenciales Telegram y Anthropic encriptadas en n8n (no en el código)
- Supabase anon key permite escribir a huerta_camas y huerta_bitacora (por diseño, son tablas públicas)
- Ningún mensaje del bot expone el token del bot

## Costos estimados

- **Telegram:** $0 (gratuito)
- **Gemini 2.5 Flash:** $0 mientras caben en el tier gratuito (250 requests/día, ~7500/mes)
- **n8n:** incluido en el plan actual de jhona.app.n8n.cloud
- **Supabase:** incluido en el tier gratuito (500 MB, 50k req/mes)

**Total: $0 USD/mes** (mientras no pasen de 250 mensajes/día al bot)

Si el volumen supera el tier gratuito, Gemini cobra ~$0.0002 por 1k tokens de input y $0.0008 por 1k output. Para 1000 mensajes/mes serían ~$0.50 USD.

## Próximos pasos

1. Importar + probar con los comandos básicos
2. Ajustar defaults de plantas si es necesario
3. Agregar más chat_ids a la whitelist (cuando otros del equipo quieran usar el bot)
4. Fase 2: agregar comandos para **animales** (`animales`, `ordenes`, `actividades`, `huevos`)
5. Fase 3: **reportes programados** — ej: cada domingo el bot manda un resumen semanal con cosechas, siembras y alertas
