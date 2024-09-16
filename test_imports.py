# test_imports.py
try:
    import pdfminer
    import streamlit
    print("Las dependencias se instalaron correctamente.")
except ImportError as e:
    print(f"Error al importar una dependencia: {e}")
