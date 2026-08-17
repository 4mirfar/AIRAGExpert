from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile, Depends

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.repositories.document_repository import DocumentRepository

from app.schemas.document import DocumentUploadResponse
from app.services.storage import StorageService
from app.services.validation import FileValidationService

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

validator = FileValidationService()
storage = StorageService()


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=201,
)
async def upload_document(
    file: Annotated[UploadFile, File()],
    category: Annotated[str, Form()],
):
    await validator.validate(file)

    result = await storage.save_file(
        file=file,
        category=category,
    )

    return result

@router.post("/upload")
async def upload_document(
    file: UploadFile,
    db: Session = Depends(get_db),
):
    result = await storage.save_file(
    file=file,
    category="documents",
    )

    repository = DocumentRepository(db)

    document = repository.create(
        document_id=result["id"],
        filename=result["filename"],
        stored_name=result["stored_name"],
        path=result["path"],
        extension=Path(result["filename"]).suffix.lower(),
        mime_type=file.content_type or "application/octet-stream",
        size=result["size"],
        category=result["category"],
    )
    chunks = await ingestion_service.ingest(
    file_path=document.path,
    document_id=document.id,
    document_metadata={
        "filename": document.filename,
        "category": document.category,
        },
    )

    repository.update_status(
    document.id,
    "processed",
    )   