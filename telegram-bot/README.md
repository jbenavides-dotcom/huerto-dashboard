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
- **Access Token:** el de apis.json (`8723932539:AAFge0kvNr8Mi7G3VJQCCw97mvPuNQ4k4e4`)
- Guardar con nombre exacto: **"Telegram Huerta Bot"**

#### b) Anthropic API (para Claude Haiku)
- **Credentials** → **+ New**
- Buscar **"Header Auth"**
- **Name:** `x-api-key`
- **Value:** tu API key de Anthropic (ej: `sk-ant-api03-...`)
- Guardar con nombre exacto: **"Anthropic API"**

Si no tienes API key de Anthropic:
1. Crear cuenta en https://console.anthropic.com
2. Ir a **API Keys** → **Create Key**
3. Cargar $5-10 USD de crédito (dura meses, Claude Haiku es barato: ~$0.001 por mensaje)

### 2. Importar el workflow

1. En n8n → **Workflows** → clic en el menú (**⋯**) arriba → **Import from File**
2. Selecciona `workflow.json`
3. El workflow se carga con 12 nodos
4. **IMPORTANTE:** después de importar, entra a cada nodo que use credenciales y re-selecciona la credencial:
   - **Telegram Trigger** → seleccionar "Telegram Huerta Bot"
   - **Telegram Reply** → seleccionar "Telegram Huerta Bot"
   - **Telegram Unauthorized** → seleccionar "Telegram Huerta Bot"
   - **Claude Haiku** → seleccionar "Anthropic API"

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
| Modelo Claude | claude-haiku-4-5-20251001 |
| Temperature | 0 (determinístico) |
| Max tokens | 600 |

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
- **Claude Haiku:** ~$0.001 por mensaje (input ~2k tokens del system prompt + output ~200 tokens). Con 1000 mensajes/mes = ~$1 USD
- **n8n:** incluido en el plan actual de jhona.app.n8n.cloud
- **Supabase:** incluido en el tier gratuito (500 MB, 50k req/mes)

**Total: < $2 USD/mes**

## Próximos pasos

1. Importar + probar con los comandos básicos
2. Ajustar defaults de plantas si es necesario
3. Agregar más chat_ids a la whitelist (cuando otros del equipo quieran usar el bot)
4. Fase 2: agregar comandos para **animales** (`animales`, `ordenes`, `actividades`, `huevos`)
5. Fase 3: **reportes programados** — ej: cada domingo el bot manda un resumen semanal con cosechas, siembras y alertas
