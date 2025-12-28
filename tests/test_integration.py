import sys
import os
# Obtiene la ruta de la carpeta donde está ESTE archivo (tests/)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Sube un nivel (..) y entra en 'src'
# Esto crea la ruta: .../RecomendacionMedicamentosVetIA/src
src_path = os.path.join(current_dir, '..', 'src')

# Añade esa ruta al sistema para que Python la vea
sys.path.append(src_path)

from processing.smart_recommendation_engine import SmartRecommendationEngine

def probar_sistema():
    print("🚀 INICIANDO TEST DE INTEGRACIÓN DE DATOS\n")
    
    # 1. Inicializar motor
    try:
        motor = SmartRecommendationEngine()
        print("✅ Motor cargado correctamente")
        
        # --- AÑADE ESTO AQUÍ ---
        print("\n🔍 CHIVATO DE SÍNTOMAS (Lo que el sistema sabe leer):")
        if motor.enfermedades_loader:
            lista = motor.enfermedades_loader.listar_sintomas()
            print(f"👉 Primeros 20 síntomas en base de datos: {lista[:20]}")
            
            # Prueba de búsqueda manual para ver si 'dolor' existe
            print(f"👉 ¿Existe la palabra 'dolor' exacta?: {'dolor' in lista}")
        # -----------------------
    except Exception as e:
        print(f"❌ Error fatal cargando motor: {e}")
        return

    # 2. Definir Casos de Prueba (Edge Cases)
    casos_prueba = [
        {
            "desc": "Caso Normal: Perro con peso",
            "query": "Perro de 20kg con dolor e inflamación"
        },
        {
            "desc": "Caso Peligroso: Raza sensible",
            "query": "Collie de 15kg con parásitos" 
        },
        {
            "desc": "Caso Sin Peso: Gato genérico",
            "query": "Gato con otitis"
        }
    ]

    # 3. Ejecutar pruebas
    for caso in casos_prueba:
        print(f"\n{'='*60}")
        print(f"🧪 TEST: {caso['desc']}")
        print(f"📝 Query: '{caso['query']}'")
        print(f"{'='*60}")
        
        # A. Extracción de parámetros
        params = motor.extraer_parametros_texto(caso['query'])
        print(f"🔍 1. Parámetros extraídos: {params}")
        
        # B. Generación de contexto (Aquí vemos si la dosis se calcula)
        # Nota: Asegúrate de usar el método nuevo 'generar_contexto_completo' 
        # o simularlo aquí llamando a procesar_consulta_chat
        resultado = motor.procesar_consulta_chat(caso['query'])
        
        print(f"💊 2. Medicamentos encontrados: {len(resultado['medicamentos_recomendados'])}")
        
        for med in resultado['medicamentos_recomendados']:
            print(f"\n   --- {med['nombre']} ---")
            
            # SIMULAMOS LA LÓGICA DE CÁLCULO AQUÍ PARA VERLA EN PANTALLA
            # (O llama a tu método interno si ya lo integraste en la clase)
            if params.get('peso'):
                texto_dosis = motor._calcular_dosis_texto(med, params['peso'])
                print(f"   {texto_dosis}")
            else:
                print("   ⚠️ No se puede calcular dosis (falta peso)")
                
    print("\n✅ FIN DE LAS PRUEBAS")

if __name__ == "__main__":
    probar_sistema()