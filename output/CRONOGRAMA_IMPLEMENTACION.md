# CRONOGRAMA DE IMPLEMENTACION
# HUERTA INTELIGENTE LPET
## Finca La Palma y El Tucan

---

**Duracion total:** 9 semanas
**Fecha inicio sugerida:** 10 Febrero 2025
**Fecha operacion plena:** 14 Abril 2025

---

## DIAGRAMA GANTT TEXTUAL

```
SEMANA       0         1         2         3         4         5         6         7         8         9
             |---------|---------|---------|---------|---------|---------|---------|---------|---------|
FASE 0       [===]
Base Op.     10-16 Feb

FASE 1                 [=========]
Digital                17-23 Feb

FASE 2                           [=========]
Sensores                         24 Feb-2 Mar

FASE 3                                     [=========]
Camaras                                    3-9 Mar

FASE 4                                               [=========]
Riego                                                10-16 Mar

FASE 5                                                         [===================]
Animales                                                       17-30 Mar

FASE 6                                                                             [===================]
Optimiz.                                                                           31 Mar - 13 Abr

             |---------|---------|---------|---------|---------|---------|---------|---------|---------|
                                                                                              ^
                                                                                    OPERACION PLENA
                                                                                      14 Abril
```

---

## FASE 0: BASE OPERATIVA
**Semana 0 | 10-16 Febrero 2025**

### Objetivo
Establecer orden fisico y digital antes de cualquier tecnologia.

### Tareas Detalladas

| # | Tarea | Responsable | Duracion | Entregable |
|---|-------|-------------|----------|------------|
| 0.1 | Numerar camas 1-6 con letreros | Propietario | 2 horas | Camas identificadas |
| 0.2 | Marcar zonas (Invernadero, Compost, etc.) | Propietario | 1 hora | Zonas senalizadas |
| 0.3 | Crear workspace en Notion | Propietario | 3 horas | Estructura lista |
| 0.4 | Documentar rutina semanal basica | Propietario | 2 horas | Manual operativo v1 |
| 0.5 | Publicar vacante operario | Propietario | 1 hora | Anuncio publicado |
| 0.6 | Inventariar infraestructura existente | Propietario | 2 horas | Lista de activos |

### Estructura Notion a Crear

```
HUERTA LPET (Workspace)
|
+-- Tareas Diarias (Database)
|   |-- Fecha
|   |-- Tarea
|   |-- Zona
|   |-- Tiempo estimado
|   |-- Estado
|   +-- Completado por
|
+-- Registro Cosecha (Database)
|   |-- Fecha
|   |-- Cultivo
|   |-- Cantidad (kg)
|   |-- Cama
|   +-- Notas
|
+-- Registro Huevos (Database)
|   |-- Fecha
|   |-- Cantidad
|   +-- Observaciones
|
+-- Incidencias (Database)
|   |-- Fecha
|   |-- Tipo
|   |-- Zona afectada
|   |-- Descripcion
|   +-- Accion tomada
|
+-- Calendario Siembra (Calendar view)
+-- KPIs Semanales (Dashboard)
+-- Documentacion (Pages)
```

### Costo Fase 0
| Item | Costo USD |
|------|-----------|
| Letreros/senalizacion | 50 |
| Materiales varios | 30 |
| **Total** | **80** |

### Criterio de Exito
- Todas las camas numeradas y visibles
- Notion operativo con estructura completa
- Rutina documentada y lista para ejecutar

---

## FASE 1: SISTEMA DIGITAL
**Semana 1 | 17-23 Febrero 2025**

### Objetivo
Habilitar la interfaz digital principal (iPad) y entrenar al operario.

### Tareas Detalladas

| # | Tarea | Responsable | Duracion | Entregable |
|---|-------|-------------|----------|------------|
| 1.1 | Adquirir iPad (nuevo o reacondicionado) | Propietario | 1 dia | iPad en mano |
| 1.2 | Instalar aplicaciones base | Tecnico | 2 horas | Apps configuradas |
| 1.3 | Configurar Notion en iPad | Tecnico | 1 hora | Acceso operario |
| 1.4 | Instalar Home Assistant app | Tecnico | 1 hora | App conectada |
| 1.5 | Configurar modo kiosco (opcional) | Tecnico | 2 horas | Acceso restringido |
| 1.6 | Contratar operario | Propietario | Variable | Contrato firmado |
| 1.7 | Entrenamiento operario - Dia 1 | Propietario | 4 horas | Operario capacitado |
| 1.8 | Semana de prueba supervisada | Propietario | 5 dias | Validacion capacidad |

