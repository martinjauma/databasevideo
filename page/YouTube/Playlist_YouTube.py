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
    if "youtube_url" not in st.session_state:
        st.session_state.youtube_url = "https://www.youtube.com/watch?v=XNaqqZNJUMc"
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

def render_sidebar():
    with st.sidebar:
        st.divider()
        st.subheader("Cargar CSV y URL de YouTube")
        st.session_state.youtube_url = st.text_input("🔗 URL YouTube", value=st.session_state.youtube_url)

        uploaded_file = st.file_uploader("📂 Cargar CSV", type=["csv"])
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file, sep=None, engine="python")
                
                # --- Lógica de mapeo de columnas flexible y insensible a mayúsculas ---
                
                # 1. Normalizar columnas del CSV (quitar espacios)
                original_cols = {col.strip(): col for col in df.columns}
                df.rename(columns={v: k for k, v in original_cols.items()}, inplace=True)
                
                # 2. Crear un mapa de columnas en minúsculas para la búsqueda
                lower_case_map = {col.lower(): col for col in df.columns}

                # 3. Definir los mapeos estándar -> posibles variantes (en minúsculas)
                column_mapping = {
                    'Row Name': ['row name', 'code'],
                    'Clip Start': ['clip start', 'start'],
                    'Clip End': ['clip end', 'stop', 'end'], # 'end' añadido
                    'EQUIPO': ['equipo']
                }

                rename_final = {}
                missing_columns = []

                # 4. Encontrar las columnas y preparar el renombrado
                for standard_name, possible_names in column_mapping.items():
                    found = False
                    for name in possible_names:
                        if name in lower_case_map:
                            original_name = lower_case_map[name]
                            rename_final[original_name] = standard_name
                            found = True
                            break
                    if not found:
                        missing_columns.append(standard_name)
                
                # 5. Validar si falta alguna columna obligatoria
                required_columns = ['Row Name', 'Clip Start', 'Clip End']
                missing_required = [col for col in required_columns if col in missing_columns]

                if missing_required:
                    st.error(f"❌ Faltan columnas obligatorias. Asegúrate de que tu CSV contenga: {', '.join(missing_required)}")
                    return

                # 6. Aplicar el renombrado para las columnas encontradas
                df.rename(columns=rename_final, inplace=True)

                # 7. Manejar la columna opcional 'EQUIPO'
                if 'EQUIPO' not in df.columns:
                    df['EQUIPO'] = 'N/A' # Añadir valor por defecto
                    st.warning("⚠️ Columna 'EQUIPO' no encontrada. Se añadió un valor por defecto ('N/A') que puedes editar en la tabla.")

                # Rellenar valores nulos en EQUIPO por si el CSV los tuviera
                df['EQUIPO'].fillna('N/A', inplace=True)

                # --- Fin de la lógica de mapeo ---

                df["Clip Start"] = pd.to_numeric(df["Clip Start"], errors='coerce')
                df["Clip End"] = pd.to_numeric(df["Clip End"], errors='coerce')
                df.dropna(subset=["Clip Start", "Clip End"], inplace=True)
                df["duracion"] = (df["Clip End"] - df["Clip Start"]).round(0)

                video_id = extraer_video_id(st.session_state.youtube_url)
                df["video_id"] = video_id
                st.success("✅ Se usó la URL general de YouTube.")

                st.session_state.df_original = df
                st.success("✅ CSV cargado.")
            except Exception as e:
                st.error(f"❌ Error al procesar el CSV: {e}")
                return

        if st.session_state.df_original is None:
            return

        st.header("📊 Filtros")
        df = st.session_state.df_original
        equipos = st.multiselect("Equipos", options=df["EQUIPO"].unique(), default=df["EQUIPO"].unique())
        eventos = st.multiselect("Eventos", options=df["Row Name"].unique())

        df_filtrado = df[df["EQUIPO"].isin(equipos)]
        if eventos:
            df_filtrado = df_filtrado[df_filtrado["Row Name"].isin(eventos)]
        st.session_state.df_filtrado = df_filtrado
        
        st.divider()
        st.header("👁️ Columnas Visibles")
        all_columns = df.columns.tolist()
        
        default_cols_to_check = ["Row Name", "EQUIPO", "RESULTADO", "Clip Start", "duracion"]
        default_selection = [col for col in default_cols_to_check if col in all_columns]

        if 'columnas_visibles' not in st.session_state or not st.session_state.columnas_visibles:
            st.session_state.columnas_visibles = default_selection

        st.session_state.columnas_visibles = st.multiselect(
            "Selecciona las columnas a mostrar en la tabla",
            options=all_columns,
            default=st.session_state.columnas_visibles
        )

        # Guardar última selección manual sin refrescar el frame
        if not st.session_state.get("playlist_active"):
            if "last_selected_index" not in st.session_state:
                st.session_state["last_selected_index"] = None
            if not st.session_state.get("clips_seleccionados", pd.DataFrame()).empty:
                last_index = st.session_state.clips_seleccionados.index[-1]
                st.session_state.last_selected_index = last_index
            else:
                st.session_state.last_selected_index = None


