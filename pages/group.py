import streamlit as st
import pandas as pd
import os

# --------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# --------------------------------

custom_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Text:ital@0;1&family=Megrim&display=swap');

        html, body, [class*="st-"] {
            font-family: "DM Serif Text", serif;
            font-weight: 400;
            font-style: normal;
        }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

st.title("👥 Soy un grupo")

# --------------------------------
# CARGAR BASE DE DATOS (CSV)
# --------------------------------
# Archivo donde se almacenan los usuarios
USER_DATA_FILE = "info_usuarios.csv"

def find_file(filename):
    """Buscar el archivo en todos los directorios empezando desde la carpeta raíz."""
    for root, _, files in os.walk(os.getcwd()):  # Comienza buscando desde el directorio actual
        if filename in files:
            return os.path.join(root, filename)
    return None


user_file_path = find_file(USER_DATA_FILE)

# --------------------------------
# REGISTRO DE USUARIOS
# --------------------------------

# Preguntar cuántos son en el grupo
grupo_size = st.selectbox("¿Cuántos sois en el grupo?", [2, 3, 4, 5, 6])

# Función para verificar si el usuario está registrado
def verificar_usuario_en_bd(usuario):
    df_usuarios = pd.read_csv(user_file_path)
    return usuario in df_usuarios['nombre_usuario'].values

# Verificar los miembros del grupo
nombres_grupo = []

for i in range(grupo_size):
    nombre = st.text_input(f"Introduce el nombre del usuario #{i+1}:")
    if nombre:
        if verificar_usuario_en_bd(nombre):
            nombres_grupo.append(nombre)
            st.success(f"El usuario {nombre} está registrado.")
        else:
            st.error(f"¡Error! El usuario {nombre} no está registrado en la base de datos. No puedes continuar.")
            break  # Si un usuario no está registrado, se detiene el registro de los siguientes
    else:
        if len(nombres_grupo) < i:  # Si hay un nombre ya ingresado, muestra un error
            st.warning("Por favor, introduce todos los nombres.")
        break

if len(nombres_grupo) == grupo_size:
    st.success("¡Todos los miembros del grupo están registrados!")
    
    # Guardamos el estado para saber que se puede continuar
    st.session_state.grupo_registrado = True

    #NO SÉ CÓMO HACERLO!!!!
    if st.button("Continuar a recomendaciones"): st.text("HAY QUE ARREGLAR ESTO")
        
