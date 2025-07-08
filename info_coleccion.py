import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Función para extraer datos de un libro individual
def extraer_datos_libro(url, headers=None):
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, 'html.parser')

        # --- VERIFICACIÓN DE COLECCIÓN---
        coleccion_encontrada = ""
        breadcrumbs = soup.find("ol", class_="breadcrumb")
        if breadcrumbs:
            items = breadcrumbs.find_all("li", class_="breadcrumb-item")
            if len(items) > 1 and items[1].find('a'):
                coleccion_encontrada = items[1].find('a').get_text(strip=True)
        if not coleccion_encontrada and "/letras-universales/" in url:
            coleccion_encontrada = "Letras Universales"
        if coleccion_encontrada != "Letras Universales":
            print(f"Advertencia: NO pertenece a 'Letras Universales' (Encontrada: '{coleccion_encontrada}'). Saltando.")
            return None

        # --- SECCIÓN DE EXTRACCIÓN---

        # Título: El h1 con clase 'alpha'
        titulo_tag = soup.find("h1", class_="alpha")
        titulo = titulo_tag.get_text(strip=True) if titulo_tag else ""

        # Autor: El primer <a class="a-link-white"> dentro de <p class="author">
        autor = ""
        author_p = soup.find("p", class_="author")
        if author_p:
            autor_a = author_p.find("a", class_="a-link-white")
            if autor_a:
                autor = autor_a.get_text(strip=True)
        
         # Portada: La imagen está dentro de un div con la clase 'book-cover'
        portada_tag = soup.select_one("div.book-cover img.book-cover-image")
        portada = portada_tag["src"] if portada_tag and portada_tag.has_attr('src') else ""

        # Páginas y Fecha de publicación: Buscar cualquier <li> que tenga un <p class="label">
        paginas, fecha_publicacion = "", ""
        data_items = soup.find_all('li', class_='data-item')
        for item in data_items:
            label = item.find('p', class_='label')
            value = item.find('p', class_='value')
            if label and value:
                if "Páginas" in label.get_text(strip=True):
                    paginas = value.get_text(strip=True)
                elif "Publicación" in label.get_text(strip=True):
                    fecha_publicacion = value.get_text(strip=True)

        # Sinopsis: Buscar el h2 con texto 'Sinopsis' y luego el <p class="description-text">
        sinopsis = ""
        h2_sinopsis = soup.find('h2', class_='delta', string='Sinopsis')
        if h2_sinopsis:
            main_info = h2_sinopsis.find_next('div', class_='main-info')
            if main_info:
                desc = main_info.find('p', class_='description-text')
                if desc:
                    sinopsis = desc.get_text(strip=True)

        return {
            "Título": titulo,
            "Autor": autor,
            "Portada": "https://www.catedra.com" + portada if portada and not portada.startswith("http") else portada,
            "Páginas": paginas,
            "Fecha de publicación": fecha_publicacion,
            "Sinopsis": sinopsis,
            "URL": url,
            "Colección": coleccion_encontrada
        }
    except requests.exceptions.RequestException as e:
        print(f"Error de red o HTTP al acceder a {url}: {e}")
        return None
    except Exception as e:
        print(f"Error al parsear la página {url}: {e}")
        return None


# Función para obtener todas las URLs de libros
def obtener_urls_libros(base_url, headers=None):
    print(f"Obteniendo URLs de libros de {base_url}")
    all_collected_urls = [] # Lista final de URLs únicas recolectadas
    seen_urls_set = set() # Conjunto para almacenar URLs únicas y detectar duplicados eficientemente
    pagina = 1

    while True:
        url_pagina = f"{base_url}&pagina={pagina}"
        print(f"Procesando página {pagina}")
        
        try:
            r = requests.get(url_pagina, headers=headers)
            r.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)
        except requests.exceptions.RequestException as e:
            print(f"Error al solicitar la página {pagina} ({url_pagina}): {e}")
            break # Rompe si hay un error de red o HTTP

        soup = BeautifulSoup(r.content, 'html.parser')

        enlaces_en_pagina = soup.select('div.book-list-item a[href^="/libro/"]')

        if not enlaces_en_pagina:
            print(f"No se encontraron más enlaces en la página {pagina}. Finalizando la paginación.")
            break # No hay enlaces, hemos llegado al final real

        found_new_link_on_this_page = False # Bandera para saber si se encontró al menos un enlace nuevo

        for a in enlaces_en_pagina:
            href = a.get("href")
            if href:
                full_url = "https://www.catedra.com" + href if not href.startswith("http") else href
                
                if full_url not in seen_urls_set:
                    seen_urls_set.add(full_url)
                    all_collected_urls.append(full_url)
                    found_new_link_on_this_page = True # Se encontró un enlace que no habíamos visto antes

        if not found_new_link_on_this_page:
            # Si en esta página no se encontró NINGÚN enlace nuevo, significa que estamos repitiendo contenido
            print(f"No se encontraron nuevos enlaces únicos en la página {pagina}. Posible repetición de contenido. Finalizando la paginación.")
            break

        print(f"Página {pagina} procesada. Total de libros únicos recolectados hasta ahora: {len(all_collected_urls)}")
        pagina += 1
        time.sleep(1) # Retraso para ser respetuoso con el servidor

    return all_collected_urls

# Ejecución principal
base_url = "https://www.catedra.com/busqueda.php?tipobusqueda=coleccion&coleccion=letras-universales&precioMin=0&precioMax=200&texto=&filtro=fecha_publicacion0desc"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8", # Puedes ajustar esto a tu preferencia
    "Referer": "https://www.catedra.com/",
    "DNT": "1"
}

urls = obtener_urls_libros(base_url, headers=headers)

# Extraer la información de cada libro
libros = []
for i, url in enumerate(urls):
    print(f"[{i+1}/{len(urls)}] Extrayendo datos de: {url}")
    datos = extraer_datos_libro(url, headers=headers)
    if datos: # Solo añadir si la extracción fue exitosa
        libros.append(datos)
        print(f"Extraído: {datos['Título']}")
    time.sleep(0.5) # Pequeño retraso entre solicitudes de libros individuales

# Crear dataframe y guardar a CSV
if libros:
    df = pd.DataFrame(libros)
    df.to_csv("letras_universales.csv", index=False, encoding='utf-8-sig')
    print("Datos guardados en letras_universales.csv")
else:
    print("No se extrajeron datos de libros. El DataFrame no fue creado.")