from streamlit_option_menu import option_menu
import streamlit as st
from modules.auth_google import login_required, render_user_info


st.set_page_config(page_title="Data App", layout="wide")

if 'video_data' not in st.session_state:
    st.session_state.video_data = None


# -- Autenticación Requerida --
login_required()

# -- Mostrar estado del registro en DB --
if 'db_log_status' in st.session_state:
    if st.session_state['db_log_status'] == "Success":
        st.toast("✅ Login registrado en DB.")
    elif st.session_state['db_log_status'] == "Error":
        st.error(f"Error al registrar en DB: {st.session_state['db_log_error']}")
    # Limpiar el estado para que el mensaje no se repita en cada recarga
    del st.session_state['db_log_status']
    if 'db_log_error' in st.session_state:
        del st.session_state['db_log_error']

current_user = st.user.name or "usuario"  # nombre del usuario logueado



with st.sidebar:
    st.markdown(
        """
        <style>
            /* Target the stImage container directly within the sidebar */
            [data-testid="stSidebar"] [data-testid="stImage"] {
                margin-top: 0px !important;
                margin-bottom: 0px !important;
                padding-top: 0px !important;
                padding-bottom: 0px !important;
            }
            /* Target the image itself within the stImage container */
            [data-testid="stSidebar"] [data-testid="stImage"] img {
                width: 200px !important; /* Force width */
                height: auto !important; /* Maintain aspect ratio */
                display: block !important; /* Remove extra space below image */
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.sidebar.image("img/logo.png", width=100)
    st.divider()
    selected_main = option_menu(
        menu_title="Menú Principal",
        options=["YouTube", "Fulcrum","LongoMatch"],
        icons=["youtube"],
        menu_icon="cast",
        default_index=0,
    )
    st.divider()
    render_user_info()




if selected_main == "YouTube":
    st.markdown("##  Herramientas de YouTube")
    selected_youtube = option_menu(
        menu_title=None,
        options=["Data Base","Links"],
        icons=["database","link"],
        orientation="horizontal",
    )

    if selected_youtube == "Links":
        exec(open("page/YouTube/Links_YouTube.py").read())

    # elif selected_youtube == "Playlist":
    #     exec(open("page/YouTube/Playlist_YouTube.py").read())

    elif selected_youtube == "Data Base":
        exec(open("page/YouTube/Data_Base.py").read())

elif selected_main == "Fulcrum":
    st.markdown("##  Herramientas de YouTube")
    selected_Fulcrum = option_menu(
        menu_title=None,
        options=["Angles", "Piston HLS - MP4"],
        icons=["link", "list"],
        orientation="horizontal",
    )
    if selected_Fulcrum == "Piston HLS - MP4":
        exec(open("page/Fulcrum/Piston/piston.py").read())
    elif selected_Fulcrum == "Angles":
        exec(open("page/Fulcrum/Angles/composerToTimelineJson.py").read())

elif selected_main == "LongoMatch":
    exec(open("page/Longo_Match/xmltocsvjson.py").read())