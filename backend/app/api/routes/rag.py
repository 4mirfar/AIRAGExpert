from fastapi import APIRouter

from app.schemas.rag import RAGRequest, RAGResponse
from app.services.rag import RAGService
from app.services.embedding import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.services.llm import LLMService



router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)



embedding_service = EmbeddingService()
qdrant_service = QdrantService()
llm_service = LLMService()

rag_service = RAGService(
    embedding_service=embedding_service,
    qdrant_service=qdrant_service,
    llm_service=llm_service,
)


@router.post("/ask", response_model=RAGResponse)
def ask_question(request: RAGRequest):
    result = rag_service.ask(request.question)

    return RAGResponse(
        answer=result["answer"],
        sources=result["sources"]
    )


# TODO use Reranker for better quality of searches