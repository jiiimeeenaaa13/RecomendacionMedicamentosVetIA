import streamlit as st
import sys
from pathlib import Path

# Configurar path raíz
sys.path.append(str(Path(__file__).parent.parent))

try:
    from processing.smart_recommendation_engine import SmartRecommendationEngine
except ImportError:
    st.error("Error crítico: No se encuentra el motor de recomendación.")
    st.stop()

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="Vet-IA Pro",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. AUTENTICACIÓN
# ==========================================
def verificar_autenticacion():
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    
    if not st.session_state.autenticado:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.title("🔒 Acceso Profesional")
            u = st.text_input("Usuario", key="u")
            p = st.text_input("Contraseña", type="password", key="p")
            
            if st.button("Entrar", type="primary"):
                if u == "admin" and p == "veterinaria":
                    st.session_state.autenticado = True
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
        st.stop()

verificar_autenticacion()

# ==========================================
# 3. ESTILOS CSS (Solución DEFINITIVA de Contraste)
# ==========================================
st.markdown("""
<style>
    /* 1. Fondo general claro */
    .stApp {
        background-color: #F8F9FA;
        color: #212121;
    }

    /* 2. Textos generales oscuros */
    h1, h2, h3, h4, h5, h6, p, li, span, div, label {
        color: #212121 !important;
    }
    
    /* 3. Títulos principales en azul */
    h1, h2, h3 {
        color: #0D47A1 !important;
    }

    /* 4. INPUTS Y SELECTBOX (CRÍTICO) */
    /* Fondo blanco y borde azul para todos los inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #212121 !important; /* Texto negro siempre */
        border: 1px solid #1976D2 !important;
    }
    
    /* DROPDOWN MENU (Las opciones que se despliegan) */
    ul[data-testid="stSelectboxVirtualDropdown"] {
        background-color: #FFFFFF !important;
    }
    
    /* Opciones individuales del menú */
    li[role="option"] {
        background-color: #FFFFFF !important;
        color: #212121 !important;
    }
    
    /* Opción seleccionada (hover) */
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {
        background-color: #E3F2FD !important;
        color: #0D47A1 !important;
    }

    /* El texto seleccionado que queda visible en la caja cerrada */
    .stSelectbox div[data-baseweb="select"] div {
        color: #212121 !important; 
    }

    /* 5. SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #E3F2FD;
    }
    section[data-testid="stSidebar"] * {
        color: #0D47A1 !important;
    }

    /* 6. Expanders/Tarjetas */
    .streamlit-expanderHeader {
        background-color: white !important;
        color: #0D47A1 !important;
        font-weight: bold !important;
    }
    div[data-testid="stExpander"] {
        background-color: white !important;
        border: 1px solid #BBDEFB !important;
    }

    /* 7. Botones */
    .stButton button {
        background-color: #1565C0 !important;
        color: white !important;
        font-weight: bold !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. MOTOR
# ==========================================
@st.cache_resource
def cargar_motor():
    return SmartRecommendationEngine()

motor = cargar_motor()

# ==========================================
# 5. SIDEBAR
# ==========================================
with st.sidebar:
    st.title("⚕️ Panel Clínico")
    st.divider()
    
    modo = st.radio(
        "Módulo:",
        ["Asistente Clínico (IA)", "Consuta Base de Datos"],
        index=0
    )
    
    st.divider()
    # Estadísticas seguras
    n_meds = len(motor.medicamentos)
    n_enfs = len(motor.enfermedades_data) if hasattr(motor, 'enfermedades_data') else 0
    
    col1, col2 = st.columns(2)
    col1.metric("Fármacos", n_meds)
    col2.metric("Protocolos", n_enfs)

# ==========================================
# 6. INTERFAZ PRINCIPAL
# ==========================================

# --- MODO 1: CHAT IA ---
if modo == "Asistente Clínico (IA)":
    st.header("📋 Asistente de Diagnóstico y Prescripción")
    
    consulta = st.text_area(
        "Caso Clínico:",
        placeholder="Ej: Felino 4kg, otitis purulenta...",
        height=100
    )
    
    if st.button("Analizar Caso", type="primary"):
        if consulta:
            with st.spinner("Procesando..."):
                resultado = motor.procesar_consulta_chat(consulta)
            
            # Informe IA
            st.markdown("### 📝 Informe Clínico")
            st.markdown(resultado["respuesta_texto"])
            
            # Medicamentos
            meds = resultado["datos_tecnicos"]["medicamentos"]
            st.divider()
            st.subheader(f"💊 Opciones Terapéuticas ({len(meds)})")
            
            if meds:
                for idx, med in enumerate(meds, 1):
                    nombre = med.get('nombre', 'Sin Nombre')
                    with st.expander(f"{idx}. {nombre}", expanded=(idx<=3)):
                        c1, c2 = st.columns([2,1])
                        with c1:
                            st.markdown("**Principios:**")
                            for p in med.get('principios_activos', []):
                                st.markdown(f"- {p}")
                            st.markdown(f"**Presentación:** {med.get('forma_farmaceutica','-')}")
                        with c2:
                            presc = med.get('prescripcion', '-')
                            if "Sujeto" in presc:
                                st.error(f"🔒 {presc}")
                            else:
                                st.success(f"🟢 {presc}")
            else:
                st.info("No se encontraron fármacos específicos en BD para este cuadro.")

# --- MODO 2: VADEMÉCUM ---
else:
    st.header("📚 Vademécum Veterinario")
    
    # Filtros
    c1, c2, c3 = st.columns(3)
    
    # Selectbox normales de Streamlit, ahora con CSS corregido
    f_esp = c1.selectbox("Especie", ["Todas", "Perro", "Gato"])
    f_rec = c2.selectbox("Receta", ["Todas", "Sí", "No"])
    q = c3.text_input("Buscar fármaco o principio activo...")
    
    if st.button("Buscar en Catálogo"):
        resultados = []
        for mid, m in motor.medicamentos.items():
            # Filtro Especie
            if f_esp != "Todas":
                esp_med = m.get('especie','').upper()
                if f_esp.upper() not in esp_med and "AMBOS" not in esp_med:
                    continue
            
            # Filtro Receta
            presc = m.get('prescripcion','')
            if f_rec == "Sí" and "Sujeto" not in presc: continue
            if f_rec == "No" and "No sujeto" not in presc: continue
            
            # Filtro Texto
            if q:
                txt = (m.get('nombre','') + " " + " ".join(m.get('principios_activos',[]))).lower()
                if q.lower() not in txt: continue
                
            resultados.append(m)
            
        st.success(f"Resultados encontrados: {len(resultados)}")
        
        # Mostrar resultados (límite 50)
        for m in resultados[:50]:
            with st.expander(f"💊 {m.get('nombre')}"):
                c_izq, c_der = st.columns([2, 1])
                with c_izq:
                    st.write(f"**Principios:** {', '.join(m.get('principios_activos', []))}")
                    st.write(f"**Titular:** {m.get('titular')}")
                with c_der:
                    if "Sujeto" in m.get('prescripcion',''):
                        st.error("Receta obligatoria")
                    else:
                        st.success("Venta libre")
