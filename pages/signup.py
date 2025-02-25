# signup.py
import streamlit as st

# Title for the sign-up page
st.title("Sign Up")

# Collect user input for sign-up
with st.form(key='signup_form'):
    st.subheader('Create an Account')
    new_username = st.text_input('Enter your username')
    new_password = st.text_input('Enter your password', type='password')
    new_name = st.text_input('Enter your full name')
    new_email = st.text_input('Enter your email')

    submit_button = st.form_submit_button(label='Submit')

    if submit_button:
        # Handle user registration logic here (e.g., save new details in a database)
        st.success("Account created successfully. You can now log in.")
s