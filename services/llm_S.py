import requests

def preguntar_modelo(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]


def interpretar_resultado(resultado):

    prompt = f"""
    Analiza estos datos y da conclusiones claras:

    {resultado}
    """

    return preguntar_modelo(prompt)