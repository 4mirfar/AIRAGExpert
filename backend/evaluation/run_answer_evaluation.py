# CAUTION! FIRST RUN run_retrieval_evaluation.py then this file

import json

from app.services.embedding import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.services.rag import RAGService
from app.services.llm import LLMService
from app.services.generation_evaluator import (
    GenerationEvaluator,
)
from app.services.answer_evaluator import (
    AnswerEvaluator,
)

llm_service = LLMService()

embedding_service = EmbeddingService()

qdrant_service = QdrantService()

rag_service = RAGService(
    embedding_service=embedding_service,
    qdrant_service=qdrant_service,
    llm_service=llm_service,
)

answer_evaluator = AnswerEvaluator(
    llm_service=llm_service,
)

evaluator = GenerationEvaluator(
    rag_service=rag_service,
    answer_evaluator=answer_evaluator,
)



# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------

with open(
    "evaluation/dataset.json",
    "r",
    encoding="utf-8",
) as file:

    dataset = json.load(file)


results = evaluator.evaluate(
    dataset=dataset,
)

print("\n==============================")
print("       RAG Answer Evaluation")
print("==============================")


print("\nGeneration")

print(
    f"Keyword Coverage   : "
    f"{results['keyword_coverage']:.2%}"
)

print(
    f"Correctness        : "
    f"{results['correctness']:.2%}"
)

print(
    f"Relevance          : "
    f"{results['relevance']:.2%}"
)

print(
    f"Faithfulness       : "
    f"{results['faithfulness']:.2%}"
)

print("==============================\n")