def render_aggrid(height=300):
    """Muestra la tabla de clips interactiva y maneja la selección y edición."""
    if st.session_state.playlist_active:
        df_display = st.session_state.clips_seleccionados.copy()
    else:
        df_display = st.session_state.df_filtrado.copy()

    if df_display.empty:
        st.info("No hay clips para mostrar.")
        return

    columnas_visibles = st.session_state.get('columnas_visibles', [])
    if not columnas_visibles:
        st.warning("👈 Desde la barra lateral, selecciona al menos una columna para mostrar en la tabla.")
        return

    # Crea un nuevo DataFrame solo con las columnas visibles para evitar errores
    df_display_final = pd.DataFrame(index=df_display.index)
    for col in columnas_visibles:
        if col in df_display.columns:
            df_display_final[col] = df_display[col]
        else:
            df_display_final[col] = "N/A" # Añade la columna con N/A si no existe
    
    if "Clip Start" in df_display_final.columns:
        df_display_final["Clip Start"] = pd.to_numeric(df_display_final["Clip Start"], errors='coerce').round(0)

    # Columnas editables deben estar presentes en el grid para que la edición funcione
    editable_cols = ["Row Name", "EQUIPO"]
    
    gb = GridOptionsBuilder.from_dataframe(df_display_final)
    
    if st.session_state.playlist_active:
        gb.configure_selection("single", use_checkbox=False)
        gb.configure_grid_options(onRowClicked=JsCode('''
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
        '''
))
    else:
        # Configurar edición y selección para la tabla principal
        gb.configure_selection("multiple", use_checkbox=True, header_checkbox=True, pre_selected_rows=st.session_state.clips_seleccionados.index.tolist())
        for col in editable_cols:
            if col in df_display_final.columns:
                 gb.configure_column(col, editable=True)


    grid_options = gb.build()
    grid_response = AgGrid(
        df_display_final, 
        gridOptions=grid_options, 
        update_mode=GridUpdateMode.MODEL_CHANGED, 
        theme="streamlit", 
        height=height, 
        allow_unsafe_jscode=True, 
        key="aggrid_clips",
        reload_data=False 
    )

    if st.session_state.playlist_active:
        if grid_response.get("component_value"):
            selected_row_data = grid_response["component_value"]
            clips_df = st.session_state.clips_seleccionados
            if not clips_df.empty:
                # Para encontrar el índice correcto, usamos las columnas visibles que definen unívocamente la fila
                key_cols = [c for c in ["Row Name", "EQUIPO", "Clip Start"] if c in clips_df.columns]
                
                match_conditions = True
                for col in key_cols:
                    if col == "Clip Start":
                        match_conditions &= (clips_df[col].round(0) == selected_row_data[col])
                    else:
                        match_conditions &= (clips_df[col] == selected_row_data[col])

                match_index = clips_df[match_conditions].index
                
                if not match_index.empty:
                    st.session_state.playlist_index = match_index[0]
                    st.rerun()
    else:
        # Este bloque maneja la tabla principal (no la playlist)
        st.session_state.clips_seleccionados = pd.DataFrame(grid_response.get("selected_rows", []))
        
        if grid_response['data'] is not None:
            df_updated_view = pd.DataFrame(grid_response['data'])
            if len(df_updated_view) == len(df_display_final):
                df_updated_view.index = df_display_final.index
                st.session_state.df_original.update(df_updated_view)
                st.session_state.df_filtrado.update(df_updated_view)

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

