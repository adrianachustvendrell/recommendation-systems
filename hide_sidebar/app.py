import streamlit as st
from streamlit_carousel import carousel
import os
import random

# Sidebar navigation
st.set_page_config(page_title="ValenciaGO", page_icon="🚀", layout="centered")
st.sidebar.page_link('app.py', label='Home')

col1, col_space, col2 = st.columns([1, 3, 1])
with col1:
    if st.button("Iniciar sesión"):
        st.switch_page("pages/signin.py")  # Redirect to login page

with col2:
    if st.button("Registrarse"):
        st.switch_page("pages/signup.py")  # Redirect to signup page

st.title("ValenciaGO")

# ✅ Dynamically locate the "images" folder
def find_images_folder(folder_name="images"):
    """Search for the images folder dynamically."""
    for root, dirs, _ in os.walk(os.getcwd()):  # Start searching from current directory
        if folder_name in dirs:
            return os.path.join(root, folder_name)
    return None  # Return None if the folder is not found

# Find the images folder
image_folder = find_images_folder()

if image_folder:
    # ✅ Get image files dynamically
    image_files = [f for f in os.listdir(image_folder) if f.endswith((".png", ".jpg", ".jpeg"))]

    if image_files:
        random_images = random.sample(image_files, min(10, len(image_files)))  # Get up to 10 random images

        # ✅ Prepare carousel items
        carousel_items = []
        for image in random_images:
            item = dict(
                title="",
                text="",
                img=os.path.join(image_folder, image),
            )
            carousel_items.append(item)

        # ✅ Display carousel
        carousel(items=carousel_items)
    else:
        st.warning("No hay imágenes disponibles en la carpeta.")
else:
    st.error("No se encontró la carpeta de imágenes.")
