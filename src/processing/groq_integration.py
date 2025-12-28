import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqIntegration:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            # Puedes manejar esto mejor en producción, pero para debug imprime error
            print("❌ ERROR: No se encontró GROQ_API_KEY")
        
        self.client = Groq(api_key=self.api_key)

    def interpretar_consulta(self, consulta_usuario: str) -> dict:
        """
        Convierte texto libre en JSON estructurado.
        """
        system_prompt = """
        Eres un asistente veterinario técnico. 
        Tu ÚNICA función es traducir la consulta del usuario a datos estructurados JSON.
        
        FORMATO JSON ESPERADO:
        {
            "especie": "Perro" | "Gato" | "Ambos",
            "sintomas_clave": ["lista", "sintomas", "normalizados"],
            "raza_detectada": "nombre raza" | null,
            "peso_detectado_kg": float | null,
            "gravedad": "Alta" | "Media" | "Baja"
        }
        
        NORMALIZACIÓN:
        - "pota/vomita" -> "Vómito"
        - "caca blanda" -> "Diarrea"
        - "se rasca" -> "Prurito"
        """

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Consulta: {consulta_usuario}"}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Error interpretando: {e}")
            return {"especie": "Perro", "sintomas_clave": []}

    def generar_respuesta_final(self, consulta_usuario: str, hallazgos_medicos: dict) -> str:
        """
        Genera la respuesta final en texto para el veterinario.
        """
        contexto = json.dumps(hallazgos_medicos, indent=2, ensure_ascii=False)
        
        system_prompt = """
        Eres un ASISTENTE CLÍNICO VETERINARIO EXPERTO.
        Tu usuario es un VETERINARIO PROFESIONAL.
        
        OBJETIVO:
        Proveer un resumen técnico y sugerencias terapéuticas basadas en los datos recuperados.
        
        REGLAS:
        1. Sé directo y técnico (usa "Emesis" no "Vómitos", "Anorexia" no "no come").
        2. NO des consejos básicos de cuidado de mascotas.
        3. Resume los hallazgos de la base de datos interna.
        """

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Consulta: {consulta_usuario}\nContexto: {contexto}"}
                ],
                temperature=0.4
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generando respuesta: {e}"

