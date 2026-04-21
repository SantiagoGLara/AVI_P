from core.tools.file_loader import cargar_dataframe
from core.tools.dataframe_tools import analizar_dataframe
from services.llm_S import interpretar_resultado

def analizar_archivo(file_path):
    df = cargar_dataframe(file_path)
    
    analisis = analizar_dataframe(df)
    
    interpretacion = interpretar_resultado(analisis)
    
    return {
        "analisis": analisis,
        "interpretacion": interpretacion
    }