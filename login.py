# login.py
import streamlit as st
import streamlit_authenticator as stauth

# Define users, passwords, and names (you could also fetch these from a database)
users = ['user1', 'user2']
passwords = ['password123', 'password456']
names = ['User One', 'User Two']
emails = ["user1@gmail.com", "user2@gmail.com"]

# Define credentials as a dictionary
credentials = {
    'usernames': {
        users[0]: {'password': passwords[0], 'name': names[0], 'email': emails[0]},
        users[1]: {'password': passwords[1], 'name': names[1], "email": emails[1]}
    }
}

# Initialize authenticator with the credentials dictionary
authenticator = stauth.Authenticate(
    credentials=credentials, 
    cookie_name='some_cookie_name', 
    cookie_expiry_days=30
)

# Login widget
authentication_status = authenticator.login('main')

if st.session_state.get('authentication_status'):
    st.write(f'Welcome *{st.session_state["name"]}*!')
    st.title('Some content')
elif st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')
    st.markdown("[Don't have an account? Sign up here!](http://localhost:8501/signup)", unsafe_allow_html=True)
elif st.session_state.get('authentication_status') is None:
    st.warning('Please enter your username and password')

    # Add link for sign up page
    st.markdown("[Don't have an account? Sign up here!](http://localhost:8501/signup)", unsafe_allow_html=True)
