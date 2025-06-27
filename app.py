import streamlit as st
import pandas as pd
import time
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# -------------------- UTILIDADES --------------------
def obtener_titulo_youtube(url):
    try:
        oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        response = requests.get(oembed_url)
        if response.status_code == 200:
            return response.json().get("title", "🎬 Sin título")
    except:
        return "⚠️ No se pudo obtener el título"

def extraer_video_id(url):
    try:
        if "watch?v=" in url:
            return url.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
    except:
        return None

def reproducir_clip(video_id, start, end):
    embed_url = f"https://www.youtube.com/embed/{video_id}?start={start}&end={end}&autoplay=1"
    st.components.v1.html(f"""
        <iframe width="100%" height="500" src="{embed_url}"
        frameborder="0" allow="autoplay; encrypted-media"
        allowfullscreen></iframe>
    """, height=500)

# -------------------- MAIN --------------------
def main():
    st.set_page_config(page_title="Rugby Clip Viewer", layout="wide")
    st.title("🏉 Reproductor Inteligente de Clips")

    # --------------- SESSION STATE inicialización ---------------
    if "youtube_url" not in st.session_state:
        st.session_state.youtube_url = "https://www.youtube.com/watch?v=XNaqqZNJUMc"
    if "df" not in st.session_state:
        st.session_state.df = None
    if "equipo_sel" not in st.session_state:
        st.session_state.equipo_sel = []
    if "rowname_sel" not in st.session_state:
        st.session_state.rowname_sel = []
    if "playlist_index" not in st.session_state:
        st.session_state.playlist_index = 0
    if "playlist_active" not in st.session_state:
        st.session_state.playlist_active = False

    # --------------- SIDEBAR ---------------
    st.sidebar.header("🎛️ Controles")
    st.session_state.youtube_url = st.sidebar.text_input(
        "🔗 URL de YouTube",
        value=st.session_state.youtube_url
    )

    video_id = extraer_video_id(st.session_state.youtube_url)
    video_title = obtener_titulo_youtube(st.session_state.youtube_url) if video_id else None

    if video_id and video_title:
        st.sidebar.success(f"🎞️ Video seleccionado: **{video_title}**")
    elif st.session_state.youtube_url.strip():
        st.sidebar.warning("⚠️ URL inválida")

    uploaded_file = st.sidebar.file_uploader("📄 Cargar CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.columns = [col.lower() for col in df.columns]
        st.session_state.df = df

    if st.session_state.df is not None:
        df = st.session_state.df.copy()

        columnas_requeridas = ["row name", "clip start", "equipo"]
        for col in columnas_requeridas:
            if col not in df.columns:
                st.sidebar.error(f"❌ Falta la columna: {col}")
                return

        if "duracion" not in df.columns:
            df["duracion"] = 20
        if "video_id" not in df.columns:
            df["video_id"] = video_id

        # --------------- FILTROS ---------------
        st.session_state.equipo_sel = st.sidebar.multiselect(
            "Equipo",
            options=df["equipo"].unique(),
            default=st.session_state.equipo_sel or df["equipo"].unique()
        )
        st.session_state.rowname_sel = st.sidebar.multiselect(
            "Eventos",
            options=df["row name"].unique(),
            default=st.session_state.rowname_sel
        )

        df_filtrado = df[df["equipo"].isin(st.session_state.equipo_sel)]
        if st.session_state.rowname_sel:
            df_filtrado = df_filtrado[df_filtrado["row name"].isin(st.session_state.rowname_sel)]

        columnas_visibles = ["row name", "equipo", "resultado"]
        for col in columnas_visibles:
            if col not in df_filtrado.columns:
                df_filtrado[col] = "Sin dato"

        # agregar clip start, duracion, video_id para reproducir
        df_filtrado = df_filtrado[columnas_visibles + ["clip start", "duracion", "video_id"]]

        # --------------- AgGrid ---------------
        st.markdown("### 🧮 Tabla de Clips")
        gb = GridOptionsBuilder.from_dataframe(df_filtrado)
        gb.configure_default_column(editable=False, resizable=True)
        gb.configure_column("duracion", editable=True)
        gb.configure_selection("multiple", use_checkbox=True)
        grid_options = gb.build()

        grid_response = AgGrid(
            df_filtrado,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.MODEL_CHANGED,
            theme="streamlit",
            height=400,
            allow_unsafe_jscode=True
        )

        updated_df = grid_response["data"]
        selected_rows = grid_response.get("selected_rows", [])

        # --------------- CONTROLES PLAYLIST ---------------
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("▶️ Play Playlist"):
                st.session_state.playlist_index = 0
                st.session_state.playlist_active = True
                st.rerun()
        with col2:
            if st.button("⏮️ Anterior"):
                st.session_state.playlist_index = max(0, st.session_state.playlist_index - 1)
                st.rerun()
        with col3:
            if st.button("⏭️ Siguiente"):
                st.session_state.playlist_index += 1
                st.rerun()
        with col4:
            if st.button("⏹️ Detener"):
                st.session_state.playlist_active = False

        # --------------- PLAYLIST AUTOMÁTICO ---------------
        if st.session_state.playlist_active:
            clips = pd.DataFrame(selected_rows)
            if clips.empty:
                st.warning("⚠️ Seleccioná al menos un clip en la tabla.")
                st.session_state.playlist_active = False
            elif st.session_state.playlist_index < len(clips):
                clip = clips.iloc[st.session_state.playlist_index]
                st.markdown(f"### ▶️ Clip: **{clip['row name']}** | Equipo: **{clip['equipo']}**")
                reproducir_clip(
                    video_id=clip["video_id"],
                    start=int(clip["clip start"]),
                    end=int(clip["clip start"] + clip["duracion"])
                )
                time.sleep(clip["duracion"])
                st.session_state.playlist_index += 1
                st.rerun()
            else:
                st.success("✅ Playlist finalizada")
                st.session_state.playlist_active = False

        # --------------- VISTA INDIVIDUAL ---------------
        elif isinstance(selected_rows, list) and len(selected_rows) > 0 and video_id:
            clip = selected_rows[0]
            st.markdown(f"### ▶️ Clip manual: **{clip['row name']}** ({clip['equipo']})")
            reproducir_clip(
                video_id=clip["video_id"],
                start=int(clip["clip start"]),
                end=int(clip["clip start"] + clip["duracion"])
            )

        # --------------- EXPORTAR ---------------
        st.sidebar.markdown("### 📥 Exportar CSV actualizado")
        st.sidebar.download_button(
            label="💾 Descargar CSV",
            data=updated_df.to_csv(index=False).encode("utf-8"),
            file_name="clips_actualizados.csv",
            mime="text/csv"
        )


if __name__ == "__main__":
    main()
