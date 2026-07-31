from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    category: str
    size: int
    stored_name: str
    path: str
    status: str