import docx
import csv

# Cargar el documento Word
doc_path = "libros Mario.docx"
doc = docx.Document(doc_path)

# Lista para guardar los pares (número, título)
libros = []

# Procesar cada párrafo del documento
for para in doc.paragraphs:
    texto = para.text.strip()
    if texto and "–" not in texto:  # Evita entradas vacías o guiones sin título
        partes = texto.split(maxsplit=1)
        if len(partes) == 2 and partes[0].isdigit():
            numero = partes[0]
            titulo = partes[1].strip()
            libros.append((numero, titulo))

# Guardar los resultados en un CSV
csv_path = "libros_extraidos.csv"
with open(csv_path, mode="w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Número", "Título"])
    writer.writerows(libros)

print(f"Se han extraído {len(libros)} libros y guardado en '{csv_path}'")
