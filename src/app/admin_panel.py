import streamlit as st
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

st.set_page_config(page_title="Panel Admin - Vet-IA", page_icon="⚙️", layout="wide")

# Login simple
if 'admin_logged' not in st.session_state:
    st.session_state.admin_logged = False

if not st.session_state.admin_logged:
    st.title("🔐 Panel de Administración")
    pwd = st.text_input("Contraseña de Admin", type="password")
    if st.button("Entrar"):
        if pwd == "veterinaria":  # Cambia esto
            st.session_state.admin_logged = True
            st.rerun()
        else:
            st.error("❌ Contraseña incorrecta")
    st.stop()

# ======== PANEL PRINCIPAL ========
st.title("⚙️ Panel de Administración Veterinaria")

tabs = st.tabs(["➕ Añadir Enfermedad", "➕ Añadir Síntoma", "📊 Ver Base de Datos"])

# TAB 1: Añadir Enfermedad
with tabs[0]:
    st.header("Nueva Enfermedad")
    
    with st.form("nueva_enfermedad"):
        nombre = st.text_input("Nombre de la enfermedad")
        especie = st.selectbox("Especie", ["Perro", "Gato", "Ambos"])
        categoria = st.selectbox("Categoría", ["Dermatología", "Oftalmología", "Otología", "Parasitología", "Gastrointestinal", "Otros"])
        
        sintomas = st.text_area("Síntomas (uno por línea)")
        medicamentos = st.text_area("Medicamentos asociados (IDs, uno por línea)")
        
        if st.form_submit_button("💾 Guardar Enfermedad"):
            try:
                # Cargar JSON existente
                with open('data/knowledge_graph/enfermedades_42_completo.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Crear nueva enfermedad
                nueva_key = f"ENF_{len(data['enfermedades']) + 1:03d}"
                data['enfermedades'][nueva_key] = {
                    "nombre": nombre,
                    "especie": especie,
                    "categoria": categoria,
                    "sintomas": [s.strip() for s in sintomas.split('\n') if s.strip()],
                    "medicamentos_asociados": [m.strip() for m in medicamentos.split('\n') if m.strip()]
                }
                
                # Guardar
                with open('data/knowledge_graph/enfermedades_42_completo.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                st.success(f"✅ Enfermedad '{nombre}' añadida con ID: {nueva_key}")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Error: {e}")

# TAB 2: Añadir Síntoma
with tabs[1]:
    st.header("Nuevo Síntoma-Enfermedad")
    
    with st.form("nuevo_sintoma"):
        sintoma = st.text_input("Síntoma (ej: 'Cojera persistente')")
        enfermedades_asociadas = st.text_area("Enfermedades que causan este síntoma (una por línea)")
        
        if st.form_submit_button("💾 Guardar Síntoma"):
            try:
                with open('data/knowledge_graph/sintomas_enfermedades_mapping.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                data['sintomas_enfermedades'][sintoma] = [
                    e.strip() for e in enfermedades_asociadas.split('\n') if e.strip()
                ]
                
                with open('data/knowledge_graph/sintomas_enfermedades_mapping.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                st.success(f"✅ Síntoma '{sintoma}' añadido")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# TAB 3: Ver Base de Datos
with tabs[2]:
    st.header("📊 Estadísticas de la Base de Datos")
    
    try:
        with open('data/knowledge_graph/enfermedades_42_completo.json', 'r', encoding='utf-8') as f:
            enf_data = json.load(f)
        
        st.metric("Total Enfermedades", len(enf_data['enfermedades']))
        
        with open('data/knowledge_graph/sintomas_enfermedades_mapping.json', 'r', encoding='utf-8') as f:
            sint_data = json.load(f)
        
        st.metric("Total Síntomas", len(sint_data['sintomas_enfermedades']))
        
        st.divider()
        st.subheader("Últimas 5 Enfermedades")
        for key in list(enf_data['enfermedades'].keys())[-5:]:
            with st.expander(f"{key}: {enf_data['enfermedades'][key]['nombre']}"):
                st.json(enf_data['enfermedades'][key])
    except Exception as e:
        st.error(f"❌ Error cargando datos: {e}")
