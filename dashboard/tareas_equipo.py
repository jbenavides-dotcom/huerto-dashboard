"""
Dashboard de Gestion de Tareas - Proyecto Circular de Produccion Agricola
Huerta Inteligente LPET - Finca La Palma y El Tucan
"""

import streamlit as st
import json
import pandas as pd
from datetime import datetime, date
from pathlib import Path

# Configuracion de la pagina
st.set_page_config(
    page_title="Tareas - Huerta LPET",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Rutas de archivos
BASE_DIR = Path(__file__).parent.parent
DATA_PATH = BASE_DIR / "data" / "tareas_proyecto.json"

# Funciones de carga y guardado
def cargar_datos():
    """Carga los datos del archivo JSON"""
    try:
        with open(DATA_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"No se encontro el archivo: {DATA_PATH}")
        return None

def guardar_datos(datos):
    """Guarda los datos al archivo JSON"""
    datos['metadata']['ultima_modificacion'] = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    # Actualizar session_state con los datos nuevos
    st.session_state['datos'] = datos

def get_estado_color(estado_id, estados):
    """Obtiene el color de un estado"""
    for e in estados:
        if e['id'] == estado_id:
            return e['color']
    return '#6c757d'

def get_estado_nombre(estado_id, estados):
    """Obtiene el nombre de un estado"""
    for e in estados:
        if e['id'] == estado_id:
            return e['nombre']
    return estado_id

def get_responsable_nombre(resp_id, equipo):
    """Obtiene el nombre de un responsable"""
    for e in equipo:
        if e['id'] == resp_id:
            return e['nombre']
    return resp_id

def get_categoria_info(cat_id, categorias):
    """Obtiene info de una categoria"""
    for c in categorias:
        if c['id'] == cat_id:
            return c
    return {'nombre': cat_id, 'icono': '📌'}

# Cargar datos usando session_state para persistencia durante edicion
if 'datos' not in st.session_state or st.session_state.get('recargar', False):
    st.session_state['datos'] = cargar_datos()
    st.session_state['recargar'] = False

datos = st.session_state['datos']

if datos is None:
    st.stop()

# CSS personalizado
st.markdown("""
<style>
    .task-card {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 5px solid;
    }
    .urgente {
        background-color: #ffebee;
        border-left-color: #dc3545;
    }
    .alta {
        background-color: #fff3e0;
        border-left-color: #ff9800;
    }
    .media {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    .baja {
        background-color: #f5f5f5;
        border-left-color: #9e9e9e;
    }
    .kpi-card {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
    }
    .stProgress > div > div > div > div {
        background-color: #28a745;
    }
    .fecha-vencida {
        color: #dc3545;
        font-weight: bold;
    }
    .fecha-hoy {
        color: #ff9800;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📋 Gestion de Tareas")
st.sidebar.markdown(f"**Proyecto:** {datos['metadata']['proyecto']}")
st.sidebar.markdown(f"**Finca:** {datos['metadata']['finca']}")
st.sidebar.markdown(f"**Actualizado:** {datos['metadata']['ultima_modificacion']}")

st.sidebar.markdown("---")

# Filtros en sidebar
st.sidebar.subheader("Filtros")

# Filtro por responsable
responsables_opciones = ["Todos"] + [e['nombre'] for e in datos['equipo']]
filtro_responsable = st.sidebar.selectbox(
    "Responsable",
    responsables_opciones,
    index=0
)

# Filtro por categoria
categorias_opciones = ["Todas"] + [f"{c['icono']} {c['nombre']}" for c in datos['categorias']]
filtro_categoria = st.sidebar.selectbox(
    "Categoria",
    categorias_opciones,
    index=0
)

# Filtro por estado
estados_opciones = ["Todos"] + [e['nombre'] for e in datos['estados']]
filtro_estado = st.sidebar.selectbox(
    "Estado",
    estados_opciones,
    index=0
)

# Filtro por prioridad
prioridades_opciones = ["Todas", "urgente", "alta", "media", "baja"]
filtro_prioridad = st.sidebar.selectbox(
    "Prioridad",
    prioridades_opciones,
    index=0
)

# Aplicar filtros
tareas_filtradas = datos['tareas'].copy()

if filtro_responsable != "Todos":
    resp_id = next((e['id'] for e in datos['equipo'] if e['nombre'] == filtro_responsable), None)
    if resp_id:
        tareas_filtradas = [t for t in tareas_filtradas if t['responsable'] == resp_id]

if filtro_categoria != "Todas":
    cat_nombre = filtro_categoria.split(' ', 1)[1] if ' ' in filtro_categoria else filtro_categoria
    cat_id = next((c['id'] for c in datos['categorias'] if c['nombre'] == cat_nombre), None)
    if cat_id:
        tareas_filtradas = [t for t in tareas_filtradas if t['categoria'] == cat_id]

if filtro_estado != "Todos":
    estado_id = next((e['id'] for e in datos['estados'] if e['nombre'] == filtro_estado), None)
    if estado_id:
        tareas_filtradas = [t for t in tareas_filtradas if t['estado'] == estado_id]

if filtro_prioridad != "Todas":
    tareas_filtradas = [t for t in tareas_filtradas if t['prioridad'] == filtro_prioridad]

# Navegacion
st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "Vista",
    ["📊 Resumen", "📝 Lista de Tareas", "🎯 Tablero Kanban", "✏️ Editar Tarea"]
)

# ============================================
# PAGINA: RESUMEN
# ============================================
if pagina == "📊 Resumen":
    st.title("📊 Resumen del Proyecto")

    # Fechas criticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📅 Inicio Obra", datos['metadata']['fecha_inicio_obra'])
    with col2:
        st.metric("🛒 Limite Compras", datos['metadata']['fecha_limite_compras'])
    with col3:
        dias_para_inicio = (datetime.strptime(datos['metadata']['fecha_inicio_obra'], "%Y-%m-%d").date() - date.today()).days
        st.metric("⏰ Dias para inicio", f"{dias_para_inicio} dias")

    st.markdown("---")

    # KPIs principales
    total_tareas = len(datos['tareas'])
    por_iniciar = len([t for t in datos['tareas'] if t['estado'] == 'por_iniciar'])
    en_proceso = len([t for t in datos['tareas'] if t['estado'] == 'en_proceso'])
    finalizadas = len([t for t in datos['tareas'] if t['estado'] == 'finalizado'])
    bloqueadas = len([t for t in datos['tareas'] if t['estado'] == 'bloqueado'])

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div class="kpi-card" style="background-color: #6c757d;">
            <h2>{total_tareas}</h2>
            <p>Total Tareas</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="kpi-card" style="background-color: #17a2b8;">
            <h2>{por_iniciar}</h2>
            <p>Por Iniciar</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card" style="background-color: #ffc107; color: black;">
            <h2>{en_proceso}</h2>
            <p>En Proceso</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card" style="background-color: #28a745;">
            <h2>{finalizadas}</h2>
            <p>Finalizadas</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown(f"""
        <div class="kpi-card" style="background-color: #dc3545;">
            <h2>{bloqueadas}</h2>
            <p>Bloqueadas</p>
        </div>
        """, unsafe_allow_html=True)

    # Progreso general
    progreso = finalizadas / total_tareas if total_tareas > 0 else 0
    st.markdown("### Progreso General")
    st.progress(progreso)
    st.markdown(f"**{finalizadas}/{total_tareas}** tareas completadas ({progreso*100:.1f}%)")

    st.markdown("---")

    # Tareas por categoria
    st.markdown("### Tareas por Categoria")
    col1, col2 = st.columns(2)

    with col1:
        for cat in datos['categorias']:
            cat_tareas = [t for t in datos['tareas'] if t['categoria'] == cat['id']]
            cat_completadas = len([t for t in cat_tareas if t['estado'] == 'finalizado'])
            cat_total = len(cat_tareas)

            st.markdown(f"**{cat['icono']} {cat['nombre']}** ({cat_completadas}/{cat_total})")
            if cat_total > 0:
                st.progress(cat_completadas / cat_total)

    with col2:
        # Tareas por responsable
        st.markdown("### Tareas por Responsable")
        for miembro in datos['equipo']:
            if miembro['id'] == 'sin_asignar':
                continue
            resp_tareas = [t for t in datos['tareas'] if t['responsable'] == miembro['id']]
            resp_pendientes = len([t for t in resp_tareas if t['estado'] not in ['finalizado']])
            if resp_pendientes > 0:
                st.markdown(f"**{miembro['nombre']}:** {resp_pendientes} pendientes")

    st.markdown("---")

    # Tareas urgentes
    st.markdown("### 🚨 Tareas Urgentes (Vencidas o Hoy)")
    hoy = date.today()

    tareas_urgentes = []
    for t in datos['tareas']:
        if t['estado'] == 'finalizado':
            continue
        fecha_obj = datetime.strptime(t['fecha_objetivo'], "%Y-%m-%d").date()
        if fecha_obj <= hoy or t['prioridad'] == 'urgente':
            tareas_urgentes.append({
                'tarea': t['tarea'],
                'fecha': t['fecha_objetivo'],
                'responsable': get_responsable_nombre(t['responsable'], datos['equipo']),
                'estado': get_estado_nombre(t['estado'], datos['estados']),
                'prioridad': t['prioridad']
            })

    if tareas_urgentes:
        df_urgentes = pd.DataFrame(tareas_urgentes)
        st.dataframe(df_urgentes, use_container_width=True)
    else:
        st.success("No hay tareas urgentes pendientes")

# ============================================
# PAGINA: LISTA DE TAREAS
# ============================================
elif pagina == "📝 Lista de Tareas":
    st.title("📝 Lista de Tareas")

    st.markdown(f"**Mostrando {len(tareas_filtradas)} tareas**")

    # Ordenar por fecha
    tareas_filtradas = sorted(tareas_filtradas, key=lambda x: x['fecha_objetivo'])

    for tarea in tareas_filtradas:
        cat_info = get_categoria_info(tarea['categoria'], datos['categorias'])
        estado_color = get_estado_color(tarea['estado'], datos['estados'])
        estado_nombre = get_estado_nombre(tarea['estado'], datos['estados'])
        resp_nombre = get_responsable_nombre(tarea['responsable'], datos['equipo'])

        # Verificar si esta vencida
        fecha_obj = datetime.strptime(tarea['fecha_objetivo'], "%Y-%m-%d").date()
        hoy = date.today()

        fecha_class = ""
        if tarea['estado'] != 'finalizado':
            if fecha_obj < hoy:
                fecha_class = "fecha-vencida"
            elif fecha_obj == hoy:
                fecha_class = "fecha-hoy"

        with st.container():
            col1, col2, col3, col4, col5 = st.columns([0.5, 3, 1.5, 1.5, 1])

            with col1:
                st.markdown(f"### {cat_info['icono']}")

            with col2:
                st.markdown(f"**{tarea['tarea']}**")
                if tarea['notas']:
                    st.caption(tarea['notas'])

            with col3:
                st.markdown(f"👤 {resp_nombre}")
                st.markdown(f"""<span class="{fecha_class}">📅 {tarea['fecha_objetivo']}</span>""", unsafe_allow_html=True)

            with col4:
                st.markdown(f"""
                <span style="background-color: {estado_color}; color: white; padding: 3px 8px; border-radius: 5px;">
                    {estado_nombre}
                </span>
                """, unsafe_allow_html=True)
                st.caption(f"Prioridad: {tarea['prioridad']}")

            with col5:
                if st.button("✏️", key=f"edit_{tarea['id']}", help="Editar tarea"):
                    st.session_state['tarea_editar'] = tarea['id']
                    st.rerun()

            st.markdown("---")

# ============================================
# PAGINA: TABLERO KANBAN
# ============================================
elif pagina == "🎯 Tablero Kanban":
    st.title("🎯 Tablero Kanban")

    # Crear columnas para cada estado principal
    estados_kanban = ['por_iniciar', 'en_proceso', 'revision', 'finalizado']
    cols = st.columns(len(estados_kanban))

    for idx, estado_id in enumerate(estados_kanban):
        estado_info = next((e for e in datos['estados'] if e['id'] == estado_id), None)
        if not estado_info:
            continue

        tareas_estado = [t for t in tareas_filtradas if t['estado'] == estado_id]

        with cols[idx]:
            st.markdown(f"""
            <div style="background-color: {estado_info['color']}; color: white; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 10px;">
                <h3>{estado_info['nombre']}</h3>
                <p>{len(tareas_estado)} tareas</p>
            </div>
            """, unsafe_allow_html=True)

            for tarea in tareas_estado:
                cat_info = get_categoria_info(tarea['categoria'], datos['categorias'])
                resp_nombre = get_responsable_nombre(tarea['responsable'], datos['equipo'])

                prioridad_class = tarea['prioridad']

                st.markdown(f"""
                <div class="task-card {prioridad_class}">
                    <strong>{cat_info['icono']} {tarea['tarea'][:40]}{'...' if len(tarea['tarea']) > 40 else ''}</strong><br>
                    <small>👤 {resp_nombre}</small><br>
                    <small>📅 {tarea['fecha_objetivo']}</small>
                </div>
                """, unsafe_allow_html=True)

# ============================================
# PAGINA: EDITAR TAREA
# ============================================
elif pagina == "✏️ Editar Tarea":
    st.title("✏️ Editar Tarea")

    # Selector de tarea
    tareas_opciones = {f"{t['id']} - {t['tarea'][:50]}": t['id'] for t in datos['tareas']}

    # Si viene de otro lado con tarea seleccionada
    default_idx = 0
    if 'tarea_editar' in st.session_state:
        tarea_id = st.session_state['tarea_editar']
        for idx, (key, val) in enumerate(tareas_opciones.items()):
            if val == tarea_id:
                default_idx = idx
                break

    tarea_seleccionada = st.selectbox(
        "Seleccionar tarea",
        list(tareas_opciones.keys()),
        index=default_idx
    )

    if tarea_seleccionada:
        tarea_id = tareas_opciones[tarea_seleccionada]
        tarea = next((t for t in datos['tareas'] if t['id'] == tarea_id), None)

        if tarea:
            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Informacion de la Tarea")

                cat_info = get_categoria_info(tarea['categoria'], datos['categorias'])
                st.markdown(f"**Categoria:** {cat_info['icono']} {cat_info['nombre']}")
                st.markdown(f"**Tarea:** {tarea['tarea']}")

                if tarea['dependencias']:
                    deps = [next((t['tarea'] for t in datos['tareas'] if t['id'] == d), str(d)) for d in tarea['dependencias']]
                    st.markdown(f"**Dependencias:** {', '.join(deps[:3])}{'...' if len(deps) > 3 else ''}")

            with col2:
                st.markdown("### Editar")

                # Responsable
                resp_opciones = [e['nombre'] for e in datos['equipo']]
                resp_actual = get_responsable_nombre(tarea['responsable'], datos['equipo'])
                resp_idx = resp_opciones.index(resp_actual) if resp_actual in resp_opciones else 0

                nuevo_responsable = st.selectbox(
                    "Responsable",
                    resp_opciones,
                    index=resp_idx
                )

                # Fecha
                fecha_actual = datetime.strptime(tarea['fecha_objetivo'], "%Y-%m-%d").date()
                nueva_fecha = st.date_input(
                    "Fecha objetivo",
                    value=fecha_actual
                )

                # Estado
                estados_opciones = [e['nombre'] for e in datos['estados']]
                estado_actual = get_estado_nombre(tarea['estado'], datos['estados'])
                estado_idx = estados_opciones.index(estado_actual) if estado_actual in estados_opciones else 0

                nuevo_estado = st.selectbox(
                    "Estado",
                    estados_opciones,
                    index=estado_idx
                )

                # Prioridad
                prioridad_opciones = ['urgente', 'alta', 'media', 'baja']
                prioridad_idx = prioridad_opciones.index(tarea['prioridad']) if tarea['prioridad'] in prioridad_opciones else 2

                nueva_prioridad = st.selectbox(
                    "Prioridad",
                    prioridad_opciones,
                    index=prioridad_idx
                )

                # Notas
                nuevas_notas = st.text_area(
                    "Notas",
                    value=tarea['notas']
                )

            st.markdown("---")

            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
                    # Actualizar tarea
                    for i, t in enumerate(st.session_state['datos']['tareas']):
                        if t['id'] == tarea_id:
                            # Obtener IDs
                            nuevo_resp_id = next((e['id'] for e in datos['equipo'] if e['nombre'] == nuevo_responsable), tarea['responsable'])
                            nuevo_estado_id = next((e['id'] for e in datos['estados'] if e['nombre'] == nuevo_estado), tarea['estado'])

                            st.session_state['datos']['tareas'][i]['responsable'] = nuevo_resp_id
                            st.session_state['datos']['tareas'][i]['fecha_objetivo'] = nueva_fecha.strftime("%Y-%m-%d")
                            st.session_state['datos']['tareas'][i]['estado'] = nuevo_estado_id
                            st.session_state['datos']['tareas'][i]['prioridad'] = nueva_prioridad
                            st.session_state['datos']['tareas'][i]['notas'] = nuevas_notas
                            break

                    guardar_datos(st.session_state['datos'])
                    st.success("✅ Tarea actualizada correctamente")
                    st.rerun()

            with col2:
                if tarea['estado'] != 'finalizado':
                    if st.button("✅ Marcar Finalizada", use_container_width=True):
                        for i, t in enumerate(st.session_state['datos']['tareas']):
                            if t['id'] == tarea_id:
                                st.session_state['datos']['tareas'][i]['estado'] = 'finalizado'
                                break
                        guardar_datos(st.session_state['datos'])
                        st.success("✅ Tarea marcada como finalizada")
                        st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Huerta Inteligente LPET**")
st.sidebar.markdown("Finca La Palma y El Tucan")
st.sidebar.markdown(f"Dashboard v1.0")

# Boton de recarga
if st.sidebar.button("🔄 Recargar Datos"):
    st.session_state['recargar'] = True
    st.rerun()
