app.py
import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

# -----------------------------
# CONFIGURACIÓN GENERAL
# -----------------------------
st.set_page_config(
    page_title="Plataforma IA para Granjas Avícolas",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# FUNCIONES DE SIMULACIÓN
# -----------------------------

def simulate_environmental_data(galpon: str, day_of_cycle: int, hours: int = 24):
    """Simula datos ambientales (temperatura y humedad) para las últimas 24 horas."""
    now = datetime.now()
    timestamps = [now - timedelta(hours=h) for h in reversed(range(hours))]

    # Base según galpón (ejemplo: algunos galpones son un poco más cálidos)
    galpon_offset = {
        "Galpón 1": 0.0,
        "Galpón 2": 0.5,
        "Galpón 3": -0.3,
    }.get(galpon, 0.0)

    # Tendencia suave según el día del ciclo (aves más grandes generan más calor)
    day_factor = min(day_of_cycle / 42, 1.0)  # suponiendo ciclo de 42 días
    base_temp = 21 + 1.5 * day_factor + galpon_offset

    # Patrón diario (más caliente al mediodía)
    temps = []
    hums = []
    for i, ts in enumerate(timestamps):
        hour = ts.hour
        diurnal_variation = 2 * np.sin((hour - 12) / 24 * 2 * np.pi)  # pico a mediodía
        noise = np.random.normal(0, 0.6)
        temp = base_temp + diurnal_variation + noise
        temp = np.round(temp, 1)

        # Humedad inversamente correlacionada de forma suave
        base_hum = 65 - 0.7 * (temp - 21) + np.random.normal(0, 2.0)
        base_hum = float(np.clip(base_hum, 45, 85))

        temps.append(temp)
        hums.append(round(base_hum, 1))

    df = pd.DataFrame({
        "Fecha/Hora": timestamps,
        "Temperatura (°C)": temps,
        "Humedad (%)": hums
    })
    return df


def simulate_population(galpon: str, day_of_cycle: int):
    """Simula población actual con mortalidad acumulada."""
    # Supongamos un número inicial de aves distinto por galpón
    initial_pop = {
        "Galpón 1": 15000,
        "Galpón 2": 12000,
        "Galpón 3": 10000,
    }.get(galpon, 12000)

    # Mortalidad esperada ~3-4% al final del ciclo
    expected_mortality_rate = 0.035
    # Mortalidad acumulada proporcional al día
    mortality_so_far = expected_mortality_rate * (day_of_cycle / 42) * initial_pop
    # Agregar algo de ruido
    mortality_so_far += np.random.normal(0, initial_pop * 0.001)
    mortality_so_far = max(0, mortality_so_far)
    current_population = int(initial_pop - mortality_so_far)

    return initial_pop, current_population


def simulate_weight_curve(day_of_cycle: int, days_total: int = 42):
    """Simula curva de peso real vs óptimo (gramos)."""
    days = np.arange(1, days_total + 1)

    # Curva logística simplificada para peso óptimo
    L = 2600  # peso asintótico en gramos
    k = 0.18
    x0 = 24
    optimal_weight = L / (1 + np.exp(-k * (days - x0)))

    # Peso real: algo de desviación + impacto del manejo (día del ciclo)
    management_factor = np.random.normal(0.0, 0.03)  # +-3%
    real_weight = optimal_weight * (1 + management_factor)

    # Ruido adicional
    real_weight = real_weight + np.random.normal(0, 40, size=len(real_weight))
    real_weight = np.maximum(real_weight, 0)

    df = pd.DataFrame({
        "Día del ciclo": days,
        "Peso Óptimo (g)": np.round(optimal_weight, 1),
        "Peso Promedio Real (g)": np.round(real_weight, 1)
    })

    # Peso actual en el día seleccionado (interpolado si fuese necesario)
    day_idx = min(max(day_of_cycle, 1), days_total) - 1
    current_weight = df.loc[day_idx, "Peso Promedio Real (g)"]

    # FCR simulada: mejora con buen peso, empeora con desviaciones
    base_fcr = 1.65  # valor de referencia
    deviation = (current_weight - df.loc[day_idx, "Peso Óptimo (g)"]) / df.loc[day_idx, "Peso Óptimo (g)"]
    fcr = base_fcr * (1 + deviation * -0.5)  # si el peso está por encima, FCR algo mejor
    fcr = float(np.clip(fcr + np.random.normal(0, 0.03), 1.45, 1.9))

    return df, float(current_weight), fcr


def simulate_vision_analysis(current_population: int):
    """Simula visión artificial: conteo de aves y distribución de comportamiento."""
    # Conteo detectado: error de +/- 2-4%
    error_rate = np.random.uniform(-0.03, 0.03)
    detected = int(current_population * (1 + error_rate))

    # Distribución de comportamiento mediante Dirichlet
    labels = ["Comiendo", "Bebiendo", "Inactivas"]
    alpha = np.array([3, 2, 2])  # ligeramente más aves comiendo
    probs = np.random.dirichlet(alpha)
    percents = np.round(probs * 100, 1)

    df_behaviour = pd.DataFrame({
        "Comportamiento": labels,
        "Porcentaje (%)": percents
    })

    return detected, df_behaviour


def simulate_health_risk(temp_mean: float, hum_mean: float, symptoms: list):
    """Simula diagnóstico de enfermedades basado en reglas sencillas."""
    symptoms = [s.lower() for s in symptoms]

    score_newcastle = 0.0
    score_bronquitis = 0.0
    score_healthy = 0.5  # punto de partida

    # Reglas basadas en síntomas
    if "tos" in symptoms or "secreción nasal" in symptoms:
        score_bronquitis += 0.8
        score_newcastle += 0.4
    if "letargo" in symptoms or "debilidad" in symptoms:
        score_newcastle += 0.7
    if "pérdida de apetito" in symptoms:
        score_newcastle += 0.5
        score_bronquitis += 0.3
    if "dificultad respiratoria" in symptoms:
        score_bronquitis += 0.7
    if len(symptoms) == 0:
        score_healthy += 0.8

    # Reglas ambientales
    if temp_mean > 25:
        score_bronquitis += 0.2
    if temp_mean < 17:
        score_newcastle += 0.2
    if hum_mean > 80:
        score_bronquitis += 0.2
    if 50 <= hum_mean <= 70 and 18 <= temp_mean <= 24 and len(symptoms) == 0:
        score_healthy += 0.5

    scores = {
        "Newcastle": score_newcastle,
        "Bronquitis Infecciosa": score_bronquitis,
        "Aves Saludables": score_healthy
    }

    # Evitar todos ceros
    total = sum(scores.values())
    if total == 0:
        scores = {k: 1 for k in scores}
        total = sum(scores.values())

    probs = {k: v / total for k, v in scores.items()}
    # Seleccionar diagnóstico con mayor probabilidad
    diagnosis = max(probs, key=probs.get)
    confidence = round(probs[diagnosis] * 100, 1)

    return diagnosis, confidence, probs


# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("Configuración del Lote")

galpon = st.sidebar.selectbox(
    "Seleccionar galpón",
    options=["Galpón 1", "Galpón 2", "Galpón 3"],
    index=0
)

day_of_cycle = st.sidebar.slider(
    "Día del ciclo de engorde",
    min_value=1,
    max_value=42,
    value=21
)

st.sidebar.markdown("---")
st.sidebar.subheader("Supuestos del MVP")
st.sidebar.markdown(
    """
Este panel utiliza **datos simulados** para ilustrar cómo la IA 
puede integrarse en granjas avícolas sin alterar la operación actual.
"""
)

# -----------------------------
# ENCABEZADO
# -----------------------------
st.title("Plataforma de Inteligencia Artificial para Granjas Avícolas")

st.markdown(
    """
**Esta plataforma demuestra cómo la IA reduce la mortalidad en hasta un 15% 
e incrementa la eficiencia alimenticia (FCR) en hasta un 8%,** 
mediante monitoreo en tiempo real, alertas tempranas y diagnóstico predictivo 
de enfermedades a partir de datos ambientales, de peso y de comportamiento.
"""
)

st.markdown(
    f"**Lote simulado:** {galpon} · **Día del ciclo:** {day_of_cycle}"
)

# -----------------------------
# GENERACIÓN DE DATOS MOCK
# -----------------------------
env_df = simulate_environmental_data(galpon, day_of_cycle)
initial_pop, current_population = simulate_population(galpon, day_of_cycle)
weight_df, current_weight, current_fcr = simulate_weight_curve(day_of_cycle)
detected_birds, behaviour_df = simulate_vision_analysis(current_population)

temp_mean = float(env_df["Temperatura (°C)"].mean())
hum_mean = float(env_df["Humedad (%)"].mean())

# Alerta de temperatura fuera de rango óptimo
TEMP_MIN_OPT = 18
TEMP_MAX_OPT = 24
temp_out_of_range = not (TEMP_MIN_OPT <= temp_mean <= TEMP_MAX_OPT)

# Salud general básica (antes del módulo de diagnóstico)
health_status = "Estable"
health_color = "green"
if temp_out_of_range or current_fcr > 1.8:
    health_status = "En riesgo moderado"
    health_color = "orange"
if temp_out_of_range and current_fcr > 1.85:
    health_status = "Alerta crítica"
    health_color = "red"

# -----------------------------
# KPIs PRINCIPALES
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Población Actual",
        value=f"{current_population:,}".replace(",", "."),
        delta=f"-{initial_pop - current_population} aves"
    )

