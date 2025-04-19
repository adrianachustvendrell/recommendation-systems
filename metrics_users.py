from metrics import obtener_items_seleccionados
import pandas as pd

# seleccionar los primeros 20 usuarios
df_usuarios = pd.read_csv('data/info_usuarios.csv')
df = df_usuarios.loc[:19, ['id_usuario', 'nombre_usuario']]

# Inicializar listas vacías
lista_demografico = []
lista_contenido = []
lista_colaborativo = []
lista_hibrido = []

# Generar recomendaciones SOLO para los 20 usuarios
for _, row in df.iterrows():
    nombre = row['nombre_usuario']
    lista_demografico.append(obtener_items_seleccionados(["Demográfico"], nombre))
    lista_contenido.append(obtener_items_seleccionados(["Basado en contenido"], nombre))
    lista_colaborativo.append(obtener_items_seleccionados(["Colaborativo"], nombre))
    lista_hibrido.append(obtener_items_seleccionados(["Demográfico", "Basado en contenido", "Colaborativo"], nombre))

# Asignar a columnas del DataFrame
df['Demografico'] = lista_demografico
df['Contenido'] = lista_contenido
df['Colaborativo'] = lista_colaborativo
df['Híbrido'] = lista_hibrido

# Mostrar el resultado
print(df.head())
