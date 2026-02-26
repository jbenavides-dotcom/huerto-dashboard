# CLAUDE.md - Huerta Inteligente LPET
## Finca La Palma y El Tucan - Zipacon, Cundinamarca

---

## CONTEXTO DEL PROYECTO

Este proyecto planifica e implementa una **huerta inteligente autosostenible** que:
- Surte al hotel con verduras frescas (cocina italiana)
- Ofrece Tours de Bienestar con hierbas medicinales
- Opera con tecnologia IoT (sensores, camaras, automatizacion)
- Funciona con 1 operario medio tiempo guiado por iPad

### Datos Clave
| Aspecto | Valor |
|---------|-------|
| Area total | 398 m2 |
| Area cultivo | 118 m2 (6 camas + invernadero) |
| Inversion | USD 4,250 |
| Beneficio neto | COP 2,390,000/mes |
| Payback | 7-9 meses |

---

## ESTRUCTURA DEL PROYECTO

```
AI STRATEGY/
├── CLAUDE.md                    # Este archivo - reglas del proyecto
├── README.md                    # Documentacion general
├── requirements.txt             # Dependencias Python
│
├── .claude/
│   ├── settings.json            # Configuracion Claude Code
│   ├── SESSION_LOG.md           # Historial de sesiones
│   ├── PROGRESO.md              # Estado del trabajo
│   ├── agents/                  # Subagentes especializados
│   ├── commands/                # Comandos personalizados
│   ├── hooks/                   # Hooks de automatizacion
│   └── skills/                  # Skills instaladas
│
├── output/
│   ├── huerta_datos.json        # Datos estructurados (FUENTE DE VERDAD)
│   ├── PLAN_HUERTA_INTELIGENTE.md
│   ├── CRONOGRAMA_IMPLEMENTACION.md
│   └── resumen_extraccion.md
│
├── dashboard/
│   └── huerta_app.py            # Dashboard Streamlit
│
├── datos/                       # Datos de entrada
├── scripts/                     # Scripts de procesamiento
│
└── [Archivos fuente originales]
    ├── MEDIDAS HUERTA Y COMPOSTARA.docx
    ├── Medidas tomadas en campo-notas.pdf
    └── Research Huerta.rtfd/
```

---

## REGLAS OBLIGATORIAS

### Datos y Calculos
1. **NUNCA calcular mentalmente** - Siempre usar codigo Python
2. **NUNCA hardcodear datos** - Leer de `output/huerta_datos.json`
3. **NUNCA modificar archivos originales** - Solo crear en output/
4. **SIEMPRE generar JSON intermedio** - Trazabilidad

### Dashboard
5. **Dashboard lee SOLO de JSON** - Nunca de archivos fuente
6. **Ejecutar con venv** - `source venv/bin/activate`
7. **Puerto por defecto** - http://localhost:8501 o 8502

### Documentacion
8. **Actualizar PROGRESO.md** - Al completar tareas
9. **Actualizar SESSION_LOG.md** - Al cerrar sesion
10. **Commits descriptivos** - feat/fix/docs: descripcion

---

## STACK TECNOLOGICO

| Componente | Tecnologia |
|------------|------------|
| Lenguaje | Python 3.x |
| Dashboard | Streamlit |
| Graficos | Plotly |
| Datos | Pandas, JSON |
| Entorno | venv (en carpeta venv/) |

### Comandos Frecuentes

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar dashboard
streamlit run dashboard/huerta_app.py

# Validar JSON
python3 -c "import json; json.load(open('output/huerta_datos.json'))"
```

---

## ARQUITECTURA DE DATOS

### Flujo de Datos
```
Archivos Fuente (.docx, .pdf, .rtf)
        ↓
    Extraccion
        ↓
output/huerta_datos.json (FUENTE DE VERDAD)
        ↓
    Dashboard Streamlit
        ↓
    Visualizaciones
```

### Estructura del JSON Principal
```json
{
  "metadata": {},
  "dimensiones": {
    "camas_huerta": [],
    "invernadero": {},
    "espacio_libre": {},
    "compostaje": {}
  },
  "animales": {},
  "agua": {},
  "tecnologia": {},
  "produccion": {},
  "finanzas": {},
  "cronograma": {},
  "operacion": {},
  "kpis": {}
}
```

---

## CONVENCIONES

### Nombres de Archivos
- Documentos: `NOMBRE_EN_MAYUSCULAS.md`
- Datos: `nombre_en_minusculas.json`
- Scripts: `nombre_descriptivo.py`

### Commits
```
feat: Nueva funcionalidad
fix: Correccion de bug
docs: Documentacion
refactor: Reestructuracion
data: Actualizacion de datos
```

### Idioma
- Codigo: Ingles (variables, funciones)
- Documentacion: Espanol
- Comentarios: Espanol

---

## ZONAS DEL PROYECTO

| Zona | Area | Uso |
|------|------|-----|
| Camas 1-6 | 84.81 m2 | Huerta principal |
| Invernadero | 33.54 m2 | Tomate, albahaca, curcuma |
| Tour Bienestar | 160 m2 | Jardin medicinal |
| Animales | Variable | Gallinas, conejos, azolla |
| Compostaje | 126 m2 | Compostera + lombricompost |

---

## CONTACTOS Y RECURSOS

### Proyecto
- **Finca:** La Palma y El Tucan
- **Ubicacion:** Zipacon, Cundinamarca, Colombia
- **Altitud:** ~2,500 msnm

### Documentacion Consultada
- Manual lombricompostaje FAO
- Guia agricultura organica ICA
- Documentacion Home Assistant
- Fichas tecnicas cultivos clima frio

---

## NOTAS IMPORTANTES

1. El dashboard tiene visualizacion interactiva del plano de la huerta
2. Los sensores y camaras estan mapeados en el JSON
3. El cronograma tiene 7 fases en 9 semanas
4. El operario trabaja maximo 4 horas/dia

---

*Ultima actualizacion: 2025-01-31*
*Mantenido por: Claude Code*
