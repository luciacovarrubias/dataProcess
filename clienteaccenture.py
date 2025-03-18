import pandas as pd
import numpy as np
from io import BytesIO

def procesar_archivos(uploaded_file1 = None, uploaded_file2 = None, uploaded_hires = None):
    # Leer los archivos de los objetos UploadedFile
    uploaded_file1 = pd.read_excel(uploaded_file1, engine="openpyxl")
    uploaded_file2 = pd.read_excel(uploaded_file2, engine="openpyxl")
    uploaded_hires = pd.read_excel(uploaded_hires, engine="openpyxl", skiprows=39)

    # Verificar que no sean None
    if uploaded_file2 is None or uploaded_file2 is None or uploaded_hires is None:
        raise ValueError("Todos los archivos deben ser proporcionados")
    
    # Unir los DataFrames por filas
    df_final = pd.concat([uploaded_file1, uploaded_file2], ignore_index=True)
    
    # Seleccionar columnas deseadas
    columnas_deseadas = [
        "Candidate Legal Name", "Candidate Legal First Name", "Candidate  Legal Last Name",
        "Company Code", "Management Level", "Hire Date", "Phone Number", "National ID",
        "Date of Birth", "Place Of Birth", "Primary Work Location"
    ]
    df = df_final[columnas_deseadas]
    
    # Ordenar por nombre
    df_sorted = df.sort_values(by="Candidate Legal Name", ascending=True)

    reporte = df_sorted.copy()

    reporte["Hire Date2"] = reporte["Hire Date"]
    reporte["Primary Work Location2"] = reporte["Primary Work Location"]
    reporte["National ID2"] = reporte["National ID"]
    reporte["Company Code2"] = reporte["Company Code"]

    
    # Renombrar columnas para el procesamiento
    template_proceso = reporte.rename(columns={ 
        'Candidate Legal First Name': "Nome",
        'Candidate  Legal Last Name': "Cognome",
        'Company Code': "Company Code",
        'Company Code2': "Gruppo",
        'Management Level': "Qualifica",
        'Hire Date': "Primo giorno in azienda",
        'Hire Date2': "Attivazione Iter",
        'Phone Number': "Telefono",
        'National ID': "Codice Fiscale",
        'National ID2': "Username",
        'Date of Birth': "Data di Nascita",
        'Place Of Birth': "Luogo Di Nascita",
        'Primary Work Location': "Sede dell'utente",
        'Primary Work Location2': "Sede del candidato"
    })

    template_proceso["Lingua"] = "Ita"
    template_proceso["Cittadinanza"] = "Italiana"
    template_proceso["Scadenza"] = np.nan
    template_proceso["Qualifica"] = "Lavoratore"
    
    # Procesar hires
    uploaded_hires.columns = uploaded_hires.iloc[0]  # Usar primera fila como encabezado
    uploaded_hires = uploaded_hires[1:].reset_index(drop=True)
    
    if "Worker" in uploaded_hires.columns:
        uploaded_hires = uploaded_hires.rename(columns={'Worker': "Candidate Legal Name"})
    
    # Limpiar nombres
    template_proceso["Candidate Legal Name"] = template_proceso["Candidate Legal Name"].astype(str).str.strip().str.lower()
    uploaded_hires["Candidate Legal Name"] = uploaded_hires["Candidate Legal Name"].astype(str).str.strip().str.lower()
    
    valores_comunes = template_proceso[template_proceso["Candidate Legal Name"].isin(uploaded_hires["Candidate Legal Name"])]
    
    uploaded_hires_seleccion = uploaded_hires[["Candidate Legal Name", "Employee ID", "Enterprise ID"]]
    valores_comunes = valores_comunes.merge(uploaded_hires_seleccion, on="Candidate Legal Name", how="left")
    
    valores_comunes["Enterprise ID"] = valores_comunes["Enterprise ID"].astype(str) + "@accenture.com"
    valores_comunes["Employee ID2"] = valores_comunes["Employee ID"]
    valores_comunes = valores_comunes.rename(columns={ 
        'Employee ID2': "Matricola",
        'Employee ID': "PersonnelNBR",
        'Enterprise ID': 'E-Mail'
    })
    
    valores_comunes["Username"] = valores_comunes["Username"].str.replace(r"\(ITA-CF\)", "", regex=True).str.strip()
    valores_comunes["Codice Fiscale"] = valores_comunes["Codice Fiscale"].str.replace(r"\(ITA-CF\)", "", regex=True).str.strip()
    valores_comunes["Attivo"] = "1"
    valores_comunes["Programma visite"] = "1"
    valores_comunes["Sottogrupo"] = np.nan
    valores_comunes["Sede dell'utente"] = valores_comunes["Sede dell'utente"].str.split(",").str[0]
    valores_comunes["Sede del candidato"] = valores_comunes["Sede del candidato"].str.split(",").str[0]
    
    def transformar_valor(valores_comunes):
        return {4400: 1, 4401: 8, 4403: 13, 4428: 42}.get(valores_comunes, valores_comunes)
    
    valores_comunes["Gruppo"] = valores_comunes["Gruppo"].apply(transformar_valor)

    def asignar_sottogrupo(row):
        corresponding_row = df_final[df_final["Candidate Legal Name"] == row["Candidate Legal Name"]]
        if not corresponding_row.empty:
            management_level = corresponding_row["Management Level"].values[0]
            gruppo = row["Gruppo"]
            if management_level in [1, 2, 3, 4, 5, 6]:
                return {1: 148, 8: 151, 13: 150, 42: 152}.get(gruppo, row["Sottogrupo"])
        return row["Sottogrupo"]
    
    valores_comunes["Sottogrupo"] = valores_comunes.apply(asignar_sottogrupo, axis=1)

    orden_columnas = ["Attivo", "Nome", "Cognome", "E-Mail", "Telefono",
                    "Luogo Di Nascita", "Data di Nascita", "Cittadinanza",
                    "Codice Fiscale", "Lingua", "Username", "Gruppo", 
                    "Qualifica", "Programma visite", "Primo giorno in azienda",
                    "Attivazione Iter", "Sede dell'utente",
                    "Sede del candidato", "Scadenza", "PersonnelNBR", 
                    "Sottogrupo", "Matricola"]
    
    valores_comunes = valores_comunes[orden_columnas]
    
    output = BytesIO()
    valores_comunes.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)  # Volver al inicio del archivo para que Streamlit lo lea correctamente

    return output


