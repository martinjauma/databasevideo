import streamlit as st
import os
import tempfile
import glob
import re
import urllib.parse
from yt_dlp import YoutubeDL


# 🔧 LIMPIAR URL de YouTube (quita parámetros como &t=, ?si=...)
def limpiar_url_youtube(url):
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    video_id = query.get("v", [None])[0]

    if not video_id and parsed.netloc == "youtu.be":
        video_id = parsed.path.strip("/")

    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    return url


# 📥 FUNCION PARA DESCARGAR USANDO API yt_dlp
def descargar_video_con_api(video_url, output_path):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4][vcodec*=avc1]+bestaudio[acodec*=mp4a]/mp4',
        'merge_output_format': 'mp4',
        'outtmpl': output_path,
        'noplaylist': True,
        'quiet': False,
        'progress_hooks': [],
    }

    progreso = st.progress(0)
    texto = st.empty()

    # 🎯 Hook de progreso
    def progreso_hook(d):
        if d['status'] == 'downloading':
            porcentaje = d.get('_percent_str', '0.0%').replace('%', '').strip()
            try:
                porcentaje_float = float(porcentaje)
                progreso.progress(min(int(porcentaje_float), 100))
                texto.text(f"{int(porcentaje_float)}% descargado")
            except:
                pass
        elif d['status'] == 'finished':
            progreso.progress(100)
            texto.text("🎉 Descarga completa, procesando archivo...")

    ydl_opts['progress_hooks'].append(progreso_hook)

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


# 🚀 FUNCION PRINCIPAL DE STREAMLIT
def run_links_youtube_page():
    st.title("🎬 Descargar Video de YouTube")
    video_url = st.text_input("📎 URL del Video de YouTube", placeholder="https://www.youtube.com/watch?v=...")

    if st.button("📥 Descargar Video") and video_url:
        video_url = limpiar_url_youtube(video_url)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")

            try:
                descargar_video_con_api(video_url, output_template)

                # Buscar archivo descargado
                downloaded_files = glob.glob(os.path.join(tmpdir, "*.mp4"))
                if not downloaded_files:
                    st.error("❌ No se encontró el archivo descargado.")
                    return

                file_path = downloaded_files[0]
                filename = os.path.basename(file_path)

                with open(file_path, "rb") as f:
                    st.success("✅ Video listo para descargar.")
                    st.download_button("💾 Guardar Video", data=f, file_name=filename, mime="video/mp4")

            except Exception as e:
                st.error(f"❌ Error durante la descarga: {e}")


# ▶️ EJECUTAR
if __name__ == "__main__":
    run_links_youtube_page()
