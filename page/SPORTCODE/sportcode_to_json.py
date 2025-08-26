
import streamlit as st
import zipfile
import tempfile
import os
import json
from collections import defaultdict

def run_sportcode_to_json_page():
    st.title("hudl SportsCode A Angles Json")

    uploaded_file = st.file_uploader("Subí un archivo .zip", type="zip")

    if uploaded_file:
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Guardar el archivo subido en el directorio temporal
                zip_path = os.path.join(temp_dir, uploaded_file.name)
                with open(zip_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Descomprimir el archivo zip
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                # Buscar la carpeta .SCPlaylist
                scplaylist_path = None
                for root, dirs, files in os.walk(temp_dir):
                    for d in dirs:
                        if d.endswith(".SCPlaylist"):
                            scplaylist_path = os.path.join(root, d)
                            break
                    if scplaylist_path:
                        break

                if scplaylist_path:
                    # Buscar el archivo Playlist.SCClips
                    playlist_scclips_path = os.path.join(scplaylist_path, "Playlist.SCClips")

                    if os.path.exists(playlist_scclips_path):
                        # Parsear el archivo .json
                        with open(playlist_scclips_path, 'r') as f:
                            data = json.load(f)

                        # Agrupar clips por originalGroupName
                        grouped_clips = defaultdict(list)
                        for item in data.get('playlist', {}).get('clips', []):
                            grouped_clips[item.get('originalGroupName', '')].append(item)

                        # Convertir a la estructura JSON deseada
                        rows = []
                        for group_name, clips in grouped_clips.items():
                            row_clips = []
                            for clip in clips:
                                qualifiers = []
                                for tag in clip.get('moment', {}).get('tags', []):
                                    qualifiers.append({
                                        "name": tag.get('key', ''),
                                        "category": tag.get('value', '')
                                    })
                                
                                row_clips.append({
                                    "time_start": clip.get('startTime', 0),
                                    "time_end": clip.get('endTime', 0),
                                    "qualifiers": {
                                        "qualifiers_array": qualifiers
                                    }
                                })
                            
                            rows.append({
                                "row_name": group_name,
                                "clips": row_clips
                            })

                        final_json = {
                            "data_version": 2,
                            "row_count": len(rows),
                            "show_rows_by_category": True,
                            "uuid_timeline": data.get('playlist', {}).get('uuid', ''),
                            "rows": rows
                        }

                        # Ofrecer la descarga del archivo JSON
                        json_string = json.dumps(final_json, indent=4)
                        st.download_button(
                            label="Descargar JSON",
                            file_name="Playlist.json",
                            mime="application/json",
                            data=json_string
                        )
                    else:
                        st.error("No se encontró el archivo Playlist.SCClips en la carpeta .SCPlaylist.")
                else:
                    st.error("No se encontró la carpeta .SCPlaylist en el ZIP.")

        except Exception as e:
            st.error(f"Ocurrió un error: {e}")
