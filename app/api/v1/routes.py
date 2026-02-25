import uuid
from fastapi import APIRouter, Depends, Query, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.schemas.responses.files import FileResponse
from app.models.files import FileMetadata
from app.storage.local import LocalStorage
from app.services.file_service import create_file_record
from app.workers.tasks import process_file
from app.utils.csv_utils import read_csv_page

router = APIRouter()
# setting global
storage = LocalStorage()

# TODO logger

# @router.get("")
# def hello():
#     return {"Hello": "World"}


@router.get("/files", response_model=list[FileResponse])
def list_files(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1),
        page_size: int = Query(settings.default_page_size, ge=1, le=100)
    ):
    """ return files uploaded"""
    return db.query(FileMetadata).offset((page-1)*page_size).limit(page_size).all()


@router.post("/upload", status_code=202)
async def upload_file(file: UploadFile, db: Session = Depends(get_db)):
    """
        file upload api
        Args:
            file: csv file
            db:

        Returns: http response
        # TODO duplicate files & more validations

    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, "Only CSV allowed")

    file_id = str(uuid.uuid4())
    path = await storage.save_file(file_id, file)
    create_file_record(db, file_id, file.filename, path)

    process_file.delay(file_id)
    return {"file_id": file_id, "status": "uploaded"}


@router.get("/files/{file_id}/metadata", response_model=FileResponse)
def get_metadata(file_id: str, db: Session = Depends(get_db)):
    file = db.get(FileMetadata, file_id)
    if not file:
        raise HTTPException(404, "File not found")
    return file


@router.get("/files/{file_id}/data")
def get_file_data(
    file_id: str,
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000)
):
    """
    Returns CSV content as paginated JSON.
    - page: 1-based page number
    - page_size: number of rows per page (max 1000)
    """
    file = db.get(FileMetadata, file_id)
    if not file or file.status != "ready":
        raise HTTPException(400, "File not ready")

    data = read_csv_page(file.path, delimiter=";", page=page, page_size=page_size)
    return {
        "file_id": file.id,
        "filename": file.filename,
        "page": page,
        "page_size": page_size,
        "rows_returned": len(data),
        "data": data
    }
