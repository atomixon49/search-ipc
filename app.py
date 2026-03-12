from flask import Flask, jsonify
import requests
import os
from groq import Groq

app = Flask(__name__)

# leer API keys desde variables de entorno
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# cliente Groq
client = Groq(api_key=GROQ_API_KEY)


def buscar_ipc():

    url = "https://serpapi.com/search"

    params = {
        "engine": "google",
        "q": "variación anual IPC Colombia DANE 2026",
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

    REGLAS:
    - devuelve solo el número con porcentaje
    - no agregues explicación
    - ejemplo de salida: 5.29%

    TEXTO:
    {texto}
    """

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="llama3-70b-8192"
    )

    return chat_completion.choices[0].message.content.strip()

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