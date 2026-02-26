import os
from app.core.logger import logger
from sqlalchemy.orm import Session
from app.models.files import FileMetadata
from app.utils.csv_utils import analyze_csv_stream

def create_file_record(db: Session, file_id: str, filename: str, path: str, checksum: str):
    """
    Service for file db record
    Args:
        db: Session obj
        file_id: uuid
        filename: string
        path: string

    Returns: db object from files table

    """
    try:
        record = FileMetadata(id=file_id, filename=filename, path=path, status="uploaded", checksum=checksum)
        db.add(record)
        db.commit()
        db.refresh(record)
    except Exception as e:
        db.rollback()
        logger.exception("Failed to create file record")
    return record


def update_file_metadata(db: Session, file_id: str):
    """
    updating file metadata in table
    Args:
        db: session
        file_id: string

    Returns:

    """
    file = db.get(FileMetadata, file_id)
    if not file:
        logger.warning("update_file_metadata: file_not_found", extra={"file_id": file_id})
        return None

    try:
        rows, columns = analyze_csv_stream(file.path)
        size = os.path.getsize(file.path)
        file.rows = rows
        file.columns = columns
        file.size = size
        file.status = "ready"
        db.commit()
        db.refresh(file)

        logger.info("update_file_metadata: success", extra={"file_id": file_id, "rows": rows,
                                                            "columns": columns, "size": size})
        return file
    except Exception:
        db.rollback()
        file.status = "failed"
        db.commit()
        logger.exception("update_file_metadata: failed", extra={"file_id": file_id})
        return None
