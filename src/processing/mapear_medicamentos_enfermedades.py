import pandas as pd
import json
from typing import Dict, List
import os

def mapear_medicamentos_a_enfermedades():
    """
    Cruza medicamentos Cimavet con enfermedades creando un grafo de conocimiento
    """
    
    print("\n" + "="*80)
    print("🔗 MAPEANDO MEDICAMENTOS → ENFERMEDADES")
    print("="*80 + "\n")
    
    # Carga datos
    medicamentos_df = pd.read_csv('data/processed/cimavet_completo.csv')
    enfermedades_df = pd.read_csv('data/raw/enfermedades_medicamentos_cimavet.csv')
    
    print(f"📦 Medicamentos cargados: {len(medicamentos_df)}")
    print(f"📋 Enfermedades cargadas: {len(enfermedades_df)}\n")
    
    # Verifica columnas disponibles
    print(f"Columnas en enfermedades CSV: {list(enfermedades_df.columns)}\n")
    
    # Estructura del grafo de conocimiento
    grafo = {
        'metadata': {
            'total_medicamentos': 0,
            'total_enfermedades': 0,
            'total_correlaciones': 0
        },
        'medicamentos': {},      # id → datos completos del medicamento
        'enfermedades': {},      # enfermedad_especie → datos de la enfermedad
        'relaciones': []         # Array de relaciones (edges)
    }
    
    # 1. CONSTRUIR NODOS DE MEDICAMENTOS
    print("📝 Paso 1: Indexando medicamentos...")
    
    for idx, row in medicamentos_df.iterrows():
        med_id = f"med_{idx}"
        
        # Limpia principios activos
        principios = [p.strip() for p in str(row['principios_activos']).split(',')]
        
        grafo['medicamentos'][med_id] = {
            'id': med_id,
            'nombre': row['medicamento'],
            'numero_registro': row['numero_registro'],
            'principios_activos': principios,
            'especie': row['especie'],
            'presentacion': row.get('fecha', 'N/A'),
            'titular': row.get('titular_autorizacion', 'N/A'),
            'prescripcion': row.get('prescripcion', 'N/A'),
            'estado': row.get('estado', 'N/A'),
            'fecha_comercializado': row.get('comercializado', 'N/A')
        }
    
    grafo['metadata']['total_medicamentos'] = len(grafo['medicamentos'])
    print(f"   ✅ {len(grafo['medicamentos'])} medicamentos indexados\n")
    
    # 2. CONSTRUIR NODOS DE ENFERMEDADES
    print("📝 Paso 2: Indexando enfermedades...")
    
    # Identifica el nombre correcto de la columna de principios activos
    col_principios = None
    for col in enfermedades_df.columns:
        if 'principios' in col.lower():
            col_principios = col
            break
    
    if col_principios is None:
        print("❌ ERROR: No se encontró columna de principios activos en enfermedades CSV")
        print(f"Columnas disponibles: {list(enfermedades_df.columns)}")
        return None
    
    print(f"   Usando columna: '{col_principios}'\n")
    
    for idx, row in enfermedades_df.iterrows():
        clave_enf = f"{row['enfermedad']}_{row['especie']}"
        
        # Parsea los principios activos recomendados
        principios_rec = [p.strip() for p in str(row[col_principios]).split(';')]
        
        grafo['enfermedades'][clave_enf] = {
            'id': clave_enf,
            'nombre': row['enfermedad'],
            'categoria': row.get('categoria', row.get('categoria_diagnostica', 'N/A')),
            'especie': row['especie'],
            'indicaciones': row.get('indicaciones', ''),
            'contraindicaciones': row.get('contraindicaciones', ''),
            'notas': row.get('notas', ''),
            'principios_recomendados': principios_rec,
            'medicamentos_asociados': []  # Se llenará en paso 3
        }
    
    grafo['metadata']['total_enfermedades'] = len(grafo['enfermedades'])
    print(f"   ✅ {len(grafo['enfermedades'])} enfermedades indexadas\n")
    
    # 3. CREAR RELACIONES (EDGES)
    print("📝 Paso 3: Creando correlaciones enfermedad-medicamento...\n")
    
    contador_relaciones = 0
    detalles_por_enfermedad = {}
    
    for clave_enf, datos_enf in grafo['enfermedades'].items():
        principios_recomendados = datos_enf['principios_recomendados']
        medicamentos_encontrados = []
        
        # Busca medicamentos que contengan estos principios activos
        for med_id, datos_med in grafo['medicamentos'].items():
            # Solo considera medicamentos de la misma especie
            if datos_med['especie'] != datos_enf['especie']:
                continue
            
            # Verifica si algún principio activo del medicamento coincide
            coincidencia = False
            principios_coincidentes = []
            
            for principio_recomendado in principios_recomendados:
                principio_rec_limpio = principio_recomendado.strip().lower()
                
                for principio_med in datos_med['principios_activos']:
                    principio_med_limpio = principio_med.strip().lower()
                    
                    # Coincidencia exacta o parcial (para variaciones)
                    if (principio_rec_limpio in principio_med_limpio or 
                        principio_med_limpio in principio_rec_limpio):
                        coincidencia = True
                        principios_coincidentes.append(principio_med)
                        break
            
            # Si hay coincidencia, crea relación
            if coincidencia:
                medicamentos_encontrados.append(med_id)
                
                relacion = {
                    'desde_enfermedad': clave_enf,
                    'hacia_medicamento': med_id,
                    'tipo': 'TRATA',
                    'nombre_enfermedad': datos_enf['nombre'],
                    'nombre_medicamento': datos_med['nombre'],
                    'especie': datos_enf['especie'],
                    'principios_coincidentes': principios_coincidentes,
                    'indicaciones': datos_enf['indicaciones'],
                    'contraindicaciones': datos_enf['contraindicaciones'],
                    'notas': datos_enf['notas']
                }
                
                grafo['relaciones'].append(relacion)
                contador_relaciones += 1
        
        # Actualiza enfermedades con medicamentos encontrados
        grafo['enfermedades'][clave_enf]['medicamentos_asociados'] = medicamentos_encontrados
        
        detalles_por_enfermedad[clave_enf] = {
            'medicamentos': len(medicamentos_encontrados),
            'medicamentos_ids': medicamentos_encontrados
        }
    
    grafo['metadata']['total_correlaciones'] = contador_relaciones
    
    print(f"   ✅ {contador_relaciones} correlaciones creadas\n")
    
    # 4. GUARDAR GRAFO
    print("📝 Paso 4: Guardando grafo de conocimiento...")
    
    os.makedirs('data/knowledge_graph', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    
    # Guarda JSON principal en knowledge_graph
    with open('data/knowledge_graph/mapeo_enfermedades_medicamentos.json', 'w', encoding='utf-8') as f:
        json.dump(grafo, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ Guardado: data/knowledge_graph/mapeo_enfermedades_medicamentos.json")
    
    # También guarda versión procesada del CSV de enfermedades
    enfermedades_procesado = enfermedades_df.copy()
    enfermedades_procesado['medicamentos_asociados'] = enfermedades_procesado.apply(
        lambda row: len([m for k, m in detalles_por_enfermedad.items() 
                        if k == f"{row['enfermedad']}_{row['especie']}"]), 
        axis=1
    )
    enfermedades_procesado.to_csv('data/processed/enfermedades_medicamentos_procesado.csv', 
                                   index=False, encoding='utf-8')
    print(f"   ✅ Guardado: data/processed/enfermedades_medicamentos_procesado.csv\n")
    
    # 5. REPORTE DETALLADO
    print("="*80)
    print("📊 REPORTE DETALLADO DEL MAPEO")
    print("="*80 + "\n")
    
    print("✅ ENFERMEDADES MAPEADAS POR ESPECIE Y CATEGORÍA:\n")
    
    for especie in ['Perro', 'Gato', 'Perra']:
        enfs_especie = {k: v for k, v in detalles_por_enfermedad.items() if k.endswith(f"_{especie}")}
        
        if enfs_especie:
            print(f"\n{especie.upper()}S - {len(enfs_especie)} patologías:")
            print("-" * 80)
            
            for clave_enf in sorted(enfs_especie.keys()):
                nombre_enf = clave_enf.replace(f"_{especie}", "")
                num_meds = detalles_por_enfermedad[clave_enf]['medicamentos']
                categoria = grafo['enfermedades'][clave_enf]['categoria']
                
                barra = "█" * min(num_meds, 20) if num_meds > 0 else "❌"
                simbolo = "✅" if num_meds > 0 else "⚠️"
                
                print(f"  {simbolo} {nombre_enf:<40} ({categoria:<20}) → {num_meds:3d} medicamentos {barra}")
    
    # 6. ESTADÍSTICAS FINALES
    print("\n" + "="*80)
    print("📈 ESTADÍSTICAS FINALES")
    print("="*80 + "\n")
    
    print(f"Total de medicamentos: {grafo['metadata']['total_medicamentos']}")
    print(f"Total de enfermedades: {grafo['metadata']['total_enfermedades']}")
    print(f"Total de correlaciones: {grafo['metadata']['total_correlaciones']}")
    
    # Calcula promedio
    if grafo['metadata']['total_enfermedades'] > 0:
        promedio = grafo['metadata']['total_correlaciones'] / grafo['metadata']['total_enfermedades']
        print(f"Promedio de medicamentos por enfermedad: {promedio:.1f}\n")
    
    # Medicamentos sin usar
    meds_usados = set()
    for rel in grafo['relaciones']:
        meds_usados.add(rel['hacia_medicamento'])
    
    meds_no_usados = len(grafo['medicamentos']) - len(meds_usados)
    print(f"Medicamentos sin correlación en este mapeo: {meds_no_usados}")
    print(f"Cobertura: {(len(meds_usados)/len(grafo['medicamentos'])*100):.1f}%\n")
    
    # Enfermedades sin medicamentos
    enfs_sin_meds = sum(1 for enf in grafo['enfermedades'].values() if not enf['medicamentos_asociados'])
    print(f"Enfermedades sin medicamentos asociados: {enfs_sin_meds}")
    
    print("\n" + "="*80)
    print("✅ MAPEO COMPLETADO EXITOSAMENTE")
    print("="*80 + "\n")
    
    return grafo

if __name__ == "__main__":
    mapear_medicamentos_a_enfermedades()