import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import time

# 1. Configuración de la Página
st.set_page_config(page_title="Control de Escrutinio ONPE", layout="wide")

st.title("🏛️ Tablero de Control de Escrutinio Oficial")
st.caption("Filtro de precisión analítica con actualización cada 60 segundos")
st.markdown("---")

# 2. Base de Datos de Entrada (Datos con precisión de 3 decimales)
datos = {
    "total_actas": 86488,
    "actas_procesadas_porc": 98.210,
    "actas_observadas": 1511,
    "candidatos": [
        {"nombre": "Keiko Fujimori", "votos": 8908140, "porcentaje": 50.002},
        {"nombre": "Roberto Sánchez", "votos": 8907428, "porcentaje": 49.998}
    ]
}

# Historial para gráfico de líneas (Evolución)
ahora = datetime.datetime.now()
data_historica = {
    "Hora": [(ahora - datetime.timedelta(hours=i)).strftime("%H:%M") for i in range(5, -1, -1)],
    "Keiko Fujimori": [8862000, 8875000, 8889000, 8895000, 8902000, 8908140],
    "Roberto Sánchez": [8859000, 8871000, 8882000, 8896000, 8905000, 8907428]
}
df_evolucion = pd.DataFrame(data_historica).set_index("Hora")

# 3. Lógica de Negocio: Determinación Automática de Posiciones
candidatos_ordenados = sorted(datos["candidatos"], key=lambda x: x["votos"], reverse=True)
primero = candidatos_ordenados[0]
segundo = candidatos_ordenados[1]

# Cálculos complementarios
diferencia_absoluta = primero["votos"] - segundo["votos"]
actas_procesadas_abs = int((datos["actas_procesadas_porc"] / 100) * datos["total_actas"])
actas_por_procesar = datos["total_actas"] - actas_procesadas_abs

# =========================================================
# CAPA DE PRESENTACIÓN CORREGIDA
# =========================================================

## NIVEL 1: PANELES DE POSICIÓN LITERAL
st.markdown("### 🥇 ESTADO DE LA CONTIENDA (VOTOS VÁLIDOS EMITIDOS)")

col_1er, col_2do = st.columns(2)

with col_1er:
    st.error(f"🏆 PRIMER LUGAR")
    st.markdown(f"### **Votos a Favor de {primero['nombre']}**")
    # CORRECCIÓN: Se cambió a 'unsafe_allow_html=True'
    st.markdown(f"<h1 style='color: #F39C12; font-size: 42px;'>{primero['votos']:,} <span style='font-size: 24px; color: gray;'>votos ({primero['porcentaje']:.3f}%)</span></h1>", unsafe_allow_html=True)

with col_2do:
    st.info(f"🥈 SEGUNDO LUGAR")
    st.markdown(f"### **Votos a Favor de {segundo['nombre']}**")
    # CORRECCIÓN: Se cambió a 'unsafe_allow_html=True'
    st.markdown(f"<h1 style='color: #1ABC9C; font-size: 42px;'>{segundo['votos']:,} <span style='font-size: 24px; color: gray;'>votos ({segundo['porcentaje']:.3f}%)</span></h1>", unsafe_allow_html=True)

st.markdown("---")

## NIVEL 2: INDICADOR CRÍTICO DE DIFERENCIA
st.markdown("### ⚖️ MARGEN DE CONTROL")
col_dif, col_actas = st.columns([2, 1])

with col_dif:
    st.subheader("Diferencia Absoluta de Votos")
    # CORRECCIÓN: Se cambió a 'unsafe_allow_html=True'
    st.markdown(f"<p style='font-size: 48px; font-weight: bold; color: #E74C3C; margin: 0;'>{diferencia_absoluta:,} <span style='font-size: 20px; font-weight: normal; color: gray;'>votos de diferencia</span></p>", unsafe_allow_html=True)
    st.caption(f"Margen de ventaja actual del Primer Lugar sobre el Segundo Lugar.")

with col_actas:
    st.metric(label="📋 Actas por Procesar", value=f"{actas_por_procesar:,}")
    st.metric(label="📂 Actas Observadas (En el JEE)", value=f"{datos['actas_observadas']:,}")

st.markdown("---")

## NIVEL 3: GRÁFICOS ANALÍTICOS
col_graph1, col_graph2 = st.columns(2)

with col_graph1:
    st.markdown("#### Distribución de Votos (Torta)")
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

# 4. Refresco Automático
time.sleep(60)
st.rerun()