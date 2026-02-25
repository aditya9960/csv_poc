import uuid
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class FileMetadata(Base):
    """
    model to store import file metadata
    """
    __tablename__ = "files"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    path = Column(String, nullable=False)
    size = Column(Integer, default=0)
    rows = Column(Integer, default=0)
    columns = Column(Integer, default=0)
    status = Column(String, default="uploading") #TODO later enum
    created_at = Column(DateTime(timezone=True), server_default=func.now())

