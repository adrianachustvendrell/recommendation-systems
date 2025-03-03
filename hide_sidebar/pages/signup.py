import streamlit as st
import pandas as pd
import os
import time

# File where users will be stored
USER_DATA_FILE = "info_usuarios.csv"

def find_file(filename):
    """Search for the file in all directories starting from the root folder."""
    for root, _, files in os.walk(os.getcwd()):  # Start searching from the current directory
        if filename in files:
            return os.path.join(root, filename)
    return None

# Locate the users.csv file dynamically
user_file_path = find_file(USER_DATA_FILE)

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

# Streamlit Sign-up Page
st.title("Registrarse")

with st.form(key="signup_form"):
    new_username = st.text_input("Introduce un usuario")
    new_age = st.text_input("Introduce tu edad")
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

    # Default child ages
    new_children1_age = 0
    new_children2_age = 0

    if new_children >= 1:
        new_children1_age = st.text_input("Introduce la edad de tu primer hijo")

    if new_children == 2:
        new_children2_age = st.text_input("Introduce la edad de tu segundo hijo")

    st.subheader("Preferencias")
    
    preference_options = ["Deportes", "Música", "Cine", "Lectura", "Tecnología", "Viajes", "Gastronomía"]
    score_options = [1, 2, 3, 4, 5]

    if "preferences" not in st.session_state:
        st.session_state.preferences = []

    # Mostrar preferencias ya añadidas
    for i, (pref, score) in enumerate(st.session_state.preferences):
        st.write(f"{pref}: {score}")

    # Nuevo selector de preferencia
    col1, col2 = st.columns([3, 1])
    with col1:
        new_pref = st.selectbox("Elige una preferencia", [p for p in preference_options if p not in [x[0] for x in st.session_state.preferences]], key="new_pref")
    with col2:
        new_score = st.selectbox("Puntuación", score_options, key="new_score")

    add_pref_button = st.form_submit_button("Añadir Preferencia")

    if add_pref_button and new_pref not in [x[0] for x in st.session_state.preferences]:
        st.session_state.preferences.append((new_pref, new_score))

    # ---- Enviar formulario ----
    submit_button = st.form_submit_button(label="Registrarse")
    

# Validate and store user
if submit_button:
    try:
        # Convert children ages to integers
        new_children1_age = int(new_children1_age) if new_children >= 1 else 0
        new_children2_age = int(new_children2_age) if new_children == 2 else 0

        if new_children == 1 and new_children1_age <= 0:
            st.error("Por favor, introduce correctamente la edad del hijo (debe ser mayor a 0).")
        elif new_children == 2 and (new_children1_age <= 0 or new_children2_age <= 0):
            st.error("Por favor, introduce correctamente la edad de ambos hijos (deben ser mayores a 0).")
        elif check_username_exists(new_username):
            st.error("El nombre de usuario ya está en uso. Por favor, elige otro.")
        else:
            add_user(new_username, new_age, new_sex, new_job, new_children, new_children1_age, new_children2_age)
            st.success("Cuenta creada satisfactoriamente.")
            time.sleep(2)
            st.switch_page("pages/signin.py") 
    except ValueError:
        st.error("Por favor, introduce solo valores numéricos para la edad de los hijos.")
