import streamlit as st
import pandas as pd
import os
import time
import random
from PIL import Image
from scipy.stats import pearsonr
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

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



# --------------------------------------
# ESTILO PÁGINA
# --------------------------------------

st.set_page_config(page_title="Registrarse", page_icon="🚀", layout="wide")

custom_css = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Text:ital@0;1&family=Megrim&display=swap');

        html, body, [class*="st-"] {
            font-family: "DM Serif Text", serif;
            font-weight: 400;
            font-style: normal;
        }
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)





# --------------------------------------
# LEER CSV USUARIOS Y PREFERENCIAS
# --------------------------------------


# File where users will be stored
USER_DATA_FILE = "info_usuarios.csv"
PREFERENCE_USER_DATA_FILE = 'prefs_usuarios.csv'
ITEMS_DATA_FILE = 'items.csv'
BASE_DATA_FILE = 'puntuaciones_usuario_base.csv'
submit_button = False
preferencias_button = False
cont_button = False



def find_file(filename):
    """Search for the file in all directories starting from the root folder."""
    for root, _, files in os.walk(os.getcwd()):  # Start searching from the current directory
        if filename in files:
            return os.path.join(root, filename)
    return None



# Locate the users.csv file dynamically
user_file_path = find_file(USER_DATA_FILE)
preference_user_file_path = find_file(PREFERENCE_USER_DATA_FILE)
items_file_path = find_file(ITEMS_DATA_FILE)
base_file_path = find_file(BASE_DATA_FILE)


# Nombres de las hojas
USUARIOS_HOJA = "info_usuarios"
PREFS_HOJA = "prefs_usuarios"
BASE_HOJA = "puntuaciones_usuario_base"

@st.cache_resource
def load_google_sheets():
    usuarios_sheet = client.open("info_usuarios").sheet1
    prefs_sheet = client.open("prefs_usuarios").sheet1
    base_sheet = client.open("puntuaciones_usuario_base").sheet1
    return usuarios_sheet, prefs_sheet, base_sheet

usuarios_sheet, prefs_sheet, base_sheet = load_google_sheets()

# Leer a DataFrames
users_df = pd.DataFrame(usuarios_sheet.get_all_records())
preference_df = pd.DataFrame(prefs_sheet.get_all_records())
items_df = pd.read_csv(items_file_path)  # si no lo vas a modificar, no necesitas moverlo a Sheets




# Load the users file or create a new one
if user_file_path:
    users_df = pd.read_csv(user_file_path)
else:
    users_df = pd.DataFrame(columns=["id_usuario", "nombre_usuario", "edad", "sexo", "id_ocupacion", "hijos", "edad_hijo_menor", "edad_hijo_mayor", "ocupacion"])
    user_file_path = os.path.join(os.getcwd(), USER_DATA_FILE)  # Save it in the current directory if not found




# --------------------------------------
# FUNCIONES DE AÑADIR USUARIO/PREFERENCIA
# --------------------------------------

def check_username_exists(username):
    """Checks if a username is already in the DataFrame."""
    return username in users_df["nombre_usuario"].values


def generate_user_id():
    """Generates a new unique id_usuario."""
    if users_df.empty:
        return 1  # Start from 1 if no users exist
    else:
        return users_df["id_usuario"].max() + 1  # Increment the highest ID


def add_user(username, age, sex, job, children, child1_age, child2_age, tipo, top_neighbours):
    new_id = generate_user_id()
    id_ocupacion = job_options.index(job) + 1

    # Asegurar que edades de hijos estén bien según cantidad de hijos
    child1_age = int(child1_age) if children >= 1 else 0
    child2_age = int(child2_age) if children == 2 else 0

    # Lista con todos los campos
    new_user = [
        new_id, username, age, sex, id_ocupacion, children, child1_age, child2_age, job, tipo, top_neighbours
    ]

    # Convertimos todo a string (evita errores de serialización JSON)
    new_user_clean = [str(x) for x in new_user]

    # Agregamos la fila a la hoja
    usuarios_sheet.append_row(new_user_clean)

    return new_id



