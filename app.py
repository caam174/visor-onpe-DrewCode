import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import datetime
import time

# ==============================================================================
# 1. INFRAESTRUCTURA VISUAL E INYECCIÓN DE ESTILO CRÍTICO (CMU SERIF & CLEAN LAYOUT)
# ==============================================================================
st.set_page_config(page_title="Control de Escrutinio ONPE", layout="wide")

st.markdown(
    """
    <style>
        @import url('https://fonts.cdnfonts.com/css/computer-modern');
        
        /* Aplicación de fuente global Serif */
        html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, span {
            font-family: 'CMU Serif', 'Computer Modern', 'Georgia', 'Times New Roman', serif !important;
            color: #1A1A1A;
        }
        
        /* Maximización de títulos y encabezados */
        h1, h2, h3, h4 {
            font-family: 'CMU Serif', 'Computer Modern', 'Georgia', 'Times New Roman', serif !important;
            font-weight: 700 !important;
            color: #000033 !important;
        }
        
        /* Tarjetas personalizadas limpias */
        .card-candidato {
            background-color: #FFFFFF;
            border: 1px solid #E0E0E0;
            border-radius: 6px;
            padding: 25px;
            margin-bottom: 15px;
            box-shadow: 0px 2px 4px rgba(0,0,0,0.02);
            text-align: center; 
        }
        
        .card-metrica {
            background-color: #F8F9FA;
            border-left: 4px solid #000080;
            padding: 20px;
            border-radius: 0px 6px 6px 0px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Firma DrewCode superior derecha estandarizada
st.markdown(
    """
    <div style="text-align: right; color: #000080; font-family: 'CMU Serif', 'Computer Modern', serif; font-weight: bold; font-size: 13px; margin-bottom: -20px; padding-right: 5px;">
        Elaborado por DrewCode - 2026. Cualquier consulta puedes escribirme a caam174@gmail.com
    </div>
    """,
    unsafe_allow_html=True
)

# Encabezado principal
st.markdown(
    """
    <div style="margin-bottom: 25px; text-align: center;">
        <h1 style="font-size: 44px; margin-bottom: 5px; color: #000033;">
            Sistema de Fiscalización y Conteo de Actas
        </h1>
        <p style="font-size: 16px; color: #555555; font-style: italic; margin-top: 0px;">
            Filtro de precisión analítica con actualización recursiva cada 60 segundos
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)
st.markdown("---")

ONPE_API_REAL = "https://resultadosegundavuelta.onpe.gob.pe/presentacion-backend/resumen/resumenPresidencial"
st.sidebar.header("🛠️ Pipeline de Datos")

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
# 2. PARAMETRIZACIÓN NOMINAL ACUMULADA (REF: image_f9bda0.jpg)
# ==============================================================================
total_actas = 92766
procesadas_porc = 99.033  
observadas_jee = 897     
corte_temporal = "16/06/2026 07:45:25 a. m."  

candidatos = [
    {"nombre": "KEIKO SOFÍA FUJIMORI HIGUCHI", "votos": 9123301, "porcentaje": 50.090}, 
    {"nombre": "ROBERTO HELBERT SÁNCHEZ PALOMINO", "votos": 9090392, "porcentaje": 49.910} 
]

por_procesar_porc = 100.0 - procesadas_porc
jee_porc = (observadas_jee / total_actas) * 100
faltante_total_inicial = por_procesar_porc + jee_porc  

# Estructuración de Serie de Tiempo con acumulación neta por día completo
if "registro_historico" not in st.session_state:
    st.session_state.registro_historico = pd.DataFrame([
        {"Día": "11/06", "Keiko": 9034070, "Roberto": 9033211, "Diferencia Absoluta": 859, "Actas JEE": 1628, "Porcentaje Faltante": 3.525, "Observación": ""},
        {"Día": "12/06", "Keiko": 9036046, "Roberto": 9034743, "Diferencia Absoluta": 1303, "Actas JEE": 1607, "Porcentaje Faltante": 3.473, "Observación": ""},
        {"Día": "13/06", "Keiko": 9050366, "Roberto": 9042680, "Diferencia Absoluta": 7686, "Actas JEE": 1498, "Porcentaje Faltante": 3.230, "Observación": ""},
        {"Día": "15/06", "Keiko": 9078181, "Roberto": 9059279, "Diferencia Absoluta": 18902, "Actas JEE": 1275, "Porcentaje Faltante": 2.744, "Observación": ""},
        {"Día": "16/06", "Keiko": 9123301, "Roberto": 9090392, "Diferencia Absoluta": 32909, "Actas JEE": 897, "Porcentaje Faltante": round(faltante_total_inicial, 3), "Observación": "Corte hasta 07:45:25 a. m."}
    ])

