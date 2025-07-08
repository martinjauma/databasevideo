import subprocess
import json
import streamlit as st
import shutil

st.title("📥 Extraer videos de un canal de YouTube")
canal_input = st.text_input("📎 Canal de YouTube", placeholder="https://www.youtube.com/@unionargentinaderugby")

if st.button("📩 Obtener videos") and canal_input:
    yt_dlp_path = shutil.which("yt-dlp")
    
    if yt_dlp_path is None:
        st.error("❌ yt-dlp no está instalado o no se encuentra en el entorno.")
        st.stop()

    result = subprocess.run(
        [yt_dlp_path, "--flat-playlist", "-J", canal_input],
        capture_output=True, text=True
    )

    # ✅ Mostrar salida para debug
    st.text("STDOUT ↓↓↓")
    st.code(result.stdout[:1000])
    st.text("STDERR ↓↓↓")
    st.code(result.stderr[:1000])

    if result.returncode != 0:
        st.error("❌ yt-dlp lanzó un error.")
        st.stop()

    if not result.stdout.strip():
        st.error("❌ yt-dlp no devolvió contenido.")
        st.stop()

    try:
        datos = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        st.error(f"❌ Error al interpretar JSON: {e}")
        st.stop()

    videos = datos.get("entries", [])
    if not videos:
        st.warning("⚠️ No se encontraron videos en el canal.")
        st.stop()

    import pandas as pd
    df = pd.DataFrame([
        {
            "Título": video.get("title"),
            "URL": f"https://www.youtube.com/watch?v={video.get('id')}"
        }
        for video in videos if video.get("id")
    ])

    st.dataframe(df)
    st.download_button("📥 Descargar CSV", df.to_csv(index=False), file_name="videos_canal.csv", mime="text/csv")
