import streamlit as st
import pandas as pd

def main():
    st.set_page_config(page_title="YouTube Clip Player", layout="wide")
    st.title("YouTube Clip Player")

    # URL del video de YouTube (inicialmente fija)
    video_url = "https://youtu.be/deZ0nafqqsc"
    
    # --- Barra lateral ---
    st.sidebar.header("Controles")

    # Cargar archivo CSV
    uploaded_file = st.sidebar.file_uploader("Cargar archivo CSV", type=["csv"])
    
    df = None
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            # Convertir nombres de columnas a minúsculas para manejo insensible a mayúsculas
            df.columns = [col.lower() for col in df.columns]
            st.sidebar.success("CSV cargado exitosamente!")
            
            # Verificar si las columnas necesarias existen (ahora en minúsculas)
            if "row name" not in df.columns or "clip start" not in df.columns:
                st.sidebar.error("El CSV debe contener las columnas 'Row Name' y 'Clip start'.")
                df = None # Invalidar el dataframe si no tiene las columnas
            
        except Exception as e:
            st.sidebar.error(f"Error al cargar el CSV: {e}")
            df = None

    selected_row_name = None
    if df is not None:
        # Filtro "Row Name" (usando la columna en minúsculas)
        row_names = df["row name"].unique()
        selected_row_name = st.sidebar.selectbox("Seleccionar Row Name", row_names)

    # --- Área principal ---
    # Modificar la URL del video si se ha seleccionado un Row Name y el df es válido
    current_video_url = video_url
    if selected_row_name and df is not None:
        try:
            # Acceder a las columnas usando nombres en minúsculas
            clip_start_seconds = df[df["row name"] == selected_row_name]["clip start"].iloc[0]
            # Asegurarse que clip_start_seconds es un entero
            clip_start_seconds = int(clip_start_seconds) 
            current_video_url = f"{video_url}?start={clip_start_seconds}"
        except (IndexError, ValueError) as e:
            st.error(f"No se pudo obtener 'Clip start' para '{selected_row_name}' o el valor no es un número válido. Mostrando video desde el inicio. Error: {e}")
            current_video_url = video_url # Volver al video original si hay error

    # Mostrar el video en el área principal
    st.video(current_video_url)

if __name__ == "__main__":
    main()
