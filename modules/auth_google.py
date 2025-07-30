# auth.py

import streamlit as st
from pymongo import MongoClient
import datetime

# Conexión a MongoDB
try:
    client = MongoClient(st.secrets["MONGO_URI"])
    db = client.login_logs # Nombre de la base de datos
    login_collection = db.saas_dbvideo # Nombre de la colección
except Exception as e:
    st.error(f"Error al conectar a MongoDB: {e}")
    st.stop()

def login_required():
    """
    Verifica si el usuario está logueado. Si no, muestra la pantalla de login.
    Llamar esto al inicio de cada app para forzar login antes de mostrar el contenido.
    """
    if not getattr(st.user, "is_logged_in", False):
        _show_login_screen()
        st.stop()  # Detiene la ejecución de la app si no está logueado
    else:
        _log_login_event(st.user.email)


def render_user_info():
    # st.header("👤 Usuario")
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.user.picture:
            st.image(st.user.picture, use_container_width=True)
    with col2:
        st.subheader(st.user.name)
        st.caption(st.user.email)
    st.button("🏃‍♂️‍➡️ Cerrar sesión", on_click=st.logout)

def _log_login_event(user_email):
    # Solo registrar el evento de login una vez por sesión.
    if "login_event_logged" not in st.session_state:
        try:
            login_data = {
                "timestamp": datetime.datetime.now(),
                "user_email": user_email
            }
            login_collection.insert_one(login_data)
            st.session_state['db_log_status'] = "Success"
        except Exception as e:
            st.session_state['db_log_status'] = "Error"
            st.session_state['db_log_error'] = str(e)
        finally:
            # Marcar que el intento de log ya se hizo, para no repetirlo.
            st.session_state["login_event_logged"] = True

def _show_login_screen():
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("🔐 Inicio de sesión requerido")
    st.subheader("Iniciá sesión con Google para continuar.")
    st.button("➡️ Iniciar sesión con Google", on_click=st.login, type="primary")

def grant_subscription(user_email):
    """Otorga una suscripción activa a un usuario, creándolo si no existe."""
    try:
        login_collection.update_one(
            {"user_email": user_email},
            {
                "$set": {
                    "subscription_status": "active",
                    "last_update": datetime.datetime.now()
                },
                "$setOnInsert": {
                    "user_email": user_email,
                    "signup_date": datetime.datetime.now()
                }
            },
            upsert=True
        )
        return True
    except Exception as e:
        st.error(f"Error al actualizar la base de datos: {e}")
        return False

def check_subscription_status(user_email):
    """Verifica si un usuario está en la lista de permitidos o tiene una suscripción activa."""
    
    # 1. Verificar si el usuario está en la lista de acceso gratuito
    allowed_users_str = st.secrets.get("ALLOWED_USERS", "")
    allowed_users = [email.strip() for email in allowed_users_str.split(",")]
    
    if user_email in allowed_users:
        return "active" # Acceso concedido para usuarios en la lista

    # 2. Si no está en la lista, verificar su estado de suscripción en la base de datos
    # (Esta es la lógica que se ejecutará para el público general)
    usuario = login_collection.find_one({"user_email": user_email})
    if usuario and usuario.get("subscription_status") == "active":
        return "active"
    
    # 3. Si no cumple ninguna condición, no tiene acceso
    return "inactive"