import streamlit as st
import pandas as pd
import os
import time

# File where users will be stored
USER_DATA_FILE = "info_usuarios.csv"
PREFERENCE_USER_DATA_FILE = 'prefs_usuarios.csv'
submit_button = False

def find_file(filename):
    """Search for the file in all directories starting from the root folder."""
    for root, _, files in os.walk(os.getcwd()):  # Start searching from the current directory
        if filename in files:
            return os.path.join(root, filename)
    return None

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

# Locate the users.csv file dynamically
user_file_path = find_file(USER_DATA_FILE)
preference_user_file_path = find_file(PREFERENCE_USER_DATA_FILE)

preference_df = pd.read_csv(preference_user_file_path)

# Load the users file or create a new one
if user_file_path:
    users_df = pd.read_csv(user_file_path)
else:
    users_df = pd.DataFrame(columns=["id_usuario", "nombre_usuario", "edad", "sexo", "id_ocupacion", "hijos", "edad_hijo_menor", "edad_hijo_mayor", "ocupacion"])
    user_file_path = os.path.join(os.getcwd(), USER_DATA_FILE)  # Save it in the current directory if not found

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
    """Añade las preferencias de un usuario al DataFrame y las guarda en un archivo CSV."""
    
    global preference_user_file_path  # Asegurar la ruta correcta del CSV de preferencias
    
    # Crear un DataFrame con las preferencias
    preferences_data = []
    for categoria, calificacion in set_preferencias:
        # Buscar el ID de la categoría en el DataFrame
        id_categoria = preference_df.loc[preference_df['categoria'] == categoria, 'id_categoria'].values
        
        if len(id_categoria) > 0:
            preferences_data.append({
                "id_usuario": new_id,
                "id_categoria": id_categoria[0],  # Extraer el valor del array
                "calificacion": calificacion,
                "categoria": categoria
            })
    
    if preferences_data:
        new_prefs_df = pd.DataFrame(preferences_data)
        
        # Cargar archivo existente o crear uno nuevo
        if os.path.exists(preference_user_file_path):
            prefs_df = pd.read_csv(preference_user_file_path)
            prefs_df = pd.concat([prefs_df, new_prefs_df], ignore_index=True)
        
        # Guardar en CSV
        prefs_df.to_csv(preference_user_file_path, index=False)


# Streamlit Sign-up Page
st.title("📝 Registrarse")

with st.form(key="signup_form"):
    new_username = st.text_input("Introduce un usuario")
    # new_age = st.text_input("Introduce tu edad")
    new_age = st.number_input("Introduce tu edad", min_value = 1, step = 1, format = "%d")
    sex_options = ['M (Masculino)', 'F (Femenino)']
    new_sex = st.selectbox("Selecciona tu sexo", sex_options)

    job_options = [
        "Fuerzas armadas", "Dirección de las empresas y de las administraciones públicas",
        "Técnicos y profesionales científicos e intelectuales", "Técnicos y profesionales de apoyo",
        "Empleados de tipo administrativo", "Trabajadores de los servicios de restauración, personales, protección y vendedores de los comercios",
        "Trabajadores cualificados en la agricultura y en la pesca", 
        "Artesanos y trabajadores cualificados de industrias manufactureras, construcción, y minería, excepto operadores de instalaciones y maquinaria",
        "Operadores de instalaciones y maquinaria, y montadores", "Trabajadores no cualificados", "Inactivo o desocupado"
    ]
    new_job = st.selectbox("Selecciona tu empleo", job_options)

    children_options = [0, 1, 2]
    new_children = st.selectbox("Selecciona el número de hijos", children_options)

    continua_button = st.form_submit_button(label="Edad hijos")
    # Default child ages
    new_children1_age = 0
    new_children2_age = 0

    if continua_button:
        if new_children >= 1:
            # new_children1_age = st.text_input("Introduce la edad de tu primer hijo")
            new_children1_age = st.number_input("Introduce la edad de tu primer hijo", min_value = 0, step = 1, format = "%d")

        if new_children == 2:
            # new_children2_age = st.text_input("Introduce la edad de tu segundo hijo")
            new_children2_age = st.number_input("Introduce la edad de tu segundo hijo", min_value = 0, step = 1, format = "%d")

    

    st.subheader("Preferencias")

    # Opciones de preferencias y puntuación
    preference_options = list(preference_df['categoria'].unique())  # Convertimos a lista
    score_options = list(range(1, 11))

    # Inicializar session_state si no existe
    if "preferences" not in st.session_state:
        st.session_state.preferences = []

    # Filtrar opciones disponibles
    available_prefs = [p for p in preference_options if p not in [x[0] for x in st.session_state.preferences]]

    # Si no hay opciones disponibles, evitar errores
    if not available_prefs:
        st.write("⚠️ Ya has seleccionado todas las preferencias disponibles.")
        st.stop()

    # Crear selección de preferencia sin modificar session_state
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_pref = st.selectbox("Elige una preferencia", available_prefs, index=0)
    with col2:
        selected_score = st.selectbox("Puntuación", score_options, key="new_score")

    # Botón para añadir preferencias
    add_pref_button = st.form_submit_button("Añadir Preferencia")

    if add_pref_button:
        if selected_pref and selected_pref not in [x[0] for x in st.session_state.preferences]:  # Asegura que no se repita
            st.session_state.preferences.append((selected_pref, selected_score))
            st.rerun()  # Recargar la app para actualizar la lista de preferencias y evitar errores de índice

    # Mostrar preferencias seleccionadas
    st.write("#### Preferencias seleccionadas:")
    for pref, score in st.session_state.preferences:
        st.write(f"✔️ {pref}: {score}")




    # ---- Enviar formulario ----
    submit_button = st.form_submit_button(label="Registrarse")
    

# Validate and store user
if submit_button:
    try:
        # Convert children ages to integers
        new_children1_age = int(new_children1_age) if new_children >= 1 else 0
        new_children2_age = int(new_children2_age) if new_children == 2 else 0
        # ✅ Validate username
        if not new_username.strip():
            st.error("El nombre de usuario no puede estar vacío.")

        # ✅ Validate children's ages
        elif new_children == 1 and new_children1_age <= 0:
            st.error("Por favor, introduce correctamente la edad del hijo (debe ser mayor a 0).")

        elif new_children == 2 and (new_children1_age <= 0 or new_children2_age <= 0):
            st.error("Por favor, introduce correctamente la edad de ambos hijos (deben ser mayores a 0).")

        # ✅ Check if username already exists
        elif check_username_exists(new_username):
            st.error("El nombre de usuario ya está en uso. Por favor, elige otro.")
        
        # ✅ If everything is correct, add user
        else:
            new_id = add_user(new_username, new_age, new_sex, new_job, new_children, new_children1_age, new_children2_age)
            add_preference(new_id, st.session_state.preferences)       
            st.success("Cuenta creada satisfactoriamente.")
            
            # ✅ Redirect to Sign-in Page
            time.sleep(2)
            st.switch_page("pages/signin.py")

    except ValueError:
        st.error("Por favor, introduce solo valores numéricos para la edad de los hijos.")