### Aplicaciones a Instalar en iPad

| App | Funcion | Costo |
|-----|---------|-------|
| Notion | Tareas y registros | Gratis |
| Home Assistant | Dashboard sensores | Gratis |
| Camara (app de camaras) | Visualizacion | Gratis |
| Temporizador | Control tiempos | Gratis |

### Protocolo de Entrenamiento (4 horas)

**Hora 1: Introduccion**
- Filosofia del sistema
- "Aqui no se improvisa"
- Todo pasa por el iPad

**Hora 2: iPad + Dashboard**
- Como leer colores (verde/amarillo/rojo)
- Como marcar tareas completadas
- Que hacer ante alertas

**Hora 3: Recorrido Fisico**
- Identificar camas numeradas
- Ubicar sensores (cuando se instalen)
- Conocer zonas de animales y compost

**Hora 4: Ejecucion Practica**
- Simular dia de trabajo
- Marcar tareas de prueba
- Registrar datos ficticios

### Costo Fase 1
| Item | Costo USD |
|------|-----------|
| iPad (reacondicionado) | 350 |
| Funda + soporte | 50 |
| Configuracion tecnica | 50 |
| **Total** | **450** |

### Criterio de Exito
- iPad funcional con todas las apps
- Operario contratado y entrenado
- Primera semana de operacion sin tecnologia de campo

---

## FASE 2: SENSORES CRITICOS
**Semana 2 | 24 Febrero - 2 Marzo 2025**

### Objetivo
Instalar sensores minimos para toma de decisiones automatizada.

### Tareas Detalladas

| # | Tarea | Responsable | Duracion | Entregable |
|---|-------|-------------|----------|------------|
| 2.1 | Recibir sensores (compra previa) | Propietario | - | Equipos en sitio |
| 2.2 | Instalar sensor huerta zona 1-2 | Tecnico IoT | 1 hora | Sensor activo |
| 2.3 | Instalar sensor huerta zona 3-4 | Tecnico IoT | 1 hora | Sensor activo |
| 2.4 | Instalar sensor huerta zona 5-6 | Tecnico IoT | 1 hora | Sensor activo |
| 2.5 | Instalar sensor invernadero (temp+hum) | Tecnico IoT | 1 hora | Sensor activo |
| 2.6 | Instalar sensor invernadero (luz) | Tecnico IoT | 30 min | Sensor activo |
| 2.7 | Instalar sensor compost | Tecnico IoT | 1 hora | Sensor activo |
| 2.8 | Configurar gateway WiFi | Tecnico IoT | 2 horas | Red operativa |
| 2.9 | Integrar a Home Assistant | Tecnico IoT | 3 horas | Dashboard con datos |
| 2.10 | Configurar alertas basicas | Tecnico IoT | 2 horas | Alertas funcionando |
| 2.11 | Pruebas de funcionamiento | Tecnico IoT | 2 horas | Sistema validado |

### Mapa de Ubicacion de Sensores

```
HUERTA PRINCIPAL
+------------------------------------------------------------------+
|  [S1]                    [S2]                    [S3]             |
|  Sensor 1                Sensor 2                Sensor 3         |
|  Camas 1-2               Camas 3-4               Camas 5-6        |
|  Humedad+Temp            Humedad+Temp            Humedad+Temp     |
+------------------------------------------------------------------+

INVERNADERO
+---------------------------+
|  [S4]          [S5]       |
|  Temp+Humedad  Luz        |
+---------------------------+

COMPOST
+---------------------------+
|  [S6]                     |
|  Temp+Humedad             |
+---------------------------+
```

### Umbrales de Alerta Iniciales

| Sensor | Parametro | Alerta Amarilla | Alerta Roja |
|--------|-----------|-----------------|-------------|
| Huerta | Humedad | < 35% | < 25% |
| Huerta | Temp suelo | < 10C o > 30C | < 5C o > 35C |
| Invernadero | Humedad | < 40% | < 30% |
| Invernadero | Temperatura | > 26C | > 30C |
| Compost | Temperatura | > 55C | > 65C |

