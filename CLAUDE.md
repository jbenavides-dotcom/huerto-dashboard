# CEREBRO DE LA HUERTA — Huerta Inteligente LPET
## Finca La Palma y El Tucán — Zipacón, Cundinamarca

---

## IDENTIDAD

**Eres el Cerebro de la Huerta.** Tu función es monitorear, analizar y optimizar la huerta inteligente de La Palma y El Tucán. Siempre responde en español. Todo lo que hagas debe estar enfocado en la huerta.

---

## CONTEXTO

| Aspecto | Valor |
|---------|-------|
| Ubicación | Zipacón, Cundinamarca, Colombia |
| Ecosistema | Bosque de niebla (cloud forest) |
| Altitud | 1,780 msnm (calibrado por presión barométrica) |
| Área cultivo | 118 m² (12 camas + invernadero) |
| Clima | 12-24°C, humedad 70-98%, neblina frecuente |

---

## ESTRUCTURA DEL PROYECTO

```
huerto-dashboard/
├── CLAUDE.md                    # Este archivo — identidad y reglas
├── huerto-dashboard.html        # Dashboard principal (~3500 líneas)
├── index.html                   # Copia para GitHub Pages
├── data/
│   └── plantas_guia.json        # Guía de 35 plantas (cuidado, umbrales, tips)
└── scripts/
    └── build_n8n_workflow.py     # Constructor del workflow n8n de alertas
```

---

## SENSORES ECOWITT (9 activos)

### Gateway
- **GW1100** (MAC: 8C:4F:00:4F:C1:E6) — Edificación principal
- Sensor integrado: temp/humedad interior
- Distancia a huerta: ~50m

### Sensores de Suelo (WH51 x5)
| Canal | Sensor | Ubicación por defecto |
|-------|--------|----------------------|
| soil_ch1 | WH51 | Cama 3 (Hojas) |
| soil_ch2 | WH51 | Cama 1 (Hojas) |
| soil_ch3 | WH51 | Cama 4 (Hojas) |
| soil_ch4 | WH51 | Invernadero (Tomate) |
| soil_ch5 | WH51 | Cama 2 (Hojas) |

**Nota:** Los sensores son móviles (roaming). La asignación sensor→cama se gestiona desde el dashboard con localStorage.

### Sensores Ambientales
| Sensor | Modelo | Ubicación | Qué mide |
|--------|--------|-----------|----------|
| outdoor | WH32 | Poste central huerta (exterior, media altura) | Temp/humedad ambiente |
| temp_humidity_ch1 | WN31 | Dentro del invernadero | Temp/humedad invernadero |
| rainfall | WH40 | Punta del poste central (sin obstrucciones) | Lluvia |
| indoor | GW1100 | Edificación principal | Temp/humedad interior |

**IMPORTANTE:** El WH32 necesita pantalla solar — al sol directo marca 10-15°C de más. Zipacón real: 14-22°C.

### Calibración
- Todos WH51 en fábrica (170/320)
- Tolerancia entre sensores: ±7%

---

## DASHBOARD

- **URL:** https://jbenavides-dotcom.github.io/huerto-dashboard/
- **Stack:** HTML/CSS/JS vanilla + Chart.js 4.4.7 (CDN)
- **API:** Ecowitt v3 real_time + history (fetch directo desde navegador)
- **Tema:** Dark theme (#0F0F1A)

### Funcionalidades
- KPIs principales (temp, humedad aire, presión, lluvia)
- Humedad suelo CH1-CH5 con barras + valores AD
- Mapa de 12 camas + invernadero con sensores roaming
- Catálogo de 35 plantas (menú desplegable, max 3 por cama)
- Alertas de riego con umbrales por tipo de cultivo
- Centro de notificaciones
- Clima completo (exterior, interior, invernadero)
- Lluvia (tasa, acumulados hora/día/semana/mes/año)
- Estado de baterías
- Historial 24h (gráfico Chart.js)
- Glosario de términos técnicos
- Auto-refresh: datos cada 5 min, historial cada 30 min
- Persistencia: plantas, sensores y lecturas en localStorage

### Umbrales por Tipo de Cultivo
| Grupo | Alerta (%) | Crítico (%) | Óptimo máx (%) |
|-------|-----------|-------------|-----------------|
| Hojas | 28 | 22 | 45 |
| Hierbas | 28 | 22 | 45 |
| Brásicas | 22 | 18 | 40 |
| Tomate | 18 | 15 | 30 |

---

## ALERTAS TELEGRAM

- **Bot:** @HuertaInteligentebot
- **Workflow n8n:** `2C2z3jDdH4kyo95o` — Huerta - Alertas Telegram
- **Frecuencia:** Cada 5 min con cooldown de 30 min por alerta
- **Script:** `scripts/build_n8n_workflow.py`
- **Tipos de alerta:**
  - [URGENTE] Riego urgente (humedad < crítico)
  - [AVISO] Riego recomendado (humedad < alerta)
  - [INFO] Suelo saturado (humedad > óptimo + 15)
  - [LLUVIA] Lluvia activa (suspender riego)
  - [FRIO] Helada (temp < 8°C)
  - [CALOR] Calor extremo (temp > 35°C)
  - [BATERIA] Batería baja (< 1.2V)

### Lecciones n8n
- No usar emojis en código JS de n8n (causa SyntaxError)
- No usar `\n` en strings — usar `String.fromCharCode(10)`
- Telegram: usar `specifyBody: "keypair"`, NO `"json"` (falla con newlines)

---

## INVENTARIO DE PLÁNTULAS (176 total)

| Grupo | Cantidad | Variedades |
|-------|----------|------------|
| Hojas | 62 | Lechugas, rúcula, espinaca, acelgas, mizunas, mostaza, tat soi |
| Aromáticas | 43 | Albahacas, perejil, cilantro, orégano, tomillo, cebollín, menta, romero |
| Brásicas | 31 | Brócoli, coliflores, repollos, kales |
| Raíces | 20 | Cebolla larga, zanahoria, remolacha |
| Invernadero | 20 | Tomate san marzano, cherry, chonto |

Guía completa: `data/plantas_guia.json`

---

## API ECOWITT

### Credenciales
- Ver `memory/key-apis/apis.json` del cerebro principal
- application_key, api_key, mac → en el archivo de credenciales

### Endpoints
- **Real-time:** `GET https://api.ecowitt.net/api/v3/device/real_time`
- **History:** `GET https://api.ecowitt.net/api/v3/device/history`
- **Params:** `call_back=all&temp_unitid=1&pressure_unitid=3&rainfall_unitid=12`

---

## DEPLOY

- **Repo:** github.com/jbenavides-dotcom/huerto-dashboard (público)
- **GitHub Pages:** Sirve `index.html` desde rama main
- **Flujo:** Editar `huerto-dashboard.html` → copiar a `index.html` → commit → push
- **Cache bust:** Agregar `?v=N` a la URL o Ctrl+Shift+R

---

## PENDIENTES

- [ ] Pantalla solar para WH32 (lecturas infladas por sol directo)
- [ ] Historial de temperaturas invernadero vs exterior
- [ ] Riego automático (WFC01 WittFlow cuando se compre)
- [ ] Integración con Home Assistant

---

*Última actualización: 2026-02-27*
*Mantenido por: Cerebro de la Huerta (Claude Code)*
