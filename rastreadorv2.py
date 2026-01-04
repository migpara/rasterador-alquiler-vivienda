# ==========================================
# rastreador_v2.py (VERSIÓN SEGURA PARA GITHUB)
# ==========================================
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import re
import random
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# --- CONFIGURACIÓN SEGURA ---
URL_BUSQUEDA = "https://www.idealista.com/alquiler-viviendas/madrid-madrid/"

URL_API = os.getenv("API_URL", "http://localhost:8000/tasar")
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_telegram(mensaje):
    if not TOKEN or not CHAT_ID:
        print("❌ Error: Faltan credenciales de Telegram en el archivo .env")
        return
        
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": CHAT_ID, "text": mensaje})
    except Exception as e:
        print(f"Error enviando Telegram: {e}")
def analizar_oportunidad_texto(descripcion):
    palabras_clave = ['negociable', 'incluida', 'particular', 'urge', 'gastos incluidos']
    encontradas = [p for p in palabras_clave if p in descripcion.lower()]
    return ", ".join(encontradas).upper() if encontradas else ""

def espiar_idealista_selenium():
    print(f"🕵️‍♂️ Iniciando Rastreador V2 (Deep Scan - Entrando en fichas)...")
    options = uc.ChromeOptions()
    options.add_argument('--headless') # No activar headless si quieres ver qué hace(activarlo si se quiere subir a la nube)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = uc.Chrome(options=options)
    pisos_extraidos = []

    try:
        # 1. CARGAR LA LISTA
        driver.get(URL_BUSQUEDA)
        print("⏳ Esperando lista de pisos...")
        time.sleep(5)
        
        # Sacamos solo los LINKS primero
        soup_lista = BeautifulSoup(driver.page_source, 'html.parser')
        articulos = soup_lista.find_all('article', class_='item')
        
        enlaces_pisos = []
        for art in articulos:
            link_tag = art.find('a', class_='item-link')
            if link_tag:
                full_link = "https://www.idealista.com" + link_tag['href']
                enlaces_pisos.append(full_link)

        print(f"📋 Encontrados {len(enlaces_pisos)} enlaces. Procesando uno a uno...")

        # 2. ENTRAR EN CADA PISO
        for i, link in enumerate(enlaces_pisos):
            try:
                print(f"   -> Entrando en piso {i+1}/{len(enlaces_pisos)}...")
                driver.get(link)
                
                # Pausa aleatoria para parecer humano (IMPORTANTE al navegar mucho)
                time.sleep(random.uniform(2, 4))
                
                soup_ficha = BeautifulSoup(driver.page_source, 'html.parser')
                
                # --- EXTRACCIÓN DESDE LA FICHA DETALLADA ---
                
                # TÍTULO
                titulo_tag = soup_ficha.find('span', class_='main-info__title-main')
                titulo = titulo_tag.text.strip() if titulo_tag else "Piso sin título"

                # PRECIO
                precio_tag = soup_ficha.find('span', class_='info-data-price')
                if not precio_tag: continue # Si no hay precio, saltamos
                precio_txt = precio_tag.get_text(strip=True)
                precio = int(re.sub(r'[^\d]', '', precio_txt))

                # CARACTERÍSTICAS (Esto suele estar en un bloque 'details-property-feature-one')
                info_features = soup_ficha.find('div', class_='details-property-feature-one')
                texto_features = info_features.get_text(" ", strip=True).lower() if info_features else ""
                
                # También leemos la descripción larga
                desc_tag = soup_ficha.find('div', class_='comment')
                texto_desc = desc_tag.get_text(" ", strip=True).lower() if desc_tag else ""
                
                texto_total = texto_features + " " + texto_desc

                # --- EXTRACCIÓN DE DATOS ---
                
                # METROS
                metros = 0
                m_metros = re.search(r'(\d+)\s*(?:m²|m2|metros)', texto_features)
                if m_metros: metros = int(m_metros.group(1))

                # HABITACIONES
                habitaciones = 0
                m_hab = re.search(r'(\d+)\s*(?:hab|dorm)', texto_features)
                if m_hab: habitaciones = int(m_hab.group(1))

                # BAÑOS
                banos = 1
                m_banos = re.search(r'(\d+)\s*(?:baño|wc)', texto_features)
                if m_banos: banos = int(m_banos.group(1))

                # PLANTA
                planta = 1 
                if "bajo" in texto_features: planta = 0
                elif "sótano" in texto_features: planta = -1
                elif "entreplanta" in texto_features: planta = 0
                else:
                    m_planta = re.search(r'planta\s*(\d+)', texto_features)
                    if not m_planta: m_planta = re.search(r'(\d+)ª\s*planta', texto_features)
                    if m_planta: planta = int(m_planta.group(1))

                # EXTRAS
                ascensor = ("con ascensor" in texto_features) or ("ascensor" in texto_features and "sin ascensor" not in texto_features)
                garaje = "garaje" in texto_total or "plaza de garaje" in texto_total
                terraza = "terraza" in texto_total or "balcón" in texto_total
                aire = "aire acondicionado" in texto_total
                amueblado = "amueblado" in texto_total or "cocina equipada" in texto_total
                reformado = "reformado" in texto_total or "buen estado" in texto_total
                
                info_extra = analizar_oportunidad_texto(texto_total)

                # --- GUARDADO ---
                if metros > 15 and precio > 300:
                    pisos_extraidos.append({
                        "ubicacion": titulo,
                        "metros": metros,
                        "habitaciones": habitaciones,
                        "banos": banos,
                        "planta": planta,
                        "ascensor": ascensor,
                        "garaje": garaje,
                        "amueblado": amueblado,
                        "reformado": reformado,
                        "terraza": terraza,
                        "aire": aire,
                        "precio_actual": precio,
                        "url": link,
                        "info_extra": info_extra
                    })
                    print(f"      ✅ Leído: {metros}m2, {habitaciones}hab, {banos}wc")

            except Exception as e:
                print(f"      ❌ Error leyendo ficha: {e}")
                continue

    except Exception as e:
        print(f"💥 Error Selenium General: {e}")
    finally:
        if driver: 
            try: driver.quit()
            except: pass
            
    return pisos_extraidos

