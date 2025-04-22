from metrics import obtener_items_seleccionados
import pandas as pd





# ----------------------------------------------------------
# SELECCIONAR LOS 20 PRIMEROS USUARIOS Y CALCULAR SUS ÍTEMS
# ----------------------------------------------------------


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






# ----------------------------------------------------------
# AÑADIR LAS PUNTUACIONES DE TEST
# ----------------------------------------------------------


# Leer el test set
df_test = pd.read_csv("data/puntuaciones_usuario_test.csv")  

# Asegurar que id_usuario sea del mismo tipo (por si acaso)
df['id_usuario'] = df['id_usuario'].astype(int)
df_test['id_usuario'] = df_test['id_usuario'].astype(int)


lista_test = []

# Recorrer solo los usuarios del df original
for _, row in df.iterrows():
    id_usuario = row['id_usuario']
    
    # Filtrar el test para ese usuario
    test_usuario = df_test[df_test['id_usuario'] == id_usuario]
    
    # Crear el diccionario {id_item: ratio}
    diccionario_test = dict(zip(test_usuario['id_item'], test_usuario['ratio']))
    lista_test.append(diccionario_test)


df['Test'] = lista_test






# ----------------------------------------------------------
# CALCULAR F1, RECALL Y PRECISIÓN CON UMBRALES
# ----------------------------------------------------------

# Umbrales
# Umbrales
umbral_recomendadores = 40  # Aumentar el umbral de recomendadores
umbral_test = 65  # Aumentar el umbral de ítems relevantes


# Función para calcular las métricas de Precision, Recall, F1
def calcular_metricas(recomendados, relevantes):
    # Filtrar los ítems recomendados y relevantes que superen el umbral
    recomendados_filtrados = {item for item, score in recomendados.items() if score >= umbral_recomendadores}
    relevantes_filtrados = {item for item, score in relevantes.items() if score >= umbral_test}
    
    # Intersección entre recomendados y relevantes
    interseccion = recomendados_filtrados.intersection(relevantes_filtrados)
    
    # Cálculo de Precision, Recall y F1
    precision = len(interseccion) / len(recomendados_filtrados) if len(recomendados_filtrados) > 0 else 0
    recall = len(interseccion) / len(relevantes_filtrados) if len(relevantes_filtrados) > 0 else 0
    f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return precision, recall, f1

# Crear las columnas para las métricas
def calcular_metricas_por_usuario(row):
    # Obtener los ítems recomendados de los diferentes recomendadores
    recomendadores = {
        "Demografico": row['Demografico'],
        "Contenido": row['Contenido'],
        "Colaborativo": row['Colaborativo'],
        "Híbrido": row['Híbrido']
    }
    
    # Obtener los ítems del test
    test_items = row['Test']
    
    # Calcular las métricas para cada recomendador
    metricas = {}
    for recomendador, recomendados in recomendadores.items():
        # Calcular precisión, recall y f1 para cada recomendador
        precision, recall, f1 = calcular_metricas(recomendados, test_items)
        metricas[f"{recomendador}_precision"] = precision
        metricas[f"{recomendador}_recall"] = recall
        metricas[f"{recomendador}_f1"] = f1
    
    return pd.Series(metricas)

# Aplicar la función a cada fila del dataframe
df = df.join(df.apply(calcular_metricas_por_usuario, axis=1))






# ----------------------------------------------------------
# CALCULAR EL MAE UTILIZANDO LA INTERSECCIÓN
# ----------------------------------------------------------

# Función para calcular el MAE
def calcular_mae(recomendados, test_items, user_test_data):
    # Inicializar la suma de los errores absolutos
    error_total = 0
    num_items = 0

    # Iterar sobre los ítems recomendados
    for item, prediccion in recomendados.items():
        # Verificar si el ítem está en el test set del usuario
        if item in test_items:
            # Usamos el ratio real del test para este ítem
            ratio_real = test_items[item]
        else:
            # Si no está en el test set, asignamos 0
            ratio_real = 0
        
        # Calculamos el error absoluto entre el ratio recomendado y el ratio real
        error_total += abs(prediccion - ratio_real)
        num_items += 1
    
    # Calcular MAE (Promedio de los errores absolutos)
    mae = error_total / num_items if num_items > 0 else 0
    return mae



# Función para calcular el MAE para cada recomendador
def calcular_mae_por_usuario(row):
    # Obtener los ítems recomendados de los diferentes recomendadores
    recomendadores = {
        "Demografico": row['Demografico'],
        "Contenido": row['Contenido'],
        "Colaborativo": row['Colaborativo'],
        "Híbrido": row['Híbrido']
    }
    
    # Obtener los ítems del test para el usuario
    test_items = row['Test']
    
    # Calcular el MAE para cada recomendador
    metricas_mae = {}
    for recomendador, recomendados in recomendadores.items():
        mae = calcular_mae(recomendados, test_items, row)
        metricas_mae[f"{recomendador}_mae"] = mae
    
    return pd.Series(metricas_mae)

# Aplicar la función de MAE a cada fila del dataframe
df = df.join(df.apply(calcular_mae_por_usuario, axis=1))





# Guardar el DataFrame en un archivo CSV
df.to_csv('data/metricas_usuarios.csv', index=False)