with col2:
    st.metric(
        label="Peso Promedio Actual",
        value=f"{current_weight:.0f} g",
        help="Peso promedio estimado para el día actual del ciclo."
    )

with col3:
    st.metric(
        label="Temperatura Promedio Últimas 24h",
        value=f"{temp_mean:.1f} °C",
        delta=f"Hum: {hum_mean:.0f}%",
        help="Temperatura y humedad medias en el galpón."
    )

with col4:
    st.metric(
        label="Estado de Salud Global (IA)",
        value=health_status,
    )
    if health_color == "red":
        st.error("Riesgo elevado. Se recomiendan acciones correctivas inmediatas.")
    elif health_color == "orange":
        st.warning("Riesgo moderado. Monitorear de cerca las condiciones.")
    else:
        st.success("Parámetros dentro de rangos esperados.")

st.markdown("---")

# -----------------------------
# MÓDULO 1: MONITOREO AMBIENTAL
# -----------------------------
st.subheader("Módulo 1: Monitoreo Ambiental en Tiempo Real")

st.markdown(
    """
Este módulo simula la **IA de alertas ambientales**, monitoreando temperatura y humedad
en tiempo real para reducir estrés térmico, mejorar bienestar y prevenir brotes sanitarios.
"""
)

col_env1, col_env2 = st.columns([2, 1])

