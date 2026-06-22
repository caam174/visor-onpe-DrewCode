import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import datetime
import time
import streamlit.components.v1 as components

# ==============================================================================
# 1. INFRAESTRUCTURA VISUAL E INYECCIÓN DE ESTILO INSTITUCIONAL (CMU SERIF)
# ==============================================================================
st.set_page_config(page_title="Control de Escrutinio ONPE", layout="wide")

st.markdown(
    """
    <style>
        @import url('https://fonts.cdnfonts.com/css/computer-modern');
        
        /* Aplicación de fuente institucional Serif */
        html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, span {
            font-family: 'CMU Serif', 'Computer Modern', 'Georgia', serif !important;
            color: #1A1A1A;
        }
        
        /* Encabezados de alta jerarquía */
        h1, h2, h3, h4 {
            font-family: 'CMU Serif', 'Computer Modern', 'Georgia', serif !important;
            font-weight: 700 !important;
            color: #002C6C !important;
        }
        
        /* Tarjetas de Candidatos Optimizadas */
        .card-candidato {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 8px;
            padding: 30px;
            margin-bottom: 15px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            text-align: center;
            transition: transform 0.2s;
        }
        
        /* Bloque de Resumen de Actas Estilo ONPE */
        .onpe-banner {
            background-color: #F8FAFC;
            border: 1px solid #CBD5E1;
            border-radius: 6px;
            padding: 18px 24px;
            margin-bottom: 25px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Firma estandarizada DrewCode en la esquina superior derecha
st.markdown(
    """
    <div style="text-align: right; color: #002C6C; font-family: 'CMU Serif', serif; font-weight: bold; font-size: 13px; margin-bottom: -20px; padding-right: 5px;">
        Elaborado por DrewCode - 2026. Cualquier consulta puedes escribirme a caam174@gmail.com
    </div>
    """,
    unsafe_allow_html=True
)

# Título Principal alineado al lenguaje oficial
st.markdown(
    """
    <div style="margin-bottom: 20px; text-align: left;">
        <h1 style="font-size: 36px; margin-bottom: 2px; color: #002C6C;">
            Elección de Fórmula Presidencial
        </h1>
        <p style="font-size: 15px; color: #64748B; margin-top: 0px; font-weight: 500;">
            Segunda Vuelta Electoral 2026 — Monitoreo de Datos Macroeconómicos y Reglas del Juego Escrutadas
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)

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
# 2. PARAMETRIZACIÓN NOMINAL FIJADA (DATA VECTOR COHERENTE CON IMAGE_80E2A1.JPG)
# ==============================================================================
total_actas = 92766
procesadas_porc = 99.691      
observadas_jee = 287         
actas_contabilizadas = 92479  
actas_pendientes = 0       
corte_temporal = "22/06/2026 A LAS 08:25:25 a. m."  

candidatos = [
    {"nombre": "KEIKO SOFÍA FUJIMORI HIGUCHI", "partido": "FUERZA POPULAR", "votos": 9188704, "porcentaje": 50.111, "color": "#F15A24"}, 
    {"nombre": "ROBERTO HELBERT SÁNCHEZ PALOMINO", "partido": "JUNTOS POR EL PERÚ", "votos": 9147886, "porcentaje": 49.889, "color": "#009245"} 
]

jee_porc = 0.309  
pendiente_porc = 0.000

