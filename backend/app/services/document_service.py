class DocumentService:

    def __init__(
        self,
        repository,
        qdrant_service,
    ):
        self.repository = repository
        self.qdrant_service = qdrant_service

    def delete_document(self, document_id: str):

        # Delete vectors first
        self.qdrant_service.delete_document(
            document_id
        )

        # Delete DB record
        deleted = self.repository.delete(
            document_id
        )

        if not deleted:
            raise ValueError(
                f"Document {document_id} not found"
            )

        return True