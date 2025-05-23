# signup.py
import streamlit as st
st.set_page_config(page_title="Iniciar sesión", page_icon="🚀", layout="wide")
import pandas as pd
from pathlib import Path
import time
import os
import gspread
from google.oauth2.service_account import Credentials

# Alcances requeridos
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource
def get_client():
    # Usar las credenciales directamente desde st.secrets
    creds = Credentials.from_service_account_info(st.secrets["google"], scopes=scope)
    return gspread.authorize(creds)



client = get_client()

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

if "new_username" not in st.session_state:
    st.session_state.new_username = None



# --------------------------------
# LEER CSV
# --------------------------------

USUARIOS_HOJA = "info_usuarios"
usuarios_sheet = client.open("info_usuarios").sheet1

def find_file(filename):
    """Search for the file in all directories starting from the root folder."""
    for root, _, files in os.walk(os.getcwd()):  # Start searching from the current directory
        if filename in files:
            return os.path.join(root, filename)
    return None

# Locate the users.csv file dynamically
user_data = pd.DataFrame(usuarios_sheet.get_all_records())


if st.button("🏠 Home"):
    st.switch_page("app.py") 


# Title for the sign-up page
st.title("🔑 Inicia sesión")



# --------------------------------
# FORMULARIO DE SIGN IN
# --------------------------------

# Formulario de registro
with st.form(key="signin_form"):
    if st.session_state.new_username:
        #st.subheader("Inicia Sesión")

        # User input fields
        username = st.text_input("Introudce tu usuario", value=st.session_state.new_username)
    else:
        username = st.text_input("Introudce tu usuario")
        st.session_state.new_username = username

    # Submit button
    submit_button = st.form_submit_button(label="Iniciar sesión")
    #st.markdown("[Don't have an account? Sign up here!](http://localhost:8501/signup)", unsafe_allow_html=True)




# --------------------------------
# MANEJO DE ERRORES
# --------------------------------


if submit_button:
    # Normalizar el nombre de usuario (eliminar espacios y convertir a minúsculas)
    username_normalized = username.strip().lower()
    st.write(f'Usuario:{username_normalized}')

    # Comparar con los nombres de usuario en la base de datos (también normalizados)
    user_row = user_data[user_data["nombre_usuario"].str.strip().str.lower() == username_normalized]

    if not user_row.empty:
        st.success(f"¡Bienvenido, {username}! ✅")
        st.session_state.user_logged_in = username
        time.sleep(2)
        st.switch_page("pages/recommendation.py")
    else:
        st.error("⚠️ Usuario no encontrado. Por favor, regístrate y vuelve a iniciar sesión.")
        st.page_link("pages/signup.py", label="👉 Regístrate aquí")

