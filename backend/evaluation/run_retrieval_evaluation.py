import json

from app.services.embedding import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.retrieval.retriever import Retriever
from app.services.retrieval_evaluator import RetrievalEvaluator
from app.services.evaluation_dataset_generator import EvaluationDatasetGenerator
from app.repositories.document_repository import DocumentRepository
from app.services.llm import LLMService
from app.database.database import SessionLocal



# ---------------------------------------------------------
# Services
# ---------------------------------------------------------

embedding_service = EmbeddingService()
qdrant_service = QdrantService()
llm_service = LLMService()

retriever = Retriever(
    embedding_service=embedding_service,
    qdrant_service=qdrant_service,
)

eval_dataset_gen = EvaluationDatasetGenerator(qdrant_service=qdrant_service, llm_service=llm_service)

db = SessionLocal()

try:
    repository = DocumentRepository(db)

    document_ids = repository.get_all_document_ids()

    print(document_ids)

finally:
    db.close()

eval_dataset_gen.generate_and_save(document_ids=document_ids, questions_per_document=5)



# ---------------------------------------------------------
# Load dataset
# ---------------------------------------------------------

with open(
    "evaluation/dataset.json",
    "r",
    encoding="utf-8",
) as file:

    dataset = json.load(file)


# ---------------------------------------------------------
# Evaluate
# ---------------------------------------------------------

evaluator = RetrievalEvaluator(
    retriever=retriever,
)

results = evaluator.evaluate(
    dataset=dataset,
    k_values=[1, 3, 5],
)


# ---------------------------------------------------------
# Print results
# ---------------------------------------------------------

print("\n==============================")
print("   Retrieval Evaluation")
print("==============================")

for metric, score in results.items():

    print(
        f"{metric.upper():<12}: "
        f"{score:.2%}"
    )