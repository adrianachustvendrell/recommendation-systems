import streamlit as st
from streamlit_carousel import carousel
import os
import random


# Sidebar navigation

st.set_page_config(page_title="ValenciaGO", page_icon="🚀", layout="centered")
st.sidebar.page_link('app.py', label='Home')


#st.write("Sign up to get started!")

col1, col_space, col2 = st.columns([1, 3, 1])
with col1:
    if st.button("Iniciar sesión"):
        st.switch_page("pages/signin.py")  # Redirige a la página de inicio de sesión

with col2:
    if st.button("Registrarse"):
        st.switch_page("pages/signup.py")  # Redirige a la página de registros
    


st.title("ValenciaGO")


#https://medium.com/@vidyutrc/making-a-sliding-carousel-with-streamlit-7704b50a760f
image_folder = "../images"
image_files = [f for f in os.listdir(image_folder) if f.endswith((".png", ".jpg", ".jpeg"))]
random_images = random.sample(image_files, min(10, len(image_files)))  # Obtener hasta 10 imágenes aleatorias

# Crear una lista de diccionarios con las imágenes aleatorias
carousel_items = []
for image in random_images:
    item = dict(
        title=f"",
        text=f"",
        img=os.path.join(image_folder, image),
    )
    carousel_items.append(item)

# Mostrar el carrusel con las imágenes aleatorias
carousel(items=carousel_items)



