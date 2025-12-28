import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqIntegration:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def generar_respuesta(self, consulta_usuario: str, contexto_tecnico: str) -> str:
        """
        Ya NO busca datos. Solo redacta una respuesta bonita.
        """
        system_prompt = """
        Eres un asistente veterinario experto basado en la base de datos CIMAVET.
        Tu trabajo es interpretar los DATOS TÉCNICOS proporcionados y explicárselos al usuario.
        
        REGLAS:
        1. Usa SOLO la información provista en el bloque CONTEXTO TÉCNICO.
        2. Si hay advertencias de raza (ej: Collie y Ivermectina), RESÁLTALAS.
        3. Si se calculó una dosis, indícala como "Dosis teórica estimada".
        4. SIEMPRE termina recomendando visita presencial.
        """
        
        user_message = f"""
        PREGUNTA DEL USUARIO: {consulta_usuario}
        
        CONTEXTO TÉCNICO (Recuperado de base de datos):
        {contexto_tecnico}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile", # O Llama-3.1-70b
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.5, # Bajamos temperatura para que sea más fiel a los datos
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error de conexión con IA: {e}"