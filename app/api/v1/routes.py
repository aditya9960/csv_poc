from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.schemas.responses.files import FileResponse
from app.models.files import FileMetadata
from app.storage.local import LocalStorage

router = APIRouter()
# setting global
storage = LocalStorage()

@router.get("")
def hello():
    return {"Hello": "World"}


@router.get("/files", response_model=list[FileResponse])
def list_files(
        db: Session = Depends(get_db),
        page: int = Query(1, ge=1),
        page_size: int = Query(settings.default_page_size, ge=1, le=100)
    ):
    return db.query(FileMetadata).offset((page-1)*page_size).limit(page_size).all()

