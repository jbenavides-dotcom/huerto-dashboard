# 🌿 Glosario del Bot — Huerta & Animales

Bot de Telegram para gestionar la huerta y el inventario animal de **La Palma y el Tucán**.

- **Bot:** `@HuertaInteligentebot`
- **Idioma:** español (no importan mayúsculas, tildes ni signos)
- **Confirma antes de escribir:** casi todos los comandos piden `sí/no` antes de guardar

---

## Reglas generales

1. **No importan las mayúsculas ni las tildes.** Estos 3 comandos son equivalentes:
   - `cama 1`
   - `CAMA 1`
   - `Cama 1`
2. **Antes de cada cambio el bot pregunta** `¿Confirmas? (sí/no)`. Si respondés:
   - `sí`, `si`, `ok`, `dale`, `listo`, `confirmo` → ejecuta
   - `no`, `cancela`, `cancelar` → cancela sin tocar nada
3. **Si hay ambigüedad** (ej: "repollo" = morado o verde?), el bot pregunta cuál querés. Respondés y sigue con la confirmación.
4. **Los comandos de lectura no piden confirmación** (`cama 1`, `animales`, `listar camas`, etc).
5. **Si no respondés en 10 minutos**, el bot olvida lo que estaba por hacer y hay que empezar de nuevo.

---

# 🌱 COMANDOS DE HUERTA

## Consultas (lectura)

| Comando | Qué hace |
|---|---|
| `cama 1` | Muestra plantas, sensor y grupo de la Cama 1 |
| `cama 7` | Cualquier número de 1 a 12 |
| `invernadero` | Información del invernadero |
| `listar camas` | Resumen de todas las camas con plantas y sensores |
| `resumen` | Igual que listar camas |

## Cambiar plantas de una cama

### Reemplazar todas las plantas
```
cama 1 cambiar plantas por repollo morado, coliflor y cebollín
cama 3 ahora tiene lechuga crespa y espinaca
cama 5 cambiar por zanahoria y perejil
```

### Dejar una cama vacía
```
cama 9 sin ocupación
cama 11 vacía
```

### Agregar una planta sin borrar lo que hay
```
cama 5 agregar albahaca
cama 2 sumar menta
```

### Quitar una planta específica
```
cama 5 quitar ají jalapeño
cama 1 eliminar cebollín
```

### Plantas ambiguas
Si decís una planta genérica, el bot pregunta:
```
Vos: cama 11 cambiar por repollo
Bot: ¿Qué tipo de repollo? • Repollo Morado • Repollo Verde
Vos: morado
Bot: Vas a cambiar Cama 11 a: Repollo Morado. ¿Confirmas?
Vos: sí
```

Lista de plantas genéricas que preguntan variedad:
- **repollo** → Morado, Verde
- **lechuga** → Batavia, Romana, Crespa, Morada Lisa
- **tomate** → San Marzano, Cherry, Chonto
- **coliflor** → Blanca, Verde
- **kale** → Toscano, Rizado
- **albahaca** → Común, Morada
- **acelga** → Común, Roja, Amarilla
- **mizuna** → Verde, Roja

## Cambiar sensor

```
cama 5 sensor ch3
cama 2 sensor 1
```

Si ese sensor ya estaba en otra cama, **el bot lo mueve automáticamente** (queda solo en la cama nueva).

### Quitar sensor
```
cama 5 sin sensor
quitar sensor de cama 3
```

## Bitácora (registrar eventos)

### Cosecha
```
cosecha cama 3 lechuga crespa 2 kg
cosecha cama 1 cebollín 500 g
coseché 20 tomates cherry del invernadero
```

### Riego
```
regué la cama 5
riego cama 3
```

### Siembra
```
sembré albahaca en la cama 9
sembrar rúcula en cama 11
```

### Plaga
```
plaga cama 4 pulgones
hay babosas en la cama 3
```

### Observación general
```
la cama 6 se ve amarilla
nota cama 1 floración abundante
```

### Fertilización
```
fertilicé la cama 1 con compost
aplicación de humus en invernadero
```

---

# 🐾 COMANDOS DE ANIMALES

## Consultas (lectura)

| Comando | Qué hace |
|---|---|
| `animales` | Resumen completo de todos los animales |
| `listar animales` | Igual |
| `inventario animales` | Igual |
| `cuántos pollitos` | Cantidad de pollitos activos |
| `cuántas gallinas` | Cantidad de gallinas activas |
| `cuántos gallos` | Machos adultos |
| `cuántos conejos` | Conejos activos |
| `cuántas larvas` | Lotes de mosca soldado |
| `cuántos pollitos muertos` | Solo los fallecidos |

## Tipos de animales soportados

| Lo que escribís | Se registra como |
|---|---|
| pollito / pollitos | Pollito (Ave, Indeterminado) |
| gallina / gallinas / ponedora | Gallina (Ave, Hembra) |
| gallo / gallos | Gallo (Ave, Macho) |
| conejo / conejos | Conejo |
| cuy / cuyes / cobayo | Cuy |
| pato / patos | Pato |
| ganso / gansos | Ganso |
| pavo / pavos | Pavo |
| codorniz / codornices | Codorniz |
| larva / larvas / mosca soldado / bsf | Mosca Soldado (BSF) |

## Nacimientos / entradas

