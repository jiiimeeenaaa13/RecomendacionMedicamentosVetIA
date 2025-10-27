"""
SCRAPER CIMAVET - VERSIÓN QUE FUNCIONA
Extrae TODOS los medicamentos de perros y gatos de CIMAVet

Guarda en: src/scraping/cimavet_final_scraper.py
Ejecuta: python src/scraping/cimavet_final_scraper.py
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def crear_driver():
    """Crea el driver de Chrome configurado correctamente"""
    print("🚀 Iniciando Chrome...")
    
    options = Options()
    options.add_argument('--headless')  # Sin ventana
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--remote-debugging-port=9222')
    
    # IMPORTANTE: Crear directorio temporal único
    temp_dir = f'/tmp/chrome_profile_{int(time.time())}'
    options.add_argument(f'--user-data-dir={temp_dir}')
    
    try:
        driver = webdriver.Chrome(options=options)
        print("✅ Chrome iniciado correctamente")
        return driver
    except Exception as e:
        print(f"❌ Error iniciando Chrome: {e}")
        print("\n💡 Solución: Cierra todos los Chrome abiertos")
        raise

def buscar_medicamentos(driver, termino=""):
    """Busca medicamentos en CIMAVet"""
    
    url = "https://cimavet.aemps.es/cimavet/publico/home.html"
    print(f"\n🌐 Abriendo: {url}")
    
    driver.get(url)
    
    try:
        # Esperar a que cargue el buscador
        wait = WebDriverWait(driver, 15)
        search_box = wait.until(
            EC.presence_of_element_located((By.ID, "inputbuscadorsimple"))
        )
        
        print(f"🔍 Buscando: '{termino}' (vacío = todos)")
        
        if termino:
            search_box.clear()
            search_box.send_keys(termino)
        
        # Hacer clic en buscar
        btn = driver.find_element(By.ID, "btnBuscarSimple")
        btn.click()
        
        # Esperar resultados
        print("⏳ Esperando resultados...")
        time.sleep(5)  # Dar tiempo a que cargue
        
        return True
        
    except Exception as e:
        print(f"❌ Error en búsqueda: {e}")
        return False

def extraer_medicamentos(driver):
    """Extrae medicamentos de la página de resultados"""
    
    print("\n📦 Extrayendo medicamentos...")
    
    # Obtener HTML
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    # Guardar HTML para análisis
    with open('data/raw/cimavet_results.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("   ✓ HTML guardado en: data/raw/cimavet_results.html")
    
    # Extraer texto completo
    texto = soup.get_text(separator='\n')
    lineas = [l.strip() for l in texto.split('\n') if l.strip()]
    
    medicamentos = []
    med_actual = {}
    
    for i, linea in enumerate(lineas):
        
        # Detectar inicio de medicamento (nombre en mayúsculas con mg)
        if len(linea) > 25 and linea.isupper() and ('mg' in linea.lower() or 'PARA' in linea):
            # Guardar medicamento anterior
            if med_actual.get('nombre'):
                medicamentos.append(med_actual.copy())
            
            # Nuevo medicamento
            med_actual = {
                'nombre': linea,
                'laboratorio': '',
                'principios_activos': '',
                'especies': '',
                'numero_registro': '',
                'estado': '',
                'comercializado': ''
            }
        
        # Detectar laboratorio (siguiente línea después del nombre)
        elif med_actual.get('nombre') and not med_actual.get('laboratorio'):
            if any(x in linea for x in ['S.A.', 'S.L.', 'GmbH', 'Limited', 'Inc.']):
                med_actual['laboratorio'] = linea
        
        # Detectar secciones
        elif 'Principios activos' in linea:
            # Siguiente línea es el principio activo
            if i + 1 < len(lineas):
                activos = []
                j = i + 1
                while j < len(lineas) and (lineas[j].startswith('*') or lineas[j].isupper()):
                    activos.append(lineas[j].replace('* ', ''))
                    j += 1