import streamlit as st
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from processing.smart_recommendation_engine import SmartRecommendationEngine
from processing.groq_integration import GroqIntegration

# ============ CONFIGURACIÓN ============
st.set_page_config(
    page_title="🐾 Chat Veterinario IA",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-header {
    font-size: 2.5em;
    color: #1f77b4;
    text-align: center;
    margin-bottom: 10px;
}
.subtitle {
    font-size: 1.1em;
    color: #666;
    text-align: center;
    margin-bottom: 30px;
}
.user-msg {
    background-color: #e3f2fd;
    padding: 10px;
    border-radius: 8px;
    margin: 8px 0;
    border-left: 4px solid #1f77b4;
}
.ai-msg {
    background-color: #f5f5f5;
    padding: 10px;
    border-radius: 8px;
    margin: 8px 0;
    border-left: 4px solid #4caf50;
}
</style>
""", unsafe_allow_html=True)

# ============ CARGAR MOTORES ============
@st.cache_resource
def cargar_motor():
    return SmartRecommendationEngine()

@st.cache_resource
def cargar_groq():
    return GroqIntegration()

try:
    motor = cargar_motor()
    groq = cargar_groq()
    groq_disponible = True
except Exception as e:
    groq_disponible = False
    error_groq = str(e)

# ============ INTERFAZ ============
st.markdown("<h1 class='main-header'>🐾 Chat Veterinario IA</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Consulta sobre medicamentos y protocolos veterinarios</p>", unsafe_allow_html=True)

if not groq_disponible:
    st.error("❌ Error de conexión con Groq: " + error_groq)
    st.info("Verifica que tu API KEY está en .env")
    st.stop()

# Inicializar historial
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ============ MOSTRAR CHAT ============
st.subheader("💬 Conversación")

for msg in st.session_state.chat_history:
    if msg['role'] == 'user':
        st.markdown("<div class='user-msg'><strong>👤 Tú:</strong> " + msg['content'] + "</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='ai-msg'><strong>🤖 Sistema:</strong><br>" + msg['content'] + "</div>", unsafe_allow_html=True)

st.divider()

# ============ INPUT ============
st.subheader("📝 Tu consulta")

col1, col2 = st.columns([4, 1])

with col1:
    user_input = st.text_input(
        "Pregunta:",
        placeholder="Ej: Dosis de FRONTLINE para un boxer de 30kg?",
        key="chat_input"
    )

with col2:
    enviar = st.button("Enviar", use_container_width=True)

# ============ PROCESAR ============
if enviar and user_input:
    st.session_state.chat_history.append({
        'role': 'user',
        'content': user_input
    })
    
    with st.spinner("Analizando y buscando datos..."):
        try:
            parametros = motor.extraer_parametros_texto(user_input)
            
            contexto = "Especie: " + str(parametros['especie']) + ", Peso: " + str(parametros.get('peso', 'N/A')) + " kg"
            if parametros.get('raza'):
                contexto += ", Raza: " + str(parametros['raza'])
            
            respuesta = groq.generar_respuesta(
                user_input,
                contexto=contexto,
                temperatura=0.7,
                max_tokens=500
            )
        except Exception as e:
            respuesta = "Error: " + str(e)
    
    st.session_state.chat_history.append({
        'role': 'assistant',
        'content': respuesta
    })
    
    st.rerun()

# ============ INFORMACIÓN ============
with st.expander("Información"):
    st.markdown("""
    ### Chat Veterinario IA + Groq
    
    Características:
    - Chat con IA inteligente (Groq - Mixtral)
    - Búsqueda en base de datos de medicamentos
    - Protocolos personalizados
    - Respuestas en 1-2 segundos
    - 5000 consultas/mes GRATIS
    
    Como usar:
    1. Escribe tu consulta
    2. El sistema busca datos
    3. Groq IA genera respuesta
    4. Obtienes protocolo
    
    Importante: Este es un ASISTENTE educativo.
    Siempre consulta con un veterinario profesional.
    """)