### Costo Fase 2
| Item | Cantidad | Costo Unit. | Total USD |
|------|----------|-------------|-----------|
| Sensor humedad+temp suelo | 3 | 30 | 90 |
| Sensor temp+humedad aire | 1 | 25 | 25 |
| Sensor luminosidad | 1 | 20 | 20 |
| Sensor temp compost | 1 | 25 | 25 |
| Gateway/Router outdoor | 1 | 120 | 120 |
| Repetidor mesh | 1 | 80 | 80 |
| Instalacion tecnica | 1 | 100 | 100 |
| **Total** | | | **460** |

### Criterio de Exito
- 6 sensores reportando datos en tiempo real
- Dashboard mostrando estado de todas las zonas
- Alertas funcionando correctamente (probar con simulacion)

---

## FASE 3: CAMARAS
**Semana 3 | 3-9 Marzo 2025**

### Objetivo
Implementar vigilancia visual para supervision remota y auditoria.

### Tareas Detalladas

| # | Tarea | Responsable | Duracion | Entregable |
|---|-------|-------------|----------|------------|
| 3.1 | Recibir camaras (compra previa) | Propietario | - | Equipos en sitio |
| 3.2 | Instalar camara huerta (poste central) | Tecnico | 2 horas | Camara activa |
| 3.3 | Instalar camara invernadero | Tecnico | 1 hora | Camara activa |
| 3.4 | Instalar camara gallinas/estanques | Tecnico | 2 horas | Camara activa |
| 3.5 | Configurar grabacion local/nube | Tecnico | 2 horas | Almacenamiento OK |
| 3.6 | Habilitar acceso remoto | Tecnico | 1 hora | App movil funcional |
| 3.7 | Integrar a iPad operario | Tecnico | 1 hora | Camaras en dashboard |
| 3.8 | Pruebas vision nocturna | Tecnico | 1 hora | Validacion nocturna |

### Especificaciones de Camaras

| Ubicacion | Tipo | Caracteristicas | Modelo Sugerido |
|-----------|------|-----------------|-----------------|
| Huerta general | Exterior | Gran angular, IP65, 1080p | TP-Link Tapo C310 |
| Invernadero | Interior | Temp/hum display, 1080p | Xiaomi Mi Home |
| Gallinas | Exterior | Vision nocturna, IP65 | Reolink RLC-510A |

### Costo Fase 3
| Item | Cantidad | Costo Unit. | Total USD |
|------|----------|-------------|-----------|
| Camara exterior WiFi | 2 | 60 | 120 |
| Camara interior | 1 | 40 | 40 |
| Tarjetas microSD 64GB | 3 | 15 | 45 |
| Cables/accesorios | 1 | 30 | 30 |
| Instalacion | 1 | 50 | 50 |
| **Total** | | | **285** |

### Criterio de Exito
- 3 camaras funcionando 24/7
- Acceso remoto desde cualquier lugar
- Grabacion continua con al menos 7 dias de historial

---

## FASE 4: RIEGO INTELIGENTE
**Semana 4 | 10-16 Marzo 2025**

### Objetivo
Automatizar parcialmente el riego basado en datos de sensores.

### Tareas Detalladas

| # | Tarea | Responsable | Duracion | Entregable |
|---|-------|-------------|----------|------------|
| 4.1 | Evaluar sistema de riego existente | Plomero | 2 horas | Diagnostico |
| 4.2 | Instalar valvula WiFi zona huerta | Plomero+Tec | 3 horas | Valvula operativa |
| 4.3 | Instalar valvula WiFi invernadero | Plomero+Tec | 2 horas | Valvula operativa |
| 4.4 | Conectar valvulas a Home Assistant | Tecnico | 2 horas | Control remoto OK |
| 4.5 | Crear automatizaciones humedad->riego | Tecnico | 3 horas | Logica programada |
| 4.6 | Pruebas de flujo y presion | Plomero | 2 horas | Sistema validado |
| 4.7 | Documentar procedimiento manual backup | Tecnico | 1 hora | Manual escrito |
| 4.8 | Entrenar operario en sistema | Tecnico | 1 hora | Operario capacitado |

### Logica de Automatizacion

