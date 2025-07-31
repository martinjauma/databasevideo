import streamlit as st
import subprocess
import shutil
import os
import tempfile
import glob
import re
import urllib.parse  # necesario para limpiar la URL


# 🔧 FUNCIÓN PARA LIMPIAR LINK DE YOUTUBE (quita &t=3s o ?si=... y admite youtu.be)
def limpiar_url_youtube(url):
    parsed = urllib.parse.urlparse(url)
    query = urllib.parse.parse_qs(parsed.query)
    video_id = query.get("v", [None])[0]

    # si es un link corto tipo https://youtu.be/xxxxx
    if not video_id and parsed.netloc == "youtu.be":
        video_id = parsed.path.strip("/")

    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    return url


def run_links_youtube_page():
    # --------------------------- DESCARGAR VIDEO CON PROGRESO ---------------------------
    st.title("🎬 Descargar Video de YouTube")
    video_url = st.text_input("📎 URL del Video de YouTube", placeholder="https://www.youtube.com/watch?v=...")

    if st.button("📥 Descargar Video") and video_url:
        yt_dlp = shutil.which("yt-dlp")
        if not yt_dlp:
            st.error("❌ yt-dlp no está instalado.")
            st.stop()

        # ✅ Limpiar la URL antes de usarla
        video_url = limpiar_url_youtube(video_url)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")
            progress_bar = st.progress(0)
            progress_text = st.empty()

            try:
                # Comando para descarga con codecs compatibles con QuickTime
                command = [
                    yt_dlp,
                    "-f", "bestvideo[ext=mp4][vcodec*=avc1]+bestaudio[acodec*=mp4a]/mp4",
                    "--merge-output-format", "mp4",
                    "-o", output_template,
                    video_url
                ]

                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )

                for line in process.stdout:
                    # ✅ Solo mostrar progreso, no logs técnicos
                    match = re.search(r'\[download\]\s+(\d+\.\d+)%', line)
                    if match:
                        percent = float(match.group(1))
                        progress_bar.progress(min(int(percent), 100))
                        progress_text.text(f"{int(percent)}% descargado")

                process.wait()

                if process.returncode != 0:
                    st.error("❌ Error durante la descarga.")
                    st.stop()

                # Buscar archivo descargado
                downloaded_files = glob.glob(os.path.join(tmpdir, "*.mp4"))
                if not downloaded_files:
                    st.error("❌ No se encontró el archivo descargado.")
                    st.stop()

                file_path = downloaded_files[0]
                filename = os.path.basename(file_path)

                with open(file_path, "rb") as f:
                    st.success("✅ Video listo para descargar.")
                    st.download_button("💾 Guardar Video", data=f, file_name=filename, mime="video/mp4")

            except Exception as e:
                st.error(f"❌ Error: {e}")

