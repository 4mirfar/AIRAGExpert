import uuid

from app.database.database import SessionLocal
from app.repositories.document_repository import DocumentRepository


def test_create_document():

    db = SessionLocal()

    document_id = str(uuid.uuid4())

    try:
        repository = DocumentRepository(db)

        document = repository.create(
            document_id=document_id,
            filename="test.pdf",
            stored_name="abc123.pdf",
            path="uploads/abc123.pdf",
            extension=".pdf",
            mime_type="application/pdf",
            size=1024,
            category="test",
        )

        assert document.id == document_id
        assert document.filename == "test.pdf"
        assert document.status == "uploaded"

        found = repository.get_by_id(document_id)

        assert found is not None
        assert found.filename == "test.pdf"

        updated = repository.update_status(
            document_id,
            "processing",
        )

        assert updated is not None
        assert updated.status == "processing"

    finally:
        db.close()