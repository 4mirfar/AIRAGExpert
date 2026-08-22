from app.retrieval.retriever import Retriever
from app.retrieval.context_builder import ContextBuilder
from app.rag.prompt_builder import PromptBuilder
from app.services.llm import LLMService


class RAGService:

    def __init__(
        self,
        embedding_service,
        qdrant_service,
        llm_service=None,
    ):
        self.retriever = Retriever(
            embedding_service=embedding_service,
            qdrant_service=qdrant_service,
        )

        self.context_builder = ContextBuilder()
        self.prompt_builder = PromptBuilder()

        self.llm_service = llm_service or LLMService()

    def ask(
        self,
        question: str,
        top_k: int = 5,
    ) -> str:

        # 1. Retrieve relevant chunks
        results = self.retriever.retrieve(
            question=question,
            top_k=top_k,
        )

        # 2. Build context
        context = self.context_builder.build(results)

        # 3. Build prompt
        prompt = self.prompt_builder.build(
            question=question,
            context=context,
        )

        # 4. Generate answer
        answer = self.llm_service.generate(prompt)

        return {
            "answer": answer,
            "sources": [
                {
                    "filename": result.payload.get("filename"),
                    "chunk_index": result.payload.get("chunk_index"),
                    "score": result.score,
                }
                for result in results
            ],
        }