```
AUTOMATIZACION: Riego Huerta
---------------------------------
TRIGGER:
  - Humedad zona 1-2 < 30%
  - O Humedad zona 3-4 < 30%
  - O Humedad zona 5-6 < 30%

CONDICION:
  - No ha llovido en ultimas 24h
  - Hora entre 6am y 9am O 5pm y 7pm

ACCION:
  - Crear alerta en iPad: "Riego necesario - Huerta"
  - Operario verifica y activa valvula
  - Duracion sugerida: 20 minutos
  - Marcar tarea completada

AUTOMATIZACION: Riego Invernadero
---------------------------------
TRIGGER:
  - Humedad invernadero < 35%
  - Y Temperatura > 22C

ACCION:
  - Alerta ALTA prioridad
  - Riego sugerido inmediato
  - Duracion: 15 minutos
```

### Costo Fase 4
| Item | Cantidad | Costo Unit. | Total USD |
|------|----------|-------------|-----------|
| Valvula solenoide WiFi 1" | 2 | 40 | 80 |
| Controlador central | 1 | 50 | 50 |
| Accesorios plomeria | 1 | 50 | 50 |
| Mano de obra plomero | 1 | 80 | 80 |
| Configuracion tecnica | 1 | 50 | 50 |
| **Total** | | | **310** |

### Criterio de Exito
- Riego activable desde iPad o app
- Alertas automaticas por humedad baja
- Sistema manual de backup documentado

---

## FASE 5: ANIMALES
**Semanas 5-6 | 17-30 Marzo 2025**

### Objetivo
Integrar gallinas y conejos al sistema productivo.

### Tareas Detalladas - Semana 5

| # | Tarea | Responsable | Duracion | Entregable |
|---|-------|-------------|----------|------------|
| 5.1 | Disenar gallinero movil | Constructor | 1 dia | Planos aprobados |
| 5.2 | Construir estructura gallinero | Constructor | 3 dias | Gallinero listo |
| 5.3 | Instalar malla y techo | Constructor | 1 dia | Gallinero cerrado |
| 5.4 | Construir nidales (5-6) | Constructor | 1 dia | Nidales listos |
| 5.5 | Disenar conejeras moviles | Constructor | 1 dia | Planos aprobados |
| 5.6 | Construir 3 conejeras | Constructor | 2 dias | Conejeras listas |

### Tareas Detalladas - Semana 6

| # | Tarea | Responsable | Duracion | Entregable |
|---|-------|-------------|----------|------------|
| 5.7 | Adquirir gallinas (25) | Propietario | 1 dia | Gallinas en sitio |
| 5.8 | Adquirir conejos (12) | Propietario | 1 dia | Conejos en sitio |
| 5.9 | Revision veterinaria inicial | Veterinario | 2 horas | Certificado salud |
| 5.10 | Instalar sensor temp gallinero | Tecnico | 1 hora | Sensor activo |
| 5.11 | Instalar sensor nivel agua | Tecnico | 1 hora | Sensor activo |
| 5.12 | Instalar sensor temp estanque | Tecnico | 1 hora | Sensor activo |
| 5.13 | Definir rutina de manejo | Propietario | 2 horas | Protocolo escrito |
| 5.14 | Entrenar operario en animales | Veterinario | 3 horas | Operario capacitado |

### Especificaciones Gallinero Movil

```
GALLINERO MOVIL - ESPECIFICACIONES
==================================

Dimensiones: 2.5m x 1.5m x 1.2m (alto)
Capacidad: 25-30 gallinas
Materiales:
  - Estructura: Madera tratada o guadua
  - Piso: Malla gallinera (sin piso solido)
  - Techo: Lamina o plastico
  - Ruedas: 4 ruedas tipo carretilla

Componentes:
  - Nidales: 6 unidades (1 por cada 4-5 gallinas)
  - Perchas: 5m lineales totales
  - Bebedero: Automatico tipo niple o campana
  - Comedero: Tolva 20kg

Sistema de rotacion:
  - Mover cada 3-5 dias
  - Circuito de 8-10 posiciones
  - Descanso por posicion: 30-40 dias
```

