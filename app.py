import streamlit as st
import mercadopago
import time
from modules.auth_google import login_required, render_user_info, check_subscription_status

# Importar funciones de páginas
from page.YouTube.Links_YouTube import run_links_youtube_page
from page.YouTube.Data_Base import run_data_base_page
from page.YouTube.Channel_YouTube import run_channel_youtube_page
from page.Fulcrum.Piston.piston import run_piston_page
from page.Fulcrum.Angles.composerToTimelineJson import run_composer_to_timeline_page
from page.Longo_Match.xmltocsvjson import run_xml_to_csv_json_page

st.set_page_config(page_title="Data App", layout="wide")

# --- 1. INICIALIZACIÓN DE ESTADOS ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"
if 'payment_initiated' not in st.session_state:
    st.session_state.payment_initiated = False

# --- 2. AUTENTICACIÓN OBLIGATORIA ---
login_required()

# --- 3. DEFINICIÓN DE PÁGINAS ---

def show_payment_page():
    st.title("Suscripción Requerida")

    # Si el usuario ya fue enviado a Mercado Pago, mostramos la pantalla de verificación.
    if st.session_state.payment_initiated:
        st.info("Si ya has completado el pago, haz clic en el botón de abajo para verificar tu suscripción.")
        
        if st.button("✅ Ya completé mi pago, verificar ahora", use_container_width=True, type="primary"):
            with st.spinner("Verificando tu pago, por favor espera..."):
                # Sondeamos la BD durante 60 segundos
                for i in range(20):
                    if check_subscription_status(st.user.email) == "active":
                        st.success("¡Tu acceso ha sido activado con éxito!")
                        st.balloons()
                        time.sleep(2)
                        st.session_state.current_page = 'home'
                        st.session_state.payment_initiated = False # Reseteamos el estado
                        st.rerun()
                        return
                    time.sleep(3)
            
            # Si el bucle termina sin éxito
            st.error("Aún no hemos recibido la confirmación de tu pago.")
            st.warning("A veces puede tardar uno o dos minutos. Por favor, inténtalo de nuevo en un momento.")

        st.divider()
        if st.button("Volver a intentar el pago"):
            st.session_state.payment_initiated = False
            st.rerun()

    # Si el usuario no ha iniciado el pago, mostramos las opciones.
    else:
        st.markdown("### Para acceder a esta herramienta, necesitas una suscripción activa.")
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Pagar en Pesos (ARS)")
            st.markdown("Acceso completo a todas las herramientas.")
            
            # Mensaje de advertencia ANTES de redirigir
            with st.container(border=True):
                st.warning("⚠️ ¡Paso Final Importante!")
                st.markdown("""
                1.  Al hacer clic en 'Suscribirse', irás a la página segura de Mercado Pago.
                2.  Después de pagar, la página de Mercado Pago puede mostrar un error o simplemente decir 'listo'. **Esto es normal.**
                3.  Lo más importante: **Debes volver a esta pestaña.** Aquí aparecerá un botón verde para **verificar tu pago** y activar tu acceso instantáneamente.
                """)

            if st.button("Entendido, ir a Pagar con Mercado Pago", use_container_width=True, type="primary"):
                st.session_state.payment_initiated = True
                sdk = mercadopago.SDK(st.secrets["MERCADOPAGO_ACCESS_TOKEN"])
                preference_data = {
                    "items": [{"title": "Suscripción Mensual", "quantity": 1, "unit_price": 100, "currency_id": "ARS"}],
                    # Ya no dependemos de la URL de retorno, pero la dejamos por si acaso.
                    "back_urls": {"success": "https://dbvideo.streamlit.app/"},
                    "auto_return": "approved",
                }
                preference_response = sdk.preference().create(preference_data)
                preference = preference_response["response"]
                st.markdown(f'<meta http-equiv="refresh" content="0; url={preference["init_point"]}">', unsafe_allow_html=True)
                # Forzamos un rerun para que la interfaz se actualice al estado de "verificación"
                time.sleep(1) # Pequeña pausa para asegurar que la redirección se inicie
                st.rerun()
        with col2:
            st.subheader("Pagar en Dólares (USD)")
            st.markdown("Acceso completo a todas las herramientas.")
            st.button("Suscribirse con Stripe", disabled=True, use_container_width=True)

