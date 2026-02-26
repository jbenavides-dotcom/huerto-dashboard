"""
HUERTA INTELIGENTE LPET - Dashboard Interactivo
Finca La Palma y El Tucan - Zipacon, Cundinamarca

Ejecutar con: streamlit run dashboard/huerta_app.py
"""

import streamlit as st
import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import os

# ============================================================
# CONFIGURACION DE PAGINA
# ============================================================
st.set_page_config(
    page_title="Huerta Inteligente LPET",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# ESTILOS CSS PERSONALIZADOS
# ============================================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #2E7D32;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #E8F5E9 0%, #C8E6C9 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    .zone-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1B5E20;
        margin-bottom: 0.5rem;
    }
    .status-green { color: #2E7D32; font-weight: bold; }
    .status-yellow { color: #F9A825; font-weight: bold; }
    .status-red { color: #C62828; font-weight: bold; }
    .info-box {
        background: #E3F2FD;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1976D2;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# CARGAR DATOS
# ============================================================
@st.cache_data
def cargar_datos():
    """Carga datos desde el archivo JSON"""
    # Intentar cargar desde ruta relativa
    rutas_posibles = [
        "output/huerta_datos.json",
        "../output/huerta_datos.json",
        os.path.join(os.path.dirname(__file__), "..", "output", "huerta_datos.json")
    ]

    for ruta in rutas_posibles:
        if os.path.exists(ruta):
            with open(ruta, 'r', encoding='utf-8') as f:
                return json.load(f)

    # Si no encuentra el archivo, usar datos de ejemplo
    st.warning("Archivo de datos no encontrado. Usando datos de ejemplo.")
    return generar_datos_ejemplo()

def generar_datos_ejemplo():
    """Genera datos de ejemplo si no existe el JSON"""
    return {
        "metadata": {
            "proyecto": "Huerta Inteligente LPET",
            "finca": "La Palma y El Tucan",
            "ubicacion": "Zipacon, Cundinamarca"
        },
        "dimensiones": {
            "area_total_m2": 398.26,
            "camas_huerta": [
                {"numero": 1, "ancho_m": 1.21, "largo_m": 8.92, "area_m2": 10.79, "uso": "Ensaladas", "color": "#90EE90"},
                {"numero": 2, "ancho_m": 1.21, "largo_m": 9.20, "area_m2": 11.13, "uso": "Hojas", "color": "#98FB98"},
                {"numero": 3, "ancho_m": 1.32, "largo_m": 12.11, "area_m2": 15.99, "uso": "Base Italiana", "color": "#8B4513"},
                {"numero": 4, "ancho_m": 1.31, "largo_m": 11.95, "area_m2": 15.65, "uso": "Cruciferas", "color": "#228B22"},
                {"numero": 5, "ancho_m": 1.31, "largo_m": 11.95, "area_m2": 15.65, "uso": "Raices", "color": "#D2691E"},
                {"numero": 6, "ancho_m": 1.31, "largo_m": 11.90, "area_m2": 15.59, "uso": "Rotacion", "color": "#DEB887"}
            ],
            "invernadero": {"area_m2": 33.54},
            "espacio_libre": {"area_total_m2": 160.25},
            "compostaje": {"camas_lombricompost": {"area_total_m2": 73.59}}
        },
        "finanzas": {
            "inversion_inicial_usd": {"total": 4250},
            "costos_operativos_mensual_cop": {"total": 1060000},
            "ahorros_mensual_cop": {"total": 1050000},
            "ingresos_mensual_cop": {"tour_bienestar": {"total": 2400000}},
            "analisis": {"beneficio_neto_cop": 2390000, "payback_meses": 7}
        }
    }

datos = cargar_datos()

# ============================================================
# SIDEBAR - NAVEGACION
# ============================================================
st.sidebar.image("https://img.icons8.com/color/96/000000/plant-under-sun.png", width=80)
st.sidebar.title("Huerta LPET")
st.sidebar.markdown("---")

pagina = st.sidebar.radio(
    "Navegacion",
    ["Vista General", "Mapa Interactivo", "Zonas de Cultivo",
     "Produccion", "Animales", "Finanzas", "Cronograma"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.info(f"**Ubicacion:** {datos['metadata']['ubicacion']}")
st.sidebar.caption(f"Ultima actualizacion: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ============================================================
# PAGINA: VISTA GENERAL
# ============================================================
if pagina == "Vista General":
    st.markdown('<div class="main-header">HUERTA INTELIGENTE LPET</div>', unsafe_allow_html=True)
    st.markdown(f"### {datos['metadata']['finca']} - {datos['metadata']['ubicacion']}")

    # KPIs principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Area Total",
            value=f"{datos['dimensiones']['area_total_m2']:.0f} m2",
            delta="Proyecto completo"
        )

    with col2:
        area_camas = sum(c['area_m2'] for c in datos['dimensiones']['camas_huerta'])
        st.metric(
            label="Area Cultivo Activo",
            value=f"{area_camas + datos['dimensiones']['invernadero']['area_m2']:.0f} m2",
            delta="6 camas + invernadero"
        )

    with col3:
        st.metric(
            label="Inversion Total",
            value=f"USD {datos['finanzas']['inversion_inicial_usd']['total']:,}",
            delta="Tecnologia + Infraestructura"
        )

    with col4:
        st.metric(
            label="Payback",
            value=f"{datos['finanzas']['analisis']['payback_meses']} meses",
            delta="ROI positivo"
        )

    st.markdown("---")

    # Estado de zonas (simulado)
    st.subheader("Estado Actual de Zonas")

    col1, col2, col3, col4 = st.columns(4)

    zonas_estado = [
        ("Huerta Principal", "OK", "#2E7D32", "Humedad: 45%"),
        ("Invernadero", "OK", "#2E7D32", "Temp: 22C"),
        ("Compostaje", "Atencion", "#F9A825", "Temp: 58C"),
        ("Gallinas", "OK", "#2E7D32", "Agua: 75%")
    ]

    for i, (nombre, estado, color, detalle) in enumerate(zonas_estado):
        with [col1, col2, col3, col4][i]:
            estado_emoji = "✅" if estado == "OK" else "⚠️" if estado == "Atencion" else "❌"
            st.markdown(f"""
            <div style="background: white; padding: 1rem; border-radius: 10px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center;
                        border-top: 4px solid {color};">
                <h4 style="margin: 0; color: #333;">{nombre}</h4>
                <p style="font-size: 2rem; margin: 0.5rem 0;">{estado_emoji}</p>
                <p style="color: {color}; font-weight: bold;">{estado}</p>
                <p style="color: #666; font-size: 0.9rem;">{detalle}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # Resumen financiero
    st.subheader("Resumen Financiero Mensual")

    col1, col2 = st.columns(2)

    with col1:
        # Grafico de ingresos vs costos
        fig_finanzas = go.Figure()

        categorias = ['Ahorros', 'Tour Bienestar', 'Costos Operativos']
        valores = [
            datos['finanzas']['ahorros_mensual_cop']['total'] / 1000000,
            datos['finanzas']['ingresos_mensual_cop']['tour_bienestar']['total'] / 1000000,
            -datos['finanzas']['costos_operativos_mensual_cop']['total'] / 1000000
        ]
        colores = ['#4CAF50', '#2196F3', '#F44336']

        fig_finanzas.add_trace(go.Bar(
            x=categorias,
            y=valores,
            marker_color=colores,
            text=[f"${v:.1f}M" for v in valores],
            textposition='outside'
        ))

        fig_finanzas.update_layout(
            title="Flujo Mensual (Millones COP)",
            yaxis_title="COP (Millones)",
            showlegend=False,
            height=350
        )

        st.plotly_chart(fig_finanzas, use_container_width=True)

    with col2:
        # Distribucion de areas
        areas = {
            'Camas Huerta': sum(c['area_m2'] for c in datos['dimensiones']['camas_huerta']),
            'Invernadero': datos['dimensiones']['invernadero']['area_m2'],
            'Espacio Tour': datos['dimensiones']['espacio_libre']['area_total_m2'],
            'Compostaje': datos['dimensiones']['compostaje']['camas_lombricompost']['area_total_m2']
        }

        fig_areas = px.pie(
            values=list(areas.values()),
            names=list(areas.keys()),
            title="Distribucion de Areas (m2)",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_areas.update_layout(height=350)

        st.plotly_chart(fig_areas, use_container_width=True)

# ============================================================
# PAGINA: MAPA INTERACTIVO
# ============================================================
elif pagina == "Mapa Interactivo":
    st.markdown('<div class="main-header">MAPA INTERACTIVO DE LA HUERTA</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
    <strong>Instrucciones:</strong> Pase el cursor sobre cada zona para ver detalles.
    Haga clic en las zonas para mas informacion.
    </div>
    """, unsafe_allow_html=True)

    # Crear mapa interactivo con Plotly
    fig = go.Figure()

    # Escala del dibujo (1 unidad = 1 metro)
    escala = 1

    # Colores por zona
    colores = {
        'cama': '#90EE90',
        'invernadero': '#87CEEB',
        'tour': '#FFD700',
        'animales': '#DEB887',
        'compost': '#8B4513'
    }

    # ====== CAMAS DE HUERTA ======
    # Posicionamos las camas en una fila
    x_inicio = 0
    y_camas = 30

    for i, cama in enumerate(datos['dimensiones']['camas_huerta']):
        ancho = cama['ancho_m'] * escala
        largo = cama['largo_m'] * escala

        # Rectangulo de la cama
        fig.add_trace(go.Scatter(
            x=[x_inicio, x_inicio + largo, x_inicio + largo, x_inicio, x_inicio],
            y=[y_camas, y_camas, y_camas + ancho, y_camas + ancho, y_camas],
            fill='toself',
            fillcolor=cama.get('color', colores['cama']),
            line=dict(color='#2E7D32', width=2),
            name=f"Cama {cama['numero']}",
            hovertemplate=f"<b>Cama {cama['numero']}</b><br>" +
                         f"Uso: {cama['uso']}<br>" +
                         f"Area: {cama['area_m2']:.1f} m2<br>" +
                         f"Dimensiones: {cama['ancho_m']} x {cama['largo_m']} m<extra></extra>",
            showlegend=True
        ))

        # Etiqueta
        fig.add_annotation(
            x=x_inicio + largo/2,
            y=y_camas + ancho/2,
            text=f"C{cama['numero']}<br>{cama['uso']}",
            showarrow=False,
            font=dict(size=10, color='black')
        )

        x_inicio += largo + 1  # Espacio entre camas

    # ====== INVERNADERO ======
    inv = datos['dimensiones']['invernadero']
    inv_x, inv_y = 0, 18
    inv_ancho = inv.get('ancho_m', 5.60) * escala
    inv_largo = inv.get('largo_m', 5.99) * escala

    fig.add_trace(go.Scatter(
        x=[inv_x, inv_x + inv_largo, inv_x + inv_largo, inv_x, inv_x],
        y=[inv_y, inv_y, inv_y + inv_ancho, inv_y + inv_ancho, inv_y],
        fill='toself',
        fillcolor=colores['invernadero'],
        line=dict(color='#1565C0', width=2),
        name="Invernadero",
        hovertemplate=f"<b>Invernadero</b><br>" +
                     f"Area: {inv['area_m2']:.1f} m2<br>" +
                     f"Cultivos: Tomate, Albahaca, Curcuma<extra></extra>"
    ))

    fig.add_annotation(
        x=inv_x + inv_largo/2,
        y=inv_y + inv_ancho/2,
        text="INVERNADERO<br>33.5 m2",
        showarrow=False,
        font=dict(size=11, color='#1565C0', weight='bold')
    )

    # ====== ESPACIO TOUR ======
    tour_x, tour_y = 15, 18
    tour_ancho = 8 * escala
    tour_largo = 11 * escala

    fig.add_trace(go.Scatter(
        x=[tour_x, tour_x + tour_largo, tour_x + tour_largo, tour_x, tour_x],
        y=[tour_y, tour_y, tour_y + tour_ancho, tour_y + tour_ancho, tour_y],
        fill='toself',
        fillcolor=colores['tour'],
        line=dict(color='#F57F17', width=2),
        name="Tour Bienestar",
        hovertemplate="<b>Zona Tour de Bienestar</b><br>" +
                     "Area: 160 m2<br>" +
                     "Jardin medicinal + Flores<extra></extra>"
    ))

    fig.add_annotation(
        x=tour_x + tour_largo/2,
        y=tour_y + tour_ancho/2,
        text="TOUR BIENESTAR<br>Jardin Medicinal<br>160 m2",
        showarrow=False,
        font=dict(size=11, color='#E65100', weight='bold')
    )

    # ====== ZONA ANIMALES ======
    anim_x, anim_y = 0, 8

    # Gallinero
    fig.add_trace(go.Scatter(
        x=[anim_x, anim_x + 8, anim_x + 8, anim_x, anim_x],
        y=[anim_y, anim_y, anim_y + 5, anim_y + 5, anim_y],
        fill='toself',
        fillcolor='#FFCC80',
        line=dict(color='#E65100', width=2),
        name="Gallinero",
        hovertemplate="<b>Gallinero Movil</b><br>" +
                     "Capacidad: 25-30 gallinas<br>" +
                     "Sistema: Pastoreo rotacional<extra></extra>"
    ))

    fig.add_annotation(
        x=anim_x + 4, y=anim_y + 2.5,
        text="GALLINERO<br>25 gallinas",
        showarrow=False,
        font=dict(size=10)
    )

    # Conejeras
    fig.add_trace(go.Scatter(
        x=[anim_x + 10, anim_x + 16, anim_x + 16, anim_x + 10, anim_x + 10],
        y=[anim_y, anim_y, anim_y + 4, anim_y + 4, anim_y],
        fill='toself',
        fillcolor='#BCAAA4',
        line=dict(color='#5D4037', width=2),
        name="Conejeras",
        hovertemplate="<b>Conejeras Moviles</b><br>" +
                     "Cantidad: 12 conejos<br>" +
                     "Sistema: Jaulas tractor<extra></extra>"
    ))

    fig.add_annotation(
        x=anim_x + 13, y=anim_y + 2,
        text="CONEJERAS<br>12 conejos",
        showarrow=False,
        font=dict(size=10)
    )

    # Estanques Azolla
    fig.add_trace(go.Scatter(
        x=[anim_x + 18, anim_x + 26, anim_x + 26, anim_x + 18, anim_x + 18],
        y=[anim_y, anim_y, anim_y + 5, anim_y + 5, anim_y],
        fill='toself',
        fillcolor='#80DEEA',
        line=dict(color='#00838F', width=2),
        name="Estanques Azolla",
        hovertemplate="<b>Estanques Azolla</b><br>" +
                     "Funcion: Alimento gallinas<br>" +
                     "Alto en proteina<extra></extra>"
    ))

    fig.add_annotation(
        x=anim_x + 22, y=anim_y + 2.5,
        text="ESTANQUES<br>AZOLLA",
        showarrow=False,
        font=dict(size=10, color='#00838F')
    )

    # ====== ZONA COMPOSTAJE ======
    comp_x, comp_y = 0, 0

    # Placa compostera
    fig.add_trace(go.Scatter(
        x=[comp_x, comp_x + 9, comp_x + 9, comp_x, comp_x],
        y=[comp_y, comp_y, comp_y + 5.5, comp_y + 5.5, comp_y],
        fill='toself',
        fillcolor='#A1887F',
        line=dict(color='#4E342E', width=2),
        name="Compostera",
        hovertemplate="<b>Placa Compostera</b><br>" +
                     "Area: 52.5 m2<br>" +
                     "Residuos de cocina<extra></extra>"
    ))

    fig.add_annotation(
        x=comp_x + 4.5, y=comp_y + 2.75,
        text="COMPOSTERA<br>52.5 m2",
        showarrow=False,
        font=dict(size=10)
    )

    # Lombricompost
    fig.add_trace(go.Scatter(
        x=[comp_x + 11, comp_x + 28, comp_x + 28, comp_x + 11, comp_x + 11],
        y=[comp_y, comp_y, comp_y + 5, comp_y + 5, comp_y],
        fill='toself',
        fillcolor='#8D6E63',
        line=dict(color='#3E2723', width=2),
        name="Lombricompost",
        hovertemplate="<b>14 Camas Lombricompost</b><br>" +
                     "Area: 73.6 m2<br>" +
                     "Produccion: 250 kg humus/mes<extra></extra>"
    ))

    fig.add_annotation(
        x=comp_x + 19.5, y=comp_y + 2.5,
        text="LOMBRICOMPOST<br>14 camas - 73.6 m2",
        showarrow=False,
        font=dict(size=10)
    )

    # ====== SENSORES (iconos) ======
    sensores = [
        (15, 31, "S1", "Humedad Camas 1-2"),
        (35, 31, "S2", "Humedad Camas 3-4"),
        (55, 31, "S3", "Humedad Camas 5-6"),
        (3, 21, "S4", "Temp Invernadero"),
        (4, 10, "S5", "Temp Gallinero"),
        (22, 10, "S6", "Temp Estanques"),
        (4.5, 2, "S7", "Temp Compost")
    ]

    for sx, sy, label, desc in sensores:
        fig.add_trace(go.Scatter(
            x=[sx], y=[sy],
            mode='markers+text',
            marker=dict(size=20, color='#FF5722', symbol='circle'),
            text=[label],
            textposition='middle center',
            textfont=dict(size=8, color='white'),
            name=desc,
            hovertemplate=f"<b>Sensor {label}</b><br>{desc}<extra></extra>",
            showlegend=False
        ))

    # ====== CAMARAS (iconos) ======
    camaras = [
        (35, 35, "CAM1", "Vista General"),
        (3, 24, "CAM2", "Invernadero"),
        (15, 13, "CAM3", "Animales")
    ]

    for cx, cy, label, desc in camaras:
        fig.add_trace(go.Scatter(
            x=[cx], y=[cy],
            mode='markers+text',
            marker=dict(size=22, color='#9C27B0', symbol='square'),
            text=["📷"],
            textposition='middle center',
            name=f"Camara: {desc}",
            hovertemplate=f"<b>{label}</b><br>{desc}<extra></extra>",
            showlegend=False
        ))

    # Configuracion del layout
    fig.update_layout(
        title=dict(
            text="Plano Interactivo - Huerta Inteligente LPET",
            font=dict(size=20, color='#2E7D32')
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='#E0E0E0',
            zeroline=False,
            showticklabels=True,
            title="Metros"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#E0E0E0',
            zeroline=False,
            showticklabels=True,
            title="Metros",
            scaleanchor="x",
            scaleratio=1
        ),
        height=700,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
        hovermode='closest',
        plot_bgcolor='#FAFAFA'
    )

    # Agregar titulo de zonas
    fig.add_annotation(
        x=35, y=33,
        text="ZONA A: HUERTA PRINCIPAL",
        showarrow=False,
        font=dict(size=14, color='#1B5E20', weight='bold')
    )

    fig.add_annotation(
        x=35, y=16,
        text="ZONA B y C: INVERNADERO + TOUR",
        showarrow=False,
        font=dict(size=12, color='#1565C0')
    )

    fig.add_annotation(
        x=35, y=6,
        text="ZONA D: ANIMALES",
        showarrow=False,
        font=dict(size=12, color='#E65100')
    )

    fig.add_annotation(
        x=35, y=-1,
        text="ZONA E: COMPOSTAJE",
        showarrow=False,
        font=dict(size=12, color='#4E342E')
    )

    st.plotly_chart(fig, use_container_width=True)

    # Leyenda adicional
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **Sensores (circulos naranjas):**
        - S1-S3: Humedad suelo huerta
        - S4: Temperatura invernadero
        - S5: Temperatura gallinero
        - S6: Temperatura estanques
        - S7: Temperatura compost
        """)

    with col2:
        st.markdown("""
        **Camaras (cuadrados morados):**
        - CAM1: Vista general huerta
        - CAM2: Interior invernadero
        - CAM3: Gallinas y estanques
        """)

    with col3:
        st.markdown("""
        **Areas:**
        - Verde: Camas de huerta (84.8 m2)
        - Azul: Invernadero (33.5 m2)
        - Amarillo: Tour bienestar (160 m2)
        - Cafe: Compostaje (126 m2)
        """)

# ============================================================
# PAGINA: ZONAS DE CULTIVO
# ============================================================
elif pagina == "Zonas de Cultivo":
    st.markdown('<div class="main-header">ZONAS DE CULTIVO</div>', unsafe_allow_html=True)

    # Tabla de camas
    st.subheader("Detalle de Camas de Huerta")

    camas_df = pd.DataFrame(datos['dimensiones']['camas_huerta'])
    camas_df['cultivos'] = camas_df['cultivos'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

    # Formatear tabla
    camas_display = camas_df[['numero', 'uso', 'ancho_m', 'largo_m', 'area_m2', 'cultivos']].copy()
    camas_display.columns = ['Cama', 'Uso', 'Ancho (m)', 'Largo (m)', 'Area (m2)', 'Cultivos']

    st.dataframe(camas_display, use_container_width=True, hide_index=True)

    # Grafico de areas
    st.subheader("Distribucion de Areas por Cama")

    fig_camas = px.bar(
        camas_df,
        x='numero',
        y='area_m2',
        color='uso',
        text='area_m2',
        labels={'numero': 'Numero de Cama', 'area_m2': 'Area (m2)', 'uso': 'Uso'},
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_camas.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig_camas.update_layout(height=400)

    st.plotly_chart(fig_camas, use_container_width=True)

    # Invernadero
    st.markdown("---")
    st.subheader("Invernadero")

    inv = datos['dimensiones']['invernadero']
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Area", f"{inv['area_m2']:.1f} m2")
    with col2:
        st.metric("Dimensiones", f"{inv.get('largo_m', 5.99)} x {inv.get('ancho_m', 5.60)} m")
    with col3:
        st.metric("Altura", f"{inv.get('alto_m', 2.60)} m")

    st.markdown("""
    **Cultivos en Invernadero:**
    - Laterales: Tomate (variedad determinada)
    - Centro: Albahaca (para pesto y pizza)
    - Fondo: Curcuma y Jengibre (infusiones)
    - Bancal: Almacigos para trasplante
    """)

# ============================================================
# PAGINA: PRODUCCION
# ============================================================
elif pagina == "Produccion":
    st.markdown('<div class="main-header">PRODUCCION ESTIMADA</div>', unsafe_allow_html=True)

    # KPIs de produccion
    col1, col2, col3, col4 = st.columns(4)

    prod = datos.get('produccion', {}).get('produccion_estimada', {})

    with col1:
        st.metric("Verduras/Semana", f"{prod.get('total_verduras_kg_semana', 23)} kg", "Meta: 20-25 kg")
    with col2:
        st.metric("Huevos/Semana", f"{prod.get('huevos_unidades_semana', 150)} u", "Meta: 150+")
    with col3:
        st.metric("Humus/Mes", "250 kg", "De lombricompost")
    with col4:
        demanda = datos.get('produccion', {}).get('demanda_hotel_kg_semana', {})
        st.metric("Demanda Hotel", f"{demanda.get('objetivo', 20)} kg/sem", "Autoabastecido")

    st.markdown("---")

    # Grafico de produccion por categoria
    st.subheader("Produccion Semanal por Categoria")

    categorias_prod = {
        'Hojas (lechuga, espinaca)': prod.get('hojas_kg_semana', 8),
        'Cruciferas (brocoli, kale)': prod.get('cruciferas_kg_semana', 4),
        'Raices (zanahoria)': prod.get('raices_kg_semana', 5),
        'Aromaticas': prod.get('aromaticas_kg_semana', 2),
        'Tomate (invernadero)': prod.get('tomate_kg_semana', 4)
    }

    fig_prod = px.bar(
        x=list(categorias_prod.keys()),
        y=list(categorias_prod.values()),
        labels={'x': 'Categoria', 'y': 'Produccion (kg/semana)'},
        color=list(categorias_prod.keys()),
        color_discrete_sequence=['#4CAF50', '#8BC34A', '#FF9800', '#9C27B0', '#F44336']
    )
    fig_prod.update_layout(showlegend=False, height=400)

    st.plotly_chart(fig_prod, use_container_width=True)

    # Calendario de cultivos
    st.markdown("---")
    st.subheader("Ciclos de Cultivo")

    ciclos = datos.get('produccion', {}).get('cultivos_por_ciclo', {})

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Ciclo Rapido (30 dias):**")
        for cultivo in ciclos.get('rapido_30_dias', ['lechuga', 'rucula', 'rabano']):
            st.markdown(f"- {cultivo.capitalize()}")

        st.markdown("**Ciclo Medio (60 dias):**")
        for cultivo in ciclos.get('medio_60_dias', ['espinaca', 'acelga']):
            st.markdown(f"- {cultivo.capitalize()}")

    with col2:
        st.markdown("**Ciclo Largo (90+ dias):**")
        for cultivo in ciclos.get('largo_90_dias', ['brocoli', 'zanahoria']):
            st.markdown(f"- {cultivo.capitalize()}")

        st.markdown("**Permanentes:**")
        for cultivo in ciclos.get('permanente', ['romero', 'tomillo']):
            st.markdown(f"- {cultivo.capitalize()}")

# ============================================================
# PAGINA: ANIMALES
# ============================================================
elif pagina == "Animales":
    st.markdown('<div class="main-header">SISTEMA DE ANIMALES</div>', unsafe_allow_html=True)

    animales = datos.get('animales', {})

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🐔 Gallinas Ponedoras")
        gallinas = animales.get('gallinas', {})

        st.metric("Cantidad", f"{gallinas.get('cantidad', {}).get('objetivo', 25)} gallinas")
        st.metric("Produccion Huevos", f"{gallinas.get('produccion_huevos_semana', {}).get('max', 175)}/semana")

        st.markdown(f"**Sistema:** {gallinas.get('sistema', 'Pastoreo rotacional')}")

        st.markdown("**Funciones:**")
        for funcion in gallinas.get('funciones', ['control plagas', 'fertilizacion']):
            st.markdown(f"- {funcion.capitalize()}")

        st.markdown("**Alimentacion:**")
        for alimento in gallinas.get('alimentacion', ['pasto', 'azolla'])[:4]:
            st.markdown(f"- {alimento.capitalize()}")

    with col2:
        st.subheader("🐰 Conejos")
        conejos = animales.get('conejos', {})

        st.metric("Cantidad", f"{conejos.get('cantidad', {}).get('objetivo', 12)} conejos")
        st.metric("Estiercol", f"{conejos.get('produccion_estiercol_kg_mes', 30)} kg/mes")

        st.markdown(f"**Sistema:** {conejos.get('sistema', 'Jaulas moviles')}")

        st.markdown("**Funciones:**")
        for funcion in conejos.get('funciones', ['fertilizacion']):
            st.markdown(f"- {funcion.capitalize()}")

    st.markdown("---")

    # Azolla
    st.subheader("🌿 Cultivo de Azolla")
    azolla = animales.get('azolla', {})

    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Ubicacion:** {azolla.get('ubicacion', 'Estanques existentes')}")
    with col2:
        st.info(f"**Funcion:** {azolla.get('funcion', 'Alimento gallinas')}")
    with col3:
        st.info(f"**Produccion:** {azolla.get('produccion', 'Duplica biomasa cada 3-5 dias')}")

# ============================================================
# PAGINA: FINANZAS
# ============================================================
elif pagina == "Finanzas":
    st.markdown('<div class="main-header">ANALISIS FINANCIERO</div>', unsafe_allow_html=True)

    finanzas = datos['finanzas']

    # KPIs financieros
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Inversion Inicial",
            f"USD {finanzas['inversion_inicial_usd']['total']:,}",
            "Unica vez"
        )
    with col2:
        st.metric(
            "Costo Operativo",
            f"${finanzas['costos_operativos_mensual_cop']['total']/1000000:.2f}M/mes",
            "COP mensual"
        )
    with col3:
        st.metric(
            "Beneficio Neto",
            f"${finanzas['analisis']['beneficio_neto_cop']/1000000:.2f}M/mes",
            f"Payback: {finanzas['analisis']['payback_meses']} meses",
            delta_color="normal"
        )
    with col4:
        roi_anual = (finanzas['analisis']['beneficio_neto_cop'] * 12) / (finanzas['inversion_inicial_usd']['total'] * 4000) * 100
        st.metric(
            "ROI Anual",
            f"{roi_anual:.0f}%",
            "Retorno de inversion"
        )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Desglose de Inversion (USD)")

        inversion = finanzas['inversion_inicial_usd']
        inv_items = {k: v for k, v in inversion.items() if k != 'total'}

        fig_inv = px.pie(
            values=list(inv_items.values()),
            names=[k.replace('_', ' ').title() for k in inv_items.keys()],
            title=f"Total: USD {inversion['total']:,}",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_inv, use_container_width=True)

    with col2:
        st.subheader("Flujo Mensual (COP)")

        flujo_data = {
            'Concepto': ['Ahorros Hotel', 'Tour Bienestar', 'Costos Operativos', 'BENEFICIO NETO'],
            'Monto': [
                finanzas['ahorros_mensual_cop']['total'],
                finanzas['ingresos_mensual_cop']['tour_bienestar']['total'],
                -finanzas['costos_operativos_mensual_cop']['total'],
                finanzas['analisis']['beneficio_neto_cop']
            ],
            'Tipo': ['Ingreso', 'Ingreso', 'Egreso', 'Neto']
        }

        fig_flujo = px.bar(
            flujo_data,
            x='Concepto',
            y='Monto',
            color='Tipo',
            text=[f"${m/1000000:.2f}M" for m in flujo_data['Monto']],
            color_discrete_map={'Ingreso': '#4CAF50', 'Egreso': '#F44336', 'Neto': '#2196F3'}
        )
        fig_flujo.update_traces(textposition='outside')
        fig_flujo.update_layout(showlegend=True, height=400)

        st.plotly_chart(fig_flujo, use_container_width=True)

    # Proyeccion de payback
    st.markdown("---")
    st.subheader("Proyeccion de Recuperacion de Inversion")

    inversion_cop = finanzas['inversion_inicial_usd']['total'] * 4000
    beneficio_mensual = finanzas['analisis']['beneficio_neto_cop']

    meses = list(range(13))
    acumulado = [-inversion_cop + (beneficio_mensual * m * 0.7 if m < 3 else beneficio_mensual * m) for m in meses]

    fig_payback = go.Figure()

    fig_payback.add_trace(go.Scatter(
        x=meses,
        y=[a/1000000 for a in acumulado],
        mode='lines+markers',
        name='Flujo Acumulado',
        line=dict(color='#2196F3', width=3),
        fill='tozeroy',
        fillcolor='rgba(33, 150, 243, 0.1)'
    ))

    fig_payback.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Punto de Equilibrio")

    fig_payback.update_layout(
        title="Flujo de Caja Acumulado (Millones COP)",
        xaxis_title="Mes",
        yaxis_title="COP (Millones)",
        height=400
    )

    st.plotly_chart(fig_payback, use_container_width=True)

# ============================================================
# PAGINA: CRONOGRAMA
# ============================================================
elif pagina == "Cronograma":
    st.markdown('<div class="main-header">CRONOGRAMA DE IMPLEMENTACION</div>', unsafe_allow_html=True)

    cronograma = datos.get('cronograma', {})
    fases = cronograma.get('fases', [])

    # Timeline visual
    st.subheader("Linea de Tiempo")

    # Crear datos para el gantt
    gantt_data = []
    for fase in fases:
        gantt_data.append({
            'Fase': f"Fase {fase['numero']}: {fase['nombre']}",
            'Inicio': fase['fecha_inicio'],
            'Fin': fase['fecha_fin'],
            'Semana': fase['semana'],
            'Costo': fase['costo_usd']
        })

    if gantt_data:
        df_gantt = pd.DataFrame(gantt_data)

        fig_gantt = px.timeline(
            df_gantt,
            x_start='Inicio',
            x_end='Fin',
            y='Fase',
            color='Costo',
            color_continuous_scale='Greens',
            labels={'Costo': 'Costo USD'}
        )

        fig_gantt.update_layout(
            height=400,
            xaxis_title="Fecha",
            yaxis_title="",
            showlegend=True
        )

        st.plotly_chart(fig_gantt, use_container_width=True)

    # Tabla de fases
    st.markdown("---")
    st.subheader("Detalle de Fases")

    for fase in fases:
        with st.expander(f"**Fase {fase['numero']}: {fase['nombre']}** - Semana {fase['semana']} - USD {fase['costo_usd']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Fecha inicio:** {fase['fecha_inicio']}")
                st.markdown(f"**Fecha fin:** {fase['fecha_fin']}")
                st.markdown(f"**Responsable:** {fase['responsable']}")
            with col2:
                st.markdown("**Tareas:**")
                for tarea in fase['tareas']:
                    st.markdown(f"- {tarea}")

    # Resumen de costos
    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Costos por Fase")
        costos_fase = {f"F{f['numero']}: {f['nombre'][:15]}": f['costo_usd'] for f in fases}

        fig_costos = px.bar(
            x=list(costos_fase.keys()),
            y=list(costos_fase.values()),
            labels={'x': 'Fase', 'y': 'Costo (USD)'},
            color=list(costos_fase.values()),
            color_continuous_scale='Greens'
        )
        fig_costos.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig_costos, use_container_width=True)

    with col2:
        st.subheader("Resumen")
        total_semanas = cronograma.get('duracion_total_semanas', 9)
        fecha_fin = cronograma.get('fecha_operacion_plena', '2025-04-14')
        total_costo = sum(f['costo_usd'] for f in fases)

        st.metric("Duracion Total", f"{total_semanas} semanas")
        st.metric("Fecha Operacion Plena", fecha_fin)
        st.metric("Costo Total Fases", f"USD {total_costo:,}")

        st.info("""
        **Hitos Clave:**
        - Semana 2: Sistema digital operativo
        - Semana 4: Sensores + camaras activos
        - Semana 6: Animales integrados
        - Semana 9: Tour de bienestar lanzado
        """)

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p><strong>Huerta Inteligente LPET</strong> | Finca La Palma y El Tucan</p>
    <p>Dashboard generado automaticamente | Datos actualizados desde huerta_datos.json</p>
    <p style="font-size: 0.8rem;">Desarrollado con Streamlit + Plotly | 2025</p>
</div>
""", unsafe_allow_html=True)
