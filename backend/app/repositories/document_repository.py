from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import DocumentDB


class DocumentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        *,
        document_id: str,
        filename: str,
        stored_name: str,
        path: str,
        extension: str,
        mime_type: str,
        size: int,
        category: str,
    ) -> DocumentDB:

        document = DocumentDB(
            id=document_id,
            filename=filename,
            stored_name=stored_name,
            path=path,
            extension=extension,
            mime_type=mime_type,
            size=size,
            category=category,
            status="uploaded",
        )

        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)

        return document

    def get_by_id(
        self,
        document_id: str,
    ) -> DocumentDB | None:

        statement = select(DocumentDB).where(
            DocumentDB.id == document_id
        )

        return self.db.execute(
            statement
        ).scalar_one_or_none()

    def update_status(
        self,
        document_id: str,
        status: str,
    ) -> DocumentDB | None:

        document = self.get_by_id(
            document_id
        )

        if not document:
            return None

        document.status = status

        self.db.commit()
        self.db.refresh(document)

        return document