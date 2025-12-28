import json
import re
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path


# Importación robusta del loader
try:
    from processing.enfermedades_loader import EnfermedadesLoader
    ENFERMEDADES_DISPONIBLES = True
except ImportError:
    try:
        from enfermedades_loader import EnfermedadesLoader
        ENFERMEDADES_DISPONIBLES = True
    except ImportError:
        ENFERMEDADES_DISPONIBLES = False


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SmartRecommendationEngine:
    """Motor de recomendación inteligente v2.1"""
    
    def __init__(self, 
                 grafo_path: str = 'data/knowledge_graph/mapeo_enfermedades_medicamentos.json',
                 dosis_path: str = 'data/knowledge_graph/dosis_medicamentos.json',
                 razas_path: str = 'data/knowledge_graph/razas_predisposiciones.json',
                 categorias_path: str = 'data/knowledge_graph/categorias_medicamentos.json'):
        
        logger.info("🔄 Inicializando SmartRecommendationEngine v2.1...")
        
        # Cargar datos básicos
        self.medicamentos, self.enfermedades, self.relaciones = self._cargar_grafo(grafo_path)
        self.dosis = self._cargar_dosis(dosis_path)
        self.razas = self._cargar_razas(razas_path)
        self.categorias = self._cargar_categorias(categorias_path)
        
        # Inicializar Loader
        self.enfermedades_loader = None
        if ENFERMEDADES_DISPONIBLES:
            try:
                self.enfermedades_loader = EnfermedadesLoader()
                logger.info("✅ Cargador de enfermedades ACTIVADO")
            except Exception as e:
                logger.warning(f"⚠️ Fallo al iniciar loader: {e}")
            
    # ========== MÉTODOS DE CARGA ==========
    
    def _cargar_grafo(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get('medicamentos', {}), data.get('enfermedades', {}), data.get('relaciones', [])
        except Exception:
            return {}, {}, []


    def _cargar_dosis(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}


    def _cargar_razas(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}


    def _cargar_categorias(self, path: str):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f).get('categorias', {})
        except Exception:
            return {}


    # ========== EXTRACCIÓN MEJORADA ==========


    def extraer_parametros_texto(self, texto: str) -> Dict:
        """Extrae parámetros asegurando detección de síntomas clave"""
        params = {
            'raza': None, 'peso': None, 'edad': None, 
            'especie': 'Perro', 'sintomas': [], 'condicion': 'normal'
        }
        
        texto_lower = texto.lower()
        
        # 1. Especie
        if 'gato' in texto_lower or 'felino' in texto_lower:
            params['especie'] = 'Gato'
        
        # 2. Peso (kg)
        match_peso = re.search(r'(\d+(?:\.?\d+)?)\s*(?:kg|kilogramos?)', texto_lower)
        if match_peso:
            params['peso'] = float(match_peso.group(1))


        # 3. Raza
        for raza in self.razas.keys():
            if raza.lower() in texto_lower:
                params['raza'] = raza
                break
        
        # 4. Síntomas (Detección Forzada de Palabras Clave)
        # 🔥 AÑADIDO: artrosis, artritis, rigidez
        palabras_clave_sintomas = [
            'dolor', 'inflamación', 'cojera', 'vómito', 'diarrea', 
            'picazón', 'rasca', 'alopecia', 'otitis', 'oído', 
            'parásitos', 'pulgas', 'garrapatas', 'gusanos',
            'infección', 'herida', 'tos', 'estornudos', 'displasia',
            'artrosis', 'artritis', 'rigidez'  # 👈 NUEVO
        ]
        
        for palabra in palabras_clave_sintomas:
            if palabra in texto_lower:
                if palabra not in params['sintomas']:
                    params['sintomas'].append(palabra)


        # Si tenemos el loader, usamos su lista también
        if self.enfermedades_loader:
            for sintoma_db in self.enfermedades_loader.listar_sintomas():
                if sintoma_db.lower() in texto_lower and sintoma_db.lower() not in params['sintomas']:
                    params['sintomas'].append(sintoma_db)
        
        logger.info(f"✅ Parámetros: Especie={params['especie']}, Síntomas={params['sintomas']}")
        return params


    # ========== LÓGICA DE DOSIS INTELIGENTE ==========


    def _calcular_dosis_texto(self, med_data: dict, peso: float) -> str:
        """Intenta calcular dosis cruzando datos o adivinando por nombre"""
        
        # 🔥 VALIDACIÓN DE PESO (para que no falle si no hay peso)
        if peso is None or peso <= 0:
            return "💊 Medicamento recomendado. Dosis: Consultar prospecto/veterinario."
        
        nombre_med = med_data.get('nombre', '').upper()
        principios = [p.upper() for p in med_data.get('principios_activos', [])]
        
        clave_dosis = None
        
        # 1. Intento Directo (Si el JSON ya tiene la clave)
        if 'clave_dosis' in med_data:
            clave_dosis = med_data['clave_dosis']
            
        # 2. Intento de Adivinanza (Heurística)
        if not clave_dosis:
            if "MELOXICAM" in nombre_med or "MELOXICAM" in principios:
                clave_dosis = "ANTIINFLAMATORIO_MELOXICAM"
            elif "AMOXICILINA" in nombre_med or "AMOXICILINA" in principios:
                clave_dosis = "ANTIBIOTICO_AMOXICILINA"
            elif "ROBENACOXIB" in nombre_med or "ONSIOOR" in nombre_med:
                clave_dosis = "ANTIINFLAMATORIO_ROBENACOXIB"
            elif "APOQUEL" in nombre_med or "OCLACITINIB" in principios:
                clave_dosis = "DERMATOLOGICO_APOQUEL"
            elif "CARPROFENO" in nombre_med or "CARPROFENO" in principios:
                clave_dosis = "ANTIINFLAMATORIO_CARPROFENO"
            elif "PARASIT" in nombre_med or "SIMPARICA" in nombre_med or "BRAVECTO" in nombre_med:
                return "Dosis: Consultar tabla de peso del envase (Antiparasitario)"


        # 3. Cálculo
        if clave_dosis and clave_dosis in self.dosis:
            info = self.dosis[clave_dosis]
            if 'dosis_mg_kg' in info:
                dosis_total = info['dosis_mg_kg'] * peso
                return f"⚖️ Dosis Calc: {dosis_total:.2f} mg ({info['dosis_mg_kg']} mg/kg) - {info.get('frecuencia','')} via {info.get('via','')}"
        
        return "Dosis: Consultar prospecto/veterinario (Sin datos automáticos)."


    # ========== PROCESAMIENTO ==========


    def procesar_consulta_chat(self, texto_consulta: str) -> Dict:
        logger.info(f"\n🏥 PROCESANDO: {texto_consulta}")
        
        parametros = self.extraer_parametros_texto(texto_consulta)
        
        resultado = {
            'parametros': parametros,
            'medicamentos_recomendados': [],
            'enfermedades_detectadas': [],
            'estado': 'exitoso'
        }
        
        if self.enfermedades_loader and parametros['sintomas']:
            # Usar el loader con traducción clínica
            enfermedades = self.enfermedades_loader.obtener_enfermedades_por_sintomas(
                parametros['sintomas'],
                parametros['especie']
            )
            
            for enfermedad in enfermedades:
                resultado['enfermedades_detectadas'].append({
                    'nombre': enfermedad['nombre'],
                    'confianza': enfermedad.get('confianza', 0)
                })
                
                # Obtener medicamentos y enriquecerlos
                med_ids = enfermedad.get('medicamentos_asociados', [])
                for med_id in med_ids[:5]:
                    if med_id in self.medicamentos:
                        med = self.medicamentos[med_id]
                        
                        # 🔥 FILTRO DE ESPECIE (para que gatos no reciban medicamentos de perros)
                        especie_med = med.get('especie', '').upper()
                        especie_paciente = parametros['especie'].upper()
                        
                        # Saltar si no es compatible
                        if especie_paciente not in especie_med and 'AMBOS' not in especie_med:
                            logger.warning(f"⚠️ Medicamento {med.get('nombre')} NO es para {especie_paciente}")
                            continue
                        
                        resultado['medicamentos_recomendados'].append({
                            'id': med_id,
                            'nombre': med.get('nombre'),
                            'principios_activos': med.get('principios_activos', []),
                            'especie': med.get('especie'),
                            'prescripcion': med.get('prescripcion'),
                            'clave_dosis': med.get('clave_dosis') 
                        })


        if not resultado['medicamentos_recomendados']:
            logger.warning("⚠️ Sin medicamentos encontrados")
        else:
            logger.info(f"✅ {len(resultado['medicamentos_recomendados'])} medicamentos encontrados")
            
        return resultado


    # ========== VALIDACIÓN DE MEDICAMENTOS ==========


    def validar_medicamento_enfermedad(self, medicamento_id: str, sintomas: List[str]) -> Dict:
        """Calcula un score de confianza cruzando síntomas con medicamentos"""
        if medicamento_id not in self.medicamentos:
            return {'valido': False, 'score': 0, 'confianza': 'Baja'}
        
        med = self.medicamentos[medicamento_id]
        principios = [p.lower() for p in med.get('principios_activos', [])]
        
        # Buscar coincidencias entre síntomas y principios activos
        coincidencias = 0
        for sintoma in sintomas:
            sintoma_lower = sintoma.lower()
            
            # Mapeo directo (expandir según tu traductor_clinico)
            mapeo_validacion = {
                'otitis': ['enrofloxacino', 'marbofloxacino', 'gentamicina', 'polimixina'],
                'dolor': ['meloxicam', 'tramadol', 'carprofeno', 'firocoxib'],
                'inflamación': ['prednisolona', 'dexametasona', 'ketoprofeno'],
                'parásitos': ['ivermectina', 'fipronilo', 'afoxolaner', 'fluralaner'],
                'pulgas': ['fipronilo', 'imidacloprid', 'selamectina'],
                'garrapatas': ['fipronilo', 'fluralaner', 'afoxolaner'],
                'diarrea': ['metronidazol', 'caolín', 'pectina'],
                'vómito': ['maropitant', 'metoclopramida'],
                'picazón': ['oclacitinib', 'ciclosporina', 'prednisolona'],
                'infección': ['amoxicilina', 'cefalexina', 'doxiciclina', 'enrofloxacino'],
                'artrosis': ['meloxicam', 'carprofeno', 'firocoxib', 'robenacoxib'],
                'artritis': ['meloxicam', 'carprofeno', 'tramadol'],
                'rigidez': ['meloxicam', 'carprofeno']
            }
            
            if sintoma_lower in mapeo_validacion:
                for principio_esperado in mapeo_validacion[sintoma_lower]:
                    if any(principio_esperado in p for p in principios):
                        coincidencias += 1
                        break
        
        score = min(coincidencias / len(sintomas), 1.0) if sintomas else 0
        
        return {
            'valido': score > 0.3,
            'score': score,
            'confianza': 'Alta' if score > 0.7 else 'Media' if score > 0.4 else 'Baja'
        }
