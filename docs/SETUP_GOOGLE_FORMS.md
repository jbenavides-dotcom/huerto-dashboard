# Configuracion Google Forms + Sheets
## Sistema de Registro para Operarios - Huerta LPET

---

## PASO 1: Crear Google Sheet (Base de Datos)

### 1.1 Crear nuevo Sheet
1. Ir a [Google Sheets](https://sheets.google.com)
2. Crear nuevo documento: **"Huerta LPET - Registro Operaciones"**

### 1.2 Crear pestanas (hojas)

Crear 4 pestanas:

| Pestana | Proposito |
|---------|-----------|
| `Cosecha` | Registro diario de kg cosechados |
| `Huevos` | Registro diario de huevos |
| `Riego` | Registro de riego por zona |
| `Tareas` | Checklist de tareas completadas |

### 1.3 Estructura de cada pestana

**Pestana: Cosecha**
| Columna | Tipo | Descripcion |
|---------|------|-------------|
| A: Timestamp | Fecha/hora | Automatico |
| B: Fecha | Fecha | Dia de cosecha |
| C: Cultivo | Texto | Nombre del cultivo |
| D: Cama | Numero | Numero de cama (1-6) |
| E: Cantidad_kg | Numero | Kilos cosechados |
| F: Calidad | Opcion | Buena/Regular/Mala |
| G: Notas | Texto | Observaciones |

**Pestana: Huevos**
| Columna | Tipo |
|---------|------|
| A: Timestamp | Fecha/hora |
| B: Fecha | Fecha |
| C: Cantidad | Numero |
| D: Rotos | Numero |
| E: Notas | Texto |

**Pestana: Riego**
| Columna | Tipo |
|---------|------|
| A: Timestamp | Fecha/hora |
| B: Fecha | Fecha |
| C: Zona | Opcion (Huerta/Invernadero/Todas) |
| D: Duracion_min | Numero |
| E: Metodo | Opcion (Goteo/Manual/Automatico) |

**Pestana: Tareas**
| Columna | Tipo |
|---------|------|
| A: Timestamp | Fecha/hora |
| B: Fecha | Fecha |
| C: Tarea | Texto |
| D: Completada | Si/No |
| E: Tiempo_min | Numero |
| F: Notas | Texto |

---

## PASO 2: Crear Google Forms

### 2.1 Form: Registro de Cosecha

1. Ir a [Google Forms](https://forms.google.com)
2. Crear: **"Registro Cosecha - Huerta LPET"**

**Campos del formulario:**

```
Titulo: Registro de Cosecha

Pregunta 1: Fecha
- Tipo: Fecha
- Requerido: Si

Pregunta 2: Cultivo
- Tipo: Lista desplegable
- Opciones:
  - Lechuga
  - Rucula
  - Espinaca
  - Acelga
  - Brocoli
  - Coliflor
  - Kale
  - Zanahoria
  - Remolacha
  - Rabano
  - Tomate
  - Albahaca
  - Perejil
  - Cilantro
  - Cebolla
  - Ajo
  - Otro
- Requerido: Si

Pregunta 3: Cama
- Tipo: Lista desplegable
- Opciones: 1, 2, 3, 4, 5, 6, Invernadero
- Requerido: Si

Pregunta 4: Cantidad (kg)
- Tipo: Respuesta corta (numero)
- Validacion: Numero mayor a 0
- Requerido: Si

Pregunta 5: Calidad
- Tipo: Opcion multiple
- Opciones: Excelente, Buena, Regular, Mala
- Requerido: Si

Pregunta 6: Notas
- Tipo: Parrafo
- Requerido: No
```

### 2.2 Form: Registro de Huevos

```
Titulo: Registro de Huevos

Pregunta 1: Fecha
- Tipo: Fecha
- Requerido: Si

Pregunta 2: Huevos recolectados
- Tipo: Respuesta corta (numero)
- Requerido: Si

Pregunta 3: Huevos rotos
- Tipo: Respuesta corta (numero)
- Default: 0

Pregunta 4: Observaciones
- Tipo: Parrafo
- Requerido: No
```

### 2.3 Form: Registro de Riego

```
Titulo: Registro de Riego

Pregunta 1: Fecha
- Tipo: Fecha

Pregunta 2: Zona regada
- Tipo: Casillas de verificacion
- Opciones:
  - Cama 1 (Ensaladas)
  - Cama 2 (Hojas)
  - Cama 3 (Base italiana)
  - Cama 4 (Cruciferas)
  - Cama 5 (Raices)
  - Cama 6 (Rotacion)
  - Invernadero
  - Jardin medicinal

Pregunta 3: Duracion (minutos)
- Tipo: Respuesta corta

Pregunta 4: Metodo
- Tipo: Opcion multiple
- Opciones: Goteo automatico, Manual manguera, Regadera
```

### 2.4 Form: Tareas Completadas

```
Titulo: Registro de Tareas

Pregunta 1: Fecha
- Tipo: Fecha

Pregunta 2: Tareas completadas hoy
- Tipo: Casillas de verificacion
- Opciones:
  - Riego huerta
  - Cosecha
  - Deshierbe
  - Alimentar gallinas
  - Recolectar huevos
  - Mover gallinero
  - Alimentar conejos
  - Voltear compost
  - Alimentar lombrices
  - Revision invernadero
  - Poda/mantenimiento
  - Siembra
  - Aplicar humus
  - Limpieza general

Pregunta 3: Tiempo total trabajado (minutos)
- Tipo: Respuesta corta

Pregunta 4: Problemas encontrados
- Tipo: Parrafo
- Requerido: No
```

---

## PASO 3: Conectar Forms con Sheet

Para cada formulario:

1. Abrir el Form
2. Ir a **Respuestas** (pestana)
3. Click en icono de Google Sheets (verde)
4. Seleccionar: **"Seleccionar hoja de calculo existente"**
5. Elegir: "Huerta LPET - Registro Operaciones"
6. Seleccionar la pestana correspondiente

---

## PASO 4: Crear Links para iPad

### Obtener links de los forms:
1. En cada Form, click **Enviar**
2. Click icono de **Link**
3. Marcar **"Acortar URL"**
4. Copiar link

### Links a guardar:

| Formulario | Link (ejemplo) |
|------------|----------------|
| Cosecha | https://forms.gle/XXXXX |
| Huevos | https://forms.gle/XXXXX |
| Riego | https://forms.gle/XXXXX |
| Tareas | https://forms.gle/XXXXX |

### Agregar a iPad:
1. Abrir Safari en iPad
2. Ir al link del form
3. Compartir → **"Agregar a pantalla de inicio"**
4. Nombrar: "Cosecha", "Huevos", etc.

---

## PASO 5: Compartir Sheet con Dashboard

### 5.1 Obtener ID del Sheet

El ID esta en la URL:
```
https://docs.google.com/spreadsheets/d/[ESTE_ES_EL_ID]/edit
```

### 5.2 Hacer Sheet publico (solo lectura)

1. Click **Compartir**
2. Click **"Cambiar a cualquier persona con el enlace"**
3. Permisos: **Lector**
4. Copiar enlace

### 5.3 Guardar configuracion

Crear archivo `config/google_sheets.json`:
```json
{
  "sheet_id": "TU_SHEET_ID_AQUI",
  "sheet_url": "https://docs.google.com/spreadsheets/d/TU_ID/edit",
  "tabs": {
    "cosecha": "Cosecha",
    "huevos": "Huevos",
    "riego": "Riego",
    "tareas": "Tareas"
  }
}
```

---

## PASO 6: Verificar Funcionamiento

### Test rapido:
1. Abrir form de Cosecha en iPad
2. Llenar datos de prueba
3. Verificar que aparezcan en Google Sheet
4. Verificar que el dashboard los muestre

### Datos de prueba:
```
Fecha: Hoy
Cultivo: Lechuga
Cama: 1
Cantidad: 2.5 kg
Calidad: Buena
```

---

## TIPS PARA OPERARIOS

### En el iPad:
- Los forms funcionan **offline** (se envian cuando hay internet)
- Usar el form correspondiente para cada registro
- Llenar al menos 1 vez al dia
- Si hay problemas, anotar en "Notas"

### Mejores practicas:
- Registrar cosecha **inmediatamente** despues de cosechar
- Pesar con bascula (no estimar)
- Contar huevos exactos
- Registrar tareas al final del dia

---

*Documento de configuracion - Huerta LPET*