### Costo Fase 5
| Item | Cantidad | Costo Unit. | Total USD |
|------|----------|-------------|-----------|
| **Construccion** |
| Gallinero movil (materiales) | 1 | 250 | 250 |
| Mano de obra gallinero | 1 | 150 | 150 |
| Conejeras (3 unidades) | 3 | 80 | 240 |
| **Animales** |
| Gallinas ponedoras | 25 | 12 | 300 |
| Conejos reproductores | 12 | 20 | 240 |
| **Equipamiento** |
| Bebederos/comederos | 1 | 80 | 80 |
| Alimento inicial (1 mes) | 1 | 100 | 100 |
| **Sensores** |
| Sensor temp gallinero | 1 | 25 | 25 |
| Sensor nivel agua | 1 | 20 | 20 |
| Sensor temp estanque | 1 | 15 | 15 |
| **Otros** |
| Revision veterinaria | 1 | 50 | 50 |
| **Total** | | | **1,470** |

### Criterio de Exito
- 25 gallinas instaladas y produciendo
- 12 conejos en conejeras funcionales
- Sistema de rotacion establecido
- Sensores de animales integrados al dashboard

---

## FASE 6: OPTIMIZACION
**Semanas 7-8 | 31 Marzo - 13 Abril 2025**

### Objetivo
Afinar el sistema, disenar el tour y preparar para operacion plena.

### Tareas Detalladas - Semana 7

| # | Tarea | Responsable | Duracion | Entregable |
|---|-------|-------------|----------|------------|
| 6.1 | Analizar datos sensores (2 semanas) | Propietario | 3 horas | Reporte tendencias |
| 6.2 | Ajustar umbrales de alerta | Tecnico | 2 horas | Umbrales optimizados |
| 6.3 | Refinar automatizaciones | Tecnico | 3 horas | Logica mejorada |
| 6.4 | Disenar recorrido tour | Propietario | 4 horas | Mapa recorrido |
| 6.5 | Escribir guion tour | Propietario | 4 horas | Guion completo |
| 6.6 | Definir estaciones del tour | Propietario | 2 horas | 6-8 estaciones |
| 6.7 | Crear senalizacion tour | Disenador | 3 horas | Letreros listos |

### Tareas Detalladas - Semana 8

| # | Tarea | Responsable | Duracion | Entregable |
|---|-------|-------------|----------|------------|
| 6.8 | Instalar senalizacion | Propietario | 4 horas | Letreros instalados |
| 6.9 | Preparar area degustacion | Propietario | 3 horas | Espacio listo |
| 6.10 | Crear material marketing | Disenador | 4 horas | Fotos + textos |
| 6.11 | Configurar reservas online | Propietario | 2 horas | Sistema activo |
| 6.12 | Tour piloto (amigos/familia) | Propietario | 3 horas | Feedback |
| 6.13 | Ajustes finales | Propietario | 2 horas | Tour refinado |
| 6.14 | Lanzamiento oficial | Propietario | - | Tour activo |

### Diseno del Tour de Bienestar

```
TOUR DE BIENESTAR - ESTACIONES
==============================

Duracion total: 90 minutos
Capacidad: 8-12 personas
Precio sugerido: $60,000 COP/persona

ESTACION 1: Bienvenida (10 min)
- Introduccion a la finca
- Filosofia de agricultura regenerativa
- Vista panoramica

ESTACION 2: Huerta Principal (15 min)
- Recorrido por las 6 camas
- Explicacion de cultivos
- Actividad: Cosechar una hoja y probar

ESTACION 3: Jardin Medicinal (20 min)
- Hierbas anticancerigenas
- Propiedades de cada planta
- Actividad: Oler y tocar las hierbas

ESTACION 4: Invernadero (10 min)
- Cultivo protegido
- Tomate y albahaca
- Curcuma y jengibre

ESTACION 5: Animales (15 min)
- Gallinas en pastoreo
- Sistema de rotacion
- Actividad: Recoger un huevo (si disponible)

ESTACION 6: Compostaje (10 min)
- Ciclo cerrado de nutrientes
- Lombricompost
- "Nada se desperdicia"

ESTACION 7: Degustacion (15 min)
- Infusion de hierbas frescas
- Jugo verde (opcional)
- Productos de la huerta

CIERRE:
- Preguntas y respuestas
- Venta de productos (huevos, aromaticas)
- Foto grupal
```

