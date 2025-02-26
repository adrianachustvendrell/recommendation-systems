import streamlit as st

st.set_page_config(page_title="Welcome", page_icon="🚀", layout="centered")

st.title("Welcome to My App")
st.write("Sign up to get started!")

if st.button("Sign Up"):
    st.switch_page("pages/signup.py")  # Redirige a la página de registro

if st.button("Sign In"):
    st.switch_page("pages/signin.py")  # Redirige a la página de registro
