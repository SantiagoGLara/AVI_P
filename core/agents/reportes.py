from services.llm_S import preguntar_modelo

def generar_reporte(analisis):

    prompt = f"""
    Genera un reporte profesional con estos datos:

    {analisis}
    """

    return preguntar_modelo(prompt)