from pathlib import Path

from fastapi import HTTPException, UploadFile, status


class FileValidationService:

    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".txt",
        ".md",
    }

    ALLOWED_CONTENT_TYPES = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/markdown",
    }

    MAX_FILE_SIZE = 100 * 1024 * 1024


    async def validate(self, file: UploadFile):

        # Extension check
        extension = Path(file.filename).suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file extension"
            )


        # MIME check
        if file.content_type not in self.ALLOWED_CONTENT_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type"
            )


        # Size check
        content = await file.read()

        size = len(content)

        if size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large"
            )


        # reset cursor
        await file.seek(0)

        return True