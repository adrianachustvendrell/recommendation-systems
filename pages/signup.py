# signup.py
import streamlit as st

# Title for the sign-up page
st.title("Sign Up")


# Formulario de registro
with st.form(key="signup_form"):
    st.subheader("Create an Account")

    # Datos básicos
    new_username = st.text_input("Enter your username")
    new_password = st.text_input("Enter your password", type="password")
    new_age = st.text_input("Enter your age")
    sex_options = ['M (Male)', 'F (Female)']
    new_sex = st.selectbox("Enter your sex", sex_options)

    # Selección de trabajo
    job_options = [
        "Fuerzas armadas",
        "Dirección de las empresas y de las administraciones públicas",
        "Técnicos y profesionales científicos e intelectuales",
        "Técnicos y profesionales de apoyo",
        "Empleados de tipo administrativo",
        "Trabajadores de los servicios de restauración, personales, protección y vendedores de los comercios",
        "Trabajadores cualificados en la agricultura y en la pesca",
        "Artesanos y trabajadores cualificados de industrias manufactureras, construcción, y minería, excepto operadores de instalaciones y maquinaria",
        "Operadores de instalaciones y maquinaria, y montadores",
        "Trabajadores no cualificados",
        "Inactivo o desocupado",
    ]
    new_job = st.selectbox("Enter your job", job_options)

    # Selección de número de hijos
    children_options = [0, 1, 2]
    new_children = st.selectbox("How many children do you have?", children_options)

    # Campos de edad de los hijos (solo aparecen si tiene hijos)
    children_ages = []
    if new_children >= 1:
        new_children1_age = st.text_input("Enter the age of your first child:")
        children_ages.append(new_children1_age)

    if new_children == 2:
        new_children2_age = st.text_input("Enter the age of your second child:")
        children_ages.append(new_children2_age)

    # Un solo botón de envío
    submit_button = st.form_submit_button(label="Submit")

# ✅ Validación después de presionar Submit
if submit_button:
    if new_children >= 1 and (not children_ages[0]):  # Si tiene 1 hijo y el campo está vacío
        st.error("Please enter the age of your child(s).")
    elif new_children == 2 and (not children_ages[1]):  # Si tiene 2 hijos y falta la segunda edad
        st.error("Please enter the age of your child(s).")
    else:
        st.success("Account created successfully. You can now see your recommendations")


# para añadir datos: recordar comprobar que sex = M o sex = F (convertir la variable). idem con el resto

# redirigir a la pagina main con ya las recomendaciones
