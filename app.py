import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# ==========================================
# CONFIGURACIÓN DE PÁGINA Y MARCA (Negro, Blanco, Amarillo)
# ==========================================
st.set_page_config(page_title="AVT La Vega - Dashboard IA", layout="wide", page_icon="🐔")

# Estilo CSS para forzar colores de marca y hover en amarillo
st.markdown("""
<style>
    /* Color de fondo principal y texto */
    .stApp { background-color: #FFFFFF; color: #000000; }
    
    /* Personalización de la barra lateral (SIDEBAR) */
    [data-testid="stSidebar"] {
        background-color: #000000; /* Fondo negro para la barra lateral */
        border-right: 2px solid #FFD700; /* Borde amarillo derecho */
    }
    [data-testid="stSidebar"] * { color: #FFFFFF !important; } /* Texto blanco en sidebar */

    /* Tarjetas Métricas */
    div[data-testid="stMetricValue"] { color: #000000; font-weight: bold; }
    div[data-testid="stMetricLabel"] { color: #000000; }
    
    /* Botones y Sliders - Toque Amarillo */
    div.stButton > button:first-child { background-color: #FFD700; color: black; border-color: black;}
    div.stButton > button:first-child:hover { background-color: #CCAC00; color: black; border-color: black;}
    
    /* Texto en general de la app */
    h1, h2, h3, h4, .stMarkdown { color: #000000 !important; }

    /* Estilo para el pie de página */
    .footer { font-style: italic; color: grey; text-align: center; margin-top: 30px;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SECCIÓN: BARRA LATERAL (Logo y Controles)
# ==========================================
# Reemplazar con el enlace directo del logo subido
URL_LOGO_AVT = "https://i.imgur.com/83pM4A7.png"

# Mostrar logo en la sidebar
st.sidebar.image(URL_LOGO_AVT, use_column_width=True)
st.sidebar.markdown("---")
st.sidebar.header("🕹️ Controles de la Granja")

# Selector de Galpón
galpon = st.sidebar.selectbox("Seleccionar Galpón", ["Galpón 1 (Pollos de Engorde)", "Galpón 2 (Ponedoras)"])

# Selector de Día del Ciclo
dia_ciclo = st.sidebar.slider("Día del Ciclo Productivo", 1, 45, 25)

st.sidebar.markdown("---")
st.sidebar.markdown("**Avícola TecnoCampo de La Vega**")
st.sidebar.markdown("*Formando jóvenes, transformando el campo.*")


# ==========================================
# LÓGICA DE SIMULACIÓN DE DATOS (Fake IA)
# ==========================================
# Usamos el día del ciclo para generar datos realistas
factor_crecimiento = dia_ciclo / 45.0
poblacion_inicial = 10000
mortalidad_simulada = (1 - (0.005 * factor_crecimiento)) # Simulamos mortalidad del 0.5% max
poblacion_actual = int(poblacion_inicial * mortalidad_simulada)

# Peso promedio simulado (kg) con ruido aleatorio
peso_promedio = (factor_crecimiento * 2.5) + (np.random.normal(0, 0.05))
temperatura_actual = 22 + (5 * np.sin(dia_ciclo / 10)) + np.random.normal(0, 1) # Oscilación natural

# ==========================================
# CUERPO PRINCIPAL DEL DASHBOARD
# ==========================================
st.title("🐔 AVT La Vega - Panel de Control Inteligente")
st.markdown(f"### Estado Actual: **{galpon}** - Día del Ciclo: **{dia_ciclo}**")
st.markdown("---")

# 1. KPIs Principales con colores de marca
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    st.metric("Aves Activas (Sim.)", f"{poblacion_actual:,}", f"-{poblacion_inicial - poblacion_actual:,} bajas", delta_color="off")
with kpi_col2:
    st.metric("Peso Promedio (Sim.)", f"{peso_promedio:.2f} kg", f"+{(peso_promedio * 0.1):.2f} kg hoy", delta_color="normal")
with kpi_col3:
    st.metric("Temperatura Galpón (Sim.)", f"{temperatura_actual:.1f} °C", "+1.2 °C vs. ópt.", delta_color="off")
with kpi_col4:
    # Simulación de FCR (Tasa de Conversión Alimenticia) - Menor es mejor
    fcr_actual = 1.6 + (np.random.normal(0, 0.02))
    st.metric("Conversión FCR (Sim.)", f"{fcr_actual:.2f}", "-0.05 vs. est.", delta_color="inverse")

st.markdown("---")

# 2. SECCIÓN DE ROI - El caso de negocio para Inversores
# ==========================================
with st.expander("📈 DEMO DE RETORNO DE INVERSIÓN (ROI) - Sección para Inversores", expanded=True):
    st.markdown("#### ¿Cuánto ahorra tu granja con nuestra IA?")
    st.markdown("Esta sección demuestra el impacto financiero de reducir la mortalidad y mejorar la eficiencia alimenticia mediante el monitoreo de IA de AVT La Vega.")
    
    col_roi_controls, col_roi_chart = st.columns([1, 2])
    
    with col_roi_controls:
        capacidad_granja = st.number_input("Aves por ciclo", 10000, 100000, 20000)
        costo_alimento_kg = st.number_input("Costo Alimento (USD/kg)", 0.20, 0.50, 0.35)
        reduccion_mortalidad_ia = st.slider("% Reducción de Mortalidad (IA)", 0.5, 5.0, 1.5)
        mejora_fcr_ia = st.slider("% Mejora de Conversión Alimenticia (IA)", 1.0, 10.0, 3.0)
        
        # Cálculos de Ahorro Simulados
        # Supuestos: Aves consumen ~3.5kg para llegar a 2.5kg
        aves_salvadas = int(capacidad_granja * (reduccion_mortalidad_ia / 100))
        alimento_ahorrado = capacidad_granja * 3.5 * (mejora_fcr_ia / 100)
        ahorro_anual_estimado = (aves_salvadas * 2) + (alimento_ahorrado * costo_alimento_kg) # Estimación simplificada x 6 ciclos/año
        
        st.success(f"**Ahorro Anual Estimado: ${ahorro_anual_estimado:,.2f} USD**")

    with col_roi_chart:
        # Gráfica de barras de ahorro anual vs. inversión estimada
        datos_roi = pd.DataFrame({
            'Categoría': ['Ahorro Mortalidad (USD/año)', 'Ahorro Alimento (USD/año)', 'Inversión IA Anual (USD/año)'],
            'Monto': [aves_salvadas * 2, alimento_ahorrado * costo_alimento_kg, 1500]
        })
        fig_roi = px.bar(datos_roi, x='Categoría', y='Monto', color='Categoría',
                          color_discrete_sequence=['#CCAC00', '#FFD700', 'black'], # Usando tonos de amarillo y negro
                          title="Comparativa Ahorro vs. Inversión (Simulado)")
        st.plotly_chart(fig_roi, use_container_width=True)

st.markdown("---")

# 3. Sección de Diagnóstico (IA)
st.header("🧠 Diagnóstico Predictivo de Salud (Simulación de IA)")

col_diag1, col_diag2 = st.columns(2)

with col_diag1:
    st.markdown("#### Selección de Síntomas Detectados (Día actual)")
    sintomas = st.multiselect("¿Qué síntomas observan los sensores/granjero?", ["Normal", "Letargo", "Dificultad Respiratoria", "Bajas repentinas", "Heces anormales", "Menor consumo agua"])

with col_diag2:
    st.markdown("#### Resultado del Modelo Predictivo (IA Sim.)")
    
    if st.button("Ejecutar Análisis de IA"):
        with st.spinner('Procesando datos del Galpón...'):
            import time
            time.sleep(1.5) # Simular tiempo de carga de IA
            
            # Lógica básica de simulación de diagnóstico
            if not síntomas or "Normal" in síntomas:
                diagnostico = "✅ Aves Saludables"
                confianza = "98%"
                alerta = "No se requieren acciones."
                color_diag = "green"
            elif "Bajas repentinas" in síntomas and "Heces anormales" in síntomas:
                diagnostico = "⚠️ Alerta Roja: Sospecha de Gumboro / Newcastle"
                confianza = "85%"
                alerta = "Aislamiento inmediato. Reportar a veterinario."
                color_diag = "red"
            elif "Dificultad Respiratoria" in síntomas:
                diagnostico = "⚠️ Alerta Naranja: Posible Bronquitis Infecciosa"
                confianza = "91%"
                alerta = "Revisar ventilación. Tomar muestras."
                color_diag = "orange"
            else:
                diagnostico = "⚠️ Alerta Amarilla: Estrés calórico / ambiental"
                confianza = "78%"
                alerta = "Revisar temperatura. Ajustar hidratación."
                color_diag = "yellow"
            
            # Mostrar resultado con estilos
            st.markdown(f"**Diagnóstico:** <span style='color:{color_diag};font-weight:bold;font-size:large'>{diagnostico}</span>", unsafe_allow_html=True)
            st.markdown(f"**Confianza del Modelo:** `{confianza}`")
            st.markdown(f"**Acción Recomendada:** *{alerta}*")

st.markdown("---")

# 4. Pie de página
st.markdown("<div class='footer'>Avícola TecnoCampo de La Vega - © 2026<br>Este es un MVP de demostración para inversores.</div>", unsafe_allow_html=True)

st.caption(
    "MVP demostrativo desarrollado en Python + Streamlit. "
    "Listo para integrarse con sensores IoT, cámaras y sistemas de gestión de granja (ERP/producción)."
)
