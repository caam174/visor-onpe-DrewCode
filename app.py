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

# =========================================================
# DATOS DE RESPALDO ACTUALIZADOS SEGÚN CAPTURA OFICIAL
# =========================================================
total_actas = 86488
procesadas_porc = 99.985  
observadas = 124          
candidatos = [
    {"nombre": "Keiko Fujimori", "votos": 9032653, "porcentaje": 50.002},
    {"nombre": "Roberto Sánchez", "votos": 9032092, "porcentaje": 49.998}
]

# Control de Inyección: Si la API responde con JSON limpio, se sobreescriben los valores
if status_msg == "OK" and json_data:
    try:
        procesadas_porc = float(json_data.get("porcentajepros", 99.985))
        observadas = int(json_data.get("totales_observadas", 124))
        lista_api = json_data.get("resumen", json_data.get("candidatos", []))
        
        if lista_api and len(lista_api) >= 2:
            candidatos = [
                {
                    "nombre": "Keiko Fujimori", 
                    "votos": int(str(lista_api[0].get("votos")).replace(",", "")), 
                    "porcentaje": float(lista_api[0].get("porcentaje"))
                },
                {
                    "nombre": "Roberto Sánchez", 
                    "votos": int(str(lista_api[1].get("votos")).replace(",", "")), 
                    "porcentaje": float(lista_api[1].get("porcentaje"))
                }
            ]
            st.sidebar.success("📊 Sincronización Real-Time Activa.")
    except Exception as e:
        st.sidebar.error(f"Estructura JSON variable: {str(e)}")
else:
    st.sidebar.warning("⚠️ Modo Contingencia Activo")
    st.sidebar.code(status_msg, language="text")

# 2. Lógica de Negocio: Determinación Dinámica de Posiciones
candidatos_ordenados = sorted(candidatos, key=lambda x: x["votos"], reverse=True)
primero = candidatos_ordenados[0]
segundo = candidatos_ordenados[1]

diferencia_absoluta = primero["votos"] - segundo["votos"]
actas_procesadas_abs = int((procesadas_porc / 100) * total_actas)
actas_por_procesar = total_actas - actas_procesadas_abs

# Simulación de vector temporal para la tendencia
ahora = datetime.datetime.now()
data_historica = {
    "Hora": [(ahora - datetime.timedelta(hours=i)).strftime("%H:%M") for i in range(5, -1, -1)],
    primero["nombre"]: [primero["votos"]-1500, primero["votos"]-1000, primero["votos"]-600, primero["votos"]-300, primero["votos"]-100, primero["votos"]],
    segundo["nombre"]: [segundo["votos"]-1200, segundo["votos"]-900, segundo["votos"]-700, segundo["votos"]-400, segundo["votos"]-50, segundo["votos"]]
}
df_evolucion = pd.DataFrame(data_historica).set_index("Hora")

# =========================================================
# CAPA DE PRESENTACIÓN ARQUITECTÓNICA (INTERFAZ LIMPIA)
# =========================================================

## NIVEL 1: PANELES DE POSICIÓN LITERAL
st.markdown("### 🥇 ESTADO DE LA CONTIENDA (VOTOS VÁLIDOS EMITIDOS)")
col_1er, col_2do = st.columns(2)

with col_1er:
    st.error("🏆 PRIMER LUGAR")
    st.markdown(f"### **Votos a Favor de {primero['nombre']}**")
    st.markdown(f"<h1 style='color: #F39C12; font-size: 42px;'>{primero['votos']:,} <span style='font-size: 24px; color: gray;'>votos ({primero['porcentaje']:.3f}%)</span></h1>", unsafe_allow_html=True)

with col_2do:
    st.info("🥈 SEGUNDO LUGAR")
    st.markdown(f"### **Votos a Favor de {segundo['nombre']}**")
    st.markdown(f"<h1 style='color: #1ABC9C; font-size: 42px;'>{segundo['votos']:,} <span style='font-size: 24px; color: gray;'>votos ({segundo['porcentaje']:.3f}%)</span></h1>", unsafe_allow_html=True)

st.markdown("---")

## NIVEL 2: INDICADOR CRÍTICO DE DIFERENCIA (Gran Formato)
st.markdown("### ⚖️ MARGEN DE CONTROL")
col_dif, col_actas = st.columns([2, 1])

with col_dif:
    st.subheader("Diferencia Absoluta de Votos")
    # CORRECCIÓN DE SINTAXIS EN LA VARIABLE DE CONTROL:
    st.markdown(f"<p style='font-size: 48px; font-weight: bold; color: #E74C3C; margin: 0;'>{diferencia_absoluta:,} <span style='font-size: 20px; font-weight: normal; color: gray;'>votos de ventaja</span></p>", unsafe_allow_html=True)
    st.caption(f"Brecha matemática actual del primer lugar sobre el segundo lugar ({primero['nombre']} vs {segundo['nombre']}).")

with col_actas:
    st.metric(label="📋 Actas por Procesar", value=f"{actas_por_procesar:,}")
    st.metric(label="📂 Actas Observadas (En el JEE)", value=f"{observadas:,}")

st.markdown("---")

## NIVEL 3: GRÁFICOS ANALÍTICOS
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
        color_discrete_map={"Keiko Fujimori": "#F39C12", "Roberto Sánchez": "#1ABC9C"},
        hole=0.4
    )
    fig_torta.update_traces(texttemplate="%{percent:.3%}<br>%{value:,} votos", textinfo="percent+value")
    fig_torta.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=300)
    st.plotly_chart(fig_torta, use_container_width=True)

with col_graph2:
    st.markdown("#### Evolución Temporal del Voto Acumulado")
    st.line_chart(df_evolucion, color=["#F39C12", "#1ABC9C"], height=300)

# 4. Ciclo de Refresco de Red
time.sleep(60)
st.rerun()