if status_msg == "OK" and json_data:
    try:
        procesadas_porc = float(json_data.get("porcentajepros", 99.033))
        observadas_jee = int(json_data.get("totales_observadas", 897))
        lista_api = json_data.get("resumen", json_data.get("candidatos", []))
        
        if lista_api and len(lista_api) >= 2:
            votos_k = int(str(lista_api[0].get("votos")).replace(",", ""))
            votos_r = int(str(lista_api[1].get("votos")).replace(",", ""))
            candidatos = [
                {"nombre": "KEIKO SOFÍA FUJIMORI HIGUCHI", "votos": votos_k, "porcentaje": float(lista_api[0].get("porcentaje"))},
                {"nombre": "ROBERTO HELBERT SÁNCHEZ PALOMINO", "votos": votos_r, "porcentaje": float(lista_api[1].get("porcentaje"))}
            ]
            corte_temporal = "Sincronizado en Tiempo Real"
            
            por_procesar_porc = 100.0 - procesadas_porc
            jee_porc = (observadas_jee / total_actas) * 100
            faltante_total_actual = por_procesar_porc + jee_porc
            
            # Actualización sobre el nodo del día actual en ejecución
            df_actual = st.session_state.registro_historico
            df_actual.loc[df_actual["Día"] == "16/06", "Keiko"] = votos_k
            df_actual.loc[df_actual["Día"] == "16/06", "Roberto"] = votos_r
            df_actual.loc[df_actual["Día"] == "16/06", "Diferencia Absoluta"] = abs(votos_k - votos_r)
            df_actual.loc[df_actual["Día"] == "16/06", "Actas JEE"] = observadas_jee
            df_actual.loc[df_actual["Día"] == "16/06", "Porcentaje Faltante"] = round(faltante_total_actual, 3)
            df_actual.loc[df_actual["Día"] == "16/06", "Observación"] = f"Corte dinámico: {datetime.datetime.now().strftime('%H:%M:%S')}"
            st.session_state.registro_historico = df_actual
    except Exception as e:
        st.sidebar.error(f"Error de parsing: {str(e)}")

# Configuración analítica de orden de mérito actual
candidatos_ordenados = sorted(candidatos, key=lambda x: x["votos"], reverse=True)
primero = candidatos_ordenados[0]
segundo = candidatos_ordenados[1]

primero["color"] = "#0046AD"  
segundo["color"] = "#D9381E"  

diferencia_actual = primero["votos"] - segundo["votos"]
st.sidebar.info(f"Corte base: {corte_temporal}")

# Generación de la columna de texto combinado para el gráfico (Votos + Observación del corte)
def construir_etiqueta(row):
    base = f"{row['Diferencia Absoluta']:,}"
    if row["Observación"]:
        return f"{base}<br><span style='font-size:10px; font-weight:bold; color:#002244;'>⚠️ {row['Observación']}</span>"
    return base

st.session_state.registro_historico["Etiqueta_Grafico"] = st.session_state.registro_historico.apply(construir_etiqueta, axis=1)

# ==============================================================================
# 3. CAPA DE PRESENTACIÓN DE ALTA VISIBILIDAD DE DATOS
# ==============================================================================

## SECCIÓN I: MARGEN DE POSICIONES REALES (VOTOS VÁLIDOS CONTABILIZADOS)
st.markdown("<h3 style='font-size: 24px; letter-spacing: 0.5px; margin-bottom: 15px;'>🥇 ESTADO NOMINAL DE LA CONTIENDA (VOTOS VÁLIDOS CONTABILIZADOS)</h3>", unsafe_allow_html=True)
col_1er, col_2do = st.columns(2)

