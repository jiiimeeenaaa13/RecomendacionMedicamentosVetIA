import pandas as pd
import os
from pathlib import Path

def importar_excels_cimavet():
    """Importa los Excels de Cimavet saltando las primeras 7 filas (encabezados/metadatos)"""
    
    raw_dir = 'data/raw'
    processed_dir = 'data/processed'
    
    # Archivos reales en tu proyecto
    archivos = {
        'PERROS.xlsx': 'Perro',
        'GATOS.xlsx': 'Gato',
        'perras-cimavet-medicamentos.xlsx': 'Reproducción'
    }
    
    # Nombres correctos de columnas (basados en tu estructura real)
    nombres_columnas = [
        'numero_registro',
        'medicamento',
        'principios_activos',
        'titular_autorizacion',
        'prescripcion',
        'estado',
        'fecha',
        'comercializado'
    ]
    
    dataframes = []
    
    for archivo, especie in archivos.items():
        ruta = os.path.join(raw_dir, archivo)
        
        if os.path.exists(ruta):
            print(f"📖 Leyendo {archivo}...")
            
            try:
                # IMPORTANTE: Salta las primeras 7 filas (encabezados/metadatos)
                # La fila 8 (índice 7) contiene "NUMERO DE REGISTRO MEDICAMENTO..."
                # La fila 9 (índice 8) es donde empiezan los datos reales
                df = pd.read_excel(ruta, engine='openpyxl', header=None, skiprows=8)
                
                # Asigna nombres de columnas solo para las que usamos
                # (descarta la primera columna que está vacía)
                df = df.iloc[:, 1:9]  # Toma columnas 1-8 (ignorando la 0 que está vacía)
                df.columns = nombres_columnas
                
                # Elimina filas completamente vacías
                df = df.dropna(how='all')
                
                # Elimina filas donde el número de registro está vacío
                df = df[df['numero_registro'].notna()]
                df = df[df['numero_registro'].astype(str).str.strip() != '']
                
                # Limpia espacios en blanco en todas las columnas
                for col in df.select_dtypes(include=['object']).columns:
                    df[col] = df[col].astype(str).str.strip()
                
                # Elimina filas donde medicamento es "nan"
                df = df[df['medicamento'] != 'nan']
                
                # Añade columna de especie
                df['especie'] = especie
                
                dataframes.append(df)
                print(f"   ✅ {len(df)} medicamentos importados")
                if len(df) > 0:
                    print(f"      Ejemplo: {df.iloc[0]['medicamento'][:50]}...")
                print()
                
            except Exception as e:
                print(f"   ⚠️ Error al leer {archivo}: {e}\n")
                import traceback
                traceback.print_exc()
        else:
            print(f"   ❌ No encontrado: {archivo}\n")
    
    if not dataframes:
        print("❌ ERROR: No se encontraron archivos Excel para procesar")
        return None
    
    # Unifica todos los dataframes
    medicamentos_totales = pd.concat(dataframes, ignore_index=True)
    
    # Elimina duplicados exactos
    medicamentos_unicos = medicamentos_totales.drop_duplicates(
        subset=['numero_registro', 'medicamento'],
        keep='first'
    )
    
    # Crea carpeta si no existe
    os.makedirs(processed_dir, exist_ok=True)
    
    # Guarda en formato limpio
    output_path = os.path.join(processed_dir, 'cimavet_completo.csv')
    medicamentos_unicos.to_csv(
        output_path,
        index=False,
        encoding='utf-8'
    )
    
    print("\n" + "="*70)
    print("✅ IMPORTACIÓN COMPLETADA EXITOSAMENTE")
    print("="*70)
    print(f"Total: {len(medicamentos_unicos)} medicamentos únicos procesados")
    print(f"  - Perros: {len(medicamentos_unicos[medicamentos_unicos['especie']=='Perro'])}")
    print(f"  - Gatos: {len(medicamentos_unicos[medicamentos_unicos['especie']=='Gato'])}")
    if 'Reproducción' in medicamentos_unicos['especie'].values:
        print(f"  - Reproducción: {len(medicamentos_unicos[medicamentos_unicos['especie']=='Reproducción'])}")
    print(f"\n📁 Guardado en: {output_path}\n")
    
    # Muestra muestra de datos
    print("📊 MUESTRA DE 5 MEDICAMENTOS:")
    print("-" * 70)
    for idx, row in medicamentos_unicos.head(5).iterrows():
        print(f"\n{idx+1}. {row['medicamento']}")
        print(f"   Nº Registro: {row['numero_registro']}")
        print(f"   Principios activos: {row['principios_activos']}")
        print(f"   Prescripción: {row['prescripcion']}")
        print(f"   Especie: {row['especie']}")
    
    print("\n" + "-" * 70)
    print("📋 COLUMNAS DISPONIBLES:")
    for i, col in enumerate(medicamentos_unicos.columns, 1):
        print(f"  {i}. {col}")
    
    print("="*70 + "\n")
    
    return medicamentos_unicos

if __name__ == "__main__":
    df = importar_excels_cimavet()
    if df is not None:
        print("✅ Script completado exitosamente\n")
        
        # Análisis adicional
        print("📈 ANÁLISIS RÁPIDO:")
        print(f"  - Medicamentos por especie: {df['especie'].value_counts().to_dict()}")
        print(f"  - Medicamentos sin prescripción: {len(df[df['prescripcion'].str.contains('No', case=False)])}")
        print(f"  - Medicamentos autorizados: {len(df[df['estado'].str.contains('Autorizado', case=False)])}")
        
    else:
        print("❌ Script falló\n")