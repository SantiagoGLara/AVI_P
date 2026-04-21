from fastapi import FastAPI
from app.routes.analysis import router as analysis_router
from app.routes.upload import router as upload_router

app = FastAPI()

app.include_router(analysis_router)
app.include_router(upload_router)

@app.get("/")
def root():
    return {"mensaje": "ok"}
