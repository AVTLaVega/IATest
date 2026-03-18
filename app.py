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
    .stApp { background-color: #FFFFFF; color: #000000; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Barra Lateral (SIDEBAR) - Fondo Negro */
    [data-testid="stSidebar"] {
        background-color: #000000; 
        border-right: 4px solid #FFD700;
    }
    
    /* CORRECCIÓN DE COLOR: Forzar etiquetas y números en la sidebar a Blanco */
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] p, [data-testid="stSidebar"] span { 
        color: #FFFFFF !important; 
        font-weight: bold;
    }
    
    /* Corregir visibilidad de los números dentro de los inputs (cajas blancas, texto negro) */
    [data-testid="stSidebar"] input { 
        color: #000000 !important; 
        background-color: #FFFFFF !important;
    }

    /* Tarjetas Métricas (KPIs) */
    div[data-testid="stMetricValue"] { color: #000000; font-weight: bold; font-size: 2.5rem; }
    div[data-testid="stMetricLabel"] { color: #555555; font-size: 1.1rem; }
    
    /* Botones AVT */
    div.stButton > button:first-child { 
        background-color: #FFD700; color: black; border: 2px solid black;
        font-weight: bold; width: 100%; border-radius: 10px; padding: 10px;
    }
    div.stButton > button:first-child:hover { background-color: #000000; color: #FFD700; border: 2px solid #FFD700; }
    
    /* Cuadro de Reporte Ejecutivo */
    .report-box { border: 2px dashed #FFD700; padding: 20px; background-color: #FFFCEB; border-radius: 15px; color: black; }

    h1 { color: #000000 !important; font-weight: 800; border-bottom: 2px solid #FFD700; padding-bottom: 10px;}
    .footer { font-style: italic; color: grey; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. SECCIÓN: BARRA LATERAL (Logo y Controles)
# ==========================================
try:
    if os.path.exists("logo1.png"):
        st.sidebar.image(Image.open("logo1.png"), use_container_width=True)
except: pass

st.sidebar.markdown("---")
st.sidebar.header("🕹️ Centro de Control")

# Selectores de Galpón
lista_galpones = ["Galpón Engorde 1", "Galpón Engorde 2", "Galpón Engorde 3", "Galpón Ponedoras 1"]
galpon = st.sidebar.selectbox("Seleccionar Galpón", lista_galpones)

is_ponedora = "Ponedoras" in galpon
max_dias = 400 if is_ponedora else 45
dia_ciclo = st.sidebar.slider("Día del Ciclo Productivo", 1, max_dias, 25)

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Parámetros en Tiempo Real")

# Aves Activas (Input numérico corregido)
poblacion_sim = st.sidebar.number_input("Aves Activas", 1000, 100000, 15000, step=100)

# Sliders de simulación
if not is_ponedora:
    peso_base = (dia_ciclo / 45.0) * 2.8
    peso_sim = st.sidebar.slider("Peso Promedio (kg)", 0.1, 4.0, float(peso_base), step=0.01)
    fcr_sim = st.sidebar.slider("FCR (Conversión)", 1.20, 2.50, 1.62, step=0.01)
else:
    peso_sim = st.sidebar.slider("Peso Promedio (kg)", 1.5, 3.0, 2.2, step=0.01)
    fcr_sim = st.sidebar.slider("FCR (Conversión)", 1.80, 3.00, 2.1, step=0.01)

temperatura_sim = st.sidebar.slider("Temperatura (°C)", 10, 40, 24)

st.sidebar.markdown("---")
st.sidebar.info("**AVT La Vega**\n\n*Formando jóvenes, transformando el campo.*")

# ==========================================
# 3. LÓGICA DE SIMULACIÓN DE DATOS
# ==========================================
np.random.seed(dia_ciclo)
dias_hist = np.arange(1, dia_ciclo + 1)
peso_hist = (dias_hist / max_dias) * peso_sim + np.random.normal(0, 0.02, len(dias_hist))
temp_hist = temperatura_sim + np.random.normal(0, 1, len(dias_hist))
mortalidad_acum = int(poblacion_sim * (0.004 * (dia_ciclo / max_dias)))

# ==========================================
# 4. CUERPO PRINCIPAL
# ==========================================
st.title("🐔 AVT La Vega - Panel Inteligente")
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.write(f"### Monitoreo: **{galpon}**")
with col_h2:
    st.markdown(f"#### Día: <span style='color:#CCAC00; font-weight:bold'>{dia_ciclo}</span>", unsafe_allow_html=True)

# KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("Aves Activas", f"{poblacion_sim:,}", f"-{mortalidad_acum} bajas")
k2.metric("Peso Promedio", f"{peso_sim:.2f} kg", "+0.08 kg hoy")
k3.metric("Temperatura", f"{temperatura_sim:.1f} °C", "Normal")
k4.metric("Moneda", "COP", delta="Peso Colombiano")

st.markdown("---")

# SECCIÓN: VIDEO DE MONITOREO (SHORTS)
# ==========================================
col_vid, col_txt = st.columns([1.2, 1])
with col_vid:
    st.subheader("📹 Visión Artificial en Vivo")
    # URL de Shorts adaptada para embeber
    video_url = "https://www.youtube.com/embed/U_it0f88v-k"
    st.components.v1.iframe(video_url, height=500)
with col_txt:
    st.markdown("#### Análisis de Comportamiento IA")
    st.write("Detección de patrones en tiempo real:")
    st.success("✅ Actividad en comederos: Normal")
    st.success("✅ Uniformidad del lote: 92%")
    st.warning("⚠️ Alerta: Agrupamiento detectado en Sector Sur")
    st.info("💡 IA sugiere: Revisar temperatura de criadoras.")

st.markdown("---")

# SECCIÓN ROI (COP - PESOS COLOMBIANOS)
# ==========================================
st.subheader("📈 Proyección Financiera (COP)")
c_roi1, c_roi2 = st.columns([1, 2])
with c_roi1:
    st.markdown("**Calculadora de Rentabilidad**")
    # Input libre para costo de alimento en COP
    costo_alimento_cop = st.number_input("Costo Alimento (COP/kg)", value=3200, step=50)
    mejora_fcr = st.slider("% Eficiencia IA", 1.0, 10.0, 4.2)
    
    # Cálculo Anual (6 ciclos)
    ahorro_anual = (poblacion_sim * 4.2 * (mejora_fcr/100)) * costo_alimento_cop * 6
    st.subheader(f"Ahorro Anual Proyectado:")
    st.title(f"${ahorro_anual:,.0f}")
    st.caption("Cifras calculadas en Pesos Colombianos (COP).")

with c_roi2:
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    ahorro_mes = [ahorro_anual * (i/12) for i in range(1, 13)]
    fig_roi = px.area(x=meses, y=ahorro_mes, title="Crecimiento de Rentabilidad Acumulada", color_discrete_sequence=['#FFD700'])
    st.plotly_chart(fig_roi, use_container_width=True)

st.markdown("---")

# SECCIÓN: DIAGNÓSTICO E IMÁGENES
# ==========================================
st.subheader("🧠 Diagnóstico de Salud con Imágenes")
cd1, cd2 = st.columns([2, 1])

# Lógica IA
if temperatura_sim > 32:
    diag, img_p, col_p = "⚠️ Estrés Térmico", "alerta_ambiental.jpg", "orange"
elif fcr_sim > 1.8:
    diag, img_p, col_p = "⚠️ Sospecha de Enfermedad", "enfermo_respiratorio.jpg", "red"
else:
    diag, img_p, col_p = "✅ Aves Saludables", "saludable.jpg", "green"

with cd1:
    st.markdown(f"#### Estado: <span style='color:{col_p}'>{diag}</span>", unsafe_allow_html=True)
    st.line_chart(pd.DataFrame({'Día': dias_hist, 'Peso': peso_hist}).set_index('Día'))

with cd2:
    try:
        if os.path.exists(img_p):
            st.image(Image.open(img_p), caption=f"Vista IA: {diag}", use_container_width=True)
        else:
            st.info(f"Vista previa de cámara: {diag}")
    except: pass

st.markdown("---")

# SECCIÓN: REPORTE EJECUTIVO (PDF SIMULADO)
# ==========================================
if st.button("📑 Generar Reporte Ejecutivo"):
    st.markdown('<div class="report-box">', unsafe_allow_html=True)
    st.markdown(f"### REPORTE DE DESEMPEÑO - AVT LA VEGA")
    st.write(f"**Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    st.write(f"**Unidad:** {galpon} | **Día:** {dia_ciclo}")
    st.markdown("---")
    r1, r2 = st.columns(2)
    r1.write(f"**Aves:** {poblacion_sim:,}")
    r1.write(f"**Peso:** {peso_sim:.2f} kg")
    r2.write(f"**FCR:** {fcr_sim}")
    r2.write(f"**Ahorro Ciclo:** ${ (ahorro_anual/6):,.0f} COP")
    st.markdown("---")
    st.write("**Análisis Final:** El lote se encuentra en parámetros productivos óptimos. La IA no recomienda cambios en la dieta actual.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f"<div class='footer'>Avícola TecnoCampo de La Vega - {datetime.now().year}</div>", unsafe_allow_html=True)
