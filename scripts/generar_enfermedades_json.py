#!/usr/bin/env python3
"""
ARCHIVO: scripts/generar_enfermedades_json.py

Genera automáticamente los JSONs para 42 enfermedades + síntomas
Usa los datos que ya tienes en CSVs

Ejecutar: python scripts/generar_enfermedades_json.py
"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Set


class GeneradorEnfermedadesJSON:
    """Genera JSONs de enfermedades desde CSVs existentes"""
    
    def __init__(self):
        self.enfermedades = {}
        self.medicamentos = {}
        self.sintomas_map = {}
    
    def cargar_datos(self):
        """Carga datos de los CSVs"""
        
        print("📥 Cargando datos...")
        
        # 1. Cargar enfermedades procesadas
        try:
            df_enf = pd.read_csv('data/processed/enfermedades_medicamentos_procesado.csv')
            print(f"✅ Enfermedades procesadas: {len(df_enf)} filas")
        except Exception as e:
            print(f"❌ Error cargando enfermedades_procesado: {e}")
            return False
        
        # 2. Cargar medicamentos CIMAVET
        try:
            df_med = pd.read_csv('data/processed/cimavet_completo.csv')
            print(f"✅ Medicamentos CIMAVET: {len(df_med)} filas")
            
            # Crear índice de medicamentos por principios activos
            for idx, row in df_med.iterrows():
                principios = str(row['principios_activos']).split(',')
                self.medicamentos[idx] = {
                    'nombre': row['medicamento'],
                    'registro': row['numero_registro'],
                    'principios': [p.strip() for p in principios],
                    'especie': row['especie'],
                    'prescripcion': row['prescripcion']
                }
        except Exception as e:
            print(f"❌ Error cargando CIMAVET: {e}")
            return False
        
        # 3. Procesar enfermedades
        for idx, row in df_enf.iterrows():
            enfermedad = row['enfermedad']
            categoria = row['categoria']
            especie = row['especie']
            
            # Parsear principios activos como síntomas
            principios = str(row['principios_activos']).split(';')
            principios = [p.strip() for p in principios if p.strip()]
            
            # Crear key única
            key = f"{enfermedad.replace(' ', '_')}_{especie.replace(' ', '_')}"
            
            self.enfermedades[key] = {
                'nombre': enfermedad,
                'categoria': categoria,
                'especie': especie,
                'síntomas': principios,  # Principios activos = síntomas/indicaciones
                'indicaciones': row['indicaciones'],
                'contraindicaciones': row['contraindicaciones'],
                'notas': row['notas'],
                'medicamentos_asociados': self._buscar_medicamentos(principios, especie)
            }
            
            # Mapear síntomas → enfermedades
            for síntoma in principios:
                if síntoma not in self.sintomas_map:
                    self.sintomas_map[síntoma] = []
                self.sintomas_map[síntoma].append(enfermedad)
        
        print(f"✅ Enfermedades procesadas: {len(self.enfermedades)}")
        return True
    
    def _buscar_medicamentos(self, principios_activos: List[str], especie: str) -> List[str]:
        """Busca medicamentos que contengan los principios activos"""
        
        medicamentos_encontrados = []
        
        for idx, med in self.medicamentos.items():
            # Verificar que sea para la especie
            if med['especie'].lower() != especie.lower():
                continue
            
            # Verificar que contenga alguno de los principios
            for principio in principios_activos:
                if any(principio.lower() in p.lower() for p in med['principios']):
                    medicamentos_encontrados.append(f"med_{idx}")
                    break
        
        return medicamentos_encontrados[:5]  # Top 5
    
    def crear_json_enfermedades(self) -> Dict:
        """Crea JSON de enfermedades"""
        
        json_final = {
            "metadata": {
                "total_enfermedades": len(self.enfermedades),
                "fecha_creacion": "2024-11-26",
                "fuente": "CIMAVET + Dr. Helena Adalid Marín",
                "nota": "Generado automáticamente desde CSVs existentes"
            },
            "enfermedades": self.enfermedades
        }
        
        return json_final
    
    def crear_json_sintomas(self) -> Dict:
        """Crea mapeo síntoma → enfermedades"""
        
        # Crear mapeo invertido: síntoma → enfermedades
        sintomas_enfermedades = {}
        
        for enfermedad_key, datos in self.enfermedades.items():
            for síntoma in datos['síntomas']:
                if síntoma not in sintomas_enfermedades:
                    sintomas_enfermedades[síntoma] = []
                sintomas_enfermedades[síntoma].append(datos['nombre'])
        
        json_final = {
            "metadata": {
                "total_sintomas": len(sintomas_enfermedades),
                "fecha_creacion": "2024-11-26"
            },
            "sintomas_enfermedades": sintomas_enfermedades
        }
        
        return json_final
    
    def guardar_jsons(self, dir_salida: str = 'data/knowledge_graph'):
        """Guarda los JSONs generados"""
        
        Path(dir_salida).mkdir(parents=True, exist_ok=True)
        
        # 1. JSON de enfermedades
        print("\n💾 Guardando JSONs...")
        
        json_enf = self.crear_json_enfermedades()
        archivo_enf = f'{dir_salida}/enfermedades_42_completo.json'
        
        with open(archivo_enf, 'w', encoding='utf-8') as f:
            json.dump(json_enf, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {archivo_enf}")
        print(f"   Contiene: {len(json_enf['enfermedades'])} enfermedades")
        
        # 2. JSON de síntomas
        json_sint = self.crear_json_sintomas()
        archivo_sint = f'{dir_salida}/sintomas_enfermedades_mapping.json'
        
        with open(archivo_sint, 'w', encoding='utf-8') as f:
            json.dump(json_sint, f, ensure_ascii=False, indent=2)
        
        print(f"✅ {archivo_sint}")
        print(f"   Contiene: {len(json_sint['sintomas_enfermedades'])} síntomas")
        
        return archivo_enf, archivo_sint
    
    def mostrar_resumen(self):
        """Muestra resumen de enfermedades"""
        
        print("\n" + "="*70)
        print("📊 RESUMEN DE ENFERMEDADES PROCESADAS")
        print("="*70)
        
        # Agrupar por especie
        por_especie = {}
        for key, datos in self.enfermedades.items():
            especie = datos['especie']
            if especie not in por_especie:
                por_especie[especie] = []
            por_especie[especie].append(datos['nombre'])
        
        for especie, enfs in por_especie.items():
            print(f"\n{especie}: {len(enfs)} enfermedades")
            for enf in enfs[:5]:
                print(f"  • {enf}")
            if len(enfs) > 5:
                print(f"  ... y {len(enfs) - 5} más")
        
        # Agrupar por categoría
        print("\n" + "-"*70)
        por_categoria = {}
        for key, datos in self.enfermedades.items():
            cat = datos['categoria']
            if cat not in por_categoria:
                por_categoria[cat] = 0
            por_categoria[cat] += 1
        
        print("\nPor categoría:")
        for cat, count in sorted(por_categoria.items()):
            print(f"  • {cat}: {count}")
        
        print("\n" + "="*70)


def main():
    """Función principal"""
    
    print("\n" + "="*70)
    print("🔧 GENERADOR DE ENFERMEDADES JSON")
    print("="*70)
    
    generador = GeneradorEnfermedadesJSON()
    
    # Cargar datos
    if not generador.cargar_datos():
        print("\n❌ Error: No se pudieron cargar los datos")
        return
    
    # Mostrar resumen
    generador.mostrar_resumen()
    
    # Guardar JSONs
    archivo_enf, archivo_sint = generador.guardar_jsons()
    
    # Mostrar estadísticas
    print("\n" + "="*70)
    print("✅ PROCESO COMPLETADO")
    print("="*70)
    print(f"\n📁 Archivos creados:")
    print(f"   1. {archivo_enf}")
    print(f"   2. {archivo_sint}")
    print(f"\n📊 Datos generados:")
    print(f"   • Total enfermedades: {len(generador.enfermedades)}")
    print(f"   • Total síntomas únicos: {len(generador.sintomas_map)}")
    print(f"   • Total medicamentos indexados: {len(generador.medicamentos)}")
    
    print("\n🎯 Próximo paso:")
    print("   Ejecuta: python scripts/integrar_enfermedades.py")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()