def add_preference(new_id, set_preferencias):
    preferences_data = []
    for categoria, subcategoria, calificacion in set_preferencias:
        id_categoria = preference_df.loc[preference_df['categoria'] == categoria, 'id_categoria'].values
        id_subcategoria = preference_df.loc[preference_df['categoria'] == subcategoria, 'id_categoria'].values

        if len(id_categoria) > 0:
            preferences_data.append([
                new_id, id_categoria[0], calificacion, categoria
            ])
        if len(id_subcategoria) > 0:
            preferences_data.append([
                new_id, id_subcategoria[0], calificacion, subcategoria
            ])
    
    # Añadir todas las filas a la hoja, asegurando que todo sea string
    for fila in preferences_data:
        prefs_sheet.append_row([str(x) for x in fila])



def add_base(new_id, selected_items):
    items_data = []
    for elem, score in selected_items.items():
        idi = items_df['id_item'][items_df['nombre_item'] == elem].iloc[0]
        items_data.append([new_id, idi, score])

    for fila in items_data:
        base_sheet.append_row([str(x) for x in fila])



def toggle_info(i):
    """ Cambia el estado de visibilidad de la información. """
    st.session_state.show_info[i] = not st.session_state.show_info[i]









# ---------------------------------
# FORM DE REGISTRO
# ---------------------------------


# --------------------------------------
# VARIABLES DE SESIÓN PARA NO PERDER DATOS
# --------------------------------------
if "new_username" not in st.session_state:
    st.session_state.new_username = None
if "new_children1_age" not in st.session_state:
    st.session_state.new_children1_age = 0
if "new_children2_age" not in st.session_state:
    st.session_state.new_children2_age = 0
if "preferences" not in st.session_state:
    st.session_state.preferences = []
if "selected_parent" not in st.session_state:
    st.session_state.selected_parent = items_df['padre_categoria'].unique()[0]
if "form_completed" not in st.session_state:
    st.session_state.form_completed = False
if "items_propuestos" not in st.session_state:
    st.session_state.items_propuestos = set()
if "selected_item" not in st.session_state:
    st.session_state.selected_item = {}
if "step" not in st.session_state:
    st.session_state.step = "inicio"
if 'registrados' not in st.session_state:
    st.session_state.registrados = True 



score_options = list(range(10, 110, 10))
job_options = [
        "Fuerzas armadas", "Dirección de empresas", "Técnicos y profesionales", 
        "Empleados administrativos", "Vendedores", "Agricultores", 
        "Artesanos", "Operadores de maquinaria", "Trabajadores no cualificados", "Inactivo o desocupado"
    ]


if st.button("🏠 Home"):
    st.switch_page("app.py") 



# --------------------------------------
# FORMULARIO DE REGISTRO SIN FORM
# --------------------------------------
if st.session_state.step == "inicio":
    st.title("📝 Registrarse")

    st.session_state.new_username = st.text_input("Introduce un usuario", st.session_state.get("new_username", ""))
    st.session_state.new_age = st.number_input("Introduce tu edad", min_value=1, step=1, format="%d", value=st.session_state.get("new_age", 1))
    sex_options = {"Masculino": "M", "Femenino": "F"}
    reverse_sex_options = {v: k for k, v in sex_options.items()}  # {'M': 'Masculino', 'F': 'Femenino'}
    current_sex = st.session_state.get("new_sex", "M")  
    current_sex_friendly = reverse_sex_options.get(current_sex, "Masculino") 
    selected_sex = st.selectbox("Selecciona tu sexo", list(sex_options.keys()), index=list(sex_options.keys()).index(current_sex_friendly))
    st.session_state.new_sex = sex_options[selected_sex]


    st.session_state.new_job = st.selectbox("Selecciona tu empleo", job_options, index=job_options.index(st.session_state.get("new_job", "Inactivo o desocupado")))



    children_options = {"No": 0, "Sí": 1}
    reverse_children_options = {v: k for k, v in children_options.items()}  # {0: 'Sin hijos', 1: 'Con hijos'}
    current_children = st.session_state.get("new_children", 0)  # Por defecto 0
    current_children_friendly = reverse_children_options.get(current_children, "Sin hijos")  # Convertir 0 → "Sin hijos"
    selected_children = st.selectbox("¿Tienes hijos?", list(children_options.keys()), index=list(children_options.keys()).index(current_children_friendly))
    st.session_state.new_children = children_options[selected_children]

    # Botón principal de continuar
    if st.button("Continuar →", key="btn_continuar"):
        if not st.session_state.new_username.strip():
            st.error("❌ El nombre de usuario no puede estar vacío.")
        elif check_username_exists(st.session_state.new_username):
            st.error("❌ El nombre de usuario ya está en uso. Por favor, elige otro.")
        else:
            if st.session_state.new_children == 0:
                st.session_state.step = "preferences"
            else:
                st.session_state.step = "edad_hijos"
            st.rerun()


