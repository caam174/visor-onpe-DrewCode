import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import datetime
import time

# ==============================================================================
# 1. CONFIGURACIÓN DE INFRAESTRUCTURA Y ENTIDAD VISUAL
# ==============================================================================
st.set_page_config(page_title="Control de Escrutinio ONPE", layout="wide")

st.markdown(
    """
    <div style="text-align: right; color: #000080; font-family: 'CMU Serif', 'Computer Modern', 'Times New Roman', serif; font-weight: bold; font-size: 13px; margin-bottom: -25px; padding-right: 5px;">
        Elaborado por DrewCode - 2026. Cualquier consulta puedes escribirme a caam174@gmail.com
    </div>
    """,
    unsafe_allow_html=True
)

st.title("🏛️ Tablero de Control de Escrutinio Oficial (EN VIVO)")
st.caption("Filtro de precisión analítica con actualización recursiva cada 60 segundos")
st.markdown("---")

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
                return None, "Bloqueo/HTML detectado en respuesta"
        return None, f"Error HTTP {response.status_code}"
    except Exception as e:
        return None, f"Fallo de Red: {str(e)}"

json_data, status_msg = consumir_api_onpe(ONPE_API_REAL)

# ==============================================================================
# 2. PARAMETRIZACIÓN NOMINAL Y AUDITORÍA VECTORIAL CORREGIDA
# ==============================================================================
total_actas = 92766
procesadas_porc = 98.593  # Avance del pipeline de digitación primaria
observadas_jee = 1305     # Stock retenido en el tribunal electoral
corte_temporal = "15/06/2026 08:10:19 a. m."

candidatos = [
    {"nombre": "Keiko Sofía Fujimori Higuchi", "votos": 9075116, "porcentaje": 50.051},
    {"nombre": "Roberto Helbert Sánchez Palomino", "votos": 9056638, "porcentaje": 49.949}
]

# Recalculo dinámico basado en las identidades macro-electorales
por_procesar_porc = 100.0 - procesadas_porc
jee_porc = (observadas_jee / total_actas) * 100
faltante_total_inicial = por_procesar_porc + jee_porc  # 2.814% para el último corte

# Registro histórico ajustado cronológicamente con la métrica corregida (mayor y exacta)
if "registro_historico" not in st.session_state:
    st.session_state.registro_historico = pd.DataFrame([
        {"Corte": "11/06 09:40", "Keiko": 9032653, "Roberto": 9032092, "Diferencia Absoluta": 561, "Actas JEE": 1650, "Porcentaje Faltante": 3.629},
        {"Corte": "11/06 12:30", "Keiko": 9033584, "Roberto": 9032662, "Diferencia Absoluta": 922, "Actas JEE": 1640, "Porcentaje Faltante": 3.588},
        {"Corte": "11/06 13:35", "Keiko": 9034070, "Roberto": 9033211, "Diferencia Absoluta": 859, "Actas JEE": 1628, "Porcentaje Faltante": 3.525},
        {"Corte": "12/06 07:55", "Keiko": 9036046, "Roberto": 9034743, "Diferencia Absoluta": 1303, "Actas JEE": 1607, "Porcentaje Faltante": 3.473},
        {"Corte": "13/06 13:25", "Keiko": 9050366, "Roberto": 9042680, "Diferencia Absoluta": 7686, "Actas JEE": 1498, "Porcentaje Faltante": 3.230},
        {"Corte": "15/06 08:10", "Keiko": 9075116, "Roberto": 9056638, "Diferencia Absoluta": 18478, "Actas JEE": 1305, "Porcentaje Faltante": round(faltante_total_inicial, 3)}
    ])

