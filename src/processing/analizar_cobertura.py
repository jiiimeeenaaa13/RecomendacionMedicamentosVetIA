import json
import pandas as pd
from collections import Counter

def analizar_cobertura():
    """
    Analiza qué medicamentos NO están mapeados y qué principios activos representan
    """
    
    print("\n" + "="*80)
    print("🔍 ANÁLISIS DE COBERTURA - MEDICAMENTOS SIN MAPEO")
    print("="*80 + "\n")
    
    # Carga grafo
    with open('data/knowledge_graph/mapeo_enfermedades_medicamentos.json', 'r', encoding='utf-8') as f:
        grafo = json.load(f)
    
    # Carga medicamentos
    medicamentos_df = pd.read_csv('data/processed/cimavet_completo.csv')
    
    # Identifica medicamentos mapeados
    meds_mapeados = set()
    for rel in grafo['relaciones']:
        meds_mapeados.add(rel['hacia_medicamento'])
    
    # Identifica medicamentos SIN mapeo
    meds_sin_mapeo = set()
    for med_id in grafo['medicamentos'].keys():
        if med_id not in meds_mapeados:
            meds_sin_mapeo.add(med_id)
    
    print(f"📊 ESTADÍSTICAS GENERALES:")
    print(f"  - Medicamentos totales: {len(grafo['medicamentos'])}")
    print(f"  - Medicamentos mapeados: {len(meds_mapeados)}")
    print(f"  - Medicamentos SIN mapeo: {len(meds_sin_mapeo)}")
    print(f"  - Cobertura: {(len(meds_mapeados)/len(grafo['medicamentos'])*100):.1f}%\n")
    
    # Análisis por especie
    print("🐾 POR ESPECIE:")
    for especie in ['Perro', 'Gato']:
        meds_especie = {mid: m for mid, m in grafo['medicamentos'].items() 
                       if m['especie'] == especie}
        meds_sin_especie = {mid for mid in meds_sin_mapeo 
                           if mid in meds_especie}
        
        if meds_especie:
            cobertura = ((len(meds_especie) - len(meds_sin_especie)) / len(meds_especie) * 100)
            print(f"\n  {especie}S:")
            print(f"    - Total: {len(meds_especie)}")
            print(f"    - Sin mapeo: {len(meds_sin_especie)}")
            print(f"    - Cobertura: {cobertura:.1f}%")
    
    # Extrae principios activos de medicamentos SIN mapeo
    print("\n" + "="*80)
    print("💊 PRINCIPIOS ACTIVOS EN MEDICAMENTOS SIN MAPEO")
    print("="*80 + "\n")
    
    principios_sin_mapeo = []
    meds_sin_mapeo_lista = []
    
    for med_id in sorted(meds_sin_mapeo):
        med = grafo['medicamentos'][med_id]
        for principio in med['principios_activos']:
            principios_sin_mapeo.append(principio.strip())
        meds_sin_mapeo_lista.append({
            'id': med_id,
            'nombre': med['nombre'],
            'principios': med['principios_activos'],
            'especie': med['especie']
        })
    
    # Cuenta principios
    contador_principios = Counter(principios_sin_mapeo)
    
    print(f"🔝 TOP 30 PRINCIPIOS ACTIVOS SIN MAPEO:\n")
    
    for i, (principio, cantidad) in enumerate(contador_principios.most_common(30), 1):
        barra = "█" * min(cantidad, 20)
        print(f"{i:2d}. {principio:<50} {cantidad:3d}x {barra}")
    
    # Analiza categorías de enfermedades potenciales
    print("\n" + "="*80)
    print("💡 ENFERMEDADES POTENCIALES QUE PODRÍAS AÑADIR")
    print("="*80 + "\n")
    
    # Mapeo de principios activos a potenciales enfermedades
    mapeo_sugerencias = {
        'VACUNA': 'Inmunización/Vacunación',
        'VIRUS': 'Inmunización/Vacunación',
        'ADENOVIRUS': 'Inmunización/Vacunación',
        'PARVOVIRUS': 'Inmunización/Vacunación',
        'MOQUILLO': 'Inmunización/Vacunación',
        'LEPTOSPIRA': 'Inmunización/Vacunación',
        'INACTIVADA': 'Inmunización/Vacunación',
        'VIVO ATENUADO': 'Inmunización/Vacunación',
        'INSULINA': 'Diabetes mellitus',
        'CORTICOSTEROIDE': 'Inflamación sistémica',
        'DEXAMETASONA': 'Inflamación sistémica',
        'PREDNISOLONA': 'Inflamación sistémica',
        'TIAMAZOL': 'Hipertiroidismo',
        'LEVOTIROXINA': 'Hipotiroidismo',
        'DIGOXINA': 'Arritmias cardíacas',
        'PIMOBENDAN': 'Insuficiencia cardíaca',
        'SILDENAFILO': 'Hipertensión pulmonar',
        'OMEPRAZOL': 'Úlcera gástrica',
        'FAMOTIDINA': 'Úlcera gástrica',
        'SUCRALFATO': 'Úlcera gástrica',
        'SULFASALAZINA': 'IBD/Colitis',
        'AZATIOPRINA': 'Enfermedad inmunomediada',
        'CICLOSPORINA': 'Enfermedad inmunomediada',
        'ANTIHISTAMÍNICO': 'Alergia sistémica',
        'CETIRIZINA': 'Alergia sistémica',
        'LORATADINA': 'Alergia sistémica',
        'DIFENHIDRAMINA': 'Alergia sistémica',
        'DESLORATADINA': 'Alergia sistémica',
        'ANTIBIÓTICO': 'Infección bacteriana',
        'ANTIFÚNGICO': 'Infección fúngica',
        'ESPIRONOLACTONA': 'Insuficiencia cardíaca',
        'FUROSEMIDA': 'Edema/Insuficiencia cardíaca',
        'TORASEMIDA': 'Edema/Insuficiencia cardíaca',
        'AMLODIPINO': 'Hipertensión',
        'DILTIAZEM': 'Arritmias cardíacas',
        'ATENOLOL': 'Arritmias cardíacas',
        'PROPRANOLOL': 'Arritmias cardíacas',
        'DOXORRUBICINA': 'Neoplasia/Cáncer',
        'QUIMIOTERAPIA': 'Neoplasia/Cáncer',
        'MEGESTROL': 'Neoplasia/Cáncer',
        'TOPIRAMATO': 'Convulsiones refractarias',
        'BROMURO POTASIO': 'Convulsiones',
        'LEVETIRACETAM': 'Convulsiones',
        'ZONISAMIDA': 'Convulsiones',
        'KETAMINA': 'Sedación/Anestesia',
        'PROPOFOL': 'Sedación/Anestesia',
        'TILETAMINA': 'Sedación/Anestesia',
        'ALFAXALONA': 'Sedación/Anestesia',
        'AINE': 'Dolor/Inflamación',
        'GLUCOSAMINA': 'Osteoartritis',
        'CONDROITINA': 'Osteoartritis',
        'MSM': 'Osteoartritis',
        'COMPLEJO B': 'Deficiencia vitamínica',
        'VITAMINA E': 'Deficiencia vitamínica',
        'VITAMINA D': 'Deficiencia vitamínica',
        'CALCIO': 'Deficiencia mineral',
        'FÓSFORO': 'Deficiencia mineral',
        'POTASIO': 'Deficiencia mineral',
        'HIERRO': 'Anemia',
        'ÁCIDO FÓLICO': 'Anemia',
        'CIANOCOBALAMINA': 'Anemia/Deficiencia B12',
        'PROBIÓTICO': 'Disbiosis intestinal',
        'PREBIÓT': 'Salud intestinal',
        'ACEITE PESCADO': 'Inflamación sistémica',
        'OMEGA-3': 'Inflamación sistémica',
    }
    
    sugerencias = {}
    
    for principio, cantidad in contador_principios.most_common(50):
        enfermedad = None
        for clave, enf in mapeo_sugerencias.items():
            if clave.upper() in principio.upper():
                enfermedad = enf
                break
        
        if enfermedad:
            if enfermedad not in sugerencias:
                sugerencias[enfermedad] = 0
            sugerencias[enfermedad] += cantidad
    
    print("Sugerencias de nuevas enfermedades por cobertura de medicamentos:\n")
    for enf, cantidad in sorted(sugerencias.items(), key=lambda x: x[1], reverse=True):
        if cantidad > 5:  # Solo muestra con cobertura significativa
            print(f"  💊 {enf:<40} → {cantidad:3d} medicamentos")
    
    # Medicamentos sin clasificar
    print("\n" + "="*80)
    print(f"📋 MEDICAMENTOS SIN MAPEO (total: {len(meds_sin_mapeo)})")
    print("="*80 + "\n")
    
    print("PERROS - Sin mapeo:")
    for med in sorted(meds_sin_mapeo_lista, key=lambda x: x['especie']):
        if med['especie'] == 'Perro':
            print(f"  - {med['nombre'][:60]}")
            print(f"    Principios: {', '.join(med['principios'][:2])}")
    
    print("\nGATOS - Sin mapeo:")
    for med in sorted(meds_sin_mapeo_lista, key=lambda x: x['especie']):
        if med['especie'] == 'Gato':
            print(f"  - {med['nombre'][:60]}")
            print(f"    Principios: {', '.join(med['principios'][:2])}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    analizar_cobertura()