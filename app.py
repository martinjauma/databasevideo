import streamlit as st
import pandas as pd

def main():
    st.set_page_config(page_title="YouTube Clip Player", layout="wide")
    st.title("🎥 Reproductor de Clips en Streamlit")

    # URL base sin parámetros
    video_base_url = "https://www.youtube.com/embed/deZ0nafqqsc"

    st.sidebar.header("📁 Controles")
    uploaded_file = st.sidebar.file_uploader("Cargar archivo CSV", type=["csv"])

    df = None
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            df.columns = [col.lower() for col in df.columns]
            st.sidebar.success("✅ CSV cargado exitosamente!")

            if "row name" not in df.columns or "clip start" not in df.columns:
                st.sidebar.error("❌ El CSV debe tener columnas 'Row Name' y 'Clip start'.")
                df = None
        except Exception as e:
            st.sidebar.error(f"Error al cargar el CSV: {e}")
            df = None

    selected_row_name = None
    clip_start = 0

    if df is not None:
        with st.sidebar.form("clip_selector"):
            row_names = df["row name"].unique()
            selected_row_name = st.selectbox("🎯 Seleccionar Row Name", row_names)
            submitted = st.form_submit_button("▶️ Aplicar")

        if submitted:
            try:
                clip_start = int(df[df["row name"] == selected_row_name]["clip start"].iloc[0])
                
                # Construimos la URL embebida con start
                full_url = f"{video_base_url}?start={clip_start}&autoplay=1"
                
                # Mostramos usando iframe HTML (que sí respeta el "start")
                st.markdown(f"### 🎬 Mostrando: {selected_row_name}")
                st.components.v1.html(f"""
                    <iframe width="100%" height="500" 
                    src="{full_url}" 
                    title="YouTube video player" frameborder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                    allowfullscreen></iframe>
                """, height=500)

            except Exception as e:
                st.error(f"No se pudo cargar el clip: {e}")

if __name__ == "__main__":
    main()
