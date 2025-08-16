# Force redeploy
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
    if not isinstance(url, str):
        return None
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
    if "df_original" not in st.session_state:
        st.session_state.df_original = None
    if "df_filtrado" not in st.session_state:
        st.session_state.df_filtrado = pd.DataFrame()
    if "clips_seleccionados" not in st.session_state:
        st.session_state.clips_seleccionados = pd.DataFrame()
    if "playlist_index" not in st.session_state:
        st.session_state.playlist_index = 0
    if "playlist_active" not in st.session_state:
        st.session_state.playlist_active = False
    if "active_clip_details" not in st.session_state:
        st.session_state.active_clip_details = None
    if "columnas_visibles" not in st.session_state:
        st.session_state.columnas_visibles = []
    if "data_context" not in st.session_state:
        st.session_state.data_context = ""
    if "new_file_loaded" not in st.session_state:
        st.session_state.new_file_loaded = False

def load_demo_data():
    local_csv_path = "page/DEMO/2025_VJUL_NZDvsFRA_LINEOUT.csv"
    remote_csv_url = "https://raw.githubusercontent.com/martinjauma/databasevideo/main/page/DEMO/2025_VJUL_NZDvsFRA_LINEOUT.csv"
    
    try:
        # Try to load from local path first
        df = pd.read_csv(local_csv_path, sep=None, engine="python")
        st.success("✅ CSV de demostración cargado localmente.")
    except FileNotFoundError:
        try:
            # If local file not found, load from remote URL
            df = pd.read_csv(remote_csv_url, sep=None, engine="python")
            st.success("✅ CSV de demostración cargado desde GitHub.")
        except Exception as e:
            st.error(f"❌ Error al cargar el CSV de demostración: {e}")
            return
    except Exception as e:
        st.error(f"❌ Error al procesar el CSV: {e}")
        return

    # --- Lógica de mapeo de columnas flexible y insensible a mayúsculas ---
    original_cols = {col.strip(): col for col in df.columns}
    df.rename(columns={v: k for k, v in original_cols.items()}, inplace=True)
    lower_case_map = {col.lower(): col for col in df.columns}
    column_mapping = {
        'Row Name': ['row name', 'code'],
        'Clip Start': ['clip start', 'start'],
        'Clip End': ['clip end', 'stop', 'end'],
        'EQUIPO': ['equipo'],
        'JUGADOR': ['jugador', 'player'],
        'RESULTADO': ['resultado', 'result'],
        'FORM': ['form', 'formacion']
    }
    rename_final = {}
    for standard_name, possible_names in column_mapping.items():
        for name in possible_names:
            if name in lower_case_map:
                rename_final[lower_case_map[name]] = standard_name
                break
    df.rename(columns=rename_final, inplace=True)

    # --- Procesamiento de datos ---
    if 'EQUIPO' not in df.columns:
        df['EQUIPO'] = 'N/A'
    df['EQUIPO'].fillna('N/A', inplace=True)

    df["Clip Start"] = pd.to_numeric(df["Clip Start"], errors='coerce')
    df["Clip End"] = pd.to_numeric(df["Clip End"], errors='coerce')
    df.dropna(subset=["Clip Start", "Clip End"], inplace=True)
    df["duracion"] = (df["Clip End"] - df["Clip Start"]).round(0)

    if "URL" in df.columns and df["URL"].notna().any():
        df["video_id"] = df["URL"].str.strip().apply(extraer_video_id)
        st.success("✅ Se usaron URLs individuales del CSV.")
    else:
        # In demo mode, we can't ask for a URL, so we should handle this case
        # For now, let's assume the CSV will always have the URL
        pass

    st.session_state.df_original = df
    st.session_state.new_file_loaded = True
    st.session_state.dynamic_filters = {} # Reinicia los filtros para el nuevo archivo

