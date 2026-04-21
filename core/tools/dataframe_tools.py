def analizar_dataframe(df):
    return {
        "filas": len(df),
        "columnas": df.columns.tolist(),
        "resumen": df.describe().to_dict(),
        "nulos": df.isnull().sum().to_dict()
    }