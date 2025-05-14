# Descubre Valencia

**Descubre Valencia** es una aplicación desarrollada como parte de la asignatura *Sistemas de Recomendadores*, del Máster Universitario en Inteligencia Artificial, Reconocimiento de Formas e Imagen Digital.

El objetivo del proyecto es ofrecer recomendaciones personalizadas de lugares y actividades en la ciudad de Valencia, utilizando diferentes enfoques de recomendación, incluyendo estrategias individuales y grupales.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://descubre-valencia.streamlit.app/](https://descubre-valencia.streamlit.app/))

## Estructura del repositorio

El repositorio contiene los siguientes directorios y archivos:

- **`.streamlit/`**: Configuración de la interfaz de usuario para la aplicación Streamlit.
- **`__pycache__/`**: Archivos temporales generados automáticamente por Python (no modificar).
- **`data/`**: Datos procesados empleados por la app.
- **`images/`**: Imágenes utilizadas en la interfaz gráfica de la aplicación.
- **`metrics/`**: Métricas y resultados de evaluación de las recomendaciones generadas.
- **`pages/`**: Subpáginas de la aplicación Streamlit (estructura multi-página).
- **`rawdata/`**: Datos en bruto antes del preprocesado.
- **`.gitignore`**: Define qué archivos/directorios deben ser ignorados por Git.
- **`README.md`**: Este archivo, con información sobre el proyecto.
- **`app.py`**: Script principal que lanza la aplicación en Streamlit.
- **`llm.py`**: Script para generar las descripciones de los lugares turísticos.
- **`prep.ipynb`**: Notebook para el preprocesamiento de datos.
- **`styles.css`**: Hoja de estilos para personalizar la apariencia de la app.

## Requisitos

- Python 3.12.7
- Streamlit
- Pandas
- Numpy
- Scikit-learn
- (y otras librerías comunes)

> Se recomienda crear un entorno virtual e instalar las dependencias con:

```bash
pip install -r requirements.txt
