import pandas as pd
import numpy as np
import ast

items = pd.read_csv("data/items.csv")
usuarios = pd.read_csv("data/info_usuarios.csv")
puntuaciones_usuario = pd.read_csv("data/puntuaciones_usuario_base.csv")
preferencias_usuario = pd.read_csv("data/prefs_usuarios.csv")


def reserva(n, excluidos):
    """
    Selecciona los mejores ítems basados en la ponderación del ratio (0.4) y el count (0.6),
    evitando los ítems ya recomendados.
    """
    best_scores = puntuaciones_usuario.groupby("id_item")["ratio"].mean() * 0.4 + items.set_index("id_item")["count"] * 0.6
    best_scores = best_scores[~best_scores.index.isin(excluidos)]
    mejores_items = best_scores.nlargest(n).index.tolist()
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



def colaborativa_recomendacion(usuario):
    """
    Este método recomienda ítems basándose en las puntuaciones de los vecinos del usuario
    y su similitud con él. Excluye ítems que ya han sido vistos por el usuario.
    
    Parámetros:
    - usuario: nombre del usuario
    - vecinos: diccionario con id_usuario vecino como clave y score de similitud como valor
    """

    usuario_data = usuarios.loc[usuarios['nombre_usuario'] == usuario]
    if usuario_data.empty:
        return f"Usuario con nombre {usuario} no encontrado."
    
    # Tomar los vecinos
    vecinos_str = usuario_data['vecinos'].iloc[0]
    vecinos_raw = ast.literal_eval(vecinos_str)
    vecinos = {int(k): v for k, v in vecinos_raw.items()}

    id_usuario = int(usuario_data['id_usuario'].iloc[0])
    vistos = set(puntuaciones_usuario[puntuaciones_usuario['id_usuario'] == id_usuario]['id_item'])

    recomendaciones = {}

    for id_vecino, similitud in vecinos.items():
        puntuaciones_vecino = puntuaciones_usuario[puntuaciones_usuario['id_usuario'] == id_vecino]
        for _, fila in puntuaciones_vecino.iterrows():
            id_item = fila['id_item']
            ratio = fila['ratio']

            if id_item not in vistos:
                if id_item not in recomendaciones:
                    recomendaciones[id_item] = 0
                recomendaciones[id_item] += ratio * similitud

    if not recomendaciones:
        return "No hay recomendaciones colaborativas disponibles para este usuario."

    # Normalización entre 1-100
    valores = list(recomendaciones.values())
    min_val, max_val = min(valores), max(valores)
    rango = max_val - min_val if max_val != min_val else 1

    recomendaciones_normalizadas = {
        k: 1 + ((v - min_val) / rango) * 99
        for k, v in recomendaciones.items()
        if v > 0  # Excluir scores igual a 0 antes de normalizar
    }

    if not recomendaciones_normalizadas:
        return "No hay recomendaciones con puntuaciones significativas."

    recomendaciones_ordenadas = sorted(recomendaciones_normalizadas.items(), key=lambda x: x[1], reverse=True)

    # Selección de las top 3 recomendaciones diversas (según padre_categoria)
    recomendaciones_diversas = {}
    categories_added = set()
    for id_item, score in recomendaciones_ordenadas:
        item = items[items['id_item'] == id_item]
        if item.empty:
            continue
        padre_categoria = item['padre_categoria'].iloc[0]
        if padre_categoria not in categories_added:
            recomendaciones_diversas[id_item] = score
            categories_added.add(padre_categoria)

        if len(recomendaciones_diversas) == 3:
            break




    # Candidatos de sorpresa
    percentil_40 = np.percentile(list(recomendaciones.values()), 40)
    candidatos_bajo_percentil = [k for k, v in recomendaciones_ordenadas if v <= percentil_40]
    puntuaciones_relevantes = puntuaciones_usuario[puntuaciones_usuario["id_item"].isin(candidatos_bajo_percentil)]
    ratio_promedios = puntuaciones_relevantes.groupby("id_item")["ratio"].mean()
    candidatos_sorpresa = ratio_promedios.nlargest(2).index.tolist()
    candidatos_sorpresa = [(item, recomendaciones[item]) for item in candidatos_sorpresa if item in recomendaciones]

    seleccionadas = list(recomendaciones_diversas.items()) + candidatos_sorpresa
    recomendaciones_finales = {k: v for k, v in seleccionadas}
    print("LONGITUD RECOMENDACIONES_FINALES", len(recomendaciones_finales))

    # ÍTEMS RESERVA
    if len(recomendaciones_finales) < 5:
        n = 5 - len(recomendaciones_finales)
        excluidos = set(recomendaciones_finales.keys())
        items_reserva = reserva(n, excluidos)
        for item in items_reserva:
            recomendaciones_finales[item] = 1


    # Calcular ratings finales para mostrar
    puntuaciones_relevantes = puntuaciones_usuario[puntuaciones_usuario["id_item"].isin(recomendaciones_finales.keys())]
    ratings = {}
    for id_item in recomendaciones_finales.keys():
        item_puntuaciones = puntuaciones_relevantes[puntuaciones_relevantes["id_item"] == id_item]
        if not item_puntuaciones.empty:
            puntuacion = np.round(item_puntuaciones["ratio"].mean() / 20, 1)
            ratings[id_item] = max(puntuacion, 0)
        else:
            ratings[id_item] = 0
            
    recomendaciones_finales = {int(k): v for k, v in recomendaciones_finales.items()}
    ratings = {int(k): v for k, v in ratings.items()}
    
    return recomendaciones_finales, ratings