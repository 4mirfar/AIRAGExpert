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

    from qdrant_client import models

    def delete_document(self, document_id: str):
        print("inside qdrant service for delete")
        self.client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(
                                value=document_id
                            ),
                        )
                    ]
                )
            ),
        )


    def get_chunks_by_document_id(
        self,
        document_id: str,
    ) -> list[dict]:

        response = self.client.scroll(
            collection_name=self.COLLECTION_NAME,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(
                            value=str(document_id),
                        ),
                    )
                ]
            ),
            limit=1000,
            with_payload=True,
            with_vectors=False,
        )

        points, _ = response

        chunks = []

        for point in points:

            payload = point.payload or {}

            chunks.append(
                {
                    "chunk_id": str(point.id),
                    "document_id": payload.get("document_id"),
                    "text": payload.get("text", ""),
                    "chunk_index": payload.get("chunk_index"),
                    "filename": payload.get("filename"),
                }
            )

        return chunks