### Costo Fase 6
| Item | Cantidad | Costo Unit. | Total USD |
|------|----------|-------------|-----------|
| Senalizacion profesional | 10 | 15 | 150 |
| Mobiliario area degustacion | 1 | 100 | 100 |
| Material marketing (fotos, etc) | 1 | 80 | 80 |
| Ajustes tecnicos finales | 1 | 50 | 50 |
| **Total** | | | **380** |

### Criterio de Exito
- Sistema funcionando 2+ semanas sin fallas mayores
- Tour disenado y probado
- Primer grupo de visitantes pagados
- Operario trabajando de forma autonoma

---

## RESUMEN DE COSTOS POR FASE

| Fase | Descripcion | Semana | Costo USD |
|------|-------------|--------|-----------|
| 0 | Base Operativa | 0 | 80 |
| 1 | Sistema Digital | 1 | 450 |
| 2 | Sensores Criticos | 2 | 460 |
| 3 | Camaras | 3 | 285 |
| 4 | Riego Inteligente | 4 | 310 |
| 5 | Animales | 5-6 | 1,470 |
| 6 | Optimizacion | 7-8 | 380 |
| | **TOTAL** | | **3,435** |

*Agregar 15% contingencia: USD 515*
**TOTAL CON CONTINGENCIA: USD 3,950**

---

## HITOS CLAVE

| Fecha | Hito | Indicador |
|-------|------|-----------|
| 16 Feb | Fase 0 completa | Camas numeradas, Notion listo |
| 23 Feb | iPad operativo | Operario usando dashboard |
| 2 Mar | Sensores activos | 6 sensores reportando |
| 9 Mar | Camaras funcionando | 3 feeds en vivo |
| 16 Mar | Riego automatizado | Alertas por humedad activas |
| 30 Mar | Animales integrados | 25 gallinas + 12 conejos |
| 6 Abr | Tour disenado | Guion y recorrido listos |
| **14 Abr** | **OPERACION PLENA** | **Sistema completo funcionando** |

---

## DEPENDENCIAS CRITICAS

```
FASE 0 --> FASE 1 (Base operativa antes de digital)
    |
    v
FASE 1 --> FASE 2 (iPad antes de sensores)
    |
    v
FASE 2 --> FASE 4 (Sensores antes de riego automatizado)
    |
FASE 3 (Camaras pueden ir en paralelo)
    |
    v
FASE 4 --> FASE 5 (Riego antes de animales - agua)
    |
    v
FASE 5 --> FASE 6 (Animales antes de tour)
```

---

## RIESGOS Y CONTINGENCIAS

| Riesgo | Probabilidad | Impacto | Contingencia |
|--------|--------------|---------|--------------|
| Retraso entrega equipos | Media | Medio | Ordenar con 2 semanas anticipacion |
| Operario no se adapta | Baja | Alto | Periodo prueba 2 semanas, backup identificado |
| Falla sensores | Baja | Medio | Operacion manual documentada |
| Clima adverso construccion | Media | Bajo | Flexibilidad en fechas Fase 5 |
| Animales enfermos | Baja | Medio | Veterinario de guardia, aislamiento |

---

## RESPONSABLES POR FASE

| Fase | Responsable Principal | Apoyo |
|------|----------------------|-------|
| 0 | Propietario | - |
| 1 | Propietario | Tecnico |
| 2 | Tecnico IoT | Propietario |
| 3 | Tecnico IoT | Propietario |
| 4 | Tecnico + Plomero | Propietario |
| 5 | Constructor | Veterinario, Propietario |
| 6 | Propietario | Disenador |

---

## CHECKLIST PRE-INICIO

Antes de comenzar Fase 0, verificar:

- [ ] Presupuesto total aprobado (USD 4,000)
- [ ] Cuenta bancaria/efectivo disponible
- [ ] Acceso a internet en finca confirmado
- [ ] Contacto de tecnico IoT identificado
- [ ] Contacto de plomero identificado
- [ ] Contacto de constructor identificado
- [ ] Contacto de veterinario identificado
- [ ] Proveedores de equipos identificados
- [ ] Proveedor de gallinas identificado
- [ ] Proveedor de conejos identificado

---

*Documento generado para Proyecto Huerta Inteligente LPET*
*Version 1.0 - Enero 2025*
