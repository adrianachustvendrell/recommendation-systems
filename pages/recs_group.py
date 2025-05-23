import pandas as pd
import numpy as np
import ast

items = pd.read_csv("data/items.csv")
usuarios = pd.read_csv("data/info_usuarios.csv")
puntuaciones_usuario = pd.read_csv("data/puntuaciones_usuario_base.csv")
preferencias_usuario = pd.read_csv("data/prefs_usuarios.csv")

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


viajeros = {
    "tipo1": {  # Viajero promedio (disfrute)
        "Parques": 90, "Playas": 80, "Calles y plazas": 100, "Paseos": 100, "Parques temáticos": 90, 
        "Cines": 90, "Conciertos y música en vivo": 50, "Restaurantes": 100, "Eventos": 70, 
        "Tiendas tradicionales": 60, "Grandes eventos (exposiciones)": 70, "Eventos deportivos": 80, 
        "Arte": 70, "Ciencia y tecnología": 60, "Historia": 50, "Religión": 60, "Ciencias naturales": 70, 
        "Arqueologia": 30, "Historia y cultura local": 80, "Centro histórico": 100, "Mercados": 100, 
        "Puentes": 80, "Estadios y áreas deportivas": 90, "Fuentes": 90
    },
    "tipo2": {  # Viajero de borrachera y adultos con crisis de los 40
        "Playas": 70, "Parques temáticos": 30, "Conciertos y música en vivo": 80, "Clubs y discotecas": 100, 
        "Bares y pubs": 100, "Eventos": 80, "Fiestas": 100, "Eventos deportivos": 30, 
        "Otros ocio": 40, "Otros eventos": 20
    },
    "tipo3": {  # Viajero joven con cultura
        "Museos": 95, "Arquitectura religiosa": 80, "Arquitectura civil": 85, "Centro histórico": 85, 
        "Mercados": 75, "Edificios académicos": 95, "Monumentos": 80, "Esculturas": 90, 
        "Historia y cultura local": 90, "Arqueología": 85, "Patrimonio de la Humanidad": 95, 
        "Arte": 95, "Música clásica": 85, "Ópera": 90, "Paseos": 85, "Restaurantes": 90, 
        "Otros gastronomía": 80, "Estilos y periodos": 80, "Exposiciones": 85, "Conferencias": 90, 
        "Congresos": 90, "Grandes eventos (exposiciones)": 85, "Ciencia y tecnología": 90, 
        "Historia": 90, "Religión": 75, "Ciencias naturales": 85, "Artesanía": 80, "Militar": 70, 
        "Otros museos": 85, "Teatros": 90
    },
    "tipo4": {  # Jubilado
        "Museos": 90, "Arquitectura religiosa": 85, "Cementerios": 85, "Arquitectura civil": 80, 
        "Centro histórico": 85, "Mercados": 90, "Edificios gubernamentales": 80, "Otros edificios públicos": 80, 
        "Otros edificios emblemáticos": 80, "Monumentos": 80, "Historia y cultura local": 90, 
        "Patrimonio de la Humanidad": 95, "Música clásica": 80, "Ópera": 80, "Jardines botánicos": 75, 
        "Calles y plazas": 85, "Paseos": 85, "Otros espacios abiertos": 75, "Restaurantes": 65, 
        "Centros de salud y spa": 80
    },
    "tipo5": {  # Viajero con niños pequeños
        "Parques": 90, "Jardines botánicos": 80, "Parque infantil": 100, "Playas": 80, "Lagos": 40, 
        "Paseos": 90, "Parques temáticos": 60, "Ciencias naturales": 30, "Castillos": 50, 
        "Torres": 40, "Murallas": 50, "Puertas": 50, "Otras arquitecturas defensivas": 30, 
        "Otros espacios abiertos": 90
    },
    "tipo6": {  # Militar
        "Historia y cultura local": 40, "Historia": 80, "Edificios gubernamentales": 60, "Militar": 100, 
        "Castillos": 70, "Torres": 50, "Murallas": 60, "Puertas": 40, "Otras arquitecturas defensivas": 30, 
        "Otros monumentos": 50, "Criptas": 40, "Esculturas": 20, "Árabe": 50, "Arqueologia": 60, 
        "Catedrales": 80, "Iglesias": 75, "Monasterios": 65, "Conferencias": 40, "Romano": 70
    }
}


puntuaciones_usuario = pd.read_csv("data/puntuaciones_usuario_base.csv")


