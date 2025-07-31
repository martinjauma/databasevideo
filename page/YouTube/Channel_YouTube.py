import streamlit as st
import subprocess
import json
import pandas as pd
import shutil

def run_channel_youtube_page():
    st.title("📥 Extraer URLs de un Canal de YouTube")
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