with col_1er:
    st.markdown(
        f"""
        <div class="card-candidato" style="border-top: 6px solid {primero['color']}; background-color: #F4F8FF;">
            <div style="font-size: 18px; font-weight: bold; color: {primero['color']}; letter-spacing: 1.5px; margin-bottom: 12px; text-align: center;">
                ✓ PRIMER LUGAR (GANADOR ACTUAL)
            </div>
            <h2 style="font-size: 26px; margin-top: 5px; margin-bottom: 10px; color: #000033;">{primero['nombre']}</h2>
            <div style="font-size: 48px; font-weight: bold; color: {primero['color']}; line-height: 1;">
                {primero['votos']:,} <span style="font-size: 24px; font-weight: normal; color: #555555;">votos</span>
            </div>
            <div style="font-size: 22px; color: #111111; margin-top: 8px; font-weight: bold;">Porcentaje Válido: {primero['porcentaje']:.3f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_2do:
    st.markdown(
        f"""
        <div class="card-candidato" style="border-top: 6px solid {segundo['color']}; background-color: #FFF4F4;">
            <div style="font-size: 18px; font-weight: bold; color: {segundo['color']}; letter-spacing: 1.5px; margin-bottom: 12px; text-align: center;">
                SEGUNDO LUGAR
            </div>
            <h2 style="font-size: 26px; margin-top: 5px; margin-bottom: 10px; color: #330000;">{segundo['nombre']}</h2>
            <div style="font-size: 48px; font-weight: bold; color: {segundo['color']}; line-height: 1;">
                {segundo['votos']:,} <span style="font-size: 24px; font-weight: normal; color: #555555;">votos</span>
            </div>
            <div style="font-size: 22px; color: #111111; margin-top: 8px; font-weight: bold;">Porcentaje Válido: {segundo['porcentaje']:.3f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

## SECCIÓN II: MARGEN DE CONTROL MATEMÁTICO (PARAMETRÍA ESTRUCTURAL)
st.markdown("<h3 style='font-size: 24px; letter-spacing: 0.5px; margin-bottom: 15px;'>⚖️ PARAMETRÍA ESTRUCTURAL Y BRECHAS</h3>", unsafe_allow_html=True)
col_dif, col_m1, col_m2 = st.columns([2, 1, 1])

with col_dif:
    st.markdown(
        f"""
        <div class="card-metrica" style="background-color: #F4FBF6; border-left-color: #198754; padding: 25px;">
            <span style="font-size: 13px; font-weight: bold; color: #198754; letter-spacing: 0.5px;">VENTAJA ABSOLUTA DEL PRIMER LUGAR</span>
            <div style="font-size: 54px; font-weight: bold; color: #198754; line-height: 1.1; margin-top: 5px;">
                {diferencia_actual:,} <span style="font-size: 24px; font-weight: normal; color: #444444;">Votos de Diferencia</span>
            </div>
            <p style="font-size: 14px; color: #555555; margin-top: 8px; margin-bottom: 0px; font-style: italic;">
                Margen neto de resguardo frente al volumen acumulado pendiente en los JEE.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_m1:
    st.markdown(
        f"""
        <div class="card-metrica" style="border-left-color: #666666; padding: 22px;">
            <span style="font-size: 13px; color: #555555; font-weight: bold;">ACTAS CONTABILIZADAS</span>
            <div style="font-size: 36px; font-weight: bold; color: #111111; margin-top: 5px;">{procesadas_porc:.3f}%</div>
            <span style="font-size: 14px; color: #555555;">{total_actas:,} Actas Totales</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_m2:
    st.markdown(
        f"""
        <div class="card-metrica" style="border-left-color: #2980B9; padding: 22px;">
            <span style="font-size: 13px; color: #555555; font-weight: bold;">PARA ENVÍO AL JEE</span>
            <div style="font-size: 36px; font-weight: bold; color: #2980B9; margin-top: 5px;">{observadas_jee:,}</div>
            <span style="font-size: 14px; color: #555555;">Equivale al {jee_porc:.3f}%</span>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br><hr>", unsafe_allow_html=True)

## SECCIÓN III: ANÁLISIS GRÁFICO (CONSOLIDACIÓN DIARIA)
st.markdown("<h3 style='font-size: 24px; letter-spacing: 0.5px; margin-bottom: 15px;'>📊 ANALÍTICA GRÁFICA DE TENDENCIAS REALES ACUMULADAS</h3>", unsafe_allow_html=True)
col_graph1, col_graph2 = st.columns(2)

plotly_font_config = dict(family="'CMU Serif', 'Computer Modern', 'Georgia', serif", size=13, color="#333333")

with col_graph1:
    st.markdown("<p style='font-size: 16px; font-weight: bold; margin-bottom: 5px;'>📈 Evolución Histórica de la Diferencia Absoluta (Acumulado por Día)</p>", unsafe_allow_html=True)
    
    # Gráfico ajustado por día con etiquetas de texto enriquecidas para las observaciones
    fig_linea_diff = px.line(
        st.session_state.registro_historico, x="Día", y="Diferencia Absoluta",
        markers=True, text="Etiqueta_Grafico"
    )
    fig_linea_diff.update_traces(
        line_color="#198754", 
        line_width=4, 
        textposition="top center",
        marker=dict(size=10, line=dict(width=2, color='white'))
    )  
    fig_linea_diff.update_layout(
        font=plotly_font_config,
        margin=dict(t=30, b=15, l=15, r=15), 
        height=340, 
        xaxis=dict(type='category', gridcolor='#F0F0F0', title="Jornada de Cómputo (Día)"),
        yaxis=dict(gridcolor='#F0F0F0', title="Brecha de Votos"),
        plot_bgcolor='white'
    )
    st.plotly_chart(fig_linea_diff, use_container_width=True)

with col_graph2:
    st.markdown("<p style='font-size: 16px; font-weight: bold; margin-bottom: 5px;'>📉 Composición Relativa del Voto Válido Actual</p>", unsafe_allow_html=True)
    df_torta = pd.DataFrame({"Candidato": [primero["nombre"], segundo["nombre"]], "Votos": [primero["votos"], segundo["votos"]]})
    fig_torta = px.pie(
        df_torta, values="Votos", names="Candidato", hole=0.45,
        color_discrete_sequence=[primero["color"], segundo["color"]]  
    )
    fig_torta.update_traces(texttemplate="<b>%{{percent:.3%}}</b><br>%{{value:,}} votos", textfont_size=13)
    fig_torta.update_layout(
        font=plotly_font_config,
        showlegend=False, 
        margin=dict(t=15, b=15, l=15, r=15), 
        height=340
    )
    st.plotly_chart(fig_torta, use_container_width=True)

# Curvas complementarias con la estructura unificada por día
col_jee_graph, col_faltante_graph = st.columns(2)

with col_jee_graph:
    st.markdown("<p style='font-size: 16px; font-weight: bold; margin-bottom: 5px;'>📂 Ritmo de Desembalse: Historial de Actas en JEE (Por Día)</p>", unsafe_allow_html=True)
    fig_jee = px.line(
        st.session_state.registro_historico, x="Día", y="Actas JEE",
        markers=True, text="Actas JEE"
    )
    fig_jee.update_traces(line_color="#2980B9", line_width=3, textposition="top center")
    fig_jee.update_layout(
        font=plotly_font_config,
        margin=dict(t=25, b=15, l=15, r=15), 
        height=300, 
        xaxis=dict(type='category', gridcolor='#F0F0F0'),
        yaxis=dict(gridcolor='#F0F0F0'),
        plot_bgcolor='white'
    )
    st.plotly_chart(fig_jee, use_container_width=True)

with col_faltante_graph:
    st.markdown("<p style='font-size: 16px; font-weight: bold; margin-bottom: 5px;'>📉 Curva de Cierre: Incertidumbre Total Pendiente (Por Día %)</p>", unsafe_allow_html=True)
    fig_faltante = px.area(
        st.session_state.registro_historico, x="Día", y="Porcentaje Faltante",
        markers=True, text="Porcentaje Faltante"
    )
    fig_faltante.update_traces(line_color="#8E44AD", texttemplate="<b>%{{text:.3f}}%</b>", textposition="top center")
    fig_faltante.update_layout(
        font=plotly_font_config,
        margin=dict(t=25, b=15, l=15, r=15), 
        height=300, 
        xaxis=dict(type='category', gridcolor='#F0F0F0'),
        yaxis=dict(gridcolor='#F0F0F0'),
        plot_bgcolor='white'
    )
    st.plotly_chart(fig_faltante, use_container_width=True)

st.markdown("---")

# Footer institucional
st.markdown(
    """
    <div style="position: relative; width: 100%; display: flex; justify-content: center; align-items: center; margin-top: 25px; margin-bottom: 10px;">
        <span style="font-size: 110px; color: #E74C3C; filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.1)); line-height: 1;">❤️</span>
        <div style="position: absolute; top: 43%; left: 50%; transform: translate(-50%, -50%); color: #FFFFFF; font-weight: bold; font-family: 'Arial', sans-serif; font-size: 14px; letter-spacing: 0.5px; text-shadow: 1px 1px 2px rgba(0,0,0,0.4);">
            Changuito
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

time.sleep(60)
st.rerun()
