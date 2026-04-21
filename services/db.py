from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

embeddings = HuggingFaceEmbeddings()

try:
    db = FAISS.load_local("faiss_index", embeddings)
except:
    db = None

def buscar(query):
    if db:
        return db.similarity_search(query, k=3)
    return []