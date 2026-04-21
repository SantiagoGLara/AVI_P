from fastapi import APIRouter
from core.orquestador import handle_request

router = APIRouter()

@router.post("/analyze")
def analyze(data: dict):
    return handle_request(data)