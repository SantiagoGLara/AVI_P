import pandas as pd

def cargar_dataframe(file_path):
    if file_path.endswith(".csv"):
        return pd.read_csv(f"data/uploads/{file_path}")
    else:
        return pd.read_excel(f"data/uploads/{file_path}")