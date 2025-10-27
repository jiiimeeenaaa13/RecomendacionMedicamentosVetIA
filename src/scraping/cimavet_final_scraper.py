"""
SCRAPER CIMAVET - INTERACCIÓN MANUAL CON FORMULARIO
Simula exactamente lo que haces en el navegador
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def crear_driver(headless=False):
    """Crea el driver de Chrome"""
    print("🚀 Iniciando Chrome...")
    
    options = Options()
    
    if headless:
        options.add_argument('--headless')
    
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--start-maximized')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    try:
        driver = webdriver.Chrome(options=options)
        print("✅ Chrome iniciado correctamente")
        return driver
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

def aceptar_cookies(driver):
    """Acepta cookies"""
    try:
        time.sleep(1)
        selectores = [
            "//a[@class='cc-btn cc-allow']",
            "//button[contains(text(), 'Aceptar')]",
        ]
        
        for selector in selectores:
            try:
                boton = driver.find_element(By.XPATH, selector)
                boton.click()
                print("🍪 Cookies aceptadas")
                time.sleep(1)
                return True
            except:
                pass
        return False
    except:
        return False

def buscar_con_formulario_avanzado(driver, especie):
    """Usa el formulario avanzado: abre el modal, rellena y busca"""
    print(f"\n🔍 Buscando: {especie}")
    wait = WebDriverWait(driver, 20)

    try:
        # Paso 1️⃣ - Clic en “Búsqueda avanzada”
        print("   1️⃣ Abriendo búsqueda avanzada...")
        boton_avanzado = wait.until(
            EC.element_to_be_clickable((By.ID, "m_buscadoravanzado"))
        )
        driver.execute_script("arguments[0].click();", boton_avanzado)
        time.sleep(2)

        # Paso 2️⃣ - Esperar el modal del formulario
        print("   2️⃣ Esperando formulario avanzado...")
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.modal-content"))
        )
        print("   ✅ Formulario avanzado visible")

        # Paso 3️⃣ - Localizar campo de especie
        print("   3️⃣ Seleccionando especie...")
        try:
            # El campo suele ser un <select id="especie"> o similar
            select_elem = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select#especie"))
            )

            from selenium.webdriver.support.ui import Select
            selector = Select(select_elem)

            # Buscar opción que contenga el texto de la especie
            opciones = [opt.text.strip().lower() for opt in selector.options]
            coincidencias = [opt for opt in opciones if especie.lower() in opt]

            if coincidencias:
                selector.select_by_visible_text(
                    next(opt for opt in selector.options if especie.lower() in opt.text.lower()).text
                )
                print(f"   ✅ Especie seleccionada: {coincidencias[0]}")
            else:
                print(f"   ⚠️ No se encontró la opción para '{especie}'")

        except Exception as e:
            print(f"   ⚠️ No se pudo seleccionar especie: {e}")

        # Paso 4️⃣ - Clic en el botón “Buscar”
        print("   4️⃣ Ejecutando búsqueda...")
        boton_buscar = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Buscar')]"))
        )
        driver.execute_script("arguments[0].click();", boton_buscar)
        print("   ✅ Búsqueda ejecutada correctamente")

        # Paso 5️⃣ - Esperar resultados visibles
        print("   ⏳ Esperando resultados...")
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#resultados, table"))
        )
        time.sleep(2)
        return True

    except Exception as e:
        print(f"   ❌ Error durante búsqueda avanzada: {str(e)[:150]}")
        return False


def extraer_medicamentos_resultados(driver):
    """Extrae medicamentos de la página de resultados"""
    
    print("   📦 Extrayendo medicamentos...")
    
    try:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        medicamentos = []
        
        # Buscar divs que contengan info de medicamentos
        # Estructura vista en capturas: tarjetas con h4 o divs específicos
        
        # Intentar encontrar por diferentes estructuras
        elementos = soup.find_all(['div', 'article'], class_=['card', 'medication', 'result'])
        
        if not elementos:
            # Buscar divs que contengan patrones característicos
            todos_divs = soup.find_all('div')
            elementos = [d for d in todos_divs 
                        if 'PRINCIPIOS ACTIVOS' in d.get_text().upper()
                        or ('ESPECIE' in d.get_text().upper() and 'LABORATORIO' in d.get_text().upper())]
        
        if not elementos:
            print("   ⚠️ No se encontraron elementos de medicamentos")
            return []
        
        for elem in elementos:
            try:
                texto_completo = elem.get_text()
                
                # Saltar si es muy corto
                if len(texto_completo) < 20:
                    continue
                
                lineas = [l.strip() for l in texto_completo.split('\n') if l.strip() and len(l.strip()) > 2]
                
                med = {
                    'nombre': '',
                    'laboratorio': '',
                    'principios_activos': '',
                    'especies': '',
                    'numero_registro': '',
                    'estado': '',
                }
                
                # Extraer información línea por línea
                i = 0
                while i < len(lineas):
                    linea = lineas[i]
                    
                    # Nombre (generalmente la primera línea larga en mayúsculas)
                    if not med['nombre'] and len(linea) > 15 and linea.isupper():
                        med['nombre'] = linea[:150]
                    
                    # Laboratorio
                    elif 'LABORATORIO' in linea.upper() or 'LABIANA' in linea or 'AXIENCE' in linea or 'CHANELLE' in linea:
                        if not med['laboratorio']:
                            med['laboratorio'] = linea[:100]
                    
                    # Principios activos
                    elif 'PRINCIPIOS ACTIVOS' in linea.upper():
                        if i + 1 < len(lineas):
                            med['principios_activos'] = lineas[i + 1][:150]
                    
                    # Especies
                    elif 'ESPECIE' in linea.upper() and 'DESTINO' in linea.upper():
                        if i + 1 < len(lineas):
                            med['especies'] = lineas[i + 1][:100]
                    
                    # Registro
                    elif 'Nº REGISTRO' in linea or 'N° REGISTRO' in linea:
                        if i + 1 < len(lineas):
                            med['numero_registro'] = lineas[i + 1][:50]
                    
                    # Estado
                    elif 'AUTORIZADO' in linea.upper() or 'COMERCIALIZADO' in linea.upper():
                        med['estado'] = linea[:50]
                    
                    i += 1
                
                # Agregar si tiene nombre
                if med['nombre'] and len(med['nombre']) > 5:
                    medicamentos.append(med)
            
            except Exception as e:
                continue
        
        print(f"   ✅ {len(medicamentos)} medicamentos extraídos")
        return medicamentos
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return []

def guardar_csv(medicamentos, filename):
    """Guarda medicamentos en CSV"""
    if not medicamentos:
        print(f"   ⚠️ No hay medicamentos")
        return False
    
    df = pd.DataFrame(medicamentos)
    df = df.drop_duplicates(subset=['nombre'])
    df = df[df['nombre'].str.len() > 5]  # Filtrar nombres inválidos
    
    if len(df) == 0:
        print(f"   ⚠️ No hay datos válidos")
        return False
    
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"   ✅ Guardado: {os.path.basename(filename)} ({len(df)} medicamentos)")
    return True

def main():
    """Función principal"""
    
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 12 + "SCRAPER CIMAVET - FORMULARIO AVANZADO INTERACTIVO" + " " * 15 + "║")
    print("╚" + "═" * 78 + "╝\n")
    
    os.makedirs('data/raw', exist_ok=True)
    driver = None
    
    # Especies a buscar
    especies = ['perros', 'gatos']
    todos_medicamentos = {}
    
    try:
        driver = crear_driver(headless=False)
        
        print("\n" + "=" * 80)
        print("EXTRAYENDO MEDICAMENTOS POR ESPECIE")
        print("=" * 80)
        
        # Abrir página principal
        print(f"\n🌐 Abriendo página principal...")
        driver.get("https://cimavet.aemps.es/cimavet/publico/home.html")
        time.sleep(2)
        
        # Aceptar cookies
        aceptar_cookies(driver)
        time.sleep(1)
        
        # Para cada especie
        for especie in especies:
            print("\n" + "─" * 80)
            print(f"ESPECIE: {especie.upper()}")
            print("─" * 80)
            
            # Buscar usando formulario avanzado
            if buscar_con_formulario_avanzado(driver, especie):
                # Extraer medicamentos
                meds = extraer_medicamentos_resultados(driver)
                
                if meds:
                    todos_medicamentos[especie] = meds
                    
                    print(f"\n   📋 Primeros 3 medicamentos:")
                    for i, med in enumerate(meds[:3]):
                        print(f"      {i+1}. {med['nombre'][:70]}")
                    
                    # Guardar
                    guardar_csv(meds, f'data/raw/cimavet_{especie}.csv')
            
            # Volver a inicio para siguiente búsqueda
            print("   🔄 Volviendo a página principal...")
            driver.get("https://cimavet.aemps.es/cimavet/publico/home.html")
            time.sleep(2)
        
        # Resumen
        print("\n" + "=" * 80)
        print("RESUMEN FINAL")
        print("=" * 80)
        
        total_unico = 0
        for especie, meds in todos_medicamentos.items():
            print(f"   • {especie.upper()}: {len(meds)} medicamentos")
            total_unico += len(meds)
        
        # Combinar todos
        todos_combinados = []
        nombres_vistos = set()
        
        for meds in todos_medicamentos.values():
            for med in meds:
                if med['nombre'] not in nombres_vistos:
                    todos_combinados.append(med)
                    nombres_vistos.add(med['nombre'])
        
        if todos_combinados:
            guardar_csv(todos_combinados, 'data/raw/cimavet_completo.csv')
            print(f"\n✅ Total de medicamentos únicos: {len(todos_combinados)}")
            print(f"   📁 Archivos guardados en: data/raw/")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if driver:
            driver.quit()
            print("\n🔒 Chrome cerrado")

if __name__ == "__main__":
    main()