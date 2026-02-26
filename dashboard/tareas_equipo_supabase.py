"""
Dashboard de Gestion de Tareas - Proyecto Circular de Produccion Agricola
Huerta Inteligente LPET - Finca La Palma y El Tucan
VERSION CON SUPABASE
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
from pathlib import Path
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Cargar variables de entorno (soporta .env local y Streamlit Cloud secrets)
BASE_DIR = Path(__file__).parent.parent
load_dotenv(BASE_DIR / ".env")

# Intentar cargar desde Streamlit secrets (Cloud) o .env (local)
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Configuracion de la pagina
st.set_page_config(
    page_title="Tareas - Huerta LPET",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Crear cliente Supabase
@st.cache_resource
def get_supabase_client():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase_client()

# Funciones de carga desde Supabase
def cargar_equipo():
    """Carga los miembros del equipo desde Supabase"""
    response = supabase.table('equipo').select('*').execute()
    return response.data

def cargar_estados():
    """Carga los estados desde Supabase"""
    response = supabase.table('estados').select('*').order('orden').execute()
    return response.data

def cargar_categorias():
    """Carga las categorias desde Supabase"""
    response = supabase.table('categorias').select('*').execute()
    return response.data

def cargar_metadata():
    """Carga la metadata del proyecto desde Supabase"""
    response = supabase.table('metadata').select('*').limit(1).execute()
    return response.data[0] if response.data else {}

def cargar_tareas():
    """Carga todas las tareas desde Supabase"""
    response = supabase.table('tareas').select('*').order('fecha_objetivo').execute()
    return response.data

def actualizar_tarea(tarea_id, datos):
    """Actualiza una tarea en Supabase"""
    datos['updated_at'] = datetime.now().isoformat()
    response = supabase.table('tareas').update(datos).eq('id', tarea_id).execute()
    return response.data

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

# Cargar datos desde Supabase
if 'datos_cargados' not in st.session_state or st.session_state.get('recargar', False):
    with st.spinner('Cargando datos desde Supabase...'):
        st.session_state['equipo'] = cargar_equipo()
        st.session_state['estados'] = cargar_estados()
        st.session_state['categorias'] = cargar_categorias()
        st.session_state['metadata'] = cargar_metadata()
        st.session_state['tareas'] = cargar_tareas()
        st.session_state['datos_cargados'] = True
        st.session_state['recargar'] = False

equipo = st.session_state['equipo']
estados = st.session_state['estados']
categorias = st.session_state['categorias']
metadata = st.session_state['metadata']
tareas = st.session_state['tareas']

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
    .supabase-badge {
        background-color: #3ECF8E;
        color: white;
        padding: 3px 8px;
        border-radius: 5px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("📋 Gestion de Tareas")
st.sidebar.markdown(f"**Proyecto:** {metadata.get('proyecto', 'N/A')}")
st.sidebar.markdown(f"**Finca:** {metadata.get('finca', 'N/A')}")
st.sidebar.markdown(f'<span class="supabase-badge">Supabase</span>', unsafe_allow_html=True)

st.sidebar.markdown("---")

# Filtros en sidebar
st.sidebar.subheader("Filtros")

# Filtro por responsable
responsables_opciones = ["Todos"] + [e['nombre'] for e in equipo]
filtro_responsable = st.sidebar.selectbox(
    "Responsable",
    responsables_opciones,
    index=0
)

# Filtro por categoria
categorias_opciones = ["Todas"] + [f"{c['icono']} {c['nombre']}" for c in categorias]
filtro_categoria = st.sidebar.selectbox(
    "Categoria",
    categorias_opciones,
    index=0
)

# Filtro por estado
estados_opciones = ["Todos"] + [e['nombre'] for e in estados]
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
tareas_filtradas = tareas.copy()

if filtro_responsable != "Todos":
    resp_id = next((e['id'] for e in equipo if e['nombre'] == filtro_responsable), None)
    if resp_id:
        tareas_filtradas = [t for t in tareas_filtradas if t['responsable'] == resp_id]

if filtro_categoria != "Todas":
    cat_nombre = filtro_categoria.split(' ', 1)[1] if ' ' in filtro_categoria else filtro_categoria
    cat_id = next((c['id'] for c in categorias if c['nombre'] == cat_nombre), None)
    if cat_id:
        tareas_filtradas = [t for t in tareas_filtradas if t['categoria'] == cat_id]

if filtro_estado != "Todos":
    estado_id = next((e['id'] for e in estados if e['nombre'] == filtro_estado), None)
    if estado_id:
        tareas_filtradas = [t for t in tareas_filtradas if t['estado'] == estado_id]

if filtro_prioridad != "Todas":
    tareas_filtradas = [t for t in tareas_filtradas if t['prioridad'] == filtro_prioridad]

# Navegacion
st.sidebar.markdown("---")

# Determinar pagina inicial
if 'pagina_actual' not in st.session_state:
    st.session_state['pagina_actual'] = "📊 Resumen"

paginas = ["📊 Resumen", "📝 Lista de Tareas", "🎯 Tablero Kanban", "✏️ Editar Tarea"]
pagina_idx = paginas.index(st.session_state['pagina_actual']) if st.session_state['pagina_actual'] in paginas else 0

pagina = st.sidebar.radio(
    "Vista",
    paginas,
    index=pagina_idx
)

# Actualizar pagina actual en session_state
st.session_state['pagina_actual'] = pagina

# ============================================
# PAGINA: RESUMEN
# ============================================
if pagina == "📊 Resumen":
    st.title("📊 Resumen del Proyecto")

    # Fechas criticas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📅 Inicio Obra", metadata.get('fecha_inicio_obra', 'N/A'))
    with col2:
        st.metric("🛒 Limite Compras", metadata.get('fecha_limite_compras', 'N/A'))
    with col3:
        try:
            dias_para_inicio = (datetime.strptime(metadata.get('fecha_inicio_obra', '2026-02-23'), "%Y-%m-%d").date() - date.today()).days
            st.metric("⏰ Dias para inicio", f"{dias_para_inicio} dias")
        except:
            st.metric("⏰ Dias para inicio", "N/A")

    st.markdown("---")

    # KPIs principales
    total_tareas = len(tareas)
    por_iniciar = len([t for t in tareas if t['estado'] == 'por_iniciar'])
    en_proceso = len([t for t in tareas if t['estado'] == 'en_proceso'])
    finalizadas = len([t for t in tareas if t['estado'] == 'finalizado'])
    bloqueadas = len([t for t in tareas if t['estado'] == 'bloqueado'])

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
        for cat in categorias:
            cat_tareas = [t for t in tareas if t['categoria'] == cat['id']]
            cat_completadas = len([t for t in cat_tareas if t['estado'] == 'finalizado'])
            cat_total = len(cat_tareas)

            st.markdown(f"**{cat['icono']} {cat['nombre']}** ({cat_completadas}/{cat_total})")
            if cat_total > 0:
                st.progress(cat_completadas / cat_total)

    with col2:
        # Tareas por responsable
        st.markdown("### Tareas por Responsable")
        for miembro in equipo:
            if miembro['id'] == 'sin_asignar':
                continue
            resp_tareas = [t for t in tareas if t['responsable'] == miembro['id']]
            resp_pendientes = len([t for t in resp_tareas if t['estado'] not in ['finalizado']])
            if resp_pendientes > 0:
                st.markdown(f"**{miembro['nombre']}:** {resp_pendientes} pendientes")

    st.markdown("---")

    # Tareas urgentes
    st.markdown("### 🚨 Tareas Urgentes (Vencidas o Hoy)")
    hoy = date.today()

    tareas_urgentes = []
    for t in tareas:
        if t['estado'] == 'finalizado':
            continue
        try:
            fecha_obj = datetime.strptime(t['fecha_objetivo'], "%Y-%m-%d").date()
            if fecha_obj <= hoy or t['prioridad'] == 'urgente':
                tareas_urgentes.append({
                    'tarea': t['tarea'],
                    'fecha': t['fecha_objetivo'],
                    'responsable': get_responsable_nombre(t['responsable'], equipo),
                    'estado': get_estado_nombre(t['estado'], estados),
                    'prioridad': t['prioridad']
                })
        except:
            pass

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
    tareas_filtradas = sorted(tareas_filtradas, key=lambda x: x['fecha_objetivo'] or '9999-99-99')

    for tarea in tareas_filtradas:
        cat_info = get_categoria_info(tarea['categoria'], categorias)
        estado_color = get_estado_color(tarea['estado'], estados)
        estado_nombre = get_estado_nombre(tarea['estado'], estados)
        resp_nombre = get_responsable_nombre(tarea['responsable'], equipo)

        # Verificar si esta vencida
        fecha_class = ""
        try:
            fecha_obj = datetime.strptime(tarea['fecha_objetivo'], "%Y-%m-%d").date()
            hoy = date.today()
            if tarea['estado'] != 'finalizado':
                if fecha_obj < hoy:
                    fecha_class = "fecha-vencida"
                elif fecha_obj == hoy:
                    fecha_class = "fecha-hoy"
        except:
            pass

        with st.container():
            col1, col2, col3, col4, col5 = st.columns([0.5, 3, 1.5, 1.5, 1])

            with col1:
                st.markdown(f"### {cat_info['icono']}")

            with col2:
                st.markdown(f"**{tarea['tarea']}**")
                if tarea.get('notas'):
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
                    st.session_state['pagina_actual'] = "✏️ Editar Tarea"
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
        estado_info = next((e for e in estados if e['id'] == estado_id), None)
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
                cat_info = get_categoria_info(tarea['categoria'], categorias)
                resp_nombre = get_responsable_nombre(tarea['responsable'], equipo)

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
    tareas_opciones = {f"{t['id']} - {t['tarea'][:50]}": t['id'] for t in tareas}

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
        tarea = next((t for t in tareas if t['id'] == tarea_id), None)

        if tarea:
            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Informacion de la Tarea")

                cat_info = get_categoria_info(tarea['categoria'], categorias)
                st.markdown(f"**Categoria:** {cat_info['icono']} {cat_info['nombre']}")
                st.markdown(f"**Tarea:** {tarea['tarea']}")

                if tarea.get('dependencias'):
                    deps = [next((t['tarea'] for t in tareas if t['id'] == d), str(d)) for d in tarea['dependencias']]
                    st.markdown(f"**Dependencias:** {', '.join(deps[:3])}{'...' if len(deps) > 3 else ''}")

            with col2:
                st.markdown("### Editar")

                # Responsable
                resp_opciones = [e['nombre'] for e in equipo]
                resp_actual = get_responsable_nombre(tarea['responsable'], equipo)
                resp_idx = resp_opciones.index(resp_actual) if resp_actual in resp_opciones else 0

                nuevo_responsable = st.selectbox(
                    "Responsable",
                    resp_opciones,
                    index=resp_idx
                )

                # Fecha
                try:
                    fecha_actual = datetime.strptime(tarea['fecha_objetivo'], "%Y-%m-%d").date()
                except:
                    fecha_actual = date.today()

                nueva_fecha = st.date_input(
                    "Fecha objetivo",
                    value=fecha_actual
                )

                # Estado
                estados_opciones = [e['nombre'] for e in estados]
                estado_actual = get_estado_nombre(tarea['estado'], estados)
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
                    value=tarea.get('notas', '') or ''
                )

            st.markdown("---")

            col1, col2, col3 = st.columns([1, 1, 2])

            with col1:
                if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
                    # Obtener IDs
                    nuevo_resp_id = next((e['id'] for e in equipo if e['nombre'] == nuevo_responsable), tarea['responsable'])
                    nuevo_estado_id = next((e['id'] for e in estados if e['nombre'] == nuevo_estado), tarea['estado'])

                    # Actualizar en Supabase
                    datos_actualizados = {
                        'responsable': nuevo_resp_id,
                        'fecha_objetivo': nueva_fecha.strftime("%Y-%m-%d"),
                        'estado': nuevo_estado_id,
                        'prioridad': nueva_prioridad,
                        'notas': nuevas_notas
                    }

                    actualizar_tarea(tarea_id, datos_actualizados)
                    st.success("✅ Tarea actualizada en Supabase")
                    st.session_state['recargar'] = True
                    st.rerun()

            with col2:
                if tarea['estado'] != 'finalizado':
                    if st.button("✅ Marcar Finalizada", use_container_width=True):
                        actualizar_tarea(tarea_id, {'estado': 'finalizado'})
                        st.success("✅ Tarea marcada como finalizada")
                        st.session_state['recargar'] = True
                        st.rerun()

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Huerta Inteligente LPET**")
st.sidebar.markdown("Finca La Palma y El Tucan")
st.sidebar.markdown(f"Dashboard v2.0 - Supabase")

# Boton de recarga
if st.sidebar.button("🔄 Recargar Datos"):
    st.session_state['recargar'] = True
    st.rerun()
