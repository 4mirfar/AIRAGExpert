from app.retrieval.retriever import Retriever
from app.retrieval.context_builder import ContextBuilder
from app.rag.prompt_builder import PromptBuilder
from app.services.llm import LLMService
from app.rag.query_rewriter import QueryRewriter


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

        self.query_rewriter = QueryRewriter(
            llm_service=self.llm_service,
        )

    def ask(
        self,
        question: str,
        history: list | None = None,
        messages: dict | None = None,
        top_k: int = 5,
    ):

        # -----------------------------------------
        # 1. Rewrite question for retrieval
        # -----------------------------------------

        search_query = self.query_rewriter.rewrite(
            question=question,
            history=history,
        )

        print("Original question:", question)
        print("Search query:", search_query)

        # -----------------------------------------
        # 2. Retrieve relevant chunks
        # -----------------------------------------

        results = self.retriever.retrieve(
            question=search_query,
            top_k=top_k,
        )

        # -----------------------------------------
        # 3. Build context
        # -----------------------------------------

        context = self.context_builder.build(
            results
        )

        # -----------------------------------------
        # 4. Build final prompt
        # -----------------------------------------

        prompt = self.prompt_builder.build(
            question=question,
            context=context,
        )

        # Create messages history
        messages = [
            {
                "role": "system",
                "content": self.prompt_builder.SYSTEM_PROMPT
            },
            *messages,
            {
                "role": "user",
                "content": f"""Context:
                        {context}

                        Question:
                        {question}"""
            }

        ]
        # print(messages)

        # -----------------------------------------
        # 5. Generate answer
        # -----------------------------------------

        answer = self.llm_service.chat(messages=messages)

        return {
            "answer": answer,
            "search_query": search_query,
            "sources": [
                {
                    "chunk_id": str(result.id),
                    "filename": result.payload.get("filename"),
                    "chunk_index": result.payload.get("chunk_index"),
                    "score": result.score,
                }
                for result in results
            ],
        }

    
