import json
import logging
from typing import Dict, List, Any
from pathlib import Path

# Importamos la integración con Groq que acabamos de crear
from processing.groq_integration import GroqIntegration

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Intentamos importar tu loader de enfermedades existente
try:
    from processing.enfermedades_loader import EnfermedadesLoader
    ENFERMEDADES_DISPONIBLES = True
except ImportError:
    # Intento de importación local si cambia la estructura de carpetas
    try:
        from enfermedades_loader import EnfermedadesLoader
        ENFERMEDADES_DISPONIBLES = True
    except ImportError:
        ENFERMEDADES_DISPONIBLES = False
        logger.warning("⚠️ No se pudo cargar EnfermedadesLoader. La búsqueda será limitada.")

class SmartRecommendationEngine:
    def __init__(self, 
                 grafo_path: str = "data/knowledge_graph/mapeo_enfermedades_medicamentos.json",
                 dosis_path: str = "data/knowledge_graph/dosis_medicamentos.json",
                 razas_path: str = "data/knowledge_graph/razas_predisposiciones.json",
                 categorias_path: str = "data/knowledge_graph/categorias_medicamentos.json"):
        
        logger.info("🚀 Inicializando SmartRecommendationEngine con Cerebro Groq...")
        
        # 1. Cargar Datos JSON (Tu "Grafo de Conocimiento")
        self.medicamentos, self.enfermedades_data, self.relaciones = self._cargar_grafo(grafo_path)
        self.dosis = self._cargar_json_simple(dosis_path)
        self.razas = self._cargar_json_simple(razas_path)
        self.categorias = self._cargar_json_simple(categorias_path).get('categorias', {})
        
        # 2. Inicializar componentes inteligentes
        self.groq = GroqIntegration()
        
        self.enfermedades_loader = None
        if ENFERMEDADES_DISPONIBLES:
            self.enfermedades_loader = EnfermedadesLoader()
            logger.info("✅ Loader de enfermedades activado y listo.")

    def _cargar_grafo(self, path: str):
        """Carga el archivo principal mapeo_enfermedades_medicamentos.json"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('medicamentos', {}), data.get('enfermedades', {}), data.get('relaciones', [])
        except Exception as e:
            logger.error(f"❌ Error cargando grafo principal: {e}")
            return {}, {}, []

    def _cargar_json_simple(self, path: str):
        """Helper para cargar JSONs simples"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Error cargando {path}: {e}")
            return {}

    def procesar_consulta_chat(self, texto_consulta: str) -> Dict[str, Any]:
        """
        FLUJO PRINCIPAL INTELIGENTE:
        1. Groq interpreta la intención (Texto -> JSON).
        2. El Engine busca en los archivos locales usando los datos de Groq.
        3. Groq redacta la respuesta final (Datos -> Texto).
        """
        logger.info(f"🧠 Procesando consulta: {texto_consulta}")

        # PASO 1: INTERPRETACIÓN (GROQ)
        # Le pedimos a Groq que estandarice la consulta (ej: "pota" -> "Vómito")
        datos_estructurados = self.groq.interpretar_consulta(texto_consulta)
        
        # Extraer variables limpias de la IA
        sintomas_ia = datos_estructurados.get("sintomas_clave", [])
        especie_ia = datos_estructurados.get("especie", "Perro")
        raza_ia = datos_estructurados.get("raza_detectada")
        peso_ia = datos_estructurados.get("peso_detectado_kg")
        
        logger.info(f"🔍 Datos extraídos por IA: {sintomas_ia} | Especie: {especie_ia}")

        # PASO 2: BÚSQUEDA EN BASE DE DATOS LOCAL (USANDO DATOS DE IA)
        hallazgos_medicos = {
            "parametros_paciente": datos_estructurados,
            "enfermedades": [],
            "medicamentos": []
        }

        # 2.1 Buscar Enfermedades coincidentes en tus JSON
        if self.enfermedades_loader and sintomas_ia:
            # Usamos tu loader existente pero con los síntomas LIMPIOS que nos dio Groq
            enfermedades_match = self.enfermedades_loader.obtener_enfermedades_por_sintomas(
                sintomas_ia, 
                especie_ia
            )
            
            # Formatear enfermedades para el contexto
            for enf in enfermedades_match:
                hallazgos_medicos["enfermedades"].append({
                    "nombre": enf.get("nombre"),
                    "confianza": enf.get("confianza"),
                    "descripcion": enf.get("indicaciones"),
                    "notas": enf.get("notas")
                })
                
                # 2.2 Buscar Medicamentos asociados a esas enfermedades
                ids_meds = enf.get("medicamentos_asociados", [])
                
                # Tomamos solo los top 5 medicamentos por enfermedad para no saturar
                for med_id in ids_meds[:5]: 
                    if med_id in self.medicamentos:
                        med_data = self.medicamentos[med_id]
                        
                        # Filtrar por especie (Seguridad)
                        especie_med = med_data.get("especie", "").upper()
                        if especie_ia.upper() in especie_med or "AMBOS" in especie_med or "PERRO" in especie_med and "GATO" in especie_med:
                            
                            hallazgos_medicos["medicamentos"].append({
                                "nombre": med_data.get("nombre"),
                                "principios_activos": med_data.get("principios_activos"),
                                "prescripcion": med_data.get("prescripcion"),
                                "forma_farmaceutica": med_data.get("presentacion")
                            })

        # PASO 3: GENERACIÓN DE RESPUESTA (GROQ)
        # Enviamos los hallazgos de tus JSON a Groq para que redacte la respuesta final
        respuesta_final_ia = self.groq.generar_respuesta_final(texto_consulta, hallazgos_medicos)

        # Devolvemos estructura completa para que Streamlit pueda mostrar lo que quiera
        return {
            "respuesta_texto": respuesta_final_ia, # El texto bonito para el chat
            "datos_tecnicos": hallazgos_medicos,   # Los datos crudos para debugging o paneles laterales
            "parametros_ia": datos_estructurados   # Lo que entendió la IA
        }

    # Métodos legacy para compatibilidad con la interfaz antigua si se necesitan
    # (Mantener estos evita que se rompa la pestaña "Base de Datos" si la usas)
    def calcular_dosis_texto(self, med_data, peso):
        # ... Tu lógica original de calcular dosis puede mantenerse aquí si se usa en otro lado ...
        return "Dosis a consultar con veterinario."