def get_full_clip_details(clip_row: pd.Series) -> Optional[pd.Series]:
    """Busca los detalles completos de un clip en el DataFrame original."""
    df_original = st.session_state.df_original
    if df_original is None or clip_row.empty: return None
    
    # Usa un conjunto de claves para encontrar la fila, ya que las columnas pueden variar
    key_cols = [c for c in ["Row Name", "EQUIPO", "Clip Start"] if c in df_original.columns and c in clip_row.index]
    
    match_conditions = True
    for col in key_cols:
        if col == "Clip Start":
            match_conditions &= (df_original[col].round(0) == round(clip_row[col], 0))
        else:
            match_conditions &= (df_original[col] == clip_row[col])

    fila_completa = df_original[match_conditions]
    return fila_completa.iloc[0] if not fila_completa.empty else None

def render_analysis_section():
    """Muestra el expander con el gráfico y el área de texto para el contexto."""
    df_filtrado = st.session_state.get("df_filtrado", pd.DataFrame())

    with st.expander("📊 Gráficos y Contexto del Análisis"):
        st.subheader("📝 Añadir Contexto al Análisis")
        st.session_state.data_context = st.text_area(
            "Añade aquí tus notas o el contexto del análisis (ej: 'Análisis del lineout de NZ vs FRA')",
            value=st.session_state.get("data_context", ""),
            height=100,
            key="data_context_input"
        )

        st.subheader("📈 Frecuencia de Eventos por Equipo")
        
        if df_filtrado.empty:
            st.info("No hay datos filtrados para generar un gráfico.")
            return

        required_cols = ['Row Name', 'EQUIPO']
        if not all(col in df_filtrado.columns for col in required_cols):
            st.warning(f"Para generar el gráfico, el CSV debe contener las columnas: {', '.join(required_cols)}.")
            return
            
        try:
            chart_data = df_filtrado.groupby(['EQUIPO', 'Row Name']).size().reset_index(name='counts')
            pivot_df = chart_data.pivot(index='Row Name', columns='EQUIPO', values='counts').fillna(0)
            
            if not pivot_df.empty:
                st.bar_chart(pivot_df)
                st.caption("El gráfico muestra el número de veces que ocurre cada 'Evento' (Row Name), agrupado por 'Equipo'.")
            else:
                st.info("No hay suficientes datos para generar un gráfico con los filtros actuales.")
        except Exception as e:
            st.error(f"Ocurrió un error al generar el gráfico: {e}")

# --- VISTA PRINCIPAL UNIFICADA ---

def render_main_view():
    """Renderiza la vista principal que contiene el reproductor y la tabla."""

    expander_expanded = st.session_state.get("show_expander", True)

    with st.expander("📁 Lista de Clips", expanded=expander_expanded):
        render_aggrid()

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
            st.session_state.show_expander = True

    if clip_to_show is not None:
        resultado_str = f" | {clip_to_show['RESULTADO']}" if 'RESULTADO' in clip_to_show and pd.notna(clip_to_show['RESULTADO']) else ""
        st.markdown(f"### **{clip_to_show['Row Name']}** | {clip_to_show['EQUIPO']}{resultado_str}")
        render_player_frame(clip_to_show, autoplay=autoplay)
    else:
        st.info("Selecciona uno o más clips de la tabla para comenzar.")

    st.divider()

    clips = st.session_state.clips_seleccionados
    is_playlist_empty = clips.empty

    is_first_clip = st.session_state.playlist_index == 0
    is_last_clip = st.session_state.playlist_index >= len(clips) - 1

    cols = st.columns([1.5, 1, 1, 1, 1.5, 2])

    if cols[0].button("▶️ Iniciar Playlist", disabled=is_playlist_empty or st.session_state.playlist_active):
        st.session_state.playlist_active = True
        st.session_state.playlist_index = 0
        st.session_state.show_expander = False
        st.rerun()

    if cols[1].button("⏪ Anterior", disabled=not st.session_state.playlist_active or is_first_clip):
        st.session_state.playlist_index -= 1
        st.rerun()

    if cols[2].button("⏩ Próximo", disabled=not st.session_state.playlist_active or is_last_clip):
        st.session_state.playlist_index += 1
        st.rerun()

    if cols[3].button("🛑 Detener", disabled=not st.session_state.playlist_active):
        st.session_state.playlist_active = False
        st.session_state.show_expander = True
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

    st.divider()
    
    render_analysis_section()