# Ejemplo de uso
# ruta_reporte1 = "C:/Users/lcovarrubias/Documents/I+D+i/dataProcess/data/WD - Report Assunzioni ACN.xlsx"
# ruta_reporte2 = "C:/Users/lcovarrubias/Documents/I+D+i/dataProcess/data/WD - Report Assunzioni ATS.xlsx"
# ruta_hires = "C:/Users/lcovarrubias/Documents/I+D+i/dataProcess/data/Hires by Worker.xlsx"
# ruta_salida = "C:/Users/lcovarrubias/Documents/I+D+i/dataProcess/data/carica_utenti.xlsx"

# procesar_reportes(ruta_reporte1, ruta_reporte2, ruta_hires, ruta_salida)





# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# import sys

# # report_path = sys.argv[1]
# # report_path2 = sys.argv[2]
# # hires_path = sys.argv[3]
# # output_path = "carica_utenti.xlsx"
#     report1 = pd.read_excel("C:/Users/lcovarrubias/Documents/I+D+i/dataProcess/data/WD - Report Assunzioni ACN dal 10 al 14 marzo 2025 con modifiche ed integrazioni - Salary in chiaro (1).xlsx", engine="openpyxl")
#     report1.sort_values(by="Candidate Legal Name", ascending=True)

#     """# Concatenación de ambos reportes"""

#     reporte1 = report1 = pd.read_excel("C:/Users/lcovarrubias/Documents/I+D+i/dataProcess/data/WD - Report Assunzioni ACN dal 10 al 14 marzo 2025 con modifiche ed integrazioni - Salary in chiaro (1).xlsx", engine="openpyxl")
#     reporte2 = report_path2 = pd.read_excel("C:/Users/lcovarrubias/Documents/I+D+i/dataProcess/data/WD - Report Assunzioni ATS dal 10 al 14 marzo 2025 con modifiche ed integrazioni - Salary in chiaro (2).xlsx", engine="openpyxl")
#     # Unir los DataFrames por filas
#     df_final = pd.concat([reporte1, reporte2], ignore_index=True)

#     num_filas = df_final.shape[0]  # La primera dimensión de shape indica las filas
#     num_filas_alt = len(df_final)

#     """##  Limpiamos columnas y nos quedamos solo con las que necesitamos"""

