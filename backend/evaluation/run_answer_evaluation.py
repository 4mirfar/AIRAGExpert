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

print(f"\nTotal Questions:\n{results["total_questions"]}")

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

for result in results["results"]:

    print("\n" + "=" * 60)


    print(
        f"Question:\n{result['question']}"
    )

    print(
        f"\nExpected Answer:\n"
        f"{result['expected_answer']}"
    )

    print(
        f"\nGenerated Answer:\n"
        f"{result['generated_answer']}"
    )

    print(
        f"\nKeyword Coverage: "
        f"{result['keyword_coverage']:.2%}"
    )

    print(
        f"Correctness: "
        f"{result['correctness']:.2f}"
    )

    print(
        f"Relevance: "
        f"{result['relevance']:.2f}"
    )

    print(
        f"Faithfulness: "
        f"{result['faithfulness']:.2f}"
    )

    print(
        f"\nMissing Keywords: "
        f"{result['missing_keywords']}"
    )

    print(
        f"\nJudge Reason:\n"
        f"{result['reason']}"
    )

print("\n" + "=" * 60)