with col_env1:
    st.markdown("**Histórico de Temperatura (últimas 24 horas)**")
    temp_chart_df = env_df.set_index("Fecha/Hora")[["Temperatura (°C)"]]
    st.line_chart(temp_chart_df)

with col_env2:
    st.markdown("**Distribución de Humedad**")
    st.bar_chart(env_df[["Humedad (%)"]])

if temp_out_of_range:
    st.warning(
        f"⚠️ Alerta de IA: La temperatura promedio ({temp_mean:.1f} °C) "
        f"está fuera del rango óptimo ({TEMP_MIN_OPT}–{TEMP_MAX_OPT} °C). "
        "Se sugiere ajustar ventilación, cortinas o nebulización."
    )
else:
    st.info(
        "✅ La IA indica que la temperatura promedio se mantiene dentro del rango óptimo "
        "para minimizar estrés térmico."
    )

st.markdown("---")

# -----------------------------
# MÓDULO 2: CONTROL DE PESO
# -----------------------------
st.subheader("Módulo 2: Control de Peso y Curva de Crecimiento")

st.markdown(
    """
La plataforma compara el **peso promedio real vs. la curva de referencia de la industria** 
y estima el impacto en la **Tasa de Conversión Alimenticia (FCR)** para optimizar 
costos de alimento y tiempo de salida a planta.
"""
)

col_weight1, col_weight2 = st.columns([2, 1])

with col_weight1:
    st.markdown("**Curva de Peso Promedio vs. Óptimo**")
    weight_chart_df = weight_df.set_index("Día del ciclo")
    st.area_chart(weight_chart_df)

with col_weight2:
    st.markdown("**Indicadores de Crecimiento**")
    st.metric("FCR Simulada", f"{current_fcr:.2f}")
    expected_fcr = 1.65
    delta_fcr = current_fcr - expected_fcr
    if current_fcr <= expected_fcr:
        st.success(
            f"La FCR simulada está **{abs(delta_fcr):.2f} puntos mejor** "
            f"que el objetivo ({expected_fcr:.2f})."
        )
    else:
        st.warning(
            f"La FCR simulada está **{delta_fcr:.2f} puntos por encima** del objetivo "
            f"({expected_fcr:.2f}). La IA puede sugerir ajustes de nutrición o manejo."
        )

    st.markdown(
        f"- **Peso promedio actual:** {current_weight:.0f} g\n"
        f"- **Peso óptimo esperado hoy:** "
        f"{weight_df.loc[day_of_cycle - 1, 'Peso Óptimo (g)']:.0f} g"
    )

