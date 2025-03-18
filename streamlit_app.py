import streamlit as st
import data_processing
import time
import pandas as pd
import clienteaccenture

def main():
    def procesamiento_pdf():
        st.title("App de Procesamiento de PDFs")

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
    

    def ficha_ingreso():
        st.title("Carica Utenti")


        st.subheader("1️⃣ Subí tu primer reporte")
        uploaded_file1 = st.file_uploader("primer reporte", type=["xlsx", "xls"], label_visibility="hidden")
        st.subheader("2️⃣ Subí tu segundo reporte")
        uploaded_file2 = st.file_uploader("segundo reporte", type=["xlsx", "xls"], label_visibility="hidden")
        st.subheader("3️⃣ Subí tu archivo Hires")
        uploaded_hires = st.file_uploader("archivo hire", type=["xlsx", "xls"], label_visibility="hidden")

        if uploaded_file1 and uploaded_file2 and uploaded_hires:
            if st.button("Procesar Reportes ✅"):
                # Llamar a la función de procesamiento con los archivos subidos
                output = clienteaccenture.procesar_archivos(uploaded_file1, uploaded_file2, uploaded_hires)
                progress_text = "Operation in progress. Please wait."
                my_bar = st.progress(0, text=progress_text)

                for percent_complete in range(100):
                        time.sleep(0.01)
                        my_bar.progress(percent_complete + 1, text=progress_text)
                time.sleep(1)
                my_bar.empty()

                # Agregar botón de descarga
                st.download_button(
                    label="Descargar archivo 📥",
                    data=output,
                    file_name="carica_utenti.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                st.balloons()


    def pagina_princiapl():
        st.title("Accenture")
        st.header("Con el menú de la izquierda elegí el proceso de hoy :) ")

    st.sidebar.title("Procesos")
    inicio = st.sidebar.selectbox("Selecciona un proceso", ["Inicio","Procesamiento de PDF's", "Ficha de Ingreso"])

    if inicio == "Inicio":
        pagina_princiapl()

    elif inicio == "Procesamiento de PDF's":
        procesamiento_pdf()

    elif inicio == "Ficha de Ingreso":
        ficha_ingreso()

    st.logo("images/logo.jpg")

    
    st.caption("⫺ Accenture | 2024 Todos los derechos reservados ® ")
        
if __name__ == "__main__":
    main()

##luciaCov