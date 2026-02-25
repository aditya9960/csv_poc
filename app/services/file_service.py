import os
from sqlalchemy.orm import Session
from app.models.files import FileMetadata
from app.utils.csv_utils import analyze_csv_stream

def create_file_record(db: Session, file_id: str, filename: str, path: str):
    """
    Service for file db record
    Args:
        db: Session obj
        file_id: uuid
        filename: string
        path: string

    Returns: db object from files table

    """
    record = FileMetadata(id=file_id, filename=filename, path=path, status="uploaded")
    db.add(record)
    db.commit()
    db.refresh(record)
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
    try:
        rows, columns = analyze_csv_stream(file.path)
        size = os.path.getsize(file.path)
        file.rows = rows
        file.columns = columns
        file.size = size
        file.status = "ready"
    except Exception:
        file.status = "failed"
    db.commit()