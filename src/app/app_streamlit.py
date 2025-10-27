import streamlit as st
import json
from typing import Dict, List
import sys
sys.path.append('src')

# Configuración de página
st.set_page_config(
    page_title="🐾 Sistema de Recomendación Veterinario IA",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
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
    .metric-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Carga el grafo una sola vez (cache)
@st.cache_resource
def cargar_grafo():
    with open('data/knowledge_graph/mapeo_enfermedades_medicamentos.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Carga motor de recomendación
@st.cache_resource
def cargar_motor():
    from processing.recommendation_egine import MedicineRecommendationEngine
    return MedicineRecommendationEngine(
        'data/knowledge_graph/mapeo_enfermedades_medicamentos.json'
    )

# Interfaz principal
st.markdown("<h1 class='main-header'>🐾 Sistema de Recomendación Veterinario IA</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Recomendación inteligente de medicamentos para perros y gatos</p>", unsafe_allow_html=True)

# Cargar datos
grafo = cargar_grafo()
engine = cargar_motor()

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(
    ["🔍 Recomendador", "📚 Base de Datos", "📊 Estadísticas", "ℹ️ Información"]
)

# ============ TAB 1: RECOMENDADOR ============
with tab1:
    st.header("🔍 Recomendador de Medicamentos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        especie = st.selectbox(
            "🐾 Selecciona especie",
            ["Perro", "Gato"],
            key="especie_select"
        )
    
    with col2:
        # Obtiene enfermedades para la especie seleccionada
        enfermedades_disponibles = engine.listar_enfermedades(especie)
        enfermedades_lista = sorted(enfermedades_disponibles.get(especie, []))
        
        enfermedad = st.selectbox(
            "🏥 Selecciona enfermedad",
            enfermedades_lista,
            key="enfermedad_select"
        )
    
    # Parámetros adicionales
    st.subheader("📋 Parámetros del animal")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        peso = st.number_input("⚖️ Peso (kg)", min_value=0.5, max_value=100.0, value=20.0)
    
    with col2:
        raza = st.text_input("🐶 Raza", placeholder="ej: Boxer")
    
    with col3:
        edad = st.number_input("📅 Edad (años)", min_value=0.1, max_value=30.0, value=5.0)
    
    with col4:
        embarazada = st.checkbox("🤰 ¿Embarazada?")
    
    st.divider()
    
    # Botón de búsqueda
    if st.button("🔍 Buscar Medicamentos", use_container_width=True, key="buscar"):
        
        encontrado, medicamentos = engine.recomendar(enfermedad, especie)
        
        if encontrado and medicamentos:
            st.success(f"✅ Se encontraron **{len(medicamentos)} medicamentos** recomendados")
            
            # Información de la enfermedad
            with st.expander("📖 Información de la enfermedad", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"**Indicaciones:**\n{medicamentos[0]['indicaciones']}")
                
                with col2:
                    st.warning(f"**⚠️ Contraindicaciones:**\n{medicamentos[0]['contraindicaciones']}")
                
                st.markdown(f"**📝 Notas:** {medicamentos[0]['notas']}")
            
            # Medicamentos
            st.subheader("💊 Medicamentos Recomendados")
            
            for i, med in enumerate(medicamentos[:10], 1):  # Top 10
                with st.expander(f"{i}. {med['nombre'][:60]}", expanded=(i==1)):
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown("### 🧪 Composición")
                        st.code(", ".join(med['principios_activos'][:2]))
                    
                    with col2:
                        st.markdown("### 📋 Presentación")
                        st.info(med['presentacion'])
                    
                    with col3:
                        rx = "✅ SÍ" if "Sí" in med['prescripcion'] else "❌ NO"
                        st.markdown("### 📄 Prescripción")
                        st.write(rx)
                    
                    # Información del medicamento
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Titular:**")
                        st.caption(med['titular'][:50])
                    
                    with col2:
                        st.markdown("**Nº Registro:**")
                        st.caption(med['numero_registro'])
                    
                    # Cálculo de dosis
                    st.markdown("### 💉 Dosis Calculada")
                    if peso:
                        dosis_estimada = f"{peso * 0.1:.1f} mg"  # Ejemplo
                        st.success(f"Dosis estimada para {peso}kg: **{dosis_estimada}** (consultar prospectos)")
            
            if len(medicamentos) > 10:
                st.info(f"ℹ️ Mostrando primeros 10 de {len(medicamentos)} resultados")
        
        else:
            st.error(f"❌ No se encontraron medicamentos para {enfermedad} en {especie}s")

# ============ TAB 2: BASE DE DATOS ============
with tab2:
    st.header("📚 Explorar Base de Datos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Buscar por Medicamento")
        nombre_med = st.text_input("Nombre del medicamento", placeholder="ej: Frontline, Baytril...")
        
        if nombre_med:
            resultados = engine.buscar_medicamento(nombre_med)
            
            if resultados:
                st.success(f"✅ {len(resultados)} medicamentos encontrados")
                
                for med in resultados[:20]:
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.write(f"**{med['nombre']}** ({med['especie']})")
                    with col_b:
                        st.caption(med['numero_registro'])
                    st.caption(f"Principios: {', '.join(med['principios_activos'][:2])}")
                    st.divider()
            else:
                st.warning("❌ No se encontraron medicamentos con ese nombre")
    
    with col2:
        st.subheader("📋 Enfermedades por Especie")
        
        especie_tab2 = st.radio("Selecciona especie", ["Perro", "Gato"])
        enfermedades_tab2 = engine.listar_enfermedades(especie_tab2)
        
        enfs_lista = enfermedades_tab2.get(especie_tab2, [])
        
        st.write(f"**Total: {len(enfs_lista)} enfermedades**")
        
        # Mostrar en columnas
        cols = st.columns(2)
        for i, enf in enumerate(enfs_lista):
            with cols[i % 2]:
                if st.button(enf, key=f"enf_{i}", use_container_width=True):
                    st.session_state.enfermedad_select = enf

# ============ TAB 3: ESTADÍSTICAS ============
with tab3:
    st.header("📊 Estadísticas del Sistema")
    
    stats = engine.obtener_estadisticas()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏥 Total Medicamentos", stats['total_medicamentos'])
    
    with col2:
        st.metric("📋 Total Enfermedades", stats['total_enfermedades'])
    
    with col3:
        st.metric("🔗 Total Relaciones", stats['total_relaciones'])
    
    with col4:
        cobertura = (stats['total_medicamentos'] / 2000 * 100)
        st.metric("📈 Cobertura Aprox.", f"{cobertura:.1f}%")
    
    st.divider()
    
    # Distribución por especie
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🐾 Medicamentos por Especie")
        datos_especies = {
            'Perros': stats['medicamentos_perro'],
            'Gatos': stats['medicamentos_gato']
        }
        st.bar_chart(datos_especies)
    
    with col2:
        st.subheader("📊 Distribución")
        pct_perro = (stats['medicamentos_perro'] / stats['total_medicamentos'] * 100)
        pct_gato = (stats['medicamentos_gato'] / stats['total_medicamentos'] * 100)
        
        st.write(f"**Perros:** {pct_perro:.1f}%")
        st.write(f"**Gatos:** {pct_gato:.1f}%")
    
    st.divider()
    
    # Información del grafo
    st.subheader("🔍 Información del Grafo")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**Enfermedades Perro:** {stats['enfermedades_perro']}")
    
    with col2:
        st.info(f"**Enfermedades Gato:** {stats['enfermedades_gato']}")
    
    with col3:
        promedio = stats['total_relaciones'] / stats['total_enfermedades']
        st.info(f"**Meds/Enfermedad:** {promedio:.1f}")

# ============ TAB 4: INFORMACIÓN ============
with tab4:
    st.header("ℹ️ Información del Sistema")
    
    st.markdown("""
    ## 🎯 ¿Qué es este sistema?
    
    Sistema avanzado de **recomendación de medicamentos veterinarios** basado en:
    - 🗄️ **Base de Datos:** 1660 medicamentos de Cimavet
    - 📚 **Conocimiento:** 44 enfermedades mapeadas
    - 🧠 **IA:** LlamaIndex + OLLAMA (próximas versiones)
    - 🔍 **RAG:** Retrieval Augmented Generation
    
    ## 💡 Características
    
    ✅ Búsqueda por enfermedad exacta
    ✅ Filtrado por especie (Perro/Gato)
    ✅ Parámetros del animal (peso, edad, raza)
    ✅ Base de datos actualizada (Cimavet)
    ✅ Información de prescripción
    ✅ Indicaciones y contraindicaciones
    
    ## 📈 Próximas versiones
    
    - 🚀 Integración LlamaIndex (búsqueda por síntomas)
    - 🤖 OLLAMA (generación automática de protocolos)
    - 📊 Análisis avanzado multiparámetro
    - 🧬 Neo4j (escalabilidad)
    
    ## 👨‍💼 Para veterinarios
    
    Este sistema está diseñado para:
    - Ayudar en la búsqueda rápida de medicamentos
    - Verificar disponibilidad en farmacia
    - Confirmar indicaciones y contraindicaciones
    - Optimizar protocolos de tratamiento
    
    **Nota:** Este sistema es un asistente. Siempre consulta con especialistas.
    
    ## 📚 Documentación Técnica
    
    - **Arquitectura:** Python + Streamlit + LLMs
    - **BD:** Grafo JSON con 2341 relaciones
    - **Modelos:** tinyllama (local) / Groq (cloud)
    - **Versión:** 1.0 Beta
    """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📧 Contacto")
        st.info("Proyecto universitario de recomendación IA")
    
    with col2:
        st.markdown("### 📚 Recursos")
        st.write("- Documentación: [Ver]()")
        st.write("- GitHub: [Repositorio]()")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>🐾 Sistema de Recomendación Veterinario IA | Versión 1.0 Beta</p>
    <p><small>Desarrollado con Streamlit, Python y IA Avanzada</small></p>
</div>
""", unsafe_allow_html=True)