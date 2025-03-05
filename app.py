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
st.set_page_config(page_title="ValenciaGO", page_icon="🚀", layout="wide")
st.sidebar.page_link('app.py', label='🏠 Home')


# -----------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# -----------------------------------

# FONTS: 

# <link href="https://fonts.googleapis.com/css2?family=Megrim&display=swap" rel="stylesheet">

custom_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Text:ital@0;1&family=Megrim&display=swap');

        html, body, [class*="st-"] {
            font-family: "DM Serif Text", serif;
            font-weight: 400;
            font-style: normal;
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
#col1, col2, col3 = st.columns([1, 1, 1])

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
        <span style="font-family: 'Dancing Script', cursive; color: #F63366;">Valencia</span>
    </h1>
    """, 
    unsafe_allow_html=True
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display&display=swap');
    </style>
    <h5 style='text-align: center; color: #000010; font-family: Playfair Display, serif;'>Explora los lugares más emblemáticos</h5>
    """, 
    unsafe_allow_html=True
)



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
fig1 = px.bar(category_visits, x="categoria", y="count", 
              labels = {"categoria": "Categoría ", "count": "Número de visistas "}, 
              title="Cantidad de Visitas por Categoría", color="categoria")
st.plotly_chart(fig1, use_container_width=True)



st.write("### 🏛 **Adecuación de lugares por Categoría**")

categorias = list(set(df_items['categoria'].tolist()))
cat = st.selectbox("📌 **Selecciona una categoría:**", categorias)
df_scores = df_items[df_items["categoria"] == cat]
df_scores = df_scores.sort_values(by="adec", ascending=True)
fig_height = 50 + 50 * len(df_scores['adec'].tolist())

# Create a horizontal bar chart
fig = px.bar(
    df_scores,
    x="adec",
    y="nombre_item",
    labels = {"adec": "Adecuación del Lugar ", "nombre_item": "Nombre del item "},
    orientation="h",
    text="adec",
    title="💯 Adecuación de Lugares",
    color="adec",
    color_continuous_scale="BuPu",  # Color gradient
)

fig.update_traces(
    texttemplate='%{text}%', 
    textposition='inside',
    marker=dict(line=dict(width=0.5)),  # Reduce outline thickness
)

fig.update_layout(
    xaxis=dict(title="", range=[0, 100]),  # Fixed range
    yaxis=dict(title="", automargin=True),
    coloraxis_showscale=False,  # Hide color scale legend
    # bargap=0.6,  # Increase gap between bars (smaller bars)
    height=fig_height,
    margin=dict(l=150, r=20, t=50, b=20),
)

# Display the chart
st.plotly_chart(fig, use_container_width=True)




st.write("### 🔍 **Búsqueda de Lugares Turísticos**")

#search_term = st.text_input("🔎 Buscar un lugar por nombre:")
#filtered_df_items = df_items[df_items["nombre_item"].str.contains(search_term, case=False, na=False)] if search_term else df_items
#st.dataframe(filtered_df_items, use_container_width=True)

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
    "Gastronomia": "beige"}

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
folium_static(folium_map)