# Inicialización y actualización de la Serie de Tiempo Consolidada Diaria
if "registro_historico" not in st.session_state:
    st.session_state.registro_historico = pd.DataFrame([
        {"Día": "11/06", "Keiko": 9034070, "Roberto": 9033211, "Diferencia Absoluta": 859, "Actas JEE": 1628, "Porcentaje Faltante": 3.525, "Observación": ""},
        {"Día": "12/06", "Keiko": 9036046, "Roberto": 9034743, "Diferencia Absoluta": 1303, "Actas JEE": 1607, "Porcentaje Faltante": 3.473, "Observación": ""},
        {"Día": "13/06", "Keiko": 9050366, "Roberto": 9042680, "Diferencia Absoluta": 7686, "Actas JEE": 1498, "Porcentaje Faltante": 3.230, "Observación": ""},
        {"Día": "15/06", "Keiko": 9078181, "Roberto": 9059279, "Diferencia Absoluta": 18902, "Actas JEE": 1275, "Porcentaje Faltante": 2.744, "Observación": ""},
        {"Día": "16/06", "Keiko": 9129316, "Roberto": 9093792, "Diferencia Absoluta": 35524, "Actas JEE": 852, "Porcentaje Faltante": 0.918, "Observación": ""},
        {"Día": "17/06", "Keiko": 9136432, "Roberto": 9100083, "Diferencia Absoluta": 36349, "Actas JEE": 787, "Porcentaje Faltante": 0.848, "Observación": ""},
        {"Día": "18/06", "Keiko": 9158662, "Roberto": 9119096, "Diferencia Absoluta": 39566, "Actas JEE": 565, "Porcentaje Faltante": 0.609, "Observación": ""},
        {"Día": "19/06", "Keiko": 9172509, "Roberto": 9128408, "Diferencia Absoluta": 44101, "Actas JEE": 458, "Porcentaje Faltante": 0.494, "Observación": ""},
        {"Día": "22/06", "Keiko": 9188704, "Roberto": 9147886, "Diferencia Absoluta": 40818, "Actas JEE": 287, "Porcentaje Faltante": jee_porc, "Observación": "Corte 08:25:25 a. m."}
    ])

if status_msg == "OK" and json_data:
    try:
        procesadas_porc = float(json_data.get("porcentajepros", 99.691))
        observadas_jee = int(json_data.get("totales_observadas", 287))
        lista_api = json_data.get("resumen", json_data.get("candidatos", []))
        
        if lista_api and len(lista_api) >= 2:
            votos_k = int(str(lista_api[0].get("votos")).replace(",", ""))
            votos_r = int(str(lista_api[1].get("votos")).replace(",", ""))
            candidatos = [
                {"nombre": "KEIKO SOFÍA FUJIMORI HIGUCHI", "partido": "FUERZA POPULAR", "votos": votos_k, "porcentaje": float(lista_api[0].get("porcentaje")), "color": "#F15A24"},
                {"nombre": "ROBERTO HELBERT SÁNCHEZ PALOMINO", "partido": "JUNTOS POR EL PERÚ", "votos": votos_r, "porcentaje": float(lista_api[1].get("porcentaje")), "color": "#009245"}
            ]
            corte_temporal = f"Sincronizado Dinámico: {datetime.datetime.now().strftime('%H:%M:%S')}"
            jee_porc = (observadas_jee / total_actas) * 100
            
            df_actual = st.session_state.registro_historico
            df_actual.loc[df_actual["Día"] == "22/06", "Keiko"] = votos_k
            df_actual.loc[df_actual["Día"] == "22/06", "Roberto"] = votos_r
            df_actual.loc[df_actual["Día"] == "22/06", "Diferencia Absoluta"] = abs(votos_k - votos_r)
            df_actual.loc[df_actual["Día"] == "22/06", "Actas JEE"] = observadas_jee
            df_actual.loc[df_actual["Día"] == "22/06", "Porcentaje Faltante"] = round(jee_porc, 3)
            df_actual.loc[df_actual["Día"] == "22/06", "Observación"] = f"Corte Dinámico: {datetime.datetime.now().strftime('%H:%M:%S')}"
            st.session_state.registro_historico = df_actual
    except Exception as e:
        st.sidebar.error(f"Error de parsing: {str(e)}")

candidatos_ordenados = sorted(candidatos, key=lambda x: x["votos"], reverse=True)
primero = candidatos_ordenados[0]
segundo = candidatos_ordenados[1]
diferencia_actual = primero["votos"] - segundo["votos"]

st.sidebar.info(f"Fijación Base: {corte_temporal}")

def mapear_anotacion(row):
    base = f"{row['Diferencia Absoluta']:,}"
    if row["Observación"]:
        return f"{base}<br><span style='font-size:10px; font-weight:bold; color:#002C6C;'>⚠️ {row['Observación']}</span>"
    return base

st.session_state.registro_historico["Etiqueta_Grafico"] = st.session_state.registro_historico.apply(mapear_anotacion, axis=1)

