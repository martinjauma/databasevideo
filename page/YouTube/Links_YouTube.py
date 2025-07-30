import streamlit as st
import subprocess
import json
import shutil
import os
import tempfile
import pandas as pd
import glob
import re


st.title("📥 Extraer URL de un canal de YouTube")
canal_input = st.text_input("📎 Canal de YouTube", placeholder="https://www.youtube.com/@unionargentinaderugby")

if st.button("📩 Obtener videos") and canal_input:
    yt_dlp = shutil.which("yt-dlp")
    if not yt_dlp:
        st.error("❌ yt-dlp no está instalado.")
        st.stop()

    result = subprocess.run(
        [yt_dlp, "--flat-playlist", "-J", canal_input],
        capture_output=True, text=True
    )

    if result.returncode != 0 or not result.stdout.strip():
        st.error("❌ Error al obtener los videos del canal.")
        st.code(result.stderr)
        st.stop()

    try:
        data = json.loads(result.stdout)
        videos = data.get("entries", [])
        df = pd.DataFrame([
            {
                "Título": v.get("title"),
                "URL": f"https://www.youtube.com/watch?v={v.get('id')}"
            } for v in videos if v.get("id")
        ])
        st.dataframe(df)
        st.download_button("📥 Descargar CSV", df.to_csv(index=False), file_name="videos_canal.csv", mime="text/csv")
    except Exception as e:
        st.error(f"❌ Error al procesar la información: {e}")

st.title("🎬 Descargar Video de YouTube con Progreso")
video_url = st.text_input("📎 URL del Video de YouTube", placeholder="https://www.youtube.com/watch?v=...")

if st.button("📥 Descargar Video") and video_url:
    yt_dlp = shutil.which("yt-dlp")
    if not yt_dlp:
        st.error("❌ yt-dlp no está instalado.")
        st.stop()

    with tempfile.TemporaryDirectory() as tmpdir:
        output_template = os.path.join(tmpdir, "%(title)s.%(ext)s")
        progress_bar = st.progress(0)
        progress_text = st.empty()

        try:
            # Comando para descarga con merge en MP4
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

