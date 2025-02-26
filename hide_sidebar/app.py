import streamlit as st


# Sidebar navigation

st.set_page_config(page_title="ValenciaGO", page_icon="🚀", layout="centered")
st.sidebar.page_link('app.py', label='Home')


#st.write("Sign up to get started!")

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Iniciar sesión"):
        st.switch_page("pages/signin.py")  # Redirige a la página de registro
    
with col2:
    if st.button("Registrarse"):
        st.switch_page("pages/signup.py")  # Redirige a la página de registro
    


st.title("Descubre Valencia")



