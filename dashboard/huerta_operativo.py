"""
HUERTA INTELIGENTE LPET - Dashboard Operativo
==============================================
- Editor visual de configuracion de huerta
- Conexion con Google Sheets (datos de operarios)
- Estimaciones automaticas basadas en datos reales

Ejecutar: streamlit run dashboard/huerta_operativo.py
"""

import streamlit as st
import json
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import os

# ============================================================
# CONFIGURACION
# ============================================================
st.set_page_config(
    page_title="Huerta LPET - Operativo",
    page_icon="🌱",
    layout="wide"
)

# Ruta de configuracion
CONFIG_PATH = "config/huerta_config.json"
SHEETS_CONFIG_PATH = "config/google_sheets.json"

# ============================================================
# FUNCIONES DE DATOS
# ============================================================

def cargar_config():
    """Carga configuracion de la huerta"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return config_default()

def guardar_config(config):
    """Guarda configuracion"""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return True

def config_default():
    """Configuracion por defecto"""
    return {
        "metadata": {
            "nombre": "Huerta LPET",
            "ubicacion": "Zipacon, Cundinamarca",
            "ultima_modificacion": datetime.now().strftime("%Y-%m-%d %H:%M")
        },
        "zonas": [
            {"id": "cama1", "nombre": "Cama 1", "tipo": "cama", "ancho": 1.21, "largo": 8.92, "x": 0, "y": 0, "cultivos": ["lechuga", "rucula"], "color": "#90EE90"},
            {"id": "cama2", "nombre": "Cama 2", "tipo": "cama", "ancho": 1.21, "largo": 9.20, "x": 10, "y": 0, "cultivos": ["acelga", "espinaca"], "color": "#98FB98"},
            {"id": "cama3", "nombre": "Cama 3", "tipo": "cama", "ancho": 1.32, "largo": 12.11, "x": 20, "y": 0, "cultivos": ["cebolla", "ajo"], "color": "#8B4513"},
            {"id": "cama4", "nombre": "Cama 4", "tipo": "cama", "ancho": 1.31, "largo": 11.95, "x": 33, "y": 0, "cultivos": ["brocoli", "kale"], "color": "#228B22"},
            {"id": "cama5", "nombre": "Cama 5", "tipo": "cama", "ancho": 1.31, "largo": 11.95, "x": 46, "y": 0, "cultivos": ["zanahoria", "remolacha"], "color": "#D2691E"},
            {"id": "cama6", "nombre": "Cama 6", "tipo": "cama", "ancho": 1.31, "largo": 11.90, "x": 59, "y": 0, "cultivos": ["rotacion"], "color": "#DEB887"},
            {"id": "invernadero", "nombre": "Invernadero", "tipo": "invernadero", "ancho": 5.60, "largo": 5.99, "x": 0, "y": 15, "cultivos": ["tomate", "albahaca"], "color": "#87CEEB"},
            {"id": "tour", "nombre": "Tour Bienestar", "tipo": "tour", "ancho": 8, "largo": 11, "x": 15, "y": 15, "cultivos": ["medicinales"], "color": "#FFD700"},
        ],
        "animales": {
            "gallinas": {"cantidad": 25, "produccion_huevos_dia": 0.7},
            "conejos": {"cantidad": 12}
        },
        "costos": {
            "operario_mensual_cop": 800000,
            "insumos_mensual_cop": 200000
        },
        "precios_venta": {
            "huevo_cop": 800,
            "lechuga_kg_cop": 8000,
            "tomate_kg_cop": 6000
        }
    }

@st.cache_data(ttl=300)
def cargar_datos_sheets(sheet_id, tab_name):
    """Carga datos desde Google Sheets publico"""
    try:
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={tab_name}"
        df = pd.read_csv(url)
        return df
    except Exception as e:
        return None

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("🌱 Huerta LPET")
st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "Menu",
    ["📊 Dashboard", "✏️ Editor Huerta", "📝 Ver Registros", "📈 Estimaciones", "⚙️ Configuracion"]
)

# Cargar configuracion
config = cargar_config()

st.sidebar.markdown("---")
st.sidebar.caption(f"Ultima mod: {config['metadata'].get('ultima_modificacion', 'N/A')}")

# ============================================================
# PAGINA: DASHBOARD
# ============================================================
if pagina == "📊 Dashboard":
    st.title("📊 Dashboard Operativo")

    # KPIs rapidos
    col1, col2, col3, col4 = st.columns(4)

    # Calcular area total
    area_total = sum(z['ancho'] * z['largo'] for z in config['zonas'])

    with col1:
        st.metric("Area Total", f"{area_total:.1f} m²")

    with col2:
        st.metric("Camas Activas", len([z for z in config['zonas'] if z['tipo'] == 'cama']))

    with col3:
        gallinas = config['animales']['gallinas']['cantidad']
        huevos_dia = int(gallinas * config['animales']['gallinas']['produccion_huevos_dia'])
        st.metric("Huevos/Dia Est.", huevos_dia)

    with col4:
        st.metric("Gallinas", config['animales']['gallinas']['cantidad'])

    st.markdown("---")

    # Mapa de la huerta
    st.subheader("Mapa de la Huerta")

    fig = go.Figure()

    for zona in config['zonas']:
        x0, y0 = zona['x'], zona['y']
        x1, y1 = x0 + zona['largo'], y0 + zona['ancho']

        fig.add_trace(go.Scatter(
            x=[x0, x1, x1, x0, x0],
            y=[y0, y0, y1, y1, y0],
            fill='toself',
            fillcolor=zona['color'],
            line=dict(color='black', width=1),
            name=zona['nombre'],
            hovertemplate=f"<b>{zona['nombre']}</b><br>" +
                         f"Area: {zona['ancho'] * zona['largo']:.1f} m²<br>" +
                         f"Cultivos: {', '.join(zona['cultivos'])}<extra></extra>"
        ))

        # Etiqueta
        fig.add_annotation(
            x=(x0 + x1) / 2,
            y=(y0 + y1) / 2,
            text=zona['nombre'],
            showarrow=False,
            font=dict(size=10)
        )

    fig.update_layout(
        height=500,
        showlegend=True,
        xaxis=dict(title="Metros", scaleanchor="y"),
        yaxis=dict(title="Metros"),
        legend=dict(orientation="h", y=-0.1)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Resumen por zona
    st.subheader("Resumen por Zona")

    zonas_df = pd.DataFrame([
        {
            "Zona": z['nombre'],
            "Tipo": z['tipo'].capitalize(),
            "Area (m²)": round(z['ancho'] * z['largo'], 2),
            "Cultivos": ", ".join(z['cultivos'])
        }
        for z in config['zonas']
    ])

    st.dataframe(zonas_df, use_container_width=True, hide_index=True)

# ============================================================
# PAGINA: EDITOR HUERTA
# ============================================================
elif pagina == "✏️ Editor Huerta":
    st.title("✏️ Editor de la Huerta")
    st.info("Modifica las dimensiones y ubicacion de cada zona. Los cambios se guardan automaticamente.")

    # Selector de zona
    zona_nombres = [z['nombre'] for z in config['zonas']]
    zona_seleccionada = st.selectbox("Seleccionar zona a editar:", zona_nombres)

    # Encontrar zona
    zona_idx = zona_nombres.index(zona_seleccionada)
    zona = config['zonas'][zona_idx]

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Editar: {zona['nombre']}")

        # Campos editables
        nuevo_nombre = st.text_input("Nombre", zona['nombre'])
        nuevo_ancho = st.slider("Ancho (m)", 0.5, 20.0, float(zona['ancho']), 0.1)
        nuevo_largo = st.slider("Largo (m)", 0.5, 30.0, float(zona['largo']), 0.1)
        nueva_x = st.slider("Posicion X", 0, 100, int(zona['x']), 1)
        nueva_y = st.slider("Posicion Y", 0, 50, int(zona['y']), 1)

        # Cultivos
        cultivos_texto = st.text_input("Cultivos (separados por coma)", ", ".join(zona['cultivos']))
        nuevos_cultivos = [c.strip() for c in cultivos_texto.split(",")]

        # Color
        nuevo_color = st.color_picker("Color", zona['color'])

        # Calcular area
        nueva_area = nuevo_ancho * nuevo_largo
        st.metric("Area calculada", f"{nueva_area:.2f} m²")

    with col2:
        st.subheader("Vista previa")

        # Mini mapa con la zona editada
        fig_preview = go.Figure()

        # Mostrar todas las zonas
        for i, z in enumerate(config['zonas']):
            if i == zona_idx:
                # Zona editada (valores nuevos)
                x0, y0 = nueva_x, nueva_y
                x1, y1 = x0 + nuevo_largo, y0 + nuevo_ancho
                color = nuevo_color
                nombre = nuevo_nombre
            else:
                x0, y0 = z['x'], z['y']
                x1, y1 = x0 + z['largo'], y0 + z['ancho']
                color = z['color']
                nombre = z['nombre']

            fig_preview.add_trace(go.Scatter(
                x=[x0, x1, x1, x0, x0],
                y=[y0, y0, y1, y1, y0],
                fill='toself',
                fillcolor=color,
                line=dict(color='black', width=2 if i == zona_idx else 1),
                name=nombre,
                showlegend=False
            ))

        fig_preview.update_layout(
            height=400,
            xaxis=dict(title="X (m)", scaleanchor="y"),
            yaxis=dict(title="Y (m)")
        )

        st.plotly_chart(fig_preview, use_container_width=True)

    # Botones de accion
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("💾 Guardar Cambios", type="primary"):
            # Actualizar zona
            config['zonas'][zona_idx] = {
                "id": zona['id'],
                "nombre": nuevo_nombre,
                "tipo": zona['tipo'],
                "ancho": nuevo_ancho,
                "largo": nuevo_largo,
                "x": nueva_x,
                "y": nueva_y,
                "cultivos": nuevos_cultivos,
                "color": nuevo_color
            }
            config['metadata']['ultima_modificacion'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            guardar_config(config)
            st.success("Cambios guardados!")
            st.rerun()

    with col2:
        if st.button("➕ Agregar Zona"):
            nueva_zona = {
                "id": f"zona_{len(config['zonas'])+1}",
                "nombre": f"Nueva Zona {len(config['zonas'])+1}",
                "tipo": "cama",
                "ancho": 1.5,
                "largo": 10,
                "x": 0,
                "y": 30,
                "cultivos": ["nuevo"],
                "color": "#CCCCCC"
            }
            config['zonas'].append(nueva_zona)
            guardar_config(config)
            st.success("Zona agregada!")
            st.rerun()

    with col3:
        if st.button("🗑️ Eliminar Zona", type="secondary"):
            if len(config['zonas']) > 1:
                config['zonas'].pop(zona_idx)
                guardar_config(config)
                st.success("Zona eliminada!")
                st.rerun()
            else:
                st.error("Debe haber al menos una zona")

    with col4:
        if st.button("🔄 Restaurar Default"):
            config = config_default()
            guardar_config(config)
            st.success("Configuracion restaurada!")
            st.rerun()

# ============================================================
# PAGINA: VER REGISTROS
# ============================================================
elif pagina == "📝 Ver Registros":
    st.title("📝 Registros de Operarios")

    # Configurar conexion
    st.markdown("### Conexion a Google Sheets")

    # Cargar config de sheets si existe
    sheets_config = {}
    if os.path.exists(SHEETS_CONFIG_PATH):
        with open(SHEETS_CONFIG_PATH, 'r') as f:
            sheets_config = json.load(f)

    sheet_id = st.text_input(
        "ID del Google Sheet:",
        value=sheets_config.get('sheet_id', ''),
        help="El ID esta en la URL: docs.google.com/spreadsheets/d/[ID]/edit"
    )

    if sheet_id:
        # Guardar config
        os.makedirs("config", exist_ok=True)
        with open(SHEETS_CONFIG_PATH, 'w') as f:
            json.dump({"sheet_id": sheet_id}, f)

        st.markdown("---")

        # Tabs para cada tipo de registro
        tab1, tab2, tab3, tab4 = st.tabs(["🥬 Cosecha", "🥚 Huevos", "💧 Riego", "✅ Tareas"])

        with tab1:
            st.subheader("Registro de Cosecha")
            df_cosecha = cargar_datos_sheets(sheet_id, "Cosecha")
            if df_cosecha is not None and len(df_cosecha) > 0:
                st.dataframe(df_cosecha.tail(20), use_container_width=True)

                # Resumen
                if 'Cantidad_kg' in df_cosecha.columns or len(df_cosecha.columns) > 4:
                    col_kg = df_cosecha.columns[4] if len(df_cosecha.columns) > 4 else None
                    if col_kg:
                        total_kg = pd.to_numeric(df_cosecha[col_kg], errors='coerce').sum()
                        st.metric("Total cosechado", f"{total_kg:.1f} kg")
            else:
                st.info("No hay datos de cosecha. Usa el Google Form para registrar.")
                st.markdown("""
                **Para empezar:**
                1. Crea el Google Form siguiendo `docs/SETUP_GOOGLE_FORMS.md`
                2. Conectalo a un Google Sheet
                3. Ingresa el ID del Sheet arriba
                """)

        with tab2:
            st.subheader("Registro de Huevos")
            df_huevos = cargar_datos_sheets(sheet_id, "Huevos")
            if df_huevos is not None and len(df_huevos) > 0:
                st.dataframe(df_huevos.tail(20), use_container_width=True)

                # Grafico de huevos por dia
                if len(df_huevos.columns) > 2:
                    col_cantidad = df_huevos.columns[2]
                    df_huevos['cantidad_num'] = pd.to_numeric(df_huevos[col_cantidad], errors='coerce')
                    fig = px.line(df_huevos.tail(30), y='cantidad_num', title="Huevos ultimos 30 registros")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No hay datos de huevos.")

        with tab3:
            st.subheader("Registro de Riego")
            df_riego = cargar_datos_sheets(sheet_id, "Riego")
            if df_riego is not None and len(df_riego) > 0:
                st.dataframe(df_riego.tail(20), use_container_width=True)
            else:
                st.info("No hay datos de riego.")

        with tab4:
            st.subheader("Tareas Completadas")
            df_tareas = cargar_datos_sheets(sheet_id, "Tareas")
            if df_tareas is not None and len(df_tareas) > 0:
                st.dataframe(df_tareas.tail(20), use_container_width=True)
            else:
                st.info("No hay datos de tareas.")

    else:
        st.warning("Ingresa el ID del Google Sheet para ver los registros.")
        st.markdown("""
        ### Como obtener el ID:

        1. Abre tu Google Sheet
        2. Mira la URL: `https://docs.google.com/spreadsheets/d/`**`ESTE_ES_EL_ID`**`/edit`
        3. Copia solo el ID y pegalo arriba

        ### Aun no tienes el Sheet?

        Sigue las instrucciones en `docs/SETUP_GOOGLE_FORMS.md`
        """)

# ============================================================
# PAGINA: ESTIMACIONES
# ============================================================
elif pagina == "📈 Estimaciones":
    st.title("📈 Estimaciones y Proyecciones")

    # Cargar datos de sheets si hay
    sheets_config = {}
    if os.path.exists(SHEETS_CONFIG_PATH):
        with open(SHEETS_CONFIG_PATH, 'r') as f:
            sheets_config = json.load(f)

    st.markdown("### Parametros de Estimacion")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Produccion")

        # Productividad por m2 (editable)
        prod_hojas = st.number_input("Kg hojas/m²/mes", 0.5, 5.0, 2.0, 0.1)
        prod_raices = st.number_input("Kg raices/m²/mes", 1.0, 8.0, 3.0, 0.1)
        prod_tomate = st.number_input("Kg tomate/m²/mes", 2.0, 10.0, 4.0, 0.1)

        # Calcular produccion estimada
        area_hojas = sum(z['ancho'] * z['largo'] for z in config['zonas']
                        if any(c in ['lechuga', 'rucula', 'espinaca', 'acelga', 'kale']
                              for c in z['cultivos']))
        area_raices = sum(z['ancho'] * z['largo'] for z in config['zonas']
                         if any(c in ['zanahoria', 'remolacha', 'rabano']
                               for c in z['cultivos']))
        area_tomate = sum(z['ancho'] * z['largo'] for z in config['zonas']
                         if 'tomate' in z['cultivos'])

    with col2:
        st.subheader("Animales")

        gallinas = st.number_input("Numero de gallinas",
                                   1, 100,
                                   config['animales']['gallinas']['cantidad'])
        tasa_postura = st.slider("Tasa postura (%)", 50, 95, 70)

        conejos = st.number_input("Numero de conejos",
                                  0, 50,
                                  config['animales']['conejos']['cantidad'])

    st.markdown("---")
    st.subheader("Resultados Estimados (Mensual)")

    # Calculos
    kg_hojas_mes = area_hojas * prod_hojas
    kg_raices_mes = area_raices * prod_raices
    kg_tomate_mes = area_tomate * prod_tomate
    huevos_mes = gallinas * (tasa_postura / 100) * 30

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Hojas verdes", f"{kg_hojas_mes:.1f} kg/mes")
    with col2:
        st.metric("Raices", f"{kg_raices_mes:.1f} kg/mes")
    with col3:
        st.metric("Tomate", f"{kg_tomate_mes:.1f} kg/mes")
    with col4:
        st.metric("Huevos", f"{huevos_mes:.0f}/mes")

    st.markdown("---")
    st.subheader("Proyeccion Financiera")

    col1, col2 = st.columns(2)

    with col1:
        # Ingresos
        precio_hojas = st.number_input("Precio hojas (COP/kg)", 1000, 20000, 8000, 500)
        precio_raices = st.number_input("Precio raices (COP/kg)", 1000, 15000, 5000, 500)
        precio_tomate = st.number_input("Precio tomate (COP/kg)", 1000, 15000, 6000, 500)
        precio_huevo = st.number_input("Precio huevo (COP/u)", 200, 2000, 800, 50)

    with col2:
        # Costos
        costo_operario = st.number_input("Costo operario (COP/mes)",
                                         100000, 2000000,
                                         config['costos']['operario_mensual_cop'], 50000)
        costo_insumos = st.number_input("Costo insumos (COP/mes)",
                                        50000, 500000,
                                        config['costos']['insumos_mensual_cop'], 10000)

    # Calcular financiero
    ingreso_hojas = kg_hojas_mes * precio_hojas
    ingreso_raices = kg_raices_mes * precio_raices
    ingreso_tomate = kg_tomate_mes * precio_tomate
    ingreso_huevos = huevos_mes * precio_huevo

    ingreso_total = ingreso_hojas + ingreso_raices + ingreso_tomate + ingreso_huevos
    costo_total = costo_operario + costo_insumos
    beneficio_neto = ingreso_total - costo_total

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Ingresos Totales", f"${ingreso_total:,.0f} COP")
    with col2:
        st.metric("Costos Totales", f"${costo_total:,.0f} COP")
    with col3:
        delta_color = "normal" if beneficio_neto > 0 else "inverse"
        st.metric("Beneficio Neto", f"${beneficio_neto:,.0f} COP",
                 delta=f"{'Ganancia' if beneficio_neto > 0 else 'Perdida'}")

    # Grafico de composicion
    fig_ingresos = go.Figure(data=[
        go.Bar(name='Ingresos', x=['Hojas', 'Raices', 'Tomate', 'Huevos'],
               y=[ingreso_hojas, ingreso_raices, ingreso_tomate, ingreso_huevos],
               marker_color=['#4CAF50', '#FF9800', '#F44336', '#FFD700'])
    ])
    fig_ingresos.update_layout(title="Composicion de Ingresos", height=300)
    st.plotly_chart(fig_ingresos, use_container_width=True)

# ============================================================
# PAGINA: CONFIGURACION
# ============================================================
elif pagina == "⚙️ Configuracion":
    st.title("⚙️ Configuracion del Sistema")

    tab1, tab2, tab3 = st.tabs(["General", "Google Sheets", "Exportar/Importar"])

    with tab1:
        st.subheader("Informacion General")

        nombre = st.text_input("Nombre del proyecto", config['metadata']['nombre'])
        ubicacion = st.text_input("Ubicacion", config['metadata']['ubicacion'])

        if st.button("Guardar Informacion"):
            config['metadata']['nombre'] = nombre
            config['metadata']['ubicacion'] = ubicacion
            config['metadata']['ultima_modificacion'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            guardar_config(config)
            st.success("Guardado!")

        st.markdown("---")
        st.subheader("Animales")

        col1, col2 = st.columns(2)
        with col1:
            gallinas_cant = st.number_input("Gallinas", 0, 100,
                                           config['animales']['gallinas']['cantidad'])
            gallinas_prod = st.number_input("Huevos/gallina/dia", 0.0, 1.0,
                                           config['animales']['gallinas']['produccion_huevos_dia'], 0.05)
        with col2:
            conejos_cant = st.number_input("Conejos", 0, 50,
                                          config['animales']['conejos']['cantidad'])

        if st.button("Guardar Animales"):
            config['animales']['gallinas']['cantidad'] = gallinas_cant
            config['animales']['gallinas']['produccion_huevos_dia'] = gallinas_prod
            config['animales']['conejos']['cantidad'] = conejos_cant
            guardar_config(config)
            st.success("Guardado!")

    with tab2:
        st.subheader("Conexion Google Sheets")

        st.markdown("""
        ### Pasos para configurar:

        1. **Crear Google Sheet** con pestanas: Cosecha, Huevos, Riego, Tareas
        2. **Crear Google Forms** para cada tipo de registro
        3. **Conectar Forms a Sheet**
        4. **Hacer Sheet publico** (solo lectura)
        5. **Copiar el ID** del Sheet aqui

        Ver instrucciones completas en: `docs/SETUP_GOOGLE_FORMS.md`
        """)

        sheets_config = {}
        if os.path.exists(SHEETS_CONFIG_PATH):
            with open(SHEETS_CONFIG_PATH, 'r') as f:
                sheets_config = json.load(f)

        sheet_id = st.text_input("Sheet ID", sheets_config.get('sheet_id', ''))

        if st.button("Guardar y Probar Conexion"):
            os.makedirs("config", exist_ok=True)
            with open(SHEETS_CONFIG_PATH, 'w') as f:
                json.dump({"sheet_id": sheet_id}, f)

            # Probar conexion
            df_test = cargar_datos_sheets(sheet_id, "Cosecha")
            if df_test is not None:
                st.success(f"Conexion exitosa! {len(df_test)} registros encontrados")
            else:
                st.warning("No se pudo conectar. Verifica el ID y que el Sheet sea publico.")

    with tab3:
        st.subheader("Exportar Configuracion")

        if st.button("Descargar JSON"):
            json_str = json.dumps(config, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 Descargar huerta_config.json",
                data=json_str,
                file_name="huerta_config.json",
                mime="application/json"
            )

        st.markdown("---")
        st.subheader("Importar Configuracion")

        uploaded_file = st.file_uploader("Subir archivo JSON", type=['json'])
        if uploaded_file:
            try:
                new_config = json.load(uploaded_file)
                st.json(new_config)
                if st.button("Aplicar Configuracion"):
                    guardar_config(new_config)
                    st.success("Configuracion importada!")
                    st.rerun()
            except:
                st.error("Archivo JSON invalido")

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption("Huerta Inteligente LPET - Dashboard Operativo v2.0")
