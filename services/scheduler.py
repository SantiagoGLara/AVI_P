import json
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from core.tools.dataframe_tools import analizar_dataframe
from services.llm_S import interpretar_resultado, preguntar_modelo
from core.agents.reportes import generar_reporte

BASE_DIR = Path(__file__).parent.parent
JOBS_FILE = BASE_DIR / "data" / "jobs.json"
OUTPUTS_DIR = BASE_DIR / "data" / "outputs"

scheduler = BackgroundScheduler(timezone="America/Mexico_City")
_logs: list[dict] = []


def _add_log(job_id: str, job_name: str, status: str, message: str):
    _logs.insert(0, {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "job_id": job_id,
        "job_name": job_name,
        "status": status,
        "message": message,
    })
    if len(_logs) > 200:
        _logs.pop()


def _load_file(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    return pd.read_excel(path)


def _execute_job(job_id: str, job_name: str, folder: str, action: str, pattern: str):
    folder_path = Path(folder)
    if not folder_path.exists():
        _add_log(job_id, job_name, "error", f"Carpeta no encontrada: {folder}")
        return

    files = []
    for ext in ("*.csv", "*.xlsx", "*.xls"):
        files.extend(folder_path.glob(ext))

    if pattern:
        files = [f for f in files if pattern.lower() in f.name.lower()]

    if not files:
        _add_log(job_id, job_name, "warning", "Sin archivos que procesar en la carpeta")
        return

    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    for file in files:
        try:
            df = _load_file(file)
            stats = analizar_dataframe(df)
            interpretacion = interpretar_resultado(stats)
            analisis_result = {"analisis": stats, "interpretacion": interpretacion}

            if action in ("analisis", "ambos"):
                out = OUTPUTS_DIR / f"{file.stem}_analisis_{ts}.json"
                out.write_text(
                    json.dumps(analisis_result, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
                _add_log(job_id, job_name, "ok", f"Análisis guardado: {out.name}")

            if action in ("reporte", "ambos"):
                reporte = generar_reporte(analisis_result)
                out = OUTPUTS_DIR / f"{file.stem}_reporte_{ts}.txt"
                out.write_text(
                    reporte if isinstance(reporte, str) else json.dumps(reporte, ensure_ascii=False),
                    encoding="utf-8"
                )
                _add_log(job_id, job_name, "ok", f"Reporte guardado: {out.name}")

        except Exception as e:
            _add_log(job_id, job_name, "error", f"Error en {file.name}: {e}")


def _load_jobs_file() -> list[dict]:
    if JOBS_FILE.exists():
        return json.loads(JOBS_FILE.read_text(encoding="utf-8"))
    return []


def _save_jobs_file(jobs: list[dict]):
    JOBS_FILE.parent.mkdir(parents=True, exist_ok=True)
    JOBS_FILE.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")


def create_job(name: str, folder: str, action: str, interval_minutes: int, pattern: str = "") -> str:
    job_id = uuid.uuid4().hex[:8]
    scheduler.add_job(
        _execute_job,
        trigger=IntervalTrigger(minutes=interval_minutes),
        args=[job_id, name, folder, action, pattern],
        id=job_id,
        name=name,
        replace_existing=True,
    )
    jobs = _load_jobs_file()
    jobs.append({
        "id": job_id,
        "name": name,
        "folder": folder,
        "action": action,
        "interval_minutes": interval_minutes,
        "pattern": pattern,
        "created_at": datetime.now().isoformat(),
    })
    _save_jobs_file(jobs)
    return job_id


def delete_job(job_id: str):
    try:
        scheduler.remove_job(job_id)
    except Exception:
        pass
    jobs = [j for j in _load_jobs_file() if j["id"] != job_id]
    _save_jobs_file(jobs)


def run_now(job_id: str) -> bool:
    jobs = _load_jobs_file()
    job = next((j for j in jobs if j["id"] == job_id), None)
    if not job:
        return False
    _execute_job(job["id"], job["name"], job["folder"], job["action"], job.get("pattern", ""))
    return True


def list_jobs() -> list[dict]:
    result = []
    for j in _load_jobs_file():
        apj = scheduler.get_job(j["id"])
        next_run = None
        if apj and apj.next_run_time:
            next_run = apj.next_run_time.strftime("%Y-%m-%d %H:%M:%S")
        result.append({**j, "next_run": next_run, "active": apj is not None})
    return result


def get_logs() -> list[dict]:
    return _logs


def start_scheduler():
    scheduler.start()
    for job in _load_jobs_file():
        try:
            scheduler.add_job(
                _execute_job,
                trigger=IntervalTrigger(minutes=job["interval_minutes"]),
                args=[job["id"], job["name"], job["folder"], job["action"], job.get("pattern", "")],
                id=job["id"],
                name=job["name"],
                replace_existing=True,
            )
        except Exception:
            pass


def stop_scheduler():
    try:
        scheduler.shutdown(wait=False)
    except Exception:
        pass
