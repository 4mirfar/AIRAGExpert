from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

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