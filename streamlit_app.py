import streamlit as st
import data_processing
import time

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
            progress_text = "Operation in progress. Please wait."
            my_bar = st.progress(0, text=progress_text)

            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1, text=progress_text)
            time.sleep(1)
            my_bar.empty()

            st.success('Procesamiento con éxito!', icon="✅")
            with open(zip_filename, "rb") as f:
                st.download_button(
                    label="Descargar zip",
                    data=f,
                    file_name=zip_filename,
                    mime="application/zip"
                )
            st.balloons()

    st.caption("⫺ Accenture | 2024 Todos los derechos reservados ® ")
        
if __name__ == "__main__":
    main()

##luciaCov