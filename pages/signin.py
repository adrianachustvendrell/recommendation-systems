# signup.py
import streamlit as st

# Title for the sign-up page
st.title("Sign In")


# Formulario de registro
with st.form(key="signin_form"):
    st.subheader("Log in with your account")

    # Datos básicos
    new_username = st.text_input("Enter your username")
    new_password = st.text_input("Enter your password", type="password")
    # Un solo botón de envío
    submit_button = st.form_submit_button(label="Submit")


if submit_button:
    st.success("Successfully log in.")

