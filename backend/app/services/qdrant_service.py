from qdrant_client import QdrantClient, models


class QdrantService:

    COLLECTION_NAME = "documents"
    VECTOR_SIZE = 1024

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
    ):
        self.client = QdrantClient(
            host=host,
            port=port,
        )

    def create_collection(self):
        collections = self.client.get_collections()

        exists = any(
            collection.name == self.COLLECTION_NAME
            for collection in collections.collections
        )

        if not exists:
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=models.Distance.COSINE,
                ),
            )

    def upsert_chunks(
        self,
        chunks,
        vectors,
    ):
        points = []

        for chunk, vector in zip(chunks, vectors):

            points.append(
                models.PointStruct(
                    id=chunk.chunk_id,
                    vector=vector,
                    payload={
                        "text": chunk.text,
                        **chunk.metadata,
                    },
                )
            )


            #    PointStruct(
            #     id="abc123_4",

            #     vector=[
            #         0.12,
            #         -0.31,
            #         0.82,
            #         ...
            #     ],

            #     payload={
            #         "text": "FastAPI is a Python framework...",
            #         "document_id": "abc123",
            #         "filename": "guide.pdf",
            #         "chunk_index": 4
            #     }
            # )

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=points,
            wait=True,
        )

        return len(points)

    def search(
    self,
    query_vector: list[float],
    top_k: int = 5,
    ):
            results = self.client.query_points(
                collection_name=self.COLLECTION_NAME,
                query=query_vector,
                limit=top_k,
                with_payload=True,
            )

            return results.points