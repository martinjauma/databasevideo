import streamlit as st
import pandas as pd
import requests
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
from typing import Optional


# --- FUNCIONES DE UTILIDAD ---

def obtener_titulo_youtube(url: str) -> str:
    """Obtiene el título de un video de YouTube a partir de su URL."""
    try:
        oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        response = requests.get(oembed_url)
        response.raise_for_status()
        return response.json().get("title", "🎬 Sin título")
    except requests.exceptions.RequestException:
        return "⚠️ No se pudo obtener el título"

def extraer_video_id(url: str) -> Optional[str]:
    """Extrae el ID de un video de YouTube de diferentes formatos de URL."""
    try:
        if "watch?v=" in url:
            return url.split("watch?v=")[1].split("&")[0]
        if "youtu.be/" in url:
            return url.split("youtu.be/")[1].split("?")[0]
    except IndexError:
        return None
    return None

# --- GESTIÓN DE ESTADO ---

def inicializar_estado():
    """Inicializa todas las variables necesarias en el session_state de Streamlit."""
    defaults = {
        "youtube_url": "https://www.youtube.com/watch?v=XNaqqZNJUMc",
        "df_original": None,
        "df_filtrado": pd.DataFrame(),
        "clips_seleccionados": pd.DataFrame(),
        "playlist_index": 0,
        "playlist_active": False,
        "active_clip_details": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# --- COMPONENTES DE UI ---

def render_sidebar():
    """Renderiza la barra lateral con los controles de carga y filtrado."""
    with st.sidebar:
        st.header("⚙️ Controles")
        st.session_state.youtube_url = st.text_input("🔗 URL YouTube", value=st.session_state.youtube_url)
        video_id = extraer_video_id(st.session_state.youtube_url)
        if video_id:
            st.success(f"🎬 Video: **{obtener_titulo_youtube(st.session_state.youtube_url)}**")
        elif st.session_state.youtube_url.strip():
            st.warning("⚠️ URL de YouTube inválida.")

        uploaded_file = st.file_uploader("📂 Cargar CSV", type=["csv"])
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file, sep=None, engine="python")
                df.columns = [col.strip() for col in df.columns]
                columnas_req = ["Row Name", "Clip Start", "Clip End", "EQUIPO"]
                if not all(col in df.columns for col in columnas_req):
                    st.error(f"❌ CSV debe contener: {', '.join(columnas_req)}")
                    return
                df["Clip Start"] = pd.to_numeric(df["Clip Start"], errors='coerce')
                df["Clip End"] = pd.to_numeric(df["Clip End"], errors='coerce')
                df.dropna(subset=["Clip Start", "Clip End"], inplace=True)
                df["duracion"] = (df["Clip End"] - df["Clip Start"]).round(0)
                df["video_id"] = video_id
                st.session_state.df_original = df
                st.success("✅ CSV cargado.")
            except Exception as e:
                st.error(f"❌ Error al leer CSV: {e}")
                return

        if st.session_state.df_original is None: return

        st.header("📊 Filtros")
        df = st.session_state.df_original
        equipos = st.multiselect("Equipos", options=df["EQUIPO"].unique(), default=df["EQUIPO"].unique())
        eventos = st.multiselect("Eventos", options=df["Row Name"].unique())

        df_filtrado = df[df["EQUIPO"].isin(equipos)]
        if eventos: df_filtrado = df_filtrado[df_filtrado["Row Name"].isin(eventos)]
        st.session_state.df_filtrado = df_filtrado

def render_aggrid(height=300):
    """Muestra la tabla de clips interactiva y maneja la selección."""
    if st.session_state.playlist_active:
        df_display = st.session_state.clips_seleccionados.copy()
    else:
        df_display = st.session_state.df_filtrado.copy()

    if df_display.empty:
        st.info("No hay clips para mostrar.")
        return

    columnas_visibles = ["Row Name", "EQUIPO", "RESULTADO", "Clip Start", "duracion"]
    for col in columnas_visibles:
        if col not in df_display.columns: df_display[col] = "N/A"
    df_display["Clip Start"] = df_display["Clip Start"].round(0)
    df_display = df_display[columnas_visibles]

    gb = GridOptionsBuilder.from_dataframe(df_display)
    
    if st.session_state.playlist_active:
        gb.configure_selection("single", use_checkbox=False)
        gb.configure_grid_options(onRowClicked=JsCode("""
            function(e) {
                let api = e.api;
                let rowIndex = e.rowIndex;
                api.forEachNode(function(node) {
                    if (node.rowIndex === rowIndex) {
                        let data = node.data;
                        Streamlit.setComponentValue(data);
                    }
                });
            }
        """))
    else:
        gb.configure_selection("multiple", use_checkbox=True, pre_selected_rows=st.session_state.clips_seleccionados.index.tolist())

    grid_options = gb.build()
    grid_response = AgGrid(df_display, gridOptions=grid_options, update_mode=GridUpdateMode.MODEL_CHANGED, theme="streamlit", height=height, allow_unsafe_jscode=True, key="aggrid_clips")

    if st.session_state.playlist_active:
        if grid_response.get("component_value"):
            selected_row_data = grid_response["component_value"]
            clips_df = st.session_state.clips_seleccionados
            if not clips_df.empty:
                match_index = clips_df[
                    (clips_df["Row Name"] == selected_row_data["Row Name"]) &
                    (clips_df["EQUIPO"] == selected_row_data["EQUIPO"]) &
                    (clips_df["Clip Start"] == selected_row_data["Clip Start"])
                ].index
                if not match_index.empty:
                    st.session_state.playlist_index = match_index[0]
                    st.rerun()
    else:
        st.session_state.clips_seleccionados = pd.DataFrame(grid_response.get("selected_rows", []))

