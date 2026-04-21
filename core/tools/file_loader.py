import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOAD_DIR = os.path.join(BASE_DIR, "data", "uploads")

def cargar_dataframe(filename):
    path = os.path.join(UPLOAD_DIR, os.path.basename(filename))
    if filename.endswith(".csv"):
        return pd.read_csv(path)
    else:
        return pd.read_excel(path)