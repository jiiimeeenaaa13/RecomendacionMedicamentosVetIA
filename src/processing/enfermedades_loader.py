import json
import re
from typing import List, Dict, Tuple
from pathlib import Path
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)

class EnfermedadesLoader:
    """Motor ULTRA INTELIGENTE - Reconoce TODO sin fallar"""
    
    def __init__(self):
        self.data_path = Path('data/knowledge_graph/enfermedades_42_completo.json')
        self.enfermedades = self._cargar_enfermedades()
        
        # 🔥 DICCIONARIOS DE SINÓNIMOS MASIVOS
        self.sinonimos_sintomas = self._construir_sinonimos_sintomas()
        
        # 🔥 ÍNDICE INTELIGENTE
        self.indice_busqueda = self._construir_indice_inteligente()
        
        logger.info(f"✅ {len(self.enfermedades)} enfermedades cargadas")
        logger.info(f"✅ {len(self.indice_busqueda)} términos indexados")
    
    def _cargar_enfermedades(self) -> Dict:
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('enfermedades', {})
        except Exception as e:
            logger.error(f"Error cargando enfermedades: {e}")
            return {}
    
    def _construir_sinonimos_sintomas(self) -> Dict[str, List[str]]:
        """🔥 MEGA DICCIONARIO DE SINÓNIMOS"""
        return {
            'otitis': ['otitis', 'otiti', 'oído', 'oidos', 'oido', 'orejas', 'oreja', 'auricular', 
                       'infección oído', 'infeccion oido', 'infeccion oreja', 'pus oreja', 
                       'sacude cabeza', 'rasca oreja', 'olor oídos', 'cerumen', 'dolor oreja'],
            
            'ojos': ['ojos', 'ojo', 'conjuntivitis', 'conjuntibitis', 'legañas', 'legaña', 
                     'infección ocular', 'infeccion ocular', 'infeccion ojo', 'infeccion ojos',
                     'ojo rojo', 'ojos rojos', 'lagrimeo', 'secreción ocular', 'pus ojos'],
            
            'dolor': ['dolor', 'artrosis', 'artritis', 'displasia', 'cojera', 'rigidez', 'caderas',
                      'dificultad levantarse', 'cojea', 'articulación', 'articulacion', 'cadera'],
            
            'piel': ['piel', 'dermatitis', 'alergia', 'picor', 'picazón', 'ronchas', 'rasca mucho',
                     'se rasca', 'prurito', 'alopecia', 'pérdida pelo', 'perdida pelo'],
            
            'pulgas': ['pulgas', 'pulga', 'parásitos', 'parasitos', 'garrapatas', 'garrapata',
                       'puntitos negros', 'bichitos'],
            
            'infección': ['infección', 'infeccion', 'bacteria', 'bacterias', 'fiebre', 'pus',
                          'herida infectada', 'inflamación', 'inflamacion'],
            
            'diarrea': ['diarrea', 'heces blandas', 'gastro', 'gastroenteritis', 'vientre suelto'],
            
            'vómito': ['vómito', 'vomito', 'devuelve', 'náuseas', 'nauseas', 'arcadas', 'no come'],
            
            'orina': ['orina', 'pipí', 'pipi', 'cistitis', 'urinaria', 'orina sangre', 'pis'],
            
            'gusanos': ['gusanos', 'lombrices', 'parásitos intestinales', 'desparasitar'],
        }
    
    def _construir_indice_inteligente(self) -> Dict[str, List[str]]:
        """Construye índice con TODOS los sinónimos"""
        indice = {}
        
        for enf_key, enf_data in self.enfermedades.items():
            nombre = enf_data.get('nombre', '').lower()
            
            # Indexar nombre completo
            if nombre:
                self._agregar_al_indice(indice, nombre, enf_key)
                
                # Indexar cada palabra del nombre
                palabras = nombre.split()
                for palabra in palabras:
                    if len(palabra) > 3:
                        self._agregar_al_indice(indice, palabra, enf_key)
            
            # Indexar keywords específicos
            keywords = self._obtener_keywords_enfermedad(enf_key, enf_data)
            for keyword in keywords:
                self._agregar_al_indice(indice, keyword, enf_key)
            
            # 🔥 INDEXAR TODOS LOS SINÓNIMOS RELEVANTES
            for sintoma_base, lista_sinonimos in self.sinonimos_sintomas.items():
                # Si la enfermedad contiene el síntoma base, indexar TODOS sus sinónimos
                if sintoma_base in nombre:
                    for sinonimo in lista_sinonimos:
                        self._agregar_al_indice(indice, sinonimo, enf_key)
        
        return indice
    
    def _agregar_al_indice(self, indice: Dict, termino: str, enf_key: str):
        """Agrega término al índice"""
        termino = termino.lower().strip()
        if termino not in indice:
            indice[termino] = []
        if enf_key not in indice[termino]:
            indice[termino].append(enf_key)
    
    def _obtener_keywords_enfermedad(self, enf_key: str, enf_data: Dict) -> List[str]:
        """Keywords manuales críticos"""
        nombre = enf_data.get('nombre', '').lower()
        keywords = []
        
        if 'otitis' in nombre or 'externa' in nombre:
            keywords.extend(['otitis', 'otiti', 'oído', 'oidos', 'oido', 'oreja', 'orejas', 
                            'infeccion oido', 'infeccion oreja', 'pus oreja'])
        
        if 'ojos' in nombre or 'ocular' in nombre or 'conjuntiv' in nombre:
            keywords.extend(['ojos', 'ojo', 'conjuntivitis', 'infeccion ojos', 'infeccion ojo',
                            'ojo rojo', 'ojos rojos', 'legañas'])
        
        if 'dolor' in nombre or 'articular' in nombre or 'inflamación' in nombre:
            keywords.extend(['dolor', 'artrosis', 'artritis', 'displasia', 'cojera', 'caderas', 'cadera'])
        
        if 'pulgas' in nombre:
            keywords.extend(['pulgas', 'pulga', 'picazón', 'rasca'])
        
        if 'diarrea' in nombre or 'gastro' in nombre:
            keywords.extend(['diarrea', 'heces', 'gastro', 'vomito', 'vómito'])
        
        if 'urinaria' in nombre or 'cistitis' in nombre:
            keywords.extend(['orina', 'cistitis', 'pipí', 'pipi', 'pis'])
        
        if 'bacteriana' in nombre or 'infección' in nombre:
            keywords.extend(['infeccion', 'infección', 'bacteria', 'fiebre', 'pus'])
        
        return keywords
    
    def normalizar_texto(self, texto: str) -> List[str]:
        """Expande texto con TODOS los sinónimos posibles"""
        texto_lower = texto.lower().strip()
        terminos_expandidos = set()
        
        # Agregar texto original
        terminos_expandidos.add(texto_lower)
        
        # Agregar palabras individuales
        palabras = texto_lower.split()
        for palabra in palabras:
            if len(palabra) > 2:  # Incluir palabras cortas también
                terminos_expandidos.add(palabra)
        
        # 🔥 EXPANDIR CON SINÓNIMOS
        for sintoma_base, lista_sinonimos in self.sinonimos_sintomas.items():
            for sinonimo in lista_sinonimos:
                # Si encuentra el sinónimo en el texto, agregar TODOS los relacionados
                if sinonimo in texto_lower or texto_lower in sinonimo:
                    terminos_expandidos.update(lista_sinonimos)
                    terminos_expandidos.add(sintoma_base)
                    break
        
        # 🔥 BÚSQUEDA FUZZY AGRESIVA para errores tipográficos
        for palabra in palabras:
            if len(palabra) > 3:
                for sintoma_base, lista_sinonimos in self.sinonimos_sintomas.items():
                    # Buscar similitud con el síntoma base
                    if SequenceMatcher(None, palabra, sintoma_base).ratio() > 0.75:
                        terminos_expandidos.update(lista_sinonimos)
                        terminos_expandidos.add(sintoma_base)
                    
                    # Buscar similitud con cada sinónimo
                    for sinonimo in lista_sinonimos:
                        if SequenceMatcher(None, palabra, sinonimo).ratio() > 0.75:
                            terminos_expandidos.update(lista_sinonimos)
                            terminos_expandidos.add(sintoma_base)
                            break
        
        return list(terminos_expandidos)
    
    def buscar_enfermedades_fuzzy(self, texto_usuario: str, especie: str) -> List[str]:
        """Búsqueda ULTRA INTELIGENTE con scoring"""
        texto_lower = texto_usuario.lower().strip()
        candidatos = {}
        
        # 1. Normalizar texto (expande con sinónimos)
        terminos_expandidos = self.normalizar_texto(texto_usuario)
        
        logger.info(f"🔍 Términos expandidos: {terminos_expandidos[:10]}...")  # Solo primeros 10 para log
        
        # 2. Búsqueda directa en nombres de enfermedades (Score: 1.0)
        for enf_key, enf_data in self.enfermedades.items():
            nombre = enf_data.get('nombre', '').lower()
            
            for termino in terminos_expandidos:
                if termino in nombre or nombre in termino:
                    candidatos[enf_key] = candidatos.get(enf_key, 0) + 1.0
        
        # 3. Búsqueda en índice inteligente (Score: 0.9)
        for termino in terminos_expandidos:
            if termino in self.indice_busqueda:
                for enf_key in self.indice_busqueda[termino]:
                    candidatos[enf_key] = candidatos.get(enf_key, 0) + 0.9
        
        # 4. Búsqueda parcial en índice (Score: 0.7)
        for termino in terminos_expandidos:
            for termino_index in self.indice_busqueda:
                if termino in termino_index or termino_index in termino:
                    for enf_key in self.indice_busqueda[termino_index]:
                        candidatos[enf_key] = candidatos.get(enf_key, 0) + 0.7
        
        # 5. Filtrar por especie
        enfermedades_filtradas = {}
        for enf_key, score in candidatos.items():
            enf_data = self.enfermedades.get(enf_key)
            if enf_data:
                especie_enf = enf_data.get('especie', '').lower()
                if especie.lower() in especie_enf or 'ambos' in especie_enf:
                    enfermedades_filtradas[enf_key] = score
        
        # 6. Ordenar por score (descendente)
        enfermedades_ordenadas = sorted(
            enfermedades_filtradas.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # 7. Umbral BAJO para ser más permisivo (0.5 en lugar de 0.6)
        enfermedades_relevantes = [
            (enf_key, score) for enf_key, score in enfermedades_ordenadas 
            if score >= 0.5
        ]
        
        logger.info(f"🔍 '{texto_usuario}' → Candidatos: {len(candidatos)} | Relevantes: {len(enfermedades_relevantes)}")
        
        # Devolver top 3
        return [enf_key for enf_key, score in enfermedades_relevantes[:3]]
    
    def obtener_enfermedades_por_sintomas(self, sintomas: List[str], especie: str) -> List[Dict]:
        """Método principal: Devuelve enfermedades con medicamentos"""
        texto_completo = " ".join(sintomas)
        enfermedades_keys = self.buscar_enfermedades_fuzzy(texto_completo, especie)
        
        resultado = []
        for enf_key in enfermedades_keys:
            enf_data = self.enfermedades.get(enf_key)
            if enf_data:
                resultado.append({
                    'key': enf_key,
                    'nombre': enf_data.get('nombre'),
                    'categoria': enf_data.get('categoria'),
                    'especie': enf_data.get('especie'),
                    'indicaciones': enf_data.get('indicaciones', ''),
                    'contraindicaciones': enf_data.get('contraindicaciones', ''),
                    'notas': enf_data.get('notas', ''),
                    'medicamentos_asociados': enf_data.get('medicamentos_asociados', []),
                    'confianza': 0.95
                })
        
        logger.info(f"✅ Devolviendo {len(resultado)} enfermedades")
        return resultado
    
    def listar_sintomas(self) -> List[str]:
        """Devuelve todos los términos indexados"""
        return list(self.indice_busqueda.keys())
