import streamlit as st
import re
import urllib.parse
from yt_dlp import YoutubeDL

def limpiar_url_youtube(url):
    """Limpia la URL de YouTube para quitar parámetros innecesarios."""
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    video_id = query.get("v", [None])[0]
    if not video_id and parsed.netloc == "youtu.be":
        video_id = parsed.path.strip("/")
    return f"https://www.youtube.com/watch?v={video_id}" if video_id else url

def obtener_info_video(video_url):
    """Obtiene la información y el enlace de descarga directo del video."""
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return info

def run_links_youtube_page():
    """Función principal de la página de Streamlit."""
    st.title("🎬 Obtener Enlace de Descarga de YouTube")
    st.warning(
        "**Atención:** Debido a las limitaciones de memoria de la plataforma para archivos grandes, "
        "esta herramienta te proporcionará un **enlace de descarga directo**."
    )

    video_url = st.text_input("📎 URL del Video de YouTube", placeholder="https://www.youtube.com/watch?v=...")

    if st.button("🔗 Obtener Enlace de Descarga") and video_url:
        cleaned_url = limpiar_url_youtube(video_url)
        try:
            with st.spinner("Buscando video y enlace de descarga..."):
                info = obtener_info_video(cleaned_url)
                download_url = info.get('url')
                title = info.get('title', 'video')

                if download_url:
                    suggested_filename = f"{title}.mp4"

                    st.success("✅ ¡Enlace de descarga listo!")
                    st.markdown(f"#### Título del Video:")
                    st.markdown(f"> {title}")

                    st.markdown(f"#### Nombre de Archivo Sugerido (Paso 1: Copiar)")
                    st.code(suggested_filename, language="text")

                    st.divider()

                    st.markdown("#### Enlace de Descarga (Paso 2: Clic Derecho en el Botón)")
                    st.link_button("Descargar Video (Clic Derecho y Guardar)", download_url)

                    st.info(
                        "**Instrucciones Detalladas:**\n"
                        "1. **Copie** el `Nombre de Archivo Sugerido` de arriba.\n"
                        "2. **Haga clic derecho** en el botón de descarga de arriba y seleccione **`Guardar enlace como...`**.\n"
                        "3. En la ventana que aparece, **pegue** el nombre que copió en el campo 'Nombre de archivo'."
                    )
                    st.divider()
                    st.markdown("Si el video no se abre en QuickTime, **use VLC**.")
                    st.link_button("Descargar VLC", "https://www.videolan.org/")
                    st.warning("El enlace de descarga es temporal y expirará en unas horas.")
                else:
                    st.error("❌ No se pudo obtener un enlace de descarga directo. El video podría estar protegido o no estar disponible en un formato enlazable.")

        except Exception as e:
            st.error(f"❌ Error al procesar el video: {e}")

if __name__ == "__main__":
    run_links_youtube_page()