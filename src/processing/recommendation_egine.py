import json
from typing import List, Dict, Tuple

class MedicineRecommendationEngine:
    """
    Motor de recomendación que usa el grafo de conocimiento
    """
    
    def __init__(self, grafo_json_path: str):
        """
        Inicializa el motor cargando el grafo
        
        Args:
            grafo_json_path: ruta al JSON del mapeo
        """
        print("🔄 Cargando grafo de conocimiento...")
        
        with open(grafo_json_path, 'r', encoding='utf-8') as f:
            self.grafo = json.load(f)
        
        self.medicamentos = self.grafo['medicamentos']
        self.enfermedades = self.grafo['enfermedades']
        self.relaciones = self.grafo['relaciones']
        
        print(f"✅ Grafo cargado:")
        print(f"   - {len(self.medicamentos)} medicamentos")
        print(f"   - {len(self.enfermedades)} enfermedades")
        print(f"   - {len(self.relaciones)} relaciones\n")
    
    def recomendar(self, enfermedad: str, especie: str) -> Tuple[bool, List[Dict]]:
        """
        Recomienda medicamentos para una enfermedad en una especie
        
        Args:
            enfermedad: nombre de la enfermedad (ej: "Otitis externa")
            especie: "Perro" o "Gato"
        
        Returns:
            (encontrado: bool, medicamentos: List[Dict])
        """
        clave_enf = f"{enfermedad}_{especie}"
        
        if clave_enf not in self.enfermedades:
            return False, []
        
        datos_enfermedad = self.enfermedades[clave_enf]
        med_ids = datos_enfermedad['medicamentos_asociados']
        
        if not med_ids:
            return False, []
        
        # Obtiene datos completos de los medicamentos
        medicamentos_recomendados = []
        
        for med_id in med_ids:
            med = self.medicamentos[med_id]
            
            # Busca la relación para obtener principios coincidentes
            principios_coincidentes = []
            for rel in self.relaciones:
                if rel['hacia_medicamento'] == med_id and rel['desde_enfermedad'] == clave_enf:
                    principios_coincidentes = rel['principios_coincidentes']
                    break
            
            medicamentos_recomendados.append({
                'nombre': med['nombre'],
                'numero_registro': med['numero_registro'],
                'principios_activos': med['principios_activos'],
                'principios_coincidentes': principios_coincidentes,
                'presentacion': med['presentacion'],
                'titular': med['titular'],
                'prescripcion': med['prescripcion'],
                'estado': med['estado'],
                'fecha_comercializado': med['fecha_comercializado'],
                'especie': med['especie'],
                'indicaciones': datos_enfermedad['indicaciones'],
                'contraindicaciones': datos_enfermedad['contraindicaciones'],
                'notas': datos_enfermedad['notas'],
                'categoria': datos_enfermedad['categoria']
            })
        
        return True, medicamentos_recomendados
    
    def listar_enfermedades(self, especie: str = None) -> Dict[str, List[str]]:
        """
        Lista todas las enfermedades disponibles
        
        Args:
            especie: Si es None, devuelve todas. Si es "Perro" o "Gato", solo esas.
        
        Returns:
            Dict con enfermedades agrupadas por especie
        """
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
            resultado[esp] = sorted(resultado[esp])
        
        return resultado
    
    def buscar_medicamento(self, nombre: str) -> List[Dict]:
        """
        Busca un medicamento por nombre
        
        Args:
            nombre: nombre o parte del nombre del medicamento
        
        Returns:
            Lista de medicamentos que coinciden
        """
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
    
    def obtener_enfermedades_para_medicamento(self, med_id: str) -> List[Dict]:
        """
        Obtiene todas las enfermedades que trata un medicamento
        
        Args:
            med_id: ID del medicamento (ej: "med_0")
        
        Returns:
            Lista de enfermedades que trata
        """
        enfermedades_tratadas = []
        
        for rel in self.relaciones:
            if rel['hacia_medicamento'] == med_id:
                enfermedades_tratadas.append({
                    'enfermedad': rel['nombre_enfermedad'],
                    'especie': rel['especie'],
                    'principios_coincidentes': rel['principios_coincidentes']
                })
        
        return enfermedades_tratadas
    
    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene estadísticas del grafo
        """
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

if __name__ == "__main__":
    # TEST DEL MOTOR
    print("\n" + "="*80)
    print("🧪 TEST DEL MOTOR DE RECOMENDACIÓN")
    print("="*80 + "\n")
    
    engine = MedicineRecommendationEngine(
        'data/knowledge_graph/mapeo_enfermedades_medicamentos.json'
    )
    
    # Test 1: Estadísticas
    print("📊 ESTADÍSTICAS DEL SISTEMA:")
    stats = engine.obtener_estadisticas()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test 2: Listar enfermedades para Perros
    print("\n" + "="*80)
    print("📋 ENFERMEDADES DISPONIBLES PARA PERROS:")
    print("="*80)
    enfs_perro = engine.listar_enfermedades('Perro')
    for enf in enfs_perro.get('Perro', []):
        print(f"  - {enf}")
    
    # Test 3: Recomendación para Otitis
    print("\n" + "="*80)
    print("💊 TEST: RECOMENDACIÓN PARA OTITIS EXTERNA EN PERRO")
    print("="*80 + "\n")
    
    encontrado, medicamentos = engine.recomendar('Otitis externa', 'Perro')
    
    if encontrado:
        print(f"✅ Se encontraron {len(medicamentos)} medicamentos recomendados\n")
        
        for i, med in enumerate(medicamentos[:5], 1):  # Muestra primeros 5
            print(f"{i}. {med['nombre']}")
            print(f"   Nº Registro: {med['numero_registro']}")
            print(f"   Principios activos: {', '.join(med['principios_activos'][:3])}")
            print(f"   Prescripción: {med['prescripcion']}")
            print(f"   Indicaciones: {med['indicaciones'][:60]}...")
            print(f"   ⚠️  Contraindicaciones: {med['contraindicaciones'][:60]}...")
            print()
        
        if len(medicamentos) > 5:
            print(f"... y {len(medicamentos) - 5} más\n")
    else:
        print("❌ No se encontraron recomendaciones")
    
    # Test 4: Búsqueda de medicamento
    print("="*80)
    print("🔍 TEST: BÚSQUEDA DE MEDICAMENTO 'FRONTLINE'")
    print("="*80 + "\n")
    
    resultados = engine.buscar_medicamento('FRONTLINE')
    if resultados:
        print(f"✅ Se encontraron {len(resultados)} resultados:\n")
        for med in resultados:
            print(f"  - {med['nombre']} ({med['especie']})")
            print(f"    Principios: {', '.join(med['principios_activos'])}")
    else:
        print("❌ No se encontraron resultados")
    
    # Test 5: Recomendación para Pulgas en Gato
    print("\n" + "="*80)
    print("💊 TEST: RECOMENDACIÓN PARA PULGAS EN GATO")
    print("="*80 + "\n")
    
    encontrado, medicamentos = engine.recomendar('Pulgas', 'Gato')
    
    if encontrado:
        print(f"✅ Se encontraron {len(medicamentos)} medicamentos\n")
        for i, med in enumerate(medicamentos[:3], 1):
            print(f"{i}. {med['nombre']}")
            print(f"   Principios: {', '.join(med['principios_activos'])}\n")
    
    print("="*80)
    print("✅ TESTS COMPLETADOS")
    print("="*80 + "\n")