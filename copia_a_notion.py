import csv
import requests
from config import HEADERS, DATABASE_ID
from datetime import datetime

NOTION_API_URL = "https://api.notion.com/v1/pages"
NOTION_DATABASE_ID = DATABASE_ID
NOTION_VERSION = "2022-06-28"

def crear_pagina_notion(fila):
    # Normaliza las claves eliminando espacios y BOM
    fila = {k.strip().replace('\ufeff', ''): v for k, v in fila.items()}

    # Convertir fecha a formato ISO 8601 (YYYY-MM-DD)
    fecha_iso = None
    try:
        fecha_iso = datetime.strptime(fila["Fecha de publicación"], "%d/%m/%Y").date().isoformat()
    except Exception:
        fecha_iso = None

    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Título": {"title": [{"text": {"content": fila["Título"]}}]},
            "Autor": {"rich_text": [{"text": {"content": fila["Autor"]}}]},
            "Portada": {"url": fila["Portada"]},
            "Páginas": {"number": int(fila["Páginas"]) if fila["Páginas"].isdigit() else None},
            "Publicación": {"date": {"start": fecha_iso} if fecha_iso else None},
            "Sinopsis": {"rich_text": [{"text": {"content": fila["Sinopsis"]}}]},
            "URL": {"url": fila["URL"]},
        }
    }
    response = requests.post(NOTION_API_URL, headers=HEADERS, json=data)
    if response.status_code != 200:
        print(f"Error al crear página para {fila['Título']}: {response.text}")
    else:
        print(f"Página creada: {fila['Título']}")

def main():
    with open("letras_universales.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for fila in reader:
            crear_pagina_notion(fila)

if __name__ == "__main__":
    main()