def render_sidebar():
    with st.sidebar:
        st.divider()
        st.info("Esta es una versión de demostración con datos precargados.")

        if st.session_state.df_original is None:
            return

        # --- Filtros Dinámicos ---
        st.header("📊 Filtros Dinámicos")
        df = st.session_state.df_original
        
        if 'dynamic_filters' not in st.session_state:
            st.session_state.dynamic_filters = {}

        with st.expander("Aplicar filtros por columna", expanded=True):
            for col in sorted(df.columns):
                # Omitir columnas no filtrables
                if col in ['video_id', 'URL', 'Clip End']: 
                    continue

                # Filtro para columnas categóricas (texto con pocas opciones)
                if df[col].dtype == 'object' and df[col].nunique() > 1 and df[col].nunique() < 50:
                    options = df[col].dropna().unique().tolist()
                    try:
                        options.sort()
                    except TypeError:
                        pass 
                    
                    default = st.session_state.dynamic_filters.get(col, options)
                    st.session_state.dynamic_filters[col] = st.multiselect(f"Filtrar {col}", options, default=default)
                
                # Filtro para columnas numéricas
                elif pd.api.types.is_numeric_dtype(df[col].dtype) and df[col].nunique() > 1:
                    min_val, max_val = float(df[col].min()), float(df[col].max())
                    default = st.session_state.dynamic_filters.get(col, (min_val, max_val))
                    st.session_state.dynamic_filters[col] = st.slider(f"Rango {col}", min_val, max_val, value=default)

        # Aplicar filtros guardados en el estado
        df_filtrado = df.copy()
        for col, value in st.session_state.get('dynamic_filters', {}).items():
            if col not in df_filtrado.columns: continue
            
            if isinstance(value, list): # Filtro de Multiselect
                df_filtrado = df_filtrado[df_filtrado[col].isin(value)]
            elif isinstance(value, tuple): # Filtro de Slider
                df_filtrado = df_filtrado[df_filtrado[col].between(value[0], value[1])]
        
        st.session_state.df_filtrado = df_filtrado

        st.divider()
        st.header("👁️ Columnas Visibles")
        all_columns = df.columns.tolist()

        if st.session_state.get('new_file_loaded', False):
            st.session_state.columnas_visibles = all_columns
            st.session_state.new_file_loaded = False

        st.session_state.columnas_visibles = st.multiselect(
            "Selecciona columnas a mostrar",
            options=all_columns,
            default=st.session_state.get('columnas_visibles', all_columns)
        )

def render_aggrid(height=400):
    """Muestra la tabla de clips interactiva y maneja la selección y edición."""
    df_display = st.session_state.df_filtrado.copy()

    if df_display.empty:
        st.info("No hay clips para mostrar con los filtros actuales.")
        return

    columnas_visibles = st.session_state.get('columnas_visibles', [])
    if not columnas_visibles:
        st.warning("👈 Selecciona al menos una columna para mostrar.")
        return

    df_display_final = df_display[columnas_visibles]
    
    gb = GridOptionsBuilder.from_dataframe(df_display_final)
    gb.configure_selection("multiple", use_checkbox=True, header_checkbox=True)
    
    # Permitir edición en todas las columnas visibles
    for col in columnas_visibles:
        gb.configure_column(col, editable=True)

    grid_options = gb.build()
    grid_response = AgGrid(
        df_display_final, 
        gridOptions=grid_options, 
        update_mode=GridUpdateMode.MODEL_CHANGED, 
        theme="streamlit", 
        height=height,
        key="aggrid_data_base",
        reload_data=False
    )
    
    st.session_state.clips_seleccionados = pd.DataFrame(grid_response.get("selected_rows", []))
    
    if grid_response['data'] is not None:
        df_updated_view = pd.DataFrame(grid_response['data'])
        if len(df_updated_view) == len(df_display_final):
            df_updated_view.index = df_display_final.index
            st.session_state.df_original.update(df_updated_view)
            st.session_state.df_filtrado.update(df_updated_view)


