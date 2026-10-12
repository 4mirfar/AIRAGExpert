class Retriever:

    def __init__(
        self,
        embedding_service,
        qdrant_service,
    ):
        self.embedding_service = embedding_service
        self.qdrant_service = qdrant_service

    def retrieve(
        self,
        question: str,
        top_k: int = 5,
    ):
        query_vector = self.embedding_service.embed_text(
            question
        )

        results = self.qdrant_service.search(
            query_vector=query_vector,
            top_k=top_k,
        )

        for result in results:
            print(
                result.score,
                result.payload["filename"],
                result.payload["chunk_index"],
            )

        return results


#  TODO Add a similarity threshold
    