def render_player_frame(clip_info: pd.Series, autoplay: bool = True):
    """Muestra el reproductor de video de YouTube para un clip específico."""
    video_id = clip_info["video_id"]
    start_time = int(clip_info["Clip Start"])
    autoplay_param = "1" if autoplay else "0"
    embed_url = f"https://www.youtube.com/embed/{video_id}?start={start_time}&autoplay={autoplay_param}&rel=0"
    
    st.components.v1.html(
        f'<div class="video-container"><iframe src="{embed_url}" width="100%" height="450" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>',
        height=480
    )

def render_playlist_controls():
    """Muestra los botones de control de la playlist y descarga."""
    clips = st.session_state.clips_seleccionados
    is_playlist_empty = clips.empty
    
    is_first_clip = st.session_state.playlist_index == 0
    is_last_clip = st.session_state.playlist_index >= len(clips) - 1

    cols = st.columns([1.5, 1, 1, 1, 1.5, 2])
    if cols[0].button("▶️ Iniciar Playlist", disabled=is_playlist_empty):
        st.session_state.playlist_active = True
        st.session_state.playlist_index = 0
        st.rerun()

    if cols[1].button("⏪ Anterior", disabled=not st.session_state.playlist_active or is_first_clip):
        st.session_state.playlist_index -= 1
        st.rerun()

    if cols[2].button("⏩ Proximo", disabled=not st.session_state.playlist_active or is_last_clip):
        st.session_state.playlist_index += 1
        st.rerun()

    if cols[3].button("🛑 Parar", disabled=not st.session_state.playlist_active):
        st.session_state.playlist_active = False
        st.rerun()
    
    csv_data = b""
    if not is_playlist_empty:
        full_details_list = [get_full_clip_details(row) for _, row in clips.iterrows()]
        full_details_list = [row for row in full_details_list if row is not None]
        if full_details_list:
            df_to_download = pd.DataFrame(full_details_list)
            csv_data = df_to_download.to_csv(index=False).encode('utf-8-sig')

    cols[4].download_button(
        label="📥 Descargar CSV",
        data=csv_data,
        file_name="playlist_seleccionada.csv",
        mime="text/csv",
        disabled=is_playlist_empty,
        help="Descarga los clips seleccionados en formato CSV."
    )

    if st.session_state.playlist_active and not is_playlist_empty:
        cols[5].info(f"**Clip {st.session_state.playlist_index + 1} de {len(clips)}**")

def get_full_clip_details(clip_row: pd.Series) -> Optional[pd.Series]:
    """Busca los detalles completos de un clip en el DataFrame original."""
    df_original = st.session_state.df_original
    if df_original is None or clip_row.empty: return None
    
    fila_completa = df_original[
        (df_original["Row Name"] == clip_row["Row Name"]) &
        (df_original["EQUIPO"] == clip_row["EQUIPO"]) &
        (df_original["Clip Start"].round(0) == clip_row["Clip Start"])
    ]
    return fila_completa.iloc[0] if not fila_completa.empty else None

# --- VISTA PRINCIPAL UNIFICADA ---

def render_main_view():
    """Renderiza la vista principal que contiene el reproductor y la tabla."""
    st.header("📺 Reproductor")

    # Determinar qué clip mostrar
    clip_to_show = None
    autoplay = False
    clips_seleccionados = st.session_state.clips_seleccionados

    if st.session_state.playlist_active:
        if not clips_seleccionados.empty and st.session_state.playlist_index < len(clips_seleccionados):
            clip_info = clips_seleccionados.iloc[st.session_state.playlist_index]
            clip_to_show = get_full_clip_details(clip_info)
            autoplay = True
        else:
            st.success("✅ Playlist finalizada o vacía.")
            st.session_state.playlist_active = False
    elif not clips_seleccionados.empty:
        last_selected = clips_seleccionados.iloc[-1]
        clip_to_show = get_full_clip_details(last_selected)
        autoplay = False

    # Renderizar el reproductor y el título si hay un clip
    if clip_to_show is not None:
        resultado_str = f" | {clip_to_show['RESULTADO']}" if 'RESULTADO' in clip_to_show and pd.notna(clip_to_show['RESULTADO']) else ""
        st.markdown(f"### **{clip_to_show['Row Name']}** | {clip_to_show['EQUIPO']}{resultado_str}")
        render_player_frame(clip_to_show, autoplay=autoplay)
    else:
        st.info("Selecciona uno o más clips de la tabla para comenzar.")

    st.divider()
    render_playlist_controls()
    st.divider()

    with st.expander("📑 Lista de Clips", expanded=True):
        render_aggrid()

# --- APLICACIÓN PRINCIPAL ---

def main():
    """Función principal que inicializa el estado y renderiza la aplicación."""
    st.set_page_config(
        page_title="Rugby Clip Viewer",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
        <style>
            .block-container { padding-top: 1rem; }
            .video-container { margin: auto; max-width: 900px; padding-top: 10px; }
        </style>
    """, unsafe_allow_html=True)

    st.title("🏉 Reproductor Inteligente de Clips")

    inicializar_estado()
    render_sidebar()

    if st.session_state.df_original is None:
        st.info("👈 Comienza cargando un archivo CSV y una URL de YouTube en la barra lateral.")
        return

    render_main_view()

if __name__ == "__main__":
    main()
