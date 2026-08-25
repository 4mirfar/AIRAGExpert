# FAST API Version

# from pathlib import Path

# from fastapi import HTTPException, UploadFile, status


# class FileValidationService:

#     ALLOWED_EXTENSIONS = {
#         ".pdf",
#         ".docx",
#         ".txt",
#         ".md",
#     }

#     ALLOWED_CONTENT_TYPES = {
#         "application/pdf",
#         "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
#         "text/plain",
#         "text/markdown",
#     }

#     MAX_FILE_SIZE = 100 * 1024 * 1024


#     async def validate(self, file: UploadFile):

#         # Extension check
#         extension = Path(file.filename).suffix.lower()

#         if extension not in self.ALLOWED_EXTENSIONS:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Unsupported file extension"
#             )


#         # MIME check
#         if file.content_type not in self.ALLOWED_CONTENT_TYPES:
#             raise HTTPException(
#                 status_code=400,
#                 detail="Unsupported file type"
#             )


#         # Size check
#         content = await file.read()

#         size = len(content)

#         if size > self.MAX_FILE_SIZE:
#             raise HTTPException(
#                 status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
#                 detail="File too large"
#             )


#         # reset cursor
#         await file.seek(0)

#         return True

# Gradio Version

from pathlib import Path


class FileValidationService:

    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".docx",
        ".txt",
        ".md",
    }

    ALLOWED_MIME_TYPES = {
        ".pdf": "application/pdf",
        ".docx": (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        ".txt": "text/plain",
        ".md": "text/markdown",
    }

    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100 MB

    async def validate(self, file_path: Path) -> bool:

        # --------------------------------------------------
        # Normalize path
        # --------------------------------------------------

        file_path = Path(file_path)

        # --------------------------------------------------
        # Existence check
        # --------------------------------------------------

        if not file_path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        if not file_path.is_file():
            raise ValueError(
                f"Not a file: {file_path}"
            )

        # --------------------------------------------------
        # Extension check
        # --------------------------------------------------

        extension = file_path.suffix.lower()

        if extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file extension: {extension}"
            )

        # --------------------------------------------------
        # Size check
        # --------------------------------------------------

        size = file_path.stat().st_size

        if size > self.MAX_FILE_SIZE:
            raise ValueError(
                "File too large. Maximum size is 100 MB."
            )

        # --------------------------------------------------
        # MIME check
        # --------------------------------------------------

        expected_mime = self.ALLOWED_MIME_TYPES.get(
            extension
        )

        if expected_mime is None:
            raise ValueError(
                f"Unsupported file type: {extension}"
            )

        # --------------------------------------------------
        # Validation successful
        # --------------------------------------------------

        return True