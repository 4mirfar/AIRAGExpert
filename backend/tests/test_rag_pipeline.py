from app.services.rag import RAGService
from app.services.embedding import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.services.llm import LLMService

def test_rag_pipeline():

    embedding_service = EmbeddingService()

    qdrant_service = QdrantService(
        host="localhost",
        port=6333,
    )

    llm_service = LLMService(
        model="llama3.2:3b",
        host="http://localhost:11434",
    )

    rag = RAGService(
        embedding_service=embedding_service,
        qdrant_service=qdrant_service,
        llm_service=llm_service,
    )

    answer = rag.ask(
        "What is this document about?"
    )

    assert isinstance(answer, str)
    assert answer.strip()