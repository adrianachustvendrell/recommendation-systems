import streamlit as st
import pandas as pd
import os
import time

# --------------------------------------
# ESTILO PÁGINA
# --------------------------------------


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
submit_button = False
preferencias_button = False



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


preference_df = pd.read_csv(preference_user_file_path)
items_df = pd.read_csv(items_file_path)



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


def add_user(username, age, sex, job, children, child1_age, child2_age):
    """Adds a new user to the DataFrame and saves it."""
    new_id = generate_user_id()  # Generate a unique ID
    id_ocupacion = job_options.index(job) + 1  # Assign a numerical ID for occupation (modify if needed)

    # Ensure child ages are set correctly
    child1_age = int(child1_age) if children >= 1 else 0
    child2_age = int(child2_age) if children == 2 else 0

    # Append new user to DataFrame
    new_user = pd.DataFrame({
        "id_usuario": [new_id],
        "nombre_usuario": [username],
        "edad": [age],
        "sexo": [sex],
        "id_ocupacion": [id_ocupacion],
        "hijos": [children],
        "edad_hijo_menor": [child1_age],
        "edad_hijo_mayor": [child2_age],
        "ocupacion": [job]
    })
    
    global users_df
    users_df = pd.concat([users_df, new_user], ignore_index=True)
    # Save to CSV
    users_df.to_csv(user_file_path, index=False)

    return new_id



def add_preference(new_id, set_preferencias):

    global preference_user_file_path  # Asegurar la ruta correcta del CSV de preferencias
    
    # Crear un DataFrame con las preferencias
    preferences_data = []
    for categoria, subcategoria, calificacion in set_preferencias:
        # Buscar el ID de la categoría en el DataFrame
        id_categoria = preference_df.loc[preference_df['categoria'] == categoria, 'id_categoria'].values
        id_subcategoria = preference_df.loc[preference_df['categoria'] == subcategoria, 'id_categoria'].values
        
        if len(id_categoria) > 0:
            preferences_data.append({
                "id_usuario": new_id,
                "id_categoria": id_categoria[0],  # Extraer el valor del array
                "calificacion": calificacion,
                "categoria": categoria
            })

        if len(id_subcategoria) > 0:
            preferences_data.append({
                "id_usuario": new_id,
                "id_categoria": id_subcategoria[0],  # Extraer el valor del array
                "calificacion": calificacion,
                "categoria": subcategoria
            })
    
    if preferences_data:
        new_prefs_df = pd.DataFrame(preferences_data)
        
        # Cargar archivo existente o crear uno nuevo
        if os.path.exists(preference_user_file_path):
            prefs_df = pd.read_csv(preference_user_file_path)
            prefs_df = pd.concat([prefs_df, new_prefs_df], ignore_index=True)
        
        # Guardar en CSV
        prefs_df.to_csv(preference_user_file_path, index=False)






# ---------------------------------
# FORM DE REGISTRO
# ---------------------------------


# --------------------------------------
# VARIABLES DE SESIÓN PARA NO PERDER DATOS
# --------------------------------------
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

# --------------------------------------
# FORMULARIO DE REGISTRO SIN FORM
# --------------------------------------
st.title("📝 Registrarse")

st.session_state.new_username = st.text_input("Introduce un usuario", st.session_state.get("new_username", ""))
st.session_state.new_age = st.number_input("Introduce tu edad", min_value=1, step=1, format="%d", value=st.session_state.get("new_age", 1))
sex_options = {"Masculino": "M", "Femenino": "F"}
reverse_sex_options = {v: k for k, v in sex_options.items()}  # {'M': 'Masculino', 'F': 'Femenino'}
current_sex = st.session_state.get("new_sex", "M")  
current_sex_friendly = reverse_sex_options.get(current_sex, "Masculino") 
selected_sex = st.selectbox("Selecciona tu sexo", list(sex_options.keys()), index=list(sex_options.keys()).index(current_sex_friendly))
st.session_state.new_sex = sex_options[selected_sex]


