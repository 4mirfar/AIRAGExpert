from app.services.qdrant_service import QdrantService


def test_qdrant_connection():

    service = QdrantService()

    service.create_collection()

    collections = service.client.get_collections()

    names = [
        collection.name
        for collection in collections.collections
    ]

    assert "documents" in names