# ==============================================================================
# 3. CONSTRUCCIÓN DE LA FAJA DE METRICAS PRINCIPAL (REPLICA REVISADA DE BANNER)
# ==============================================================================
st.markdown(
    f"""
    <div class="onpe-banner">
        <table style="width:100%; border:none; border-collapse:collapse;">
            <tr style="border:none;">
                <td style="width: 20%; vertical-align: middle; border:none;">
                    <span style="font-size: 13px; color: #64748B; font-weight: bold; display:block; margin-bottom:-5px;">Actas contabilizadas</span>
                    <strong style="font-size: 40px; color: #002C6C; font-family: 'Arial', sans-serif;">{procesadas_porc:.3f} %</strong>
                </td>
                <td style="width: 50%; vertical-align: middle; padding-left: 20px; border:none;">
                    <div style="font-size: 13px; color: #1E293B; font-weight: bold;">
                        Total de actas: <span style="color:#002C6C;">{total_actas:,}</span>
                    </div>
                    <div style="font-size: 11px; color: #64748B; font-style: italic; margin-top:2px;">
                        {jee_porc:.3f}% de Actas para envío al JEE y {pendiente_porc:.3f}% de Actas pendientes
                    </div>
                    <div style="width: 100%; background-color: #E2E8F0; border-radius: 9999px; height: 10px; margin-top: 8px; overflow: hidden; display: flex;">
                        <div style="width: {procesadas_porc}%; background-color: #002C6C; height: 100%;"></div>
                        <div style="width: {jee_porc}%; background-color: #38BDF8; height: 100%;"></div>
                        <div style="width: {pendiente_porc}%; background-color: #CBD5E1; height: 100%;"></div>
                    </div>
                </td>
                <td style="width: 30%; text-align: right; vertical-align: middle; border:none; font-size: 11px; color: #475569; font-weight: 500;">
                    <span style="background-color: #002C6C; width: 8px; height: 8px; display: inline-block; border-radius: 50%; margin-right: 4px;"></span> Contabilizadas ({actas_contabilizadas:,}) <br>
                    <span style="background-color: #38BDF8; width: 8px; height: 8px; display: inline-block; border-radius: 50%; margin-right: 4px;"></span> Para envío al JEE ({observadas_jee:,}) <br>
                    <span style="background-color: #CBD5E1; width: 8px; height: 8px; display: inline-block; border-radius: 50%; margin-right: 4px;"></span> Pendientes ({actas_pendientes})
                </td>
            </tr>
        </table>
        <div style="font-size: 10px; color: #64748B; font-weight: bold; text-transform: uppercase; margin-top: 10px; border-top: 1px solid #E2E8F0; padding-top: 6px;">
            ACTUALIZADO AL {corte_temporal}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# 4. CAPA DE PRESENTACIÓN SIMÉTRICA DE CANDIDATOS
# ==============================================================================
col_izq, col_der = st.columns(2)

with col_izq:
    st.markdown(
        f"""
        <div class="card-candidato" style="border-top: 6px solid {candidatos[0]['color']};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 11px; font-weight: 800; color: {candidatos[0]['color']}; letter-spacing: 1px; border: 1px solid {candidatos[0]['color']}; padding: 2px 8px; border-radius: 4px;">
                    {candidatos[0]['partido']}
                </span>
                <span style="font-size: 12px; font-weight: bold; color: #166534; background-color: #DCFCE7; padding: 2px 10px; border-radius: 9999px;">Ganador</span>
            </div>
            <h2 style="font-size: 24px; margin: 15px 0 5px 0; color: #0F172A;">{candidatos[0]['nombre']}</h2>
            <div style="font-size: 56px; font-weight: 800; color: #002C6C; font-family: 'Arial', sans-serif; line-height: 1;">
                {candidatos[0]['porcentaje']:.3f} %
            </div>
            <div style="font-size: 18px; color: #475569; margin-top: 10px; font-weight: 600;">
                {candidatos[0]['votos']:,} <span style="font-size: 14px; color: #94A3B8; font-weight: normal;">votos válidos</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col_der:
    st.markdown(
        f"""
        <div class="card-candidato" style="border-top: 6px solid {candidatos[1]['color']};">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 11px; font-weight: 800; color: {candidatos[1]['color']}; letter-spacing: 1px; border: 1px solid {candidatos[1]['color']}; padding: 2px 8px; border-radius: 4px;">
                    {candidatos[1]['partido']}
                </span>
                <span style="font-size: 12px; font-weight: bold; color: #991B1B; background-color: #FEE2E2; padding: 2px 10px; border-radius: 9999px;">Perdedor</span>
            </div>
            <h2 style="font-size: 24px; margin: 15px 0 5px 0; color: #0F172A;">{candidatos[1]['nombre']}</h2>
            <div style="font-size: 56px; font-weight: 800; color: #002C6C; font-family: 'Arial', sans-serif; line-height: 1;">
                {candidatos[1]['porcentaje']:.3f} %
            </div>
            <div style="font-size: 18px; color: #475569; margin-top: 10px; font-weight: 600;">
                {candidatos[1]['votos']:,} <span style="font-size: 14px; color: #94A3B8; font-weight: normal;">votos válidos</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown(
    f"""
    <div style="background-color: #F0FDF4; border: 1px solid #BBF7D0; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 25px;">
        <span style="font-size: 12px; font-weight: bold; color: #15803D; letter-spacing: 0.5px; text-transform: uppercase;">Ventaja Absoluta del Primer Lugar</span>
        <div style="font-size: 38px; font-weight: 800; color: #166534; font-family: 'Arial', sans-serif; margin-top: 2px;">
            {diferencia_actual:,} <span style="font-size: 18px; font-weight: 500; color: #15803D;">Votos netos de separación</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ==============================================================================
# 5. MÓDULO GRÁFICO TÉCNICO COMPLEMENTARIO
# ==============================================================================
st.markdown("<h3 style='font-size: 20px; margin-bottom: 15px; border-bottom: 2px solid #E2E8F0; padding-bottom: 6px;'>📊 Vector de Tendencias y Distribución Macroeconómica</h3>", unsafe_allow_html=True)
col_g1, col_g2 = st.columns(2)

plotly_layout_defaults = dict(
    font=dict(family="'CMU Serif', Georgia, serif", size=13, color="#1E293B"),
    plot_bgcolor='white',
    paper_bgcolor='white'
)

with col_g1:
    st.markdown("<p style='font-size: 14px; font-weight: bold; color:#0F172A; margin-bottom: 5px;'>📈 Evolución Histórica de la Diferencia Absoluta (Dato por Día Acumulado)</p>", unsafe_allow_html=True)
    fig_linea_diff = px.line(st.session_state.registro_historico, x="Día", y="Diferencia Absoluta", markers=True, text="Etiqueta_Grafico")
    fig_linea_diff.update_traces(line_color="#002C6C", line_width=4, textposition="top center", marker=dict(size=10, line=dict(width=2, color='white'), color="#F15A24"))  
    fig_linea_diff.update_layout(**plotly_layout_defaults, margin=dict(t=35, b=15, l=15, r=15), height=340, xaxis=dict(type='category', gridcolor='#F1F5F9'), yaxis=dict(gridcolor='#F1F5F9'))
    st.plotly_chart(fig_linea_diff, use_container_width=True)

with col_g2:
    st.markdown("<p style='font-size: 14px; font-weight: bold; color:#0F172A; margin-bottom: 5px;'>📉 Composición Porcentual del Espectro Válido</p>", unsafe_allow_html=True)
    df_pie = pd.DataFrame({"Candidato": [candidatos[0]["nombre"], candidatos[1]["nombre"]], "Votos": [candidatos[0]["votos"], candidatos[1]["votos"]]})
    fig_pie = px.pie(df_pie, values="Votos", names="Candidato", hole=0.5, color_discrete_sequence=[candidatos[0]["color"], candidatos[1]["color"]])
    fig_pie.update_traces(texttemplate="<b>%{percent:.3%}</b><br>%{value:,} votos", textfont_size=12, marker=dict(line=dict(color='#FFFFFF', width=2)))
    fig_pie.update_layout(**plotly_layout_defaults, showlegend=False, margin=dict(t=15, b=15, l=15, r=15), height=340)
    st.plotly_chart(fig_pie, use_container_width=True)

col_c1, col_c2 = st.columns(2)

with col_c1:
    st.markdown("<p style='font-size: 14px; font-weight: bold; color:#0F172A; margin-bottom: 5px;'>📂 Desembalse Operativo: Curva de Actas en el JEE por Jornada</p>", unsafe_allow_html=True)
    fig_jee = px.line(st.session_state.registro_historico, x="Día", y="Actas JEE", markers=True, text="Actas JEE")
    fig_jee.update_traces(line_color="#38BDF8", line_width=3, textposition="top center", marker=dict(size=8, color="#002C6C"))
    fig_jee.update_layout(**plotly_layout_defaults, margin=dict(t=25, b=15, l=15, r=15), height=280, xaxis=dict(type='category', gridcolor='#F1F5F9'), yaxis=dict(gridcolor='#F1F5F9'))
    st.plotly_chart(fig_jee, use_container_width=True)

with col_c2:
    st.markdown("<p style='font-size: 14px; font-weight: bold; color:#0F172A; margin-bottom: 5px;'>📉 Umbral Regulatorio: % Pendiente de Resolución Total</p>", unsafe_allow_html=True)
    fig_faltante = px.area(st.session_state.registro_historico, x="Día", y="Porcentaje Faltante", markers=True, text="Porcentaje Faltante")
    fig_faltante.update_traces(line_color="#64748B", texttemplate="<b>%{text:.3f}%</b>", textposition="top center", marker=dict(size=8, color="#002C6C"))
    fig_faltante.update_layout(**plotly_layout_defaults, margin=dict(t=25, b=15, l=15, r=15), height=280, xaxis=dict(type='category', gridcolor='#F1F5F9'), yaxis=dict(gridcolor='#F1F5F9'))
    st.plotly_chart(fig_faltante, use_container_width=True)

st.markdown("---")

# ==============================================================================
# 6. COMPONENTE INTERACTIVO ACTUALIZADO: UN PUNTO SEGURO PARA EL DESESTRÉS
# ==============================================================================
st.markdown("<h3 style='text-align: center; color: #002C6C; margin-bottom: 2px;'>🕹️ Un punto seguro para el desestrés</h3>", unsafe_allow_html=True)

st.markdown(
    """
    <p style='text-align: center; font-size: 14px; color: #475569; margin-top: 6px; font-weight: 500; max-width: 750px; margin-left: auto; margin-right: auto; line-height: 1.5;'>
        Sé que mirar los resultados oficiales te estresa por lo lento que son, así que ¿por qué no te tomas un minuto, te diviertes con este juego y luego vas por un café? ☕<br>
        <span style='font-size: 12px; color: #94A3B8; font-weight: bold;'>[ Control: Presiona la barra espaciadora o haz clic dentro del cuadro para saltar las vallas ]</span>
    </p>
    """, 
    unsafe_allow_html=True
)

juego_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; background-color: transparent; font-family: 'Arial', sans-serif; }
        #canvasContainer { position: relative; width: 600px; height: 160px; }
        canvas { border: 1px solid #CBD5E1; background-color: #F8FAFC; border-radius: 8px; display: block; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02); }
        #scoreBoard { position: absolute; top: 10px; right: 15px; font-size: 12px; color: #475569; font-weight: bold; line-height: 1.5; text-align: right; pointer-events: none; }
        #gameOverOverlay { position: absolute; top: 0; left: 0; width: 600px; height: 160px; background: rgba(248, 250, 252, 0.85); display: none; flex-direction: column; justify-content: center; align-items: center; border-radius: 8px; border: 1px solid #CBD5E1; cursor: pointer; }
        #gameOverOverlay h4 { color: #991B1B; margin: 0 0 5px 0; font-size: 16px; }
        #gameOverOverlay p { color: #475569; margin: 0; font-size: 12px; font-weight: bold; }
    </style>
</head>
<body>
    <div id="canvasContainer">
        <canvas id="runnerCanvas" width="600" height="150"></canvas>
        <div id="scoreBoard">PUNTOS: <span id="currentScore">0</span><br>MÁXIMO: <span id="highScore">0</span></div>
        <div id="gameOverOverlay" onclick="resetGame()">
            <h4>¡Valla impactada!</h4>
            <p>Haz clic o presiona Espacio para reiniciar</p>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('runnerCanvas');
        const ctx = canvas.getContext('2d');
        const overlay = document.getElementById('gameOverOverlay');
        
        let score = 0;
        let highScore = localStorage.getItem('catRunnerHighScore') || 0;
        document.getElementById('highScore').innerText = highScore;

        let gameRunning = true;
        let gravity = 0.6;
        
        let cat = { x: 50, y: 115, wy: 26, hy: 26, vy: 0, jumping: false, emoji: '🐈' };
        let obstacles = [];
        let frame = 0;
        let nextObstacleFrame = 100;

        function spawnObstacle() {
            obstacles.push({ x: 620, y: 118, width: 20, height: 22, emoji: '🚧', speed: 5 + Math.floor(score / 15) });
        }

        function drawFloor() {
            ctx.beginPath();
            ctx.moveTo(0, 138);
            ctx.lineTo(600, 138);
            ctx.strokeStyle = '#CBD5E1';
            ctx.lineWidth = 2;
            ctx.stroke();
        }

        function update() {
            if (!gameRunning) return;
            frame++;

            if (cat.jumping) {
                cat.vy += gravity;
                cat.y += cat.vy;
                if (cat.y >= 115) {
                    cat.y = 115;
                    cat.vy = 0;
                    cat.jumping = false;
                }
            }

            if (frame >= nextObstacleFrame) {
                spawnObstacle();
                frame = 0;
                nextObstacleFrame = Math.max(45, 90 - Math.floor(score * 1.5) + Math.floor(Math.random() * 40));
            }

            for (let i = obstacles.length - 1; i >= 0; i--) {
                obstacles[i].x -= obstacles[i].speed;

                if (obstacles[i].x < cat.x + cat.wy - 4 && obstacles[i].x + obstacles[i].width > cat.x + 4) {
                    if (cat.y + cat.hy - 2 > obstacles[i].y) {
                        endGame();
                    }
                }

                if (obstacles[i].x + obstacles[i].width < cat.x && !obstacles[i].passed) {
                    obstacles[i].passed = true;
                    score++;
                    document.getElementById('currentScore').innerText = score;
                    if (score > highScore) {
                        highScore = score;
                        document.getElementById('highScore').innerText = highScore;
                        localStorage.setItem('catRunnerHighScore', highScore);
                    }
                }

                if (obstacles[i].x < -30) {
                    obstacles.splice(i, 1);
                }
            }
        }

        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            drawFloor();

            ctx.save();
            ctx.translate(cat.x + 13, cat.y + 13);
            ctx.scale(-1, 1);
            ctx.font = '26px Arial';
            ctx.textBaseline = 'middle';
            ctx.textAlign = 'center';
            
            let currentEmoji = gameRunning ? cat.emoji : '😿';
            ctx.fillText(currentEmoji, 0, 0);
            ctx.restore();

            if (!gameRunning) {
                ctx.save();
                ctx.font = 'bold 12px Arial';
                ctx.fillStyle = '#DC2626';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';
                ctx.fillText('¡Perdí! 😾', cat.x + 13, cat.y - 6);
                ctx.restore();
            }

            ctx.font = '22px Arial';
            ctx.textBaseline = 'top';
            ctx.textAlign = 'left';
            for (let obs of obstacles) {
                ctx.fillText(obs.emoji, obs.x, obs.y);
            }
        }

        function loop() {
            update();
            draw();
            requestAnimationFrame(loop);
        }

        function jump() {
            if (!cat.jumping && gameRunning) {
                cat.vy = -9.5;
                cat.jumping = true;
            }
            if (!gameRunning) {
                resetGame();
            }
        }

        function endGame() {
            gameRunning = false;
            overlay.style.display = 'flex';
        }

        function resetGame() {
            score = 0;
            document.getElementById('currentScore').innerText = '0';
            obstacles = [];
            cat.y = 115;
            cat.vy = 0;
            cat.jumping = false;
            frame = 0;
            nextObstacleFrame = 100;
            overlay.style.display = 'none';
            gameRunning = true;
        }

        window.addEventListener('keydown', function(e) {
            if (e.code === 'Space') {
                e.preventDefault();
                jump();
            }
        });

        canvas.addEventListener('click', function(e) {
            e.preventDefault();
            jump();
        });

        loop();
    </script>
</body>
</html>
"""

components.html(juego_html, height=175)

st.markdown("---")

# Footer de cierre estructurado
st.markdown(
    """
    <div style="position: relative; width: 100%; display: flex; justify-content: center; align-items: center; margin-top: 15px; margin-bottom: 10px;">
        <span style="font-size: 100px; color: #EF4444; filter: drop-shadow(0px 4px 6px rgba(0,0,0,0.08)); line-height: 1;">❤️</span>
        <div style="position: absolute; top: 43%; left: 50%; transform: translate(-50%, -50%); color: #FFFFFF; font-weight: bold; font-family: 'Arial', sans-serif; font-size: 13px; letter-spacing: 0.5px; text-shadow: 1px 1px 2px rgba(0,0,0,0.3);">
            Changuito
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

time.sleep(60)
st.rerun()
