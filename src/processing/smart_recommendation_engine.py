"""
Motor de recomendación INTELIGENTE que:
- Filtra TOP 10 medicamentos (no 34)
- Calcula dosis exacta por peso
- Considera predisposiciones de raza
- Extrae parámetros de texto natural
- Compatible con ambas interfaces (Chat + Clásico)
"""

import json
import re
from typing import Dict, List, Tuple
from pathlib import Path

class SmartRecommendationEngine:
    def __init__(self, 
                 grafo_path: str = 'data/knowledge_graph/mapeo_enfermedades_medicamentos.json',
                 dosis_path: str = 'data/knowledge_graph/dosis_medicamentos.json',
                 razas_path: str = 'data/knowledge_graph/razas_predisposiciones.json',
                 categorias_path: str = 'data/knowledge_graph/categorias_medicamentos.json'):
        
        print("🔄 Cargando motor inteligente...")
        
        # Cargar grafo principal
        with open(grafo_path, 'r', encoding='utf-8') as f:
            grafo = json.load(f)
        
        self.medicamentos = grafo['medicamentos']
        self.enfermedades = grafo['enfermedades']
        self.relaciones = grafo['relaciones']
        
        # Cargar dosis
        try:
            with open(dosis_path, 'r', encoding='utf-8') as f:
                self.dosis = json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Archivo de dosis no encontrado: {dosis_path}")
            self.dosis = {}
        
        # Cargar razas
        try:
            with open(razas_path, 'r', encoding='utf-8') as f:
                self.razas = json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Archivo de razas no encontrado: {razas_path}")
            self.razas = {}
        
        # Cargar categorías
        try:
            with open(categorias_path, 'r', encoding='utf-8') as f:
                self.categorias = json.load(f)['categorias']
        except FileNotFoundError:
            print(f"⚠️ Archivo de categorías no encontrado: {categorias_path}")
            self.categorias = {}
        
        print(f"✅ Motor cargado:")
        print(f"   - {len(self.medicamentos)} medicamentos")
        print(f"   - {len(self.enfermedades)} enfermedades")
        print(f"   - {len(self.dosis)} categorías de dosis")
        print(f"   - {len(self.razas)} razas\n")
    
    # ========== MÉTODOS COMPATIBILIDAD BÁSICA ==========
    
    def listar_enfermedades(self, especie: str = None) -> Dict[str, List[str]]:
        """Lista todas las enfermedades disponibles (compatible con motor básico)"""
        resultado = {}
        
        for clave_enf, datos in self.enfermedades.items():
            esp = datos['especie']
            
            if especie and esp != especie:
                continue
            
            if esp not in resultado:
                resultado[esp] = []
            
            resultado[esp].append(datos['nombre'])
        
        # Ordena alfabéticamente
        for esp in resultado:
            resultado[esp] = sorted(list(set(resultado[esp])))
        
        return resultado
    
    def buscar_medicamento(self, nombre: str) -> List[Dict]:
        """Busca un medicamento por nombre"""
        nombre_lower = nombre.lower()
        resultados = []
        
        for med_id, med in self.medicamentos.items():
            if nombre_lower in med['nombre'].lower():
                resultados.append({
                    'id': med_id,
                    'nombre': med['nombre'],
                    'numero_registro': med['numero_registro'],
                    'principios_activos': med['principios_activos'],
                    'especie': med['especie'],
                    'prescripcion': med['prescripcion'],
                    'estado': med['estado']
                })
        
        return resultados
    
    def recomendar(self, enfermedad: str, especie: str) -> Tuple[bool, List[Dict]]:
        """Recomienda medicamentos para una enfermedad (compatible con motor básico)"""
        clave_enf = f"{enfermedad}_{especie}"
        
        if clave_enf not in self.enfermedades:
            return False, []
        
        datos_enfermedad = self.enfermedades[clave_enf]
        med_ids = datos_enfermedad['medicamentos_asociados']
        
        if not med_ids:
            return False, []
        
        # Obtiene datos completos de los medicamentos
        medicamentos_recomendados = []
        
        for med_id in med_ids[:10]:  # Limita a TOP 10
            med = self.medicamentos.get(med_id, {})
            
            medicamentos_recomendados.append({
                'nombre': med.get('nombre'),
                'numero_registro': med.get('numero_registro'),
                'principios_activos': med.get('principios_activos', []),
                'presentacion': med.get('presentacion'),
                'titular': med.get('titular'),
                'prescripcion': med.get('prescripcion'),
                'estado': med.get('estado'),
                'fecha_comercializado': med.get('fecha_comercializado'),
                'especie': med.get('especie'),
                'indicaciones': datos_enfermedad.get('indicaciones'),
                'contraindicaciones': datos_enfermedad.get('contraindicaciones'),
                'notas': datos_enfermedad.get('notas'),
                'categoria': datos_enfermedad.get('categoria')
            })
        
        return True, medicamentos_recomendados
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas del grafo"""
        meds_perro = sum(1 for m in self.medicamentos.values() if m['especie'] == 'Perro')
        meds_gato = sum(1 for m in self.medicamentos.values() if m['especie'] == 'Gato')
        
        enfs_perro = sum(1 for e in self.enfermedades.values() if e['especie'] == 'Perro')
        enfs_gato = sum(1 for e in self.enfermedades.values() if e['especie'] == 'Gato')
        
        return {
            'total_medicamentos': len(self.medicamentos),
            'medicamentos_perro': meds_perro,
            'medicamentos_gato': meds_gato,
            'total_enfermedades': len(self.enfermedades),
            'enfermedades_perro': enfs_perro,
            'enfermedades_gato': enfs_gato,
            'total_relaciones': len(self.relaciones)
        }
    
    # ========== MÉTODOS INTELIGENTES (NUEVOS) ==========
    
    def extraer_parametros_texto(self, texto: str) -> Dict:
        """Extrae parámetros de texto natural"""
        
        params = {
            'raza': None,
            'peso': None,
            'edad': None,
            'especie': 'Perro',
            'sintomas': [],
            'condicion': 'normal'
        }
        
        texto_lower = texto.lower()
        
        # Detectar especie
        if 'gato' in texto_lower or 'felino' in texto_lower:
            params['especie'] = 'Gato'
        
        # Extraer peso
        match_peso = re.search(r'(\d+(?:\.?\d+)?)\s*(?:kg|kilogramos?)', texto_lower)
        if match_peso:
            params['peso'] = float(match_peso.group(1))
        
        # Extraer edad
        match_edad = re.search(r'(\d+)\s*(años|meses|semanas)', texto_lower)
        if match_edad:
            params['edad'] = f"{match_edad.group(1)} {match_edad.group(2)}"
        
        # Detectar razas (sin considerar tildes)
        razas_keys = list(self.razas.keys())
        texto_normalizado = texto_lower.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        
        for raza in razas_keys:
            raza_normalizada = raza.lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            if raza_normalizada in texto_normalizado:
                params['raza'] = raza
                break
        
        # Detectar síntomas
        sintomas_mapping = {
            'picazón': ['picazón', 'picor', 'rasca', 'rascado'],
            'vómito': ['vomita', 'vómito', 'vomitar'],
            'diarrea': ['diarrea', 'deposiciones'],
            'otitis': ['oído', 'otitis', 'oreja'],
            'dolor': ['dolor', 'adolorido', 'cojera', 'cojea', 'caderas', 'articular'],
            'dermatitis': ['dermatitis', 'piel', 'herida'],
            'tos': ['tos', 'tose', 'toser'],
            'fiebre': ['fiebre', 'temperatura'],
            'infección': ['infección', 'infectado'],
        }
        
        for sintoma, palabras in sintomas_mapping.items():
            for palabra in palabras:
                if palabra in texto_lower:
                    params['sintomas'].append(sintoma)
                    break
        
        # Detectar condiciones
        if 'embarazada' in texto_lower or 'gestación' in texto_lower:
            params['condicion'] = 'embarazada'
        elif 'cachorro' in texto_lower or 'joven' in texto_lower:
            params['condicion'] = 'cachorro'
        elif 'adulto' in texto_lower or 'mayor' in texto_lower:
            params['condicion'] = 'adulto'
        
        return params
    
    def obtener_categoria_medicamento(self, principios: List[str]) -> str:
        """Deduce la categoría del medicamento"""
        
        for principio in principios:
            for principio_mapped, categoria in self.categorias.items():
                if principio_mapped.lower() in principio.lower() or \
                   principio.lower() in principio_mapped.lower():
                    return categoria
        
        return 'Otro'
    
    def recomendar_top_10(self, enfermedad: str, especie: str, 
                         peso: float = None, raza: str = None) -> List[Dict]:
        """Recomienda TOP 10 medicamentos filtrados inteligentemente"""
        
        clave_enf = f"{enfermedad}_{especie}"
        
        if clave_enf not in self.enfermedades:
            return []
        
        datos_enfermedad = self.enfermedades[clave_enf]
        med_ids = datos_enfermedad.get('medicamentos_asociados', [])
        
        if not med_ids:
            return []
        
        # Calcular puntuación para cada medicamento
        medicamentos_puntuados = []
        
        for med_id in med_ids:
            med = self.medicamentos.get(med_id, {})
            
            puntuacion = 0
            
            # +100: Indicado para la enfermedad
            puntuacion += 100
            
            # +50: Es para la especie correcta
            if med.get('especie') == especie:
                puntuacion += 50
            
            # +30: Compatibilidad de peso
            if peso:
                categoria = self.obtener_categoria_medicamento(med.get('principios_activos', []))
                dosis_info = self.dosis.get(categoria, {})
                
                peso_min = dosis_info.get('ajustes_peso', {}).get('peso_minimo_kg', 0)
                peso_max = dosis_info.get('ajustes_peso', {}).get('peso_maximo_kg', 100)
                
                if peso_min <= peso <= peso_max:
                    puntuacion += 30
            
            # +20: Sin contraindicaciones de raza
            if raza and raza in self.razas:
                contraindicados = self.razas[raza].get('medicamentos_precaución', [])
                conflicto = False
                for principio in med.get('principios_activos', []):
                    if any(c.lower() in principio.lower() for c in contraindicados):
                        conflicto = True
                        break
                
                if not conflicto:
                    puntuacion += 20
            
            # BONUS: Si la raza es predispuesta a la enfermedad
            if raza and raza in self.razas:
                for pred in self.razas[raza].get('enfermedades_predisposicion', []):
                    if pred['enfermedad'].lower() in enfermedad.lower():
                        puntuacion += pred.get('factor', 1) * 15
            
            medicamentos_puntuados.append({
                'medicamento': med,
                'puntuacion': puntuacion,
                'med_id': med_id
            })
        
        # Ordenar por puntuación
        medicamentos_puntuados.sort(key=lambda x: x['puntuacion'], reverse=True)
        
        # Obtener TOP 10
        top_10 = medicamentos_puntuados[:10]
        
        # Enriquecer con información
        resultado = []
        for item in top_10:
            med = item['medicamento']
            categoria = self.obtener_categoria_medicamento(med.get('principios_activos', []))
            dosis_info = self.dosis.get(categoria, {})
            
            resultado.append({
                'nombre': med.get('nombre'),
                'numero_registro': med.get('numero_registro'),
                'principios_activos': med.get('principios_activos', []),
                'presentacion': med.get('presentacion'),
                'titular': med.get('titular'),
                'prescripcion': med.get('prescripcion'),
                'categoria': categoria,
                'dosis_info': dosis_info,
                'puntuacion': item['puntuacion'],
                'indicaciones': datos_enfermedad.get('indicaciones'),
                'contraindicaciones': datos_enfermedad.get('contraindicaciones'),
                'notas': datos_enfermedad.get('notas')
            })
        
        return resultado
    
    def procesar_consulta_chat(self, texto_consulta: str) -> Dict:
        """Procesa una consulta completa en lenguaje natural"""
        
        print(f"\n{'='*60}")
        print(f"🏥 PROCESANDO CONSULTA: {texto_consulta}")
        print(f"{'='*60}\n")
        
        # 1. Extraer parámetros
        parametros = self.extraer_parametros_texto(texto_consulta)
        print(f"✅ Parámetros extraídos:")
        print(f"   - Especie: {parametros['especie']}")
        print(f"   - Peso: {parametros['peso']} kg" if parametros['peso'] else "   - Peso: No detectado")
        print(f"   - Raza: {parametros['raza']}" if parametros['raza'] else "   - Raza: No detectada")
        print(f"   - Síntomas: {', '.join(parametros['sintomas'])}\n" if parametros['sintomas'] else "   - Síntomas: Ninguno\n")
        
        resultado = {
            'parametros': parametros,
            'medicamentos_recomendados': [],
        }
        
        # Mapeo síntoma → enfermedad
        enfermedades_sintomas = {
            'picazón': 'Dermatitis alérgica',
            'otitis': 'Otitis externa',
            'diarrea': 'Gastroenteritis',
            'dolor': 'Dolor/Inflamación articular',
            'vómito': 'Náuseas/Vómitos',
            'tos': 'Problemas respiratorios crónicos',
            'fiebre': 'Infección bacteriana sistémica',
            'infección': 'Infección urinaria',
            'dermatitis': 'Dermatitis alérgica',
        }
        
        # 2. Buscar medicamentos
        for sintoma in parametros['sintomas']:
            if sintoma in enfermedades_sintomas:
                enfermedad = enfermedades_sintomas[sintoma]
                
                medicamentos = self.recomendar_top_10(
                    enfermedad,
                    parametros['especie'],
                    parametros['peso'],
                    parametros['raza']
                )
                
                if medicamentos:
                    print(f"✅ Medicamentos para {enfermedad}: {len(medicamentos)} encontrados\n")
                    resultado['medicamentos_recomendados'].extend(medicamentos[:5])
        
        return resultado


if __name__ == "__main__":
    engine = SmartRecommendationEngine()
    
    # Test
    resultado = engine.procesar_consulta_chat("Pastor alemán de 30kg con dolor en las caderas")
    
    print(f"📋 RECOMENDACIONES:")
    if resultado['medicamentos_recomendados']:
        for i, med in enumerate(resultado['medicamentos_recomendados'][:5], 1):
            print(f"\n{i}. {med['nombre']}")
            print(f"   Puntuación: {med['puntuacion']}")