def render_player_frame(clip_info: pd.Series, autoplay: bool = True):
    """Muestra el reproductor de video de YouTube para un clip específico."""
    video_id = clip_info.get("video_id")
    if not video_id:
        st.warning("No se pudo encontrar el ID del video para este clip.")
        return
    start_time = int(clip_info["Clip Start"])
    autoplay_param = "1" if autoplay else "0"
    embed_url = f"https://www.youtube.com/embed/{video_id}?start={start_time}&autoplay={autoplay_param}&rel=0"
    
    # Aumentamos la altura del reproductor para aprovechar mejor la pantalla
    player_height = 650 # Originalmente 450
    component_height = player_height + 20 # Espacio adicional para el componente

    st.components.v1.html(
        f'<div class="video-container"><iframe src="{embed_url}" width="100%" height="{player_height}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>',
        height=component_height
    )

# --- SECCIÓN DE GRÁFICOS DINÁMICOS ---

def render_event_frequency_chart(df):
    if 'Row Name' in df.columns and 'EQUIPO' in df.columns:
        st.markdown("#### Frecuencia de Eventos por Equipo")
        try:
            chart_data = df.groupby(['EQUIPO', 'Row Name']).size().unstack(fill_value=0)
            st.bar_chart(chart_data)
            st.caption("Muestra el número de veces que ocurre cada evento, agrupado por equipo.")
        except Exception as e:
            st.warning(f"No se pudo generar el gráfico de frecuencia: {e}")
        st.divider()

def render_result_distribution_chart(df):
    if 'RESULTADO' in df.columns and 'EQUIPO' in df.columns:
        st.markdown("#### Distribución de Resultados por Equipo")
        df_chart = df.dropna(subset=['RESULTADO'])
        if not df_chart.empty:
            try:
                chart_data = df_chart.groupby(['EQUIPO', 'RESULTADO']).size().unstack(fill_value=0)
                st.bar_chart(chart_data)
                st.caption("Muestra la cantidad de resultados (ej: GANO, PERDIO) para cada equipo.")
            except Exception as e:
                st.warning(f"No se pudo generar el gráfico de resultados: {e}")
        else:
            st.info("No hay datos en la columna 'RESULTADO' para graficar.")
        st.divider()

def render_lineout_charts(df):
    if 'Row Name' in df.columns and df['Row Name'].str.contains('LINEOUT', case=False, na=False).any():
        lineout_df = df[df['Row Name'].str.contains('LINEOUT', case=False, na=False)].copy()
        st.markdown("### Análisis de Lineouts")

        if 'FORM' in lineout_df.columns:
            st.markdown("##### Formaciones de Lineout")
            form_counts = lineout_df['FORM'].value_counts()
            if not form_counts.empty:
                st.bar_chart(form_counts)
                st.caption("Frecuencia de las formaciones ('FORM') en los lineouts.")
            else:
                st.info("No hay datos en 'FORM' para los lineouts.")

        if 'JUGADOR' in lineout_df.columns and 'RESULTADO' in lineout_df.columns:
            st.markdown("##### Jugadores con más Lineouts Ganados")
            won_lineouts = lineout_df[lineout_df['RESULTADO'].str.contains('GANO|WIN', case=False, na=False)]
            if not won_lineouts.empty:
                player_wins = won_lineouts['JUGADOR'].value_counts()
                if not player_wins.empty:
                    st.bar_chart(player_wins)
                    st.caption("Número de lineouts ganados por jugador.")
                else:
                    st.info("No se encontraron lineouts ganados.")
            else:
                st.info("No hay datos de lineouts con resultado 'GANO' o 'WIN'.")
        st.divider()

def render_analysis_section():
    """Muestra el expander con gráficos dinámicos y contexto."""
    df_filtrado = st.session_state.get("df_filtrado", pd.DataFrame())

    with st.expander("📊 Gráficos y Contexto del Análisis", expanded=False):
        st.subheader("📝 Añadir Contexto al Análisis")
        st.session_state.data_context = st.text_area(
            "Añade aquí tus notas o el contexto del análisis (ej: 'Análisis del lineout de NZ vs FRA')",
            value=st.session_state.get("data_context", ""),
            height=100,
            key="data_context_input"
        )
        st.divider()
        st.subheader("📈 Gráficos de Análisis")

        if df_filtrado.empty:
            st.info("Carga y filtra datos para ver los gráficos.")
            return

        render_event_frequency_chart(df_filtrado)
        render_result_distribution_chart(df_filtrado)
        render_lineout_charts(df_filtrado)