if status_msg == "OK" and json_data:
    try:
        procesadas_porc = float(json_data.get("porcentajepros", 98.593))
        observadas_jee = int(json_data.get("totales_observadas", 1305))
        lista_api = json_data.get("resumen", json_data.get("candidatos", []))
        
        if lista_api and len(lista_api) >= 2:
            votos_k = int(str(lista_api[0].get("votos")).replace(",", ""))
            votos_r = int(str(lista_api[1].get("votos")).replace(",", ""))
            candidatos = [
                {"nombre": "Keiko Sofía Fujimori Higuchi", "votos": votos_k, "porcentaje": float(lista_api[0].get("porcentaje"))},
                {"nombre": "Roberto Helbert Sánchez Palomino", "votos": votos_r, "porcentaje": float(lista_api[1].get("porcentaje"))}
            ]
            corte_temporal = "Sincronizado en Tiempo Real"
            
            # Recálculo de la ecuación de balance en tiempo real
            por_procesar_porc = 100.0 - procesadas_porc
            jee_porc = (observadas_jee / total_actas) * 100
            faltante_total_actual = por_procesar_porc + jee_porc
            
            df_actual = st.session_state.registro_historico
            if not df_actual.empty and df_actual.iloc[-1]["Keiko"] != votos_k:
                fecha_hora_viva = datetime.datetime.now().strftime("%d/%m %H:%M")
                nueva_fila = pd.DataFrame([{
                    "Corte": fecha_hora_viva, 
                    "Keiko": votos_k, 
                    "Roberto": votos_r, 
                    "Diferencia Absoluta": abs(votos_k - votos_r),
                    "Actas JEE": observadas_jee,
                    "Porcentaje Faltante": round(faltante_total_actual, 3)
                }])
                st.session_state.registro_historico = pd.concat([df_actual, nueva_fila], ignore_index=True)
    except Exception as e:
        st.sidebar.error(f"Error de parsing: {str(e)}")

# Consolidación final de variables de salida
porcentaje_faltante_real = por_procesar_porc + jee_porc

# ==============================================================================
# 3. CAPA DE PRESENTACIÓN VISUAL
# ==============================================================================
candidatos_ordenados = sorted(candidatos, key=lambda x: x["votos"], reverse=True)
primero = candidatos_ordenados[0]
segundo = candidatos_ordenados[1]
diferencia_actual = primero["votos"] - segundo["votos"]

st.sidebar.info(f"Último corte cargado: {corte_temporal}")

## SECCIÓN I: MARGEN DE POSICIONES
st.markdown("### 🥇 ESTADO DE LA CONTIENDA (VOTOS VÁLIDOS EMITIDOS)")
col_1er, col_2do = st.columns(2)
with col_1er:
    st.error("🏆 PRIMER LUGAR")
    st.markdown(f"### **{primero['nombre']}**")
    st.markdown(f"<h1 style='color: #F39C12; font-size: 38px;'>{primero['votos']:,} <span style='font-size: 20px; color: gray;'>votos ({primero['porcentaje']:.3f}%)</span></h1>", unsafe_allow_html=True)

with col_2do:
    st.info("🥈 SEGUNDO LUGAR")
    st.markdown(f"### **{segundo['nombre']}**")
    st.markdown(f"<h1 style='color: #1ABC9C; font-size: 38px;'>{segundo['votos']:,} <span style='font-size: 20px; color: gray;'>votos ({segundo['porcentaje']:.3f}%)</span></h1>", unsafe_allow_html=True)

st.markdown("---")

## SECCIÓN II: METRICAS ESTRUCTURALES CORREGIDAS
st.markdown("### ⚖️ MARGEN DE CONTROL")
col_dif, col_actas = st.columns([2, 1])

with col_dif:
    st.subheader("Diferencia Absoluta de Votos")
    st.markdown(f"<p style='font-size: 48px; font-weight: bold; color: #E74C3C; margin: 0;'>{diferencia_actual:,} <span style='font-size: 20px; font-weight: normal; color: gray;'>votos de ventaja</span></p>", unsafe_allow_html=True)
    st.caption(f"Brecha matemática actual del primer lugar sobre el segundo lugar.")

