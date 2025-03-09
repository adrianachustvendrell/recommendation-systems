import pandas as pd
import requests
from huggingface_hub import InferenceClient


df = pd.read_csv('data/items.csv')
print(df)



client = InferenceClient(
	token="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"
)

descripciones = {}

# Iterar sobre los elementos únicos del nombre_item
for elem in df['nombre_item'].unique():
    # Realizar la solicitud de generación de texto
    result = client.text_generation(
        model="google/gemma-2-2b-it",
        prompt=f"Descríbeme en español {elem} de Valencia en tres frases todo en un párrafo. Hazlo atractivo para turistas",
    )

    # Almacenar la descripción en el diccionario
    descripciones[elem] = result

# Añadir la nueva columna 'descripcion' al DataFrame
df['descripcion'] = df['nombre_item'].map(descripciones)

print(df)

df.to_csv('items.csv', index=False)