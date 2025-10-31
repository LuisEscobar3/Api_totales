# test_api.py
import requests

API_URL = "http://127.0.0.1:4000/consulta"

payload = {
    "placa": "DQU371",
    "numero_documento": "1121842328",
    "nombre_propietario": "OSCAR FERNANDO CARRILLO GARAVITO"
}

try:
    response = requests.post(API_URL, json=payload)
    response.raise_for_status()
    print("✅ Respuesta exitosa:")
    print(response.json())
except requests.exceptions.RequestException as e:
    print("❌ Error al consumir la API:", e)