#     columnas_deseadas = ["Candidate Legal Name", "Candidate Legal First Name","Candidate  Legal Last Name",
#                         "Company Code", "Management Level", "Hire Date", "Phone Number", "National ID",
#                         "Date of Birth", "Place Of Birth", "Primary Work Location"]
#     df = df_final[columnas_deseadas]

#     df_sorted = df.sort_values(by="Candidate Legal Name", ascending=True)

#     """
#     ---

#     # Procesamiento de los datos"""

#     carica = pd.read_csv("C:/Users/lcovarrubias/Documents/I+D+i/dataProcess/data/carica utenti_ template (1).csv")

#     reporte = df_sorted.copy()

#     reporte["Hire Date2"] = reporte["Hire Date"]
#     reporte["Primary Work Location2"] = reporte["Primary Work Location"]
#     reporte["National ID2"] = reporte["National ID"]
#     reporte["Company Code2"] = reporte["Company Code"]

#     template_proceso = reporte.rename(columns={
        # 'Candidate Legal First Name': "Nome",
        # 'Candidate  Legal Last Name': "Cognome",
        # 'Company Code': "Company Code",
        # 'Company Code2': "Gruppo",
        # 'Management Level': "Qualifica",
        # 'Hire Date': "Primo giorno in azienda",
        # 'Hire Date2': "Attivazione Iter",
        # 'Phone Number': "Telefono",
        # 'National ID': "Codice Fiscale",
        # 'National ID2': "Username",
        # 'Date of Birth': "Data di Nascita",
        # 'Place Of Birth': "Luogo Di Nascita",
        # 'Primary Work Location': "Sede dell'utente",
        # 'Primary Work Location2': "Sede del candidato"
#     })

    # template_proceso["Lingua"] = "Ita"
    # template_proceso["Cittadinanza"] = "Italiana"
    # template_proceso["Scadenza"] = np.nan
    # template_proceso["Qualifica"] = "Lavoratore"

#     """## Cargamos excel 5"""

#     # hires = pd.read_excel("C:/Users/lcovarrubias/Documents/I+D+i/dataProcess/data/Hires by Worker WR0573 - 05.03.2025 2025-03-05 08_01 GMT-3 (1).xlsx", engine="openpyxl")

#     # print(hires.head())  # Muestra las primeras filas del DataFrame
#     hires = pd.read_excel("C:/Users/lcovarrubias/Documents/I+D+i/dataProcess/data/Hires by Worker WR0573 - 05.03.2025 2025-03-05 08_01 GMT-3 (1).xlsx", 
#                         engine="openpyxl", skiprows=39)

#     # Renombrar columnas correctamente
#     hires.columns = hires.iloc[0]  # Toma la nueva fila como encabezado
#     hires = hires[1:].reset_index(drop=True)  # Elimina la fila duplicada y resetea los índices

#     # Renombrar columna si existe
#     if "Worker" in hires.columns:
#         hires = hires.rename(columns={'Worker': "Candidate Legal Name"})

#     # Mostrar primeras filas
#     print(hires.head())

#     template_proceso["Candidate Legal Name"] = (
#         template_proceso["Candidate Legal Name"].astype(str).str.strip().str.lower()
#     )
#     hires["Candidate Legal Name"] = (
#         hires["Candidate Legal Name"].astype(str).str.strip().str.lower()
#     )

#     valores_comunes = template_proceso[
#         template_proceso["Candidate Legal Name"].isin(hires["Candidate Legal Name"])
#     ]



#     hires_seleccion = hires[["Candidate Legal Name", "Employee ID", "Enterprise ID"]]
#     valores_comunes = valores_comunes.merge(hires_seleccion, on="Candidate Legal Name", how="left")

#     valores_comunes["Enterprise ID"] = valores_comunes["Enterprise ID"].astype(str) + "@accenture.com"
#     valores_comunes["Employee ID2"] = valores_comunes["Employee ID"]
#     valores_comunes = valores_comunes.rename(columns={
        # 'Employee ID2': "Matricola",
        # 'Employee ID': "PersonnelNBR",
        # 'Enterprise ID': 'E-Mail'