job_options = [
    "Fuerzas armadas", "Dirección de empresas", "Técnicos y profesionales", 
    "Empleados administrativos", "Vendedores", "Agricultores", 
    "Artesanos", "Operadores de maquinaria", "Trabajadores no cualificados", "Inactivo"
]
st.session_state.new_job = st.selectbox("Selecciona tu empleo", job_options, index=job_options.index(st.session_state.get("new_job", "Inactivo")))



children_options = {"Sin hijos": 0, "Con hijos": 1}
reverse_children_options = {v: k for k, v in children_options.items()}  # {0: 'Sin hijos', 1: 'Con hijos'}
current_children = st.session_state.get("new_children", 0)  # Por defecto 0
current_children_friendly = reverse_children_options.get(current_children, "Sin hijos")  # Convertir 0 → "Sin hijos"
selected_children = st.selectbox("¿Tienes hijos?", list(children_options.keys()), index=list(children_options.keys()).index(current_children_friendly))
st.session_state.new_children = children_options[selected_children]

# Botón principal de continuar
if st.button("Continuar", key="btn_continuar"):
    if st.session_state.new_children == 0:
        st.session_state.form_completed = "preferences"  # Ir directamente a preferencias
    else:
        st.session_state.form_completed = True  # Si hay hijos, pedir edades
    st.rerun()

# --------------------------------------
# FORMULARIO DE EDAD DE HIJOS
# --------------------------------------
if st.session_state.get("form_completed") == True and st.session_state.new_children > 0:
    if st.session_state.new_children >= 1:
        st.session_state.new_children1_age = st.number_input("Edad del primer hijo", min_value=0, step=1, format="%d", value=st.session_state.get("new_children1_age", 0))
        st.session_state.new_children2_age = st.number_input("Edad del segundo hijo (0 si sólo tienes un hijo)", min_value=0, step=1, format="%d", value=st.session_state.get("new_children2_age", 0))
    
    if st.button(label="Continuar a Preferencias", key="btn_preferencias"):
        st.session_state.form_completed = "preferences"



# --------------------------------------
# SELECCIÓN DE PREFERENCIAS (MOSTRAR SOLO CUANDO SE HAYA COMPLETADO EL FORM ANTERIOR)
# --------------------------------------

if st.session_state.get("form_completed") == "preferences":
    st.title("🎯 Preferencias")
    padre_options = list(items_df['padre_categoria'].unique())
    score_options = list(range(10, 110, 10))

    # 🔹 Filtrar subcategorías ya seleccionadas
    selected_subcategories = {child for _, child, _ in st.session_state.preferences}
    hijos_disponibles = [
            cat for cat in items_df[items_df['padre_categoria'] == st.session_state.selected_parent]['categoria'].unique()
            if cat not in selected_subcategories
        ]

    selected_parent = st.selectbox(
            "Elige una categoría",
            padre_options,
            index=padre_options.index(st.session_state.selected_parent),
            key="parent_select"
        )

    if selected_parent != st.session_state.selected_parent:
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
    for parent, child, score in st.session_state.preferences:
        st.markdown(f"✅ **{parent} ➝ {child}**: {score}")

    submit_button = st.button(label="Registrarse", key=1234)



# ---------------------------------
# CONTROLAR ERRORES FORMULARIO
# ---------------------------------

# Validate and store user
if submit_button:
    if not st.session_state.new_username.strip():
        st.error("❌ El nombre de usuario no puede estar vacío.")
    # ✅ Check if username already exists
    elif check_username_exists(st.session_state.new_username):
        st.error("❌ El nombre de usuario ya está en uso. Por favor, elige otro.")
        
    # ✅ If everything is correct, add user
    else:
        new_id = add_user(st.session_state.new_username, 
                          st.session_state.new_age, 
                          st.session_state.new_sex, 
                          st.session_state.new_job, 
                          st.session_state.new_children, 
                          st.session_state.new_children1_age, 
                          st.session_state.new_children2_age)
        add_preference(new_id, st.session_state.preferences)       
        st.success("👌 Cuenta creada satisfactoriamente.")
            
        # ✅ Redirect to Sign-in Page
        time.sleep(2)
        st.switch_page("pages/signin.py")