# Este script procesa un archivo XML para extraer datos de instancias.
# Convierte los datos extraídos a un formato tabular (DataFrame de pandas).
# Finalmente, guarda los datos en dos formatos: un archivo CSV y un archivo JSON.

import xml.etree.ElementTree as ET
import pandas as pd
import json

# Archivo de entrada
xml_file = "/Users/martinjauma/Documents/CODIGO/playlistcsv/ignore/data/logoMatch.xml"

# Parsear el XML
tree = ET.parse(xml_file)
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

# pasar a DataFrame
df = pd.DataFrame(instances)

# guardar como CSV
df.to_csv("ignore/data/outputLongo.csv", index=False, encoding="utf-8-sig")

# guardar como JSON
with open("ignore/data/outputlongo.json", "w", encoding="utf-8") as f:
    json.dump(instances, f, ensure_ascii=False, indent=2)

print("✅ Archivo CSV y JSON generados correctamente.")