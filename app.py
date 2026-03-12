from flask import Flask, jsonify
import requests
import os
from google import genai

app = Flask(__name__)

# leer API keys desde variables de entorno
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GEMINI_KEY = os.getenv("GEMINI_KEY")

# cliente Gemini
client = genai.Client(api_key=GEMINI_KEY)


def buscar_ipc():

    url = "https://serpapi.com/search"

    params = {
        "engine": "google",
        "q": "variación anual IPC Colombia DANE",
        "hl": "es",
        "api_key": SERPAPI_KEY
    }

    r = requests.get(url, params=params)
    data = r.json()

    textos = []

    for r in data.get("organic_results", []):
        textos.append(r.get("title", ""))
        textos.append(r.get("snippet", ""))

    return " ".join(textos)


def extraer_ipc(texto):

    prompt = f"""
    Extrae el IPC anual actual de Colombia del siguiente texto.
    Devuelve solo el número con porcentaje.
    Ejemplo de respuesta: 5.29%

    TEXTO:
    {texto}
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text.strip()


@app.route("/")
def home():
    return {"status": "API IPC funcionando"}


@app.route("/ipc-colombia")
def ipc():

    try:

        texto = buscar_ipc()

        ipc = extraer_ipc(texto)

        return jsonify({
            "ipc_anual": ipc
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        })


if __name__ == "__main__":
    app.run()