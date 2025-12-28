"""
🏥 SISTEMA INTELIGENTE DE RECOMENDACIÓN VETERINARIA
Versión: 3.0 - Ultra Completo
"""

import streamlit as st
import sys
from pathlib import Path

# Configurar paths
sys.path.append(str(Path(__file__).parent.parent))

from processing.smart_recommendation_engine import SmartRecommendationEngine

# ==========================================
# CONFIGURACIÓN DE PÁGINA
# ==========================================
st.set_page_config(
    page_title="🏥 Sistema Veterinario IA",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ==========================================
# 🔒 AUTENTICACIÓN
# ==========================================
def verificar_autenticacion():
    """Sistema de login simple"""
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    
    if not st.session_state.autenticado:
        st.title("🔒 Sistema Veterinario - Login")
        st.markdown("### Acceso Restringido a Profesionales")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            usuario = st.text_input("👤 Usuario", key="login_user")
            password = st.text_input("🔑 Contraseña", type="password", key="login_pass")
            
            if st.button("🚀 Iniciar Sesión", type="primary", use_container_width=True):
                # Credenciales (cambiar en producción)
                if usuario == "admin" and password == "veterinaria":
                    st.session_state.autenticado = True
                    st.success("✅ Acceso concedido")
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
            
            st.info("🔐 **Demo:** usuario: `admin` | contraseña: `veterinaria`")
        
        st.stop()

# Ejecutar verificación
verificar_autenticacion()
# ==========================================
# ESTILOS CSS MEJORADOS
# ==========================================
st.markdown("""
<style>
    /* Tema general */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Headers personalizados */
    h1 {
        color: #1565C0;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    h2, h3 {
        color: #1976D2;
        font-weight: 600;
    }
    
    /* 🔥 NUEVO: Selectbox más legible */
    div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 2px solid #1976D2 !important;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Opciones del dropdown */
    div[role="listbox"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Opción seleccionada/hover */
    div[role="option"]:hover {
        background-color: #E3F2FD !important;
        color: #1565C0 !important;
        font-weight: 500;
    }
    
    /* Texto del selectbox */
    div[data-baseweb="select"] span {
        color: #262730 !important;
        font-weight: 500;
        font-size: 1rem;
    }
    
    /* Text input más visible */
    input {
        background-color: #FFFFFF !important;
        border: 2px solid #1976D2 !important;
        border-radius: 8px;
        color: #262730 !important;
        font-weight: 500;
    }
    
    /* Placeholder del text_input */
    input::placeholder {
        color: #757575 !important;
        opacity: 0.8;
        font-weight: 400;
    }
    
    /* Botones mejorados */
    .stButton > button {
        background: linear-gradient(90deg, #1976D2 0%, #1565C0 100%);
        color: white;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    }
    
    /* Dividers más sutiles */
    hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 2px solid #E0E0E0;
        opacity: 0.5;
    }
    
    /* Expanders con mejor contraste */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF;
        border: 2px solid #E3F2FD;
        border-radius: 10px;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Títulos de expanders */
    div[data-testid="stExpander"] summary {
        font-weight: 600;
        color: #1565C0;
        font-size: 1.1rem;
    }
    
    /* Success/Error/Warning boxes */
    .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 8px;
        padding: 1rem;
        font-weight: 500;
    }
    
    /* Captions más legibles */
    .stCaption {
        color: #616161 !important;
        font-size: 0.9rem;
    }
    
    /* Tabs mejorados */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #FFFFFF;
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border: 2px solid #E0E0E0;
        border-bottom: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1976D2;
        color: white !important;
        border-color: #1976D2;
    }
    
    /* Markdown mejorado */
    .stMarkdown strong {
        color: #1565C0;
    }
    
    /* Code blocks */
    code {
        background-color: #F5F5F5;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        color: #D32F2F;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# INICIALIZACIÓN DEL MOTOR
# ==========================================
@st.cache_resource
def cargar_motor():
    """Carga el motor de recomendación (solo 1 vez)"""
    return SmartRecommendationEngine()

motor = cargar_motor()

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2138/2138440.png", width=100)
    st.title("🐾 Panel de Control")
    
    st.divider()
    
    modo = st.radio(
        "**Selecciona Modo:**",
        ["💬 Chat con IA", "📚 Base de Datos"],
        index=0
    )
    
    st.divider()
    
    st.markdown("### 📊 Estadísticas del Sistema")
    total_medicamentos = len(motor.medicamentos)
    total_enfermedades = len(motor.enfermedades)
    
    col1, col2 = st.columns(2)
    col1.metric("💊 Medicamentos", total_medicamentos)
    col2.metric("🏥 Enfermedades", total_enfermedades)
    
    st.divider()
    
    st.markdown("### ℹ️ Acerca de")
    st.info(
        """
        **Sistema Veterinario v3.0**
        
        - 🤖 IA Avanzada
        - 🎯 300+ Síntomas
        - 💊 1600+ Medicamentos
        - 🏥 44 Enfermedades
        - 🔍 Búsqueda Fuzzy
        """
    )

# ==========================================
# HEADER PRINCIPAL
# ==========================================
st.title("🏥 Sistema Inteligente de Recomendación Veterinaria")
st.markdown("### 🐕 Diagnóstico y Tratamiento Asistido por IA")

# ==========================================
# MODO 1: CHAT CON IA
# ==========================================
if modo == "💬 Chat con IA":
    st.header("💬 Consulta con Asistente Virtual")
    
    # Ejemplos de consultas
    with st.expander("📝 Ejemplos de Consultas", expanded=False):
        st.markdown("""
        **Prueba estas consultas:**
        
        🐕 Perros:
        - "Perro labrador 25kg con dolor en las caderas"
        - "Perro pequeño se rasca mucho las orejas"
        - "Perro golden 30kg con diarrea y vómitos"
        - "Perro pastor alemán con displasia de cadera"
        
        🐱 Gatos:
        - "Gato 4kg con infección en el oído"
        - "Gato persa con ojos rojos y legañas"
        - "Gato 5kg que orina con sangre"
        - "Gato siamés con picazón y alopecia"
        """)
    
    # Input del usuario
    consulta_usuario = st.text_area(
        "🗣️ Describe el caso clínico:",
        placeholder="Ej: Gato 5kg con otitis externa, tiene pus en la oreja...",
        height=120,
        help="Incluye: especie, peso, síntomas, raza (opcional)"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        btn_consultar = st.button("🔍 Analizar", type="primary", use_container_width=True)
    with col2:
        btn_limpiar = st.button("🗑️ Limpiar", use_container_width=True)
    
    if btn_limpiar:
        st.rerun()
    
    if btn_consultar and consulta_usuario:
        with st.spinner("🤖 Analizando caso clínico..."):
            resultado = motor.procesar_consulta_chat(consulta_usuario)
        
        # ========== RESULTADOS ==========
        st.divider()
        st.subheader("📋 Resultados del Análisis")
        
        # Parámetros detectados
        params = resultado['parametros']
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🐾 Especie", params.get('especie', 'N/A'))
        col2.metric("⚖️ Peso", f"{params.get('peso', 'N/A')} kg" if params.get('peso') else "N/A")
        col3.metric("🏷️ Raza", params.get('raza', 'N/A') or "No detectada")
        col4.metric("🔍 Síntomas", len(params.get('sintomas', [])))
        
        # Síntomas detectados
        if params.get('sintomas'):
            st.markdown("**🩺 Síntomas Identificados:**")
            sintomas_str = ", ".join([f"`{s}`" for s in params['sintomas']])
            st.info(sintomas_str)
        
        st.divider()
        
        # Enfermedades detectadas
        if resultado['enfermedades_detectadas']:
            st.success(f"✅ **{len(resultado['enfermedades_detectadas'])} enfermedad(es) identificada(s)**")
            
            for idx, enf in enumerate(resultado['enfermedades_detectadas'], 1):
                confianza = enf.get('confianza', 0) * 100
                color = "🟢" if confianza >= 70 else "🟡" if confianza >= 40 else "🔴"
                
                st.markdown(f"{color} **{idx}. {enf['nombre']}** - Confianza: {confianza:.0f}%")
        else:
            st.warning("⚠️ No se detectaron enfermedades específicas. Refina la descripción.")
        
        st.divider()
        
        # Medicamentos recomendados
        if resultado['medicamentos_recomendados']:
            st.success(f"💊 **{len(resultado['medicamentos_recomendados'])} medicamento(s) recomendado(s)**")
            
            for idx, med in enumerate(resultado['medicamentos_recomendados'], 1):
                with st.expander(f"💊 {idx}. {med['nombre']}", expanded=(idx <= 3)):
                    
                    col_izq, col_der = st.columns([1, 1])
                    
                    with col_izq:
                        st.markdown("**📋 Información:**")
                        st.markdown(f"- **Especie:** `{med.get('especie', 'N/A')}`")
                        st.markdown(f"- **Prescripción:** `{med.get('prescripcion', 'N/A')}`")
                    
                    with col_der:
                        st.markdown("**🧪 Principios Activos:**")
                        for pa in med.get('principios_activos', []):
                            st.markdown(f"- `{pa}`")
                    
                    # Calcular dosis si hay peso
                    if params.get('peso'):
                        dosis_info = motor._calcular_dosis_texto(med, params['peso'])
                        st.info(f"⚖️ {dosis_info}")
                    else:
                        st.warning("⚠️ Peso no especificado. No se puede calcular dosis automática.")
        else:
            st.error("❌ No se encontraron medicamentos. Intenta ser más específico.")

# ==========================================
# MODO 2: BASE DE DATOS
# ==========================================
else:
    st.header("📚 Catálogo Completo de Medicamentos CIMAVET")
    
    # 🔥 FILTROS CON MEJOR ESTILO
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_especie = st.selectbox(
            "🐕 Especie", 
            ["Todos", "Perro", "Gato"],
            key="filtro_especie",
            help="Filtra medicamentos por especie animal"
        )
    with col2:
        filtro_prescripcion = st.selectbox(
            "💊 Prescripción", 
            ["Todos", "Sí", "No"],
            key="filtro_prescripcion",
            help="Filtra si requiere receta veterinaria"
        )
    with col3:
        busqueda = st.text_input(
            "🔍 Buscar", 
            placeholder="Ej: Meloxicam, Enrofloxacino...",
            help="Busca por nombre o principio activo"
        )
    
    # Botón de búsqueda
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    with col_btn1:
        btn_buscar = st.button("🔍 Buscar", type="primary", use_container_width=True)
    with col_btn2:
        btn_reset = st.button("🔄 Reset", use_container_width=True)
    
    if btn_reset:
        st.rerun()
    
    # Filtrado de medicamentos
    medicamentos_filtrados = []
    for med_id, med_data in motor.medicamentos.items():
        # Filtro especie
        if filtro_especie != "Todos":
            especie_med = med_data.get('especie', '').upper()
            if filtro_especie.upper() not in especie_med:
                continue
        
        # Filtro prescripción
        prescripcion = med_data.get('prescripcion', '')
        if filtro_prescripcion == "Sí" and "Sujeto a prescripción" not in prescripcion:
            continue
        if filtro_prescripcion == "No" and "No sujeto" not in prescripcion:
            continue
        
        # Filtro búsqueda
        if busqueda:
            nombre = med_data.get('nombre', '').lower()
            principios = ' '.join(med_data.get('principios_activos', [])).lower()
            if busqueda.lower() not in nombre and busqueda.lower() not in principios:
                continue
        
        medicamentos_filtrados.append((med_id, med_data))
    
    st.divider()
    
    # 🔥 MENSAJE DE RESULTADOS CON ESTILO
    if medicamentos_filtrados:
        st.success(f"📊 **{len(medicamentos_filtrados)}** medicamentos encontrados de **{len(motor.medicamentos)}** totales")
    else:
        st.warning("⚠️ No se encontraron medicamentos con esos filtros. Prueba con otros criterios.")
    
    # 🔥 TABLA DE MEDICAMENTOS CON MEJOR DISEÑO
    for med_id, med in medicamentos_filtrados[:50]:  # Limitar a 50 por rendimiento
        with st.expander(f"💊 **{med.get('nombre', 'Sin nombre')}**"):
            
            # Dividir en 2 columnas
            col_izq, col_der = st.columns([1, 1])
            
            with col_izq:
                st.markdown("### 📋 Información General")
                st.markdown(f"**Especie:** `{med.get('especie', 'N/A')}`")
                st.markdown(f"**Nº Registro:** `{med.get('numero_registro', 'N/A')}`")
                st.markdown(f"**Estado:** `{med.get('estado', 'N/A')}`")
                st.markdown(f"**Comercializado:** `{med.get('fecha_comercializado', 'N/A')}`")
            
            with col_der:
                st.markdown("### 🧪 Principios Activos")
                principios = med.get('principios_activos', [])
                if principios:
                    for pa in principios:
                        st.markdown(f"- `{pa}`")
                else:
                    st.markdown("*No especificado*")
            
            # Fila completa para prescripción
            st.divider()
            prescripcion = med.get('prescripcion', 'N/A')
            if "Sujeto a prescripción" in prescripcion:
                st.error(f"🔒 **{prescripcion}**")
            else:
                st.success(f"🟢 **{prescripcion}**")
            
            # Titular
            st.caption(f"📦 **Titular:** {med.get('titular', 'N/A')}")
    
    # Mensaje si se excede el límite
    if len(medicamentos_filtrados) > 50:
        st.info(f"ℹ️ Mostrando solo los primeros 50 medicamentos. Usa los filtros para refinar la búsqueda.")

# ==========================================
# FOOTER
# ==========================================
st.divider()
st.markdown("""
<div style='text-align: center; color: #757575; padding: 1rem;'>
    <p><strong>🏥 Sistema Veterinario v3.0</strong> | Powered by IA 🤖</p>
    <p style='font-size: 0.8rem;'>⚠️ Este sistema es de apoyo. Consulta siempre con un veterinario colegiado.</p>
</div>
""", unsafe_allow_html=True)

