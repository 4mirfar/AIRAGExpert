from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile, Depends

from pathlib import Path


from app.services.ingestion import IngestionService

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
ingestion_service = IngestionService()


@router.post("/upload")
async def upload_document(
    file: UploadFile,
    db: Session = Depends(get_db),
):

    # 1. Validate
    await validator.validate(file)

    # 2. Save file
    result = await storage.save_file(
        file=file,
        category="documents",
    )

    # 3. Create DB record
    repository = DocumentRepository(db)

    document = repository.create(
        document_id=result["id"],
        filename=result["filename"],
        stored_name=result["stored_name"],
        path=result["path"],
        extension=Path(
            result["filename"]
        ).suffix.lower(),
        mime_type=file.content_type
        or "application/octet-stream",
        size=result["size"],
        category=result["category"],
    )

    # 4. Ingest
    try:

        repository.update_status(
            document.id,
            "processing",
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

    except Exception:

        repository.update_status(
            document.id,
            "failed",
        )

        raise

    return {
        "document_id": document.id,
        "filename": document.filename,
        "status": "processed",
        "chunk_count": len(chunks),
    }