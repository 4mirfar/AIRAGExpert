# FAST API Version

# from pathlib import Path
# from uuid import uuid4
# import shutil

# from fastapi import UploadFile


# class StorageService:
#     BASE_UPLOAD_DIR = Path("uploads")

#     def __init__(self):
#         self.BASE_UPLOAD_DIR.mkdir(exist_ok=True)

#     async def save_file(
#         self,
#         file,
#         category: str,
#     ) -> dict:

#         upload_dir = self.BASE_UPLOAD_DIR / category
#         upload_dir.mkdir(parents=True, exist_ok=True)

#         extension = Path(file.filename).suffix.lower()

#         content = await file.read()
#         size = len(content)
#         await file.seek(0)

#         file_id = str(uuid4())

#         filename = f"{file_id}{extension}"

#         destination = upload_dir / filename

#         with destination.open("wb") as buffer:
#             shutil.copyfileobj(file.file, buffer)

#         return {
#             "id": file_id,
#             "filename": file.filename,
#             "category": category,
#             "size": size,
#             "stored_name": filename,
#             "path": str(destination),
#             "status": "uploaded",
#         }


# GRADIO Version

from pathlib import Path
import shutil
import uuid


class StorageService:

    def __init__(self, base_dir: str = "storage"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    async def save_file(
        self,
        file: Path,
        category: str = "documents",
    ):

        file = Path(file)

        if not file.exists():
            raise FileNotFoundError(
                f"File does not exist: {file}"
            )

        # Original filename
        filename = file.name

        # Generate unique document ID
        document_id = str(uuid.uuid4())

        # Preserve extension
        extension = file.suffix.lower()

        # Stored filename
        stored_name = f"{document_id}{extension}"

        # Category directory
        category_dir = self.base_dir / category
        category_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Destination
        destination = category_dir / stored_name

        # Copy uploaded file
        shutil.copy2(
            file,
            destination,
        )

        return {
            "document_id": document_id,
            "filename": filename,
            "stored_name": stored_name,
            "path": str(destination),
            "size": destination.stat().st_size,
            "category": category,
        }