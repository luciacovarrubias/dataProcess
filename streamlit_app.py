import streamlit as st
import data_processing

def main():
    st.title("App de Procesamiento de PDFs")
    st.logo('images/logo.png')

    uploaded_files = st.file_uploader(
        "Seleccionar archivos PDFs", accept_multiple_files=True, type=["pdf"]
    )

    if uploaded_files:
        st.write(f"Has subido {len(uploaded_files)} archivo(s).")

        if st.button("Procesar todos los archivos"):
            zip_filename = "pdfs_procesados.zip"
            data_processing.process_pdfs(uploaded_files, zip_filename)
            with open(zip_filename, "rb") as f:
                st.download_button(
                    label="Descargar zip",
                    data=f,
                    file_name=zip_filename,
                    mime="application/zip"
                )
            st.balloons()
        
if __name__ == "__main__":
    main()