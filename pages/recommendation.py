import streamlit as st
import os
from PIL import Image
import pandas as pd
from streamlit_folium import folium_static
import folium
import importlib

# ---------------------------------
# CARGAR LOS TIPOS DE RECOMENDADORES
# ---------------------------------
from demographic import demografico  


def mostrar_recomendaciones(diccionario_recomendaciones, items, IMAGE_FOLDER='images', page_width=None):
    
    # Mostrar las 3 mejores recomendaciones
    top_3_items = diccionario_recomendaciones[:3]
    st.markdown("### Esta es la recomendación que hemos preparado para ti")
    cols = st.columns(3)
    for i, (id_item, score) in enumerate(top_3_items):
        item = items[items["id_item"] == id_item]
        item_name = item["nombre_item"].unique()[0]
        img_file = f"{id_item}.jpg"  # Suponemos que el archivo de imagen tiene el id_item como nombre
        img_path = os.path.join(IMAGE_FOLDER, img_file)
        image = Image.open(img_path)

        with cols[i]:
            st.image(image, use_container_width=True, caption=f"{item_name}")
            if st.button(f"Ver más", key=f"btn_{i}"):
                st.session_state.show_info[i] = not st.session_state.show_info[i]
            if st.session_state.show_info[i]:
                categorias = item['categoria'].drop_duplicates().tolist()
                padre_categoria = item['padre_categoria'].drop_duplicates().tolist()
                categorias_info = categorias + padre_categoria
                bullet_list = "\n".join([f"* {categoria}" for categoria in categorias_info])

                st.markdown(f"**Descripción:**")
                st.markdown(item['descripcion'].iloc[0][3:])
                st.markdown(f"**Categorías:**")
                st.markdown(bullet_list)

                # Mostrar mapa
                latitud = float(item["latitud"].iloc[0])
                longitud = float(item["longitud"].iloc[0])
                map_center = [latitud, longitud]
                folium_map = folium.Map(location=map_center, zoom_start=13, tiles="cartodb positron")
                folium.Marker(
                    location=[latitud, longitud],
                    popup=item["nombre_item"].iloc[0],
                    icon=folium.Icon(color="#f63366", icon="info-sign")
                ).add_to(folium_map)

                folium_static(folium_map, width=page_width/3, height=400)

    # Mostrar las 2 recomendaciones "sorpresivas" (con los puntajes más bajos)
    surprise_items = diccionario_recomendaciones[-2:]
    st.markdown("### También podría interesarte...")
    cols2 = st.columns(2)
    x = 3  # La posición de la imagen siguiente a la última recomendación mostrada
    for i, (id_item, score) in enumerate(surprise_items):
        item = items[items["id_item"] == id_item]
        item_name = item["nombre_item"].unique()[0]
        img_file = f"{id_item}.jpg"  # Suponemos que el archivo de imagen tiene el id_item como nombre
        img_path = os.path.join(IMAGE_FOLDER, img_file)
        image = Image.open(img_path)

        with cols2[i]:
            st.image(image, use_container_width=True, caption=f"{item_name}")
            if st.button(f"Ver más", key=f"btn_{i+x}"):
                st.session_state.show_info[i+x] = not st.session_state.show_info[i+x]
            if st.session_state.show_info[i+x]:
                categorias = item['categoria'].drop_duplicates().tolist()
                padre_categoria = item['padre_categoria'].drop_duplicates().tolist()
                categorias_info = categorias + padre_categoria
                bullet_list = "\n".join([f"* {categoria}" for categoria in categorias_info])

                st.markdown(f"**Descripción:**")
                st.markdown(item['descripcion'].iloc[0][3:])
                st.markdown(f"**Categorías:**")
                st.markdown(bullet_list)

                # Mostrar mapa
                latitud = float(item["latitud"].iloc[0])
                longitud = float(item["longitud"].iloc[0])
                map_center = [latitud, longitud]
                folium_map = folium.Map(location=map_center, zoom_start=13, tiles="cartodb positron")
                folium.Marker(
                    location=[latitud, longitud],
                    popup=item["nombre_item"].iloc[0],
                    icon=folium.Icon(color="#f63366", icon="info-sign")
                ).add_to(folium_map)

                folium_static(folium_map, width=page_width/2, height=400)

# Cargar los items y recomendaciones (función global)
items = pd.read_csv("data/items.csv")

# Configurar la página para que ocupe todo el ancho disponible
st.set_page_config(layout='wide')

# Inyectar JavaScript para obtener el ancho de la página
from streamlit_javascript import st_javascript
page_width = st_javascript("window.innerWidth")

if "user_logged_in" not in st.session_state:
    st.warning("⚠️ No has iniciado sesión. Redirigiendo a la página de inicio de sesión...")
    st.switch_page("pages/signin.py") 

else:
    user_id = st.session_state.user_logged_in  # Retrieve user ID
    st.title(f"👋 Bienvenido, **{user_id}**.")
    options = ["Demográfico", "Basado en contenido", "SR Colaborativo"]
    selection = st.pills("Selecciona el sistema recomendador", options, selection_mode="single", default=["Demográfico"])

    st.markdown(f"**Opciones seleccionadas:** {', '.join(selection)}")

    # Obtener las recomendaciones del sistema seleccionado
    if "Demográfico" in selection:
        recomendaciones = demografico(user_id)  # Llamamos a la función desde el archivo .py

        # Validar que el diccionario de recomendaciones no esté vacío
        if isinstance(recomendaciones, dict):
            # Mostrar las recomendaciones utilizando la función global
            mostrar_recomendaciones(recomendaciones, items, IMAGE_FOLDER='images', page_width=page_width)

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
