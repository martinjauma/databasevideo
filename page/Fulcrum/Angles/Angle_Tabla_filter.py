import streamlit as st
import zipfile
import tempfile
import os
import re

# -------------------------------
# Funciones auxiliares
# -------------------------------

def extract_zip_to_temp(uploaded_file):
    """Descomprime el ZIP subido a un directorio temporal"""
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    return temp_dir

def find_vault(temp_dir):
    """Busca la carpeta .VAult en cualquier nivel dentro del ZIP (ignorando mayúsculas)"""
    for root, dirs, files in os.walk(temp_dir):
        for d in dirs:
            if d.lower().endswith(".avault"):  # <- ahora ignora mayúsculas
                return os.path.join(root, d)
    return None


def get_tables(vault_path):
    """Devuelve todas las tablas con su ruta interna"""
    tables = {}
    tables_root = os.path.join(vault_path, "Panels", "Tables and Matrices")
    if os.path.exists(tables_root):
        for table_dir in os.listdir(tables_root):
            table_path = os.path.join(tables_root, table_dir)
            split_info = os.path.join(table_path, "split view info.plist")
            if os.path.isdir(table_path) and os.path.exists(split_info):
                with open(split_info, 'r', encoding='utf-8') as f:
                    text = f.read()
                match = re.search(r"<key>split view name</key>\s*<string>(.*?)</string>", text)
                if match:
                    table_name = match.group(1)
                    tables[table_name] = table_path
    return tables

def get_teams_from_table(table_path):
    """Extrae los equipos según el patrón [RN]'EQUIPO - ...'"""
    teams = set()
    cells_dir = os.path.join(table_path, "CELLS DATA")
    if os.path.exists(cells_dir):
        for file in os.listdir(cells_dir):
            if file.endswith(".plist") and "all cells data" in file:
                with open(os.path.join(cells_dir, file), 'r', encoding='utf-8') as f:
                    text = f.read()
                matches = re.findall(r'\[RN\]"(.*?) - ', text)
                for m in matches:
                    teams.add(m.strip())
    return sorted(teams)

def replace_teams_in_table(table_path, replacements):
    """Reemplaza los nombres de equipos en el bloque [RN] solo antes del guion"""
    cells_dir = os.path.join(table_path, "CELLS DATA")
    if os.path.exists(cells_dir):
        for file in os.listdir(cells_dir):
            if file.endswith(".plist") and "all cells data" in file:
                file_path = os.path.join(cells_dir, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                for old, new in replacements.items():
                    text = re.sub(rf'(\[RN\]"){old}(?= - )', rf'\1{new}', text)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)

def zip_vault(vault_path, output_zip):
    """Crea un ZIP con la carpeta .VAult"""
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(vault_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(vault_path))
                zipf.write(file_path, arcname)

# -------------------------------
# Interfaz Streamlit
# -------------------------------

def run_angle_tabla_filter_page():
    st.title("⚡ Editor de equipos en archivos .VAult dentro de ZIP")

    uploaded_file = st.file_uploader("Subí un archivo ZIP que contenga la carpeta .VAult", type="zip")

    if uploaded_file:
        temp_dir = extract_zip_to_temp(uploaded_file)
        vault_path = find_vault(temp_dir)
        if not vault_path:
            st.error("❌ No se encontró la carpeta .VAult dentro del ZIP")
        else:
            tables = get_tables(vault_path)
            if not tables:
                st.error("❌ No se encontraron tablas en la .VAult")
            else:
                tabla_seleccionada = st.selectbox("Elegí una tabla", list(tables.keys()))
                if tabla_seleccionada:
                    equipos = get_teams_from_table(tables[tabla_seleccionada])
                    if not equipos:
                        st.warning("No se encontraron equipos en esta tabla.")
                    else:
                        st.write("### ⚽ Equipos detectados:")
                        replacements = {}
                        for eq in equipos:
                            nuevo = st.text_input(f"Reemplazar '{eq}' por:", value=eq, key=f"{eq}_{tabla_seleccionada}")
                            if nuevo != eq:
                                replacements[eq] = nuevo

                        if st.button("Aplicar cambios y descargar nuevo .VAult"):
                            replace_teams_in_table(tables[tabla_seleccionada], replacements)
                            output_zip = os.path.join(tempfile.gettempdir(), "VAult_editado.zip")
                            zip_vault(vault_path, output_zip)
                            with open(output_zip, "rb") as f:
                                st.download_button(
                                    "⬇️ Descargar nuevo archivo .VAult",
                                    f,
                                    file_name="VAult_editado.zip",
                                    mime="application/zip"
                                )

if __name__ == "__main__":
    run_angle_tabla_filter_page()