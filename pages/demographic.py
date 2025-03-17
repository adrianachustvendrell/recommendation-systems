import pandas as pd

# TIPO 1 - viajero_disfrute (viajero promedio)
tipo1 = {"Parques": 90, "Playas": 80, "Calles y plazas": 100, "Paseos": 100, "Parques temáticos": 90, "Cines": 90, "Conciertos y música en vivo": 50, "Restaurantes": 100, "Eventos": 70, "Tiendas tradicionales": 60, "Grandes eventos (exposiciones)": 70, "Eventos deportivos": 80, "Arte": 70, "Ciencia y tecnología": 60, "Historia": 50, "Religión": 60, "Ciencias naturales": 70, "Arqueologia": 30, "Historia y cultura local": 80, "Centro histórico": 100, "Mercados": 100, "Puentes": 80, "Estadios y áreas deportivas": 90, "Fuentes": 90}

# TIPO 2 - viajero de borrachera y adultos con crisis de los 40
tipo2 = {"Playas": 70, "Parques temáticos": 30, "Conciertos y música en vivo": 80, "Clubs y discotecas": 100, "Bares y pubs": 100, "Eventos": 80, "Fiestas": 100, "Eventos deportivos": 30, "Otros ocio": 40, "Otros eventos": 20}

# TIPO 3 - viajero joven con cultura
tipo3 = { "Museos": 95, "Arquitectura religiosa": 80, "Arquitectura civil": 85, "Centro histórico": 85, "Mercados": 75, "Edificios académicos": 95, "Monumentos": 80, "Esculturas": 90, "Historia y cultura local": 90, "Arqueología": 85, "Patrimonio de la Humanidad": 95, "Arte": 95, "Música clásica": 85, "Ópera": 90, "Paseos": 85, "Restaurantes": 90, "Otros gastronomía": 80, "Estilos y periodos": 80, "Exposiciones": 85, "Conferencias": 90, "Congresos": 90, "Grandes eventos (exposiciones)": 85, "Ciencia y tecnología": 90, "Historia": 90, "Religión": 75, "Ciencias naturales": 85, "Artesanía": 80, "Militar": 70, "Otros museos": 85, "Teatros": 90}
 
# TIPO 4 - jubilado
tipo4 = { "Museos": 90, "Arquitectura religiosa": 85, "Cementerios": 85, "Arquitectura civil": 80, "Centro histórico": 85, "Mercados": 90, "Edificios gubernamentales": 80, "Otros edificios públicos": 80, "Otros edificios emblemáticos": 80, "Monumentos": 80, "Historia y cultura local": 90, "Patrimonio de la Humanidad": 95, "Música clásica": 80, "Ópera": 80, "Jardines botánicos": 75, "Calles y plazas": 85, "Paseos": 85, "Otros espacios abiertos": 75, "Restaurantes": 65, "Centros de salud y spa": 80}

# TIPO 5 - viajero con niños pequeños
tipo5 = {"Parques": 90, "Jardines botánicos": 80, "Parque infantil": 100, "Playas": 80, "Lagos": 40, "Paseos": 90, "Parques temáticos": 60, "Ciencias naturales": 30, "Castillos": 50, "Torres": 40, "Murallas": 50, "Puertas": 50, "Otras arquitecturas defensivas": 30, "Otros espacios abiertos": 90}

tipo6 = {}


items = pd.read_csv("../data/items.csv")
prefs_usuarios = pd.read_csv("../data/prefs_usuarios.csv")

selecc_items = items[items['categoria'].isin(tipo5.keys())]
# selecc_usuarios = seleccionar los usuarios que sean del tipo X
# buscar esos usuarios en prefs_usuarios

selecc_usuarios = prefs_usuarios[prefs_usuarios["id_usuario"].isin([123, 124, 125, 126])]

#print(selecc_items)
print(selecc_usuarios)

