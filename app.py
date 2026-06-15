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

# Inyección CSS Global para control de fuentes grandes, tipografía CMU y limpieza visual
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

# Encabezado limpio e institucional
st.markdown(
    """
    <div style="margin-bottom: 25px;">
        <h1 style="font-size: 42px; margin-bottom: 5px;">
            <span style="vertical-align: middle;">🇵🇪</span> Sistema de Fiscalización y Conteo de Actas
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
# 2. PARAMETRIZACIÓN NOMINAL Y AUDITORÍA VECTORIAL
# ==============================================================================
total_actas = 92766
procesadas_porc = 98.598  
observadas_jee = 1301     
corte_temporal = "15/06/2026 10:55:19 a. m."

candidatos = [
    {"nombre": "KEIKO SOFÍA FUJIMORI HIGUCHI", "votos": 9075361, "porcentaje": 50.051, "color": "#F39C12"},
    {"nombre": "ROBERTO HELBERT SÁNCHEZ PALOMINO", "votos": 9057036, "porcentaje": 49.949, "color": "#1ABC9C"}
]

por_procesar_porc = 100.0 - procesadas_porc
jee_porc = (observadas_jee / total_actas) * 100
faltante_total_inicial = por_procesar_porc + jee_porc  

if "registro_historico" not in st.session_state:
    st.session_state.registro_historico = pd.DataFrame([
        {"Corte": "11/06 09:40", "Keiko": 9032653, "Roberto": 9032092, "Diferencia Absoluta": 561, "Actas JEE": 1650, "Porcentaje Faltante": 3.629},
        {"Corte": "11/06 12:30", "Keiko": 9033584, "Roberto": 9032662, "Diferencia Absoluta": 922, "Actas JEE": 1640, "Porcentaje Faltante": 3.588},
        {"Corte": "11/06 13:35", "Keiko": 9034070, "Roberto": 9033211, "Diferencia Absoluta": 859, "Actas JEE": 1628, "Porcentaje Faltante": 3.525},
        {"Corte": "12/06 07:55", "Keiko": 9036046, "Roberto": 9034743, "Diferencia Absoluta": 1303, "Actas JEE": 1607, "Porcentaje Faltante": 3.473},
        {"Corte": "13/06 13:25", "Keiko": 9050366, "Roberto": 9042680, "Diferencia Absoluta": 7686, "Actas JEE": 1498, "Porcentaje Faltante": 3.230},
        {"Corte": "15/06 08:10", "Keiko": 9075116, "Roberto": 9056638, "Diferencia Absoluta": 18478, "Actas JEE": 1305, "Porcentaje Faltante": 2.814},
        {"Corte": "15/06 08:30", "Keiko": 9075116, "Roberto": 9056638, "Diferencia Absoluta": 18478, "Actas JEE": 1305, "Porcentaje Faltante": 2.814},
        {"Corte": "15/06 10:55", "Keiko": 9075361, "Roberto": 9057036, "Diferencia Absoluta": 18325, "Actas JEE": 1301, "Porcentaje Faltante": round(faltante_total_inicial, 3)}
    ])

if status_msg == "OK" and json_data:
    try:
        procesadas_porc = float(json_data.get("porcentajepros", 98.598))
        observadas_jee = int(json_data.get("totales_observadas", 1301))
        lista_api = json_data.get("resumen", json_data.get("candidatos", []))
        
        if lista_api and len(lista_api) >= 2:
            votos_k = int(str(lista_api[0].get("votos")).replace(",", ""))
            votos_r = int(str(lista_api[1].get("votos")).replace(",", ""))
            candidatos = [
                {"nombre": "KEIKO SOFÍA FUJIMORI HIGUCHI", "votos": votos_k, "porcentaje": float(lista_api[0].get("porcentaje")), "color": "#F39C12"},
                {"nombre": "ROBERTO HELBERT SÁNCHEZ PALOMINO", "votos": votos_r, "porcentaje": float(lista_api[1].get("porcentaje")), "color": "#1ABC9C"}
            ]
            corte_temporal = "Sincronizado en Tiempo Real"
            
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

# Ordenación formal por volumen de votación
candidatos_ordenados = sorted(candidatos, key=lambda x: x["votos"], reverse=True)
primero = candidatos_ordenados[0]
segundo = candidatos_ordenados[1]
diferencia_actual = primero["votos"] - segundo["votos"]

st.sidebar.info(f"Corte: {corte_temporal}")

# ==============================================================================
# 3. CAPA DE PRESENTACIÓN DE ALTA VISIBILIDAD (LETRAS GRANDES Y LIMPIAS)
# ==============================================================================

## SECCIÓN I: MARGEN DE POSICIONES (HTML PURIFICADO)
st.markdown("<h3 style='font-size: 24px; letter-spacing: 0.5px; margin-bottom: 15px;'>🥇 ESTADO NOMINAL DE LA CONTIENDA (VOTOS VÁLIDOS)</h3>", unsafe_allow_html=True)
col_1er, col_2do = st.columns(2)

with col_1er:
    st.markdown(
        f"""
        <div class="card-candidato" style="border-top: 5px solid {primero['color']};">
            <span style="font-size: 14px; font-weight: bold; color: {primero['color']}; letter-spacing: 1px;">✓ LÍDER EN ESCRUTINIO</span>
            <h2 style="font-size: 26px; margin-top: 5px; margin-bottom: 10px; color: #111111;">{primero['nombre']}</h2>
            <div style="font-size: 46px; font-weight: bold; color: #000022; line-height: 1;">
                {primero['votos']:,} <span style="font-size: 24px; font-weight: normal; color: #555555;">votos</span>
            </div>
            <div style="font-size: 22px; color: #333333; margin-top: 5px; font-weight: bold;">Porcentaje Válido: {primero['porcentaje']:.3f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_2do:
    st.markdown(
        f"""
        <div class="card-candidato" style="border-top: 5px solid {segundo['color']};">
            <span style="font-size: 14px; font-weight: bold; color: #777777; letter-spacing: 1px;">SEGUNDA POSICIÓN</span>
            <h2 style="font-size: 26px; margin-top: 5px; margin-bottom: 10px; color: #111111;">{segundo['nombre']}</h2>
            <div style="font-size: 46px; font-weight: bold; color: #000022; line-height: 1;">
                {segundo['votos']:,} <span style="font-size: 24px; font-weight: normal; color: #555555;">votos</span>
            </div>
            <div style="font-size: 22px; color: #333333; margin-top: 5px; font-weight: bold;">Porcentaje Válido: {segundo['porcentaje']:.3f}%</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

## SECCIÓN II: MARGEN DE CONTROL MATEMÁTICO (LETRAS MAXIMIZADAS)
st.markdown("<h3 style='font-size: 24px; letter-spacing: 0.5px; margin-bottom: 15px;'>⚖️ PARAMETRÍA ESTRUCTURAL Y BRECHAS</h3>", unsafe_allow_html=True)
col_dif, col_m1, col_m2 = st.columns([2, 1, 1])

with col_dif:
    st.markdown(
        f"""
        <div class="card-metrica" style="background-color: #FFF9F9; border-left-color: #D9534F; padding: 25px;">
            <span style="font-size: 13px; font-weight: bold; color: #D9534F; letter-spacing: 0.5px;">VENTAJA ABSOLUTA DEL PRIMER LUGAR</span>
            <div style="font-size: 52px; font-weight: bold; color: #B92C28; line-height: 1.1; margin-top: 5px;">
                {diferencia_actual:,} <span style="font-size: 22px; font-weight: normal; color: #555555;">Votos de Diferencia</span>
            </div>
            <p style="font-size: 14px; color: #666666; margin-top: 8px; margin-bottom: 0px; font-style: italic;">
                Umbral crítico de contingencia remanente en actas del JEE.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_m1:
    st.markdown(
        f"""
        <div class="card-metrica" style="padding: 22px;">
            <span style="font-size: 13px; color: #555555; font-weight: bold;">ACTAS PROCESADAS</span>
            <div style="font-size: 36px; font-weight: bold; color: #000080; margin-top: 5px;">{procesadas_porc:.3f}%</div>
            <span style="font-size: 14px; color: #444444;">{total_actas:,} Actas Totales</span>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_m2:
    st.markdown(
        f"""
        <div class="card-metrica" style="border-left-color: #2980B9; padding: 22px;">
            <span style="font-size: 13px; color: #555555; font-weight: bold;">STOCK EN EL JEE</span>
            <div style="font-size: 36px; font-weight: bold; color: #2980B9; margin-top: 5px;">{observadas_jee:,}</div>
            <span style="font-size: 14px; color: #444444;">Equivale al {jee_porc:.3f}%</span>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("<br><hr>", unsafe_allow_html=True)

## SECCIÓN III: ANÁLISIS VECTORIAL GRÁFICO (CON FUENTE SERIF UNIFORME)
st.markdown("<h3 style='font-size: 24px; letter-spacing: 0.5px; margin-bottom: 15px;'>📊 ANALÍTICA GRÁFICA DE TENDENCIAS</h3>", unsafe_allow_html=True)
col_graph1, col_graph2 = st.columns(2)

# Configuración base de tipografía limpia para los gráficos de Plotly
plotly_font_config = dict(family="'CMU Serif', 'Computer Modern', 'Georgia', serif", size=13, color="#333333")

with col_graph1:
    st.markdown("<p style='font-size: 16px; font-weight: bold; margin-bottom: 5px;'>📈 Evolución Histórica de la Diferencia Absoluta</p>", unsafe_allow_html=True)
    fig_linea_diff = px.line(
        st.session_state.registro_historico, x="Corte", y="Diferencia Absoluta",
        markers=True, text="Diferencia Absoluta"
    )
    fig_linea_diff.update_traces(line_color="#B92C28", line_width=3, textposition="top center")
    fig_linea_diff.update_layout(
        font=plotly_font_config,
        margin=dict(t=15, b=15, l=15, r=15), 
        height=300, 
        xaxis=dict(type='category', gridcolor='#F0F0F0'),
        yaxis=dict(gridcolor='#F0F0F0'),
        plot_bgcolor='white'
    )
    st.plotly_chart(fig_linea_diff, use_container_width=True)

with col_graph2:
    st.markdown("<p style='font-size: 16px; font-weight: bold; margin-bottom: 5px;'>📉 Composición Relativa del Voto Válido</p>", unsafe_allow_html=True)
    df_torta = pd.DataFrame({"Candidato": [primero["nombre"], segundo["nombre"]], "Votos": [primero["votos"], segundo["votos"]]})
    fig_torta = px.pie(
        df_torta, values="Votos", names="Candidato", hole=0.45,
        color_discrete_sequence=[primero["color"], segundo["color"]]
    )
    fig_torta.update_traces(texttemplate="<b>%{percent:.3%}</b><br>%{value:,} votos", textfont_size=13)
    fig_torta.update_layout(
        font=plotly_font_config,
        showlegend=False, 
        margin=dict(t=15, b=15, l=15, r=15), 
        height=300
    )
    st.plotly_chart(fig_torta, use_container_width=True)

# Curvas avanzadas de descenso de incertidumbre
col_jee_graph, col_faltante_graph = st.columns(2)

with col_jee_graph:
    st.markdown("<p style='font-size: 16px; font-weight: bold; margin-bottom: 5px;'>📂 Ritmo de Desembalse: Historial de Actas en JEE</p>", unsafe_allow_html=True)
    fig_jee = px.line(
        st.session_state.registro_historico, x="Corte", y="Actas JEE",
        markers=True, text="Actas JEE"
    )
    fig_jee.update_traces(line_color="#2980B9", line_width=3, textposition="top center")
    fig_jee.update_layout(
        font=plotly_font_config,
        margin=dict(t=15, b=15, l=15, r=15), 
        height=300, 
        xaxis=dict(type='category', gridcolor='#F0F0F0'),
        yaxis=dict(gridcolor='#F0F0F0'),
        plot_bgcolor='white'
    )
    st.plotly_chart(fig_jee, use_container_width=True)

with col_faltante_graph:
    st.markdown("<p style='font-size: 16px; font-weight: bold; margin-bottom: 5px;'>📉 Curva de Cierre: Incertidumbre Total Pendiente (%)</p>", unsafe_allow_html=True)
    fig_faltante = px.area(
        st.session_state.registro_historico, x="Corte", y="Porcentaje Faltante",
        markers=True, text="Porcentaje Faltante"
    )
    fig_faltante.update_traces(line_color="#8E44AD", texttemplate="<b>%{text:.3f}%</b>", textposition="top center")
    fig_faltante.update_layout(
        font=plotly_font_config,
        margin=dict(t=15, b=15, l=15, r=15), 
        height=300, 
        xaxis=dict(type='category', gridcolor='#F0F0F0'),
        yaxis=dict(gridcolor='#F0F0F0'),
        plot_bgcolor='white'
    )
    st.plotly_chart(fig_faltante, use_container_width=True)

st.markdown("---")

# Footer institucional de cierre emotivo y de control animado
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
