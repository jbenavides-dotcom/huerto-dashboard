# Sensores, Materiales y Especificaciones de Compra
## Huerta Inteligente LPET - Finca La Palma y El Tucan

**Ultima actualizacion:** 2026-02-04
**Fuente:** Investigacion ChatGPT + validacion tecnica

---

## 1. DISEÑO NUEVO: 12 CAMAS

### Medidas por cama
| Parametro | Valor |
|-----------|-------|
| Largo | 3.50 m |
| Ancho util | 0.70 m |
| Altura | 0.65 - 0.70 m |
| Area util/cama | ~2.45 m² |
| Area total 12 camas | ~29-30 m² |

### Invernadero (existente)
| Parametro | Valor |
|-----------|-------|
| Largo | 5.99 m |
| Ancho | 5.60 m |
| Altura | 2.60 m |
| Area | 33.54 m² |

---

## 2. SENSORES - ECOSISTEMA ECOWITT

### Decision: Ecowitt (WiFi, app iOS, historico, escalable)

### Compra Amazon (ya en carrito / confirmados)

| Item | Modelo | Cant. | Precio USD | Uso |
|------|--------|-------|------------|-----|
| Humedad suelo | Ecowitt WH51 | 8 | $22.99 c/u | 3 hojas + 2 brasicas + 2 tomate + 1 backup |
| Gateway WiFi | Ecowitt GW1100 | 1 | ~$30 | Hub central, conecta todo al iPad |
| Temp/Hum exterior | Ecowitt WN32 (WH32) | 1 | ~$15 | Microclima huerta abierta |
| Temp/Hum invernadero | Ecowitt WH31 | 1 | ~$15 | OBLIGATORIO para tomate |
| Pluviometro | Ecowitt WH40BH | 1 | ~$25 | Lluvia real, evitar riegos innecesarios |

### Distribucion de sensores WH51

| Sensor | Ubicacion | Profundidad | Cultivos |
|--------|-----------|-------------|----------|
| 1 | Cama hojas (promedio) | 7-10 cm | Lechuga, rucula |
| 2 | Cama hojas (mas sol) | 7-10 cm | Acelga, espinaca |
| 3 | Cama hierbas | 7-10 cm | Albahaca, cilantro |
| 4 | Cama brasicas (promedio) | 12-15 cm | Brocoli, coliflor |
| 5 | Cama brasicas (zona critica) | 12-15 cm | Repollo, kale |
| 6 | Invernadero tomate CENTRO | 15-20 cm | Tomate |
| 7 | Invernadero tomate BORDE | 15-20 cm | Tomate |
| 8 | Movil / diagnostico | Variable | Backup |

### Ubicacion sensores aire
- **WN32 exterior:** Bajo sombra ligera, no pegado a paredes, ~1.5 m del suelo
- **WH31 invernadero:** 1.5-1.8 m de altura, nunca pegado al plastico

---

## 3. UMBRALES DE RIEGO POR CULTIVO

### Hojas / Hierbas (lechuga, acelga, albahaca, cilantro)
| Estado | Lectura suelo | Accion |
|--------|--------------|--------|
| Optimo | 30-45% | No regar |
| Bajo | 28-30% | Evaluar clima |
| Critico | < 28% | Regar hoy |
| Riesgo | < 22% | Regar inmediato |

**Mejor hora:** 5:30-8:30 am
**Evitar:** Riego tarde (hongos)

### Brasicas (brocoli, coliflor, repollo, kale)
| Estado | Lectura suelo | Accion |
|--------|--------------|--------|
| Optimo | 25-40% | No regar |
| Bajo | 22-25% | Evaluar |
| Critico | < 22% | Regar |
| Riesgo | < 18% | Regar inmediato |

**Nota:** Prefieren ciclos mojado-secado moderado. Nunca encharcar.

### Tomate (invernadero)
| Estado | Lectura suelo | Accion |
|--------|--------------|--------|
| Optimo | 20-30% | No regar |
| Bajo | 18-20% | Evaluar |
| Critico | < 18% | Regar |
| Riesgo | < 15% | Regar inmediato |

**CRITICO:** Nunca mantener humedo constante → hongos, rajado de fruto.
Mejor riegos profundos y espaciados.

### Humedad aire invernadero
| Condicion | Accion |
|-----------|--------|
| > 80% por > 4 h | Ventilar |
| > 85% | Abrir si o si |
| Temp > 32°C | Ventilar + evaluar riego |

---

## 4. ALERTAS RECOMENDADAS (iPad)

1. **"Cama hojas < 28% por 24h"** → Regar
2. **"Tomate suelo < 18%"** → Regar urgente
3. **"Invernadero humedad aire > 85% por 6h"** → Ventilar
4. **"Lluvia > X mm hoy"** → No regar manana
5. **"Temp > 33°C y humedad baja"** → Riego corto/sombra

---

## 5. MALLAS Y COBERTURAS

### 5.1 Malla Anti-Insectos (PRIORIDAD #1)

| Especificacion | Valor |
|----------------|-------|
| Tipo | Malla anti-insectos agricola |
| Mesh | 50 mesh |
| Color | Blanco |
| Material | PE estabilizado UV |
| Ancho | 2.20 m |
| Cantidad camas | 55 m lineales |
| Cantidad invernadero | 25 m lineales |

