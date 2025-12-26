import streamlit as st

st.set_page_config(page_title="Debug Auth")
st.title("Prueba de Autenticación de Google")

st.write("Esta es una aplicación mínima para depurar `st.login()`.")
st.write("Utiliza la configuración de secretos de [connections.google_oauth] de tu app.")

# El botón que inicia el flujo de OAuth
st.login()

# st.user solo existe después de un login exitoso.
# Usamos getattr para evitar un error si st.user no existe.
user_info = getattr(st, "user", None)

if user_info:
    st.header("✅ ¡Login Exitoso!")
    st.write("Streamlit ha creado el objeto `st.user`. Su contenido es:")
    # Usamos st.json para un formato más limpio
    try:
        user_dict = {
            "name": user_info.name,
            "email": user_info.email,
            "picture": user_info.picture,
            "is_logged_in": user_info.is_logged_in,
        }
        st.json(user_dict)
    except Exception as e:
        st.error(f"No se pudo convertir st.user a diccionario: {e}")
        st.write(user_info)
else:
    st.info("Esperando el resultado del inicio de sesión...")
    st.write("Si el inicio de sesión falla, la aplicación podría reiniciarse o mostrar un error sin llegar aquí.")

