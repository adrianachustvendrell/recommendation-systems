import streamlit as st
import os
from PIL import Image
import pandas as pd
from streamlit_folium import folium_static
import folium
from streamlit_javascript import st_javascript
import numpy as np
from pages.recs_group import demografico
from pages.content import contenido_recomendacion
from pages.collaborative import colaborativa_recomendacion



# --------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# --------------------------------------

st.set_page_config(page_title="Descubre Valencia", page_icon="🚀", layout="wide")
st.cache_data.clear()

# Inject JavaScript to get page width
page_width = st_javascript("window.innerWidth")


if "grupo_registrado" not in st.session_state:
    st.session_state.grupo_registrado = False

if 'ids_grupo' not in st.session_state:
    st.session_state.ids_grupo = []


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

if st.button("🏠 Home"):
    st.switch_page("app.py")

if "grupo_registrado" not in st.session_state:
    st.warning("⚠️ No has iniciado sesión. Redirigiendo a la página de inicio de sesión...")
    st.switch_page("pages/signin.py") 

else:
    st.title(f"👋 Bienvenido, grupo.")




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
    st.markdown("### Esta es la recomendación que hemos preparado para tu grupo")
    
    # Tres imágenes arriba (i <= 2 muestra las tres primeras)
    cols = st.columns(3)
    top_items = list(diccionario.items())[:3]
    for i, (id_item, score) in enumerate(top_items):
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
                    #st.markdown(f'<div class="score-matching">{np.round(score, 2)}% coincidencia para tu grupo</div>', unsafe_allow_html=True)

                    if rating[item_id] > 0:
                        st.markdown(f"Otros usuarios han puntuado: {rating[item_id]}/5⭐")
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


    st.markdown("### También podría interesaros...")

    # Dos imágenes grandes debajo (i > 2 para las siguientes imágenes)
    cols = st.columns(2)
    bottom_items = list(diccionario.items())[3:5]
    for i, (id_item, score) in enumerate(bottom_items, start=3):
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
                        st.markdown(f"Otros usuarios han puntuado: {rating[item_id]}/5⭐")
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


# -------------------------------------------------
# Funciones auxiliares para ponderar recomendadores
# -------------------------------------------------

from collections import defaultdict

def res_ponderado_por_rec(group_ids_list, rec):
    res = []
    if rec == 'Demográfico':
        for user_id in group_ids_list:
            d1, r1 = demografico(user_id)
            res.append((d1, r1))
    elif rec == 'Basado en contenido':
        for user_id in group_ids_list:
            d2, r2 = contenido_recomendacion(user_id)
            res.append((d2, r2))
    else:
        for user_id in group_ids_list:
            d3, r3 = colaborativa_recomendacion(user_id)
            res.append((d3, r3))
    return res


def borda_count_from_res(res, top_k=10):
    scores = defaultdict(int)
    ratings = {}

    for diccionario, rating_dict in res:
        items_ordenados = sorted(diccionario.items(), key=lambda x: x[1], reverse=True)
        n = len(items_ordenados)
        for rank, (item, _) in enumerate(items_ordenados):
            scores[item] += n - rank
            if item not in ratings:
                ratings[item] = rating_dict.get(item, 0)

    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_items_dict = dict(sorted_items[:top_k])
    return top_items_dict, ratings


def mezclar_diccionarios(dic1, dic2, alpha, beta):
    resultado = defaultdict(float)
    for k, v in dic1.items():
        resultado[k] += alpha * v
    for k, v in dic2.items():
        resultado[k] += beta * v
    # Ordenar por valor descendente
    resultado_ordenado = dict(sorted(resultado.items(), key=lambda x: x[1], reverse=True))
    return resultado_ordenado


def mezclar_tres_diccionarios(dic1, dic2, dic3, alpha, beta, gamma):
    resultado = defaultdict(float)
    for k, v in dic1.items():
        resultado[k] += alpha * v
    for k, v in dic2.items():
        resultado[k] += beta * v
    for k, v in dic3.items():
        resultado[k] += gamma * v
    # Ordenar por valor descendente
    resultado_ordenado = dict(sorted(resultado.items(), key=lambda x: x[1], reverse=True))
    return resultado_ordenado


def combinar_ratings(*ratings_dicts):
    resultado = {}
    for d in ratings_dicts:
        resultado.update(d)
    return resultado


def obtener_items_seleccionados(selection, group_ids):
    if len(selection) == 1:
        res = res_ponderado_por_rec(group_ids, selection[0])
        diccionario, rating = borda_count_from_res(res)
        print("SELECTION", selection)
        print("res", res)
        print("diccionario", diccionario)
        print('\n')


    elif len(selection) == 2:
        rec1, rec2 = selection
        res1 = res_ponderado_por_rec(group_ids, rec1)
        res2 = res_ponderado_por_rec(group_ids, rec2)

        dic1, rating1 = borda_count_from_res(res1)
        dic2, rating2 = borda_count_from_res(res2)

        # Asignar pesos
        pesos = {
            ("Demográfico", "Basado en contenido"): (0.4, 0.6),
            ("Demográfico", "Colaborativo"): (0.35, 0.65),
            ("Basado en contenido", "Colaborativo"): (0.45, 0.55)
        }
        clave = tuple(sorted([rec1, rec2]))
        alpha, beta = pesos.get(clave, (0.5, 0.5))

        diccionario = mezclar_diccionarios(dic1, dic2, alpha, beta)
        rating = combinar_ratings(rating1, rating2)


    else:
        res1 = res_ponderado_por_rec(group_ids, "Demográfico")
        res2 = res_ponderado_por_rec(group_ids, "Basado en contenido")
        res3 = res_ponderado_por_rec(group_ids, "Colaborativo")

        dic1, rating1 = borda_count_from_res(res1)
        dic2, rating2 = borda_count_from_res(res2)
        dic3, rating3 = borda_count_from_res(res3)

        alpha, beta, gamma = 0.25, 0.35, 0.4
        diccionario = mezclar_tres_diccionarios(dic1, dic2, dic3, alpha, beta, gamma)
        rating = combinar_ratings(rating1, rating2, rating3)

    mostrar_items(diccionario, rating)
    return diccionario, rating




# -------------------------------------------
# SELECCIÓN DE RECOMENDADOR (PÁGINA PRINCIPAL)
# -------------------------------------------

# Opciones de selección
options = ["Demográfico", "Basado en contenido", "Colaborativo"]
selection = st.pills("Selecciona el sistema recomendador", options, selection_mode="multi", default=["Demográfico"])

ids_grupo = st.session_state.ids_grupo

obtener_items_seleccionados(selection, ids_grupo)



