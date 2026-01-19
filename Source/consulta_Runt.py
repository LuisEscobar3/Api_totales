import requests
import json
from typing import Any, Dict, Optional

def ConsultaRunt(placa: str) -> Optional[Dict[str, Any]]:
    """
    Consulta la información del RUNT para una placa dada.
    Devuelve solo el contenido del campo 'data' si la respuesta es válida.
    """

    url = "https://by726twxji.execute-api.us-east-1.amazonaws.com/dev/middleware_movilidad/api/v1/runt"

    headers = {
        "Content-Type": "application/json",
        "x-api-key": "lB5SgJCpmWaqq3bSafIRx2pTJbJ5GVOl6Mwr3Znv"  # 🔒 reemplaza con tu clave real
    }

    data = {
        "placa": placa,
        "tipo_documento": None,
        "numero_documento": None,
        "vin": None
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        response_json = response.json()

        # Obtener solo la sección 'data'
        data_content = response_json.get("data")

        if isinstance(data_content, dict):
            # Imprimir JSON formateado
            print(json.dumps(data_content, indent=4, ensure_ascii=False))
            return data_content
        else:
            print("⚠️ El campo 'data' no está presente o no es un diccionario.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la solicitud: {e}")
        return None
    except ValueError:
        print("⚠️ La respuesta no es un JSON válido.")
        print(response.text)
        return None

