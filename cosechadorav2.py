import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import pandas as pd
import random
import re
import os

# ================= CONFIGURACIÓN =================
URL_BASE = "https://www.idealista.com/alquiler-viviendas/madrid-madrid/"
PAGINAS = 70               # 70 páginas ≈ 2.100 pisos
ARCHIVO = "dataset_madrid_definitivo.csv"

# ================= BARRIOS =================
BARRIOS_OFICIALES = [
    "Lavapiés","Embajadores","Malasaña","Universidad","Justicia","Chueca","Sol","Palacio",
    "Cortes","Huertas","Letras","La Latina","Opera","Centro","Recoletos","Goya",
    "Fuente del Berro","Guindalera","Lista","Castellana","Salamanca","Gaztambide",
    "Arapiles","Trafalgar","Almagro","Ríos Rosas","Vallehermoso","Nuevos Ministerios",
    "Pacífico","Adelfas","Estrella","Ibiza","Jerónimos","Niño Jesús","Retiro",
    "Bellas Vistas","Cuatro Caminos","Castillejos","Almenara","Valdeacederas",
    "Berruguete","Tetuán","El Viso","Prosperidad","Ciudad Jardín","Hispanoamérica",
    "Nueva España","Castilla","Chamartín","Arganzuela","Acacias","Chopera","Imperial",
    "Delicias","Legazpi","Moncloa","Argüelles","Ciudad Universitaria","Aravaca",
    "Fuencarral","El Pardo","Mirasierra","Barrio del Pilar","Las Tablas","Montecarmelo",
    "Latina","Puerta del Ángel","Lucero","Carabanchel","Usera","Puente de Vallecas",
    "Villa de Vallecas","Moratalaz","Ciudad Lineal","Arturo Soria","Ventas",
    "Pueblo Nuevo","Hortaleza","Pinar del Rey","Valdebebas","Sanchinarro",
    "Villaverde","Vicálvaro","San Blas","Canillejas","Barajas"
]

def detectar_barrio(titulo):
    t = titulo.lower()
    for b in BARRIOS_OFICIALES:
        if b.lower() in t:
            return b
    return "Otros Madrid"

# ================= GUARDADO INCREMENTAL =================
def guardar_csv(registros):
    df = pd.DataFrame(registros)
    if not os.path.isfile(ARCHIVO):
        df.to_csv(ARCHIVO, sep=";", index=False, encoding="utf-8-sig")
    else:
        df.to_csv(ARCHIVO, sep=";", index=False, mode="a", header=False, encoding="utf-8-sig")

# ================= SCRAPER =================
print("🚜 INICIANDO SCRAPER DEFINITIVO IDEALISTA")

options = uc.ChromeOptions()
options.add_argument("--incognito")
options.add_argument("--guest")
driver = uc.Chrome(options=options)

total_guardados = 0

try:
    for p in range(66, PAGINAS + 1):
        url = URL_BASE if p == 1 else f"{URL_BASE}pagina-{p}.htm"
        print(f"\n📄 Página {p}/{PAGINAS}")
        driver.get(url)
        time.sleep(random.uniform(4, 7))

        soup = BeautifulSoup(driver.page_source, "html.parser")
        items = soup.find_all("article", class_="item")
        print(f"   → {len(items)} anuncios encontrados")

        registros_pagina = []

        for item in items:
            try:
                # -------- LISTADO --------
                precio_tag = item.find("span", class_="item-price")
                if not precio_tag:
                    continue
                precio = int(precio_tag.text.replace(".", "").replace("€/mes", "").strip())

                link = item.find("a", class_="item-link")
                if not link:
                    continue

                titulo = link.text.strip()
                url_detalle = "https://www.idealista.com" + link["href"]
                barrio = detectar_barrio(titulo)

                metros = 0
                habitaciones = 0
                planta = -1

                for d in item.find_all("span", class_="item-detail"):
                    txt = d.text.lower()
                    if "m²" in txt:
                        metros = int(re.findall(r"\d+", txt.replace(".", ""))[0])
                    elif "hab" in txt:
                        habitaciones = int(re.findall(r"\d+", txt)[0])
                    elif "bajo" in txt:
                        planta = 0
                    elif "planta" in txt and re.search(r"\d+", txt):
                        planta = int(re.findall(r"\d+", txt)[0])

                # -------- DETALLE --------
                driver.get(url_detalle)
                time.sleep(random.uniform(2, 4))
                s = BeautifulSoup(driver.page_source, "html.parser")
                texto = s.get_text(" ", strip=True).lower()

                ascensor = 1 if "ascensor" in texto else 0
                garaje = 1 if "garaje" in texto or "parking" in texto else 0
                terraza = 1 if "terraza" in texto or "ático" in texto else 0
                aire = 1 if "aire acondicionado" in texto else 0

                amueblado = 1 if "amueblado" in texto or "cocina equipada" in texto else 0
                if "sin amueblar" in texto:
                    amueblado = 0

                reformado = 1 if any(x in texto for x in [
                    "reformado","a estrenar","reforma integral","obra nueva",
                    "todo nuevo","rehabilitado","recién reformado"
                ]) else 0

                banos = 1
                m = re.search(r"(\d+)\s*baño", texto)
                if m:
                    banos = int(m.group(1))

                registros_pagina.append({
                    "titulo": titulo,
                    "barrio": barrio,
                    "precio": precio,
                    "metros": metros,
                    "habitaciones": habitaciones,
                    "banos": banos,
                    "planta": planta,
                    "ascensor": ascensor,
                    "garaje": garaje,
                    "terraza": terraza,
                    "aire": aire,
                    "amueblado": amueblado,
                    "reformado": reformado,
                    "url": url_detalle
                })

                print(f"   ✔ {barrio} | {metros}m² | {precio}€")

            except Exception:
                continue

        if registros_pagina:
            guardar_csv(registros_pagina)
            total_guardados += len(registros_pagina)
            print(f"💾 Guardados {len(registros_pagina)} | Total: {total_guardados}")

        if p % 10 == 0:
            print("☕ Pausa anti-baneo (60s)")
            time.sleep(60)
        else:
            time.sleep(2)

except KeyboardInterrupt:
    print("\n🛑 Proceso interrumpido manualmente")

finally:
    driver.quit()
    print("\n==============================")
    print(f"🏁 FIN DEL SCRAPING")
    print(f"📦 Total pisos guardados: {total_guardados}")
    print(f"📁 Archivo: {ARCHIVO}")
    print("==============================")
