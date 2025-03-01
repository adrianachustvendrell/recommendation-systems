# signup.py
import streamlit as st

# Title for the sign-up page
st.title("Inicia sesión")


# Formulario de registro
with st.form(key="signin_form"):
    #st.subheader("Inicia Sesión")

    # Datos básicos
    new_username = st.text_input("Introduce tu usuario")
    new_password = st.text_input("Introduce tu contraseña", type="password")
    # Un solo botón de envío
    submit_button = st.form_submit_button(label="Entrar")
    #st.markdown("[Don't have an account? Sign up here!](http://localhost:8501/signup)", unsafe_allow_html=True)


if submit_button:
    st.success("Inicio de sesión correcto.")

