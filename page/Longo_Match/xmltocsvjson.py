import streamlit as st
import xml.etree.ElementTree as ET
import pandas as pd
import json


def run_xml_to_csv_json_page():
    st.title("Conversor de XML de LongoMatch a CSV/JSON")

    # 1. Widget para subir el archivo
    uploaded_file = st.file_uploader(
        "Elige un archivo XML de LongoMatch",
        type=["xml"]
    )

    # El resto del script solo se ejecuta si se ha subido un archivo
    if uploaded_file is not None:
        try:
            # Parsear el XML directamente desde el objeto subido
            tree = ET.parse(uploaded_file)
            root = tree.getroot()

            # Lista donde guardamos cada instancia
            instances = []

            # recorrer cada <instance>
            for inst in root.findall(".//instance"):
                row = {}
                row["ID"] = inst.find("ID").text
                row["start"] = inst.find("start").text
                row["end"] = inst.find("end").text
                row["code"] = inst.find("code").text
                
                # leer los labels dentro de cada instancia
                labels = inst.findall(".//label")
                for label in labels:
                    group = label.find("group").text
                    text = label.find("text").text
                    # para evitar columnas repetidas
                    row[group] = text
                
                instances.append(row)

            # Si no se encontraron instancias, mostrar un mensaje
            if not instances:
                st.warning("No se encontraron datos de instancias en el archivo XML.")
            else:
                st.success(f"✅ Se han procesado {len(instances)} instancias correctamente.")

                # pasar a DataFrame
                df = pd.DataFrame(instances)

                # Mostrar una vista previa de los datos
                st.subheader("Vista Previa de los Datos")
                st.dataframe(df)

                # --- Botones de Descarga ---
                st.subheader("Descargar Archivos")
                col1, col2 = st.columns(2)

                # 2. Botón para descargar el CSV
                csv_data = df.to_csv(index=False, encoding="utf-8-sig").encode('utf-8')
                with col1:
                    st.download_button(
                        label="📥 Descargar CSV",
                        data=csv_data,
                        file_name="output_longomatch.csv",
                        mime="text/csv",
                    )

                # 3. Botón para descargar el JSON
                json_data = json.dumps(instances, ensure_ascii=False, indent=2).encode('utf-8')
                with col2:
                    st.download_button(
                        label="📥 Descargar JSON",
                        data=json_data,
                        file_name="output_longomatch.json",
                        mime="application/json",
                    )

        except Exception as e:
            st.error(f"Ha ocurrido un error al procesar el archivo: {e}")