# --------------------------------------
# FORMULARIO DE EDAD DE HIJOS
# --------------------------------------
elif st.session_state.step == "edad_hijos":
    st.title('🧒 Hijos')
    if st.session_state.new_children >= 1:
        st.session_state.new_children1_age = st.number_input("Edad del primer hijo", min_value=0, step=1, format="%d", value=st.session_state.get("new_children1_age", 0))
        st.session_state.new_children2_age = st.number_input("Edad del segundo hijo (0 si sólo tienes un hijo)", min_value=0, step=1, format="%d", value=st.session_state.get("new_children2_age", 0))
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Volver"):
            st.session_state.step = "inicio"
            st.rerun()
    
    with col2:
        if st.button("Continuar → ", key="btn_preferencias_huidsjk"):
            st.session_state.step = "preferences"
            st.rerun()


# --------------------------------------
# SELECCIÓN DE PREFERENCIAS (MOSTRAR SOLO CUANDO SE HAYA COMPLETADO EL FORM ANTERIOR)
# --------------------------------------

elif st.session_state.step == "preferences":
    st.title("🎯 Preferencias")
    
    padre_options = list(items_df['padre_categoria'].unique())
    score_options = list(range(10, 110, 10))

    # 🔹 Inicializar preferencias si no existen
    if "preferences" not in st.session_state:
        st.session_state.preferences = []

    # 🔹 Filtrar subcategorías ya seleccionadas
    selected_subcategories = {child for _, child, _ in st.session_state.preferences}
    hijos_disponibles = [
        cat for cat in items_df[items_df['padre_categoria'] == st.session_state.get("selected_parent", padre_options[0])]['categoria'].unique()
        if cat not in selected_subcategories
    ]

    selected_parent = st.selectbox(
        "Elige una categoría",
        padre_options,
        index=padre_options.index(st.session_state.get("selected_parent", padre_options[0])),
        key="parent_select"
    )

    if selected_parent != st.session_state.get("selected_parent", None):
        st.session_state.selected_parent = selected_parent
        hijos_disponibles = [
            cat for cat in items_df[items_df['padre_categoria'] == selected_parent]['categoria'].unique()
            if cat not in selected_subcategories
        ]
        if hijos_disponibles:
            st.session_state.selected_child = hijos_disponibles[0]

    col1, col2 = st.columns([2, 1])
    with col1:
        selected_child = st.selectbox("Elige una subcategoría", hijos_disponibles, key="child_select")
        st.session_state.selected_child = selected_child

    with col2:
        selected_score = st.selectbox("Valoración", score_options, key="score_select")

    # 🚀 Limitar selección a 10 preferencias
    if st.button("Añadir Preferencia"):
        if len(st.session_state.preferences) >= 10:
            st.warning("⚠️ Has alcanzado el límite de 10 preferencias.")
        elif selected_parent and selected_child:
            st.session_state.preferences.append((selected_parent, selected_child, selected_score))
            st.rerun()

    st.write(f"#### Preferencias seleccionadas ({len(st.session_state.preferences)}/10):")

    # 🔥 Mostrar preferencias con botón para eliminar
    for i, (parent, child, score) in enumerate(st.session_state.preferences):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"✅ **{parent} ➝ {child}**: {score}")
        with col2:
            if st.button(f"❌", key=f"remove_{i}"):
                del st.session_state.preferences[i]  # Eliminar la preferencia
                st.rerun()


    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Volver"):
            if st.session_state.new_children == 0:
                st.session_state.step = "inicio"
            else:
                st.session_state.step = "edad_hijos"
            st.rerun()

    with col2:
        if st.button("Continuar →", key="btn_puntuaciones"):
            if not st.session_state.preferences:
                st.error("❌ Selecciona al menos tres preferencias.")
            elif len(st.session_state.preferences) < 3:
                st.error("❌ Selecciona más preferencias  (al menos 3).")
            else:
                st.session_state.step = "puntuacion"
                st.rerun()