def handle_card_click(page_name):
    is_admin = st.user.email in st.secrets.get("ADMINS", [])
    is_subscribed = check_subscription_status(st.user.email) == "active"

    if is_admin or is_subscribed:
        st.session_state.current_page = page_name
    else:
        st.session_state.current_page = "payment"

# --- 4. PÁGINA PRINCIPAL Y ROUTER ---
def show_main_app():
    with st.sidebar:
        st.image("img/logo.png", width=200)
        st.divider()
        if st.session_state.current_page != "home":
            if st.button("⬅️ Volver al Inicio", use_container_width=True):
                st.session_state.current_page = "home"
                st.session_state.payment_initiated = False # Reseteamos por si acaso
                st.rerun()
        else:
            st.button("🏠 INICIO", disabled=True, use_container_width=True)
        st.divider()
        render_user_info()

    # --- Router Principal ---
    if st.session_state.current_page == "home":
        st.title("Bienvenido")
        st.subheader("Selecciona una herramienta para comenzar:")
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
            {"title": "YouTube","subtitle": "PlayList de Base de Datos", "logo": "img/youtube_logo.png", "page": "youtube_database", "tutorial_url": "https://www.youtube.com/watch?v=yHZZbqonZ0Q&t=4s"},
            {"title": "YouTube","subtitle": "Descargar Video por URL", "logo": "img/youtube_logo.png", "page": "youtube_links", "tutorial_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            {"title": "YouTube", "subtitle": "Extraer URLs de un Canal","logo": "img/youtube_logo.png", "page": "youtube_channel", "tutorial_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            {"title": "LongoMatch","subtitle": "Convertir XML a CSV", "logo": "img/longomatch_logo.png", "page": "longo_match", "tutorial_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            {"title": "Fulcrum Angles", "subtitle": "Convertir Composer Standalone a TimelineJson","logo": "img/angles_logo.png", "page": "fulcrum_angles", "tutorial_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
            {"title": "Fulcrum Piston", "subtitle": "Piston HLS a MP4", "logo": "img/piston_logo.png", "page": "piston_hls", "tutorial_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
        ]
        cols = st.columns(3)
        for i, card in enumerate(cards):
            with cols[i % 3]:
                with st.container(border=True):
                    top_cols = st.columns([1, 2], vertical_alignment="center")
                    with top_cols[0]:
                        st.image(card["logo"], width=80)
                    with top_cols[1]:
                        st.subheader(card["title"])
                    st.text(card["subtitle"])
                    btn_cols = st.columns(2)
                    with btn_cols[0]:
                        st.button(
                            "Abrir",
                            use_container_width=True,
                            key=f"open_{card['page']}",
                            on_click=handle_card_click,
                            args=(card['page'],)
                        )
                    with btn_cols[1]:
                        st.link_button(
                            "Tutorial",
                            card["tutorial_url"],
                            use_container_width=True
                        )
    elif st.session_state.current_page == "payment":
        show_payment_page()
    elif st.session_state.current_page == "youtube_database":
        run_data_base_page()
    elif st.session_state.current_page == "youtube_links":
        run_links_youtube_page()
    elif st.session_state.current_page == "youtube_channel":
        run_channel_youtube_page()
    elif st.session_state.current_page == "longo_match":
        run_xml_to_csv_json_page()
    elif st.session_state.current_page == "fulcrum_angles":
        run_composer_to_timeline_page(st.user.name)
    elif st.session_state.current_page == "piston_hls":
        run_piston_page()

# --- 5. EJECUCIÓN PRINCIPAL ---
show_main_app()