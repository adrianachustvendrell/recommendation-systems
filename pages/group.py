import streamlit as st
import pandas as pd
import os
import time

# --------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# --------------------------------

st.set_page_config(page_title="Descubre Valencia", page_icon="🚀", layout="wide")
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


if "grupo_registrado" not in st.session_state:
    st.session_state.grupo_registrado = False



if st.button("🏠 Home"):
    st.switch_page("app.py")
    
st.title("👥 Soy un grupo")

# Añadir texto adicional debajo del título
st.write("Los grupos pueden ser de máximo 6 personas. Todas ellas deben estar registradas.")

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
usuarios_ingresados = set()  # Usamos un set para evitar nombres duplicados

for i in range(grupo_size):
    nombre = st.text_input(f"Introduce el nombre del usuario #{i+1}:")
    if nombre:
        if nombre in usuarios_ingresados:
            st.error(f"¡Error! El nombre de usuario '{nombre}' ya ha sido introducido.")
        elif verificar_usuario_en_bd(nombre):
            nombres_grupo.append(nombre)
            usuarios_ingresados.add(nombre)  # Agregar a set para evitar duplicados
            st.success(f"El usuario {nombre} está registrado.")
        else:
            st.error("Usuario no encontrado. Por favor, regístrate y vuelve a iniciar sesión.")
            st.page_link("pages/signup.py", label="👉 Regístrate aquí")
            break  # Si un usuario no está registrado, se detiene el registro de los siguientes
    else:
        if len(nombres_grupo) < i:  # Si hay un nombre ya ingresado, muestra un error
            st.warning("Por favor, introduce todos los nombres.")
        break

if len(nombres_grupo) == grupo_size:
    st.success("¡Todos los miembros del grupo están registrados!")
    
    # Guardamos el estado para saber que se puede continuar
    st.session_state.grupo_registrado = True

    if st.button("Continuar a recomendaciones"):
        time.sleep(2)
        st.switch_page("pages/recommendation.py") 
