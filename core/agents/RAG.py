from services.db import buscar
from services.llm_S import preguntar_modelo

def responder(pregunta):
    docs = buscar(pregunta)
    
    contexto = "\n".join([doc.page_content for doc in docs])

    prompt = f"""
    Usa esta información:

    {contexto}

    Pregunta: {pregunta}
    """

    return preguntar_modelo(prompt)