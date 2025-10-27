import json
import ollama
from typing import Dict, List, Tuple
import re

class AdvancedRecommendationSystem:
    """
    Sistema AVANZADO de recomendación veterinaria con:
    - Análisis de lenguaje natural
    - Inferencia de múltiples enfermedades
    - Generación de protocolos con OLLAMA (tinyllama)
    - Análisis multiparámetro (peso, raza, edad)
    """
    
    def __init__(self, grafo_path: str):
        """Inicializa el sistema cargando el grafo"""
        print("🔄 Cargando sistema avanzado...")
        
        with open(grafo_path, 'r', encoding='utf-8') as f:
            self.grafo = json.load(f)
        
        self.medicamentos = self.grafo['medicamentos']
        self.enfermedades = self.grafo['enfermedades']
        self.relaciones = self.grafo['relaciones']
        
        print("✅ Sistema cargado:")
        print(f"   - {len(self.medicamentos)} medicamentos")
        print(f"   - {len(self.enfermedades)} enfermedades")
        print(f"   - {len(self.relaciones)} correlaciones\n")
    
    def extraer_parametros(self, texto_entrada: str) -> Dict:
        """Extrae parámetros de la entrada"""
        parametros = {
            'peso': None,
            'raza': None,
            'edad': None,
            'especie': 'Perro',  # Default
            'sintomas': [],
            'texto_original': texto_entrada
        }
        
        texto_lower = texto_entrada.lower()
        
        # Detecta especie
        if 'gato' in texto_lower or 'felino' in texto_lower:
            parametros['especie'] = 'Gato'
        
        # Extrae peso
        match_peso = re.search(r'(\d+)\s*kg', texto_lower)
        if match_peso:
            parametros['peso'] = int(match_peso.group(1))
        
        # Extrae edad
        match_edad = re.search(r'(\d+)\s*(años|meses)', texto_lower)
        if match_edad:
            parametros['edad'] = f"{match_edad.group(1)} {match_edad.group(2)}"
        
        # Detecta razas
        razas = ['boxer', 'labrador', 'golden', 'pastor', 'bulldog', 'cocker', 'chihuahua', 
                 'persa', 'siamés', 'bengalí', 'british', 'siberiano']
        for raza in razas:
            if raza in texto_lower:
                parametros['raza'] = raza.capitalize()
                break
        
        # Extrae síntomas
        sintomas_clave = {
            'dolor': ['dolor', 'duele', 'adolorido', 'extremidades'],
            'picazón': ['picazón', 'picor', 'rasca'],
            'otitis': ['oído', 'otitis'],
            'infección': ['infección', 'infectado'],
            'vómito': ['vomita', 'vómito'],
            'diarrea': ['diarrea'],
            'dermatitis': ['dermatitis', 'piel'],
            'cojera': ['cojera', 'cojea'],
            'fiebre': ['fiebre'],
            'tos': ['tos', 'tose']
        }
        
        for enfermedad, palabras in sintomas_clave.items():
            for palabra in palabras:
                if palabra in texto_lower:
                    parametros['sintomas'].append(enfermedad)
                    break
        
        return parametros
    
    def inferir_enfermedades(self, parametros: Dict) -> List[Tuple[str, float]]:
        """Infiere enfermedades basándose en síntomas y predisposición"""
        enfermedades_puntuadas = {}
        
        raza = parametros.get('raza', '').lower()
        sintomas = parametros.get('sintomas', [])
        
        # Predisposiciones por raza
        predisposiciones = {
            'boxer': ['Dolor/Inflamación articular', 'Insuficiencia cardíaca', 'Dermatitis alérgica'],
            'labrador': ['Dolor/Inflamación articular'],
            'pastor': ['Convulsiones/Epilepsia'],
            'bulldog': ['Dermatitis alérgica', 'Otitis externa'],
            'persa': ['Infección urinaria', 'Dermatitis alérgica']
        }
        
        # Mapeo síntomas → enfermedades
        mapeo_sintomas = {
            'dolor': ['Dolor/Inflamación articular', 'Otitis externa'],
            'picazón': ['Dermatitis alérgica', 'Sarna sarcóptica'],
            'otitis': ['Otitis externa'],
            'infección': ['Infección bacteriana sistémica', 'Infección urinaria'],
            'vómito': ['Gastroenteritis', 'Náuseas/Vómitos'],
            'diarrea': ['Gastroenteritis'],
            'dermatitis': ['Dermatitis alérgica'],
            'cojera': ['Dolor/Inflamación articular'],
            'fiebre': ['Infección bacteriana sistémica'],
            'tos': ['Problemas respiratorios crónicos']
        }
        
        # Puntuación por síntomas
        for sintoma in sintomas:
            if sintoma in mapeo_sintomas:
                for enf in mapeo_sintomas[sintoma]:
                    enfermedades_puntuadas[enf] = enfermedades_puntuadas.get(enf, 0) + 2
        
        # Bonus por predisposición
        if raza in predisposiciones:
            for enf in predisposiciones[raza]:
                enfermedades_puntuadas[enf] = enfermedades_puntuadas.get(enf, 0) + 1.5
        
        # Ordena
        return sorted(enfermedades_puntuadas.items(), key=lambda x: x[1], reverse=True)
    
    def buscar_medicamentos_multiples(self, enfermedades: List[str], especie: str) -> Dict:
        """Busca medicamentos para múltiples enfermedades"""
        resultado = {}
        
        for enfermedad in enfermedades:
            clave = f"{enfermedad}_{especie}"
            
            if clave in self.enfermedades:
                datos_enf = self.enfermedades[clave]
                meds_ids = datos_enf.get('medicamentos_asociados', [])
                
                if meds_ids:
                    medicamentos = []
                    for med_id in meds_ids[:5]:  # Top 5
                        med = self.medicamentos.get(med_id, {})
                        medicamentos.append({
                            'nombre': med.get('nombre'),
                            'principios': med.get('principios_activos'),
                        })
                    
                    resultado[enfermedad] = {
                        'medicamentos': medicamentos,
                        'indicaciones': datos_enf.get('indicaciones'),
                        'notas': datos_enf.get('notas')
                    }
        
        return resultado
    
    def generar_protocolo_ollama(self, parametros: Dict, 
                                enfermedades: List[Tuple[str, float]],
                                medicamentos_info: Dict) -> str:
        """Genera protocolo con OLLAMA tinyllama"""
        
        enfermedades_list = [e[0] for e in enfermedades[:3]]
        meds_texto = "\n".join([
            f"- {enf}: {', '.join([m['nombre'][:50] for m in info['medicamentos'][:3]])}"
            for enf, info in medicamentos_info.items()
        ])
        
        prompt = f"""Eres un veterinario experto. Genera un protocolo de tratamiento BREVE y PRÁCTICO.

CASO:
- Animal: {parametros.get('especie', 'Perro')} {parametros.get('raza', 'sin raza especificada')}
- Peso: {parametros.get('peso', 'N/A')} kg
- Edad: {parametros.get('edad', 'N/A')}
- Síntomas: {', '.join(parametros.get('sintomas', ['No especificados']))}

DIAGNÓSTICOS POSIBLES:
{chr(10).join([f"1. {e[0]}" for e in enfermedades[:3]])}

MEDICAMENTOS DISPONIBLES:
{meds_texto}

Genera:
1. Diagnóstico más probable (1 línea)
2. Protocolo de tratamiento (dosis, duración, vía)
3. Monitoreo (qué vigilar)
4. Cuándo mejoraría

Sé CONCISO Y PRÁCTICO."""
        
        try:
            response = ollama.generate(
                model="tinyllama",
                prompt=prompt,
                stream=False
            )
            return response['response']
        except Exception as e:
            return f"Error: {str(e)}"
    
    def procesar_caso(self, entrada: str) -> Dict:
        """Procesa un caso completo"""
        print("\n" + "="*80)
        print("🏥 PROCESANDO CASO VETERINARIO")
        print("="*80 + "\n")
        
        # Paso 1
        print("📝 Paso 1: Extrayendo parámetros...")
        parametros = self.extraer_parametros(entrada)
        print(f"   ✅ Especie: {parametros['especie']}")
        print(f"   ✅ Peso: {parametros['peso']} kg" if parametros['peso'] else "   ⚠️ Peso: No especificado")
        print(f"   ✅ Raza: {parametros['raza']}" if parametros['raza'] else "   ⚠️ Raza: No especificada")
        print(f"   ✅ Síntomas: {', '.join(parametros['sintomas']) if parametros['sintomas'] else 'No detectados'}\n")
        
        # Paso 2
        print("🔍 Paso 2: Infiriendo enfermedades posibles...")
        enfermedades = self.inferir_enfermedades(parametros)
        if enfermedades:
            for i, (enf, puntuacion) in enumerate(enfermedades[:3], 1):
                print(f"   {i}. {enf}")
        else:
            print("   ⚠️ No se infirieron enfermedades")
        print()
        
        # Paso 3
        print("💊 Paso 3: Buscando medicamentos...")
        medicamentos_info = self.buscar_medicamentos_multiples(
            [e[0] for e in enfermedades[:3]] if enfermedades else [],
            parametros['especie']
        )
        print(f"   ✅ {len(medicamentos_info)} enfermedades con medicamentos\n")
        
        # Paso 4
        print("🤖 Paso 4: Generando protocolo con OLLAMA (tinyllama)...")
        print("   ⏳ Procesando...\n")
        
        protocolo = self.generar_protocolo_ollama(parametros, enfermedades, medicamentos_info)
        
        print("✅ PROTOCOLO GENERADO:")
        print("="*80)
        print(protocolo)
        print("="*80 + "\n")
        
        return {
            'parametros': parametros,
            'enfermedades': enfermedades,
            'medicamentos': medicamentos_info,
            'protocolo': protocolo
        }


if __name__ == "__main__":
    sistema = AdvancedRecommendationSystem(
        'data/knowledge_graph/mapeo_enfermedades_medicamentos.json'
    )
    
    # Caso real
    caso = "Perro Boxer de 20 kg, 6 años, con dolor en extremidades traseras"
    
    resultado = sistema.procesar_caso(caso)