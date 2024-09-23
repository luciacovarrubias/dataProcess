import re
import zipfile
import pdfplumber
from io import BytesIO

def process_pdf(uploaded_file, pdf_zip):
    # Leer el archivo PDF cargado
    uploaded_file.seek(0)  # Asegúrate de que el puntero del archivo esté al principio
    text = extract_text_from_pdf(BytesIO(uploaded_file.read()))

    # Print del texto extraído para verificar
    # print("Texto extraído del PDF:")
    # print(text)

    # Buscar nombre
    nombre_match = re.search(r'Cognome e Nome:\s*([A-Z\s]+) Nat[ao] il:', text)
    nombre = nombre_match.group(1).strip() if nombre_match else "No encontrado"
    # print(f"Nombre encontrado: {nombre}")

    # Dividir el texto en líneas
    lines = text.splitlines()

    # Buscar la línea de "GIUDIZIO CONCLUSIVO"
    giudizio_line_index = None
    for i, line in enumerate(lines):
        if "GIUDIZIO CONCLUSIVO" in line:
            giudizio_line_index = i
            break

    # Extraer el giudizio
    if giudizio_line_index is not None and giudizio_line_index + 1 < len(lines):
        giudizio = lines[giudizio_line_index + 1].strip().lower()  # Convertir a minúsculas

        # Comparar con los posibles valores de giudizio
        if giudizio == "idoneo":
            giudizio = "idoneo"
        elif giudizio == "idoneo con prescrizione":
            giudizio = "idoneo con prescrizione"
        elif giudizio == "non idoneo":
            giudizio = "non idoneo"
    else:
        giudizio = "No encontrado"

    # print(f"GIUDIZIO CONCLUSIVO encontrado: {giudizio}")



    # Buscar fecha de scadenza
    scadenza_match = re.search(r'Scadenza visita successiva prevista dal Piano Sanitario:\s*(.+)', text)
    scadenza = scadenza_match.group(1) if scadenza_match else "No encontrado"
    # print(f"Scadenza encontrada: {scadenza}")

    # Crear un nuevo nombre de archivo con la información extraída
    nuevo_nombre = f"{nombre}_{giudizio}_{scadenza}".replace(" ", "_").replace("/", "-") + ".pdf"
    # print(f"Nuevo nombre de archivo: {nuevo_nombre}")

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
