import streamlit as st
from streamlit_carousel import carousel
import os
import random
from PIL import Image

# Sidebar navigation
#st.set_page_config(page_title="ValenciaGO", page_icon="🚀", layout="centered")
#st.sidebar.page_link('app2.py', label='Home')

col1, col_space, col2 = st.columns([1, 3, 1])
with col1:
    if st.button("Iniciar sesión"):
        st.switch_page("pages/signin.py")  # Redirect to login page

with col2:
    if st.button("Registrarse"):
        st.switch_page("pages/signup.py")  # Redirect to signup page

st.title("ValenciaGO")

image_folder = "./images"
image_files = [f for f in os.listdir(image_folder) if f.endswith((".png", ".jpg", ".jpeg"))]
random_images = random.sample(image_files, min(10, len(image_files)))  # Obtener hasta 10 imágenes aleatorias

# Definir el tamaño estándar para todas las imágenes
#image_size = (300, 300)  # Cambia el tamaño según tus necesidades

# Crear una lista de diccionarios con las imágenes redimensionadas
carousel_items = []
for image in random_images:
    # Redimensionar la imagen
    img_path = os.path.join(image_folder, image)
    
    item = dict(
        title=f"",
        text=f"",
        img=img_path,
    )
    carousel_items.append(item)

# Mostrar el carrusel con las imágenes redimensionadas
carousel(items=carousel_items)