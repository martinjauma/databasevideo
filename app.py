import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
from modules.auth_google import login_required, render_user_info, check_subscription_status, grant_subscription
import mercadopago

st.set_page_config(page_title="Data App", layout="wide")

if 'video_data' not in st.session_state:
    st.session_state.video_data = None

def show_payment_page():
    st.title("Suscripción Requerida")
    st.markdown("### Para acceder a la aplicación, por favor, elige un plan de suscripción.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Pagar en Pesos Argentinos (ARS)")
        if st.button("Suscribirse con Mercado Pago"):
            # Configurar Mercado Pago
            sdk = mercadopago.SDK(st.secrets["MERCADOPAGO_ACCESS_TOKEN"])

            # Crear la preferencia de pago
            preference_data = {
                "items": [
                    {
                        "title": "Suscripción Mensual",
                        "quantity": 1,
                        "unit_price": 1500,
                        "currency_id": "ARS",
                    }
                ],
                "back_urls": {
                    "success": "https://dbvideo.streamlit.app/",
                    "failure": "https://dbvideo.streamlit.app/",
                    "pending": "https://dbvideo.streamlit.app/",
                },
                "auto_return": "approved",
            }

            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]
            st.markdown(f'<meta http-equiv="refresh" content="0; url={preference["init_point"]}"> ', unsafe_allow_html=True)


    with col2:
        st.subheader("Pagar en Dólares (USD)")
        st.button("Suscribirse con Tarjeta (Stripe)", disabled=True)

    st.markdown("--- ")
    st.button("🏃‍♂️‍➡️ Cerrar sesión", on_click=st.logout)

def show_main_app():
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
            from page.YouTube.Links_YouTube import run_links_youtube_page
            run_links_youtube_page()

        elif selected_youtube == "Data Base":
            from page.YouTube.Data_Base import run_data_base_page
            run_data_base_page()

    elif selected_main == "Fulcrum":
        st.markdown("##  Herramientas de YouTube")
        selected_Fulcrum = option_menu(
            menu_title=None,
            options=["Angles", "Piston HLS - MP4"],
            icons=["link", "list"],
            orientation="horizontal",
        )
        if selected_Fulcrum == "Piston HLS - MP4":
            from page.Fulcrum.Piston.piston import run_piston_page
            run_piston_page()
        elif selected_Fulcrum == "Angles":
            exec(open("page/Fulcrum/Angles/composerToTimelineJson.py").read(), globals(), locals())

    elif selected_main == "LongoMatch":
        from page.Longo_Match.xmltocsvjson import run_xml_to_csv_json_page
        run_xml_to_csv_json_page()

# -- Autenticación Requerida --
login_required()

# Verificar si el pago fue aprobado
query_params = st.query_params
if query_params.get("status") == "approved":
    if grant_subscription(st.user.email):
        st.success("¡Pago aprobado! Tu acceso ha sido activado.")
        st.balloons()
        st.rerun()
    else:
        st.error("Hubo un error al activar tu suscripción. Por favor, contacta a soporte.")

# Verificar estado de la suscripción
subscription_status = check_subscription_status(st.user.email)

if subscription_status == "active":
    show_main_app()
else:
    show_payment_page()