```
nacieron 3 pollitos
compré 10 gallinas ponedoras
me regalaron 2 conejos
entraron 5 cuyes
```

El bot crea registros consecutivos (`Pollito-51`, `Pollito-52`, etc).

## Muertes, ventas, pérdidas

```
murió 1 pollito
se murieron 3 conejos
vendí 2 gallinas
perdí 1 pollo
```

El bot marca **los últimos N activos** del tipo indicado y registra la acción en actividades con la fecha.

## Huevos

### Sin decir cuántos rotos (te pregunta)
```
hoy puse 14 huevos
recogí 20 huevos
```
El bot responde: `¿Hubo huevos rotos? (número o 'no')`
- Respondés `2` → registra 14 buenos + 2 rotos
- Respondés `no` o `0` → registra 14 buenos sin rotos

### Diciendo los rotos directo (sin pregunta)
```
14 huevos 2 rotos
20 huevos ninguno roto
hoy 10 huevos sin rotos
```

## Vacunación / cuidados sanitarios

```
vacuné las 4 gallinas contra newcastle
desparasité los pollitos con ivermectina
revisión veterinaria de los conejos
```

---

# 🚫 Lo que el bot NO hace (todavía)

- No maneja animales grandes con nombre (vacas, caballos, cerdos individuales con nombre)
- No registra ventas con monto (`vendí X a $Y`) — solo marca vendido
- No maneja costos (alimentación, veterinario)
- No hace reportes semanales/mensuales (cosechas, producción de huevos, etc.)
- No modifica el dashboard visual (pero sí la base de datos que lo alimenta)

---

# ⚙️ Modo técnico (para Jhonatan/admin)

## Arquitectura
```
Telegram → n8n webhook → [Fast Parse o Gemini Flash Lite] → Supabase → Telegram
```

- **Workflow n8n:** `IeHSEjjZ1GE6JMU1` (Huerta Bot - Telegram + Gemini)
- **LLM:** `gemini-flash-lite-latest` (Google AI Studio, free tier)
- **BD:** Supabase `pzkxbymwvimwnfmqoihj`
- **Tablas:** `huerta_camas`, `huerta_bitacora`, `huerta_bot_state`, `animales`, `actividades`, `ordenes`, `huevos`

## Fast-path (sin llamar a Gemini)
Estos comandos se procesan localmente y ahorran cuota de Gemini:
- `sí` / `no` (confirmaciones)
- `cama N`, `invernadero`, `listar camas`
- `animales`, `listar animales`
- `cuántos [tipo de animal]`

## Errores comunes

| Error | Causa | Solución |
|---|---|---|
| "No entendí" | Gemini no reconoció el comando | Usa ejemplos del glosario |
| "Error ejecutando" | Fallo en Supabase | Reintentá en unos segundos |
| "rate limit" / "too many requests" | Saturaste Gemini (10 RPM) | Esperá 1 minuto |
| No responde nada | Workflow desactivado o Telegram con delay | Verificá en n8n |

## Whitelist de usuarios

Solo usuarios autorizados pueden usar el bot. El chat_id debe estar en la lista del nodo `IF Autorizado`. Para agregar más:
1. La persona manda un mensaje al bot
2. Admin extrae su chat_id desde n8n executions
3. Admin agrega el chat_id al IF en el workflow

---

# 📝 Ejemplos reales de conversaciones

## Ejemplo 1 — Cambiar plantas de una cama
```
Vos: cama 11 cambiar plantas por rucula y espinaca
Bot: Vas a cambiar Cama 11 a:
     • Rúcula
     • Espinaca
     ¿Confirmas? (sí/no)
Vos: sí
Bot: ✅ Cama actualizada.
```

## Ejemplo 2 — Cosecha
```
Vos: cosecha cama 3 lechuga crespa 2 kg
Bot: Vas a registrar:
     🌱 Cosecha · Cama 3
     2 kg de Lechuga Crespa
     ¿Confirmas? (sí/no)
Vos: sí
Bot: ✅ Registrado en bitácora.
```

## Ejemplo 3 — Huevos con ask
```
Vos: hoy puse 14 huevos
Bot: ¿Hubo huevos rotos? (número o 'no')
Vos: 1
Bot: Vas a registrar:
     🥚 14 huevos (1 roto) en Gallinero
     ¿Confirmas? (sí/no)
Vos: sí
Bot: ✅ Huevos registrados: 14 (1 rotos).
```

## Ejemplo 4 — Muerte de animal
```
Vos: murió 1 pollito
Bot: Vas a marcar como Fallecido:
     💀 1 pollito
     ¿Confirmas? (sí/no)
Vos: sí
Bot: ✅ Fallecido: 1 pollito.
```

## Ejemplo 5 — Consulta rápida
```
Vos: cuántos pollitos
Bot: 29 pollitos activos
```

## Ejemplo 6 — Ambigüedad con memoria
```
Vos: cama 12 agregar tomate
Bot: ¿Qué tomate?
     • Tomate San Marzano
     • Tomate Cherry
     • Tomate Chonto
Vos: cherry
Bot: Vas a agregar Tomate Cherry a Cama 12.
     ¿Confirmas? (sí/no)
Vos: sí
Bot: ✅ Cama actualizada.
```

---

*Última actualización: 2026-04-08*
*Mantenido por: Cerebro Claude Code*
