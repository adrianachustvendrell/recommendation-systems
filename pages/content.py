import pandas as pd
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
# Alcances requeridos
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

@st.cache_resource
def get_client():
    # Usar las credenciales directamente desde st.secrets
    creds = Credentials.from_service_account_info(st.secrets["google"], scopes=scope)
    return gspread.authorize(creds)



client = get_client()

BASE_HOJA = "puntuaciones_usuario_base"
USUARIOS_HOJA = "info_usuarios"
PREFS_HOJA = "prefs_usuarios"

def load_google_sheets():
    usuarios_sheet = client.open("info_usuarios").sheet1
    prefs_sheet = client.open("prefs_usuarios").sheet1
    base_sheet = client.open("puntuaciones_usuario_base").sheet1
    return usuarios_sheet, prefs_sheet, base_sheet

usuarios_sheet, prefs_sheet, base_sheet = load_google_sheets()

items = pd.read_csv("data/items.csv")
usuarios = pd.DataFrame(usuarios_sheet.get_all_records())
puntuaciones_usuario = pd.DataFrame(base_sheet.get_all_records())
preferencias_usuario = pd.DataFrame(prefs_sheet.get_all_records())

def reserva(n, excluidos):
    """
    Selecciona los mejores N ítems únicos basados en la ponderación del ratio (0.4) y el count (0.6),
    evitando los ítems ya recomendados y garantizando que no haya elementos repetidos.
    """
    best_scores = (puntuaciones_usuario.groupby("id_item")["ratio"].mean() * 0.4 + 
                   items.set_index("id_item")["count"] * 0.6)
    best_scores = best_scores[~best_scores.index.isin(excluidos)]
    sorted_items = best_scores.sort_values(ascending=False).index.tolist()
    mejores_items = list(dict.fromkeys(sorted_items))[:n]
    return mejores_items


def calcular_score(adec, pref, count):
    """
    Calcula el score en un rango de 0 a 100 considerando:
    - adec (adecuación del ítem a la categoría, de 0 a 100)
    - pref (preferencia del usuario por la categoría, de 0 a 100, con más peso que adec)
    - count (número de visitas, sumado directamente)
    """
    score = (0.4 * adec + 0.6 * pref + count)  # Más peso a pref, se suma count
    score_normalizado = (score / (100 + max(count, 1))) * 100  # Normalización a [0,100]
    return min(max(score_normalizado, 0), 100)



items = pd.read_csv("data/items.csv")


def contenido_recomendacion(usuario):
    """
    Este método recomienda ítems basándose únicamente en la afinidad entre los ítems y las categorías 
    que le gustan al usuario. Excluye ítems que ya han sido vistos por el usuario.
    """

    usuario_data = usuarios.loc[usuarios['nombre_usuario'] == usuario]

    if usuario_data.empty:
        return f"Usuario con nombre {usuario} no encontrado."

    id_usuario = int(usuario_data['id_usuario'].iloc[0])
    calificaciones = preferencias_usuario[preferencias_usuario['id_usuario'] == id_usuario]

    if calificaciones.empty:
        return f"El usuario {usuario} no tiene preferencias de categorías."

    categorias_usuario = calificaciones[['id_usuario', 'id_categoria', 'calificacion', 'categoria']].drop_duplicates()

    threshold = categorias_usuario['calificacion'].mean()
    categorias_usuario = categorias_usuario[categorias_usuario['calificacion'] >= threshold]
    categorias_usuario = categorias_usuario.set_index('categoria')

    items_filtrados = items[items['categoria'].isin(categorias_usuario.index)]

    vistos = puntuaciones_usuario[puntuaciones_usuario['id_usuario'] == id_usuario]['id_item'].unique()
    items_filtrados = items_filtrados[~items_filtrados['id_item'].isin(vistos)]

    recomendaciones = {}

    for _, item in items_filtrados.iterrows():
        categoria_item = item['categoria']
        adec = item['adec']
        count = item['count']
        
        if categoria_item in categorias_usuario.index:
            pref = categorias_usuario.loc[categoria_item, 'calificacion']
            score = calcular_score(adec, pref, count)            
            id_item = item['id_item']

            if id_item not in recomendaciones:
                recomendaciones[id_item] = score
            else:
                recomendaciones[id_item] = max(recomendaciones[id_item], score)

    if not recomendaciones:
        return "No hay recomendaciones disponibles para este usuario."

    recomendaciones_ordenadas = sorted(recomendaciones.items(), key=lambda x: x[1], reverse=True)
    recomendaciones_diversas = {}
    categories_added = set() 

    for id_item, score in recomendaciones_ordenadas:
        item = items[items['id_item'] == id_item].iloc[0]
        padre_categoria = item['padre_categoria']
        
        if padre_categoria not in categories_added:
            recomendaciones_diversas[id_item] = score
            categories_added.add(padre_categoria)

        if len(recomendaciones_diversas) == 3:
            break

    if len(recomendaciones_diversas) < 3:
        for id_item, score in recomendaciones_ordenadas:
            if id_item not in recomendaciones_diversas:
                recomendaciones_diversas[id_item] = score
            if len(recomendaciones_diversas) == 3:
                break

    percentil_40 = np.percentile(list(recomendaciones.values()), 40)
    candidatos_bajo_percentil = [k for k, v in recomendaciones_ordenadas if v <= percentil_40]
    puntuaciones_relevantes = puntuaciones_usuario[puntuaciones_usuario["id_item"].isin(candidatos_bajo_percentil)]
    ratio_promedios = puntuaciones_relevantes.groupby("id_item")["ratio"].mean()
    candidatos_sorpresa = ratio_promedios.nlargest(2).index.tolist()
    candidatos_sorpresa = [(item, recomendaciones[item]) for item in candidatos_sorpresa]
    seleccionadas = list(recomendaciones_diversas.items()) + candidatos_sorpresa
    recomendaciones_finales = {k: v for k, v in seleccionadas}

    # ÍTEMS RESERVA
    if len(recomendaciones_finales) < 5:
        n = 5 - len(recomendaciones_finales)
        excluidos = set(recomendaciones_finales.keys())
        items_reserva = reserva(n, excluidos)
        for item in items_reserva:
            recomendaciones_finales[item] = 1

    # Cálculo del rating basado en la media de todas las puntuaciones de todos los usuarios para cada ítem
    puntuaciones_relevantes = puntuaciones_usuario[puntuaciones_usuario["id_item"].isin(recomendaciones_finales.keys())]

    ratings = {}
    for id_item in recomendaciones_finales.keys():
        item_puntuaciones = puntuaciones_relevantes[puntuaciones_relevantes["id_item"] == id_item]
        if not item_puntuaciones.empty:
            puntuacion = np.round(item_puntuaciones["ratio"].mean() / 20, 1)
            if puntuacion > 0:
                ratings[id_item] = puntuacion
            else:
                ratings[id_item] = 0
        else:
            ratings[id_item] = 0

    return recomendaciones_finales, ratings
