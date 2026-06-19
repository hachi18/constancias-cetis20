import streamlit as st
import pandas as pd
import requests
import json

# URL DE TU APLICACIÓN WEB DE APPS SCRIPT
URL_API = "https://script.google.com/macros/s/AKfycbz1z9TjPs05jsxksRAK_PsiwJyL-LoZ-y6oBhu_-8OCheEsqubNKpSD6MPhGYwk1cdz6w/exec"

st.title("Registro de Servicio Social - CETIS 20")

LISTA_GRUPOS = [
    "6ACM", "6BCM", "6ACV", "6BCV", "6APABM", "6APABV", 
    "6BPABV", "6AMAM", "6AMAV", "6AEV", "6ALCM", "6BLCM", "6ALCV"
]

LISTA_ESPECIALIDADES = [
    "TECNICO EN CONTABILIDAD",
    "TECNICO EN PREPARACION DE ALIMENTOS Y BEBIDAS",
    "TECNICO EN MANTENIMIENTO AUTOMOTRIZ",
    "TECNICO EN ELECTRICIDAD",
    "TECNICO EN LABORATORISTA CLINICO"
]

tab1, tab2 = st.tabs(["📝 Registro de Alumnos", "⚙️ Panel de Administración"])

# --- PESTAÑA 1: REGISTRO DE ALUMNOS ---
with tab1:
    st.header("Ingresa tus datos para la constancia")
    
    with st.form("form_alumno", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo (Empezando por Apellido Paterno y en MAYÚSCULAS)")
        matricula = st.text_input("Número de Control / Matrícula")
        grupo = st.selectbox("Grupo", LISTA_GRUPOS)
        especialidad = st.selectbox("Especialidad", LISTA_ESPECIALIDADES)
        institucion = st.text_input("Institución o Dependencia (Donde realizas tu Servicio Social)")
        
        enviar = st.form_submit_button("Registrar Datos")
        
        if enviar:
            if nombre and matricula and institucion:
                payload = {
                    "nombre": nombre.upper().strip(),
                    "matricula": matricula.strip(),
                    "grupo": grupo,
                    "especialidad": especialidad,
                    "institucion": institucion.upper().strip()
                }
                try:
                    res = requests.post(URL_API, data=json.dumps(payload))
                    if res.status_code == 200:
                        st.success("¡Registro exitoso! Tus datos han sido guardados correctamente en el sistema de Servicio Social.")
                    else:
                        st.error("Error en el servidor de Google. Intenta más tarde.")
                except Exception as e:
                    st.error(f"Hubo un problema al conectar con Google: {e}")
            else:
                st.error("Por favor, llena todos los campos obligatorios.")

# --- PESTAÑA 2: PANEL DE LA MAESTRA ---
with tab2:
    st.header("Control de Constancias por Grupo")
    password = st.text_input("Contraseña de Admin", type="password")
    
    if password == "cetis2026":
        try:
            # Consultar datos directo a Google Sheets
            res = requests.get(URL_API)
            datos_json = res.json()
            
            if len(datos_json) > 1:
                # Convertir la respuesta de Google en un DataFrame limpio
                df_maestra = pd.DataFrame(datos_json[1:], columns=datos_json[0])
                
                st.subheader("Filtros de búsqueda")
                col1, col2 = st.columns(2)
                with col1:
                    filtro_grupo = st.selectbox("Selecciona el Grupo", ["Todos"] + LISTA_GRUPOS)
                with col2:
                    filtro_esp = st.selectbox("Selecciona la Especialidad", ["Todas"] + LISTA_ESPECIALIDADES)
                
                df_filtrado = df_maestra.copy()
                if filtro_grupo != "Todos":
                    df_filtrado = df_filtrado[df_filtrado["Grupo"] == filtro_grupo]
                if filtro_esp != "Todas":
                    df_filtrado = df_filtrado[df_filtrado["Especialidad"] == filtro_esp]
                
                st.write(f"Alumnos encontrados: {len(df_filtrado)}")
                st.dataframe(df_filtrado)
                
                csv_filtrado = df_filtrado.to_csv(index=False).encode('utf-8-sig')
                nombre_archivo = f"Constancias_{filtro_grupo}.csv" if filtro_grupo != "Todos" else "Constancias_Filtradas.csv"
                
                st.download_button(
                    label=f"📥 Descargar lista de {filtro_grupo} para Correspondencia",
                    data=csv_filtrado,
                    file_name=nombre_archivo,
                    mime="text/csv",
                )
            else:
                st.info("Aún no hay alumnos registrados en la hoja de cálculo.")
        except Exception as e:
            st.error(f"No se pudo leer la hoja de cálculo: {e}")