# --- APLICACIÓN PRINCIPAL ---

def run_playlist_youtube_page():
    st.markdown('''
        <style>
            .block-container { padding-top: 2rem; }
            .video-container { margin: auto; max-width: 900px; padding-top: 10px; }
        </style>
    ''', unsafe_allow_html=True)

    st.title("▶️ Playlist de YouTube")

    with st.expander("ℹ️ Ayuda y Estructura de Datos"):
        st.markdown('''
        ### ¿Qué hace esta página?
        Esta aplicación te permite analizar clips de video a partir de un archivo CSV y una URL de YouTube.
        
        - **Carga y Visualiza**: Carga un archivo CSV con marcas de tiempo y metadatos de clips. La aplicación los mostrará en una tabla interactiva.
        - **Filtra y Selecciona**: Puedes filtrar los clips por equipo o evento y seleccionar los que te interesen usando las casillas de verificación.
        - **Crea una Playlist**: Una vez seleccionados, puedes iniciar una playlist para ver los clips uno tras otro.
        - **Descarga**: Puedes descargar los datos de los clips que seleccionaste en un nuevo archivo CSV.

        ### Estructura del Archivo CSV
        Para que la aplicación funcione correctamente, el archivo CSV que subas debe tener una estructura específica y contener las siguientes columnas **obligatorias**:

        - **`Row Name`**: (Texto) El nombre o la descripción del clip/evento (ej: "Try Jugador X", "Defensa Lineout").
        - **`Clip Start`**: (Numérico) El segundo exacto en el que comienza el clip dentro del video de YouTube.
        - **`Clip End`**: (Numérico) El segundo exacto en el que termina el clip.
        - **`EQUIPO`**: (Texto) El nombre del equipo o la categoría a la que pertenece el clip.

        Opcionalmente, puedes incluir una columna `URL` si cada clip proviene de un video de YouTube diferente. Si no se proporciona, se usará la URL general ingresada en la barra lateral.
        ''')

        sample_csv_data = '''"Row Name","Clip Start","Clip End","EQUIPO","URL"
"Try Jugador A",10,25,"Equipo Rojo","ESTA COLUMNA ES OPCIONAL!, si este campo no se le proporciona un link de YouTube, se usará la URL de YouTube ingresada en la barra lateral para todos los clips."
"Try Jugador B",30,45,"Equipo Azul","https://www.youtube.com/watch?v=XNaqqZNJUMc"
"Falta Jugador C",70,80,"Equipo Rojo","https://www.youtube.com/watch?v=XNaqqZNJUMc"
"Defensa Lineout",50,65,"Equipo Azul"
"Scrum Ganado",120,130,"Equipo Rojo"
'''
        col1, col2 = st.columns([3,1])    
            
        with col1:    
            st.download_button(
                label="📥 Descargar CSV de Ejemplo con las columnas obligatorias",
                data=sample_csv_data.encode('utf-8'),
                file_name="ejemplo_clips.csv",
                mime="text/csv",
            )
        with col2:
            st.write(" ")
            st.markdown("[VIDEO TUTORIAL](https://youtu.be/yHZZbqonZ0Q)")

    inicializar_estado()
    render_sidebar()

    if st.session_state.df_original is None:
        st.info("👈 Comienza cargando un archivo CSV y una URL de YouTube en la barra lateral.")
    else:
        render_main_view()
