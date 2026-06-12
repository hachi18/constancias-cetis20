import streamlit as st
import pandas as pd
import os

# Nombre del archivo donde se guardarán los datos de forma local
DB_FILE = "datos_servicio_social.csv"

# Forzar la actualización si falta la columna 'Institucion' por cambios anteriores
if os.path.exists(DB_FILE):
    df_check = pd.read_csv(DB_FILE)
    if "Institucion" not in df_check.columns:
        os.remove(DB_FILE)

# Crear el archivo si no existe (Ahora con la columna Institución)
if not os.path.exists(DB_FILE):
    df_init = pd.DataFrame(columns=["Nombre", "Matrícula", "Grupo", "Especialidad", "Institucion"])
    df_init.to_csv(DB_FILE, index=False)

st.title("Sistema de Constancias - CETIS 20")

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

# Creamos pestañas visuales para separar el registro del panel administrativo
tab1, tab2 = st.tabs(["📝 Registro de Alumnos", "⚙️ Panel de Administración"])

# --- PESTAÑA 1: REGISTRO DE ALUMNOS ---
with tab1:
    st.header("Ingresa tus datos para la constancia")
    
    with st.form("form_alumno", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo (Empezando por Apellido Paterno y en MAYÚSCULAS)")
        matricula = st.text_input("Número de Control / Matrícula")
        grupo = st.selectbox("Grupo", LISTA_GRUPOS)
        especialidad = st.selectbox("Especialidad", LISTA_ESPECIALIDADES)
        
        # NUEVO CAMPO: Institución donde harán el servicio social
        institucion = st.text_input("Institución o Dependencia (Donde realizas tu Servicio Social)")
        
        enviar = st.form_submit_button("Registrar Datos")
        
        if enviar:
            if nombre and matricula and institucion:
                # Cargar datos existentes, agregar el nuevo y guardar
                df = pd.read_csv(DB_FILE)
                # Asegurar que se guarden los textos limpios en mayúsculas
                nuevo_alumno = pd.DataFrame([[
                    nombre.upper().strip(), 
                    matricula.strip(), 
                    grupo, 
                    especialidad,
                    institucion.upper().strip()
                ]], columns=df.columns)
                
                df = pd.concat([df, nuevo_alumno], ignore_index=True)
                df.to_csv(DB_FILE, index=False)
                st.success("¡Datos guardados correctamente! Ya puedes avisar a la maestra.")
            else:
                st.error("Por favor, llena todos los campos obligatorios (Nombre, Matrícula e Institución).")

# --- PESTAÑA 2: PANEL DE LA MAESTRA ---
with tab2:
    st.header("Control de Constancias por Grupo")
    
    password = st.text_input("Contraseña de Admin", type="password")
    
    if password == "cetis2026":
        df_maestra = pd.read_csv(DB_FILE)
        
        if not df_maestra.empty:
            st.subheader("Filtros de búsqueda")
            
            col1, col2 = st.columns(2)
            with col1:
                filtro_grupo = st.selectbox("Selecciona el Grupo", ["Todos"] + LISTA_GRUPOS)
            with col2:
                filtro_esp = st.selectbox("Selecciona la Especialidad", ["Todas"] + LISTA_ESPECIALIDADES)
            
            # Aplicar filtros al DataFrame
            df_filtrado = df_maestra.copy()
            if filtro_grupo != "Todos":
                df_filtrado = df_filtrado[df_filtrado["Grupo"] == filtro_grupo]
            if filtro_esp != "Todas":
                df_filtrado = df_filtrado[df_filtrado["Especialidad"] == filtro_esp]
            
            # Mostrar la lista limpia en pantalla
            st.write(f"Alumnos encontrados: {len(df_filtrado)}")
            st.dataframe(df_filtrado)
            
            # Botón para descargar lo filtrado
            csv_filtrado = df_filtrado.to_csv(index=False).encode('utf-8-sig')
            
            nombre_archivo = f"Constancias_{filtro_grupo}.csv" if filtro_grupo != "Todos" else "Constancias_Filtradas.csv"
            
            st.download_button(
                label=f"📥 Descargar lista de {filtro_grupo} para Correspondencia",
                data=csv_filtrado,
                file_name=nombre_archivo,
                mime="text/csv",
            )
        else:
            st.info("Aún no hay alumnos registrados en el sistema.")