# --- VISTA PRINCIPAL ---

def render_main_view():
    """Renderiza la vista principal que contiene el reproductor y la tabla."""
    
    st.info("Selecciona clips en la tabla de abajo y usa los botones para crear y reproducir una playlist.")
    
    render_aggrid()

    clips_seleccionados = st.session_state.get("clips_seleccionados", pd.DataFrame())
    is_playlist_empty = clips_seleccionados.empty

    # --- Lógica de validación para el índice de la playlist ---
    if st.session_state.get("playlist_active", False):
        # Si la selección de clips queda vacía, detener la playlist
        if is_playlist_empty:
            st.session_state.playlist_active = False
            st.warning("La playlist se detuvo porque no hay clips seleccionados.")
            st.rerun()
        # Si el índice actual está fuera de los límites de la nueva selección, reiniciarlo a 0
        elif st.session_state.playlist_index >= len(clips_seleccionados):
            st.session_state.playlist_index = 0
            st.info("La selección de clips cambió. La playlist continuará desde el inicio de la nueva selección.")

    # --- Controles de la Playlist ---
    cols = st.columns([1.5, 1, 1, 1, 1.5, 2])

    if cols[0].button("▶️ Iniciar Playlist", disabled=is_playlist_empty):
        st.session_state.playlist_active = True
        st.session_state.playlist_index = 0
        st.rerun()

    if cols[1].button("⏪ Anterior", disabled=not st.session_state.playlist_active):
        if st.session_state.playlist_index > 0:
            st.session_state.playlist_index -= 1
            st.rerun()

    if cols[2].button("⏩ Próximo", disabled=not st.session_state.playlist_active):
        if st.session_state.playlist_index < len(clips_seleccionados) - 1:
            st.session_state.playlist_index += 1
            st.rerun()

    if cols[3].button("🛑 Detener", disabled=not st.session_state.playlist_active):
        st.session_state.playlist_active = False
        st.rerun()

    if st.session_state.playlist_active and not is_playlist_empty:
        cols[5].info(f"**Clip {st.session_state.playlist_index + 1} de {len(clips_seleccionados)}**")

    # --- Reproductor de Video ---
    if st.session_state.playlist_active and not is_playlist_empty:
        # El índice ya ha sido validado, por lo que esta línea ahora es segura
        clip_to_show = clips_seleccionados.iloc[st.session_state.playlist_index]
        
        title_cols = [c for c in ["Row Name", "EQUIPO", "JUGADOR", "RESULTADO"] if c in clip_to_show]
        st.markdown(f"### " + " | ".join([str(clip_to_show[c]) for c in title_cols]))
        
        render_player_frame(clip_to_show, autoplay=True)
    
    st.divider()
    render_analysis_section()


# --- APLICACIÓN PRINCIPAL ---

def run_data_base_demo_page():
    st.markdown('''
        <style>
            .block-container { padding-top: 2rem; }
            .video-container { margin: auto; max-width: 900px; padding-top: 10px; }
        </style>
    ''', unsafe_allow_html=True)

    st.title("📊 Base de Datos y Análisis Interactivo (DEMO)")

    with st.expander("ℹ️ Ayuda y Estructura de Datos"):
        st.markdown('''
        Esta es una versión de demostración de la aplicación.
        - **Datos Precargados**: Los datos se cargan desde un archivo CSV de ejemplo.
        - **Filtra y Analiza**: Usa los filtros en la barra lateral para explorar tus datos. Los gráficos se actualizarán dinámicamente.
        - **Crea una Playlist**: Selecciona filas en la tabla para crear una playlist de video.
        ''')
    
    inicializar_estado()
    if st.session_state.df_original is None:
        load_demo_data()
    
    render_sidebar()

    if st.session_state.df_original is None:
        st.info("No se pudieron cargar los datos de demostración.")
    else:
        render_main_view()
