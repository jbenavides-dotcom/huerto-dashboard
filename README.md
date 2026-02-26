# Huerta Inteligente LPET
## Finca La Palma y El Tucan - Zipacon, Cundinamarca

---

## Descripcion

Plan estrategico completo para una huerta inteligente autosostenible que:
- Surte al hotel con verduras frescas (cocina italiana)
- Ofrece Tours de Bienestar con hierbas medicinales
- Opera con tecnologia IoT (sensores, camaras, automatizacion)
- Funciona con 1 operario medio tiempo

---

## Quick Start - Claude Code

### ABRIR SESION
```bash
# 1. Navegar al proyecto
cd "/Users/felipesardi/Desktop/EL GREEN HUB/LP&ET/HUERTA/AI STRATEGY"

# 2. Invocar Claude Code
claude

# 3. Ejecutar protocolo de apertura
/project:start
```

### CERRAR SESION
```bash
# Dentro de Claude Code:
/project:close
```

---

## Dashboard

```bash
# Activar entorno y ejecutar
source venv/bin/activate
streamlit run dashboard/huerta_app.py

# Abrir: http://localhost:8501 o http://localhost:8502
```

---

## Estructura del Proyecto

```
AI STRATEGY/
├── output/
│   ├── huerta_datos.json           # Datos estructurados (FUENTE DE VERDAD)
│   ├── PLAN_HUERTA_INTELIGENTE.md  # Plan estrategico completo
│   ├── CRONOGRAMA_IMPLEMENTACION.md # Cronograma 7 fases
│   └── resumen_extraccion.md       # Resumen de datos extraidos
│
├── dashboard/
│   └── huerta_app.py               # Dashboard Streamlit interactivo
│
├── .claude/                        # Configuracion Claude Code
│   ├── SESSION_LOG.md              # Historial de sesiones
│   ├── PROGRESO.md                 # Estado del trabajo
│   ├── commands/                   # Comandos personalizados
│   └── agents/                     # Subagentes
│
├── CLAUDE.md                       # Reglas del proyecto
├── README.md                       # Este archivo
└── requirements.txt                # Dependencias Python
```

---

## Datos Clave

| Aspecto | Valor |
|---------|-------|
| **Area total** | 398 m2 |
| **Area cultivo** | 118 m2 |
| **Inversion** | USD 4,250 |
| **Beneficio neto** | COP 2,390,000/mes |
| **Payback** | 7-9 meses |
| **Duracion implementacion** | 9 semanas |

---

## Dashboard

El dashboard incluye 7 paginas interactivas:

1. **Vista General** - KPIs y estado de zonas
2. **Mapa Interactivo** - Plano visual de la huerta
3. **Zonas de Cultivo** - Detalle de las 6 camas
4. **Produccion** - Estimados y ciclos
5. **Animales** - Gallinas, conejos, azolla
6. **Finanzas** - ROI y proyecciones
7. **Cronograma** - Gantt de implementacion

---

## Tecnologias

- **Python 3.x** - Lenguaje principal
- **Streamlit** - Framework de dashboard
- **Plotly** - Visualizaciones interactivas
- **Pandas** - Manejo de datos
- **JSON** - Formato de datos

---

## Instalacion

```bash
# Crear entorno virtual (ya existe)
python3 -m venv venv

# Activar
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## Comandos Utiles

```bash
# Validar JSON
python3 -c "import json; json.load(open('output/huerta_datos.json')); print('OK')"

# Ver estructura de archivos
ls -la output/ dashboard/

# Estado del dashboard
lsof -i :8501 -i :8502
```

---

## Documentacion

- [Plan Estrategico](output/PLAN_HUERTA_INTELIGENTE.md)
- [Cronograma](output/CRONOGRAMA_IMPLEMENTACION.md)
- [Resumen de Datos](output/resumen_extraccion.md)
- [Reglas del Proyecto](CLAUDE.md)

---

## Licencia

Proyecto privado - Finca La Palma y El Tucan

---

*Generado con Claude Code - 2025*