#     })

    # valores_comunes["Username"] = valores_comunes["Username"].str.replace(r"\(ITA-CF\)", "", regex=True).str.strip()
    # valores_comunes["Codice Fiscale"] = valores_comunes["Codice Fiscale"].str.replace(r"\(ITA-CF\)", "", regex=True).str.strip()
    # valores_comunes["Attivo"] = "1"
    # valores_comunes["Programma visite"] = "1"
    # valores_comunes["Sottogrupo"] = np.NaN
    # valores_comunes["Sede dell'utente"] = valores_comunes["Sede dell'utente"].str.split(",").str[0]

#     def transformar_valor(valor):
#         return {4400: 1, 4401: 8, 4403: 13, 4428: 42}.get(valor, valor)

#     valores_comunes["Gruppo"] = valores_comunes["Gruppo"].apply(transformar_valor)

    # def asignar_sottogrupo(row):
    #     corresponding_row = df_final[df_final["Candidate Legal Name"] == row["Candidate Legal Name"]]
    #     if not corresponding_row.empty:
    #         management_level = corresponding_row["Management Level"].values[0]
    #         gruppo = row["Gruppo"]
    #         if management_level in [1, 2, 3, 4, 5, 6]:
    #             return {1: 148, 8: 151, 13: 150, 42: 152}.get(gruppo, row["Sottogrupo"])
    #     return row["Sottogrupo"]

#     valores_comunes["Sottogrupo"] = valores_comunes.apply(asignar_sottogrupo, axis=1)

#     orden_columnas = ["Attivo", "Nome", "Cognome", "E-Mail", "Telefono", "Luogo Di Nascita", "Data di Nascita", "Cittadinanza", "Codice Fiscale", "Lingua", "Username", "Gruppo", "Qualifica", "Programma visite", "Primo giorno in azienda", "Attivazione Iter", "Sede dell'utente", "Sede del candidato", "Scadenza", "PersonnelNBR", "Sottogrupo", "Matricola"]
#     valores_comunes = valores_comunes[orden_columnas]

#     valores_comunes.to_excel("C:/Users/lcovarrubias/Documents/I+D+i/dataProcess/data/carica_utenti.xlsx", index=False, engine="openpyxl")


# -*- coding: utf-8 -*-
# """clienteAccenture.ipynb

# Automatically generated by Colab.

# Original file is located at
#     https://colab.research.google.com/drive/1usCfdzzvpRyDW06wpyqjfewDuDN3PDG9
# """

# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns


# report1 = pd.read_excel("/content/WD - Report Assunzioni ACN dal 10 al 14 marzo 2025 con modifiche ed integrazioni - Salary in chiaro (1).xlsx", engine="openpyxl")

# report1.sort_values(by="Candidate Legal Name", ascending=True)

# """# Concatenación de ambos reportes"""

# reporte1 = pd.read_excel("/content/WD - Report Assunzioni ACN dal 10 al 14 marzo 2025 con modifiche ed integrazioni - Salary in chiaro (1).xlsx", engine="openpyxl")
# reporte2 = pd.read_excel("/content/WD - Report Assunzioni ATS dal 10 al 14 marzo 2025 con modifiche ed integrazioni - Salary in chiaro (2).xlsx", engine="openpyxl")

# # Unir los DataFrames por filas
# df_final = pd.concat([reporte1, reporte2], ignore_index=True)

# # Guardar el resultado en un nuevo archivo
# df_final.to_excel("df_final.xlsx", index=False, engine="openpyxl")

# num_filas = df_final.shape[0]  # La primera dimensión de shape indica las filas
# num_filas_alt = len(df_final)

# """##  Limpiamos columnas y nos quedamos solo con las que necesitamos"""

# columnas_deseadas = ["Candidate Legal Name", "Candidate Legal First Name","Candidate  Legal Last Name",
#                      "Company Code", "Management Level", "Hire Date", "Phone Number", "National ID",
#                      "Date of Birth", "Place Of Birth", "Primary Work Location"]  # Cambia por los nombres de las columnas que necesitas
# df = pd.read_excel("/content/df_final.xlsx", usecols=columnas_deseadas, engine="openpyxl")

# df.columns

# df_sorted = df.sort_values(by="Candidate Legal Name", ascending=True)  ##Nota: los nombres que no estan en mayúscula, van a lo último

# df_sorted.to_excel("datos_filtrados.xlsx", index=False, engine="openpyxl")

# """

# ---

# # Procesamiento de los datos"""

# carica = pd.read_csv("/content/carica utenti_ template (1).csv")

# reporte = pd.read_excel("/content/datos_filtrados.xlsx", engine="openpyxl")

