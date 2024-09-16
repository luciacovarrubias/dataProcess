import re
import zipfile
import pdfplumber
from io import BytesIO

def process_pdf(uploaded_file, pdf_zip):
    # Leer el archivo PDF cargado
    uploaded_file.seek(0)  # Asegúrate de que el puntero del archivo esté al principio
    text = extract_text_from_pdf(BytesIO(uploaded_file.read()))

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
    uploaded_file.seek(0)  # Reinicia el puntero del archivo para que pueda ser leído nuevamente
    pdf_zip.writestr(nuevo_nombre, uploaded_file.read())

def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

def process_pdfs(uploaded_files, zip_filename):
    # Crear el archivo ZIP para almacenar los PDFs procesados
    with zipfile.ZipFile(zip_filename, 'w') as pdf_zip:
        for uploaded_file in uploaded_files:
            process_pdf(uploaded_file, pdf_zip)

