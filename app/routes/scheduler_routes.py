from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.scheduler import create_job, delete_job, run_now, list_jobs, get_logs

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


class JobCreate(BaseModel):
    name: str
    folder: str
    action: str        # "analisis" | "reporte" | "ambos"
    interval_minutes: int
    pattern: str = ""


@router.get("/jobs")
def get_jobs():
    return list_jobs()


@router.post("/jobs")
def post_job(body: JobCreate):
    if body.interval_minutes < 1:
        raise HTTPException(status_code=400, detail="El intervalo mínimo es 1 minuto")
    if body.action not in ("analisis", "reporte", "ambos"):
        raise HTTPException(status_code=400, detail="Acción inválida")
    job_id = create_job(body.name, body.folder, body.action, body.interval_minutes, body.pattern)
    return {"job_id": job_id}


@router.delete("/jobs/{job_id}")
def remove_job(job_id: str):
    delete_job(job_id)
    return {"ok": True}


@router.post("/jobs/{job_id}/run")
def execute_now(job_id: str):
    ok = run_now(job_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return {"ok": True}


@router.get("/logs")
def get_scheduler_logs():
    return get_logs()
