from celery import Celery
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.file_service import update_file_metadata

celery_app = Celery(
    "worker",
    broker=settings.redis_url,
    backend=settings.redis_url
)

@celery_app.task
def process_file(file_id: str):
    """ process file in background using celery"""
    db = SessionLocal()
    try:
        update_file_metadata(db, file_id)
    finally:
        db.close()