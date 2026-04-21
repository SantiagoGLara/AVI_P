from core.agents.analisis import analizar_archivo
from core.agents.reportes import generar_reporte
from core.agents.RAG import responder

def handle_request(data):

    tipo = data.get("type")

    if tipo == "excel_analysis":
        resultado = analizar_archivo(data["file"])
        return resultado

    elif tipo == "report":
        analisis = analizar_archivo(data["file"])
        return generar_reporte(analisis)

    elif tipo == "rag_query":
        return responder(data["query"])

    else:
        return {"error": "Tipo no soportado"}