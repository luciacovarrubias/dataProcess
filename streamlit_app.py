import streamlit as st
import data_processing
import time
import pandas as pd
import clienteaccenture
from streamlit_lottie import st_lottie
import json


def load_lottiefile(filepath: str):
        with open(filepath, "r") as f:
            return json.load(f)

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

            
            # st.info(f"Valores comunes encontrados en los reportes y hires: {clienteaccenture.valores_comunes_encontrados}")
            # st.warning("Valor/es no enontrado/s en el archivo hires:")
            # st.write(clienteaccenture.valores_comunes_no_encontrados)
            st.divider()
            st.subheader("Detalles")
            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    label="⚠️ Valores NO encontrados",
                    value=len(clienteaccenture.valores_comunes_no_encontrados),
                    delta_color="off"
                )
                st.warning("**Valores no encontrados en Hires**")
                st.write(clienteaccenture.valores_comunes_no_encontrados)

            with col2:
                st.metric(
                label="✅ Valores comunes encontrados",
                value=clienteaccenture.valores_comunes_encontrados
                )
                st.success(f"**Valores comunes encontrados:** {clienteaccenture.valores_comunes_encontrados}")
            st.divider()
            
            st.download_button(
                    label="Descargar archivo 📥",
                    data=output,
                    file_name="carica_utenti.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            st.balloons()


def main():
    def pagina_princiapl():
        st.title("Accenture")
        st.header("Con el menú de la izquierda elegí el proceso de hoy :) ")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        col1, col2, col3 = st.columns(3)

        with col1:
            lottie_json = load_lottiefile("icons/wired-flat-1330-rest-api-in-reveal.json")
            st_lottie(lottie_json, speed=0.40, width=130, height=130, key="icono_animado")
        with col2:
            lottie_json = load_lottiefile("icons/wired-flat-1963-yerba-mate-tea-hover-pinch.json")
            st_lottie(lottie_json, speed=1, width=130, height=130, key="icono_animado2")
        with col3:
            lottie_json = load_lottiefile("icons/wired-flat-970-video-conference-in-reveal.json")
            st_lottie(lottie_json, speed=0.40, width=130, height=130, key="icono_animado3")
        # with col4:
        #     lottie_json = load_lottiefile("icons/wired-flat-2844-magic-wand-hover-pinch.json")
        #     st_lottie(lottie_json, speed=1, width=150, height=150, key="icono_animado4")
        # with col5:
        #     lottie_json = load_lottiefile("icons/wired-flat-3042-bonfire-hover-pinch.json")
        #     st_lottie(lottie_json, speed=1, width=150, height=150, key="icono_animado5")



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