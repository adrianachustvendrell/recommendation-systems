# signup.py
import streamlit as st
import pandas as pd
from pathlib import Path
import time
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

if "new_username" not in st.session_state:
    st.session_state.new_username = None



# --------------------------------
# LEER CSV
# --------------------------------

USER_DATA_FILE = "info_usuarios.csv"

def find_file(filename):
    """Search for the file in all directories starting from the root folder."""
    for root, _, files in os.walk(os.getcwd()):  # Start searching from the current directory
        if filename in files:
            return os.path.join(root, filename)
    return None

# Locate the users.csv file dynamically
user_file_path = find_file(USER_DATA_FILE)
user_data = pd.read_csv(user_file_path)
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

    # Submit button
    submit_button = st.form_submit_button(label="Iniciar sesión")
    #st.markdown("[Don't have an account? Sign up here!](http://localhost:8501/signup)", unsafe_allow_html=True)




# --------------------------------
# MANEJO DE ERRORES
# --------------------------------


if submit_button:
    # Find user in the dataset
    user_row = user_data[user_data["nombre_usuario"] == username]

    if not user_row.empty:
        st.success(f"¡Bienvenido, {username}! ✅")
        st.session_state.user_logged_in = username
        time.sleep(2)
        st.switch_page("pages/recommendation.py")

    else:
        st.error("⚠️ Usuario no encontrado. Por favor, regístrate y vuelve a iniciar sesión.")
        st.page_link("pages/signup.py", label="👉 Regístrate aquí")
