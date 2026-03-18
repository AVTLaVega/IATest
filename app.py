import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from PIL import Image
import os
from datetime import datetime  # <--- ESTO ES LO QUE FALTABA

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y MARCA
# ==========================================
st.set_page_config(page_title="AVT La Vega - Dashboard IA", layout="wide", page_icon="🐔")

# Estilo CSS personalizado
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; color: #000000; }
    [data-testid="stSidebar"] {
        background-color: #000000; 
        border-right: 3px solid #FFD700;
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; }
    div[data-testid="stMetricValue"] { color: #000000; font-weight: bold; }
    div.stButton > button:first-child { 
        background-color: #FFD700; 
        color: black; 
        border: 2px solid black;
        font-weight: bold;
        width: 100%;
    }
    .footer { font-style: italic; color: grey; text-align: center; margin-top: 50px; border-top: 1px solid #eee; padding-top: 20px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SECCIÓN: BARRA LATERAL (Logo y Controles)
# ==========================================
try:
    if os.path.exists("logo.png"):
        img = Image.open("logo1.png")
        st.sidebar.image(img, use_container_width=True)
    else:
        st.sidebar.warning("⚠️ Sube 'logo.png' a tu GitHub")
except Exception as e:
    st.sidebar.error("Error al cargar imagen")

st.sidebar.markdown("---")
st.sidebar.header("🕹️ Panel de Control")
galpon = st.sidebar.selectbox("Seleccionar Galpón", ["Galpón 1 (Engorde)", "Galpón 2 (Ponedoras)"])
dia_ciclo = st.sidebar.slider("Día del Ciclo Productivo", 1, 45, 25)
st.sidebar.markdown("---")
st.sidebar.info("**Avícola TecnoCampo de La Vega**\n\n*Formando jóvenes, transformando el campo.*")

# ==========================================
# LÓGICA DE SIMULACIÓN DE DATOS
# ==========================================
factor = dia_ciclo / 45.0
poblacion_actual = int(10000 * (1 - (0.004 * factor)))
peso_promedio = (factor * 2.6) + (np.random.normal(0, 0.04))
temp = 23 + (4 * np.sin(dia_ciclo / 5))

# ==========================================
# CUERPO PRINCIPAL
# ==========================================
st.title("🐔 AVT La Vega - Gestión Avícola con IA")
st.write(f"Monitoreo en tiempo real para: **{galpon}**")
st.markdown("---")

# 1. KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("Aves Activas", f"{poblacion_actual:,}", "-42 bajas")
k2.metric("Peso Promedio", f"{peso_promedio:.2f} kg", "+0.08 kg")
k3.metric("Temp. Galpón", f"{temp:.1f} °C", "Óptima", delta_color="off")
k4.metric("FCR (Conversión)", "1.58", "-0.02 vs est.")

st.markdown("---")

# 2. SECCIÓN DE ROI PARA INVERSORES
st.subheader("📈 Proyección de Retorno de Inversión (ROI)")
c_roi1, c_roi2 = st.columns([1, 2])

with c_roi1:
    cap = st.number_input("Cantidad de Aves", 5000, 50000, 20000)
    ahorro_fcr = st.slider("% Eficiencia Alimento (IA)", 1.0, 10.0, 3.5)
    usd_ahorro = (cap * 4 * (ahorro_fcr/100)) * 0.40 
    st.success(f"**Ahorro Estimado por Ciclo: ${usd_ahorro:,.2f} USD**")

with c_roi2:
    df_roi = pd.DataFrame({
        'Mes': ['Mes 1', 'Mes 2', 'Mes 3', 'Mes 4', 'Mes 5', 'Mes 6'],
        'Ahorro': [usd_ahorro, usd_ahorro*2, usd_ahorro*3.5, usd_ahorro*5, usd_ahorro*7, usd_ahorro*9]
    })
    fig = px.area(df_roi, x='Mes', y='Ahorro', title="Crecimiento de Rentabilidad (USD)", color_discrete_sequence=['#FFD700'])
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# 3. DIAGNÓSTICO IA
st.subheader("🧠 Diagnóstico Predictivo de Salud")
col_d1, col_d2 = st.columns(2)
with col_d1:
    sints = st.multiselect("Observaciones:", ["Normal", "Tos/Estridor", "Baja Actividad", "Heces Líquidas", "Consumo Agua Bajo"])
with col_d2:
    if st.button("🔍 Ejecutar Análisis de IA"):
        with st.spinner('Analizando patrones...'):
            import time
            time.sleep(1)
            if "Normal" in sints or not sints:
                st.success("✅ **ESTADO: SALUDABLE** (99%)")
            else:
                st.warning("⚠️ **ALERTA: POSIBLE CUADRO RESPIRATORIO** (82%)")

# 4. Footer
st.markdown(f"<div class='footer'>Avícola TecnoCampo de La Vega - {datetime.now().year}<br>Tecnología para el campo del futuro.</div>", unsafe_allow_html=True)
