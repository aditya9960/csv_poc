from celery import Celery
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logger import logger
from app.services.file_service import update_file_metadata

celery_app = Celery(
    "worker",
    broker=settings.redis_url,
    backend=settings.redis_url
)

@celery_app.task(name="process_file")
def process_file(file_id: str):
    """ process file in background using celery"""
    logger.info("process_file_celery: started", extra={"file_id": file_id})
    db = SessionLocal()
    try:
        file = update_file_metadata(db, file_id)
        if not file:
            logger.info("process_file_celery: file not found ", extra={"file_id": file_id})
    except Exception as e:
        logger.error("process_file_celery: failed ", extra={"file_id": file_id, "error": str(e)})
    finally:
        db.close()
        logger.info("process_file_celery: finished", extra={"file_id": file_id})
