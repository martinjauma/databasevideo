import streamlit as st
import mercadopago
from modules.auth_google import login_required, render_user_info, check_subscription_status, grant_subscription

# Importar funciones de páginas
from page.YouTube.Links_YouTube import run_links_youtube_page
from page.YouTube.Data_Base import run_data_base_page
from page.YouTube.Channel_YouTube import run_channel_youtube_page # <-- IMPORTAMOS LA NUEVA PÁGINA
from page.Fulcrum.Piston.piston import run_piston_page
from page.Fulcrum.Angles.composerToTimelineJson import run_composer_to_timeline_page
from page.Longo_Match.xmltocsvjson import run_xml_to_csv_json_page

st.set_page_config(page_title="Data App", layout="wide")

# --- 1. INICIALIZACIÓN DE ESTADOS ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"
if 'redirect_after_payment' not in st.session_state:
    st.session_state.redirect_after_payment = None

# --- 2. AUTENTICACIÓN OBLIGATORIA ---
# Esta función detiene la ejecución y muestra la página de login si el usuario no está logueado.
login_required()

# --- 3. MANEJO DEL REGRESO DEL PAGO ---
# Si el usuario vuelve de Mercado Pago con un pago aprobado.
query_params = st.query_params
if query_params.get("status") == "approved":
    if grant_subscription(st.user.email):
        st.success("¡Pago aprobado! Tu acceso ha sido activado.")
        st.balloons()
        # Si habíamos guardado la página a la que quería ir, lo redirigimos allí.
        if st.session_state.redirect_after_payment:
            st.session_state.current_page = st.session_state.pop('redirect_after_payment')
        else:
            st.session_state.current_page = 'home' # Fallback por si acaso
        # Limpiamos los query params y re-ejecutamos para mostrar la página correcta.
        st.query_params.clear()
        st.rerun()
    else:
        st.error("Error al activar la suscripción. Contacta soporte.")

# --- PÁGINA DE PAGO ---
def show_payment_page():
    # El logo, el botón de volver y la info de sesión ahora se manejan en la sidebar de show_main_app()
    st.title("Suscripción Requerida")
    st.markdown(f"### Para acceder a esta herramienta, necesitas una suscripción activa.")
    st.markdown("---")

    # Columnas para las opciones de pago
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Pagar en Pesos (ARS)")
        st.markdown("Acceso completo a todas las herramientas.")
        if st.button("Suscribirse con Mercado Pago", use_container_width=True, type="primary"):
            sdk = mercadopago.SDK(st.secrets["MERCADOPAGO_ACCESS_TOKEN"])
            preference_data = {
                "items": [{"title": "Suscripción Mensual", "quantity": 1, "unit_price": 100, "currency_id": "ARS"}],
                "back_urls": {"success": "https://dbvideo.streamlit.app/", "failure": "https://dbvideo.streamlit.app/", "pending": "https://dbvideo.streamlit.app/"},
                "auto_return": "approved",
            }
            preference_response = sdk.preference().create(preference_data)
            preference = preference_response["response"]
            st.markdown(f'<meta http-equiv="refresh" content="0; url={preference["init_point"]}">', unsafe_allow_html=True)
    with col2:
        st.subheader("Pagar en Dólares (USD)")
        st.markdown("Acceso completo a todas las herramientas.")
        st.button("Suscribirse con Stripe", disabled=True, use_container_width=True)

# --- LÓGICA DE NAVEGACIÓN AL HACER CLIC ---
def handle_card_click(page_name):
    is_admin = st.user.email in st.secrets["ADMINS"]
    # Corregimos la comprobación para que sea explícitamente "active"
    is_subscribed = check_subscription_status(st.user.email) == "active"

    if is_admin or is_subscribed:
        # Si tiene acceso, lo llevamos a la página de la herramienta.
        st.session_state.current_page = page_name
    else:
        # Si no tiene acceso, guardamos a dónde quería ir y lo mandamos a la página de pago.
        st.session_state.redirect_after_payment = page_name
        st.session_state.current_page = "payment"
    # st.rerun() # Se elimina porque es un callback y Streamlit lo hace automáticamente.