def demografico(usuario):
    usuario_data = usuarios.loc[usuarios['nombre_usuario'] == usuario]
    if usuario_data.empty:
        return f"Usuario con nombre {usuario} no encontrado."

    id_usuario = int(usuario_data['id_usuario'].iloc[0])
    tipo_usuario = usuario_data['tipos_usuario'].iloc[0]
    preferencias = viajeros.get(tipo_usuario, {})

    if not preferencias:
        return f"No hay preferencias definidas para el tipo de usuario {tipo_usuario}."

    threshold = np.mean(list(preferencias.values()))
    categorias_filtradas = {k: v for k, v in preferencias.items() if v >= threshold}
    items_filtrados = items[items['categoria'].isin(categorias_filtradas.keys())]

    vistos = puntuaciones_usuario[puntuaciones_usuario['id_usuario'] == id_usuario]['id_item'].unique()
    items_filtrados = items_filtrados[~items_filtrados['id_item'].isin(vistos)]
    
    recomendaciones = {}
    for _, item in items_filtrados.iterrows():
        categoria_item = item['categoria']
        adec = item['adec']
        pref = categorias_filtradas.get(categoria_item, 0)
        count = item['count']
        
        score = calcular_score(adec, pref, count)
        id_item = item['id_item']

        if id_item not in recomendaciones:
            recomendaciones[id_item] = score
        else:
            recomendaciones[id_item] = max(recomendaciones[id_item], score)
    

    if len(recomendaciones) < 5:
        n = 5 - len(recomendaciones)
        excluidos = set(recomendaciones.keys())
        items_reserva = reserva(n, excluidos)
        for item in items_reserva:
            recomendaciones[item] = 1

    if not recomendaciones:
        return "No hay recomendaciones disponibles para este usuario."
    
    recomendaciones_ordenadas = sorted(recomendaciones.items(), key=lambda x: x[1], reverse=True)
    puntuaciones_relevantes = puntuaciones_usuario[puntuaciones_usuario["id_item"].isin(recomendaciones.keys())]

    # Diccionario con los ratings en escala de 0 a 5
    ratings = {}
    if not puntuaciones_relevantes.empty:
        for id_item in recomendaciones_ordenadas[0]:
            item_puntuaciones = puntuaciones_relevantes[puntuaciones_relevantes["id_item"] == id_item]
            if not item_puntuaciones.empty:
                puntuacion = np.round(item_puntuaciones["ratio"].mean() / 20, 1)
                if puntuacion > 0:
                    ratings[id_item] = puntuacion
                else:
                    ratings[id_item] = 0
            else:
                ratings[id_item] = 0


    print("RATINGS DEMOGRÁFICO", ratings)
    return dict(recomendaciones_ordenadas), ratings



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


    if len(recomendaciones) < 5:
        n = 5 - len(recomendaciones)
        excluidos = set(recomendaciones.keys())
        items_reserva = reserva(n, excluidos)
        for item in items_reserva:
            recomendaciones[item] = 1
            
    if not recomendaciones:
        return "No hay recomendaciones disponibles para este usuario."

    recomendaciones_ordenadas = sorted(recomendaciones.items(), key=lambda x: x[1], reverse=True)
    puntuaciones_relevantes = puntuaciones_usuario[puntuaciones_usuario["id_item"].isin(recomendaciones.keys())]

    # Diccionario con los ratings en escala de 0 a 5
    ratings = {}
    if not puntuaciones_relevantes.empty:
        for id_item in recomendaciones_ordenadas[0]:
            item_puntuaciones = puntuaciones_relevantes[puntuaciones_relevantes["id_item"] == id_item]
            if not item_puntuaciones.empty:
                puntuacion = np.round(item_puntuaciones["ratio"].mean() / 20, 1)
                print(puntuacion)
                if puntuacion > 0:
                    ratings[id_item] = puntuacion
                else:
                    ratings[id_item] = 0
            else:
                ratings[id_item] = 0
    
    print("RATINGS CONTENIDO", ratings)
    return dict(recomendaciones_ordenadas), ratings



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


    if len(recomendaciones) < 5:
        n = 5 - len(recomendaciones)
        excluidos = set(recomendaciones.keys())
        items_reserva = reserva(n, excluidos)
        for item in items_reserva:
            recomendaciones[item] = 1


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
    puntuaciones_relevantes = puntuaciones_usuario[puntuaciones_usuario["id_item"].isin(recomendaciones.keys())]

    # Diccionario con los ratings en escala de 0 a 5
    ratings = {}
    if not puntuaciones_relevantes.empty:
        for id_item in recomendaciones_ordenadas[0]:
            item_puntuaciones = puntuaciones_relevantes[puntuaciones_relevantes["id_item"] == id_item]
            if not item_puntuaciones.empty:
                puntuacion = np.round(item_puntuaciones["ratio"].mean() / 20, 1)
                if puntuacion > 0:
                    ratings[id_item] = puntuacion
                else:
                    ratings[id_item] = 0
            else:
                ratings[id_item] = 0

    print("RATINGS COLABORATIVO", ratings)
    return dict(recomendaciones_ordenadas), ratings