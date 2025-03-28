import pandas as pd
import numpy as np

items = pd.read_csv("data/items.csv")
usuarios = pd.read_csv("data/info_usuarios.csv")
puntuaciones_usuario = pd.read_csv("data/puntuaciones_usuario_base.csv")
preferencias_usuario = pd.read_csv("data/prefs_usuarios.csv")

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
            score = (adec / 100) * (pref / 100)
            score *= (1 + np.log(16 + count))
            score = np.round(score, 2)
            
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
