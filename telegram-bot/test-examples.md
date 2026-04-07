# Ejemplos de prueba — Bot Huerta

Mensajes reales para probar cada acción. Los resultados esperados están al lado.

## 1. Consultas (lectura — seguras de probar primero)

| Mensaje | Respuesta esperada |
|---|---|
| `cama 1` | 📍 Cama 1 · Grupo: brasicas · Sensor: CH2 · Plantas: Repollo morado, Coliflor Blanca, Cebollín |
| `que hay en la cama 3` | 📍 Cama 3 · Plantas: Lechuga Crespa, Lechuga Morada Lisa |
| `cama 9` | 📍 Cama 9 · Plantas: sin ocupación |
| `listar camas` | 🌿 Camas de la huerta: lista con las 13 |
| `invernadero` | 📍 Invernadero · Sensor: CH4 · Plantas: Tomate San Marzano, Tomate Cherry, Tomate Chonto |

## 2. Cambiar plantas

| Mensaje | Acción en BD |
|---|---|
| `cama 11 cambiar plantas por rúcula y espinaca` | UPDATE cama11 SET plantas = ['rucula','espinaca'] |
| `cama 9 sin ocupación` | UPDATE cama9 SET plantas = [] |
| `en la cama 12 ahora hay kale toscano y kale rizado` | UPDATE cama12 SET plantas = ['kale_toscano','kale_rizado'] |
| `cambiar cama 3 a lechuga batavia y lechuga romana` | UPDATE cama3 SET plantas = ['lechuga_batavia','lechuga_romana'] |

## 3. Agregar / quitar plantas

| Mensaje | Acción esperada |
|---|---|
| `cama 1 agregar menta` | Añade menta a las plantas existentes |
| `cama 5 quitar ají jalapeño` | Quita solo ají, deja caléndula y repollo |
| `sumar cilantro en la cama 2` | Añade cilantro |

⚠️ Estas 2 acciones requieren leer el estado actual primero; el workflow actual tiene ese paso incompleto. Hasta arreglarlo, usa `cama X cambiar plantas por [lista completa]` como alternativa.

## 4. Sensores

| Mensaje | Acción |
|---|---|
| `cama 5 sensor ch3` | UPDATE cama5 SET sensor_asignado = 'soil_ch3' |
| `asignar sensor 1 a cama 8` | UPDATE cama8 SET sensor_asignado = 'soil_ch1' |
| `cama 5 sin sensor` | UPDATE cama5 SET sensor_asignado = NULL |
| `quitar sensor de cama 2` | UPDATE cama2 SET sensor_asignado = NULL |

## 5. Bitácora — Cosecha

| Mensaje | Entrada en huerta_bitacora |
|---|---|
| `cosecha cama 3 lechuga 2 kg` | tipo:cosecha, cama:cama3, planta:lechuga_crespa, cantidad:2, unidad:kg |
| `coseché 500 g de cebollín en la cama 1` | tipo:cosecha, cama:cama1, planta:cebollin, cantidad:500, unidad:g |
| `cosecha de acelga en cama 4, 1.5 kg` | tipo:cosecha, cama:cama4, planta:acelga_comun, cantidad:1.5, unidad:kg |
| `recogí 20 tomates cherry del invernadero` | tipo:cosecha, cama:invernadero, planta:tomate_cherry, cantidad:20, unidad:unidades |

## 6. Bitácora — Siembra / trasplante

| Mensaje | Entrada |
|---|---|
| `sembré albahaca en la cama 9` | tipo:siembra, cama:cama9, planta:albahaca |
| `trasplanté rúcula de la cama 2 a la 11` | tipo:trasplante (nota con origen→destino) |

## 7. Bitácora — Riego

| Mensaje | Entrada |
|---|---|
| `regué la cama 5` | tipo:riego_manual, cama:cama5 |
| `riego manual cama 3 y 4` | Puede devolver 2 entradas o una combinada |

## 8. Bitácora — Plagas / observaciones

| Mensaje | Entrada |
|---|---|
| `plaga cama 4 pulgones` | tipo:plagas, nota:"pulgones" |
| `hay babosas en la cama 3` | tipo:plagas, nota:"babosas" |
| `la cama 6 se ve amarilla` | tipo:observacion, nota:"se ve amarilla" |
| `nota cama 1 floración abundante` | tipo:observacion, nota:"floración abundante" |

## 9. Fertilización

| Mensaje | Entrada |
|---|---|
| `fertilicé la cama 1 con compost` | tipo:fertilizacion, nota:"compost" |
| `aplicación de humus en invernadero` | tipo:fertilizacion, cama:invernadero, nota:"humus" |

## 10. Mensajes ambiguos (deberían responder con aclaración)

| Mensaje | Respuesta esperada |
|---|---|
| `hola` | ❌ error: "No entendí. Probá: 'cama 1 cambiar plantas por...'" |
| `cosecha` | ❌ error: "Falta la cama y la planta. Probá: 'cosecha cama 3 lechuga 2 kg'" |
| `cama 13` | ❌ error: "Solo hay camas 1-12 o invernadero" |
| `cama 5 plantar marihuana` | ❌ error: "No tengo esa planta en el catálogo" |

## Cómo validar una prueba

1. Envía el mensaje al bot
2. Esperá respuesta (< 5 seg normalmente)
3. Si es acción de escritura, verificá en Supabase:
   ```sql
   SELECT * FROM huerta_camas WHERE cama_id = 'camaN';
   -- o
   SELECT * FROM huerta_bitacora ORDER BY created_at DESC LIMIT 5;
   ```
4. O abrí el dashboard y verificá que los cambios se reflejen: https://jbenavides-dotcom.github.io/huerto-dashboard/

## Reportar bugs

Si un mensaje no funciona bien:
1. Anotá el mensaje exacto
2. Anotá la respuesta del bot
3. Revisá la ejecución en n8n → **Executions** → ver logs de cada nodo
4. Si la falla es en Claude Haiku, ajustar el `system-prompt.md` con un ejemplo más del caso que falló