# --- PÁGINA PRINCIPAL Y ROUTER ---
def show_main_app():
    # -- Sidebar
    with st.sidebar:
        st.image("img/logo.png", width=200)
        st.divider()
        # Si no estamos en la home, muestra el botón para volver.
        if st.session_state.current_page != "home":
            if st.button("⬅️ Volver al Inicio", use_container_width=True):
                st.session_state.current_page = "home"
                st.session_state.redirect_after_payment = None
                st.rerun()
        # Si ya estamos en la home, muestra un botón desactivado como indicador.
        else:
            st.button("🏠 INICIO", disabled=True, use_container_width=True)
        st.divider()
        render_user_info()

    # -- Contenido Principal
    if st.session_state.current_page == "home":
        st.title("Bienvenido")
        st.subheader("Selecciona una herramienta para comenzar:")

        # CSS para estandarizar el tamaño del contenedor del logo (versión con clase personalizada)
        st.markdown("""
            <style>
            .logo-container {
                display: flex;
                justify-content: left;
                align-items: left;
                height: 20px;
                margin-bottom: 1rem;
            }
            .logo-container img {
                max-height: 5%;
                max-width: 5%;
                object-fit: contain;
            }
            </style>
        """, unsafe_allow_html=True)

        st.divider()

        cards = [
            {"title": "YouTube","subtitle": "PlayList de DataBase", "logo": "img/youtube_logo.png", "page": "youtube_database", "tutorial_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            {"title": "YouTube","subtitle": "Descargar Video por URL", "logo": "img/youtube_logo.png", "page": "youtube_links", "tutorial_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            {"title": "YouTube", "subtitle": "Extraer URLs de Canal","logo": "img/youtube_logo.png", "page": "youtube_channel", "tutorial_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            {"title": "LongoMatch","subtitle": "Convertir XML a CSV", "logo": "img/longomatch_logo.png", "page": "longo_match", "tutorial_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            {"title": "Fulcrum Angles", "subtitle": "Conv. Composer Standalone a Timeline","logo": "img/angles_logo.png", "page": "fulcrum_angles", "tutorial_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            {"title": "Fulcrum Piston", "subtitle": "Piston HLS a MP4", "logo": "img/piston_logo.png", "page": "piston_hls", "tutorial_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
        ]

        # Volvemos a 3 columnas
        cols = st.columns(3)
        for i, card in enumerate(cards):
            with cols[i % 3]:
                # Usamos un contenedor con borde para cada tarjeta
                with st.container(border=True):
                    # Fila superior con logo y título alineados
                    top_cols = st.columns([1, 2], vertical_alignment="center")
                    with top_cols[0]:
                        st.image(card["logo"], width=80)
                    with top_cols[1]:
                        st.subheader(card["title"])
                    st.text(card["subtitle"])
                    # Fila inferior con los botones
                    btn_cols = st.columns(2)
                    with btn_cols[0]:
                        st.button(
                            "Abrir",
                            use_container_width=True,
                            key=f"open_{card['page']}", # Clave única para el botón de abrir
                            on_click=handle_card_click,
                            args=(card['page'],)
                        )
                    with btn_cols[1]:
                        st.link_button(
                            "Tutorial",
                            card["tutorial_url"],
                            use_container_width=True
                        )

    # -- Router para mostrar la página/herramienta correcta
    elif st.session_state.current_page == "payment":
        show_payment_page()
    elif st.session_state.current_page == "youtube_database":
        run_data_base_page()
    elif st.session_state.current_page == "youtube_links":
        run_links_youtube_page()
    elif st.session_state.current_page == "youtube_channel": # <-- AÑADIMOS LA RUTA
        run_channel_youtube_page()
    elif st.session_state.current_page == "longo_match":
        run_xml_to_csv_json_page()
    elif st.session_state.current_page == "fulcrum_angles":
        run_composer_to_timeline_page(st.user.name)
    elif st.session_state.current_page == "piston_hls":
        run_piston_page()

# --- 4. EJECUCIÓN PRINCIPAL ---
# Siempre mostramos la app principal, el router interno se encarga del resto.
show_main_app()