# -------------------------------------------
# PREFERENCIAS ÍTEMS
# -------------------------------------------

elif st.session_state.step == "puntuacion":
    st.title("🎖️ ¿Cómo puntuarías estos lugares?")

    # Generar los ítems solo si aún no se han guardado en session_state
    if not st.session_state.items_propuestos:
        cat = set()
        for i in range(len(st.session_state.preferences)):
            cat.add(random.choice(st.session_state.preferences)[1])
            if len(cat) == 5:
                break

        cat_lista = list(cat)  # Convertir el set en lista para poder indexarlo

        while len(st.session_state.items_propuestos) < 5:
            r = random.randint(0, len(cat_lista) - 1)  # Elegir un índice aleatorio
            items = items_df.loc[items_df['categoria'] == cat_lista[r], 'nombre_item'].tolist()
            if items:
                st.session_state.items_propuestos.add(random.choice(items))

    # Asegúrate de que los elementos estén en una lista
    st.session_state.items_propuestos = list(st.session_state.items_propuestos)

    # Inicializar estado si no existe
    if "show_info" not in st.session_state:
        st.session_state.show_info = {i: False for i in range(len(st.session_state.items_propuestos))}  # Default to False for all items


    # Crear las columnas para mostrar los elementos
    cols = st.columns(2)

    # Mostrar elementos y sus detalles en columnas
    for idx, elem in enumerate(st.session_state.items_propuestos):
        col = cols[idx % 2]  # Alternar entre las dos columnas

        with col:

            # Definir la clave del botón y la visibilidad de la información
            button_key = f"btnnnn_{elem}"
            is_info_visible = st.session_state.show_info[idx]  # Cambiar 'i' por 'idx' aquí
            
            button_text = f"📌 {elem} +" if not is_info_visible else f"📌 {elem} -"
            button_style = (
                "background-color: #888888; color: white;" if is_info_visible else "background-color: white; color: #f63366;"
            )
            
            # Botón para mostrar/ocultar detalles
            if st.button(button_text, key=button_key, use_container_width=True, 
                        on_click=lambda idx=idx: toggle_info(idx)):  # Pasar 'idx' en el lambda
                pass  # El on_click actualiza automáticamente el estado en session_state

            # Mostrar la información adicional si está visible
            if is_info_visible:
                        
                # Mostrar la información adicional cuando el botón ha sido presionado
                if is_info_visible:
                    fila_desc = items_df['descripcion'][items_df['nombre_item'] == elem].iloc[0]
                    fila_id = items_df['id_item'][items_df['nombre_item'] == elem].iloc[0]
                    img_file = f"{fila_id}.jpg"
                    img_path = os.path.join('images', img_file)

                    # Mostrar imagen si existe
                    if os.path.exists(img_path):
                        image = Image.open(img_path)
                        st.image(image)
                    else:
                        st.error("❌ Imagen no encontrada.")

                    st.write(fila_desc)

            
            # Selectbox para la valoración
            selected_score = st.selectbox(
                label="Selecciona una valoración",  # Se necesita, pero será ocultado
                options=score_options,
                key=f"{elem}_select",
                label_visibility="collapsed",
                index = score_options.index(100)
            )

            st.markdown('\n\n\n')

            # Guardar la valoración seleccionada
            st.session_state.selected_item[elem] = selected_score

                        
            
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Volver"):
            st.session_state.step = "preferences"
            st.rerun()

    with col2:
        # Botón de registro
        submit_button = st.button(label="Registrarse →")






