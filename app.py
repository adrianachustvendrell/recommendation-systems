import streamlit as st
from streamlit_carousel import carousel
import os
import random
import pandas as pd
import plotly.express as px
from streamlit_folium import folium_static
import folium
from folium.plugins import TagFilterButton

# Sidebar navigation
st.set_page_config(page_title="Descubre Valencia", page_icon="🚀", layout="wide")
st.sidebar.page_link('app.py', label='🏠 Home')

# -----------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -----------------------------------

# FONTS: 
custom_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Text:ital@0;1&family=Megrim&display=swap');
        html, body, [class*="st-"] {
            font-family: "DM Serif Text", serif;
            font-weight: 400;
            font-style: normal;
        }

        /* Carousel image styling */
        .carousel img {
            height: 400px;  /* Define a fixed height for images */
            object-fit: contain;  /* This ensures the image is adjusted to fit without being cropped */
            width: auto;  /* Maintain aspect ratio */
            display: block;
            margin: 0 auto;  /* Center the images */
        }

        /* Ensure that when the sidebar is hidden, the image height stays fixed */
        .css-1v3fvcr {
            width: 100% !important;  /* Ensures that the container for the carousel is full width */
        }
        
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# Load data
items_file_path = "./data/items.csv"  # Change this to your actual CSV path
df_items = pd.read_csv(items_file_path)

# -----------------------------------
# BOTONES (FALTA AÑADIR GRUPO)
# -----------------------------------

# --- HEADER SECTION ---
col1, col_space, col2, col_space, col3 = st.columns([1, 1.5, 1, 1.5, 1])

with col1:
    if st.button("🔑 Iniciar sesión"):
        st.switch_page("pages/signin.py")

with col2:
    if st.button("👥 Soy un grupo"):
        st.switch_page("pages/group.py")

with col3:
    if st.button("📝 Registrarse"):
        st.switch_page("pages/signup.py")

# -----------------------------------
# TÍTULO Y CAROUSEL DE FOTOS
# -----------------------------------

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Dancing+Script&family=Playfair+Display&display=swap');
    </style>
    <h1 style='text-align: center; color: #F63366; font-family: Playfair Display, serif; font-size: 46px'>
        Descubre lo mejor de 
        <span style="font-family: 'Dancing Script', cursive; color: #F63366; font-size: 60px;">Valencia</span>
    </h1>
    """, 
    unsafe_allow_html=True)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display&display=swap');
    </style>
    <h5 style='text-align: center; color: #000010; font-family: Playfair Display, serif;'>Explora los lugares más emblemáticos</h5>
    """, 
    unsafe_allow_html=True)

# --- IMAGE CAROUSEL ---
image_folder = "./images"
image_files = [f for f in os.listdir(image_folder) if f.endswith((".png", ".jpg", ".jpeg"))]
random_images = random.sample(image_files, min(10, len(image_files)))  

carousel_items = [{"title": "", "text": "", "img": os.path.join(image_folder, img)} for img in random_images]

# Centering the carousel text
st.write("")
carousel(items=carousel_items)

# ---------------------------------
# ESTADÍSTICAS 
# ---------------------------------
st.markdown("### 📊 **Análisis de Visitantes**")
padre_categorias = list(set(df_items['padre_categoria'].tolist()))
padre = st.selectbox("📌 **Selecciona un tipo de lugar:**", padre_categorias)
df_filtered = df_items[df_items["padre_categoria"] == padre]
category_visits = df_filtered.groupby("categoria")["count"].sum().reset_index()

# Filtrar solo categorías con count > 1
category_visits = category_visits[category_visits["count"] > 1]
if not category_visits.empty:
    fig1 = px.bar(category_visits, x="categoria", y="count", 
                  labels={"categoria": "Categoría", "count": "Número de visitas"}, 
                  title="", color="categoria")
    st.plotly_chart(fig1, use_container_width=True)
else:
    st.info("No hay suficientes datos para mostrar el gráfico.")

st.divider()

st.write("### 🔍 **Búsqueda de Lugares Turísticos**")

category_colors = {
    "Museos": "blue",
    "Estilos y periodos": "green",
    "Eventos": "red",
    "Arquitectura civil": "purple",
    "Deportes": "orange",
    "Ocio": "pink",
    "Compras": "cadetblue",
    "Arquitectura religiosa": "darkblue",
    "Espacios Abiertos": "darkgreen",
    "Monumentos": "darkred",
    "Arquitectura defensiva": "lightgray",
    "Gastronomia": "beige"
}

#df_unique = df_items.drop_duplicates(subset=["id_item", "latitud", "longitud"])
df_unique = df_items
map_center = [df_unique["latitud"].mean(), df_unique["longitud"].mean()]
folium_map = folium.Map(location=map_center, zoom_start=12, tiles="cartodb positron")

# Add markers to the map with category tags
for _, row in df_unique.iterrows():
    color = category_colors.get(row["padre_categoria"], "gray")
    folium.Marker(
        location=[row["latitud"], row["longitud"]],
        popup=row["nombre_item"],
        icon=folium.Icon(color=color, icon="info-sign"),
        tags=[row["padre_categoria"]]  # Adding tags for filtering
    ).add_to(folium_map)

TagFilterButton(list(category_colors.keys())).add_to(folium_map)
folium_static(folium_map, width=1000)