st.markdown("---")

# -----------------------------
# MÓDULO 3: VISIÓN ARTIFICIAL (SIMULACIÓN)
# -----------------------------
st.subheader("Módulo 3: Análisis de Cámara en Tiempo Real (Simulado)")

st.markdown(
    """
En una implementación real, cámaras instaladas en el galpón alimentarían modelos de **visión artificial** 
para contar aves, detectar aglomeraciones, comportamientos anómalos y signos tempranos de estrés.
En este MVP, se simula la salida de dicho modelo.
"""
)

col_cam1, col_cam2 = st.columns([1, 2])

with col_cam1:
    st.metric("Aves Detectadas por IA (Cámara)", f"{detected_birds:,}".replace(",", "."),
              delta=f"Esperadas: {current_population:,}".replace(",", "."))

    detection_error = (detected_birds - current_population) / max(current_population, 1) * 100
    st.markdown(
        f"**Error de conteo simulado:** {detection_error:+.1f}%\n\n"
        "La precisión mejora con calibración y más datos de entrenamiento."
    )

with col_cam2:
    st.markdown("**Distribución de Comportamiento (IA de Visión)**")
    st.bar_chart(
        behaviour_df.set_index("Comportamiento")
    )

st.markdown("---")

# -----------------------------
# MÓDULO 4: DIAGNÓSTICO PREDICTIVO DE ENFERMEDADES
# -----------------------------
st.subheader("Módulo 4: Diagnóstico Predictivo de Enfermedades (Core de la IA)")

st.markdown(
    """
Este módulo simula el **core de IA de diagnóstico**, combinando síntomas observados en campo 
con datos ambientales para estimar un **diagnóstico probable** y la **confianza del modelo**.
En producción, este componente se entrenaría con históricos de mortalidad, necropsias 
y datos de laboratorio.
"""
)

col_diag1, col_diag2 = st.columns([1.4, 1])

with col_diag1:
    st.markdown("**Entrada de datos y síntomas**")

    st.markdown("Seleccione los síntomas observados en el lote:")
    symptom_options = [
        "Tos",
        "Secreción nasal",
        "Letargo",
        "Debilidad",
        "Pérdida de apetito",
        "Dificultad respiratoria"
    ]
    selected_symptoms = st.multiselect(
        "Síntomas clínicos",
        options=symptom_options,
        default=[]
    )

    st.markdown("Ajuste manualmente las condiciones medidas de campo (si difieren del promedio):")
    manual_temp = st.slider(
        "Temperatura corporal o ambiente percibida (°C)",
        min_value=15.0,
        max_value=35.0,
        value=float(round(temp_mean, 1)),
        step=0.1
    )
    manual_hum = st.slider(
        "Humedad relativa percibida (%)",
        min_value=40,
        max_value=95,
        value=int(round(hum_mean)),
        step=1
    )

    run_diagnosis = st.button("Ejecutar Diagnóstico Simulado de IA")

with col_diag2:
    st.markdown("**Salida del modelo de IA (simulado)**")

    if run_diagnosis:
        diagnosis, confidence, probs = simulate_health_risk(manual_temp, manual_hum, selected_symptoms)

        if diagnosis == "Aves Saludables":
            st.success(f"Diagnóstico probable: **{diagnosis}**")
        else:
            st.error(f"Diagnóstico probable: **{diagnosis}**")

        st.metric("Confianza estimada de la IA", f"{confidence:.1f} %")

        # Mostrar distribución de probabilidad completa
        prob_df = pd.DataFrame({
            "Diagnóstico": list(probs.keys()),
            "Probabilidad (%)": [round(v * 100, 1) for v in probs.values()]
        }).set_index("Diagnóstico")
        st.bar_chart(prob_df)

        st.markdown(
            """
**Nota:** Este resultado es una **simulación demostrativa**. 
En un entorno real, el modelo se entrenaría con datos históricos de granjas comerciales 
para alcanzar niveles de precisión clínicamente validados.
"""
        )
    else:
        st.info("Configure los síntomas y presione **'Ejecutar Diagnóstico Simulado de IA'** para ver el resultado.")

st.markdown("---")

st.caption(
    "MVP demostrativo desarrollado en Python + Streamlit. "
    "Listo para integrarse con sensores IoT, cámaras y sistemas de gestión de granja (ERP/producción)."
)