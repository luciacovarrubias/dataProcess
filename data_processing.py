import re
import zipfile
from pdfminer.high_level import extract_text

def process_pdf(uploaded_file, pdf_zip):
    # Leer el archivo PDF cargado
    text = extract_text(uploaded_file)

    # Buscar nombre
    nombre_match = re.search(r'Cognome e Nome:\s*(.+)', text)
    nombre = nombre_match.group(1) if nombre_match else "No encontrado"

    # Dividir el texto en líneas
    lines = text.splitlines()

    # Buscar la línea de "GIUDIZIO CONCLUSIVO"
    giudizio_line_index = None
    for i, line in enumerate(lines):
        if "GIUDIZIO CONCLUSIVO" in line:
            giudizio_line_index = i
            break

    # Extraer el giudizio
    if giudizio_line_index is not None and giudizio_line_index + 2 < len(lines):
        giudizio = lines[giudizio_line_index + 2].strip()
    else:
        giudizio = "No encontrado"

    # Buscar fecha de scadenza
    scadenza_match = re.search(r'Scadenza visita successiva prevista dal Piano Sanitario:\s*(.+)', text)
    scadenza = scadenza_match.group(1) if scadenza_match else "No encontrado"

    # Crear un nuevo nombre de archivo con la información extraída
    nuevo_nombre = f"{nombre}_{giudizio}_{scadenza}".replace(" ", "_").replace("/", "-") + ".pdf"

    # Añadir el archivo PDF procesado al archivo ZIP
    pdf_zip.writestr(nuevo_nombre, uploaded_file.read())

def process_pdfs(uploaded_files, zip_filename):
    # Crear el archivo ZIP para almacenar los PDFs procesados
    with zipfile.ZipFile(zip_filename, 'w') as pdf_zip:
        for uploaded_file in uploaded_files:
            process_pdf(uploaded_file, pdf_zip)