**Bloquea:** pulgon, mosca blanca, trips, mariposa de brasicas

**Sellado inferior OBLIGATORIO:**
- Enterrar malla 10-15 cm en tierra
- O usar faja de mulch negro/geotextil (30 cm ancho)
- Perimetro por cama ≈ 8.4 m → Total ≈ 100 m lineales

### 5.2 Malla Sombra (solo camas de hojas)

| Especificacion | Valor |
|----------------|-------|
| Porcentaje | 30-35% |
| Color | Negra |
| Ancho | 2.0-2.5 m |
| Cantidad | 25 m lineales |

**Solo para:** lechuga, acelga, hierbas, rucula
**NO para:** brasicas establecidas, tomate

### 5.3 Cubierta Invernadero

| Especificacion | Valor |
|----------------|-------|
| Tipo | Plastico agricola translucido UV |
| Transmision | >= 85% |
| Calibre | Agricola (no ferretero) |
| Cantidad | 45 m² |

---

## 6. ESTRUCTURA PVC (camas tipo tunel abrible)

### Diseño
- Arcos de PVC 3/4" sobre cada cama (tipo tunel)
- 3 arcos por cama
- Un lado fijo, otro con bisagra para abrir/cerrar
- Malla baja hasta el suelo, sellada

### Materiales
| Item | Cantidad | Nota |
|------|----------|------|
| Tubo PVC 3/4" | 80 m | Flexible para arcos |
| Bisagras plasticas/metalicas | 36 | 3 por cama |
| Amarras plasticas UV | 1 bolsa grande | |
| Grapas tipo U galvanizadas | 1 bolsa | |

---

## 7. GEOTEXTIL (interior de camas)

| Especificacion | Valor |
|----------------|-------|
| Tipo | Geotextil agricola/paisajismo |
| Permeable | Si (debe dejar pasar agua) |
| Gramaje | Medio |
| Color | Negro o gris |
| Cantidad | 45-50 m² |

**Funcion:**
- Cubrir madera por dentro
- Evitar contacto tierra-madera
- Aumentar vida util de la cama
- Permitir drenaje

**Instalacion:** Forrar interior, grapar a madera, no tensar demasiado, fondo libre para drenaje.

---

## 8. CAPAS DE RELLENO (orden de abajo hacia arriba)

1. **Compostaje / materia organica** (base)
2. **Tierra negra / tierra agricola** (medio)
3. **Biochar** (mezclado con tierra, NO en capa sola)

---

## 9. DONDE COMPRAR EN BOGOTA

### Sensores/Tecnologia
- **Amazon** (pedido online)
- Ecowitt: sensores, gateway, pluviometro

### Mallas y Coberturas (COMPRA LOCAL)
- Agrotiendas en Suba, Fontibon, Mosquera, Cota
- Casas de plasticos agricolas (NO ferreterias comunes)
- Proveedores de insumos para floricultura

**Frase clave al comprar:**
> "Lo necesito agricola, estabilizado UV, para uso permanente en huerta, no domestico."

### Estructura y Herramientas
- Ferreterias grandes
- Homecenter
- Proveedores agricolas locales

---

## 10. QUE NO COMPRAR (errores comunes)

- Malla sombra > 70% (mata crecimiento)
- Malla verde barata (se degrada rapido)
- Anti-insectos < 40 mesh (no sirve contra plagas reales)
- Plastico transparente tipo ferreteria (quema plantas, dura poco)
- Sensores "3 en 1" baratos con cable
- Medidores de pH baratos (datos malos)

---

## 11. CULTIVOS DE ALTO VALOR ADICIONALES (RECOMENDADOS)

| Cultivo | Mercado | Potencial |
|---------|---------|-----------|
| Microverdes (microgreens) | Restaurantes, hoteles | Muy alto |
| Fresas gourmet | Mercados gourmet, cajas regalo | Muy alto |
| Pimientos premium | Restaurantes | Alto |
| Aromaticas organicas | Tiendas, productos secos | Alto |
| Tomate cherry/heirloom | Restaurantes, venta directa | Muy alto |
| Hortalizas exoticas (pak choi, tatsoi) | Restaurantes gourmet | Alto |

### Coberturas por cultivo
| Cultivo | Malla sombra | Anti-insectos | Invernadero |
|---------|-------------|---------------|-------------|
| Microverdes | 30-40% | Si | Opcional |
| Fresas | 20-30% | Si | Opcional |
| Pimientos | No | Si | Si (recomendado) |
| Aromaticas | 20-30% germinacion | Opcional | No |
| Tomate cherry | No | Si (80 mesh para Tuta) | Si |

---

## 12. PROTOCOLO DE RIEGO PARA PERSONAL (1 pagina)

### Regla de oro
> **El sensor avisa. El encargado decide y riega. Nunca riego automatico.**

### Rutina diaria (10 minutos)
1. Abrir iPad → App Ecowitt
2. Mirar sensores de suelo (exteriores + tomate)
3. Verificar clima y lluvia
4. Decidir riego segun umbrales
5. Despues de regar: confirmar que sensor sube

### Errores a evitar
- Mover sensores todos los dias
- Regar solo por costumbre
- Poner sensores pegados al gotero
- Usar mismo criterio para tomate y lechuga

---

*Documento compilado de investigacion ChatGPT + especificaciones tecnicas*
*Proyecto Huerta Inteligente LPET - 2026*
