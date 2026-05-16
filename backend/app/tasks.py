"""
Celery async tasks for CallMate AI.
"""
from app.celery_app import celery_app


@celery_app.task(name="tasks.calculate_performance_scores")
def calculate_performance_scores(operator_id: str, date: str):
    """Günlük performans skorlarını hesapla."""
    # TODO: implement
    return {"status": "ok", "operator_id": operator_id, "date": date}


@celery_app.task(name="tasks.process_call_recording")
def process_call_recording(call_id: str, s3_key: str):
    """Çağrı kaydını S3'e yükle ve şifrele."""
    # TODO: implement
    return {"status": "ok", "call_id": call_id}
