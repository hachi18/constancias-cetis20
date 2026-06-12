import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.title("Sistema de Constancias - CETIS 20")

# URL DE TU GOOGLE SHEETS (Pega aquí el enlace de tu hoja de cálculo)
URL_HOJA = "https://docs.google.com/spreadsheets/d/TU_ENLACE_AQUI/edit?usp=sharing"

# Establecer la conexión con Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    st.error("Error al conectar con la base de datos. Verifica la configuración de Streamlit Cloud.")

# Listas oficiales del plantel
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
                try:
                    # Leer los datos actuales de Google Sheets
                    df_actual = conn.read(spreadsheet=URL_HOJA, ttl="0d")
                    
                    # Crear el nuevo registro
                    nuevo_alumno = pd.DataFrame([[
                        nombre.upper().strip(), 
                        matricula.strip(), 
                        grupo, 
                        especialidad,
                        institucion.upper().strip()
                    ]], columns=["Nombre", "Matrícula", "Grupo", "Especialidad", "Institucion"])
                    
                    # Combinar y actualizar la nube
                    df_final = pd.concat([df_actual, nuevo_alumno], ignore_index=True)
                    conn.update(spreadsheet=URL_HOJA, data=df_final)
                    
                    st.success("¡Datos guardados correctamente en la nube! Ya puedes avisar a la maestra.")
                except Exception as e:
                    st.error(f"Hubo un problema al guardar los datos: {e}")
            else:
                st.error("Por favor, llena todos los campos obligatorios.")

# --- PESTAÑA 2: PANEL DE LA MAESTRA ---
with tab2:
    st.header("Control de Constancias por Grupo")
    
    password = st.text_input("Contraseña de Admin", type="password")
    
    if password == "cetis2026":
        try:
            # Forzar lectura sin caché (ttl="0d") para ver registros nuevos al instante
            df_maestra = conn.read(spreadsheet=URL_HOJA, ttl="0d")
            
            # Verificar si la hoja tiene registros (omitir si está vacía la fila 2)
            if df_maestra is not None and not df_maestra.empty and df_maestra.iloc[0].notna().any():
                st.subheader("Filtros de búsqueda")
                
                col1, col2 = st.columns(2)
                with col1:
                    filtro_grupo = st.selectbox("Selecciona el Grupo", ["Todos"] + LISTA_GRUPOS)
                with col2:
                    filtro_esp = st.selectbox("Selecciona la Especialidad", ["Todas"] + LISTA_ESPECIALIDADES)
                
                # Aplicar filtros
                df_filtrado = df_maestra.copy()
                if filtro_grupo != "Todos":
                    df_filtrado = df_filtrado[df_filtrado["Grupo"] == filtro_grupo]
                if filtro_esp != "Todas":
                    df_filtrado = df_filtrado[df_filtrado["Especialidad"] == filtro_esp]
                
                st.write(f"Alumnos encontrados: {len(df_filtrado)}")
                st.dataframe(df_filtrado)
                
                # Botón de descarga
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