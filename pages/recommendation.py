import streamlit as st
import os
from PIL import Image
import pandas as pd
from streamlit_folium import folium_static
import folium
from streamlit_javascript import st_javascript
import numpy as np
from pages.demographic import demografico
from pages.content import contenido_recomendacion




# --------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# --------------------------------------


st.cache_data.clear()
# Configurar la página para que ocupe todo el ancho disponible
st.set_page_config(layout='wide')

# Inject JavaScript to get page width
page_width = st_javascript("window.innerWidth")


# Estilo adicional para fijar el alto de las imágenes, mejorar la apariencia y modificar el botón
st.markdown(
    """
    <style>
        header.stAppHeader {
        background-color: transparent;
    }
    section.stMain .block-container {
        padding-top: 0rem;
        z-index: 1;
    }
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
            color: #f63366; /* Cambio de color al pasar el ratón */
        }
        .stImage figcaption {
            color: black;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            margin-top: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

if "user_logged_in" not in st.session_state:
    st.warning("⚠️ No has iniciado sesión. Redirigiendo a la página de inicio de sesión...")
    st.switch_page("pages/signin.py") 
else:
    user_id = st.session_state.user_logged_in  # Retrieve user ID
    st.title(f"👋 Bienvenido, **{user_id}**.")






# -------------------------------------------
# FUNCIONES DE ÍTEMS, SCORES...
# -------------------------------------------


def score_to_stars(score):
    """
    Convierte un puntaje entre 0-5 a una calificación de estrellas (de 0 a 5).
    Utiliza estrellas llenas (⭐), vacías (☆), y medias (✩).
    """
    full_stars = int(score) 
    half_star = 1 if (score - full_stars) >= 0.5 else 0  
    empty_stars = 5 - full_stars - half_star 

    return "⭐" * full_stars + ("✩" if half_star else "") + "☆" * empty_stars




def mostrar_items(diccionario, rating):
    items = pd.read_csv("data/items.csv")
    IMAGE_FOLDER = 'images'

    # Initialize show_info in session_state if it doesn't exist
    if "show_info" not in st.session_state:
        st.session_state.show_info = {i: False for i in range(len(diccionario))}  # Default to False for all items

    # Mostrar los 5 ítems
    st.markdown("### Esta es la recomendación que hemos preparado para ti")
    
    # Tres imágenes arriba (i <= 2 muestra las tres primeras)
    cols = st.columns(3)
    for i, (id_item, score) in enumerate(diccionario.items()):
        item = items[items["id_item"] == id_item]
        item_id = item["id_item"].unique()[0]
        if item.empty:
            continue
        
        item_name = item["nombre_item"].unique()[0]
        img_file = f"{id_item}.jpg"
        img_path = os.path.join(IMAGE_FOLDER, img_file)
        
        if os.path.exists(img_path):
            image = Image.open(img_path)
            if i <= 2:  # Mostrar solo las 3 primeras imágenes arriba
                with cols[i % 3]:
                    st.image(image, use_container_width=True, caption=item_name)

                    st.markdown(
                        """
                        <style>
                            .score-matching {
                                background-color: green;
                                color: white;
                                padding: 5px 10px;  /* Ajusta el padding para que sea más pequeño */
                                border-radius: 5px;
                                font-weight: bold;
                                display: inline-block;  /* Hace que el fondo se ajuste al texto */
                                width: auto;  /* El ancho se ajusta al contenido */
                                max-width: 200px;  /* Puedes ajustar el max-width para hacerlo más compacto */
                                text-align: center;  /* Centra el texto dentro del contenedor */
                            }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )

                    # Modificar la sección donde se muestra la coincidencia de puntuación
                    st.markdown(f'<div class="score-matching">{np.round(score, 2)}% coincidencia</div>', unsafe_allow_html=True)

                    if rating[item_id] > 0:
                        st.markdown(f"{rating[item_id]}/5⭐")
                    else:
                        st.markdown(f"¡Sé el primero en calificarlo!")

                    # Botón de "Ver más" para cada imagen
                    button_key = f"btn_{i}"
                    is_info_visible = st.session_state.show_info[i]
                    button_text = "Ver más" if not is_info_visible else "Ver menos"
                    button_style = (
                        "background-color: #888888; color: white;" if is_info_visible else "background-color: white; color: #f63366;"
                    )
                    if st.button(button_text, key=button_key, help="Haga clic para ver más/menos detalles", use_container_width=True, 
                                 on_click=lambda i=i: toggle_info(i)):
                        st.session_state.show_info[i] = not st.session_state.show_info[i]
                    
                    # Mostrar la información adicional cuando el botón ha sido presionado
                    if is_info_visible:
                        # Mostrar la descripción y categorías
                        categorias = item['categoria'].drop_duplicates().tolist()
                        padre_categoria = item['padre_categoria'].drop_duplicates().tolist()
                        categorias_info = categorias + padre_categoria
                        bullet_list = "\n".join([f"* {categoria}" for categoria in categorias_info])
                        
                        st.markdown(f"**Descripción:**")
                        st.markdown(item['descripcion'].iloc[0])
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

                        folium_static(folium_map, width=page_width / 3, height=400)


    st.markdown("### También podría interesarte...")

    # Dos imágenes grandes debajo (i > 2 para las siguientes imágenes)
    cols = st.columns(2)
    for i, (id_item, score) in enumerate(diccionario.items()):
        if i > 2:  # Solo mostrar los siguientes ítems en las imágenes grandes
            item = items[items["id_item"] == id_item]
            item_id = item["id_item"].unique()[0]
            if item.empty:
                continue
            
            item_name = item["nombre_item"].unique()[0]
            img_file = f"{id_item}.jpg"
            img_path = os.path.join(IMAGE_FOLDER, img_file)
            
            if os.path.exists(img_path):
                image = Image.open(img_path)
                with cols[(i-3) % 2]:  # Aquí aseguramos que las imágenes se distribuyan correctamente en las 2 columnas
                    st.image(image, use_container_width=True, caption=item_name)
                    if rating[item_id] > 0:
                        st.markdown(f"{rating[item_id]}/5⭐")
                    else:
                        st.markdown(f"¡Sé el primero en calificarlo!")

                    # Botón de "Ver más" para cada imagen
                    button_key = f"btn_{i+3}"
                    is_info_visible = st.session_state.show_info[i]
                    button_text = "Ver más" if not is_info_visible else "Ver menos"
                    button_style = (
                        "background-color: #888888; color: white;" if is_info_visible else "background-color: white; color: #f63366;"
                    )
                    if st.button(button_text, key=button_key, help="Haga clic para ver más/menos detalles", use_container_width=True, 
                                 on_click=lambda i=i: toggle_info(i)):
                        st.session_state.show_info[i] = not st.session_state.show_info[i]

                    # Mostrar la información adicional cuando el botón ha sido presionado
                    if is_info_visible:
                        # Mostrar la descripción y categorías
                        categorias = item['categoria'].drop_duplicates().tolist()
                        padre_categoria = item['padre_categoria'].drop_duplicates().tolist()
                        categorias_info = categorias + padre_categoria
                        bullet_list = "\n".join([f"* {categoria}" for categoria in categorias_info])
                        
                        st.markdown(f"**Descripción:**")
                        st.markdown(item['descripcion'].iloc[0])
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

                        folium_static(folium_map, width=page_width / 2, height=400)

def toggle_info(i):
    """ Cambia el estado de visibilidad de la información. """
    st.session_state.show_info[i] = not st.session_state.show_info[i]


def obtener_items_seleccionados(seleccion):
    if selection  == "Demográfico":
        diccionario, rating = demografico(user_id)  # Suponiendo que esta función devuelve un diccionario de {id_item: score}
    elif selection  == "Basado en contenido":
        diccionario, rating = contenido_recomendacion(user_id)
    else:
        diccionario = {}
    
    mostrar_items(diccionario, rating)




# -------------------------------------------
# SELECCIÓN DE RECOMENDADOR (PÁGINA PRINCIPAL)
# -------------------------------------------

# Opciones de selección
options = ["Demográfico", "Basado en contenido", "SR Colaborativo"]
selection = st.pills("Selecciona el sistema recomendador", options, selection_mode="single", default=["Demográfico"])

st.markdown(f"Opción seleccionada: {selection}")


if selection:
    obtener_items_seleccionados(selection[0])




