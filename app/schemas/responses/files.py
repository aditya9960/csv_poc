from pydantic import BaseModel
from datetime import datetime

class FileResponse(BaseModel):
    """
    files table response pydantic
    """
    id: str
    filename: str
    size: int
    rows: int
    columns: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True