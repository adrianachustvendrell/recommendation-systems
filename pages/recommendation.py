import streamlit as st
import os
import random
from PIL import Image
import pandas as pd
from streamlit_folium import folium_static
import folium
import openai  # Necesitas instalar openai con `pip install openai`


# Configurar la página para que ocupe todo el ancho disponible
st.set_page_config(layout='wide')

# Título
st.title("Esta es la recomendación que hemos preparado para ti")

# Opciones de selección
options = ["Demográfico", "Basado en contenido", "SR Colaborativo"]
selection = st.pills("Sistema recomendador", options, selection_mode="multi", default=["Demográfico"])

st.markdown(f"**Opciones seleccionadas:** {', '.join(selection)}")

items = pd.read_csv("data/items.csv")
IMAGE_FOLDER = 'images'

# Función para obtener imágenes aleatorias
def get_random_images(folder, n=2):
    if not os.path.exists(folder):
        st.error(f"La carpeta '{folder}' no existe.")
        return []
    files = [f for f in os.listdir(folder) if f.endswith(('png', 'jpg', 'jpeg'))]
    if len(files) < n:
        st.error(f"No hay suficientes imágenes en la carpeta '{folder}'.")
        return []
    return random.sample(files, n)

# Cargar imágenes en session_state para persistencia
if 'images' not in st.session_state:
    st.session_state.images = get_random_images(IMAGE_FOLDER)

# Estado para mostrar más información
if 'show_info' not in st.session_state:
    st.session_state.show_info = [False] * len(st.session_state.images)

# Mostrar imágenes aleatorias con interacción
images = st.session_state.images
if images:
    cols = st.columns(len(images))
    for i, img_file in enumerate(images):
        img_path = os.path.join(IMAGE_FOLDER, img_file)
        with cols[i]:
            id_item = img_file.split('.')[0]
            item = items[items["id_item"] == int(id_item)]
            item_name = item["nombre_item"].unique()[0]
            image = Image.open(img_path)
            st.image(image, use_container_width=True, caption=f"{item_name}")
            
            if st.button(f"Ver más", key=f"btn_{i}"):
                st.session_state.show_info[i] = not st.session_state.show_info[i]

            if st.session_state.show_info[i]:
                categorias = item['categoria'].tolist()
                padre_categoria = item['padre_categoria'].tolist()
                categorias_info = categorias + padre_categoria
                bullet_list = "\n".join([f"* {categoria}" for categoria in categorias_info])
                

                st.markdown(f"**Categorías:**")
                st.markdown(bullet_list)
                st.markdown(f"**Descripción:**")
                st.markdown(item['descripcion'].iloc[0][3:])

                # Mostrar mapa
                latitud = float(item["latitud"].iloc[0])
                longitud = float(item["longitud"].iloc[0])
                map_center = [latitud, longitud]
                folium_map = folium.Map(location=map_center, zoom_start=12, tiles="cartodb positron")
                folium.Marker(
                    location=[latitud, longitud],
                    popup=item["nombre_item"].iloc[0],
                    icon=folium.Icon(color="#f63366", icon="info-sign")
                ).add_to(folium_map)

                folium_static(folium_map, width=600)


# Estilo adicional para fijar el alto de las imágenes, mejorar la apariencia y modificar el botón
st.markdown(
    """
    <style>
        .stImage img {
            height: 300px !important; /* Altura fija */
            width: auto;
            object-fit: cover; /* Recortar para mantener la relación de aspecto */
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            margin-bottom: 20px; /* Espacio debajo de la imagen */
        }
        .stButton>button {
            background-color: #f63366; /* Rosa-rojo de Streamlit */
            color: white;
            padding: 8px 16px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease;
            margin-top: 8px;
        }
        .stButton>button:hover {
            background-color: white;
            color: #f63366; /* Cambio de color al hacer clic */
        }
    </style>
    """,
    unsafe_allow_html=True
)
