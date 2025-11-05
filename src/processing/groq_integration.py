import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqIntegration:
    """Integración con Groq API + búsqueda en datos locales"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError("GROQ_API_KEY no encontrada en .env")
        
        self.client = Groq(api_key=api_key)
        self.cargar_datos()
        print("✅ Groq conectado + Datos cargados\n")
    
    def cargar_datos(self):
        """Carga tus JSONs de medicamentos"""
        try:
            with open('data/knowledge_graph/mapeo_enfermedades_medicamentos.json', 'r', encoding='utf-8') as f:
                self.grafo = json.load(f)
                self.medicamentos = self.grafo.get('medicamentos', {})
                self.enfermedades = self.grafo.get('enfermedades', {})
            print(f"✅ Cargados {len(self.medicamentos)} medicamentos")
        except Exception as e:
            print(f"⚠️ Error cargando datos: {e}")
            self.medicamentos = {}
            self.enfermedades = {}
    
    def buscar_en_datos(self, pregunta: str) -> str:
        """Busca respuesta en tus datos locales"""
        
        pregunta_lower = pregunta.lower()
        
        # Buscar medicamentos por nombre
        for med_id, med in self.medicamentos.items():
            nombre = med.get('nombre', '').lower()
            for palabra in pregunta_lower.split():
                if len(palabra) > 3 and palabra in nombre:
                    # Encontró medicamento
                    info = "ENCONTRADO EN MIS DATOS:\n"
                    info += "Medicamento: " + med.get('nombre', 'N/A') + "\n"
                    info += "Principios: " + ", ".join(med.get('principios_activos', [])) + "\n"
                    info += "Presentacion: " + med.get('presentacion', 'N/A') + "\n"
                    info += "Titular: " + med.get('titular', 'N/A') + "\n"
                    return info
        
        return None
    
    def generar_respuesta(self, pregunta: str, contexto: str = "", temperatura: float = 0.7, max_tokens: int = 500) -> str:
        
        # PASO 1: Busca en datos locales primero
        respuesta_local = self.buscar_en_datos(pregunta)
        if respuesta_local:
            return respuesta_local
        
        # PASO 2: Si no encuentra, usa Groq
        if contexto:
            prompt = "Eres un veterinario experto en farmacologia animal.\n\nCONTEXTO: " + contexto + "\n\nPREGUNTA: " + pregunta + "\n\nResponde de forma clara, profesional y concisa. Maximo 200 palabras. SIEMPRE incluye: Consulta con un veterinario profesional para diagnostico."
        else:
            prompt = "Eres un veterinario experto.\n\nPREGUNTA: " + pregunta + "\n\nResponde de forma clara y profesional. Maximo 150 palabras."
        
        try:
            response = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperatura,
                max_tokens=max_tokens
            )
            
            respuesta = response.choices[0].message.content
            return respuesta
        
        except Exception as e:
            return "Error con Groq: " + str(e) + ". Verifica tu API KEY en .env"