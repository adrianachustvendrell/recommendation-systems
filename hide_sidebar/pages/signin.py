# signup.py
import streamlit as st
import pandas as pd
from pathlib import Path
import time

@st.cache_data
def load_user_data():
    file_path = Path("../data/info_usuarios.csv")
    return pd.read_csv(file_path)  # Ensure the CSV file is in the correct directory

user_data = load_user_data()

# Title for the sign-up page
st.title("Inicia sesión")


# Formulario de registro
with st.form(key="signin_form"):
    #st.subheader("Inicia Sesión")

    # User input fields
<<<<<<< HEAD
    username = st.text_input("Introduce tu usuario")
    password = st.text_input("Introduce tu contraseña", type="password")
=======
    username = st.text_input("Ingresa tu nombre de usuario")
>>>>>>> d4ce36815c3f8284a7d5491637e41597f2c8ec04

    # Submit button
    submit_button = st.form_submit_button(label="Submit")
    #st.markdown("[Don't have an account? Sign up here!](http://localhost:8501/signup)", unsafe_allow_html=True)


if submit_button:
    # Find user in the dataset
    user_row = user_data[user_data["nombre_usuario"] == username]

    if not user_row.empty:
        st.success(f"Welcome, {username}!")
        time.sleep(2)
        st.switch_page("app.py") 

<<<<<<< HEAD
        if password == correct_password:
            st.session_state["authenticated"] = True 
            st.success(f"Bienvenido, {username}!")
            # st.switch_page("pages/recs_page.py")
            # st.switch_page("recs_page.py")
        else:
            st.error("Contraseña incorrecta. Introdúcela de nuevo.")
    else:
        st.error("Usuario no encontrado. Revisa tus credenciales.")
=======
    else:
        st.error("Usuario no encontrado. Por favor registrese y vuelva a iniciar sesión.")
        st.page_link("pages/signup.py", label="👉 Regístrate aquí")
>>>>>>> d4ce36815c3f8284a7d5491637e41597f2c8ec04