# reporte["Hire Date2"] =reporte["Hire Date"]
# reporte["Primary Work Location2"] = reporte["Primary Work Location"]
# reporte["National ID2"] = reporte["National ID"]
# reporte["Company Code2"] = reporte["Company Code"]

# template_proceso = reporte = reporte.rename(columns={
#     'Candidate Legal First Name':"Nome",
#        'Candidate  Legal Last Name':"Cognome",
#      'Company Code':"Company Code",
#     'Company Code2':"Gruppo",
#      'Management Level':"Qualifica",
#        'Hire Date':"Primo giorno in azienda",
#     'Hire Date2':"Attivazione Iter",
#      'Phone Number':"Telefono",
#      'National ID':"Codice Fiscale",
#     'National ID2':"Username",
#      'Date of Birth':"Data di Nascita",
#        'Place Of Birth':"Luogo Di Nascita",
#     'Primary Work Location':"Sede dell'utente",
#     'Primary Work Location2':"Sede del candidato"
# })

# template_proceso["Lingua"] = "Ita"
# template_proceso["Cittadinanza"] ="Italiana"
# template_proceso["Scadenza"] = np.nan
# template_proceso["Qualifica"] = "Lavoratore"

# """## Cargamos excel 5"""

# hires = pd.read_excel("/content/Hires by Worker WR0573 - 05.03.2025 2025-03-05 08_01 GMT-3 (1).xlsx", engine="openpyxl")

# hires = hires.iloc[39:] #limpiamos hasta fila 39

# hires.to_excel("hires_modificado.xlsx", index=False, engine="openpyxl")

# hires_limpio= pd.read_excel("/content/hires_modificado.xlsx", engine="openpyxl")

# hires_limpio.columns = hires_limpio.iloc[0]

# # Eliminar la primera fila ahora que la hemos usado como encabezado
# hires_limpio = hires_limpio.drop(0)

# # Resetear los índices
# hires_limpio = hires_limpio.reset_index(drop=True)

# hires_limpio.columns

# hires_limpio.sort_values(by="Worker", ascending=True)

# hires_limpio = hires_limpio.rename(columns={
#     'Worker':"Candidate Legal Name"
#     })

# template_proceso["Candidate Legal Name"] = (
#     template_proceso["Candidate Legal Name"].astype(str).str.strip().str.lower()
# )
# hires_limpio["Candidate Legal Name"] = (
#     hires_limpio["Candidate Legal Name"].astype(str).str.strip().str.lower()
# )

# valores_comunes = template_proceso[
#     template_proceso["Candidate Legal Name"].isin(hires_limpio["Candidate Legal Name"])
# ]
# valores_comunes.to_excel("valores_comunes.xlsx", index=False, engine="openpyxl")

# print("Archivo guardado como 'valores_comunes.xlsx'")

# print(f"Valores comunes encontrados: {len(valores_comunes)}")

# valores_no_encontrados = template_proceso[
#     ~template_proceso["Candidate Legal Name"].isin(hires_limpio["Candidate Legal Name"])
# ]
# print("\nValores en template_proceso pero NO en hires_limpio:")
# print(valores_no_encontrados["Candidate Legal Name"].head(10))  # Mostrar los primeros 10

# hires_limpio_seleccion = hires_limpio[["Candidate Legal Name", "Employee ID", "Enterprise ID"]]

# # Hacer un merge para agregar Employee ID y Enterprise ID al archivo valores_comunes
# valores_comunes = valores_comunes.merge(hires_limpio_seleccion, on="Candidate Legal Name", how="left")

# # Guardar el resultado en un nuevo archivo
# valores_comunes.to_excel("valores_comunes_completos.xlsx", index=False, engine="openpyxl")

# valores_comunes_completos = pd.read_excel("/content/valores_comunes_completos.xlsx", engine="openpyxl")
# valores_comunes_completos["Enterprise ID"] = valores_comunes_completos["Enterprise ID"].astype(str) + "@accenture.com"

# valores_comunes_completos["Employee ID2"] = valores_comunes_completos["Employee ID"]
# valores_comunes_completos = valores_comunes_completos.rename(columns={
#     'Employee ID2':"Matricola",
#     'Employee ID':"PersonnelNBR",
#     'Enterprise ID': 'E-Mail'})