# -----------------------------------
# OBTENER TIPO DE USUARIO DEMOGRÁFICO
# -----------------------------------


if st.session_state.new_age < 60:
    #tipo 2: viajero borrachera
    if st.session_state.new_age > 18 and (st.session_state.new_job == 'Trabajadores no cualificados' or st.session_state.new_job == 'Inactivo o desocupado') and st.session_state.new_children == 0:
        tipo = 'tipo2'
    #tipo 5: viajero niños
    elif st.session_state.new_age > 30 and st.session_state.new_children > 0 and (st.session_state.new_children1_age < 12 or st.session_state.new_children2_age < 12):
        tipo = 'tipo5'
    #tipo 3: viajero joven con cultura 
    elif st.session_state.new_age < 30 and st.session_state.new_age > 18 and (st.session_state.new_job == 'Dirección de las empresas y de las administraciones públicas' or st.session_state.new_job == 'Técnicos y profesionales científicos e intelectuales'or st.session_state.new_job == 'Técnicos y profesionales de apoyo'):
        tipo = 'tipo3'
    else:
        #tipo 6: militares
        if st.session_state.new_job == 'Fuerzas armadas':
            tipo = 'tipo6'
        #tipo 1: viajero disfrute (grupo grande)  
        else:
            tipo = 'tipo1'
#tipo 4: viajero jubilado
else:
    tipo = 'tipo4'







# -----------------------------------
# OBTENER VECINOS COLABORATIVO
# -----------------------------------


#usuarios = pd.DataFrame(users_df['id_usuario'])
ratings_df = pd.read_csv(base_file_path)
# Crear matriz usuario-item (usuarios en filas, ítems en columnas)
user_item_matrix = ratings_df.pivot(index="id_usuario", columns="id_item", values="ratio")

nuevo_usuario_rating = {}
for elem, score in st.session_state.selected_item.items():
    # Buscar el ID de la categoría en el DataFrame
    idi = items_df['id_item'][items_df['nombre_item'] == elem].iloc[0]
    nuevo_usuario_rating[idi] = score


# Suponiendo que nuevo_usuario_ratings es un diccionario con ítems y calificaciones
top_neighbors = {}
nuevo_usuario_series = pd.Series(nuevo_usuario_rating)

similarities = {}
for user in user_item_matrix.index:
    # Filtrar ítems comunes entre el nuevo usuario y el usuario existente
    common_items = user_item_matrix.loc[user].dropna().reindex(nuevo_usuario_series.index).dropna()
    nuevo_common = nuevo_usuario_series.reindex(common_items.index).dropna()
    
    if len(common_items) > 1:  # Se necesitan al menos 2 valores para Pearson
        if common_items.std() > 0 and nuevo_common.std() > 0:
            corr, _ = pearsonr(common_items, nuevo_common)
            similarities[user] = round(float(corr), 6)

# Ordenar por similitud y seleccionar los 8 más cercanos
top_neighbors = dict(sorted(similarities.items(), key=lambda x: x[1], reverse=True)[:8])






# ---------------------------------
# CONTROLAR ERRORES FORMULARIO
# ---------------------------------

# Validate and store user
if submit_button:
    if len(set(st.session_state.selected_item.values())) == 1:
        st.error("❌ Todos los ítems tienen la misma valoración. Cambia al menos uno.")
    else:
        new_id = add_user(st.session_state.new_username, 
                            st.session_state.new_age, 
                            st.session_state.new_sex, 
                            st.session_state.new_job, 
                            st.session_state.new_children, 
                            st.session_state.new_children1_age, 
                            st.session_state.new_children2_age,
                            tipo,
                            top_neighbors)
        add_preference(new_id, st.session_state.preferences)    
        add_base(new_id, st.session_state.selected_item)   
        st.success("👌 Cuenta creada satisfactoriamente.")
                
        # Redirect to Sign-in Page
        if st.session_state.registrados == False:
            time.sleep(2)
            st.switch_page("pages/group.py")

        else:
            time.sleep(2)
            st.switch_page("pages/signin.py")


