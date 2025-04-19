
from metrics import obtener_items_seleccionados

# Por ejemplo, probamos con un usuario y un método:
usuario = "Usuario_123"
metodos = ["Demográfico", "Basado en contenido"]

resultados = obtener_items_seleccionados(metodos, usuario)
print(resultados)
