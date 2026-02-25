from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.schemas.responses.files import FileResponse
from app.models.files import FileMetadata

router = APIRouter()


@router.get("")
def hello():
    return {"Hello": "World"}