# valores_comunes_completos["Username"] = valores_comunes_completos["Username"].str.replace(r"\(ITA-CF\)", "", regex=True).str.strip()
# valores_comunes_completos["Codice Fiscale"] = valores_comunes_completos["Codice Fiscale"].str.replace(r"\(ITA-CF\)", "", regex=True).str.strip()
# valores_comunes_completos["Attivo"] = "1"
# valores_comunes_completos["Programma visite"] = "1"
# valores_comunes_completos["Sottogrupo"] = np.NaN
# valores_comunes_completos["Sede dell'utente"] = valores_comunes_completos["Sede dell'utente"].str.split(",").str[0]

# def transformar_valor(valor):
#     if valor == 4400:
#         return 1
#     elif valor == 4401:
#         return 8
#     elif valor == 4403:
#         return 13
#     elif valor == 4428:
#         return 42
#     else:
#         return valor

# valores_comunes_completos["Gruppo"] = valores_comunes_completos["Gruppo"].apply(transformar_valor)

# def asignar_sottogrupo(row):
#     # Buscar el valor correspondiente en df_final
#     corresponding_row = df_final[df_final["Candidate Legal Name"] == row["Candidate Legal Name"]]

#     if not corresponding_row.empty:
#         # Si el valor de Managmente Level está entre 1 y 6
#         management_level = corresponding_row["Management Level"].values[0]
#         gruppo = row["Gruppo"]

#         if management_level in [1, 2, 3, 4, 5, 6]:
#             if gruppo == 1:
#                 return 148
#             elif gruppo == 8:
#                 return 151
#             elif gruppo == 13:
#                 return 150
#             elif gruppo == 42:
#                 return 152

#     return row["Sottogrupo"]  # Mantener el valor original si no se cumple la condición

# # Aplicar la función a cada fila de valores_comunes_completos
# valores_comunes_completos["Sottogrupo"] = valores_comunes_completos.apply(asignar_sottogrupo, axis=1)

# orden_columnas = ["Attivo", "Nome", "Cognome", "E-Mail", "Telefono","Luogo Di Nascita",
#                   "Data di Nascita", "Cittadinanza", "Codice Fiscale", "Lingua", "Username", "Gruppo",
#                   "Qualifica", "Programma visite","Primo giorno in azienda", "Attivazione Iter",
#                   "Sede dell'utente", "Sede del candidato","Scadenza", "PersonnelNBR", "Sottogrupo",
#                   "Matricola"]

# valores_comunes_completos = valores_comunes_completos[orden_columnas]

# valores_comunes_completos.to_excel("carica utenti.xlsx", index=False, engine="openpyxl")





# -----------------------------------------------------------------------------------------------
# import streamlit as st
# import pandas as pd
# import numpy as np

# # Función de procesamiento
# def procesar_archivos(report_path, report_path2, hires_path):
#     # Cargar los reportes
#     reporte1 = pd.read_excel(report_path, engine="openpyxl")
#     reporte2 = pd.read_excel(report_path2, engine="openpyxl")

#     # Concatenar los dos reportes
#     df_final = pd.concat([reporte1, reporte2], ignore_index=True)

#     # Definir las columnas de interés
#     columnas_deseadas = ["Candidate Legal Name", "Candidate Legal First Name", "Candidate Legal Last Name",
#                          "Company Code", "Management Level", "Hire Date", "Phone Number", "National ID",
#                          "Date of Birth", "Place Of Birth", "Primary Work Location"]
#     df = df_final[columnas_deseadas]

#     # Ordenar los datos por "Candidate Legal Name"
#     df_sorted = df.sort_values(by="Candidate Legal Name", ascending=True)

#     # Procesamiento de los datos
#     template_proceso = df_sorted.copy()

#     # Crear nuevas columnas renombradas
#     template_proceso["Hire Date2"] = template_proceso["Hire Date"]
#     template_proceso["Primary Work Location2"] = template_proceso["Primary Work Location"]
#     template_proceso["National ID2"] = template_proceso["National ID"]
#     template_proceso["Company Code2"] = template_proceso["Company Code"]

#     template_proceso = template_proceso.rename(columns={
#         'Candidate Legal First Name': "Nome",
#         'Candidate Legal Last Name': "Cognome",
#         'Company Code': "Company Code",
#         'Company Code2': "Gruppo",
#         'Management Level': "Qualifica",
#         'Hire Date': "Primo giorno in azienda",
#         'Hire Date2': "Attivazione Iter",
#         'Phone Number': "Telefono",
#         'National ID': "Codice Fiscale",
#         'National ID2': "Username",
#         'Date of Birth': "Data di Nascita",
#         'Place Of Birth': "Luogo Di Nascita",
#         'Primary Work Location': "Sede dell'utente",
#         'Primary Work Location2': "Sede del candidato"
#     })

