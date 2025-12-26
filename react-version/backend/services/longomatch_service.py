import xml.etree.ElementTree as ET
import pandas as pd
import json
from typing import List, Dict, Any

def convert_longomatch_xml_to_instances(xml_content: str) -> List[Dict[str, Any]]:
    """
    Parsea el contenido de un XML de LongoMatch y devuelve una lista de diccionarios (instancias).
    """
    try:
        root = ET.fromstring(xml_content)
        instances = []

        # Recorrer cada <instance>
        for inst in root.findall(".//instance"):
            row = {}
            id_elem = inst.find("ID")
            start_elem = inst.find("start")
            end_elem = inst.find("end")
            code_elem = inst.find("code")

            row["ID"] = id_elem.text if id_elem is not None else ""
            row["start"] = start_elem.text if start_elem is not None else ""
            row["end"] = end_elem.text if end_elem is not None else ""
            row["code"] = code_elem.text if code_elem is not None else ""
            
            # Leer los labels dentro de cada instancia
            labels = inst.findall(".//label")
            for label in labels:
                group_elem = label.find("group")
                text_elem = label.find("text")
                if group_elem is not None and text_elem is not None:
                    group = group_elem.text
                    text = text_elem.text
                    row[group] = text
            
            instances.append(row)
        
        return instances
    except Exception as e:
        raise ValueError(f"Error al procesar el XML de LongoMatch: {str(e)}")

def instances_to_csv_string(instances: List[Dict[str, Any]]) -> str:
    """Convierte la lista de instancias a una cadena CSV."""
    if not instances:
        return ""
    df = pd.DataFrame(instances)
    return df.to_csv(index=False, encoding="utf-8-sig")

def instances_to_json_string(instances: List[Dict[str, Any]]) -> str:
    """Convierte la lista de instancias a una cadena JSON."""
    return json.dumps(instances, ensure_ascii=False, indent=2)
