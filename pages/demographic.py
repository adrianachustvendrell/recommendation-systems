import pandas as pd
import numpy as np

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



items = pd.read_csv("../data/items.csv")
#print(items.columns)

usuarios = pd.read_csv("../data/info_usuarios.csv")
#print(usuarios.columns)



def demografico(usuario_id):
    # Obtener el tipo de usuario
    usuario = usuarios.loc[usuarios['id_usuario'] == usuario_id]
    if usuario.empty:
        return f"Usuario con id {usuario_id} no encontrado."
    
    tipo_usuario = usuario['tipos_usuario'].iloc[0]
    print(usuario)
    preferencias = viajeros.get(tipo_usuario, {})
    
    if not preferencias:
        return f"No hay preferencias definidas para el tipo de usuario {tipo_usuario}."

    # Filtrar ítems con categorías relevantes para el usuario
    items_filtrados = items[items['categoria'].isin(preferencias.keys())]

    recomendaciones = {}

    for _, item in items_filtrados.iterrows():
        cat = item['categoria']
        adec = item['adec']
        pref = preferencias[cat]
        count = item['count']
        
        # Calcular la puntuación basada en adecuación y preferencia
        score = (adec / 100) * (pref / 100)
        # Ajustar por popularidad
        score *= (1 + np.log(1 + count))
        
        id_item = item['id_item']
        
        if id_item not in recomendaciones or score > recomendaciones[id_item]:
            recomendaciones[id_item] = score

    if not recomendaciones:
        return "No hay recomendaciones disponibles para este usuario."

    recomendaciones = {k:v for k, v in recomendaciones.items()}
    recomendaciones = dict(sorted(recomendaciones.items(), key=lambda x: x[1], reverse=True))
    return recomendaciones


# Ejemplo de uso
recomendaciones = demografico(178)
print(recomendaciones)


