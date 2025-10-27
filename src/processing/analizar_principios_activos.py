import pandas as pd
import json
from collections import Counter

def analizar_principios_activos():
    """Analiza qué principios activos tienes disponibles en Cimavet"""
    
    print("\n" + "="*80)
    print("📊 ANÁLISIS DE PRINCIPIOS ACTIVOS DISPONIBLES EN CIMAVET")
    print("="*80 + "\n")
    
    # Carga datos
    df = pd.read_csv('data/processed/cimavet_completo.csv')
    
    # Extrae todos los principios activos
    todos_principios = []
    
    for idx, row in df.iterrows():
        principios_str = str(row['principios_activos'])
        if principios_str != 'nan':
            # Separa por comas
            principios = [p.strip() for p in principios_str.split(',')]
            todos_principios.extend(principios)
    
    # Cuenta frecuencia
    contador = Counter(todos_principios)
    
    # Ordena por frecuencia
    principios_ordenados = sorted(contador.items(), key=lambda x: x[1], reverse=True)
    
    print(f"📈 TOTAL DE PRINCIPIOS ACTIVOS ÚNICOS: {len(contador)}\n")
    
    print("🔝 TOP 50 PRINCIPIOS ACTIVOS MÁS COMUNES:")
    print("-" * 80)
    
    for i, (principio, cantidad) in enumerate(principios_ordenados[:50], 1):
        barra = "█" * int(cantidad / 10)
        print(f"{i:2d}. {principio:<50} {cantidad:3d} {barra}")
    
    print("\n" + "-" * 80)
    print(f"... y {len(principios_ordenados) - 50} más\n")
    
    # Análisis por especie
    print("\n" + "="*80)
    print("🐾 PRINCIPIOS ACTIVOS POR ESPECIE")
    print("="*80 + "\n")
    
    for especie in ['Perro', 'Gato']:
        df_especie = df[df['especie'] == especie]
        
        principios_especie = []
        for idx, row in df_especie.iterrows():
            principios_str = str(row['principios_activos'])
            if principios_str != 'nan':
                principios = [p.strip() for p in principios_str.split(',')]
                principios_especie.extend(principios)
        
        contador_especie = Counter(principios_especie)
        
        print(f"\n{especie.upper()} - Total de principios únicos: {len(contador_especie)}")
        print("-" * 80)
        
        for i, (principio, cantidad) in enumerate(sorted(contador_especie.items(), 
                                                         key=lambda x: x[1], 
                                                         reverse=True)[:20], 1):
            print(f"  {i:2d}. {principio:<55} ({cantidad}x)")
    
    # Crea archivo JSON para referencia
    output_dict = {
        'total_principios_unicos': len(contador),
        'principios_activos_frecuencia': dict(principios_ordenados),
        'principios_por_especie': {
            'Perro': dict(Counter(
                [p.strip() for idx, row in df[df['especie']=='Perro'].iterrows()
                 for p in str(row['principios_activos']).split(',') 
                 if str(row['principios_activos']) != 'nan']
            ).most_common(50)),
            'Gato': dict(Counter(
                [p.strip() for idx, row in df[df['especie']=='Gato'].iterrows()
                 for p in str(row['principios_activos']).split(',') 
                 if str(row['principios_activos']) != 'nan']
            ).most_common(50))
        }
    }
    
    with open('data/processed/principios_activos_analisis.json', 'w', encoding='utf-8') as f:
        json.dump(output_dict, f, ensure_ascii=False, indent=2)
    
    # Crea CSV para facilitar el mapeo
    lista_principios = pd.DataFrame([
        {'principio_activo': p, 'frecuencia': c}
        for p, c in principios_ordenados
    ])
    
    lista_principios.to_csv(
        'data/processed/principios_activos_lista.csv',
        index=False,
        encoding='utf-8'
    )
    
    print("\n" + "="*80)
    print("✅ ANÁLISIS COMPLETADO")
    print("="*80)
    print("📁 Archivos generados:")
    print("  - data/processed/principios_activos_analisis.json")
    print("  - data/processed/principios_activos_lista.csv")
    print("="*80 + "\n")

if __name__ == "__main__":
    analizar_principios_activos()