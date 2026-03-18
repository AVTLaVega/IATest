import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import os
from datetime import datetime, timedelta

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y MARCA (AVT)
# ==========================================
st.set_page_config(
    page_title="AVT La Vega - Inteligencia Avícola",
    layout="wide",
    page_icon="🐔",
    initial_sidebar_state="expanded"
)

# Estilo CSS Avanzado para diseño Negro, Blanco y Amarillo
st.markdown("""
<style>
    /* Fondo principal y texto general */
    .stApp { background-color: #FFFFFF; color: #000000; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Barra Lateral (SIDEBAR) - Fondo Negro con Borde Amarillo */
    [data-testid="stSidebar"] {
        background-color: #000000; 
        border-right: 4px solid #FFD700;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    [data-testid="stSidebar"] .stSlider > label { color: #FFD700 !important; font-weight: bold; }

    /* Tarjetas Métricas (KPIs) */
    div[data-testid="stMetricValue"] { color: #000000; font-weight: bold; font-size: 2.5rem; }
    div[data-testid="stMetricLabel"] { color: #555555; font-size: 1.1rem; }
    div[data-testid="stMetricDelta"] { font-weight: bold; }
    
    /* Botones y Sliders - Toque AVT */
    div.stButton > button:first-child { 
        background-color: #FFD700; color: black; border: 2px solid black;
        font-weight: bold; width: 100%; border-radius: 10px; padding: 10px;
    }
    div.stButton > button:first-child:hover { background-color: #000000; color: #FFD700; border: 2px solid #FFD700; }
    
    /* Títulos y Subtítulos */
    h1 { color: #000000 !important; font-weight: 800; border-bottom: 2px solid #FFD700; padding-bottom: 10px;}
    h2, h3 { color: #111111 !important; margin-top: 20px;}

    /* Contenedores visuales para secciones */
    .st_box { border: 1px solid #EEEEEE; padding: 20px; border-radius: 15px; background-color: #FAFAFA; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }

    /* Estilo para el pie de página */
    .footer { font-style: italic; color: grey; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SECCIÓN: BARRA LATERAL (Logo y Controles)
# ==========================================
# A. Intentar cargar el logo localmente desde el repositorio de GitHub
try:
    if os.path.exists("logo.png"):
        img = Image.open("logo1.png")
        st.sidebar.image(img, use_container_width=True)
    else:
        st.sidebar.warning("⚠️ Sube 'logo.png' a tu GitHub")
except Exception as e:
    st.sidebar.error("Error al cargar imagen")

st.sidebar.markdown("---")
st.sidebar.header("🕹️ Centro de Control Interactivo")
st.sidebar.markdown("Mueve los controles para simular diferentes escenarios de la granja.")

# B. Selectores de Galpón y Día (Core Interactividad)
# 3 Galpones de Engorde y 1 de Ponedoras
lista_galpones = ["Galpón Engorde 1 (Lote A)", "Galpón Engorde 2 (Lote B)", "Galpón Engorde 3 (Lote C)", "Galpón Ponedoras 1"]
galpon = st.sidebar.selectbox("Seleccionar Galpón", lista_galpones)

# Día del Ciclo (diferente rango si es engorde o ponedora)
is_ponedora = "Ponedoras" in galpon
max_dias = 400 if is_ponedora else 45
dia_ciclo = st.sidebar.slider("Día del Ciclo Productivo", 1, max_dias, 25 if not is_ponedora else 150)

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Parámetros de Simulación Manual")
st.sidebar.markdown("<small>Ajusta estos valores para ver el impacto en tiempo real.</small>", unsafe_allow_html=True)

# C. Sliders para editar KPIs manualmente
# Usamos el día del ciclo para dar valores iniciales lógicos
if not is_ponedora:
    peso_base = (dia_ciclo / 45.0) * 2.8
    peso_sim = st.sidebar.slider("Peso Promedio (kg)", 0.1, 4.0, float(peso_base), step=0.01)
    fcr_base = 1.6 - (dia_ciclo * 0.002)
    fcr_sim = st.sidebar.slider("FCR (Conversión)", 1.20, 2.50, float(fcr_base), step=0.01)
else:
    # Ponedoras: Peso es más estable, FCR es diferente
    peso_sim = st.sidebar.slider("Peso Promedio (kg)", 1.5, 3.0, 2.2, step=0.01)
    fcr_sim = st.sidebar.slider("FCR (Conversión x Docena)", 1.80, 3.00, 2.1, step=0.01)

temperatura_sim = st.sidebar.slider("Temperatura (°C)", 10, 40, 24)
poblacion_sim = st.sidebar.number_input("Aves Activas", 1000, 50000, 15000, step=100)

st.sidebar.markdown("---")
st.sidebar.info("**Avícola TecnoCampo de La Vega**\n\n*Formando jóvenes, transformando el campo.*")


# ==========================================
# 3. LÓGICA DE SIMULACIÓN DE DATOS (Fake IA Dinámica)
# ==========================================
# Usamos los valores de los sliders para generar datos con un poco de ruido para el dashboard
np.random.seed(dia_ciclo) # Para que sea reproducible por día

# Generar datos históricos (curva) basados en el día seleccionado
dias_hist = np.arange(1, dia_ciclo + 1)
peso_hist = (dias_hist / max_dias) * peso_sim + np.random.normal(0, 0.02, len(dias_hist))
temp_hist = temperatura_sim + np.random.normal(0, 1, len(dias_hist))

# Mortalidad acumulada simulada (0.5% max)
mortalidad_acumulada = int(poblacion_sim * (0.005 * (dia_ciclo / max_dias)))

# ==========================================
# 4. CUERPO PRINCIPAL (DASHBOARD)
# ==========================================
# Header Principal
st.title("🐔 AVT La Vega - Panel de Control Inteligente")
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.write(f"### Monitoreo en Tiempo Real: **{galpon}**")
with col_h2:
    st.markdown(f"#### Día del Ciclo: <span style='color:#CCAC00; font-weight:bold'>{dia_ciclo}</span>", unsafe_allow_html=True)

st.markdown("---")

# A. KPIs Principales (Con valores de los Sliders)
with st.container():
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        st.metric("Aves Activas", f"{poblacion_sim:,}", f"-{mortalidad_acumulada} bajas acum.")
    with k2:
        st.metric("Peso Promedio", f"{peso_sim:.2f} kg", "+0.09 kg hoy", delta_color="normal")
    with k3:
        # Lógica de color de temperatura
        delta_temp = temperatura_sim - 23
        delta_color = "inverse" if abs(delta_temp) > 3 else "normal"
        st.metric("Temperatura Galpón", f"{temperatura_sim:.1f} °C", f"{delta_temp:+.1f} °C vs. ópt.", delta_color=delta_color)
    with k4:
        # Lógica de FCR
        st.metric("Conversión FCR (Sim.)", f"{fcr_sim:.2f}", "-0.04 vs est.", delta_color="inverse")

st.markdown("---")

# B. Sección ROI: Interactividad para Inversores
# ==========================================
with st.container():
    st.markdown('<div class="st_box">', unsafe_allow_html=True)
    st.subheader("📈 Sección para Inversores: Proyección de Retorno de Inversión (ROI)")
    st.markdown("Ajusta los parámetros para ver cómo la tecnología de AVT incrementa la rentabilidad anual.")
    
    col_roi_controls, col_roi_chart = st.columns([1, 2])
    
    with col_roi_controls:
        capacidad_granja = st.number_input("Cantidad Total de Aves", 10000, 200000, 50000, step=1000)
        costo_alimento_kg = st.number_input("Costo Alimento (USD/kg)", 0.20, 0.60, 0.38)
        
        st.markdown("**Beneficios Simulados por IA**")
        mejora_fcr_ia = st.slider("% Mejora FCR (IA)", 1.0, 10.0, 4.0, step=0.1)
        reduccion_mortalidad_ia = st.slider("% Reducción Mortalidad (IA)", 0.2, 5.0, 1.8, step=0.1)
        
        # Cálculos de Ahorro (Simulación Anual x 6 ciclos de engorde)
        # Supuesto: Ave promedio consume 4.2kg para llegar a peso mercado
        alimento_total_año = capacidad_granja * 4.2 * 6
        ahorro_alimento_usd = alimento_total_año * (mejora_fcr_ia / 100) * costo_alimento_kg
        
        aves_salvadas_año = capacidad_granja * 6 * (reduccion_mortalidad_ia / 100)
        ahorro_mortalidad_usd = aves_salvadas_año * 2.5 # Valor mercado promedio de ave
        
        ahorro_anual_total = ahorro_alimento_usd + ahorro_mortalidad_usd
        
        st.success(f"**Ahorro Anual Estimado: ${ahorro_anual_total:,.2f} USD**")
        st.caption(f"Incluye mejora alimenticia (${ahorro_alimento_usd:,.0f}) y reducción de bajas (${ahorro_mortalidad_usd:,.0f}).")

    with col_roi_chart:
        # Gráfica Plotly de crecimiento de ahorro mensual
        meses = [f"Mes {i}" for i in range(1, 13)]
        ahorro_acumulado = [ahorro_anual_total * (i/12) for i in range(1, 13)]
        
        fig_roi = px.area(x=meses, y=ahorro_acumulado, title="Crecimiento del Ahorro Acumulado (USD/año)", 
                          labels={'x': 'Tiempo', 'y': 'Ahorro (USD)'},
                          color_discrete_sequence=['#FFD700']) # Amarillo AVT
        fig_roi.update_layout(plot_bgcolor='white', paper_bgcolor='white', xaxis_title=None)
        st.plotly_chart(fig_roi, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# C. Sección de Diagnóstico con Imágenes Dinámicas
# ==========================================
st.subheader("🧠 Diagnóstico Predictivo y Visión Artificial (Simulación)")
st.markdown("Esta sección demuestra cómo la IA analiza la salud y el entorno de las aves.")

col_diag1, col_diag2 = st.columns([2, 1])

# Lógica de Diagnóstico basada en los Sliders
diagnostico = "Cargando..."
imagen_diag = None
mensaje_alerta = ""
color_diag = "black"

# Lógica simple de simulación de IA
if temperatura_sim > 32:
    diagnostico = "⚠️ Alerta Amarilla: Estrés Térmico (Calor Excesivo)"
    imagen_diag = "alerta_ambiental.jpg"
    mensaje_alerta = "Ajustar ventilación y nebulizadores inmediatamente. Aves jadeando detectadas por cámara."
    color_diag = "#CCAC00" # Amarillo oscuro
elif fcr_sim > (fcr_base + 0.2): # FCR es mucho más alto que el simulado base
    diagnostico = "⚠️ Alerta Naranja: Posible Cuadro Respiratorio / Newcastle"
    imagen_diag = "enfermo_respiratorio.jpg"
    mensaje_alerta = "Alta variabilidad en consumo de alimento y baja actividad detected. Sospecha de enfermedad. Aislamiento recomendado."
    color_diag = "orange"
else:
    diagnostico = "✅ Estado: Saludable y Normal"
    imagen_diag = "saludable.jpg"
    mensaje_alerta = "Parámetros óptimos. Curva de crecimiento según el estándar AVT La Vega."
    color_diag = "green"

with col_diag1:
    st.markdown(f"**Análisis de IA:** <span style='color:{color_diag};font-weight:bold;font-size:large'>{diagnostico}</span>", unsafe_allow_html=True)
    st.write(f"*Recomendación:* {mensaje_alerta}")
    st.markdown("#### Histórico de Peso y Temperatura (Días transcurridos)")
    
    # Gráfica dinámica usando los datos históricos
    chart_data = pd.DataFrame({
        'Día': dias_hist,
        'Peso (kg)': peso_hist,
        'Temp (°C)': temp_hist
    })
    
    st.line_chart(chart_data, x='Día', y=['Peso (kg)', 'Temp (°C)'], color=["#FFD700", "#333333"])

with col_diag2:
    st.markdown("#### Estado Visual Simulado")
    
    # Intentar cargar la imagen de diagnóstico dinámica
    try:
        if os.path.exists(imagen_diag):
            st.image(Image.open(imagen_diag), caption=f"Simulación visual de {diagnostico}", use_container_width=True)
        else:
            st.warning(f"Sube la imagen '{imagen_diag}' a GitHub para la demo visual.")
    except Exception as e:
        st.error("Error al cargar la imagen de diagnóstico.")

# ==========================================
# 5. PIE DE PÁGINA (Footer)
# ==========================================
st.markdown("---")
st.markdown(f"<div class='footer'>Avícola TecnoCampo de La Vega - {datetime.now().year}<br>Tecnología Avanzada para la Agricultura del Futuro.<br>Formando jóvenes, transformando el campo.</div>", unsafe_allow_html=True)
