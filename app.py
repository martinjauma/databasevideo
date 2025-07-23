from streamlit_option_menu import option_menu
import streamlit as st

st.set_page_config(page_title="Data App", layout="wide")

with st.sidebar:
    selected_main = option_menu(
        menu_title="Menú Principal",
        options=["YouTube", "Fulcrum","LongoMatch"],
        icons=["youtube"],
        menu_icon="cast",
        default_index=0,
    )

if selected_main == "YouTube":
    st.markdown("##  Herramientas de YouTube")
    selected_youtube = option_menu(
        menu_title=None,
        options=["Links", "Data Base"],
        icons=["link", "list", "database"],
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
        options=["Piston HLS - MP4", "Angles"],
        icons=["link", "list", "database"],
        orientation="horizontal",
    )
    if selected_Fulcrum == "Piston HLS - MP4":
        exec(open("page/Fulcrum/Piston/piston.py").read())
    elif selected_Fulcrum == "Angles":
        exec(open("page/Fulcrum/Angles/composerToTimelineJson.py").read())

elif selected_main == "LongoMatch":
    exec(open("page/Longo_Match/xmltocsvjson.py").read())
