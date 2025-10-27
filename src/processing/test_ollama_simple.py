import json
import ollama

# Test 1: Verifica que tinyllama responde
print("="*80)
print("🧪 TEST 1: ¿Responde OLLAMA con tinyllama?")
print("="*80 + "\n")

prompt_simple = """
Eres un veterinario. Un dueño llega con un perro de 20kg, raza Boxer, con dolor en las extremidades traseras.
¿Cuál es tu diagnóstico diferencial? Sé conciso.
"""

try:
    print("⏳ Llamando a OLLAMA (tinyllama)...")
    response = ollama.generate(
        model="tinyllama",
        prompt=prompt_simple,
        stream=False
    )
    print("✅ OLLAMA RESPONDIÓ:\n")
    print(response['response'])
    print("\n" + "="*80 + "\n")
except Exception as e:
    print(f"❌ Error: {e}\n")

# Test 2: Carga grafo y verifica estructura
print("="*80)
print("🧪 TEST 2: Verificar estructura del grafo")
print("="*80 + "\n")

with open('data/knowledge_graph/mapeo_enfermedades_medicamentos.json', 'r', encoding='utf-8') as f:
    grafo = json.load(f)

print(f"Total enfermedades: {len(grafo['enfermedades'])}\n")

# Busca enfermedades para PERRO
print("Enfermedades mapeadas para PERRO:\n")
enfs_perro = {}
for clave, datos in grafo['enfermedades'].items():
    if datos['especie'] == 'Perro':
        enfs_perro[clave] = datos
        num_meds = len(datos.get('medicamentos_asociados', []))
        print(f"  {clave:<50} → {num_meds} medicamentos")

print(f"\nTotal: {len(enfs_perro)} enfermedades para Perro\n")

# Test 3: Busca medicamentos para una enfermedad específica
print("="*80)
print("🧪 TEST 3: Buscar medicamentos para una enfermedad")
print("="*80 + "\n")

# Busca "Dolor/Inflamación articular_Perro"
clave_busqueda = "Dolor/Inflamación articular_Perro"

if clave_busqueda in grafo['enfermedades']:
    datos_enf = grafo['enfermedades'][clave_busqueda]
    meds_ids = datos_enf.get('medicamentos_asociados', [])
    
    print(f"Enfermedad: {datos_enf['nombre']}")
    print(f"Medicamentos asociados: {len(meds_ids)}\n")
    
    print("Top 5 medicamentos:\n")
    for i, med_id in enumerate(meds_ids[:5], 1):
        med = grafo['medicamentos'].get(med_id, {})
        print(f"{i}. {med.get('nombre')}")
        print(f"   Principios: {med.get('principios_activos')}")
        print(f"   Prescripción: {med.get('prescripcion')}\n")
else:
    print(f"❌ No encontrada: {clave_busqueda}")
    print(f"Claves disponibles: {list(enfs_perro.keys())[:5]}")

print("="*80)