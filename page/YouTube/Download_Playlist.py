
import streamlit as st
import subprocess
import os
import shutil

def run_download_playlist_page():
    st.title("Descargar Playlist de YouTube")

    # Input for the YouTube playlist URL
    playlist_url = st.text_input("Introduce la URL de la Playlist de YouTube")

    # Button to start the download
    if st.button("Descargar Playlist"):
        if playlist_url:
            try:
                st.info("Iniciando la descarga... Esto puede tardar un momento.")
                
                # Define the download directory
                download_path = os.path.join(os.path.expanduser("~"), "Downloads")
                if not os.path.exists(download_path):
                    os.makedirs(download_path)

                st.info(f"Los archivos se descargarán en: {download_path}")

                # Construct the yt-dlp command
                command = [
                    "yt-dlp",
                    "--verbose",
                    "--ignore-errors",
                    "--force-overwrites",
                    "--rm-cache-dir",
                    "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
                    "-f", "best",
                    "-o", f"{download_path}/%(playlist_index)s-%(title)s.%(ext)s",
                    playlist_url
                ]

                # Execute the command
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8')

                # Display the output in real-time
                with st.expander("Ver registro de descarga"):
                    while True:
                        output = process.stdout.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            st.text(output.strip())
                
                process.wait()

                st.success("¡Proceso de descarga finalizado!")
                if os.path.exists(download_path):
                    st.subheader("Videos descargados:")
                    downloaded_files = os.listdir(download_path)
                    if downloaded_files:
                        for file in downloaded_files:
                            st.write(file)
                    else:
                        st.warning("No se encontraron archivos en la carpeta de descargas.")
                else:
                    st.error(f"La carpeta de descargas no existe: {download_path}")

            except Exception as e:
                st.error(f"Ha ocurrido un error: {e}")
        else:
            st.warning("Por favor, introduce una URL de la playlist.")
