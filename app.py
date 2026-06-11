import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import datetime
import time

# 1. Configuración de la Infraestructura de la Página
st.set_page_config(page_title="Control de Escrutinio ONPE", layout="wide")

st.title("🏛️ Tablero de Control de Escrutinio Oficial (EN VIVO)")
st.caption("Filtro de precisión analítica con actualización cada 60 segundos")
st.markdown("---")

# URL del Backend de la ONPE
ONPE_API_REAL = "https://resultadosegundavuelta.onpe.gob.pe/presentacion-backend/resumen/resumenPresidencial"

st.sidebar.header("🛠️ Estado del Pipeline de Datos")

@st.cache_data(ttl=10)
def consumir_api_onpe(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://resultadosegundavuelta.onpe.gob.pe",
        "Referer": "https://resultadosegundavuelta.onpe.gob.pe/"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            try:
                return response.json(), "OK"
            except Exception:
                texto_intruso = response.text.strip()[:150]
                return None, f"Bloqueo/HTML detectado: {texto_intruso}..."
        return None, f"Error HTTP {response.status_code}"
    except Exception as e:
        return None, f"Fallo de Red: {str(e)}"

json_data, status_msg = consumir_api_onpe(ONPE_API_REAL)

# ==============================================================================
# PIPELINE HISTÓRICO REAL (PERSISTENCIA DE SESIÓN)
# ==============================================================================
# Serie cronológica indexada que incluye la validación de la meseta temporal (image_d9dd66.jpg)
if "registro_historico" not in st.session_state:
    st.session_state.registro_historico = pd.DataFrame([
        {"Hora": "09:40", "Keiko": 9032653, "Roberto": 9032092, "Diferencia Absoluta": 561},
        {"Hora": "10:00", "Keiko": 9032653, "Roberto": 9032092, "Diferencia Absoluta": 561},
        {"Hora": "12:20", "Keiko": 9033584, "Roberto": 9032662, "Diferencia Absoluta": 922},
        {"Hora": "12:30", "Keiko": 9033584, "Roberto": 9032662, "Diferencia Absoluta": 922},
        {"Hora": "13:05", "Keiko": 9033680, "Roberto": 9032774, "Diferencia Absoluta": 906},
        {"Hora": "13:12", "Keiko": 9033756, "Roberto": 9032886, "Diferencia Absoluta": 870},
        {"Hora": "13:35", "Keiko": 9034070, "Roberto": 9033211, "Diferencia Absoluta": 859},
        {"Hora": "14:40", "Keiko": 9034070, "Roberto": 9033211, "Diferencia Absoluta": 859}
    ])

# Datos de contingencia actuales basados estrictamente en image_d9dd66.jpg
total_actas = 92766
procesadas_porc = 98.236  
observadas_jee = 1623     
pendientes = 13           
corte_temporal = "11/06/2026 02:40:25 p. m."

candidatos = [
    {"nombre": "Keiko Sofía Fujimori Higuchi", "votos": 9034070, "porcentaje": 50.002},
    {"nombre": "Roberto Helbert Sánchez Palomino", "votos": 9033211, "porcentaje": 49.998}
]

# Control de Inyección Dinámica
if status_msg == "OK" and json_data:
    try:
        procesadas_porc = float(json_data.get("porcentajepros", 98.236))
        observadas_jee = int(json_data.get("totales_observadas", 1623))
        lista_api = json_data.get("resumen", json_data.get("candidatos", []))
        
        if lista_api and len(lista_api) >= 2:
            votos_k = int(str(lista_api[0].get("votos")).replace(",", ""))
            votos_r = int(str(lista_api[1].get("votos")).replace(",", ""))
            porc_k = float(lista_api[0].get("porcentaje"))
            porc_r = float(lista_api[1].get("porcentaje"))
            
            candidatos = [
                {"nombre": "Keiko Sofía Fujimori Higuchi", "votos": votos_k, "porcentaje": porc_k},
                {"nombre": "Roberto Helbert Sánchez Palomino", "votos": votos_r, "porcentaje": porc_r}
            ]
            corte_temporal = "Sincronizado en Tiempo Real"
            st.sidebar.success("📊 Sincronización Real-Time Activa.")
            
            # Guardas de consistencia para el ledger histórico dinámico
            df_actual = st.session_state.registro_historico
            if not df_actual.empty and df_actual.iloc[-1]["Keiko"] != votos_k:
                hora_actual = datetime.datetime.now().strftime("%H:%M")
                nueva_fila = pd.DataFrame([{
                    "Hora": hora_actual, 
                    "Keiko": votos_k, 
                    "Roberto": votos_r, 
                    "Diferencia Absoluta": abs(votos_k - votos_r)
                }])
                st.session_state.registro_historico = pd.concat([df_actual, nueva_fila], ignore_index=True)
                
    except Exception as e:
        st.sidebar.error(f"Estructura JSON variable: {str(e)}")
else:
    st.sidebar.warning("⚠️ Modo Contingencia Activo")
    st.sidebar.code(status_msg, language="text")

# 2. Lógica del Modelo Analítico
candidatos_ordenados = sorted(candidatos, key=lambda x: x["votos"], reverse=True)
primero = candidatos_ordenados[0]
segundo = candidatos_ordenados[1]
diferencia_actual = primero["votos"] - segundo["votos"]

# ==============================================================================
# CAPA DE PRESENTACIÓN VISUAL
# ==============================================================================

st.sidebar.info(f"Último corte cargado: {corte_temporal}")

## SECCIÓN I: MARGEN DE POSICIONES LITERALES
st.markdown("### 🥇 ESTADO DE LA CONTIENDA (VOTOS VÁLIDOS EMITIDOS)")
col_1er, col_2do = st.columns(2)

with col_1er:
    st.error("🏆 PRIMER LUGAR")
    st.markdown(f"### **Votos a Favor de {primero['nombre']}**")
    st.markdown(f"<h1 style='color: #F39C12; font-size: 38px;'>{primero['votos']:,} <span style='font-size: 20px; color: gray;'>votos ({primero['porcentaje']:.3f}%)</span></h1>", unsafe_allow_html=True)

with col_2do:
    st.info("🥈 SEGUNDO LUGAR")
    st.markdown(f"### **Votos a Favor de {segundo['nombre']}**")
    st.markdown(f"<h1 style='color: #1ABC9C; font-size: 38px;'>{segundo['votos']:,} <span style='font-size: 20px; color: gray;'>votos ({segundo['porcentaje']:.3f}%)</span></h1>", unsafe_allow_html=True)

st.markdown("---")

## SECCIÓN II: INDICADORES ESTRUCTURALES Y MARGEN DE CONTROL
st.markdown("### ⚖️ MARGEN DE CONTROL")
col_dif, col_actas = st.columns([2, 1])

with col_dif:
    st.subheader("Diferencia Absoluta de Votos")
    st.markdown(f"<p style='font-size: 48px; font-weight: bold; color: #E74C3C; margin: 0;'>{diferencia_actual:,} <span style='font-size: 20px; font-weight: normal; color: gray;'>votos de ventaja</span></p>", unsafe_allow_html=True)
    st.caption(f"Brecha matemática actual del primer lugar sobre el segundo lugar ({primero['nombre']} vs {segundo['nombre']}).")

with col_actas:
    st.metric(label="📊 Avance de Actas Contabilizadas", value=f"{procesadas_porc:.3f}%", delta=f"{total_actas:,} Totales")
    st.metric(label="📂 Actas en el JEE (Impugnadas)", value=f"{observadas_jee:,}")
    st.metric(label="⏳ Actas Pendientes de Ingreso", value=f"{pendientes:,}")

st.markdown("---")

## SECCIÓN III: ANÁLISIS GRÁFICO AVANZADO
st.markdown("### 📊 VISUALIZACIÓN ANALÍTICA DEL ESCRUTINIO")
col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    st.markdown("#### Distribución Porcentual del Voto Válido")
    df_torta = pd.DataFrame({
        "Candidato": [primero["nombre"], segundo["nombre"]],
        "Votos": [primero["votos"], segundo["votos"]]
    })
    fig_torta = px.pie(
        df_torta, values="Votos", names="Candidato",
        color="Candidato",
        color_discrete_map={primero["nombre"]: "#F39C12", segundo["nombre"]: "#1ABC9C"},
        hole=0.4
    )
    fig_torta.update_traces(texttemplate="%{percent:.3%}<br>%{value:,} votos", textinfo="percent+value")
    fig_torta.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=320)
    st.plotly_chart(fig_torta, use_container_width=True)

with col_graph2:
    st.markdown("#### 📈 Evolución Real de la Diferencia Absoluta (Brecha de Ventaja)")
    
    # Renderizado lineal del comportamiento de la brecha
    fig_linea_diff = px.line(
        st.session_state.registro_historico,
        x="Hora",
        y="Diferencia Absoluta",
        markers=True,
        text="Diferencia Absoluta",
        labels={"Diferencia Absoluta": "Margen de Votos", "Hora": "Hora del Corte"}
    )
    
    fig_linea_diff.update_traces(
        line_color="#E74C3C", 
        line_width=3, 
        marker=dict(size=10, color="#C0392B"),
        textposition="top center"
    )
    fig_linea_diff.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        height=320,
        xaxis=dict(type='category')
    )
    st.plotly_chart(fig_linea_diff, use_container_width=True)

# 4. Ciclo Automatizado de Refresco (Frecuencia: 60s)
time.sleep(60)
st.rerun()
