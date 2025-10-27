import json
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class SimpleSearchSystem:
    """
    Sistema de búsqueda INTELIGENTE (sin dependencias pesadas)
    Entiende lenguaje natural veterinario
    """
    
    def __init__(self, grafo_path: str):
        """Inicializa el sistema"""
        print("🔄 Inicializando Sistema de Búsqueda...\n")
        
        with open(grafo_path, 'r', encoding='utf-8') as f:
            self.grafo = json.load(f)
        
        self.medicamentos = self.grafo['medicamentos']
        self.enfermedades = self.grafo['enfermedades']
        
        # Crea corpus para búsqueda
        self._crear_corpus()
        print("✅ Sistema listo\n")
    
    def _crear_corpus(self):
        """Crea corpus de búsqueda"""
        self.corpus = []
        self.corpus_metadata = []
        
        for clave_enf, datos_enf in self.enfermedades.items():
            texto = f"{datos_enf['nombre']} {datos_enf['indicaciones']} {datos_enf['categoria']}"
            self.corpus.append(texto)
            self.corpus_metadata.append({
                'clave': clave_enf,
                'nombre': datos_enf['nombre'],
                'especie': datos_enf['especie'],
                'datos': datos_enf
            })
        
        # Vectorizador
        self.vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(2, 3))
        self.corpus_vectors = self.vectorizer.fit_transform(self.corpus)
    
    def buscar_por_sintomas(self, query: str, especie: str = "Perro") -> List[Dict]:
        """Busca enfermedades por síntomas"""
        print(f"🔍 Buscando: '{query}' en {especie}s\n")
        
        try:
            # Vectoriza query
            query_vector = self.vectorizer.transform([query])
            
            # Calcula similitud
            similarities = cosine_similarity(query_vector, self.corpus_vectors)[0]
            
            # Ordena por similitud
            top_indices = np.argsort(similarities)[::-1][:10]
            
            resultados = []
            
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Threshold mínimo
                    metadata = self.corpus_metadata[idx]
                    
                    if metadata['especie'] == especie:
                        datos_enf = metadata['datos']
                        meds_ids = datos_enf.get('medicamentos_asociados', [])
                        medicamentos = []
                        
                        for med_id in meds_ids[:5]:
                            med = self.medicamentos.get(med_id, {})
                            medicamentos.append({
                                'nombre': med.get('nombre'),
                                'principios_activos': med.get('principios_activos')
                            })
                        
                        resultados.append({
                            'enfermedad': datos_enf['nombre'],
                            'indicaciones': datos_enf['indicaciones'],
                            'medicamentos': medicamentos,
                            'num_meds': len(meds_ids),
                            'similitud': float(similarities[idx])
                        })
            
            return resultados
        
        except Exception as e:
            print(f"⚠️ Error: {e}")
            return []
    
    def buscar_multiples_sintomas(self, sintomas: List[str], especie: str = "Perro") -> Dict:
        """Busca para múltiples síntomas"""
        print(f"🔍 Analizando: {', '.join(sintomas)}\n")
        
        todas_enfermedades = {}
        medicamentos_comunes = {}
        
        for sintoma in sintomas:
            resultados = self.buscar_por_sintomas(sintoma, especie)
            
            for enf in resultados:
                nombre_enf = enf['enfermedad']
                
                if nombre_enf not in todas_enfermedades:
                    todas_enfermedades[nombre_enf] = {
                        'sintomas_coincidentes': [],
                        'medicamentos': {},
                        'indicaciones': enf['indicaciones']
                    }
                
                todas_enfermedades[nombre_enf]['sintomas_coincidentes'].append(sintoma)
                
                for med in enf['medicamentos']:
                    med_nombre = med['nombre']
                    if med_nombre not in medicamentos_comunes:
                        medicamentos_comunes[med_nombre] = {
                            'principios': med['principios_activos'],
                            'enfermedades': []
                        }
                    if nombre_enf not in medicamentos_comunes[med_nombre]['enfermedades']:
                        medicamentos_comunes[med_nombre]['enfermedades'].append(nombre_enf)
        
        return {
            'enfermedades_posibles': todas_enfermedades,
            'medicamentos_multiusos': medicamentos_comunes,
            'total_sintomas_analizados': len(sintomas)
        }


if __name__ == "__main__":
    sistema = SimpleSearchSystem(
        'data/knowledge_graph/mapeo_enfermedades_medicamentos.json'
    )
    
    print("="*80)
    print("🧪 TEST 1: Búsqueda por síntoma")
    print("="*80 + "\n")
    
    resultados = sistema.buscar_por_sintomas("dolor en extremidades", "Perro")
    
    if resultados:
        for enf in resultados[:3]:
            print(f"✅ {enf['enfermedad']} (similitud: {enf['similitud']:.2f})")
            print(f"   Medicamentos: {enf['num_meds']}")
            for med in enf['medicamentos'][:2]:
                print(f"   - {med['nombre']}")
            print()
    
    print("\n" + "="*80)
    print("🧪 TEST 2: Múltiples síntomas")
    print("="*80 + "\n")
    
    resultados_multi = sistema.buscar_multiples_sintomas(
        ["dolor", "picazón"],
        "Perro"
    )
    
    print(f"Enfermedades: {len(resultados_multi['enfermedades_posibles'])}")
    print(f"Medicamentos multiusos: {len(resultados_multi['medicamentos_multiusos'])}\n")
    
    for med_nombre, med_data in list(resultados_multi['medicamentos_multiusos'].items())[:3]:
        print(f"💊 {med_nombre}")
        print(f"   Para: {', '.join(med_data['enfermedades'])}")