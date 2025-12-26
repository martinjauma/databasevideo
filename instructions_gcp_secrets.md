¡Claro! Aquí tienes los pasos precisos para encontrar tu `client_id` y `client_secret` en la Consola de Google Cloud, y para revisar tus URIs de redireccionamiento autorizadas.

**Paso a paso para revisar tus credenciales de Google OAuth 2.0:**

1.  **Ve a la Consola de Google Cloud:**
    *   Abre tu navegador y ve a: [https://console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)
    *   Asegúrate de haber iniciado sesión con la cuenta de Google correcta y de haber seleccionado el **proyecto** adecuado en el selector de proyectos (arriba a la izquierda, junto al logo de Google Cloud).

2.  **Identifica tus "ID de cliente de OAuth 2.0":**
    *   En la página "Credenciales", desplázate hacia abajo hasta la sección que dice "ID de cliente de OAuth 2.0". Deberías ver una entrada para tu aplicación de Streamlit (probablemente con el tipo "Aplicación web").

3.  **Abre los detalles de tu ID de cliente:**
    *   Haz clic en el nombre de tu "ID de cliente de OAuth 2.0" (por ejemplo, "Aplicación web 1" o el nombre que le hayas dado) para abrir su configuración detallada.

4.  **Encuentra tu `Client ID` y `Client Secret`:**
    *   En la parte superior de la página de detalles, verás dos campos:
        *   **ID de cliente:** Esta es tu `client_id`.
        *   **Secreto de cliente:** Esta es tu `client_secret`.
    *   **Copia estos valores con EXTREMA PRECISIÓN.** Asegúrate de no copiar espacios adicionales al principio o al final.

5.  **Revisa tus "URIs de redireccionamiento autorizadas":**
    *   Desplázate un poco más abajo en la misma página de detalles del "ID de cliente de OAuth 2.0".
    *   Busca la sección "URIs de redireccionamiento autorizadas".
    *   **Asegúrate de que estén presentes TODAS estas URIs:**
        *   `http://localhost:8501` (para tu desarrollo local, ya que Streamlit ahora parece que usa solo esto)
        *   `http://localhost:8501/oauth2callback` (para tu desarrollo local, ya que a veces parece que también lo usa o lo requería)
        *   `https://dbvideo.streamlit.app` (para tu despliegue en Streamlit Cloud, sin `/oauth2callback` al final)
        *   `https://dbvideo.streamlit.app/oauth2callback` (para tu despliegue en Streamlit Cloud, ya que nos dijiste que antes funcionaba así)
        *   `https://dbvideo.onrender.com/oauth2callback` (para tu despliegue en Render)
    *   Si alguna falta, añádela haciendo clic en "AÑADIR URI" y pegándola.
    *   **Guarda** cualquier cambio que hayas hecho en esta página haciendo clic en el botón "Guardar" en la parte inferior.

**Una vez que hayas verificado y copiado estos valores con absoluta precisión, vuelve a tu configuración de secretos en Streamlit Cloud y en Render (si aplica) y actualízalos.**

Recuerda que estamos asumiendo que el `client_id` y `client_secret` son la causa del objeto `st.user` incompleto. Asegurarse de que estos sean 100% correctos es crucial.