def ejecutar_rastreo():
    pisos = espiar_idealista_selenium()
    
    if not pisos: 
        print("⚠️ No se han encontrado pisos.")
        return

    print(f"\n🧠 Consultando a la API para {len(pisos)} inmuebles...")
    datos_excel = []

    for piso in pisos:
        try:
            payload = {
                "ubicacion": str(piso['ubicacion']),
                "metros": int(piso['metros']),
                "habitaciones": int(piso['habitaciones']),
                "banos": int(piso['banos']),
                "planta": int(piso['planta']),
                "ascensor": bool(piso['ascensor']),
                "garaje": bool(piso['garaje']),
                "amueblado": bool(piso['amueblado']),
                "reformado": bool(piso['reformado']),
                "terraza": bool(piso['terraza']),
                "aire": bool(piso['aire']),
                "precio_actual": float(piso['precio_actual'])
            }
            
            resp = requests.post(URL_API, json=payload)
            item_excel = piso.copy()
            
            if resp.status_code == 200:
                data = resp.json()
                item_excel['IA_Precio_Justo'] = data['tasacion_ia']
                item_excel['IA_Veredicto'] = data['veredicto']
                item_excel['IA_Diff'] = data['diferencia_porcentaje']
                item_excel['Barrio_IA'] = data['barrio_oficial']
                print(f"✅ Tasado -> Hab:{piso['habitaciones']} | Baños:{piso['banos']} | Planta:{piso['planta']} | {data['veredicto']}")
            else:
                item_excel['IA_Veredicto'] = f"ERROR API {resp.status_code}"
                print(f"❌ Error API: {resp.text}")

            datos_excel.append(item_excel)

        except Exception as e:
            print(f"Error conexión: {e}")

    if datos_excel:
        df = pd.DataFrame(datos_excel)
        cols = ['IA_Veredicto', 'IA_Diff', 'precio_actual', 'IA_Precio_Justo', 'Barrio_IA', 'ubicacion', 'url']
        cols_finales = [c for c in cols if c in df.columns] + [c for c in df.columns if c not in cols]
        df = df[cols_finales]
        df.to_csv("caza_gangas_resultados.csv", index=False, sep=';', encoding='utf-8-sig')
        print(f"\n✅ Resultados guardados en 'caza_gangas_resultados.csv'")

        for _, row in df.iterrows():
            veredicto = str(row.get('IA_Veredicto', ''))
            if "GANGA" in veredicto or "OPORTUNIDAD" in veredicto:
                msg = (
                    f"🚨 {veredicto}\n"
                    f"📍 {row.get('Barrio_IA', 'Zona desconocida')}\n"
                    f"💰 Pide: {row['precio_actual']}€ | IA: {row['IA_Precio_Justo']}€\n"
                    f"📉 {row['IA_Diff']} descuento\n"
                    f"🏠 {row['metros']}m² | {row['habitaciones']} hab | 🚽 {row.get('banos', 1)} baños\n"
                    f"🔗 {row['url']}"
                )
                enviar_telegram(msg)
                time.sleep(1)

if __name__ == "__main__":
    ejecutar_rastreo()