#     # Agregar columnas adicionales
#     template_proceso["Lingua"] = "Ita"
#     template_proceso["Cittadinanza"] = "Italiana"
#     template_proceso["Scadenza"] = np.nan
#     template_proceso["Qualifica"] = "Lavoratore"

#     # Cargar el archivo hires
#     hires = pd.read_excel(hires_path, engine="openpyxl", skiprows=39)

#     # Renombrar columnas
#     hires.columns = hires.iloc[0]
#     hires = hires[1:].reset_index(drop=True)

#     if "Worker" in hires.columns:
#         hires = hires.rename(columns={'Worker': "Candidate Legal Name"})

#     # Procesar nombres
#     template_proceso["Candidate Legal Name"] = template_proceso["Candidate Legal Name"].astype(str).str.strip().str.lower()
#     hires["Candidate Legal Name"] = hires["Candidate Legal Name"].astype(str).str.strip().str.lower()

#     # Filtrar valores comunes entre ambos DataFrames
#     valores_comunes = template_proceso[template_proceso["Candidate Legal Name"].isin(hires["Candidate Legal Name"])]

#     # Seleccionar columnas relevantes de hires
#     hires_seleccion = hires[["Candidate Legal Name", "Employee ID", "Enterprise ID"]]

#     # Hacer un merge de los datos
#     valores_comunes = valores_comunes.merge(hires_seleccion, on="Candidate Legal Name", how="left")

#     # Procesar valores
#     valores_comunes["Enterprise ID"] = valores_comunes["Enterprise ID"].astype(str) + "@accenture.com"
#     valores_comunes["Employee ID2"] = valores_comunes["Employee ID"]
#     valores_comunes = valores_comunes.rename(columns={
#         'Employee ID2': "Matricola",
#         'Employee ID': "PersonnelNBR",
#         'Enterprise ID': 'E-Mail'
#     })

#     # Limpiar columnas
#     valores_comunes["Username"] = valores_comunes["Username"].str.replace(r"\(ITA-CF\)", "", regex=True).str.strip()
#     valores_comunes["Codice Fiscale"] = valores_comunes["Codice Fiscale"].str.replace(r"\(ITA-CF\)", "", regex=True).str.strip()
#     valores_comunes["Attivo"] = "1"
#     valores_comunes["Programma visite"] = "1"
#     valores_comunes["Sottogrupo"] = np.NaN
#     valores_comunes["Sede dell'utente"] = valores_comunes["Sede dell'utente"].str.split(",").str[0]

#     # Función de transformación
#     def transformar_valor(valor):
#         return {4400: 1, 4401: 8, 4403: 13, 4428: 42}.get(valor, valor)

#     valores_comunes["Gruppo"] = valores_comunes["Gruppo"].apply(transformar_valor)

#     # Asignar sottogrupo
#     def asignar_sottogrupo(row):
#         corresponding_row = df_final[df_final["Candidate Legal Name"] == row["Candidate Legal Name"]]
#         if not corresponding_row.empty:
#             management_level = corresponding_row["Management Level"].values[0]
#             gruppo = row["Gruppo"]
#             if management_level in [1, 2, 3, 4, 5, 6]:
#                 return {1: 148, 8: 151, 13: 150, 42: 152}.get(gruppo, row["Sottogrupo"])
#         return row["Sottogrupo"]

#     valores_comunes["Sottogrupo"] = valores_comunes.apply(asignar_sottogrupo, axis=1)

#     # Reordenar las columnas
#     orden_columnas = ["Attivo", "Nome", "Cognome", "E-Mail", "Telefono", "Luogo Di Nascita", "Data di Nascita", "Cittadinanza", "Codice Fiscale", "Lingua", "Username", "Gruppo", "Qualifica", "Programma visite", "Primo giorno in azienda", "Attivazione Iter", "Sede dell'utente", "Sede del candidato", "Scadenza", "PersonnelNBR", "Sottogrupo", "Matricola"]
#     valores_comunes = valores_comunes[orden_columnas]

#     return valores_comunes

