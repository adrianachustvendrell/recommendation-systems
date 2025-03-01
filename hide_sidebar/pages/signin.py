# signup.py
import streamlit as st
import pandas as pd
from pathlib import Path

@st.cache_data
def load_user_data():
    file_path = Path("data/info_usuarios.csv")
    return pd.read_csv(file_path)  # Ensure the CSV file is in the correct directory

user_data = load_user_data()

# Check if user is already logged in
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# if st.session_state["authenticated"]:
#     st.switch_page("recs_page.py")

# Title for the sign-up page
st.title("Inicia sesión")


# Formulario de registro
with st.form(key="signin_form"):
    #st.subheader("Inicia Sesión")

    # User input fields
    username = st.text_input("Enter your username")
    password = st.text_input("Enter your password", type="password")

    # Submit button
    submit_button = st.form_submit_button(label="Submit")
    #st.markdown("[Don't have an account? Sign up here!](http://localhost:8501/signup)", unsafe_allow_html=True)


if submit_button:
    # Find user in the dataset
    user_row = user_data[user_data["nombre_usuario"] == username]

    if not user_row.empty:
        # Extract user ID (password)
        correct_password = str(user_row.iloc[0]["id_usuario"])

        if password == correct_password:
            st.session_state["authenticated"] = True 
            st.success(f"Welcome, {username}!")
            # st.switch_page("pages/recs_page.py")
            # st.switch_page("recs_page.py")
        else:
            st.error("Incorrect password. Please try again.")
    else:
        st.error("Username not found. Please check your credentials.")

