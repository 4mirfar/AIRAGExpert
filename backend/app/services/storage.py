from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import UploadFile


class StorageService:
    BASE_UPLOAD_DIR = Path("uploads")

    def __init__(self):
        self.BASE_UPLOAD_DIR.mkdir(exist_ok=True)

    async def save_file(
        self,
        file,
        category: str,
    ) -> dict:

        upload_dir = self.BASE_UPLOAD_DIR / category
        upload_dir.mkdir(parents=True, exist_ok=True)

        extension = Path(file.filename).suffix.lower()

        content = await file.read()
        size = len(content)
        await file.seek(0)

        file_id = str(uuid4())

        filename = f"{file_id}{extension}"

        destination = upload_dir / filename

        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "id": file_id,
            "filename": file.filename,
            "category": category,
            "size": size,
            "stored_name": filename,
            "path": str(destination),
            "status": "uploaded",
        }