with col_actas:
    st.metric(label="📊 Avance de Actas Procesadas", value=f"{procesadas_porc:.3f}%", delta=f"{total_actas:,} Totales")
    st.metric(label="📂 Actas en el JEE (Impugnadas/Stock)", value=f"{observadas_jee:,}", delta=f"{jee_porc:.3f}% del total")
    st.metric(label="⏳ Porcentaje Faltante Real (Cierre Total)", value=f"{porcentaje_faltante_real:.3f}%", delta="Pendiente Integrar", delta_color="inverse")

st.markdown("---")

## SECCIÓN III: ANÁLISIS GRÁFICO VECTORIAL AMPLIADO
st.markdown("### 📊 VISUALIZACIÓN ANALÍTICA DEL ESCRUTINIO")
col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    st.markdown("#### 📈 Evolución Real de la Diferencia Absoluta")
    fig_linea_diff = px.line(
        st.session_state.registro_historico, x="Corte", y="Diferencia Absoluta",
        markers=True, text="Diferencia Absoluta"
    )
    fig_linea_diff.update_traces(line_color="#E74C3C", line_width=3, textposition="top center")
    fig_linea_diff.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280, xaxis=dict(type='category'))
    st.plotly_chart(fig_linea_diff, use_container_width=True)

with col_graph2:
    st.markdown("#### 📉 Distribución Porcentual del Voto Válido Actual")
    df_torta = pd.DataFrame({"Candidato": [primero["nombre"], segundo["nombre"]], "Votos": [primero["votos"], segundo["votos"]]})
    fig_torta = px.pie(
        df_torta, values="Votos", names="Candidato", hole=0.4,
        color_discrete_sequence=["#F39C12", "#1ABC9C"]
    )
    fig_torta.update_traces(texttemplate="%{percent:.3%}<br>%{value:,} votos")
    fig_torta.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=280)
    st.plotly_chart(fig_torta, use_container_width=True)

# Cobertura remanente con curvas de descenso recalibradas bajo el nuevo criterio
st.markdown("### 🔍 AUDITORÍA DE ACTAS EN EL JEE Y COBERTURA REMANENTE RECALIBRADA")
col_jee_graph, col_faltante_graph = st.columns(2)

with col_jee_graph:
    st.markdown("#### Curva de Descenso: Actas Físicas en el JEE")
    fig_jee = px.line(
        st.session_state.registro_historico, x="Corte", y="Actas JEE",
        markers=True, text="Actas JEE"
    )
    fig_jee.update_traces(line_color="#2980B9", line_width=3, textposition="top center")
    fig_jee.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280, xaxis=dict(type='category'))
    st.plotly_chart(fig_jee, use_container_width=True)

with col_faltante_graph:
    st.markdown("#### Curva de Cierre: Brecha de Incertidumbre Real (% Faltante Consolidado)")
    fig_faltante = px.area(
        st.session_state.registro_historico, x="Corte", y="Porcentaje Faltante",
        markers=True, text="Porcentaje Faltante"
    )
    fig_faltante.update_traces(line_color="#8E44AD", texttemplate="%{text:.3f}%", textposition="top center")
    fig_faltante.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=280, xaxis=dict(type='category'))
    st.plotly_chart(fig_faltante, use_container_width=True)

st.markdown("---")

st.markdown(
    """
    <div style="position: relative; width: 100%; display: flex; justify-content: center; align-items: center; margin-top: 30px; margin-bottom: 10px;">
        <span style="font-size: 110px; color: #E74C3C; filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.15)); line-height: 1;">❤️</span>
        <div style="position: absolute; top: 43%; left: 50%; transform: translate(-50%, -50%); color: #FFFFFF; font-weight: bold; font-family: 'Arial', sans-serif; font-size: 14px; letter-spacing: 0.5px; text-shadow: 1px 1px 2px rgba(0,0,0,0.4);">
            Changuito
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

time.sleep(60)
st.rerun()
