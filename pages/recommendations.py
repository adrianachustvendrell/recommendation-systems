import streamlit as st

# Verificar si el grupo está registrado en session_state
if "grupo_registrado" in st.session_state and st.session_state.grupo_registrado:
    st.title("Recomendaciones Turísticas para tu Grupo")
    # Aquí pondrías la lógica para mostrar las recomendaciones
else:
    st.error("No has completado el registro. Por favor, regístrate primero.")